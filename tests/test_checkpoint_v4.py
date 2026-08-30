"""Tests for Phase 8: Persist homeostasis and learning state in checkpoint v4.

Covers:
1. Homeostasis rates are captured in checkpoint v4
2. Learning state is captured in checkpoint v4
3. Homeostasis rates survive write/read roundtrip
4. Learning state survives write/read roundtrip
5. Version 3 checkpoints are still readable (backward compatibility)
"""

from __future__ import annotations

import json
from pathlib import Path

from src.storage.checkpoint import (
    capture_runtime_checkpoint,
    read_runtime_checkpoint,
    write_runtime_checkpoint,
)

# ============================================================================
# Mock implementations
# ============================================================================


class MockEvent:
    def __init__(self, source_id: int, target_id: int, weight: float, delivery_tick: int):
        self.source_id = source_id
        self.target_id = target_id
        self.weight = weight
        self.delivery_tick = delivery_tick


class MockNeuron:
    def __init__(self, neuron_id: int):
        self.neuron_id = neuron_id
        self.a = 0.02
        self.b = 0.2
        self.c = -65.0
        self.d = 8.0
        self.v = -65.0
        self.u = -13.0
        self.energy = 1.0
        self.spike_cost = 0.001
        self.spike_counter = 0
        self.last_spike_tick = -1
        self.threshold_adaptation = 0.0
        self.last_external_current = 0.0
        self.last_synaptic_current = 0.0
        self.firing_rate_estimate = 0.0
        self._spike_count_window = 0
        self._last_update_tick = 0
        self.pre_trace = 0.0
        self.post_trace = 0.0


class MockSynapse:
    def __init__(self, target_id: int):
        self.target_id = target_id
        self.weight = 0.1
        self.delay = 1
        self.eligibility = 0.0
        self.last_pre_spike = -1


class MockCheckpointNetwork:
    def __init__(self):
        import random
        self.rng = random.Random(42)
        self.current_tick = 50
        self.total_spikes = 100
        self.total_events_processed = 200
        self.pending_currents: dict[int, float] = {}
        self.input_cells = {1, 2}
        self.output_cells = {3, 4}
        self.event_slots: list[list[MockEvent]] = [[], []]
        self.neurons: dict[int, MockNeuron] = {1: MockNeuron(1), 2: MockNeuron(2)}
        self.synapses: dict[int, list[MockSynapse]] = {1: [MockSynapse(2)]}


# ============================================================================
# Tests
# ============================================================================


