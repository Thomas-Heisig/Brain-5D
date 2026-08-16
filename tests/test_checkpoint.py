"""Runtime checkpoint sidecar tests."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import random

from src.storage.checkpoint import (
    capture_runtime_checkpoint,
    read_runtime_checkpoint,
    write_runtime_checkpoint,
)


@dataclass(slots=True)
class Event:
    source_id: int
    target_id: int
    weight: float
    delivery_tick: int


@dataclass(slots=True)
class Network:
    rng: random.Random
    current_tick: int
    total_spikes: int
    total_events_processed: int
    pending_currents: dict[int, float]
    input_cells: set[int]
    output_cells: set[int]
    event_slots: list[list[Event]]


def test_runtime_checkpoint_roundtrip(tmp_path: Path) -> None:
    network = Network(
        rng=random.Random(42),
        current_tick=10,
        total_spikes=7,
        total_events_processed=5,
        pending_currents={1: 3.5},
        input_cells={1},
        output_cells={2},
        event_slots=[[Event(1, 2, 0.4, 11)], []],
    )
    checkpoint = capture_runtime_checkpoint(network)
    path = tmp_path / "runtime.json"
    write_runtime_checkpoint(path, checkpoint)
    loaded = read_runtime_checkpoint(path)
    assert loaded == checkpoint
    restored_rng = random.Random()
    restored_rng.setstate(
        (loaded.rng.version, tuple(loaded.rng.state), loaded.rng.gauss_next)
    )
    assert restored_rng.random() == network.rng.random()
