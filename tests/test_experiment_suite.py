"""Focused tests for the executable scientific protocol runners."""

from pathlib import Path
from typing import Any, cast

import yaml

from src.research.experiment_suite import (
    run_learning_repeat,
    run_ping,
    run_ping_v2,
    run_regulation,
    run_stdp,
    run_temporal,
)


def _config() -> dict[str, Any]:
    loaded = yaml.safe_load(
        Path("configs/learning_experiment.yaml").read_text(encoding="utf-8")
    )
    assert isinstance(loaded, dict)
    return cast(dict[str, Any], loaded)


def test_ping_is_reproducible_for_identical_seed() -> None:
    first = run_ping(_config(), seeds=(42,))
    second = run_ping(_config(), seeds=(42,))
    assert first == second
    assert {run.condition for run in first} == {"recurrence_off", "recurrence_on"}


def test_ping_v2_repeats_identical_initial_states_and_responses() -> None:
    runs = run_ping_v2(_config(), seeds=(42,))

    assert len(runs) == 4
    for recurrence in ("recurrence_off", "recurrence_on"):
        replicas = [run for run in runs if run.condition.startswith(recurrence)]
        assert len({run.state_digest_before for run in replicas}) == 1
        assert len({str(run.metrics) for run in replicas}) == 1


def test_temporal_runner_keeps_explicit_unknown_metrics() -> None:
    runs = run_temporal(_config(), seeds=(42,))
    assert len(runs) == 1
    assert runs[0].metrics["novelty"] == "not_registered"
    assert runs[0].metrics["prediction_error"] == "not_available"
    assert runs[0].metrics["comparisons"]


def test_regulation_runner_is_reproducible_and_fail_closed() -> None:
    runs = run_regulation(_config(), seeds=(42,))

    assert runs == run_regulation(_config(), seeds=(42,))
    assert {run.condition for run in runs} == {
        "nominal",
        "chronic_pressure",
        "telemetry_unknown",
    }
    unknown = next(run for run in runs if run.condition == "telemetry_unknown")
    assert unknown.metrics["drives"]["drives"]["thermal_threat"] is None
    pressure = next(run for run in runs if run.condition == "chronic_pressure")
    assert pressure.metrics["drives"]["drives"]["resource_pressure"] is not None


def test_productive_stdp_and_learning_repeat_use_real_result() -> None:
    stdp = run_stdp(_config(), seeds=(42,))
    repeat = run_learning_repeat(_config(), seeds=(42,))
    assert stdp[0].metrics["final_mean_weight"] > stdp[0].metrics["initial_mean_weight"]
    by_condition = {run.condition: run for run in repeat}
    assert set(by_condition) == {"learning_on", "learning_off", "sham_replay"}
    assert by_condition["learning_on"].metrics["after_greater_than_before"] is True
    assert by_condition["learning_off"].metrics["mean_weight_delta"] == 0.0
    assert by_condition["learning_off"].metrics["reward_weight_updates"] == 0
    assert by_condition["sham_replay"].metrics["mean_weight_delta"] == 0.0
    assert by_condition["sham_replay"].metrics["rewards_received"] > 0
    assert by_condition["sham_replay"].metrics["reward_weight_updates"] == 0