class TestCheckpointV4:
    """Checkpoint v4 captures homeostasis and learning state."""

    def test_homeostasis_state_captured(self) -> None:
        """Homeostasis rates are captured in checkpoint v4."""
        net = MockCheckpointNetwork()
        checkpoint = capture_runtime_checkpoint(
            net,  # type: ignore[arg-type]
            homeostasis_rates={1: 5.0, 2: 3.0, 3: 7.5},
        )
        assert checkpoint.version == 4
        assert len(checkpoint.homeostasis_state) == 3
        # Sorted by neuron_id
        assert checkpoint.homeostasis_state[0].neuron_id == 1
        assert checkpoint.homeostasis_state[0].rate_hz == 5.0
        assert checkpoint.homeostasis_state[1].neuron_id == 2
        assert checkpoint.homeostasis_state[1].rate_hz == 3.0
        assert checkpoint.homeostasis_state[2].neuron_id == 3
        assert checkpoint.homeostasis_state[2].rate_hz == 7.5

    def test_learning_state_captured(self) -> None:
        """Learning state is captured in checkpoint v4."""
        net = MockCheckpointNetwork()
        learning_states = [
            {"pre_id": 1, "target_id": 2, "last_pre_tick": 10, "last_post_tick": 12, "eligibility_value": 0.05},
            {"pre_id": 2, "target_id": 3, "last_pre_tick": None, "last_post_tick": None, "eligibility_value": 0.0},
        ]
        checkpoint = capture_runtime_checkpoint(
            net,  # type: ignore[arg-type]
            learning_states=learning_states,  # type: ignore[arg-type]
        )
        assert checkpoint.version == 4
        assert len(checkpoint.learning_state) == 2
        assert checkpoint.learning_state[0].pre_id == 1
        assert checkpoint.learning_state[0].target_id == 2
        assert checkpoint.learning_state[0].last_pre_tick == 10
        assert checkpoint.learning_state[0].eligibility_value == 0.05
        assert checkpoint.learning_state[1].pre_id == 2
        assert checkpoint.learning_state[1].last_pre_tick is None

    def test_write_read_homeostasis_roundtrip(self, tmp_path: Path) -> None:
        """Homeostasis state survives write/read roundtrip."""
        net = MockCheckpointNetwork()
        checkpoint = capture_runtime_checkpoint(
            net,  # type: ignore[arg-type]
            homeostasis_rates={1: 5.0, 5: 2.5, 10: 8.0},
        )
        chk_path = tmp_path / "v4_checkpoint.json"
        write_runtime_checkpoint(chk_path, checkpoint)

        restored = read_runtime_checkpoint(chk_path)
        assert restored.version == 4
        assert len(restored.homeostasis_state) == 3
        assert restored.homeostasis_state[0].neuron_id == 1
        assert restored.homeostasis_state[0].rate_hz == 5.0
        assert restored.homeostasis_state[1].neuron_id == 5
        assert restored.homeostasis_state[1].rate_hz == 2.5
        assert restored.homeostasis_state[2].neuron_id == 10
        assert restored.homeostasis_state[2].rate_hz == 8.0

    def test_write_read_learning_roundtrip(self, tmp_path: Path) -> None:
        """Learning state survives write/read roundtrip."""
        net = MockCheckpointNetwork()
        learning_states = [
            {"pre_id": 1, "target_id": 2, "last_pre_tick": 10, "last_post_tick": 15, "eligibility_value": 0.03},
        ]
        checkpoint = capture_runtime_checkpoint(
            net,  # type: ignore[arg-type]
            learning_states=learning_states,  # type: ignore[arg-type]
        )
        chk_path = tmp_path / "v4_learning.json"
        write_runtime_checkpoint(chk_path, checkpoint)

        restored = read_runtime_checkpoint(chk_path)
        assert restored.version == 4
        assert len(restored.learning_state) == 1
        assert restored.learning_state[0].pre_id == 1
        assert restored.learning_state[0].target_id == 2
        assert restored.learning_state[0].last_pre_tick == 10
        assert restored.learning_state[0].eligibility_value == 0.03

    def test_v3_backward_compatible(self, tmp_path: Path) -> None:
        """Version 3 checkpoints are still readable."""
        v3_payload = {
            "version": 3,
            "current_tick": 50,
            "total_spikes": 100,
            "total_events_processed": 200,
            "rng": {"version": 3, "state": [1, 2, 3], "gauss_next": None},
            "pending_currents": [],
            "input_cells": [1],
            "output_cells": [2],
            "queued_events": [],
            "neuron_states": [],
            "synapse_states": [],
        }
        chk_path = tmp_path / "v3_checkpoint.json"
        chk_path.write_text(
            json.dumps(v3_payload, separators=(",", ":")), encoding="utf-8"
        )

        restored = read_runtime_checkpoint(chk_path)
        assert restored.version == 3
        assert restored.current_tick == 50
        assert restored.homeostasis_state == ()
        assert restored.learning_state == ()

    def test_homeostasis_optional(self) -> None:
        """Homeostasis state is optional in checkpoint (defaults to empty)."""
        net = MockCheckpointNetwork()
        checkpoint = capture_runtime_checkpoint(net)  # type: ignore[arg-type]  # No homeostasis_rates
        assert checkpoint.homeostasis_state == ()

    def test_learning_optional(self) -> None:
        """Learning state is optional in checkpoint (defaults to empty)."""
        net = MockCheckpointNetwork()
        checkpoint = capture_runtime_checkpoint(net)  # type: ignore[arg-type]  # No learning_states
        assert checkpoint.learning_state == ()
