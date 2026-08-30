"""Tests for Sprint 2C reward-modulated three-factor plasticity."""

import math
import random
from typing import Any, cast

import pytest

from src.core.network import NeuralNetwork, StepResult
from src.learning.learning_engine import LearningEngine
from src.learning.reward import RewardSignal
from tests.conftest import base_config


def _config(*, delay: int = 0, reset_trace: bool = False) -> dict[str, Any]:
    """
    Erzeugt eine Testkonfiguration mit stdp-, eligibility- und reward-Abschnitten.
    Rückgabetyp dict[str, Any] erlaubt das Hinzufügen beliebiger Schlüssel,
    ohne dass TestConfig erweitert werden muss.
    """
    config: dict[str, Any] = cast(dict[str, Any], base_config())
    config["stdp"] = {
        "enabled": False,
        "a_plus": 0.1,
        "a_minus": 0.12,
        "tau_plus": 20.0,
        "tau_minus": 20.0,
        "min_weight": 0.0,
        "max_weight": 1.0,
    }
    config["eligibility"] = {"enabled": True, "tau_ticks": 200.0}
    config["reward"] = {
        "enabled": True,
        "learning_rate": 0.1,
        "delay_ticks": delay,
        "clamp_weights": True,
        "reset_trace_after_reward": reset_trace,
        "trace_epsilon": 1.0e-12,
    }
    return config


def _result(tick: int, *spike_ids: int) -> StepResult:
    return StepResult(
        tick=tick,
        spike_ids=tuple(spike_ids),
        output_spike_ids=(),
        spikes_this_tick=len(spike_ids),
        total_spikes=len(spike_ids),
        delivered_events=0,
        queued_events=0,
        external_injection_count=0,
        external_total_current=0.0,
        synaptic_current_targets=0,
        mean_v=-65.0,
        min_v=-65.0,
        max_v=-65.0,
        mean_energy=1.0,
        core_step_ms=0.0,
    )


def _network(
    config: dict[str, Any], weight: float = 0.5
) -> tuple[NeuralNetwork, int, int]:
    # Die Testkonfiguration enthält zusätzliche Felder; für den Test ist die
    # Typprüfung an dieser Stelle deaktiviert – die Laufzeitstruktur ist korrekt.
    network = NeuralNetwork(config, random.Random(7))  # type: ignore[arg-type]
    pre_id = network.add_neuron((1, 1, 1, 1, 1))
    post_id = network.add_neuron((1, 1, 1, 1, 2))
    network.connect(pre_id, post_id, weight, 1)
    return network, pre_id, post_id


def _create_positive_trace(engine: LearningEngine, pre_id: int, post_id: int) -> float:
    engine.update(_result(0, pre_id))
    engine.update(_result(10, post_id))
    return 0.1 * math.exp(-10.0 / 20.0)


def test_reward_signal_delay() -> None:
    reward = RewardSignal(1.0, 5)
    assert reward.due_tick(3) == 8
    assert not reward.is_due(7, 3)
    assert reward.is_due(8, 3)


def test_positive_reward_potentiates_positive_eligibility() -> None:
    config = _config()
    network, pre_id, post_id = _network(config)
    engine = LearningEngine(network, config)  # type: ignore[arg-type]
    eligibility = _create_positive_trace(engine, pre_id, post_id)
    engine.set_reward(1.0, 10)
    assert network.synapses[pre_id][0].weight == pytest.approx(0.5 + 0.1 * eligibility)  # type: ignore[reportUnknownMemberType]


def test_negative_reward_depresses_positive_eligibility() -> None:
    config = _config()
    network, pre_id, post_id = _network(config)
    engine = LearningEngine(network, config)  # type: ignore[arg-type]
    eligibility = _create_positive_trace(engine, pre_id, post_id)
    engine.set_reward(-1.0, 10)
    assert network.synapses[pre_id][0].weight == pytest.approx(0.5 - 0.1 * eligibility)  # type: ignore[reportUnknownMemberType]


def test_signed_negative_eligibility_is_used() -> None:
    config = _config()
    network, pre_id, post_id = _network(config)
    engine = LearningEngine(network, config)  # type: ignore[arg-type]
    engine.update(_result(0, post_id))
    engine.update(_result(10, pre_id))
    eligibility = -0.12 * math.exp(-10.0 / 20.0)
    engine.set_reward(1.0, 10)
    assert network.synapses[pre_id][0].weight == pytest.approx(0.5 + 0.1 * eligibility)  # type: ignore[reportUnknownMemberType]


def test_delayed_reward_uses_decayed_trace() -> None:
    config = _config(delay=20)
    network, pre_id, post_id = _network(config)
    engine = LearningEngine(network, config)  # type: ignore[arg-type]
    initial_trace = _create_positive_trace(engine, pre_id, post_id)
    engine.set_reward(1.0, 10)
    engine.update(_result(29))
    assert network.synapses[pre_id][0].weight == pytest.approx(0.5)  # type: ignore[reportUnknownMemberType]
    engine.update(_result(30))
    decayed = initial_trace * math.exp(-20.0 / 200.0)
    assert network.synapses[pre_id][0].weight == pytest.approx(0.5 + 0.1 * decayed)  # type: ignore[reportUnknownMemberType]


def test_reward_weight_clamping() -> None:
    config = _config()
    config["reward"]["learning_rate"] = 100.0
    network, pre_id, post_id = _network(config, weight=0.99)
    engine = LearningEngine(network, config)  # type: ignore[arg-type]
    _create_positive_trace(engine, pre_id, post_id)
    engine.set_reward(1.0, 10)
    assert network.synapses[pre_id][0].weight == 1.0


def test_optional_trace_reset_after_reward() -> None:
    config = _config(reset_trace=True)
    network, pre_id, post_id = _network(config)
    engine = LearningEngine(network, config)  # type: ignore[arg-type]
    _create_positive_trace(engine, pre_id, post_id)
    engine.set_reward(1.0, 10)
    assert engine.get_eligibility(pre_id, post_id) == 0.0


def test_reward_requires_eligibility() -> None:
    config = _config()
    config["eligibility"]["enabled"] = False
    with pytest.raises(ValueError, match="requires eligibility"):
        LearningEngine(_network(config)[0], config)  # type: ignore[arg-type]
