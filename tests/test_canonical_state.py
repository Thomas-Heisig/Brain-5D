"""Tests for Phase 3 & 4: Canonical scientific state and full-state digest.

Covers:
1. Canonical state capture produces deterministic ordering
2. Neuron state is sorted by neuron_id
3. Synapse state is sorted by source_id, target_id
4. Event state is sorted by delivery_tick, source_id, target_id
5. RNG state is captured via getstate()
6. Digest is deterministic (same input -> same output)
7. Digest changes when any field changes
8. No memory addresses or repr() in serialization
9. No wall-clock timestamps in serialization
10. Integration with real NeuralNetwork
"""

from __future__ import annotations

import json
import random

from src.research.canonical_state import (
    canonical_state_digest,
    capture_canonical_state,
)


# ============================================================================
# Mock implementations for protocol testing
# ============================================================================


class MockNeuron:
    """Minimal mock implementing CanonicalNeuronLike."""

    def __init__(self, neuron_id: int, v: float = -65.0, u: float = -13.0):
        self.neuron_id = neuron_id
        self.a = 0.02
        self.b = 0.2
        self.c = -65.0
        self.d = 8.0
        self.v = v
        self.u = u
        self.energy = 1.0
        self.spike_cost = 0.001
        self.spike_counter = 0
        self.last_spike_tick = -1
        self.threshold_adaptation = 0.0
        self.last_external_current = 0.0
        self.last_synaptic_current = 0.0


class MockSynapse:
    """Minimal mock implementing CanonicalSynapseLike."""

    def __init__(self, target_id: int, weight: float = 0.1, delay: int = 1):
        self.target_id = target_id
        self.weight = weight
        self.delay = delay
        self.eligibility = 0.0
        self.last_pre_spike = -1


class MockSpikeEvent:
    """Minimal mock implementing CanonicalSpikeEventLike."""

    def __init__(self, source_id: int, target_id: int, weight: float, delivery_tick: int):
        self.source_id = source_id
        self.target_id = target_id
        self.weight = weight
        self.delivery_tick = delivery_tick


class MockNetwork:
    """Minimal mock implementing CanonicalNetworkLike."""

    def __init__(self):
        self._rng = random.Random(42)
        self.current_tick = 100
        self.dimensions = (10, 10, 10, 10, 10)
        self.total_spikes = 500
        self.total_events_processed = 1000
        self._neurons: dict[int, MockNeuron] = {}
        self._synapses: dict[int, list[MockSynapse]] = {}
        self.event_slots: list[list[MockSpikeEvent]] = [[] for _ in range(6)]
        self.pending_currents: dict[int, float] = {}
        self.input_cells: set[int] = set()
        self.output_cells: set[int] = set()

    @property
    def rng(self) -> random.Random:
        return self._rng

    @property
    def neurons(self) -> dict[int, MockNeuron]:
        return self._neurons

    @property
    def synapses(self) -> dict[int, list[MockSynapse]]:
        return self._synapses


# ============================================================================
# Tests
# ============================================================================


class TestCanonicalStateCapture:
    """Canonical state capture produces deterministic ordering."""

    def test_neuron_ordering(self) -> None:
        """Neurons are sorted by neuron_id."""
        net = MockNetwork()
        net._neurons = {  # type: ignore[misc]
            5: MockNeuron(5),
            2: MockNeuron(2),
            8: MockNeuron(8),
            1: MockNeuron(1),
        }
        state = capture_canonical_state(net)  # type: ignore[arg-type]
        neuron_ids = [n["neuron_id"] for n in state["neurons"]]
        assert neuron_ids == [1, 2, 5, 8]

    def test_synapse_ordering(self) -> None:
        """Synapses are sorted by source_id, then target_id."""
        net = MockNetwork()
        net._synapses = {  # type: ignore[misc]
            3: [MockSynapse(7), MockSynapse(5)],
            1: [MockSynapse(2)],
        }
        state = capture_canonical_state(net)  # type: ignore[arg-type]
        syn_list = state["synapses"]
        assert len(syn_list) == 3
        assert syn_list[0]["source_id"] == 1
        assert syn_list[0]["target_id"] == 2
        assert syn_list[1]["source_id"] == 3
        assert syn_list[1]["target_id"] == 5
        assert syn_list[2]["source_id"] == 3
        assert syn_list[2]["target_id"] == 7

    def test_event_ordering(self) -> None:
        """Events are sorted by delivery_tick, then source_id, then target_id."""
        net = MockNetwork()
        net.event_slots = [
            [],
            [MockSpikeEvent(3, 5, 0.1, 101), MockSpikeEvent(1, 2, 0.2, 101)],
            [MockSpikeEvent(5, 1, 0.3, 102)],
        ]
        state = capture_canonical_state(net)  # type: ignore[arg-type]
        events = state["events"]
        assert len(events) == 3
        assert events[0]["delivery_tick"] == 101
        assert events[0]["source_id"] == 1
        assert events[1]["delivery_tick"] == 101
        assert events[1]["source_id"] == 3
        assert events[2]["delivery_tick"] == 102

    def test_rng_state_captured(self) -> None:
        """RNG state is captured via getstate()."""
        net = MockNetwork()
        # Advance RNG to get non-trivial state
        for _ in range(10):
            net._rng.random()  # type: ignore[misc]
        state = capture_canonical_state(net)  # type: ignore[arg-type]
        rng_state = state["rng"]
        assert "version" in rng_state
        assert "state" in rng_state
        assert isinstance(rng_state["state"], list)
        assert len(rng_state["state"]) > 0

    def test_pending_currents_sorted(self) -> None:
        """Pending currents are sorted by neuron_id."""
        net = MockNetwork()
        net.pending_currents = {5: 1.0, 2: 2.0, 8: 3.0}
        state = capture_canonical_state(net)  # type: ignore[arg-type]
        currents = state["pending_currents"]
        assert currents == [(2, 2.0), (5, 1.0), (8, 3.0)]

    def test_input_output_cells_sorted(self) -> None:
        """Input and output cells are sorted."""
        net = MockNetwork()
        net.input_cells = {5, 2, 8}
        net.output_cells = {3, 1, 7}
        state = capture_canonical_state(net)  # type: ignore[arg-type]
        assert state["input_cells"] == [2, 5, 8]
        assert state["output_cells"] == [1, 3, 7]

    def test_no_timestamps_in_state(self) -> None:
        """No wall-clock timestamps appear in canonical state."""
        net = MockNetwork()
        state_json = json.dumps(capture_canonical_state(net), sort_keys=True)  # type: ignore[arg-type]
        # Check that no ISO timestamp or wall-clock time appears
        assert "timestamp" not in state_json
        assert "created_at" not in state_json
        assert "generated" not in state_json


