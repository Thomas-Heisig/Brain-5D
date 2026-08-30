"""Tests for Phase 6: Explicit iteration-order determinism.

Covers:
1. Neuron iteration in step() is deterministic
2. Synapse iteration in step() is deterministic
3. Homeostasis iteration is deterministic
4. Learning engine iteration is deterministic
5. Dict/set iteration in scientific paths uses explicit ordering
6. Event queue processing order is deterministic
"""

from __future__ import annotations

import random
from typing import Any

import pytest

from src.core.network import Brain5DConfig, NeuralNetwork
from src.homeostasis.engine import HomeostasisEngine
from src.learning.learning_engine import LearningEngine


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def config_dict() -> dict[str, Any]:
    """Minimal config for deterministic testing."""
    return {
        "seed": 42,
        "dimensions": [5, 5, 5, 5, 5],
        "initial_neurons": 100,
        "simulation": {"dt_ms": 1.0, "max_delay": 5, "debug_invariants": True},
        "network": {
            "initial_connections_per_neuron": 5,
            "neighbour_radius": 3.0,
            "weight_min": 0.0,
            "weight_max": 0.5,
        },
        "neuron": {"a": 0.02, "b": 0.2, "c": -65.0, "d": 8.0},
        "energy": {"initial": 1.0, "spike_cost": 0.001},
        "topology": {
            "input": {"dimension": "x", "coordinate": 0},
            "output": {"dimension": "x", "coordinate": 4},
        },
        "homeostasis": {
            "enabled": False,
        },
        "stdp": {
            "enabled": False,
        },
    }


def build_network(config: dict[str, Any], seed: int = 42) -> NeuralNetwork:
    """Build a network deterministically."""
    rng = random.Random(seed)
    b5d_config = Brain5DConfig.from_dict(config)
    network = NeuralNetwork(b5d_config, rng)

    dims = config["dimensions"]
    total = 1
    for d in dims:
        total *= d

    # Add neurons deterministically
    from src.core.spatial_index import linear_to_5d

    for i in range(config.get("initial_neurons", 100)):
        coord = linear_to_5d(i, tuple(dims))
        network.add_neuron(coord)

    # Set input/output
    network.set_input_output_cells("x", 0, "x", dims[0] - 1)

    # Initialize connections
    network.initialize_random_connections(
        config["network"]["initial_connections_per_neuron"],
        config["network"]["neighbour_radius"],
    )

    return network


# ============================================================================
# Tests
# ============================================================================


