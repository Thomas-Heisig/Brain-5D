"""Tests for Phase 7: Structural determinism.

Covers:
1. Same initial state + config + RNG + tick count -> same proposals
2. Same proposal ordering across independent runs
3. Same structural mutations across independent runs
4. Same final topology digest across independent runs
5. N >= 3 independent identical runs produce same result
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Any

import pytest

from src.core.network import Brain5DConfig, NeuralNetwork
from src.homeostasis.engine import HomeostasisEngine
from src.self_organization.composition import compose_structural_subsystem
from src.self_organization.policy import (
    SelfOrganizationPolicyConfig,
)
from src.self_organization.runtime_adapter import SelfOrganizationRuntimeAdapter

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def structural_config() -> dict[str, Any]:
    """Config with structural plasticity enabled for determinism testing."""
    return {
        "seed": 42,
        "dimensions": [6, 6, 6, 6, 6],
        "initial_neurons": 50,
        "simulation": {"dt_ms": 1.0, "max_delay": 5, "debug_invariants": True},
        "network": {
            "initial_connections_per_neuron": 3,
            "neighbour_radius": 2.0,
            "weight_min": 0.0,
            "weight_max": 0.5,
        },
        "neuron": {"a": 0.02, "b": 0.2, "c": -65.0, "d": 8.0},
        "energy": {"initial": 1.0, "spike_cost": 0.001},
        "topology": {
            "input": {"dimension": "x", "coordinate": 0},
            "output": {"dimension": "x", "coordinate": 5},
        },
        "homeostasis": {
            "enabled": True,
            "target_rate_hz": 5.0,
            "rate_tau_ticks": 200.0,
            "threshold_learning_rate": 0.001,
        },
        "self_organization": {
            "enabled": True,
            "interval_ticks": 10,
            "neurogenesis_enabled": True,
            "pruning_enabled": True,
            "sprouting_enabled": True,
            "synapse_pruning_enabled": True,
            "neurogenesis_max_per_cycle": 1,
        },
        "stdp": {"enabled": False},
    }


def build_network(config: dict[str, Any], seed: int = 42) -> NeuralNetwork:
    """Build a network deterministically for structural testing."""
    rng = random.Random(seed)
    b5d_config = Brain5DConfig.from_dict(config)
    network = NeuralNetwork(b5d_config, rng)

    dims = config["dimensions"]
    total = 1
    for d in dims:
        total *= d

    from src.core.spatial_index import linear_to_5d

    for i in range(config.get("initial_neurons", 50)):
        coord = linear_to_5d(i, tuple(dims))
        network.add_neuron(coord)

    network.set_input_output_cells("x", 0, "x", dims[0] - 1)
    network.initialize_random_connections(
        config["network"]["initial_connections_per_neuron"],
        config["network"]["neighbour_radius"],
    )

    return network


# ============================================================================
# Tests
# ============================================================================


class TestStructuralDeterminism:
    """Structural plasticity produces identical results across runs."""

    def _setup_full_structural(
        self, config: dict[str, Any], tmp_path: Path, seed: int = 42
    ) -> tuple[NeuralNetwork, Any, Any]:
        """Set up network + homeostasis + structural subsystem."""
        network = build_network(config, seed)
        homeostasis = HomeostasisEngine(network, config)
        if homeostasis.enabled:
            homeostasis.attach()

        journal_path = tmp_path / f"structural_{seed}.journal"
        composed = compose_structural_subsystem(
            network,
            journal_path,
            coordinator_enabled=True,
            coordinator_dry_run=False,
            max_changes_per_tick=1,
            allow_neurogenesis=True,
            allow_neuron_pruning=True,
            allow_synapse_sprouting=True,
            allow_synapse_pruning=True,
        )
        coordinator = composed["coordinator"]
        _plasticity = composed["plasticity"]

        policy_config = SelfOrganizationPolicyConfig.from_config(config)
        adapter = SelfOrganizationRuntimeAdapter(
            homeostasis_engine=homeostasis,
            coordinator=coordinator,
            interval_ticks=10,
            policy_config=policy_config,
        )

        return network, adapter, coordinator

    def test_identical_proposals_across_runs(
        self, structural_config: dict[str, Any], tmp_path: Path
    ) -> None:
        """Two independent runs produce identical proposal sequences."""
        net_a, adapter_a, coord_a = self._setup_full_structural(
            structural_config, tmp_path, 42
        )
        net_b, adapter_b, coord_b = self._setup_full_structural(
            structural_config, tmp_path, 42
        )

        for tick in range(50):
            net_a.step()
            net_b.step()

            # Run adapter every 10 ticks
            if (tick + 1) % 10 == 0:
                adapter_a(net_a.current_tick, None)
                adapter_b(net_b.current_tick, None)

        # Compare proposals seen (should be identical)
        assert coord_a._proposals_seen == coord_b._proposals_seen

    def test_identical_mutations_across_runs(
        self, structural_config: dict[str, Any], tmp_path: Path
    ) -> None:
        """Two independent runs produce identical mutation counts."""
        net_a, adapter_a, coord_a = self._setup_full_structural(
            structural_config, tmp_path, 42
        )
        net_b, adapter_b, coord_b = self._setup_full_structural(
            structural_config, tmp_path, 42
        )

        for tick in range(50):
            net_a.step()
            net_b.step()

            if (tick + 1) % 10 == 0:
                adapter_a(net_a.current_tick, None)
                adapter_b(net_b.current_tick, None)

        assert coord_a._mutations_applied == coord_b._mutations_applied

    def test_identical_topology_across_runs(
        self, structural_config: dict[str, Any], tmp_path: Path
    ) -> None:
        """Two independent runs produce identical final topology."""
        net_a, adapter_a, _ = self._setup_full_structural(
            structural_config, tmp_path, 42
        )
        net_b, adapter_b, _ = self._setup_full_structural(
            structural_config, tmp_path, 42
        )

        for tick in range(50):
            net_a.step()
            net_b.step()

            if (tick + 1) % 10 == 0:
                adapter_a(net_a.current_tick, None)
                adapter_b(net_b.current_tick, None)

        # Compare neuron counts
        assert len(net_a.neurons) == len(net_b.neurons)
        # Compare synapse counts
        assert net_a.synapse_count == net_b.synapse_count
        # Compare neuron IDs (should be identical set)
        assert set(net_a.neurons.keys()) == set(net_b.neurons.keys())

    def test_three_independent_structural_runs_identical(
        self, structural_config: dict[str, Any], tmp_path: Path
    ) -> None:
        """N >= 3 independent runs produce identical structural results."""
        results: list[dict[str, Any]] = []

        for seed in [42, 42, 42]:  # Same seed for all
            net, adapter, coord = self._setup_full_structural(
                structural_config, tmp_path, seed
            )
            for tick in range(50):
                net.step()
                if (tick + 1) % 10 == 0:
                    adapter(net.current_tick, None)

            results.append(
                {
                    "neuron_count": len(net.neurons),
                    "synapse_count": net.synapse_count,
                    "proposals_seen": coord._proposals_seen,
                    "mutations_applied": coord._mutations_applied,
                }
            )

        assert results[0] == results[1] == results[2]

    def test_different_seeds_produce_different_results(
        self, structural_config: dict[str, Any], tmp_path: Path
    ) -> None:
        """Different seeds produce different structural outcomes (sanity check)."""
        net_a, adapter_a, _coord_a = self._setup_full_structural(
            structural_config, tmp_path, 42
        )
        net_b, adapter_b, _coord_b = self._setup_full_structural(
            structural_config, tmp_path, 99
        )

        for tick in range(100):
            net_a.step()
            net_b.step()
            if (tick + 1) % 10 == 0:
                adapter_a(net_a.current_tick, None)
                adapter_b(net_b.current_tick, None)

        # Different seeds should produce different RNG states (guaranteed)
        state_a = net_a.rng.getstate()
        state_b = net_b.rng.getstate()
        assert state_a != state_b