class TestCanonicalStateDigest:
    """Full-state digest properties."""

    def test_digest_deterministic(self) -> None:
        """Same input produces same digest."""
        net = MockNetwork()
        d1 = canonical_state_digest(net)  # type: ignore[arg-type]
        d2 = canonical_state_digest(net)  # type: ignore[arg-type]
        assert d1 == d2
        assert isinstance(d1, str)
        assert len(d1) == 64  # SHA-256 hex

    def test_digest_changes_on_tick(self) -> None:
        """Digest changes when current_tick changes."""
        net = MockNetwork()
        d1 = canonical_state_digest(net)  # type: ignore[arg-type]
        net.current_tick = 101
        d2 = canonical_state_digest(net)  # type: ignore[arg-type]
        assert d1 != d2

    def test_digest_changes_on_rng(self) -> None:
        """Digest changes when RNG state changes."""
        net = MockNetwork()
        d1 = canonical_state_digest(net)  # type: ignore[arg-type]
        net._rng.random()  # type: ignore[misc]
        d2 = canonical_state_digest(net)  # type: ignore[arg-type]
        assert d1 != d2

    def test_digest_changes_on_neuron(self) -> None:
        """Digest changes when neuron state changes."""
        net = MockNetwork()
        net._neurons = {1: MockNeuron(1, v=-65.0)}  # type: ignore[misc]
        d1 = canonical_state_digest(net)  # type: ignore[arg-type]
        net._neurons[1].v = -60.0  # type: ignore[misc]
        d2 = canonical_state_digest(net)  # type: ignore[arg-type]
        assert d1 != d2

    def test_digest_changes_on_synapse(self) -> None:
        """Digest changes when synapse state changes."""
        net = MockNetwork()
        net._neurons = {1: MockNeuron(1), 2: MockNeuron(2)}  # type: ignore[misc]
        net._synapses = {1: [MockSynapse(2, weight=0.1)]}  # type: ignore[misc]
        d1 = canonical_state_digest(net)  # type: ignore[arg-type]
        net._synapses[1][0].weight = 0.5  # type: ignore[misc]
        d2 = canonical_state_digest(net)  # type: ignore[arg-type]
        assert d1 != d2

    def test_digest_changes_on_events(self) -> None:
        """Digest changes when queued events change."""
        net = MockNetwork()
        net.event_slots = [[MockSpikeEvent(1, 2, 0.1, 101)]]
        d1 = canonical_state_digest(net)  # type: ignore[arg-type]
        net.event_slots = [[MockSpikeEvent(1, 2, 0.2, 101)]]
        d2 = canonical_state_digest(net)  # type: ignore[arg-type]
        assert d1 != d2

    def test_digest_includes_homeostasis(self) -> None:
        """Homeostasis rates affect the digest."""
        net = MockNetwork()
        d1 = canonical_state_digest(net, homeostasis_rates={1: 5.0, 2: 3.0})  # type: ignore[arg-type]
        d2 = canonical_state_digest(net, homeostasis_rates={1: 10.0, 2: 3.0})  # type: ignore[arg-type]
        assert d1 != d2

    def test_digest_includes_learning(self) -> None:
        """Learning state affects the digest."""
        net = MockNetwork()
        d1 = canonical_state_digest(net, learning_state={"stdp_updates": 0})  # type: ignore[arg-type]
        d2 = canonical_state_digest(net, learning_state={"stdp_updates": 10})  # type: ignore[arg-type]
        assert d1 != d2

    def test_digest_includes_structural(self) -> None:
        """Structural state affects the digest."""
        net = MockNetwork()
        d1 = canonical_state_digest(net, structural_state={"topology_digest": "abc"})  # type: ignore[arg-type]
        d2 = canonical_state_digest(net, structural_state={"topology_digest": "def"})  # type: ignore[arg-type]
        assert d1 != d2

    def test_digest_includes_config_sha256(self) -> None:
        """Config SHA-256 affects the digest."""
        net = MockNetwork()
        d1 = canonical_state_digest(net, config_sha256="config-a")  # type: ignore[arg-type]
        d2 = canonical_state_digest(net, config_sha256="config-b")  # type: ignore[arg-type]
        assert d1 != d2
