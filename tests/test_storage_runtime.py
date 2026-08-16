"""Runtime persistence hook tests for alpha.3."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from src.storage.delta_journal import DeltaJournal, DeltaType
from src.storage.runtime import StorageRuntimeConfig, StorageSession


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


@dataclass(frozen=True, slots=True)
class FakeStep:
    tick: int
    spike_ids: tuple[int, ...]


Hook = Callable[[FakeStep], None]


@dataclass(slots=True)
class FakeNetwork:
    dimensions: tuple[int, int, int, int, int]
    current_tick: int
    neurons: dict[int, FakeNeuron]
    synapses: dict[int, list[FakeSynapse]]
    hooks: list[Hook] = field(default_factory=list)

    def add_post_step_hook(self, hook: Hook) -> None:
        self.hooks.append(hook)

    def remove_post_step_hook(self, hook: Hook) -> None:
        self.hooks.remove(hook)


def test_storage_session_captures_changes_and_commits(tmp_path: Path) -> None:
    net = FakeNetwork(
        dimensions=(10, 10, 10, 10, 10),
        current_tick=0,
        neurons={1: FakeNeuron(), 2: FakeNeuron()},
        synapses={1: [FakeSynapse(2, 0.2, 1)], 2: []},
    )
    config = StorageRuntimeConfig(
        snapshot_path=tmp_path / "live.b5d",
        journal_path=tmp_path / "live.b5d.journal",
        commit_interval_ticks=1,
    )
    session = StorageSession(net, config)
    session.start()
    assert session.attached
    net.current_tick = 1
    net.neurons[1].v = -40.0
    net.neurons[1].spike_counter = 1
    net.neurons[1].last_spike_tick = 1
    net.synapses[1][0].weight = 0.7
    for hook in tuple(net.hooks):
        hook(FakeStep(1, (1,)))
    session.close()

    assert config.snapshot_path.exists()
    assert config.journal_path.exists()
    with DeltaJournal(config.journal_path) as journal:
        kinds = {entry.delta_type for entry in journal.iter_committed_entries()}
    assert DeltaType.NEURON_STATE in kinds
    assert DeltaType.SYNAPSE_WEIGHT in kinds
    assert DeltaType.SPIKE_EVENT in kinds
    assert session.stats.commits == 1
    assert not session.attached
