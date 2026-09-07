from __future__ import annotations

from pathlib import Path

import yaml

from src.research.followup_experiments import run_recurrence_map

ROOT = Path(__file__).parents[1]


def test_recurrence_map_covers_registered_weight_delay_grid() -> None:
    config = yaml.safe_load(
        (ROOT / "configs" / "learning_experiment.yaml").read_text(encoding="utf-8")
    )
    runs = run_recurrence_map(config, seeds=(42, 43), ticks=256)

    assert len(runs) == 2 * 5 * 3
    assert {run.seed for run in runs} == {42, 43}
    assert {run.metrics["recurrent_weight"] for run in runs} == {
        0.0,
        50.0,
        75.0,
        100.0,
        125.0,
    }
    assert {run.metrics["recurrent_delay"] for run in runs} == {1, 2, 4}
    assert {run.metrics["persistence_class"] for run in runs} == {
        "immediate_decay",
        "transient",
        "persistent_to_window",
    }
    assert all(run.metrics["ticks_requested"] == 256 for run in runs)
    assert all(run.runtime_error is None for run in runs)
