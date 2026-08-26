"""Tests for Phase 8: Engine-state restore from checkpoint v4.

Covers:
1. Homeostasis engine _rates_hz is restored from checkpoint
2. Learning engine _states (traces) are restored from checkpoint
3. Learning engine _pending_rewards are restored from checkpoint
4. Engine restore is a true roundtrip (capture -> write -> read -> restore)
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Any

import pytest

from src.homeostasis.engine import HomeostasisEngine
from src.learning.learning_engine import LearningEngine
from src.learning.reward import RewardSignal
from src.storage.checkpoint import (
    capture_runtime_checkpoint,
    read_runtime_checkpoint,
    write_runtime_checkpoint,
)
from src.storage.core_restore import (
    restore_homeostasis_state,
    restore_learning_state,
)
from src.core.network import Brain5DConfig, NeuralNetwork


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def config_dict() -> dict[str, Any]:
    return {
        "seed": 42,
        "dimensions": [5, 5, 5, 5, 5],
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
            "delay_ticks": 0,
        },
    }


@pytest.fixture
def network(config_dict: dict[str, Any]) -> NeuralNetwork:
    rng = random.Random(42)
    b5d_config = Brain5DConfig.from_dict(config_dict)
    net = NeuralNetwork(b5d_config, rng)
    from src.core.spatial_index import linear_to_5d
    dims = config_dict["dimensions"]
    for i in range(config_dict.get("initial_neurons", 20)):
        net.add_neuron(linear_to_5d(i, tuple(dims)))
    net.set_input_output_cells("x", 0, "x", dims[0] - 1)
    net.initialize_random_connections(3, 2.0)
    return net


# ============================================================================
# Tests
# ============================================================================


class TestHomeostasisRestore:
    """Homeostasis engine state is restored from checkpoint v4."""

    def test_rates_hz_restored(self, network: NeuralNetwork, config_dict: dict[str, Any]) -> None:
        """Homeostasis _rates_hz is restored after capture -> write -> read -> restore."""
        homeo = HomeostasisEngine(network, config_dict)
        homeo.attach()

        # Run a few ticks to build up non-trivial rates
        for _ in range(20):
            network.step()

        original_rates = dict(homeo._rates_hz)

        # Capture checkpoint with homeostasis state
        checkpoint = capture_runtime_checkpoint(
            network,
            homeostasis_rates=homeo._rates_hz,
        )

        # Write and read back
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            tmp_path = Path(f.name)
        try:
            write_runtime_checkpoint(tmp_path, checkpoint)
            restored_checkpoint = read_runtime_checkpoint(tmp_path)

            # Create fresh engine and restore
            fresh_homeo = HomeostasisEngine(network, config_dict)
            restore_homeostasis_state(fresh_homeo, restored_checkpoint)

            # Verify rates match
            for nid, rate in original_rates.items():
                assert nid in fresh_homeo._rates_hz
                assert fresh_homeo._rates_hz[nid] == rate
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_empty_homeostasis_restore_is_noop(self, network: NeuralNetwork, config_dict: dict[str, Any]) -> None:
        """Restoring empty homeostasis state is a no-op."""
        homeo = HomeostasisEngine(network, config_dict)
        checkpoint = capture_runtime_checkpoint(network)  # No homeostasis_rates

        restore_homeostasis_state(homeo, checkpoint)
        # Should not crash, _rates_hz should remain empty
        assert hasattr(homeo, "_rates_hz")


class TestLearningRestore:
    """Learning engine state is restored from checkpoint v4."""

    def test_synapse_traces_restored(self, network: NeuralNetwork, config_dict: dict[str, Any]) -> None:
        """Learning engine per-synapse traces are restored."""
        learn = LearningEngine(network, config_dict)
        learn.attach()

        # Run a few ticks to build up traces
        for _ in range(20):
            network.step()

        # Capture learning state from engine internals
        learning_states = []
        for key, state in learn._states.items():
            learning_states.append({
                "pre_id": state.pre_id,
                "target_id": state.synapse.target_id,
                "last_pre_tick": state.last_pre_tick,
                "last_post_tick": state.last_post_tick,
                "eligibility_value": state.eligibility.value,
            })

        checkpoint = capture_runtime_checkpoint(
            network,
            learning_states=learning_states,
        )

        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            tmp_path = Path(f.name)
        try:
            write_runtime_checkpoint(tmp_path, checkpoint)
            restored_checkpoint = read_runtime_checkpoint(tmp_path)

            # Create fresh engine and restore
            fresh_learn = LearningEngine(network, config_dict)
            restore_learning_state(fresh_learn, restored_checkpoint)

            # Verify traces match
            for orig_state in learning_states:
                pre_id = orig_state["pre_id"]
                target_id = orig_state["target_id"]
                key = (pre_id, target_id)
                assert key in fresh_learn._states, f"Synapse {pre_id}->{target_id} not found in restored engine"
                state = fresh_learn._states[key]
                assert state.last_pre_tick == orig_state["last_pre_tick"]
                assert state.last_post_tick == orig_state["last_post_tick"]
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_pending_rewards_restored(self, network: NeuralNetwork, config_dict: dict[str, Any]) -> None:
        """Learning engine pending rewards are restored."""
        # Use a non-zero delay so rewards go to _pending_rewards instead of being applied immediately
        cfg = dict(config_dict)
        cfg["reward"] = dict(cfg.get("reward", {}))
        cfg["reward"]["delay_ticks"] = 10
        learn = LearningEngine(network, cfg)
        learn.attach()

        # Add some pending rewards (won't be applied due to delay)
        learn.set_reward(0.5, 10)
        learn.set_reward(-0.3, 15)

        # Capture pending rewards
        pending_rewards = [
            {"value": r.value, "tick": r.tick}
            for r in learn._pending_rewards
        ]
        assert len(pending_rewards) == 2, "Both rewards should be pending"

        checkpoint = capture_runtime_checkpoint(
            network,
            pending_rewards=pending_rewards,
        )

        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            tmp_path = Path(f.name)
        try:
            write_runtime_checkpoint(tmp_path, checkpoint)
            restored_checkpoint = read_runtime_checkpoint(tmp_path)

            # Create fresh engine and restore
            fresh_learn = LearningEngine(network, config_dict)
            restore_learning_state(fresh_learn, restored_checkpoint)

            # Verify pending rewards match
            assert len(fresh_learn._pending_rewards) == 2
            assert fresh_learn._pending_rewards[0].value == 0.5
            assert fresh_learn._pending_rewards[0].tick == 10
            assert fresh_learn._pending_rewards[1].value == -0.3
            assert fresh_learn._pending_rewards[1].tick == 15
        finally:
            tmp_path.unlink(missing_ok=True)
