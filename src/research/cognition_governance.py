"""Fail-closed cognition launch and evidence-promotion boundaries.

A validated operational adapter may execute functional measurements or a
methodological audit. Neither path is a consciousness detector and neither may
promote itself to EVID.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, cast

from .protocol_registry import protocol_by_id

PROGRAM = Path("protocols/COGNITION_CONSCIOUSNESS_V1.json")
PREFIXES = ("RQ-CNS-", "RQ-WEL-", "RQ-EPI-1")
HYPOTHESIS_PREFIXES = ("H-CNS-", "H-WEL-", "H-EPI-1")
MAX_RECORD_BYTES = 262144
_ALLOWED_EXECUTION_KINDS = {"functional_experiment", "conceptual_audit"}


class CognitionGovernanceError(ValueError):
    """A cognitive study cannot enter an unvalidated or held path."""


def _read_record(path: Path) -> dict[str, Any]:
    try:
        if path.stat().st_size > MAX_RECORD_BYTES:
            raise CognitionGovernanceError("Oversized governance record")
        raw: object = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CognitionGovernanceError("Unreadable governance record; launch blocked") from exc
    if not isinstance(raw, dict):
        raise CognitionGovernanceError("Governance record must be an object")
    return cast(dict[str, Any], raw)


def cognition_catalog(research_root: Path) -> list[dict[str, Any]]:
    """Expose original proposals without rewriting their historical maturity."""
    path = research_root / PROGRAM
    if not path.is_file():
        return []
    values = _read_record(path).get("protocols")
    if not isinstance(values, list):
        raise CognitionGovernanceError("Cognition protocols must be a list")
    result: list[dict[str, Any]] = []
    ids: set[str] = set()
    for value in cast(list[object], values):
        if not isinstance(value, dict):
            raise CognitionGovernanceError("Malformed cognition protocol")
        item = cast(dict[str, Any], value)
        identifier = item.get("id")
        if not isinstance(identifier, str) or not identifier.strip() or identifier in ids:
            raise CognitionGovernanceError("Missing or duplicate cognition protocol ID")
        ids.add(identifier)
        if item.get("consciousness_inference") != "not_established":
            raise CognitionGovernanceError("Catalogue cannot certify consciousness")
        result.append(dict(item))
    return result


def guard_cognition_launch(
    research_root: Path, question_id: str, protocol: str
) -> None:
    """Permit only explicitly registered validated adapters; reject generic fallback."""
    protected = question_id.startswith(PREFIXES) or protocol.startswith("cog_")
    state_path = research_root / "ethics/operational_state.json"
    if state_path.exists():
        state = _read_record(state_path).get("state")
        if not isinstance(state, str) or state not in {"NORMAL", "REVIEW_REQUIRED", "HOLD"}:
            raise CognitionGovernanceError("Invalid ethics state; new research launches blocked")
        if state != "NORMAL":
            raise CognitionGovernanceError(
                "ETHICS_HOLD: new experiment launches blocked; stop/isolate remains available"
            )
    elif (research_root / PROGRAM).exists():
        raise CognitionGovernanceError(
            "Ethics state missing for installed programme; new launches blocked"
        )
    if not protected:
        return
    contract = protocol_by_id(research_root, protocol)
    if (
        contract is None
        or contract.get("research_question") != question_id
        or contract.get("adapter_validated") is not True
        or contract.get("execution_kind") not in _ALLOWED_EXECUTION_KINDS
    ):
        raise CognitionGovernanceError(
            "COGNITION_ADAPTER_NOT_VALIDATED: registered question/protocol; instruments are not native experiments. "
            "No fallback to generic ticks, PING or unrelated suites is permitted."
        )


def guard_cognition_promotion(hypothesis_id: str, claim_id: str) -> None:
    """Never turn cognition/audit output into accepted evidence automatically."""
    if hypothesis_id.startswith(HYPOTHESIS_PREFIXES) or claim_id.startswith(
        ("CLAIM-CNS-", "CLAIM-WEL-", "CLAIM-EPI-1")
    ):
        raise CognitionGovernanceError(
            "INDEPENDENT_COGNITION_REVIEW_REQUIRED: automatic EVID promotion disabled for the cognition programme. "
            "Functional observations require a candidate dossier and external review, not a phenomenal verdict."
        )


def _nonempty_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _texts(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(
        _nonempty_text(item) for item in cast(list[object], value)
    )


def _matches(value: object, pattern: str) -> bool:
    return isinstance(value, str) and re.fullmatch(pattern, value) is not None


def assess_candidate(candidate: dict[str, object]) -> dict[str, object]:
    """Check dossier metadata shape/consistency, never phenomenal truth."""
    reasons: list[str] = []
    patterns = {
        "candidate_id": r"CAND-CNS-[A-Za-z0-9_-]+",
        "protocol_id": r"cog_(?:cns|wel|epi)_[0-9]+_v[0-9]+",
        "question_id": r"RQ-(?:CNS|WEL|EPI)-[0-9]+",
        "hypothesis_id": r"H-(?:CNS|WEL|EPI)-[0-9]+-[A-Z]+",
        "source_commit": r"[0-9a-f]{40}",
        "analysis_hash": r"[0-9a-f]{64}",
    }
    for key, pattern in patterns.items():
        if not _matches(candidate.get(key), pattern):
            reasons.append(f"invalid:{key}")
    if candidate.get("schema_version") != "1.0":
        reasons.append("invalid:schema_version")
    if candidate.get("claim_scope") != "functional_or_theory_conditional":
        reasons.append("unsupported_claim_scope")
    if candidate.get("consciousness_verdict") != "not_established":
        reasons.append("phenomenal_verdict_not_authorized")
    if candidate.get("accepted_evidence") not in {None, False}:
        reasons.append("candidate_cannot_accept_itself")
    question = candidate.get("question_id")
    hypothesis = candidate.get("hypothesis_id")
    protocol = candidate.get("protocol_id")
    if isinstance(question, str) and isinstance(hypothesis, str) and isinstance(protocol, str):
        key = question.removeprefix("RQ-")
        if not hypothesis.startswith("H-" + key + "-") or not protocol.startswith(
            "cog_" + key.lower().replace("-", "_") + "_v"
        ):
            reasons.append("inconsistent_research_links")
    for key in ("limitations", "alternatives", "theory_assumptions"):
        if not _texts(candidate.get(key)):
            reasons.append(f"invalid:{key}")
    raw = candidate.get("raw_artifacts")
    if not isinstance(raw, list) or not raw:
        reasons.append("invalid:raw_artifacts")
    else:
        for index, item in enumerate(cast(list[object], raw)):
            if not isinstance(item, dict):
                reasons.append(f"invalid:raw_artifacts:{index}")
                continue
            record = cast(dict[str, object], item)
            path_value = record.get("path")
            role = record.get("role")
            if (
                not _nonempty_text(path_value)
                or not _matches(record.get("sha256"), r"[0-9a-f]{64}")
                or role not in {"primary_observation", "stimulus_schedule", "state", "configuration"}
            ):
                reasons.append(f"invalid:raw_artifacts:{index}")
            if isinstance(path_value, str):
                path = Path(path_value.replace("\\", "/"))
                if path.is_absolute() or ".." in path.parts:
                    reasons.append(f"unsafe:raw_artifacts:{index}")
    measurement = candidate.get("measurement_validity")
    if not isinstance(measurement, dict):
        reasons.append("invalid:measurement_validity")
    else:
        record = cast(dict[str, object], measurement)
        for key in ("observation_model", "units", "holdout", "independent_unit", "uncertainty"):
            if not _nonempty_text(record.get(key)):
                reasons.append(f"invalid:measurement_validity:{key}")
        if not _texts(record.get("controls")):
            reasons.append("invalid:measurement_validity:controls")
    for key in ("replication", "human_review", "ethics_review"):
        review = candidate.get(key)
        if not isinstance(review, dict):
            reasons.append(f"invalid:{key}")
            continue
        record = cast(dict[str, object], review)
        if record.get("status") not in {"PENDING", "RECEIVED_UNVERIFIED", "VERIFIED_EXTERNALLY", "REJECTED"}:
            reasons.append(f"invalid:{key}:status")
        if not all(field in record for field in ("reviewer", "artifact", "independence", "authentication")):
            reasons.append(f"incomplete:{key}")
        if not _nonempty_text(record.get("independence")) or not _nonempty_text(record.get("authentication")):
            reasons.append(f"invalid:{key}:provenance")
        if record.get("status") == "REJECTED":
            reasons.append(f"rejected:{key}")
    return {
        "status": "INCOMPLETE" if reasons else "READY_FOR_EXTERNAL_REVIEW",
        "reasons": sorted(set(reasons)),
        "authority": "candidate_only",
        "accepted_evidence": False,
        "reviewer_identity_authenticated": False,
        "raw_artifact_bytes_verified": False,
        "consciousness_inference": "not_established",
    }
