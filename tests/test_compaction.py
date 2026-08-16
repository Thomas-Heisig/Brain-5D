"""Generation-manifest compaction tests."""

from __future__ import annotations

from pathlib import Path

from src.storage.b5d import B5DSnapshotWriter
from src.storage.compaction import StorageCompactor
from src.storage.delta_codec import NeuronStateDelta, encode_neuron_state
from src.storage.delta_journal import DeltaJournal
from tests.test_storage_runtime import FakeNetwork, FakeNeuron, FakeSynapse


def test_compaction_publishes_new_generation(tmp_path: Path) -> None:
    network = FakeNetwork(
        dimensions=(10, 10, 10, 10, 10),
        current_tick=0,
        neurons={1: FakeNeuron(), 2: FakeNeuron()},
        synapses={1: [FakeSynapse(2, 0.2, 1)], 2: []},
    )
    snapshot = tmp_path / "brain5d.g0.b5d"
    journal_path = tmp_path / "brain5d.g0.b5d.journal"
    B5DSnapshotWriter(restart_capable=True).write(snapshot, network)
    with DeltaJournal(journal_path, base_tick=0) as journal:
        journal.append(
            encode_neuron_state(
                1,
                NeuronStateDelta(1, -40.0, -8.0, 0.5, 1, 1),
            )
        )
        journal.commit()
    compactor = StorageCompactor(tmp_path)
    compactor.initialize(snapshot, journal_path)
    result = compactor.compact()
    assert result.compacted
    assert result.generation == 1
    assert result.base_tick == 1
    assert result.snapshot_path.exists()
    assert result.journal_path.exists()
    active = compactor.manifest.read()
    assert active.generation == 1
