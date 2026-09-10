from __future__ import annotations

from pathlib import Path

import pytest

from src.research.cognition_experiments import (
    run_behavior_profile_control,
    run_memory_delayed_information,
    run_methodological_audit,
    run_world_model_prediction,
)
from src.research.cognition_governance import (
    CognitionGovernanceError,
    guard_cognition_launch,
)
from src.research.protocol_registry import (
    OPERATIONAL_RUNNERS,
    protocol_for_question,
    validate_operational_protocol,
)

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"


def _by_condition(runs: list[object], condition: str) -> list[object]:
    return [run for run in runs if getattr(run, "condition") == condition]


def test_memory_delayed_information_uses_independent_real_controls() -> None:
    seeds = (101, 102, 103)
    runs = run_memory_delayed_information({}, seeds)
    assert len(runs) == len(seeds) * 4
    treatment = _by_condition(runs, "memory_read_write")
    shuffled = _by_condition(runs, "memory_time_shuffled")
    read_off = _by_condition(runs, "memory_read_off")
    write_off = _by_condition(runs, "memory_write_off")
    assert all(run.metrics["accuracy"] == 1.0 for run in treatment)
    assert all(run.metrics["retrievals"] == 24 for run in treatment)
    assert any(run.metrics["accuracy"] < 1.0 for run in shuffled)
    assert all(run.metrics["retrievals"] == 0 for run in read_off)
    assert all(run.metrics["retrievals"] == 0 for run in write_off)
    assert all(run.metrics["target_leakage"] is False for run in runs)
    assert {run.seed for run in treatment} == set(seeds)


def test_world_model_has_holdout_and_beats_persistence_reference() -> None:
    runs = run_world_model_prediction({}, (101, 102, 103))
    adaptive = _by_condition(runs, "adaptive")
    persistence = _by_condition(runs, "persistence")
    assert len(runs) == 12
    assert all(run.metrics["held_out"] is True for run in runs)
    assert all(run.metrics["target_leakage"] is False for run in runs)
    assert all(run.metrics["world_model_influences_actions"] is False for run in runs)
    adaptive_mean = sum(run.metrics["mean_prediction_error"] for run in adaptive) / len(
        adaptive
    )
    persistence_mean = sum(
        run.metrics["mean_prediction_error"] for run in persistence
    ) / len(persistence)
    assert adaptive_mean < persistence_mean


def test_behavior_profile_control_uses_real_profile_causal_path() -> None:
    runs = run_behavior_profile_control({}, (101, 102, 103))
    assert len(runs) == 12
    adaptive = _by_condition(runs, "adaptive")
    fixed = _by_condition(runs, "fixed_low_exploration")
    assert all(run.metrics["update_count"] == 40 for run in adaptive)
    assert all(run.metrics["update_count"] == 0 for run in fixed)
    assert all(
        run.metrics["behavioral_causal_path"] == "BehaviorProfile.select_action"
        for run in runs
    )
    assert all(run.metrics["psychological_personality_claim"] is False for run in runs)


def test_methodological_audit_never_masquerades_as_empirical_evidence() -> None:
    runs = run_methodological_audit(
        {},
        (101, 102, 103),
        protocol_id="cog_cns_101_v1",
        question_id="RQ-CNS-101",
    )
    assert len(runs) == 12
    assert all(run.metrics["audit_complete"] is True for run in runs)
    assert all(run.metrics["native_empirical_experiment"] is False for run in runs)
    assert all(run.metrics["scientific_evidence"] is False for run in runs)
    assert all(run.metrics["consciousness_inference"] == "not_established" for run in runs)


@pytest.mark.parametrize(
    ("question_id", "hypothesis_id", "protocol_id"),
    [
        ("RQ-MEM-002", "H-MEM-002-A", "memory_delayed_information_v1"),
        ("RQ-WM-001", "H-WM-001-A", "world_model_prediction_v1"),
        ("RQ-PROFILE-001", "H-PROFILE-001-A", "behavior_profile_control_v1"),
        ("RQ-CNS-101", "H-CNS-101-A", "cog_cns_101_v1"),
        ("RQ-EPI-101", "H-EPI-101-A", "cog_epi_101_v1"),
        ("RQ-WEL-101", "H-WEL-101-A", "cog_wel_101_v1"),
    ],
)
def test_operational_cognition_protocols_are_validated_and_executable(
    question_id: str, hypothesis_id: str, protocol_id: str
) -> None:
    contract = protocol_for_question(RESEARCH, question_id)
    assert contract is not None
    assert contract["id"] == protocol_id
    assert contract["adapter_validated"] is True
    assert protocol_id in OPERATIONAL_RUNNERS
    prereg = validate_operational_protocol(
        RESEARCH,
        question_id=question_id,
        hypothesis_id=hypothesis_id,
        protocol_id=protocol_id,
        seed_count=3,
    )
    assert prereg["freeze"]["status"] == "FROZEN"
    guard_cognition_launch(RESEARCH, question_id, protocol_id)


def test_generic_runtime_fallback_is_blocked_for_native_cognition_questions() -> None:
    for question_id in ("RQ-MEM-002", "RQ-WM-001", "RQ-PROFILE-001", "RQ-CNS-101"):
        with pytest.raises(CognitionGovernanceError, match="No fallback"):
            guard_cognition_launch(RESEARCH, question_id, "runtime_ticks_v1")
