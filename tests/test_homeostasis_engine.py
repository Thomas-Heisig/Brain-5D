"""Homeostatic self-regulation tests for Brain-5D v0.5."""

from __future__ import annotations

import random

from src.core.network import ConfigDict, NeuralNetwork
from src.homeostasis import HomeostasisEngine


def _configs(enabled: bool = True) -> tuple[ConfigDict, dict[str, object]]:
    core: ConfigDict = {
        "dimensions": [2, 1, 1, 1, 1],
        "simulation": {"dt_ms": 1.0, "max_delay": 2},
        "neuron": {"a": 0.02, "b": 0.2, "c": -65.0, "d": 8.0},
        "energy": {"initial": 1.0, "spike_cost": 0.1},
        "topology": {"allow_self_connections": False},
        "network": {"weight_min": 0.0, "weight_max": 1.0},
    }
    runtime: dict[str, object] = {
        "homeostasis": {
            "enabled": enabled,
            "target_rate_hz": 5.0,
            "rate_tau_ticks": 20.0,
            "threshold_learning_rate": 0.01,
            "threshold_min": -15.0,
            "threshold_max": 30.0,
            "energy_enabled": True,
            "target_energy": 1.0,
            "energy_recovery_rate": 0.1,
            "energy_min": 0.0,
            "energy_max": 1.0,
        }
    }
    return core, runtime


def test_high_activity_raises_threshold_and_reports_rate() -> None:
    core, runtime = _configs()
    network = NeuralNetwork(core, random.Random(7))
    neuron_id = network.add_neuron((0, 0, 0, 0, 0))
    engine = HomeostasisEngine(network, runtime)
    engine.attach()
    network.inject_current(neuron_id, 100.0)
    network.step()
    assert engine.stats.updates == 1
    assert engine.rate_hz(neuron_id) > 0.0
    assert network.neurons[neuron_id].threshold_adaptation > 0.0


def test_energy_recovers_toward_target() -> None:
    core, runtime = _configs()
    network = NeuralNetwork(core, random.Random(7))
    neuron_id = network.add_neuron((0, 0, 0, 0, 0))
    network.neurons[neuron_id].energy = 0.5
    engine = HomeostasisEngine(network, runtime)
    engine.attach()
    network.step()
    assert 0.5 < network.neurons[neuron_id].energy < 1.0
    assert engine.stats.mean_energy_error > 0.0


def test_disabled_homeostasis_is_behaviorally_inert() -> None:
    core, runtime = _configs(enabled=False)
    network = NeuralNetwork(core, random.Random(7))
    neuron_id = network.add_neuron((0, 0, 0, 0, 0))
    neuron = network.neurons[neuron_id]
    neuron.energy = 0.5
    engine = HomeostasisEngine(network, runtime)
    engine.attach()
    network.step()
    assert neuron.threshold_adaptation == 0.0
    assert neuron.energy == 0.5
    assert engine.stats.updates == 0
