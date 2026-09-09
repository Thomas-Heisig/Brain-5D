from __future__ import annotations

from pathlib import Path

import yaml

from src.research.followup_experiments import (
    run_learning_interference,
    run_replication,
)

ROOT = Path(__file__).parents[1]


def _config() -> dict[str, object]:
    raw = yaml.safe_load(
        (ROOT / "configs" / "learning_experiment.yaml").read_text(encoding="utf-8")
    )
    assert isinstance(raw, dict)
    return raw


def test_independent_replication_runner_executes_both_arms() -> None:
    runs = run_replication(_config(), seeds=(42, 43), ticks=64)
    assert len(runs) == 4
    assert {run.condition for run in runs} == {"recurrence_off", "recurrence_on"}
    assert all(run.runtime_error is None for run in runs)
    assert all(run.metrics["ticks_executed"] == 64 for run in runs)


def test_learning_interference_retry_completes_all_three_tasks() -> None:
    runs = run_learning_interference(_config(), seeds=(42, 43))
    assert len(runs) == 2
    for run in runs:
        assert run.runtime_error is None
        assert run.metrics["task_successes"] == [True, True, True]
        assert run.metrics["retained_success_fraction"] == 1.0
