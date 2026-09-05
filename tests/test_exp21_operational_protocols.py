from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from src.research.protocol_registry import (
    PreregistrationError,
    load_operational_protocols,
    validate_operational_protocol,
)

ROOT = Path(__file__).resolve().parents[1] / "research"

EXPECTED = {
    "RQ-REC-001": ("H-REC-001-A", "recurrence_map_v1", 20),
    "RQ-GEN-001": ("H-GEN-001-A", "learning_generalization_v1", 20),
    "RQ-REPL-001": ("H-REPL-001-A", "independent_replication_v1", 20),
    "RQ-5D-005": ("H-5D-005-A", "topology_matched_5d_v1", 30),
    "RQ-REG-002": ("H-REG-002-A", "closed_loop_regulation_v1", 20),
    "RQ-TEMP-002": ("H-TEMP-002-A", "temporal_order_spiking_v1", 20),
    "RQ-PERF-001": ("H-PERF-001-A", "subsystem_performance_v1", 10),
    "RQ-REC-002": ("H-REC-002-A", "recurrence_scale_v1", 20),
    "RQ-LEARN-INTERF-001": (
        "H-LEARN-INTERF-001-A",
        "learning_interference_screen_v1",
        20,
    ),
}


def _yaml_ids(path: Path) -> set[str]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(payload, list)
    return {str(item["id"]) for item in payload if isinstance(item, dict)}


def test_followup_questions_and_hypotheses_are_canonical() -> None:
    questions = _yaml_ids(ROOT / "registry" / "questions.yaml")
    hypotheses = _yaml_ids(ROOT / "registry" / "hypotheses.yaml")
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
