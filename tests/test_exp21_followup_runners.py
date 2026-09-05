from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from src.research.followup_experiments import (
    run_5d_matched,
    run_performance_profile,
    run_recurrence_map,
    run_temporal_order,
)

ROOT = Path(__file__).resolve().parents[1]


def _config() -> dict[str, Any]:
    loaded = yaml.safe_load(
        (ROOT / "configs" / "learning_experiment.yaml").read_text(encoding="utf-8")
    )
    assert isinstance(loaded, dict)
    return loaded


def test_recurrence_map_has_control_and_treatment() -> None:
    runs = run_recurrence_map(_config(), seeds=(42,), ticks=16)
    assert len(runs) == 15
    assert any(run.metrics["recurrent_weight"] == 0.0 for run in runs)
    assert any(run.metrics["recurrent_weight"] == 100.0 for run in runs)
    assert all(run.metrics["ticks_executed"] >= 16 for run in runs)


def test_topology_matched_5d_keeps_graph_contract() -> None:
    runs = run_5d_matched(_config(), seeds=(42,), ticks=8)
    assert {run.condition for run in runs} == {"1d", "2d", "3d", "5d"}
    assert all(run.metrics["matched_neuron_count"] == 3 for run in runs)
    assert all(run.metrics["matched_synapse_count"] == 2 for run in runs)


def test_temporal_order_is_spike_carrying() -> None:
    runs = run_temporal_order(_config(), seeds=(42,), ticks=12)
    assert {run.condition for run in runs} == {"forward", "reverse", "simultaneous"}
    assert all(run.metrics["ticks_executed"] == 12 for run in runs)
    assert all(run.metrics["total_spikes"] > 0 for run in runs)


def test_performance_profile_reports_subsystem_times() -> None:
    runs = run_performance_profile(_config(), seeds=(42,), ticks=25)
    assert len(runs) == 1
    metrics = runs[0].metrics
    assert metrics["ticks_executed"] == 25
    assert metrics["construction_seconds"] >= 0.0
    assert metrics["core_step_seconds"] >= 0.0
    assert metrics["digest_seconds"] >= 0.0
    assert metrics["ticks_per_second"] > 0.0