class TestIterationDeterminism:
    """Scientific execution paths use deterministic iteration order."""

    def test_identical_runs_produce_identical_spike_sequence(self, config_dict: dict[str, Any]) -> None:
        """Two identical runs produce identical spike sequences."""
        network_a = build_network(config_dict)
        network_b = build_network(config_dict)

        # Run both for 50 ticks
        spikes_a: list[int] = []
        spikes_b: list[int] = []
        for _ in range(50):
            result_a = network_a.step()
            result_b = network_b.step()
            spikes_a.append(result_a.spikes_this_tick)
            spikes_b.append(result_b.spikes_this_tick)

        assert spikes_a == spikes_b

    def test_identical_runs_produce_identical_neuron_state(self, config_dict: dict[str, Any]) -> None:
        """Two identical runs produce identical neuron states at each tick."""
        network_a = build_network(config_dict)
        network_b = build_network(config_dict)

        for tick in range(30):
            network_a.step()
            network_b.step()

            # Compare all neuron states
            for nid in sorted(network_a.neurons):
                na = network_a.neurons[nid]
                nb = network_b.neurons[nid]
                assert na.v == nb.v, f"Tick {tick}, neuron {nid}: v mismatch"
                assert na.u == nb.u, f"Tick {tick}, neuron {nid}: u mismatch"
                assert na.energy == nb.energy, f"Tick {tick}, neuron {nid}: energy mismatch"

    def test_identical_runs_produce_identical_synapse_state(self, config_dict: dict[str, Any]) -> None:
        """Two identical runs produce identical synapse weights."""
        network_a = build_network(config_dict)
        network_b = build_network(config_dict)

        for _ in range(30):
            network_a.step()
            network_b.step()

        # Compare all synapse weights
        for src_id in sorted(network_a.synapses):
            syns_a = network_a.synapses[src_id]
            syns_b = network_b.synapses[src_id]
            assert len(syns_a) == len(syns_b)
            for sa, sb in zip(syns_a, syns_b):
                assert sa.target_id == sb.target_id
                assert sa.weight == sb.weight
                assert sa.eligibility == sb.eligibility

    def test_identical_runs_produce_identical_event_queue(self, config_dict: dict[str, Any]) -> None:
        """Two identical runs produce identical event queues."""
        network_a = build_network(config_dict)
        network_b = build_network(config_dict)

        for _ in range(30):
            network_a.step()
            network_b.step()

            # Compare queued event count
            assert network_a.queued_event_count == network_b.queued_event_count

        # Compare event slot contents
        for slot_idx, (slot_a, slot_b) in enumerate(zip(network_a.event_slots, network_b.event_slots)):
            assert len(slot_a) == len(slot_b), f"Slot {slot_idx} length mismatch"
            for ea, eb in zip(slot_a, slot_b):
                assert ea.source_id == eb.source_id
                assert ea.target_id == eb.target_id
                assert ea.weight == eb.weight
                assert ea.delivery_tick == eb.delivery_tick

    def test_identical_runs_produce_identical_rng_state(self, config_dict: dict[str, Any]) -> None:
        """Two identical runs produce identical RNG states."""
        network_a = build_network(config_dict)
        network_b = build_network(config_dict)

        for _ in range(30):
            network_a.step()
            network_b.step()

        state_a = network_a.rng.getstate()
        state_b = network_b.rng.getstate()
        assert state_a == state_b

    def test_homeostasis_iteration_deterministic(self, config_dict: dict[str, Any]) -> None:
        """Homeostasis engine iteration is deterministic."""
        # Enable homeostasis
        config_dict["homeostasis"]["enabled"] = True

        network_a = build_network(config_dict)
        network_b = build_network(config_dict)

        homeo_a = HomeostasisEngine(network_a, config_dict)
        homeo_b = HomeostasisEngine(network_b, config_dict)
        homeo_a.attach()
        homeo_b.attach()

        for _ in range(20):
            network_a.step()
            network_b.step()

        stats_a = homeo_a.stats
        stats_b = homeo_b.stats
        assert stats_a.mean_rate_hz == stats_b.mean_rate_hz
        assert stats_a.mean_threshold_adaptation == stats_b.mean_threshold_adaptation

    def test_learning_iteration_deterministic(self, config_dict: dict[str, Any]) -> None:
        """Learning engine iteration is deterministic."""
        # Enable STDP
        config_dict["stdp"]["enabled"] = True

        network_a = build_network(config_dict)
        network_b = build_network(config_dict)

        learn_a = LearningEngine(network_a, config_dict)
        learn_b = LearningEngine(network_b, config_dict)
        learn_a.attach()
        learn_b.attach()

        for _ in range(20):
            network_a.step()
            network_b.step()

        stats_a = learn_a.stats
        stats_b = learn_b.stats
        assert stats_a.stdp_weight_updates == stats_b.stdp_weight_updates

    def test_three_independent_runs_identical(self, config_dict: dict[str, Any]) -> None:
        """Three independent runs produce identical final state."""
        networks = [build_network(config_dict) for _ in range(3)]
        results = []

        for net in networks:
            for _ in range(40):
                net.step()
            # Capture canonical state
            from src.research.canonical_state import canonical_state_digest
            digest = canonical_state_digest(net)  # type: ignore[arg-type]
            results.append(digest)  # type: ignore[arg-type]

        assert results[0] == results[1] == results[2]
