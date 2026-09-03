"""
Evidence Engine — Evaluates experimental results and updates evidence status.

After each experiment, the evidence engine:
1. Creates evidence entries from results
2. Links evidence to claims and hypotheses
3. Re-evaluates claim/hypothesis status based on accumulated evidence
4. Generates automated follow-up questions
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, cast

from .registry import (
    REGISTRY_DIR,
    REPO_ROOT,
    Claim,
    Hypothesis,
    ResearchRegistry,
)

EXPERIMENTS_DIR = REPO_ROOT / "research" / "experiments"
EVIDENCE_DIR = REGISTRY_DIR / "evidence"
EVIDENCE_DIR.mkdir(exist_ok=True)


def _next_evidence_id() -> str:
    """Generate the next evidence ID: EVID-{YYYY}-{NN}."""
    year = datetime.now().year
    existing = list(EVIDENCE_DIR.glob(f"EVID-{year}-*.json"))
    n = len(existing) + 1
    return f"EVID-{year}-{n:02d}"


_INVALID_EVIDENCE_STATUSES = frozenset(
    {
        "template",
        "not_started",
        "running",
        "failed",
        "invalid",
    }
)
"""Experiment statuses that cannot produce scientific evidence."""

_VALID_EVIDENCE_MODES = frozenset(
    {
        "deterministic_verification",
        "stochastic_experiment",
        "observational_experiment",
    }
)


def _check_experiment_valid(experiment_id: str) -> dict[str, Any] | None:
    """Check whether an experiment manifest is valid scientific evidence.

    Returns the manifest dict if valid, None if invalid.

    The EvidenceEngine MUST NOT accept:
    - template (template/example experiments)
    - not_started (not yet executed)
    - running (incomplete execution)
    - failed (execution failure/crash)
    - invalid (scientifically unusable run)

    Only ``completed`` experiments with ``validity.valid == True`` may
    generate scientific evidence.
    """
    manifest_path = EXPERIMENTS_DIR / experiment_id / "manifest.json"
    if not manifest_path.exists():
        return None

    try:
        manifest: dict[str, Any] = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None

    status = manifest.get("experiment_status", "not_started")
    if status in _INVALID_EVIDENCE_STATUSES:
        return None

    validity_raw = manifest.get("validity", {})
    if not isinstance(validity_raw, dict):
        return None
    validity = cast(dict[str, object], validity_raw)
    valid = validity.get("valid", True)
    if not isinstance(valid, bool) or not valid:
        return None
    causal_taint = manifest.get("causal_taint", "PURE")
    if causal_taint != "PURE":
        treatment_raw = manifest.get("ai_treatment")
        if not isinstance(treatment_raw, dict):
            return None
        treatment = cast(dict[str, object], treatment_raw)
        protocol_id = treatment.get("protocol_id")
        if not treatment.get("registered") or not isinstance(protocol_id, str) or not protocol_id.strip():
            return None
    git_raw = manifest.get("git", {})
    if not isinstance(git_raw, dict):
        return None
    git = cast(dict[str, Any], git_raw)
    if git.get("dirty") is not False:
        return None

    return manifest


class EvidenceEngine:
    """Evaluates experimental evidence and updates claim/hypothesis status.

    The engine enforces scientific validity:
    - Only ``completed`` experiments with ``validity.valid == True``
      can produce evidence.
    - Invalid, failed, or template experiments are silently rejected.
    """

    def __init__(self, registry: ResearchRegistry):
        self.registry = registry

    def evaluate_experiment(
        self,
        experiment_id: str,
        claim_id: str,
        hypothesis_id: str,
        result_summary: str,
        effect_size: dict[str, Any] | None = None,
        statistical_significance: dict[str, Any] | None = None,
        evidence_mode: str = "observational_experiment",
        verification: dict[str, Any] | None = None,
        status: str = "inconclusive",
        limitations: str | None = None,
    ) -> str:
        """
        Evaluate an experiment and create an evidence entry.

        Args:
            experiment_id: ID of the experiment to evaluate.
            claim_id: ID of the claim to link evidence to.
            hypothesis_id: ID of the hypothesis to link evidence to.
            result_summary: Summary of the experimental result.
            effect_size: Optional effect size metrics.
            statistical_significance: Optional statistical significance data.
            status: Evidence status (supports | refutes | inconclusive).
            limitations: Optional limitations text.

        Returns:
            The evidence ID.

        Raises:
            ValueError: If the experiment is not scientifically valid
                (template, not_started, running, failed, or invalid).
        """
        if evidence_mode not in _VALID_EVIDENCE_MODES:
            raise ValueError(f"Unknown evidence mode: {evidence_mode!r}")
        if evidence_mode == "deterministic_verification" and statistical_significance:
            raise ValueError(
                "Deterministic verification must not claim statistical significance."
            )

        # Phase 1: Reject scientifically invalid experiments
        manifest = _check_experiment_valid(experiment_id)
        if manifest is None:
            raise ValueError(
                f"Cannot create evidence from experiment {experiment_id}: "
                "experiment is not scientifically valid. "
                "Only 'completed' experiments with valid execution may "
                "produce evidence."
            )
        evidence_id = _next_evidence_id()

        # Include experiment validity info in evidence record
        validity = manifest.get("validity", {})
        evidence: dict[str, Any] = {
            "evidence_id": evidence_id,
            "experiment_id": experiment_id,
            "claim_id": claim_id,
            "hypothesis_id": hypothesis_id,
            "result_summary": result_summary,
            "effect_size": effect_size or {},
            "statistical_significance": statistical_significance or {},
            "evidence_mode": evidence_mode,
            "verification": verification or {},
            "status": status,  # supports | refutes | inconclusive | pending
            "limitations": limitations or "",
            "artifacts": {"figures": [], "data_files": []},
            "generated": datetime.now().isoformat(),
            "experiment_validity": {
                "valid": validity.get("valid", True),
                "runtime_error_count": validity.get("runtime_error_count", 0),
                "fatal_error_count": validity.get("fatal_error_count", 0),
            },
        }

        # Save evidence
        evidence_path = EVIDENCE_DIR / f"{evidence_id}.json"
        with open(evidence_path, "w", encoding="utf-8") as f:
            json.dump(evidence, f, indent=2, ensure_ascii=False)

        # Update claim
        claim = self.registry.claims.get(claim_id)
        if claim:
            claim.evidence.append(evidence_id)
            claim.experiments.append(experiment_id)
            self._update_claim_status(claim)
            self.registry.save_claims()

        # Update hypothesis
        hypothesis = self.registry.hypotheses.get(hypothesis_id)
        if hypothesis:
            hypothesis.evidence.append(evidence_id)
            self._update_hypothesis_status(hypothesis)
            self.registry.save_hypotheses()

        self.update_research_question(claim_id, evidence_id)

        return evidence_id

    def _update_claim_status(self, claim: Claim) -> None:
        """Re-evaluate claim status based on all accumulated evidence."""
        if not claim.evidence:
            claim.status = "untested"
            claim.confidence = "none"
            return

        supporting = 0
        refuting = 0
        inconclusive = 0

        for evid_id in claim.evidence:
            evid = self._load_evidence(evid_id)
            if evid:
                s = evid.get("status", "inconclusive")
                if s == "supports":
                    supporting += 1
                elif s == "refutes":
                    refuting += 1
                else:
                    inconclusive += 1

        total = supporting + refuting + inconclusive

        # Check minimum runs requirement
        if total < claim.minimum_runs:
            claim.status = "inconclusive"
            claim.confidence = "low"
            return

        # Decision logic
        if supporting >= 2 * refuting and supporting >= 3 and supporting > total * 0.7:
            claim.status = "supported"
            claim.confidence = "high" if supporting >= 10 else "medium"
        elif refuting >= 2 * supporting and refuting >= 3:
            claim.status = "refuted"
            claim.confidence = "high" if refuting >= 10 else "medium"
        elif supporting > refuting:
            claim.status = "inconclusive"
            claim.confidence = "low"
        else:
            claim.status = "inconclusive"
            claim.confidence = "none"

    def _update_hypothesis_status(self, hypothesis: Hypothesis) -> None:
        """Simple hypothesis status based on linked evidence."""
        if not hypothesis.evidence:
            hypothesis.status = "untested"
            return

        supporting = 0
        refuting = 0

        for evid_id in hypothesis.evidence:
            evid = self._load_evidence(evid_id)
            if evid:
                s = evid.get("status", "inconclusive")
                if s == "supports":
                    supporting += 1
                elif s == "refutes":
                    refuting += 1

        if supporting > refuting and supporting >= 2:
            hypothesis.status = "supported"
        elif refuting > supporting and refuting >= 2:
            hypothesis.status = "refuted"
        else:
            hypothesis.status = "inconclusive"

    def update_research_question(self, claim_id: str, evidence_id: str) -> None:
        """Reflect claim maturity in its question without authoring an answer.

        ``ready_for_answer`` is deliberately a review state. A human researcher
        must still evaluate methods and limitations before setting an answer to
        ``provisionally_answered`` or ``answered``.
        """
        claim = self.registry.claims.get(claim_id)
        if claim is None:
            return
        question = self.registry.questions.get(claim.research_question)
        if question is None or question.status in {"answered", "superseded"}:
            return

        if evidence_id not in question.evidence:
            question.evidence.append(evidence_id)
        related_claims = self.registry.claims_for_question(question.id)
        if related_claims and all(
            item.status in {"supported", "refuted"} for item in related_claims
        ):
            question.status = "ready_for_answer"
        elif any(item.status == "inconclusive" for item in related_claims):
            question.status = "inconclusive"
        else:
            question.status = "in_progress"
        self.registry.save_questions()

    def _load_evidence(self, evidence_id: str) -> dict[str, Any] | None:
        path = EVIDENCE_DIR / f"{evidence_id}.json"
        if not path.exists():
            return None
        with open(path, encoding="utf-8") as f:
            data: Any = json.load(f)
            return cast("dict[str, Any]", data) if isinstance(data, dict) else None

    def generate_followup_questions(self, experiment_id: str) -> list[dict[str, str]]:
        """
        Automatically generate follow-up research questions based on
        experimental outcomes. Returns candidate questions for human review.
        """
        manifest_path = EXPERIMENTS_DIR / experiment_id / "manifest.json"
        if not manifest_path.exists():
            return []

        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        sim = manifest.get("simulation", {})
        questions: list[dict[str, str]] = []

        # Pattern: STDP + Homeostasis → check interaction
        if sim.get("learning") and sim.get("homeostasis"):
            questions.append(
                {
                    "id": "RQ-AUTO-CANDIDATE",
                    "question": "Ist die beobachtete Stabilität hauptsächlich durch Homeostase statt STDP verursacht?",
                    "source": "auto_generated",
                    "trigger": "STDP + Homeostasis co-occurrence",
                }
            )

        # Pattern: Single dimension → suggest ablation
        dims = sim.get("dimensions", [])
        if len(dims) == 5:
            questions.append(
                {
                    "id": "RQ-AUTO-CANDIDATE",
                    "question": "Wäre der Effekt in niedrigeren Dimensionen (1D/2D/3D) derselbe?",
                    "source": "auto_generated",
                    "trigger": "5D experiment without lower-dimensional control",
                }
            )

        return questions
