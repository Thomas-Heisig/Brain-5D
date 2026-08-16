"""Typed runtime checkpoint sidecar for deterministic restore-and-continue."""

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
class RuntimeCheckpoint:
    """Non-neuron runtime state that the frozen `.b5d` V1 cannot contain."""

    current_tick: int
    total_spikes: int
    total_events_processed: int
    rng: RandomStateRecord
    pending_currents: tuple[tuple[int, float], ...]
    input_cells: tuple[int, ...]
    output_cells: tuple[int, ...]
    queued_events: tuple[QueuedEventRecord, ...]


def capture_runtime_checkpoint(network: CheckpointNetworkLike) -> RuntimeCheckpoint:
    """Capture deterministic runtime state from a live network."""
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
    )


def write_runtime_checkpoint(path: Path, checkpoint: RuntimeCheckpoint) -> None:
    """Write a deterministic JSON checkpoint sidecar."""
    payload = {
        "version": 1,
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
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )


def read_runtime_checkpoint(path: Path) -> RuntimeCheckpoint:
    """Read and validate a runtime checkpoint sidecar."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("version") != 1:
        raise ValueError("unsupported runtime checkpoint")
    rng_raw = raw.get("rng")
    if not isinstance(rng_raw, dict):
        raise ValueError("runtime checkpoint RNG state is missing")
    state_raw = rng_raw.get("state")
    if not isinstance(state_raw, list):
        raise ValueError("runtime checkpoint RNG vector is invalid")
    pending_raw = raw.get("pending_currents", [])
    queued_raw = raw.get("queued_events", [])
    if not isinstance(pending_raw, list) or not isinstance(queued_raw, list):
        raise ValueError("runtime checkpoint collections are invalid")
    pending: list[tuple[int, float]] = []
    for item in pending_raw:
        if not isinstance(item, list) or len(item) != 2:
            raise ValueError("invalid pending-current record")
        pending.append((int(item[0]), float(item[1])))
    events: list[QueuedEventRecord] = []
    for item in queued_raw:
        if not isinstance(item, dict):
            raise ValueError("invalid queued-event record")
        events.append(
            QueuedEventRecord(
                source_id=int(item["source_id"]),
                target_id=int(item["target_id"]),
                weight=float(item["weight"]),
                delivery_tick=int(item["delivery_tick"]),
            )
        )
    input_raw = raw.get("input_cells", [])
    output_raw = raw.get("output_cells", [])
    if not isinstance(input_raw, list) or not isinstance(output_raw, list):
        raise ValueError("runtime checkpoint cell sets are invalid")
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
    )
