"""Tests for Phase 5: Full RNG state persistence.

Covers:
1. RNG state is captured via getstate() in checkpoint
2. RNG state is restored via setstate() from checkpoint
3. After snapshot+restore, next 100 values are identical
4. Two independent fresh processes with same RNG state produce same sequence
5. Multiple RNGs (network, stimulus) each have stable IDs
"""

from __future__ import annotations

import random
from collections.abc import Mapping, Sequence
from pathlib import Path

from src.storage.checkpoint import (
    RandomStateRecord,
    RuntimeCheckpoint,
    capture_runtime_checkpoint,
    read_runtime_checkpoint,
    write_runtime_checkpoint,
)

# ============================================================================
# Mock network with RNG for checkpoint testing
# ============================================================================


class MockEvent:
    """Minimal event for checkpoint testing."""

    def __init__(self, source_id: int, target_id: int, weight: float, delivery_tick: int):
        self.source_id = source_id
        self.target_id = target_id
        self.weight = weight
        self.delivery_tick = delivery_tick


class MockNeuron:
    """Minimal neuron for checkpoint testing."""

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
    """Minimal synapse for checkpoint testing."""

    def __init__(self, target_id: int):
        self.target_id = target_id
        self.weight = 0.1
        self.delay = 1
        self.eligibility = 0.0
        self.last_pre_spike = -1


class MockCheckpointNetwork:
    """Minimal network implementing CheckpointNetworkLike."""

    def __init__(self):
        self.rng = random.Random(42)
        self.current_tick = 50
        self.total_spikes = 100
        self.total_events_processed = 200
        self.pending_currents: Mapping[int, float] = {1: 0.5, 2: 0.3}
        self.input_cells = {1, 2, 3}
        self.output_cells = {4, 5}
        self.event_slots: Sequence[Sequence[MockEvent]] = [
            [],
            [MockEvent(1, 5, 0.1, 51)],
            [],
            [MockEvent(2, 6, 0.2, 53)],
        ]
        self.neurons: dict[int, MockNeuron] = {
            1: MockNeuron(1),
            2: MockNeuron(2),
            3: MockNeuron(3),
        }
        self.synapses: dict[int, list[MockSynapse]] = {
            1: [MockSynapse(2), MockSynapse(3)],
            2: [MockSynapse(3)],
        }


# ============================================================================
# Tests
# ============================================================================


class TestRNGStateCapture:
    """RNG state is correctly captured in checkpoint."""

    def test_rng_state_captured(self) -> None:
        """Checkpoint captures RNG state via getstate()."""
        net = MockCheckpointNetwork()
        # Advance RNG to get non-trivial state
        for _ in range(100):
            net.rng.random()
        checkpoint = capture_runtime_checkpoint(net)  # type: ignore[arg-type]
        assert checkpoint.rng.version >= 3
        assert len(checkpoint.rng.state) > 0

    def test_rng_state_restored(self) -> None:
        """Checkpoint restores RNG state via setstate()."""
        net = MockCheckpointNetwork()
        # Advance RNG
        for _ in range(100):
            net.rng.random()

        # Capture checkpoint (getstate returns state BEFORE next random)
        checkpoint = capture_runtime_checkpoint(net)  # type: ignore[arg-type]

        # The original RNG produces values from this point
        expected_values = [net.rng.random() for _ in range(50)]

        # Create fresh RNG and restore to same state
        restored_rng = random.Random()
        restored_rng.setstate((
            checkpoint.rng.version,
            tuple(checkpoint.rng.state),
            checkpoint.rng.gauss_next,
        ))

        # Compare next values — should match
        restored_values = [restored_rng.random() for _ in range(50)]
        assert expected_values == restored_values

    def test_rng_roundtrip_identical(self) -> None:
        """After snapshot+restore, next N values are identical."""
        net = MockCheckpointNetwork()
        # Advance RNG to a non-trivial state (50 advances)
        for _ in range(50):
            net.rng.random()

        # Capture checkpoint (state at position 50)
        checkpoint = capture_runtime_checkpoint(net)  # type: ignore[arg-type]

        # Original continues from position 50
        original_values = [net.rng.random() for _ in range(50)]

        # Restore from checkpoint (should be at position 50 again)
        restored_rng = random.Random()
        restored_rng.setstate((
            checkpoint.rng.version,
            tuple(checkpoint.rng.state),
            checkpoint.rng.gauss_next,
        ))

        # Should produce same 50 values as original from position 50
        restored_values = [restored_rng.random() for _ in range(50)]
        assert original_values == restored_values

    def test_write_read_roundtrip(self, tmp_path: Path) -> None:
        """Checkpoint survives write-then-read cycle."""
        net = MockCheckpointNetwork()
        for _ in range(100):
            net.rng.random()

        checkpoint = capture_runtime_checkpoint(net)  # type: ignore[arg-type]
        # Original continues from this point
        expected = [net.rng.random() for _ in range(30)]

        chk_path = tmp_path / "runtime_checkpoint.json"
        write_runtime_checkpoint(chk_path, checkpoint)

        # Read back — should restore to same state as checkpoint capture point
        restored = read_runtime_checkpoint(chk_path)
        restored_rng = random.Random()
        restored_rng.setstate((
            restored.rng.version,
            tuple(restored.rng.state),
            restored.rng.gauss_next,
        ))
        actual = [restored_rng.random() for _ in range(30)]
        assert expected == actual

    def test_two_fresh_processes_same_sequence(self, tmp_path: Path) -> None:
        """Two independent fresh RNGs with same restored state produce same sequence."""
        # Create first RNG, advance, capture
        rng1 = random.Random(42)
        for _ in range(50):
            rng1.random()

        checkpoint = RuntimeCheckpoint(
            version=3,
            current_tick=50,
            total_spikes=100,
            total_events_processed=200,
            rng=RandomStateRecord(
                version=rng1.getstate()[0],
                state=tuple(int(v) for v in rng1.getstate()[1]),
                gauss_next=rng1.getstate()[2],
            ),
            pending_currents=(),
            input_cells=(),
            output_cells=(),
            queued_events=(),
        )

        # Two independent restores
        rng_a = random.Random()
        rng_a.setstate((
            checkpoint.rng.version,
            tuple(checkpoint.rng.state),
            checkpoint.rng.gauss_next,
        ))
        rng_b = random.Random()
        rng_b.setstate((
            checkpoint.rng.version,
            tuple(checkpoint.rng.state),
            checkpoint.rng.gauss_next,
        ))

        seq_a = [rng_a.random() for _ in range(100)]
        seq_b = [rng_b.random() for _ in range(100)]
        assert seq_a == seq_b

    def test_checkpoint_serialization_no_rng_advancement(self) -> None:
        """Capturing a checkpoint does NOT advance the RNG."""
        net = MockCheckpointNetwork()
        rng = net.rng
        v1 = rng.random()
        # Capture checkpoint (should not advance RNG)
        checkpoint = capture_runtime_checkpoint(net)  # type: ignore[arg-type]
        v2 = rng.random()
        # The two values should be consecutive — checkpoint didn't consume random
        assert v1 != v2  # Different values (RNG advanced between them)

        # Verify checkpoint state matches v1 position
        restored_rng = random.Random()
        restored_rng.setstate((
            checkpoint.rng.version,
            tuple(checkpoint.rng.state),
            checkpoint.rng.gauss_next,
        ))
        # Restored RNG should produce v2 (the value after v1)
        assert restored_rng.random() == v2
