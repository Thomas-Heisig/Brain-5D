from __future__ import annotations

from pathlib import Path

import yaml

from src.research.experiment_suite import run_sustained_stability
from src.research.protocol_registry import validate_operational_protocol

ROOT = Path(__file__).parents[1]


def test_sustained_stability_protocol_is_frozen_and_linked() -> None:
    prereg = validate_operational_protocol(
        ROOT / "research",
        question_id="RQ-SNN-001",
        hypothesis_id="H-SNN-001-A",
        protocol_id="sustained_activity_stability_v1",
        seed_count=10,
    )
    assert prereg["mode"] == "CONFIRMATORY"
    assert prereg["freeze"]["status"] == "FROZEN"
    assert prereg["seed_strategy"]["minimum_independent_seeds"] == 10


def test_sustained_stability_runner_records_control_and_drive_traces() -> None:
    config = yaml.safe_load(
        (ROOT / "configs" / "learning_experiment.yaml").read_text(encoding="utf-8")
    )
    runs = run_sustained_stability(config, seeds=(42, 43), ticks=1_000)
    assert len(runs) == 4
    assert {run.condition for run in runs} == {"no_input_control", "tonic_drive"}
    for run in runs:
        assert run.metrics["ticks_executed"] == 1_000
        assert len(run.metrics["spikes_per_tick"]) == 1_000
        assert run.metrics["finite_state"] is True
        assert run.metrics["topology_unchanged"] is True
    assert all(
        run.metrics["stability_pass"] for run in runs if run.condition == "tonic_drive"
    )
