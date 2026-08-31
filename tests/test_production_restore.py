"""Tests for the production restore bundle (Phase 9).

Tests that ``restore_full()`` correctly restores the network, homeostasis
engine, and learning engine from a checkpoint, producing a deterministic
state that matches the original.

This is the A/B/C restore experiment foundation:
- A: uninterrupted run (reference)
- B: in-process restore (same Network object, fresh engines)
- C: fresh-process restore (Network from file, fresh engines)

This file implements the C path, which is the most demanding.
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Any, cast

from src.config.loader import ConfigDict
from src.core.network import Brain5DConfig, NeuralNetwork
from src.core.spatial_index import linear_to_5d
from src.homeostasis.engine import HomeostasisEngine
from src.learning.learning_engine import LearningEngine
from src.storage.checkpoint import (
    capture_runtime_checkpoint,
    write_runtime_checkpoint,
)
from src.storage.core_restore import restore_full
from src.storage.runtime import RuntimeNetworkLike, StorageRuntimeConfig, StorageSession

# ============================================================================
# Helpers
# ============================================================================


def _make_config() -> dict[str, Any]:
    return {
        "seed": 42,
        "dimensions": [5, 5, 1, 1, 1],
        "initial_neurons": 20,
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
            "output": {"dimension": "x", "coordinate": 4},
        },
        "homeostasis": {
            "enabled": True,
            "target_rate_hz": 5.0,
            "rate_tau_ticks": 200.0,
        },
        "stdp": {
            "enabled": True,
            "a_plus": 0.1,
            "a_minus": 0.12,
            "tau_plus": 20.0,
            "tau_minus": 20.0,
        },
        "eligibility": {
            "enabled": True,
            "tau_ticks": 200.0,
        },
        "reward": {
            "enabled": True,
            "learning_rate": 0.01,
            "delay_ticks": 5,
        },
    }


def _create_network(config: dict[str, Any]) -> NeuralNetwork:
    """Create a deterministic test network."""
    rng = random.Random(42)
    b5d_config = Brain5DConfig.from_dict(config)
    net = NeuralNetwork(b5d_config, rng)
    dims = config["dimensions"]
    for i in range(config.get("initial_neurons", 20)):
        net.add_neuron(linear_to_5d(i, tuple(dims)))
    net.set_input_output_cells("x", 0, "x", dims[0] - 1)
    net.initialize_random_connections(3, 2.0)
    return net


def _state_digest(
    network: NeuralNetwork,
    homeostasis: HomeostasisEngine | None = None,
    learning: LearningEngine | None = None,
) -> dict[str, object]:
    """Capture a deterministic state digest for comparison.

    Returns a dictionary of canonical state values that must match
    across A/B/C restore paths. Synapse state uses stable
    (source_id, target_id) keys rather than iteration order.
    """
    ids = tuple(sorted(network.neurons))
    # Build synapse state keyed by (source_id, target_id) for stable comparison
    synapse_weights: dict[tuple[int, int], float] = {}
    synapse_eligibility: dict[tuple[int, int], float] = {}
    for source_id in ids:
        for synapse in network.synapses[source_id]:
            key = (source_id, synapse.target_id)
            synapse_weights[key] = synapse.weight
            synapse_eligibility[key] = synapse.eligibility

    digest: dict[str, object] = {
        "tick": network.current_tick,
        "total_spikes": network.total_spikes,
        "total_events_processed": network.total_events_processed,
        "queued_event_count": network.queued_event_count,
        "neuron_v": tuple(network.neurons[nid].v for nid in ids),
        "neuron_u": tuple(network.neurons[nid].u for nid in ids),
        "neuron_energy": tuple(network.neurons[nid].energy for nid in ids),
        "neuron_spike_counter": tuple(
            network.neurons[nid].spike_counter for nid in ids
        ),
        "synapse_weights": tuple(
            synapse_weights[key] for key in sorted(synapse_weights)
        ),
        "synapse_eligibility": tuple(
            synapse_eligibility[key] for key in sorted(synapse_eligibility)
        ),
    }

    if homeostasis is not None:
        digest["homeostasis_rates"] = tuple(
            sorted(homeostasis._rates_hz.items())  # type: ignore[attr-defined]
        )

    if learning is not None:
        learning_traces: list[tuple[int, int, object, object, float]] = []
        for key, state in learning._states.items():  # type: ignore[attr-defined]
            pre_id, target_id = key
            learning_traces.append(
                (
                    pre_id,
                    target_id,
                    state.last_pre_tick,
                    state.last_post_tick,
                    state.eligibility.value,
                )
            )
        digest["learning_traces"] = tuple(sorted(learning_traces))
        digest["pending_rewards"] = tuple(
            (r.value, r.tick) for r in learning._pending_rewards  # type: ignore[attr-defined]
        )

    return digest


# ============================================================================
# Tests
# ============================================================================


class TestProductionRestoreBundle:
    """Full production restore bundle: network + homeostasis + learning."""

    def test_restore_full_network_and_engines(self, tmp_path: Path) -> None:
        """Restore_full produces identical state to the original run.

        This is the "C path" test:
        - Process A: create network, run ticks, capture checkpoint
        - Process B: restore from snapshot + checkpoint, create engines
        - Verify full state digest matches
        """
        config = _make_config()

        # ── Process A: create network, run, capture ──────────────────────
        network = _create_network(config)

        # Attach homeostasis and learning
        homeo = HomeostasisEngine(network, config)
        homeo.attach()
        learn = LearningEngine(network, config)
        learn.attach()

        # Run with storage session to create snapshot + journal
        runtime = StorageRuntimeConfig(
            snapshot_path=tmp_path / "base.b5d",
            journal_path=tmp_path / "base.b5d.journal",
            commit_interval_ticks=1,
        )
        with StorageSession(cast(RuntimeNetworkLike, network), runtime):
            # Inject some input current to generate spikes
            network.inject_current(0, 50.0)
            network.inject_current(1, 30.0)

            # Run ticks to build up non-trivial state
            for _ in range(30):
                network.step()

            # Set some rewards (delayed, so they go to _pending_rewards)
            learn.set_reward(0.5, network.current_tick)
            learn.set_reward(-0.2, network.current_tick)

            # Run more ticks to process some rewards
            for _ in range(10):
                network.step()

        # Capture checkpoint with engine state
        learning_states: list[dict[str, object]] = []
        for key, state in learn._states.items():  # type: ignore[attr-defined]
            pre_id, target_id = key
            learning_states.append(
                {
                    "pre_id": pre_id,
                    "target_id": target_id,
                    "last_pre_tick": state.last_pre_tick,
                    "last_post_tick": state.last_post_tick,
                    "eligibility_value": state.eligibility.value,
                }
            )

        checkpoint = capture_runtime_checkpoint(
            cast(Any, network),
            homeostasis_rates=homeo._rates_hz,  # type: ignore[attr-defined]
            learning_states=learning_states,
            pending_rewards=[
                {"value": r.value, "tick": r.tick}
                for r in learn._pending_rewards  # type: ignore[attr-defined]
            ],
        )
        checkpoint_path = tmp_path / "runtime.json"
        write_runtime_checkpoint(checkpoint_path, checkpoint)

        # Capture reference digest from Process A
        reference_digest = _state_digest(network, homeo, learn)

        # ── Process B: restore from snapshot + checkpoint ────────────────
        bundle = restore_full(
            snapshot_path=runtime.snapshot_path,
            journal_path=runtime.journal_path,
            checkpoint_path=checkpoint_path,
            config=cast(ConfigDict, config),
            recovered_path=tmp_path / "recovered.b5d",
            create_homeostasis_engine=True,
            create_learning_engine=True,
        )

        restored_digest = _state_digest(
            bundle.network,
            bundle.homeostasis_engine,
            bundle.learning_engine,
        )

        # ── Verify full state identity ───────────────────────────────────
        assert restored_digest["tick"] == reference_digest["tick"]
        assert restored_digest["total_spikes"] == reference_digest["total_spikes"]
        assert (
            restored_digest["total_events_processed"]
            == reference_digest["total_events_processed"]
        )
        assert (
            restored_digest["queued_event_count"]
            == reference_digest["queued_event_count"]
        )
        assert restored_digest["neuron_v"] == reference_digest["neuron_v"]
        assert restored_digest["neuron_u"] == reference_digest["neuron_u"]
        assert restored_digest["neuron_energy"] == reference_digest["neuron_energy"]
        assert (
            restored_digest["neuron_spike_counter"]
            == reference_digest["neuron_spike_counter"]
        )
        assert restored_digest["synapse_weights"] == reference_digest["synapse_weights"]
        assert (
            restored_digest["synapse_eligibility"]
            == reference_digest["synapse_eligibility"]
        )

        # Homeostasis state
        assert "homeostasis_rates" in restored_digest
        assert "homeostasis_rates" in reference_digest
        assert (
            restored_digest["homeostasis_rates"]
            == reference_digest["homeostasis_rates"]
        )

        # Learning state
        assert "learning_traces" in restored_digest
        assert "learning_traces" in reference_digest
        assert restored_digest["learning_traces"] == reference_digest["learning_traces"]

        # Pending rewards
        assert "pending_rewards" in restored_digest
        assert "pending_rewards" in reference_digest
        assert restored_digest["pending_rewards"] == reference_digest["pending_rewards"]

    def test_restore_full_without_engines(self, tmp_path: Path) -> None:
        """Restore_full with create_*_engine=False returns network only."""
        config = _make_config()
        network = _create_network(config)

        runtime = StorageRuntimeConfig(
            snapshot_path=tmp_path / "base.b5d",
            journal_path=tmp_path / "base.b5d.journal",
            commit_interval_ticks=1,
        )
        with StorageSession(cast(RuntimeNetworkLike, network), runtime):
            network.inject_current(0, 50.0)
            for _ in range(10):
                network.step()

        checkpoint = capture_runtime_checkpoint(cast(Any, network))
        checkpoint_path = tmp_path / "runtime.json"
        write_runtime_checkpoint(checkpoint_path, checkpoint)

        bundle = restore_full(
            snapshot_path=runtime.snapshot_path,
            journal_path=runtime.journal_path,
            checkpoint_path=checkpoint_path,
            config=cast(ConfigDict, config),
            recovered_path=tmp_path / "recovered.b5d",
            create_homeostasis_engine=False,
            create_learning_engine=False,
        )

        assert bundle.network is not None
        assert bundle.network.current_tick == network.current_tick
        assert bundle.homeostasis_engine is None
        assert bundle.learning_engine is None

    def test_restore_full_continue_determinism(self, tmp_path: Path) -> None:
        """Restored network + engines produce identical continuation.

        After restore, running additional ticks on the restored bundle
        must produce the same results as continuing on the original.
        """
        config = _make_config()

        # ── Original run ─────────────────────────────────────────────────
        network = _create_network(config)
        homeo = HomeostasisEngine(network, config)
        homeo.attach()
        learn = LearningEngine(network, config)
        learn.attach()

        runtime = StorageRuntimeConfig(
            snapshot_path=tmp_path / "base.b5d",
            journal_path=tmp_path / "base.b5d.journal",
            commit_interval_ticks=1,
        )
        with StorageSession(cast(RuntimeNetworkLike, network), runtime):
            network.inject_current(0, 50.0)
            for _ in range(20):
                network.step()

        learning_states: list[dict[str, object]] = []
        for key, state in learn._states.items():  # type: ignore[attr-defined]
            pre_id, target_id = key
            learning_states.append(
                {
                    "pre_id": pre_id,
                    "target_id": target_id,
                    "last_pre_tick": state.last_pre_tick,
                    "last_post_tick": state.last_post_tick,
                    "eligibility_value": state.eligibility.value,
                }
            )

        checkpoint = capture_runtime_checkpoint(
            cast(Any, network),
            homeostasis_rates=homeo._rates_hz,  # type: ignore[attr-defined]
            learning_states=learning_states,
        )
        checkpoint_path = tmp_path / "runtime.json"
        write_runtime_checkpoint(checkpoint_path, checkpoint)

        # Continue original for 10 more ticks (reference)
        original_continued = _state_digest(network, homeo, learn)
        for _ in range(10):
            network.step()
        original_final = _state_digest(network, homeo, learn)

        # ── Restore and continue ─────────────────────────────────────────
        bundle = restore_full(
            snapshot_path=runtime.snapshot_path,
            journal_path=runtime.journal_path,
            checkpoint_path=checkpoint_path,
            config=cast(ConfigDict, config),
            recovered_path=tmp_path / "recovered2.b5d",
            create_homeostasis_engine=True,
            create_learning_engine=True,
        )

        # Verify state matches at checkpoint point
        restored_at_checkpoint = _state_digest(
            bundle.network,
            bundle.homeostasis_engine,
            bundle.learning_engine,
        )
        assert restored_at_checkpoint["tick"] == original_continued["tick"]
        assert restored_at_checkpoint["neuron_v"] == original_continued["neuron_v"]
        assert (
            restored_at_checkpoint["synapse_weights"]
            == original_continued["synapse_weights"]
        )

        # Continue restored for 10 more ticks
        if bundle.homeostasis_engine is not None:
            bundle.homeostasis_engine.attach()
        if bundle.learning_engine is not None:
            bundle.learning_engine.attach()
        for _ in range(10):
            bundle.network.step()

        restored_final = _state_digest(
            bundle.network,
            bundle.homeostasis_engine,
            bundle.learning_engine,
        )

        # Verify final state matches
        assert restored_final["tick"] == original_final["tick"]
        assert restored_final["neuron_v"] == original_final["neuron_v"]
        assert restored_final["neuron_u"] == original_final["neuron_u"]
        assert restored_final["neuron_energy"] == original_final["neuron_energy"]
        assert restored_final["synapse_weights"] == original_final["synapse_weights"]
        assert (
            restored_final["homeostasis_rates"] == original_final["homeostasis_rates"]
        )
        assert restored_final["learning_traces"] == original_final["learning_traces"]
