"""System-level acceptance tests for the deterministic learning experiment."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, cast

import pytest
import yaml

from src.experiments.learning_lab import run_learning_experiment


@pytest.fixture(name="experiment_config")
def fixture_experiment_config() -> dict[str, Any]:
    """Load the checked-in deterministic experiment configuration."""
    path = Path("configs/learning_experiment.yaml")
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    # Tell the type checker that loaded is a dict[str, Any]; runtime check above.
    return cast(dict[str, Any], loaded)


def test_reward_training_changes_network_response(
    experiment_config: dict[str, Any],
) -> None:
    """Training must convert a subthreshold baseline into a target spike."""
    result = run_learning_experiment(experiment_config)

    assert not result.baseline_target_spiked
    assert result.trained_target_spiked
    assert result.trained_target_spike_tick == 2
    assert result.learned


def test_reward_training_strengthens_weights(
    experiment_config: dict[str, Any],
) -> None:
    """Three-factor learning must increase convergent synaptic weights."""
    result = run_learning_experiment(experiment_config)

    assert result.initial_mean_weight == pytest.approx(0.05)
    assert result.final_mean_weight > 0.8
    assert result.final_mean_weight <= 1.0
    assert result.mean_weight_delta > 0.0


def test_reward_accounting_matches_training_trials(
    experiment_config: dict[str, Any],
) -> None:
    """Every training episode must receive and apply exactly one reward."""
    result = run_learning_experiment(experiment_config)

    assert result.rewards_received == result.training_trials
    assert result.rewards_applied == result.training_trials
    assert result.reward_weight_updates == (
        result.training_trials * result.presynaptic_neurons
    )


def test_experiment_is_deterministic(experiment_config: dict[str, Any]) -> None:
    """Repeated runs with the same configuration must produce identical output."""
    first = run_learning_experiment(experiment_config)
    second = run_learning_experiment(experiment_config)

    assert first == second


def test_experiment_requires_reward_learning(
    experiment_config: dict[str, Any],
) -> None:
    """Fail fast instead of silently running a non-learning experiment."""
    config = deepcopy(experiment_config)
    config["reward"]["enabled"] = False

    with pytest.raises(ValueError, match="reward.enabled=true"):
        run_learning_experiment(config)