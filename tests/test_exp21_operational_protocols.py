from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import pytest
import yaml

from src.research.protocol_registry import (
    PreregistrationError,
    load_operational_protocols,
    validate_operational_protocol,
)

ROOT = Path(__file__).resolve().parents[1] / "research"

EXPECTED = {
    "RQ-SNN-001": ("H-SNN-001-A", "sustained_activity_stability_v1", 10),
    "RQ-REC-001": ("H-REC-001-A", "recurrence_map_v1", 20),
    "RQ-GEN-001": ("H-GEN-001-A", "learning_generalization_v1", 20),
    "RQ-REPL-001": ("H-REPL-001-A", "independent_replication_v1", 20),
    "RQ-5D-005": ("H-5D-005-A", "topology_matched_5d_v1", 30),
    "RQ-REG-002": ("H-REG-002-A", "closed_loop_regulation_v1", 20),
    "RQ-TEMP-002": ("H-TEMP-002-A", "temporal_order_spiking_v1", 20),
    "RQ-PERF-001": ("H-PERF-001-A", "subsystem_performance_v1", 10),
    "RQ-REC-002": ("H-REC-002-A", "recurrence_scale_v1", 20),
    "RQ-LIFE-001": (
        "H-LIFE-001-A",
        "learning_interference_screen_v1",
        20,
    ),
    "RQ-MSBA-E01": ("H-MSBA-E01-A", "msba_energy_efficiency_v1", 3),
    "RQ-MSBA-E02": ("H-MSBA-E02-A", "msba_resource_allocation_v1", 3),
    "RQ-MSBA-E03": ("H-MSBA-E03-A", "msba_visual_roi_v1", 3),
    "RQ-MSBA-E04": ("H-MSBA-E04-A", "msba_digital_integrity_v1", 3),
    "RQ-MSBA-E05": ("H-MSBA-E05-A", "msba_modality_compensation_v1", 3),
    "RQ-EMB-001": ("H-EMB-001-B", "embodied_closed_loop_v1", 3),
    "RQ-EMB-002": ("H-EMB-002-A", "embodied_proprioception_v1", 3),
    "RQ-EMB-004": ("H-EMB-004-A", "embodied_perturbation_screen_v1", 3),
    "RQ-CONN-002": ("H-CONN-002-A", "connectome_topology_screen_v1", 3),
    "RQ-EMB-009": ("H-EMB-009-A", "embodied_controller_attribution_v1", 3),
    "RQ-TIME-002": ("H-TIME-002-A", "embodied_timing_v1", 3),
}


def _yaml_ids(path: Path) -> set[str]:
    payload_value: object = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(payload_value, list)
    payload = cast(list[object], payload_value)
    ids: set[str] = set()
    for item_value in payload:
        if not isinstance(item_value, dict):
            continue
        item = cast(dict[str, Any], item_value)
        ids.add(str(item["id"]))
    return ids


def _registry_ids(prefix: str) -> set[str]:
    registry = ROOT / "registry"
    ids: set[str] = set()
    for path in sorted(registry.glob(f"{prefix}*.yaml")):
        ids.update(_yaml_ids(path))
    return ids


def test_followup_questions_and_hypotheses_are_canonical() -> None:
    questions = _registry_ids("questions")
    hypotheses = _registry_ids("hypotheses")
    assert set(EXPECTED).issubset(questions)
    assert {value[0] for value in EXPECTED.values()}.issubset(hypotheses)


def test_every_operational_protocol_has_a_valid_frozen_preregistration() -> None:
    protocols = load_operational_protocols(ROOT)
    assert {str(item["research_question"]) for item in protocols} == set(EXPECTED)

    for question_id, (hypothesis_id, protocol_id, minimum_seeds) in EXPECTED.items():
        prereg = validate_operational_protocol(
            ROOT,
            question_id=question_id,
            hypothesis_id=hypothesis_id,
            protocol_id=protocol_id,
            seed_count=minimum_seeds,
        )
        if protocol_id.startswith(("embodied_", "connectome_")):
            assert prereg["freeze"]["status"] == "REGISTERED"
            assert prereg["mode"] == "EXPLORATORY"
            assert prereg["freeze"]["human_review"] == "not_recorded"
        else:
            assert prereg["freeze"]["status"] == "FROZEN"
        assert prereg["freeze"]["immutable_after_first_run"] is True
        assert prereg["freeze"]["human_review_required"] is True


def test_preregistration_gate_rejects_underpowered_seed_request() -> None:
    with pytest.raises(PreregistrationError, match="at least 20"):
        validate_operational_protocol(
            ROOT,
            question_id="RQ-REC-001",
            hypothesis_id="H-REC-001-A",
            protocol_id="recurrence_map_v1",
            seed_count=3,
        )
