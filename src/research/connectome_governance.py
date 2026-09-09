"""Fail-closed boundaries for the connectome/embodiment research extension.

Registration and successful technical execution are not accepted scientific
EVID. These guards constrain the standard workflow and EvidenceEngine, not
arbitrary Python code or independent runtime stop/isolate operations.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, cast

PROGRAM = Path("protocols/CONNECTOME_EMBODIMENT_V1.json")
PROTECTED_HYPOTHESES = frozenset(
    {
        "H-EMB-001-B",
        "H-EMB-002-A",
        "H-EMB-003-A",
        "H-EMB-004-A",
        "H-MSBA-E05-B",
        "H-REG-002-B",
        "H-EMB-007-A",
        "H-EMB-008-A",
        "H-CONN-001-A",
        "H-CONN-002-A",
        "H-EMB-009-A",
        "H-TIME-002-A",
    }
)
PROTECTED_QUESTIONS = frozenset(
    {
        "RQ-EMB-002",
        "RQ-EMB-003",
        "RQ-EMB-004",
        "RQ-EMB-007",
        "RQ-EMB-008",
        "RQ-CONN-001",
        "RQ-CONN-002",
        "RQ-EMB-009",
        "RQ-TIME-002",
    }
)


class ConnectomeGovernanceError(ValueError):
    """A study cannot be relabelled as a generic run or accepted evidence."""


def connectome_catalog(research_root: Path) -> list[dict[str, Any]]:
    path = research_root / PROGRAM
    if not path.is_file():
        return []
    if path.stat().st_size > 262144:
        raise ConnectomeGovernanceError("Oversized connectome programme")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ConnectomeGovernanceError("Programme must be an object")
    raw = cast(dict[str, Any], raw)
    if raw.get("automatic_evidence_promotion") is not False:
        raise ConnectomeGovernanceError(
            "Programme may not grant itself evidence authority"
        )
    values = raw.get("protocols")
    if not isinstance(values, list):
        raise ConnectomeGovernanceError("Malformed programme protocols")
    ids: set[str] = set()
    result: list[dict[str, Any]] = []
    for value in cast(list[object], values):
        if not isinstance(value, dict):
            raise ConnectomeGovernanceError("Malformed programme entry")
        value = cast(dict[str, Any], value)
        identifier = value.get("id")
        if not isinstance(identifier, str) or not identifier or identifier in ids:
            raise ConnectomeGovernanceError("Missing/duplicate programme ID")
        if value.get("hypothesis") not in PROTECTED_HYPOTHESES:
            raise ConnectomeGovernanceError(
                "Programme hypothesis lacks a launch/promotion guard"
            )
        if value.get("automatic_evidence_promotion") is not False:
            raise ConnectomeGovernanceError("Protocol cannot promote itself")
        ids.add(identifier)
        result.append(value)
    return result


def guard_connectome_launch(
    research_root: Path,
    question_id: str,
    hypothesis_id: str,
    protocol_id: str,
) -> None:
    protected = (
        hypothesis_id in PROTECTED_HYPOTHESES
        or question_id in PROTECTED_QUESTIONS
        or protocol_id.startswith(("embodied_", "connectome_"))
    )
    if not protected:
        return
    verify_design_lock(research_root)
    from src.research.connectome_embodiment import RUNNERS

    matches = [
        item
        for item in connectome_catalog(research_root)
        if item["id"] == protocol_id
        and item.get("research_question") == question_id
        and item.get("hypothesis") == hypothesis_id
    ]
    if len(matches) != 1 or protocol_id not in RUNNERS:
        raise ConnectomeGovernanceError(
            "CONNECTOME_ADAPTER_NOT_VALIDATED: no generic ticks/PING substitution; "
            "select a matching native exploratory protocol or complete adapter review."
        )
    record = matches[0]
    if (
        record.get("implementation_status") != "NATIVE_EXPLORATORY_SCREEN"
        or record.get("runner") != RUNNERS[protocol_id]
    ):
        raise ConnectomeGovernanceError("Connectome runner/status mismatch")


def guard_connectome_promotion(hypothesis_id: str, claim_id: str) -> None:
    if hypothesis_id in PROTECTED_HYPOTHESES or claim_id.startswith("CLAIM-CONN-"):
        raise ConnectomeGovernanceError(
            "CONNECTOME_EXTERNAL_REVIEW_REQUIRED: synthetic screens and registered "
            "designs cannot automatically become accepted EVID."
        )


def verify_design_lock(research_root: Path) -> None:
    """Check versioned design bytes, not truth or human approval."""
    path = research_root / "protocols/connectome.design-lock.json"
    if not path.is_file() or path.stat().st_size > 65536:
        raise ConnectomeGovernanceError("Missing or oversized connectome design lock")
    raw: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ConnectomeGovernanceError("Malformed connectome design lock")
    lock = cast(dict[str, Any], raw)
    values = lock.get("sha256")
    if not isinstance(values, dict):
        raise ConnectomeGovernanceError("Missing design hashes")
    hashes = cast(dict[str, Any], values)
    expected = {
        "protocols/CONNECTOME_EMBODIMENT_V1.json",
        "protocols/connectome.operational.json",
    }
    expected.update(
        str(record["preregistration"]) for record in connectome_catalog(research_root)
    )
    if set(hashes) != expected:
        raise ConnectomeGovernanceError("Design lock inventory mismatch")
    for relative, expected_digest in hashes.items():
        target = (research_root / relative).resolve()
        if not target.is_relative_to(research_root.resolve()) or not target.is_file():
            raise ConnectomeGovernanceError("Invalid design lock path")
        if target.stat().st_size > 262144:
            raise ConnectomeGovernanceError("Oversized locked design")
        if hashlib.sha256(target.read_bytes()).hexdigest() != expected_digest:
            raise ConnectomeGovernanceError(
                "Design changed without versioned review: " + relative
            )
