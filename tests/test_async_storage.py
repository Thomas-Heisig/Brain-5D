"""Bounded asynchronous storage tests."""

from __future__ import annotations

from pathlib import Path

from src.storage.async_runtime import AsyncStorageConfig, AsyncStorageSession
from src.storage.delta_journal import DeltaJournal, DeltaType
from src.storage.runtime import StorageRuntimeConfig
from tests.test_storage_runtime import FakeNetwork, FakeNeuron, FakeStep, FakeSynapse


def test_async_session_writes_and_reports_telemetry(tmp_path: Path) -> None:
    network = FakeNetwork(
        dimensions=(10, 10, 10, 10, 10),
        current_tick=0,
        neurons={1: FakeNeuron(), 2: FakeNeuron()},
        synapses={1: [FakeSynapse(2, 0.2, 1)], 2: []},
    )
    runtime = StorageRuntimeConfig(
        snapshot_path=tmp_path / "async.b5d",
        journal_path=tmp_path / "async.b5d.journal",
        commit_interval_ticks=1,
    )
    session = AsyncStorageSession(
        network,  # type: ignore[arg-type]
        runtime,
        AsyncStorageConfig(queue_size=8),
    )
    session.start()
    network.current_tick = 1
    network.neurons[1].v = -40.0
    network.neurons[1].spike_counter = 1
    network.neurons[1].last_spike_tick = 1
    for hook in tuple(network.hooks):
        hook(FakeStep(1, (1,)))
    session.close()
    telemetry = session.telemetry
    assert telemetry.batches_enqueued == 1
    assert telemetry.batches_written == 1
    assert telemetry.deltas_written >= 2
    assert telemetry.dropped_batches == 0
    assert not telemetry.worker_failed
    with DeltaJournal(runtime.journal_path) as journal:
        kinds = {entry.delta_type for entry in journal.iter_committed_entries()}
    assert DeltaType.NEURON_STATE in kinds
    assert DeltaType.SPIKE_EVENT in kinds
