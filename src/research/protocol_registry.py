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
    "memory_delayed_information_v1": "run_memory_delayed_information",
    "world_model_prediction_v1": "run_world_model_prediction",
    "behavior_profile_control_v1": "run_behavior_profile_control",
}
OPERATIONAL_RUNNERS.update(
    {f"cog_cns_{number}_v1": f"run_cog_cns_{number}_v1" for number in range(101, 118)}
)
OPERATIONAL_RUNNERS.update(
    {
        "cog_epi_101_v1": "run_cog_epi_101_v1",
        "cog_epi_102_v1": "run_cog_epi_102_v1",
        "cog_wel_101_v1": "run_cog_wel_101_v1",
        "cog_wel_102_v1": "run_cog_wel_102_v1",
        "cog_wel_103_v1": "run_cog_wel_103_v1",
    }
)


OPERATIONAL_RUNNERS.update(
    {
        "dimensional_connectivity_v1": "run_eval_dimensional",
        "native_association_holdout_v1": "run_eval_association",
        "brian2_single_neuron_v1": "run_eval_brian2",
        "active_scaling_v1": "run_eval_scaling",
        "active_scaling_v2": "run_eval_scaling_v2",
    }
)


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
        for value in cast(list[object], values):
            if not isinstance(value, dict):
                raise PreregistrationError("Operational protocol must be an object.")
            item = cast(dict[str, Any], value)
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


def _merge_bundle_preregistration(
    bundle: dict[str, Any], protocol: dict[str, Any]
) -> dict[str, Any]:
    """Resolve one immutable preregistration from a versioned bundle."""
    protocol_id = protocol.get("id")
    values = bundle.get("preregistrations")
    if not isinstance(protocol_id, str) or not isinstance(values, dict):
        raise PreregistrationError("Bundled preregistration is malformed.")
    raw = cast(dict[str, Any], values).get(protocol_id)
    if not isinstance(raw, dict):
        raise PreregistrationError(
            f"Bundled preregistration lacks protocol '{protocol_id}'."
        )
    defaults_value = bundle.get("defaults")
    if not isinstance(defaults_value, dict):
        raise PreregistrationError("Bundled preregistration defaults are malformed.")
    resolved = {
        **cast(dict[str, Any], defaults_value),
        **cast(dict[str, Any], raw),
    }
    execution_kind = resolved.get("execution_kind", protocol.get("execution_kind"))
    if execution_kind != protocol.get("execution_kind"):
        raise PreregistrationError("Bundled execution kind disagrees with protocol.")
    if execution_kind == "conceptual_audit":
        audit_defaults = bundle.get("audit_defaults")
        if not isinstance(audit_defaults, dict):
            raise PreregistrationError("Audit preregistration defaults are malformed.")
        resolved = {**cast(dict[str, Any], audit_defaults), **resolved}
    resolved.update(
        {
            "schema_version": "1.0",
            "preregistration_id": (
                f"{bundle.get('bundle_id', 'PREREG-BUNDLE')}:{protocol_id}"
            ),
            "protocol_id": protocol_id,
            "freeze": bundle.get("freeze"),
        }
    )
    return resolved


def _load_preregistration(
    research_root: Path, protocol: dict[str, Any]
) -> tuple[dict[str, Any], Path]:
    value = protocol.get("preregistration")
    if not isinstance(value, str) or not value:
        raise PreregistrationError("Operational protocol lacks preregistration path.")
    path = research_root / value
    if not path.is_file():
        raise PreregistrationError(f"Preregistration artifact not found: {value}")
    raw = _json_object(path)
    if "preregistrations" in raw:
        return _merge_bundle_preregistration(raw, protocol), path
    return raw, path


