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

OPERATIONAL_RUNNERS: dict[str, str] = {
    "recurrence_map_v1": "run_recurrence_map",
    "learning_generalization_v1": "run_generalization",
    "independent_replication_v1": "run_replication",
    "topology_matched_5d_v1": "run_5d_matched",
    "closed_loop_regulation_v1": "run_regulation_recovery",
    "temporal_order_spiking_v1": "run_temporal_order",
    "subsystem_performance_v1": "run_performance_profile",
    "recurrence_scale_v1": "run_recurrence_scale",
    "learning_interference_screen_v1": "run_learning_interference",
}


class PreregistrationError(ValueError):
    """Raised when a scientific protocol lacks a valid frozen preregistration."""


def _json_object(path: Path) -> dict[str, Any]:
    raw: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise PreregistrationError(f"JSON root must be an object: {path}")
    return cast(dict[str, Any], raw)


def load_operational_protocols(research_root: Path) -> list[dict[str, Any]]:
    path = research_root / PROTOCOL_FILE
    if not path.is_file():
        return []
    raw = _json_object(path)
    protocol_values: object = raw.get("protocols")
    if not isinstance(protocol_values, list):
        raise PreregistrationError("Operational protocol registry is malformed.")
    protocols: list[dict[str, Any]] = []
    for item_value in cast(list[object], protocol_values):
        if isinstance(item_value, dict):
            protocols.append(cast(dict[str, Any], item_value))
    return protocols


def protocol_by_id(research_root: Path, protocol_id: str) -> dict[str, Any] | None:
    return next(
        (
            protocol
            for protocol in load_operational_protocols(research_root)
            if protocol.get("id") == protocol_id
        ),
        None,
    )


def protocol_for_question(
    research_root: Path, question_id: str
) -> dict[str, Any] | None:
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
    outcomes_value: object = prereg.get("primary_outcomes")
    if not isinstance(outcomes_value, list):
        raise PreregistrationError("primary_outcomes must be a non-empty string list.")
    outcomes = cast(list[object], outcomes_value)
    if not outcomes or not all(isinstance(item, str) and item for item in outcomes):
        raise PreregistrationError("primary_outcomes must be a non-empty string list.")
    conditions_value: object = prereg.get("conditions")
    if not isinstance(conditions_value, list) or not conditions_value:
        raise PreregistrationError("conditions must be a non-empty list.")
    seed_strategy_value: object = prereg.get("seed_strategy")
    if not isinstance(seed_strategy_value, dict):
        raise PreregistrationError("seed_strategy must be an object.")
    seed_strategy = cast(dict[str, Any], seed_strategy_value)
    minimum: object = seed_strategy.get("minimum_independent_seeds")
    if isinstance(minimum, bool) or not isinstance(minimum, int) or minimum < 1:
        raise PreregistrationError(
            "seed_strategy.minimum_independent_seeds must be a positive integer."
        )
    freeze_value: object = prereg.get("freeze")
    if not isinstance(freeze_value, dict):
        raise PreregistrationError("freeze must be an object.")
    freeze = cast(dict[str, Any], freeze_value)
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
    prereg_value: object = protocol.get("preregistration")
    if not isinstance(prereg_value, str) or not prereg_value:
        raise PreregistrationError("Operational protocol lacks preregistration path.")
    prereg_path = research_root / prereg_value
    if not prereg_path.is_file():
        raise PreregistrationError(
            f"Preregistration artifact not found: {prereg_value}"
        )
    prereg = _json_object(prereg_path)
    _validate_prereg_object(prereg, protocol=protocol)
    seed_strategy_value: object = prereg["seed_strategy"]
    if not isinstance(seed_strategy_value, dict):
        raise PreregistrationError("seed_strategy must be an object.")
    seed_strategy = cast(dict[str, Any], seed_strategy_value)
    minimum_value: object = seed_strategy["minimum_independent_seeds"]
    if isinstance(minimum_value, bool) or not isinstance(minimum_value, int):
        raise PreregistrationError("Invalid minimum independent seed count.")
    if seed_count < minimum_value:
        raise PreregistrationError(
            f"Protocol '{protocol_id}' requires at least {minimum_value} independent seeds; got {seed_count}."
        )
    return prereg


def protocol_catalog(research_root: Path) -> list[dict[str, str]]:
    catalog: list[dict[str, str]] = []
    for protocol in load_operational_protocols(research_root):
        protocol_id = protocol.get("id")
        question_id = protocol.get("research_question")
        if not isinstance(protocol_id, str) or not isinstance(question_id, str):
            raise PreregistrationError("Operational protocol ID/RQ must be strings.")
        catalog.append({"id": protocol_id, "label": f"{protocol_id} — {question_id}"})
    return catalog
