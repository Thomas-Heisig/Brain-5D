import random
from typing import Any, cast

from tests.conftest import base_config

from src.core.network import NeuralNetwork
from src.manipulation import Brain5DManipulator
from src.self_organization import SelfOrganizationEngine


def test_pruning_removes_old_weak_synapse() -> None:
    cfg: dict[str, Any] = cast(dict[str, Any], base_config())
    cfg["self_organization"] = {
        "enabled": True,
        "interval_ticks": 1,
        "pruning_enabled": True,
        "pruning_weight_threshold": 0.01,
        "pruning_min_age_ticks": 0,
    }
    net = NeuralNetwork(cfg, random.Random(1))  # type: ignore[arg-type]
    m = Brain5DManipulator(net)
    a = m.create_neuron((1, 1, 1, 1, 1))
    b = m.create_neuron((1, 1, 1, 1, 2))
    m.create_synapse(a, b, 0.001, 1)
    engine = SelfOrganizationEngine(net, m, cfg)
    engine.run_cycle(10)
    assert net.synapse_count == 0
    assert engine.stats.pruned_synapses == 1


def test_neurogenesis_can_create_child_near_active_parent() -> None:
    cfg: dict[str, Any] = cast(dict[str, Any], base_config())
    cfg["max_neurons"] = 10
    cfg["self_organization"] = {
        "enabled": True,
        "interval_ticks": 1,
        "neurogenesis_enabled": True,
        "neurogenesis_spike_delta_threshold": 1,
        "neurogenesis_radius": 1.0,
        "neurogenesis_max_per_cycle": 1,
        "sprouting_weight": 0.05,
    }
    net = NeuralNetwork(cfg, random.Random(1))  # type: ignore[arg-type]
    m = Brain5DManipulator(net)
    parent = m.create_neuron((2, 2, 2, 2, 2))
    net.neurons[parent].spike_counter = 2
    engine = SelfOrganizationEngine(net, m, cfg)
    engine.run_cycle(10)
    assert len(net.neurons) == 2
    assert net.synapse_count == 1
    assert engine.stats.created_neurons == 1
