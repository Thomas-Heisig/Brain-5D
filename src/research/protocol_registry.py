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
    "sustained_activity_stability_v1": "run_sustained_stability",
    "msba_energy_efficiency_v1": "run_msba_e01",
    "msba_resource_allocation_v1": "run_msba_e02",
    "msba_visual_roi_v1": "run_msba_e03",
    "msba_digital_integrity_v1": "run_msba_e04",
    "msba_modality_compensation_v1": "run_msba_e05",
    "embodied_closed_loop_v1": "run_embodied_closed_loop",
    "embodied_proprioception_v1": "run_embodied_proprioception",
    "embodied_perturbation_screen_v1": "run_embodied_perturbation",
    "connectome_topology_screen_v1": "run_connectome_topology",
    "embodied_controller_attribution_v1": "run_embodied_controller",
    "embodied_timing_v1": "run_embodied_timing",
}


class PreregistrationError(ValueError):
    """Raised when a scientific protocol lacks a valid frozen preregistration."""


def _json_object(path: Path) -> dict[str, Any]:
    raw: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise PreregistrationError(f"JSON root must be an object: {path}")
    return cast(dict[str, Any], raw)


def load_operational_protocols(research_root: Path) -> list[dict[str, Any]]:
    paths = [research_root / PROTOCOL_FILE]
    paths.extend(sorted((research_root / "protocols").glob("*.operational.json")))
    protocols: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in paths:
        if not path.is_file():
            continue
        values = _json_object(path).get("protocols")
        if not isinstance(values, list):
            raise PreregistrationError("Operational protocol registry is malformed.")
        for item in cast(list[Any], values):
            if not isinstance(item, dict):
                raise PreregistrationError("Operational protocol must be an object.")
            item = cast(dict[str, Any], item)
            identifier = item.get("id")
            if not isinstance(identifier, str) or not identifier or identifier in seen:
                raise PreregistrationError(
                    "Missing or duplicate operational protocol ID."
                )
            seen.add(identifier)
            protocols.append(item)
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
            f"Protocol '{protocol_id}' requires at least {minimum_value} independent "
            f"seeds; got {seed_count}."
        )
    return prereg


def _condition_label(item: object) -> str:
    if isinstance(item, dict):
        mapping = cast(dict[str, Any], item)
        condition_id = (
            mapping.get("id") or mapping.get("condition_id") or mapping.get("name")
        )
        role = mapping.get("role")
        if condition_id:
            return f"{condition_id}{f' ({role})' if role else ''}"
        return ""
    return str(item) if item else ""


def protocol_catalog(research_root: Path) -> list[dict[str, Any]]:
    """Return operational protocols enriched with their frozen user-facing contract.

    The dashboard uses this payload to show the scientific execution requirements
    before a run starts. The data is read only from the registered protocol and its
    frozen preregistration, so the UI cannot silently invent or weaken requirements.
    """
    catalog: list[dict[str, Any]] = []
    for protocol in load_operational_protocols(research_root):
        protocol_id = protocol.get("id")
        question_id = protocol.get("research_question")
        hypothesis_id = protocol.get("hypothesis")
        prereg_value = protocol.get("preregistration")
        if not isinstance(protocol_id, str) or not isinstance(question_id, str):
            raise PreregistrationError("Operational protocol ID/RQ must be strings.")
        if not isinstance(hypothesis_id, str):
            raise PreregistrationError(
                "Operational protocol hypothesis must be a string."
            )
        if not isinstance(prereg_value, str) or not prereg_value:
            raise PreregistrationError(
                "Operational protocol lacks preregistration path."
            )

        prereg_path = research_root / prereg_value
        prereg = _json_object(prereg_path)
        _validate_prereg_object(prereg, protocol=protocol)
        seed_strategy = cast(dict[str, Any], prereg["seed_strategy"])
        analysis_plan = cast(dict[str, Any], prereg["analysis_plan"])
        minimum_seeds = int(seed_strategy.get("minimum_independent_seeds", 1))
        default_seed_expression = (
            "101" if minimum_seeds <= 1 else f"101-{100 + minimum_seeds}"
        )
        prereg_conditions_value: object = prereg.get("conditions", [])
        prereg_conditions = (
            cast(list[object], prereg_conditions_value)
            if isinstance(prereg_conditions_value, list)
            else []
        )
        condition_labels = [_condition_label(item) for item in prereg_conditions]
        condition_labels = [item for item in condition_labels if item]
        controls = [str(item) for item in protocol.get("controls", [])]
        treatments = [str(item) for item in protocol.get("treatments", [])]
        condition_profiles = {
            "standard": "; ".join(condition_labels),
            "controls": "; ".join(controls),
            "treatments": "; ".join(treatments),
        }

        catalog.append(
            {
                "id": protocol_id,
                "label": f"{protocol_id} — {question_id}",
                "research_question": question_id,
                "hypothesis": hypothesis_id,
                "mode": prereg.get("mode"),
                "preregistration": prereg_value,
                "default_ticks": protocol.get("default_ticks"),
                "tick_aware": protocol.get("tick_aware", False),
                "minimum_independent_seeds": minimum_seeds,
                "default_seed_expression": default_seed_expression,
                "seed_rule": seed_strategy.get("rule"),
                "condition_profiles": condition_profiles,
                "conditions": prereg_conditions,
                "controls": protocol.get("controls", []),
                "treatments": protocol.get("treatments", []),
                "primary_outcomes": prereg.get("primary_outcomes", []),
                "secondary_outcomes": prereg.get("secondary_outcomes", []),
                "inclusion_criteria": prereg.get("inclusion_criteria", []),
                "exclusion_criteria": prereg.get("exclusion_criteria", []),
                "inference_policy": analysis_plan.get("inference_policy"),
                "freeze": prereg.get("freeze", {}),
            }
        )
    return catalog
