"""Fail-closed launch and evidence boundaries for the cognition programme.

These guards cover the dashboard experiment workflow and EvidenceEngine entry
points, not arbitrary Python code or an already running process. Stop/isolate
commands must remain available independently of this research governance.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

PROGRAM = Path("protocols/COGNITION_CONSCIOUSNESS_V1.json")
PREFIXES = ("RQ-CNS-", "RQ-WEL-", "RQ-EPI-1")
HYPOTHESIS_PREFIXES = ("H-CNS-", "H-WEL-", "H-EPI-1")


class CognitionGovernanceError(ValueError):
    """A new cognitive experiment cannot safely or validly enter a legacy path."""


def cognition_catalog(research_root: Path) -> list[dict[str, Any]]:
    """Expose planned protocols without pretending they are runnable protocols."""
    path = research_root / PROGRAM
    if not path.is_file():
        return []
    raw: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise CognitionGovernanceError("Malformed cognition programme")
    values: object = raw.get("protocols")
    if not isinstance(values, list):
        raise CognitionGovernanceError("Cognition protocols must be a list")
    result: list[dict[str, Any]] = []
    ids: set[str] = set()
    for value in cast(list[object], values):
        if not isinstance(value, dict):
            raise CognitionGovernanceError("Malformed cognition protocol")
        item = cast(dict[str, Any], value)
        identifier = item.get("id")
        if not isinstance(identifier, str) or identifier in ids:
            raise CognitionGovernanceError("Missing or duplicate cognition protocol ID")
        ids.add(identifier)
        if item.get("consciousness_inference") != "not_established":
            raise CognitionGovernanceError(
                "A task catalogue cannot certify consciousness"
            )
        result.append(dict(item))
    return result


def guard_cognition_launch(
    research_root: Path, question_id: str, protocol: str
) -> None:
    """Prevent generic runtime fallback for protected RQs and draft protocols.

    No native adapter is validated in this revision. A flag in a submitted body,
    a fabricated approval string or editing a catalogue status cannot enable one.
    A reviewed adapter must be implemented in code and independently evaluated.
    """
    protected = question_id.startswith(PREFIXES) or protocol.startswith("cog_")
    state_path = research_root / "ethics" / "operational_state.json"
    if state_path.exists():
        try:
            state: object = json.loads(state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CognitionGovernanceError(
                "Ethics state unreadable; new research launches blocked"
            ) from exc
        if not isinstance(state, dict) or state.get("state") not in {
            "NORMAL",
            "REVIEW_REQUIRED",
            "HOLD",
        }:
            raise CognitionGovernanceError(
                "Invalid ethics state; new research launches blocked"
            )
        if state.get("state") != "NORMAL":
            raise CognitionGovernanceError(
                "ETHICS_HOLD: new experiment launches blocked; stop/isolate remains available"
            )
    if protected:
        raise CognitionGovernanceError(
            "COGNITION_ADAPTER_NOT_VALIDATED: registered research question/protocol; "
            "stimulus/scoring tools do not constitute a native experiment. "
            "No fallback to PING, generic ticks or an unrelated science suite is permitted."
        )


def guard_cognition_promotion(hypothesis_id: str, claim_id: str) -> None:
    """Never turn instruments or unreviewed indicators into accepted EVID.

    Functional observations belong in an evidence candidate dossier first.
    Independent replication, theory scope and ethics review are separate records.
    Existing historical evidence is neither rewritten nor retrospectively revoked.
    """
    if hypothesis_id.startswith(HYPOTHESIS_PREFIXES) or claim_id.startswith(
        ("CLAIM-CNS-", "CLAIM-WEL-", "CLAIM-EPI-1")
    ):
        raise CognitionGovernanceError(
            "INDEPENDENT_COGNITION_REVIEW_REQUIRED: automatic EVID promotion disabled "
            "for the new programme; use the candidate schema and external review. "
            "No functional metric establishes phenomenal consciousness."
        )


def assess_candidate(candidate: dict[str, object]) -> dict[str, object]:
    """Check dossier completeness, never authenticate reviewers or accept evidence."""
    required = {
        "candidate_id",
        "protocol_id",
        "question_id",
        "hypothesis_id",
        "source_commit",
        "raw_artifacts",
        "analysis_hash",
        "claim_scope",
        "limitations",
        "alternatives",
        "replication",
        "ethics_review",
        "theory_assumptions",
        "measurement_validity",
        "human_review",
    }
    missing = sorted(
        key
        for key in required
        if key not in candidate or candidate[key] in (None, "", [], {})
    )
    reasons = [f"missing:{key}" for key in missing]
    if candidate.get("claim_scope") != "functional_or_theory_conditional":
        reasons.append("unsupported_claim_scope")
    if candidate.get("consciousness_verdict") not in (None, "not_established"):
        reasons.append("phenomenal_verdict_not_authorized")
    return {
        "status": "INCOMPLETE" if reasons else "READY_FOR_EXTERNAL_REVIEW",
        "reasons": reasons,
        "authority": "candidate_only",
        "accepted_evidence": False,
        "reviewer_identity_authenticated": False,
        "consciousness_inference": "not_established",
    }
