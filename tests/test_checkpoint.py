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
    a: float
    b: float
    c: float
    d: float
    v: float
    u: float
    energy: float
    spike_cost: float
    threshold_adaptation: float
    spike_counter: int
    last_spike_tick: int
    last_external_current: float
    last_synaptic_current: float


@dataclass(slots=True)
class Synapse:
    target_id: int
    weight: float
    delay: int
    eligibility: float
    last_pre_spike: int


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
    synapses: dict[int, list[Synapse]]


def test_runtime_checkpoint_roundtrip(tmp_path: Path) -> None:
    """Exact neuron, synapse, RNG and queue state survives JSON roundtrip."""

    network = Network(
        rng=random.Random(42),
        current_tick=10,
        total_spikes=7,
        total_events_processed=5,
        pending_currents={1: 3.5},
        input_cells={1},
        output_cells={2},
        event_slots=[[Event(1, 2, 0.4000000000000001, 11)], []],
        neurons={
            1: Neuron(
                a=0.020000000000000004,
                b=0.20000000000000004,
                c=-65.0,
                d=8.000000000000002,
                v=-64.123456789,
                u=-12.987654321,
                energy=0.9987654321,
                spike_cost=0.0010000000000000002,
                threshold_adaptation=0.00123456789,
                spike_counter=3,
                last_spike_tick=9,
                last_external_current=1.25,
                last_synaptic_current=0.75,
            )
        },
        synapses={
            1: [
                Synapse(
                    target_id=2,
                    weight=0.3333333333333333,
                    delay=2,
                    eligibility=0.1234567890123456,
                    last_pre_spike=8,
                )
            ]
        },
    )
    checkpoint = capture_runtime_checkpoint(network)
    path = tmp_path / "runtime.json"
    write_runtime_checkpoint(path, checkpoint)
    loaded = read_runtime_checkpoint(path)
    assert loaded == checkpoint
    assert loaded.neuron_states[0].a == network.neurons[1].a
    assert loaded.neuron_states[0].membrane_v == network.neurons[1].v
    assert loaded.neuron_states[0].energy == network.neurons[1].energy
    assert loaded.synapse_states[0].weight == network.synapses[1][0].weight
    restored_rng = random.Random()
    restored_rng.setstate(
        (loaded.rng.version, tuple(loaded.rng.state), loaded.rng.gauss_next)
    )
    assert restored_rng.random() == network.rng.random()
