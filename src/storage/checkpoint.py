"""Typed runtime checkpoint sidecar for deterministic restore-and-continue.

The frozen .b5d V1 snapshot intentionally keeps its compact optical record.
That record quantizes selected dynamic values.  Exact continuation therefore
stores the runtime-critical neuron values in this sidecar and reapplies them
after snapshot/journal reconstruction.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
from pathlib import Path
import random
from typing import Protocol


class CheckpointEventLike(Protocol):
    """Queued spike event fields required by the checkpoint sidecar."""

    source_id: int
    target_id: int
    weight: float
    delivery_tick: int


class CheckpointNeuronLike(Protocol):
    """Exact dynamic neuron fields required for deterministic continuation."""

    v: float
    u: float
    energy: float
    threshold_adaptation: float
    spike_counter: int
    last_spike_tick: int


class CheckpointNetworkLike(Protocol):
    """Runtime fields required to persist non-snapshot simulation state."""

    rng: random.Random
    current_tick: int
    total_spikes: int
    total_events_processed: int
    pending_currents: Mapping[int, float]
    input_cells: set[int]
    output_cells: set[int]
    event_slots: Sequence[Sequence[CheckpointEventLike]]
    neurons: Mapping[int, CheckpointNeuronLike]


@dataclass(frozen=True, slots=True)
class RandomStateRecord:
    """JSON-safe representation of ``random.Random`` state."""

    version: int
    state: tuple[int, ...]
    gauss_next: float | None


@dataclass(frozen=True, slots=True)
class QueuedEventRecord:
    """One future spike delivery retained across restart."""

    source_id: int
    target_id: int
    weight: float
    delivery_tick: int


@dataclass(frozen=True, slots=True)
class RuntimeNeuronStateRecord:
    """Exact dynamic neuron state layered over the compact snapshot record."""

    neuron_id: int
    membrane_v: float
    recovery_u: float
    energy: float
    threshold_adaptation: float
    spike_counter: int
    last_spike_tick: int


@dataclass(frozen=True, slots=True)
class RuntimeCheckpoint:
    """Non-topological runtime state required for deterministic continuation."""

    current_tick: int
    total_spikes: int
    total_events_processed: int
    rng: RandomStateRecord
    pending_currents: tuple[tuple[int, float], ...]
    input_cells: tuple[int, ...]
    output_cells: tuple[int, ...]
    queued_events: tuple[QueuedEventRecord, ...]
    neuron_states: tuple[RuntimeNeuronStateRecord, ...]


def capture_runtime_checkpoint(network: CheckpointNetworkLike) -> RuntimeCheckpoint:
    """Capture exact runtime state from a live network at a tick boundary."""

    version, raw_state, gauss_next = network.rng.getstate()
    state_tuple = tuple(int(value) for value in raw_state)
    queued = tuple(
        QueuedEventRecord(
            source_id=int(event.source_id),
            target_id=int(event.target_id),
            weight=float(event.weight),
            delivery_tick=int(event.delivery_tick),
        )
        for slot in network.event_slots
        for event in slot
    )
    neuron_states = tuple(
        RuntimeNeuronStateRecord(
            neuron_id=int(neuron_id),
            membrane_v=float(neuron.v),
            recovery_u=float(neuron.u),
            energy=float(neuron.energy),
            threshold_adaptation=float(neuron.threshold_adaptation),
            spike_counter=int(neuron.spike_counter),
            last_spike_tick=int(neuron.last_spike_tick),
        )
        for neuron_id, neuron in sorted(network.neurons.items())
    )
    return RuntimeCheckpoint(
        current_tick=int(network.current_tick),
        total_spikes=int(network.total_spikes),
        total_events_processed=int(network.total_events_processed),
        rng=RandomStateRecord(int(version), state_tuple, gauss_next),
        pending_currents=tuple(
            sorted(
                (int(key), float(value))
                for key, value in network.pending_currents.items()
            )
        ),
        input_cells=tuple(sorted(int(value) for value in network.input_cells)),
        output_cells=tuple(sorted(int(value) for value in network.output_cells)),
        queued_events=queued,
        neuron_states=neuron_states,
    )


def write_runtime_checkpoint(path: Path, checkpoint: RuntimeCheckpoint) -> None:
    """Write a deterministic JSON checkpoint sidecar."""

    payload: dict[str, object] = {
        "version": 2,
        "current_tick": checkpoint.current_tick,
        "total_spikes": checkpoint.total_spikes,
        "total_events_processed": checkpoint.total_events_processed,
        "rng": {
            "version": checkpoint.rng.version,
            "state": list(checkpoint.rng.state),
            "gauss_next": checkpoint.rng.gauss_next,
        },
        "pending_currents": [list(item) for item in checkpoint.pending_currents],
        "input_cells": list(checkpoint.input_cells),
        "output_cells": list(checkpoint.output_cells),
        "queued_events": [
            {
                "source_id": event.source_id,
                "target_id": event.target_id,
                "weight": event.weight,
                "delivery_tick": event.delivery_tick,
            }
            for event in checkpoint.queued_events
        ],
        "neuron_states": [
            {
                "neuron_id": state.neuron_id,
                "membrane_v": state.membrane_v,
                "recovery_u": state.recovery_u,
                "energy": state.energy,
                "threshold_adaptation": state.threshold_adaptation,
                "spike_counter": state.spike_counter,
                "last_spike_tick": state.last_spike_tick,
            }
            for state in checkpoint.neuron_states
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )


def _mapping(value: object, message: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(message)
    return {str(key): item for key, item in value.items()}


def _list(value: object, message: str) -> list[object]:
    if not isinstance(value, list):
        raise ValueError(message)
    return value


def read_runtime_checkpoint(path: Path) -> RuntimeCheckpoint:
    """Read and validate runtime checkpoint sidecar version 1 or 2."""

    raw_object: object = json.loads(path.read_text(encoding="utf-8"))
    raw = _mapping(raw_object, "runtime checkpoint must be an object")
    version = int(raw.get("version", 0))
    if version not in {1, 2}:
        raise ValueError("unsupported runtime checkpoint")

    rng_raw = _mapping(raw.get("rng"), "runtime checkpoint RNG state is missing")
    state_raw = _list(rng_raw.get("state"), "runtime checkpoint RNG vector is invalid")
    pending_raw = _list(raw.get("pending_currents", []), "invalid pending currents")
    queued_raw = _list(raw.get("queued_events", []), "invalid queued events")
    input_raw = _list(raw.get("input_cells", []), "invalid input cells")
    output_raw = _list(raw.get("output_cells", []), "invalid output cells")

    pending: list[tuple[int, float]] = []
    for item in pending_raw:
        pair = _list(item, "invalid pending-current record")
        if len(pair) != 2:
            raise ValueError("invalid pending-current record")
        pending.append((int(pair[0]), float(pair[1])))

    events: list[QueuedEventRecord] = []
    for item in queued_raw:
        event = _mapping(item, "invalid queued-event record")
        events.append(
            QueuedEventRecord(
                source_id=int(event["source_id"]),
                target_id=int(event["target_id"]),
                weight=float(event["weight"]),
                delivery_tick=int(event["delivery_tick"]),
            )
        )

    neuron_states: list[RuntimeNeuronStateRecord] = []
    if version >= 2:
        states_raw = _list(raw.get("neuron_states", []), "invalid neuron states")
        for item in states_raw:
            state = _mapping(item, "invalid neuron-state record")
            neuron_states.append(
                RuntimeNeuronStateRecord(
                    neuron_id=int(state["neuron_id"]),
                    membrane_v=float(state["membrane_v"]),
                    recovery_u=float(state["recovery_u"]),
                    energy=float(state["energy"]),
                    threshold_adaptation=float(state["threshold_adaptation"]),
                    spike_counter=int(state["spike_counter"]),
                    last_spike_tick=int(state["last_spike_tick"]),
                )
            )

    return RuntimeCheckpoint(
        current_tick=int(raw["current_tick"]),
        total_spikes=int(raw["total_spikes"]),
        total_events_processed=int(raw["total_events_processed"]),
        rng=RandomStateRecord(
            version=int(rng_raw["version"]),
            state=tuple(int(value) for value in state_raw),
            gauss_next=(
                None
                if rng_raw.get("gauss_next") is None
                else float(rng_raw["gauss_next"])
            ),
        ),
        pending_currents=tuple(pending),
        input_cells=tuple(int(value) for value in input_raw),
        output_cells=tuple(int(value) for value in output_raw),
        queued_events=tuple(events),
        neuron_states=tuple(neuron_states),
    )
