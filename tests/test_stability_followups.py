from __future__ import annotations

from pathlib import Path

import yaml

from src.research.stability_followups import (
    run_drive_response_curve,
    run_parameter_robustness,
    run_stimulus_class_stability,
)

ROOT = Path(__file__).parents[1]


def _config() -> dict[str, object]:
    raw = yaml.safe_load(
        (ROOT / "configs" / "learning_experiment.yaml").read_text(encoding="utf-8")
    )
    assert isinstance(raw, dict)
    return raw


def test_drive_response_separates_quiescence_from_active_stability() -> None:
    runs = run_drive_response_curve(
        _config(), seeds=(101,), ticks=2_000, drive_levels=(0.0, 50.0)
    )
    assert len(runs) == 2
    control, driven = runs

    assert control.runtime_error is None
    assert control.metrics["numerical_stability_pass"] is True
    assert control.metrics["active_dynamics_pass"] is False
    assert control.metrics["activity_regime"] == "quiescent"
    assert control.metrics["post_burn_in_mean_spikes"] == 0.0

    assert driven.runtime_error is None
    assert driven.metrics["numerical_stability_pass"] is True
    assert driven.metrics["total_spikes"] > 0
    assert driven.metrics["post_burn_in_mean_spikes"] > 0.0
    assert driven.metrics["activity_regime"] in {
        "stable_active",
        "active_variable",
        "intermittent",
    }


def test_stimulus_class_screen_contains_seeded_noise_intervention() -> None:
    runs = run_stimulus_class_stability(_config(), seeds=(101,), ticks=2_000)
    assert [run.condition for run in runs] == [
        "stimulus_none",
        "stimulus_tonic",
        "stimulus_rhythmic",
        "stimulus_noise",
    ]
    assert all(run.runtime_error is None for run in runs)
    noise = runs[-1]
    assert noise.metrics["seed_effect_expected"] is True
    assert noise.metrics["stimulus_mode"] == "noise"


def test_parameter_robustness_varies_parameters_across_seed_labels() -> None:
    runs = run_parameter_robustness(
        _config(), seeds=(101, 102), ticks=2_000, jitter_fraction=0.05
    )
    assert len(runs) == 2
    assert all(run.runtime_error is None for run in runs)
    assert all(run.metrics["seed_effect_expected"] is True for run in runs)
    parameter_pairs = {
        (run.metrics["weight_scale"], run.metrics["drive_scale"]) for run in runs
    }
    assert len(parameter_pairs) == 2
