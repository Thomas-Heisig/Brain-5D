"""Regression coverage for the productive learning experiment."""

from pathlib import Path

import yaml

from src.experiments.learning_lab import run_learning_experiment


def test_productive_learning_changes_real_synapses_and_response() -> None:
    config_path = Path("configs/learning_experiment.yaml")
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    result = run_learning_experiment(config)

    assert result.final_mean_weight > result.initial_mean_weight
    assert result.mean_weight_delta > 0.0
    assert result.reward_weight_updates > 0
    assert not result.baseline_target_spiked
    assert result.trained_target_spiked
    assert result.learned