def _validate_prereg_object(
    prereg: dict[str, Any], *, protocol: dict[str, Any]
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
    if (
        not isinstance(outcomes, list)
        or not outcomes
        or not all(
            isinstance(item, str) and item for item in cast(list[object], outcomes)
        )
    ):
        raise PreregistrationError("primary_outcomes must be a non-empty string list.")
    conditions = prereg.get("conditions")
    if not isinstance(conditions, list) or not conditions:
        raise PreregistrationError("conditions must be a non-empty list.")
    seed_strategy = prereg.get("seed_strategy")
    if not isinstance(seed_strategy, dict):
        raise PreregistrationError("seed_strategy must be an object.")
    minimum = cast(dict[str, Any], seed_strategy).get("minimum_independent_seeds")
    if isinstance(minimum, bool) or not isinstance(minimum, int) or minimum < 1:
        raise PreregistrationError(
            "seed_strategy.minimum_independent_seeds must be a positive integer."
        )
    freeze = prereg.get("freeze")
    if not isinstance(freeze, dict):
        raise PreregistrationError("freeze must be an object.")
    frozen = cast(dict[str, Any], freeze)
    if frozen.get("immutable_after_first_run") is not True:
        raise PreregistrationError("Preregistration must be immutable after first run.")
    if frozen.get("human_review_required") is not True:
        raise PreregistrationError("Preregistration must require human review.")
    if frozen.get("status") not in {"REGISTERED", "FROZEN", "AMENDED"}:
        raise PreregistrationError("Invalid preregistration freeze status.")


def validate_operational_protocol(
    research_root: Path,
    *,
    question_id: str,
    hypothesis_id: str,
    protocol_id: str,
    seed_count: int,
) -> dict[str, Any]:
    """Validate RQ/H/protocol linkage and return its frozen preregistration."""
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
    prereg, _ = _load_preregistration(research_root, protocol)
    _validate_prereg_object(prereg, protocol=protocol)
    seed_strategy = cast(dict[str, Any], prereg["seed_strategy"])
    minimum = seed_strategy["minimum_independent_seeds"]
    if isinstance(minimum, bool) or not isinstance(minimum, int):
        raise PreregistrationError("Invalid minimum independent seed count.")
    if seed_count < minimum:
        raise PreregistrationError(
            f"Protocol '{protocol_id}' requires at least {minimum} independent "
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
    """Return operational protocols enriched with their frozen UI contract."""
    catalog: list[dict[str, Any]] = []
    for protocol in load_operational_protocols(research_root):
        protocol_id = protocol.get("id")
        question_id = protocol.get("research_question")
        hypothesis_id = protocol.get("hypothesis")
        if not all(
            isinstance(value, str)
            for value in (protocol_id, question_id, hypothesis_id)
        ):
            raise PreregistrationError("Operational protocol ID/RQ/H must be strings.")
        prereg, _ = _load_preregistration(research_root, protocol)
        _validate_prereg_object(prereg, protocol=protocol)
        seed_strategy = cast(dict[str, Any], prereg["seed_strategy"])
        analysis_plan = cast(dict[str, Any], prereg["analysis_plan"])
        minimum_seeds = int(seed_strategy.get("minimum_independent_seeds", 1))
        default_seed_expression = (
            "101" if minimum_seeds <= 1 else f"101-{100 + minimum_seeds}"
        )
        explicit_seeds = seed_strategy.get("seeds")
        if isinstance(explicit_seeds, list):
            values = cast(list[object], explicit_seeds)
            if len(values) < minimum_seeds or any(
                isinstance(value, bool) or not isinstance(value, int)
                for value in values
            ):
                raise PreregistrationError("Invalid explicit protocol seeds.")
            default_seed_expression = ",".join(str(value) for value in values)
        raw_conditions = prereg.get("conditions", [])
        condition_values = (
            cast(list[object], raw_conditions)
            if isinstance(raw_conditions, list)
            else []
        )
        condition_labels = [
            label for value in condition_values if (label := _condition_label(value))
        ]
        controls = [str(item) for item in protocol.get("controls", [])]
        treatments = [str(item) for item in protocol.get("treatments", [])]
        catalog.append(
            {
                "id": protocol_id,
                "label": f"{protocol_id} — {question_id}",
                "research_question": question_id,
                "hypothesis": hypothesis_id,
                "mode": prereg.get("mode"),
                "preregistration": protocol.get("preregistration"),
                "default_ticks": protocol.get("default_ticks"),
                "tick_aware": protocol.get("tick_aware", False),
                "minimum_independent_seeds": minimum_seeds,
                "default_seed_expression": default_seed_expression,
                "seed_rule": seed_strategy.get("rule"),
                "condition_profiles": {
                    "standard": "; ".join(condition_labels),
                    "controls": "; ".join(controls),
                    "treatments": "; ".join(treatments),
                },
                "conditions": condition_values,
                "controls": controls,
                "treatments": treatments,
                "primary_outcomes": prereg.get("primary_outcomes", []),
                "secondary_outcomes": prereg.get("secondary_outcomes", []),
                "inclusion_criteria": prereg.get("inclusion_criteria", []),
                "exclusion_criteria": prereg.get("exclusion_criteria", []),
                "inference_policy": analysis_plan.get("inference_policy"),
                "freeze": prereg.get("freeze", {}),
                "execution_kind": protocol.get("execution_kind"),
                "adapter_validated": protocol.get("adapter_validated", False),
            }
        )
    return catalog
