"""Fail-closed launch and candidate boundaries; never a consciousness detector.

These guards cover dashboard experiment entry points and EvidenceEngine writes,
not arbitrary Python processes or an already running simulation. Independent
stop/isolate actions must remain available. Local metadata is not external
review authentication, and a complete candidate is never accepted evidence.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, cast

PROGRAM = Path("protocols/COGNITION_CONSCIOUSNESS_V1.json")
PREFIXES = ("RQ-CNS-", "RQ-WEL-", "RQ-EPI-1")
HYPOTHESIS_PREFIXES = ("H-CNS-", "H-WEL-", "H-EPI-1")
MAX_RECORD_BYTES = 262144


class CognitionGovernanceError(ValueError):
    """A cognitive study cannot enter an unvalidated or held legacy path."""


def _read_record(path: Path) -> dict[str, Any]:
    try:
        if path.stat().st_size > MAX_RECORD_BYTES:
            raise CognitionGovernanceError("Oversized governance record")
        raw: object = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CognitionGovernanceError(
            "Unreadable governance record; launch blocked"
        ) from exc
    if not isinstance(raw, dict):
        raise CognitionGovernanceError("Governance record must be an object")
    return cast(dict[str, Any], raw)


def cognition_catalog(research_root: Path) -> list[dict[str, Any]]:
    """Expose proposals, without declaring native adapters operational."""
    path = research_root / PROGRAM
    if not path.is_file():
        return []
    values: object = _read_record(path).get("protocols")
    if not isinstance(values, list):
        raise CognitionGovernanceError("Cognition protocols must be a list")
    result: list[dict[str, Any]] = []
    ids: set[str] = set()
    for value in cast(list[object], values):
        if not isinstance(value, dict):
            raise CognitionGovernanceError("Malformed cognition protocol")
        item = cast(dict[str, Any], value)
        identifier = item.get("id")
        if (
            not isinstance(identifier, str)
            or not identifier.strip()
            or identifier in ids
        ):
            raise CognitionGovernanceError("Missing or duplicate cognition protocol ID")
        ids.add(identifier)
        if (
            item.get("consciousness_inference") != "not_established"
            or item.get("native_adapter_validated") is not False
        ):
            raise CognitionGovernanceError(
                "Catalogue cannot certify consciousness or an unimplemented adapter"
            )
        result.append(dict(item))
    return result


def guard_cognition_launch(
    research_root: Path, question_id: str, protocol: str
) -> None:
    """Reject protected launches and generic fallbacks; a payload cannot opt out."""
    protected = question_id.startswith(PREFIXES) or protocol.startswith("cog_")
    state_path = research_root / "ethics/operational_state.json"
    if state_path.exists():
        state = _read_record(state_path).get("state")
        if not isinstance(state, str) or state not in {
            "NORMAL",
            "REVIEW_REQUIRED",
            "HOLD",
        }:
            raise CognitionGovernanceError(
                "Invalid ethics state; new research launches blocked"
            )
        if state != "NORMAL":
            raise CognitionGovernanceError(
                "ETHICS_HOLD: new experiment launches blocked; stop/isolate remains available"
            )
    elif (research_root / PROGRAM).exists():
        raise CognitionGovernanceError(
            "Ethics state missing for installed programme; new launches blocked"
        )
    if protected:
        raise CognitionGovernanceError(
            "COGNITION_ADAPTER_NOT_VALIDATED: registered question/protocol; "
            "instruments are not native experiments. No fallback to generic "
            "ticks, PING or unrelated suites is permitted."
        )


def guard_cognition_promotion(hypothesis_id: str, claim_id: str) -> None:
    """Do not turn unreviewed indicators or instrument tests into accepted EVID."""
    if hypothesis_id.startswith(HYPOTHESIS_PREFIXES) or claim_id.startswith(
        ("CLAIM-CNS-", "CLAIM-WEL-", "CLAIM-EPI-1")
    ):
        raise CognitionGovernanceError(
            "INDEPENDENT_COGNITION_REVIEW_REQUIRED: automatic EVID promotion "
            "disabled for the new programme. Functional observations require a "
            "candidate dossier and external review, not a phenomenal verdict."
        )


def _nonempty_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _texts(value: object) -> bool:
    return (
        isinstance(value, list)
        and bool(cast(list[object], value))
        and all(_nonempty_text(item) for item in cast(list[object], value))
    )


def _matches(value: object, pattern: str) -> bool:
    return isinstance(value, str) and re.fullmatch(pattern, value) is not None


def assess_candidate(candidate: dict[str, object]) -> dict[str, object]:
    """Check metadata shape/consistency, not raw bytes, truth or reviewer identity.

    READY_FOR_EXTERNAL_REVIEW means only a structurally complete review request.
    Pending reviews are permitted, but no declaration can grant accepted EVID.
    """
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
    if (
        candidate.get("accepted_evidence") is not None
        and candidate.get("accepted_evidence") is not False
    ):
        reasons.append("candidate_cannot_accept_itself")
    question = candidate.get("question_id")
    hypothesis = candidate.get("hypothesis_id")
    protocol = candidate.get("protocol_id")
    if (
        isinstance(question, str)
        and isinstance(hypothesis, str)
        and isinstance(protocol, str)
    ):
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
                or not isinstance(role, str)
                or role
                not in {
                    "primary_observation",
                    "stimulus_schedule",
                    "state",
                    "configuration",
                }
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
        for key in (
            "observation_model",
            "units",
            "holdout",
            "independent_unit",
            "uncertainty",
        ):
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
        if not isinstance(record.get("status"), str) or record.get("status") not in {
            "PENDING",
            "RECEIVED_UNVERIFIED",
            "VERIFIED_EXTERNALLY",
            "REJECTED",
        }:
            reasons.append(f"invalid:{key}:status")
        if not all(
            field in record
            for field in ("reviewer", "artifact", "independence", "authentication")
        ):
            reasons.append(f"incomplete:{key}")
        if not _nonempty_text(record.get("independence")) or not _nonempty_text(
            record.get("authentication")
        ):
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
