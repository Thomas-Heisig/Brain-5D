"""Operational follow-up protocol registry and preregistration gate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

PROTOCOL_FILE = Path("protocols/EXP_GEN_0021_OPERATIONAL_PROTOCOLS.json")
PREREG_REQUIRED = {
    "schema_version",
    "preregistration_id",
    "research_question",
    "hypothesis",
    "protocol_id",
    "mode",
    "primary_outcomes",
    "conditions",
    "seed_strategy",
    "stopping_rule",
    "inclusion_criteria",
    "exclusion_criteria",
    "analysis_plan",
    "freeze",
}


class PreregistrationError(ValueError):
    """Raised when a scientific protocol lacks a valid frozen preregistration."""


def load_operational_protocols(research_root: Path) -> list[dict[str, Any]]:
    path = research_root / PROTOCOL_FILE
    if not path.is_file():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("protocols"), list):
        raise PreregistrationError("Operational protocol registry is malformed.")
    return [
        cast(dict[str, Any], item)
        for item in raw["protocols"]
        if isinstance(item, dict)
    ]


def protocol_by_id(research_root: Path, protocol_id: str) -> dict[str, Any] | None:
    return next(
        (
            protocol
            for protocol in load_operational_protocols(research_root)
            if protocol.get("id") == protocol_id
        ),
        None,
    )


def protocol_for_question(research_root: Path, question_id: str) -> dict[str, Any] | None:
    matches = [
        protocol
        for protocol in load_operational_protocols(research_root)
        if protocol.get("research_question") == question_id
    ]
    if len(matches) > 1:
        raise PreregistrationError(
            f"More than one operational protocol is registered for {question_id}."
        )
    return matches[0] if matches else None


def _validate_prereg_object(
    prereg: dict[str, Any],
    *,
    protocol: dict[str, Any],
) -> None:
    missing = sorted(PREREG_REQUIRED - set(prereg))
    if missing:
        raise PreregistrationError(
            f"Preregistration is missing required fields: {', '.join(missing)}"
        )
    if prereg.get("schema_version") != "1.0":
        raise PreregistrationError("Unsupported preregistration schema version.")
    for key, protocol_key in (
        ("research_question", "research_question"),
        ("hypothesis", "hypothesis"),
        ("protocol_id", "id"),
    ):
        if prereg.get(key) != protocol.get(protocol_key):
            raise PreregistrationError(
                f"Preregistration {key} does not match operational protocol."
            )
    outcomes = prereg.get("primary_outcomes")
    if not isinstance(outcomes, list) or not outcomes or not all(
        isinstance(item, str) and item for item in outcomes
    ):
        raise PreregistrationError("primary_outcomes must be a non-empty string list.")
    conditions = prereg.get("conditions")
    if not isinstance(conditions, list) or not conditions:
        raise PreregistrationError("conditions must be a non-empty list.")
    seed_strategy = prereg.get("seed_strategy")
    if not isinstance(seed_strategy, dict):
        raise PreregistrationError("seed_strategy must be an object.")
    minimum = seed_strategy.get("minimum_independent_seeds")
    if isinstance(minimum, bool) or not isinstance(minimum, int) or minimum < 1:
        raise PreregistrationError(
            "seed_strategy.minimum_independent_seeds must be a positive integer."
        )
    freeze = prereg.get("freeze")
    if not isinstance(freeze, dict):
        raise PreregistrationError("freeze must be an object.")
    if freeze.get("immutable_after_first_run") is not True:
        raise PreregistrationError("Preregistration must be immutable after first run.")
    if freeze.get("human_review_required") is not True:
        raise PreregistrationError("Preregistration must require human review.")
    if freeze.get("status") not in {"REGISTERED", "FROZEN", "AMENDED"}:
        raise PreregistrationError("Invalid preregistration freeze status.")


def validate_operational_protocol(
    research_root: Path,
    *,
    question_id: str,
    hypothesis_id: str,
    protocol_id: str,
    seed_count: int,
) -> dict[str, Any]:
    """Validate RQ/H/protocol linkage and return the frozen preregistration."""
    protocol = protocol_by_id(research_root, protocol_id)
    if protocol is None:
        raise PreregistrationError(f"Unknown operational protocol '{protocol_id}'.")
    if protocol.get("research_question") != question_id:
        raise PreregistrationError(
            f"Protocol '{protocol_id}' is not registered for {question_id}."
        )
    if protocol.get("hypothesis") != hypothesis_id:
        raise PreregistrationError(
            f"Protocol '{protocol_id}' is not registered for {hypothesis_id}."
        )
    prereg_value = protocol.get("preregistration")
    if not isinstance(prereg_value, str) or not prereg_value:
        raise PreregistrationError("Operational protocol lacks preregistration path.")
    prereg_path = research_root / prereg_value
    if not prereg_path.is_file():
        raise PreregistrationError(
            f"Preregistration artifact not found: {prereg_value}"
        )
    raw = json.loads(prereg_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise PreregistrationError("Preregistration root must be an object.")
    prereg = cast(dict[str, Any], raw)
    _validate_prereg_object(prereg, protocol=protocol)
    seed_strategy = cast(dict[str, Any], prereg["seed_strategy"])
    minimum = int(seed_strategy["minimum_independent_seeds"])
    if seed_count < minimum:
        raise PreregistrationError(
            f"Protocol '{protocol_id}' requires at least {minimum} independent seeds; got {seed_count}."
        )
    return prereg


def protocol_catalog(research_root: Path) -> list[dict[str, str]]:
    return [
        {
            "id": str(protocol["id"]),
            "label": f"{protocol['id']} — {protocol['research_question']}",
        }
        for protocol in load_operational_protocols(research_root)
    ]
