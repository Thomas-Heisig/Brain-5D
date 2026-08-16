"""End-to-end snapshot+journal recovery tests."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from src.storage.b5d import B5DReader, B5DSnapshotWriter
from src.storage.delta_codec import (
    NeuronStateDelta,
    SynapseWeightDelta,
    encode_neuron_state,
    encode_synapse_weight,
)
from src.storage.delta_journal import DeltaJournal
from src.storage.recovery import RecoveryManager


@dataclass(slots=True)
class FakeNeuron:
    a: float = 0.02
    b: float = 0.2
    c: float = -65.0
    d: float = 8.0
    v: float = -60.0
    u: float = -12.0
    energy: float = 0.8
    spike_cost: float = 0.001
    spike_counter: int = 0
    last_spike_tick: int = -1
    threshold_adaptation: float = 0.0


@dataclass(slots=True)
class FakeSynapse:
    target_id: int
    weight: float
    delay: int
    eligibility: float = 0.0
    last_pre_spike: int = -1


@dataclass(slots=True)
class FakeNetwork:
    dimensions: tuple[int, int, int, int, int]
    current_tick: int
    neurons: dict[int, FakeNeuron]
    synapses: dict[int, list[FakeSynapse]]


def _snapshot(path: Path) -> None:
    network = FakeNetwork(
        dimensions=(10, 10, 10, 10, 10),
        current_tick=5,
        neurons={1: FakeNeuron(), 2: FakeNeuron(v=-55.0)},
        synapses={1: [FakeSynapse(2, 0.2, 2)], 2: []},
    )
    B5DSnapshotWriter(restart_capable=True).write(path, network)


def test_recovery_applies_committed_state(tmp_path: Path) -> None:
    snapshot = tmp_path / "base.b5d"
    journal_path = tmp_path / "base.b5d.journal"
    recovered = tmp_path / "recovered.b5d"
    _snapshot(snapshot)
    with DeltaJournal(journal_path, base_tick=5) as journal:
        journal.append(
            encode_neuron_state(
                6,
                NeuronStateDelta(1, -40.0, -8.0, 0.5, 3, 6),
            )
        )
        journal.append(
            encode_synapse_weight(
                6,
                SynapseWeightDelta(1, 2, 0.75, 0.2, 6),
            )
        )
        journal.commit()
    result = RecoveryManager(snapshot, journal_path).recover(recovered)
    assert result.success, result.error
    assert result.applied_entries == 2
    assert result.recovered_tick == 6
    with B5DReader(recovered) as reader:
        neuron = reader.get_neuron(1)
        assert neuron is not None
        assert neuron.optical.membrane_v == pytest.approx(-40.0, abs=0.01)
        synapse = list(reader.get_synapses(1))[0]
        assert synapse.weight == pytest.approx(0.75)
        assert synapse.eligibility == pytest.approx(0.2)


def test_recovery_ignores_uncommitted_tail(tmp_path: Path) -> None:
    snapshot = tmp_path / "base.b5d"
    journal_path = tmp_path / "base.b5d.journal"
    recovered = tmp_path / "recovered.b5d"
    _snapshot(snapshot)
    with DeltaJournal(journal_path, base_tick=5) as journal:
        journal.append(
            encode_neuron_state(6, NeuronStateDelta(1, -50.0, -9.0, 0.7, 1, 6))
        )
        journal.commit()
        journal.append(
            encode_neuron_state(7, NeuronStateDelta(1, -20.0, -2.0, 0.2, 2, 7))
        )
    result = RecoveryManager(snapshot, journal_path).recover(recovered)
    assert result.success, result.error
    with B5DReader(recovered) as reader:
        neuron = reader.get_neuron(1)
        assert neuron is not None
        assert neuron.optical.membrane_v == pytest.approx(-50.0, abs=0.01)
