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
class Neuron:
    v: float
    u: float
    energy: float
    threshold_adaptation: float
    spike_counter: int
    last_spike_tick: int


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
    neurons: dict[int, Neuron]


def test_runtime_checkpoint_roundtrip(tmp_path: Path) -> None:
    """Exact dynamic state, RNG and queues survive JSON roundtrip."""

    network = Network(
        rng=random.Random(42),
        current_tick=10,
        total_spikes=7,
        total_events_processed=5,
        pending_currents={1: 3.5},
        input_cells={1},
        output_cells={2},
        event_slots=[[Event(1, 2, 0.4, 11)], []],
        neurons={
            1: Neuron(
                v=-64.123456789,
                u=-12.987654321,
                energy=0.9987654321,
                threshold_adaptation=0.00123456789,
                spike_counter=3,
                last_spike_tick=9,
            )
        },
    )
    checkpoint = capture_runtime_checkpoint(network)
    path = tmp_path / "runtime.json"
    write_runtime_checkpoint(path, checkpoint)
    loaded = read_runtime_checkpoint(path)
    assert loaded == checkpoint
    assert loaded.neuron_states[0].membrane_v == network.neurons[1].v
    assert loaded.neuron_states[0].energy == network.neurons[1].energy

    restored_rng = random.Random()
    restored_rng.setstate(
        (loaded.rng.version, tuple(loaded.rng.state), loaded.rng.gauss_next)
    )
    assert restored_rng.random() == network.rng.random()
