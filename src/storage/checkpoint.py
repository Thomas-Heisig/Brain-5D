"""Typed runtime checkpoint sidecar for deterministic restore-and-continue.

The frozen ``.b5d`` V1 snapshot deliberately uses compact float32 fields for
restart metadata and synapse values.  Exact continuation therefore stores the
runtime-critical neuron and synapse values in this JSON sidecar and reapplies
them after snapshot/journal reconstruction.
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
    """Exact neuron fields required for deterministic continuation."""

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


class CheckpointSynapseLike(Protocol):
    """Exact synapse fields required for deterministic continuation."""

    target_id: int
    weight: float
    delay: int
    eligibility: float
    last_pre_spike: int


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
    synapses: Mapping[int, Sequence[CheckpointSynapseLike]]


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
    """Exact neuron state layered over the compact snapshot record."""

    neuron_id: int
    a: float | None
    b: float | None
    c: float | None
    d: float | None
    membrane_v: float
    recovery_u: float
    energy: float
    spike_cost: float | None
    threshold_adaptation: float
    spike_counter: int
    last_spike_tick: int
    last_external_current: float
    last_synaptic_current: float


@dataclass(frozen=True, slots=True)
class RuntimeSynapseStateRecord:
    """Exact synapse state layered over the compact snapshot record."""

    source_id: int
    target_id: int
    weight: float
    delay: int
    eligibility: float
    last_pre_spike: int


@dataclass(frozen=True, slots=True)
class RuntimeCheckpoint:
    """Runtime state required for deterministic continuation."""

    current_tick: int
    total_spikes: int
    total_events_processed: int
    rng: RandomStateRecord
    pending_currents: tuple[tuple[int, float], ...]
    input_cells: tuple[int, ...]
    output_cells: tuple[int, ...]
    queued_events: tuple[QueuedEventRecord, ...]
    neuron_states: tuple[RuntimeNeuronStateRecord, ...] = ()
    synapse_states: tuple[RuntimeSynapseStateRecord, ...] = ()


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
            a=float(neuron.a),
            b=float(neuron.b),
            c=float(neuron.c),
            d=float(neuron.d),
            membrane_v=float(neuron.v),
            recovery_u=float(neuron.u),
            energy=float(neuron.energy),
            spike_cost=float(neuron.spike_cost),
            threshold_adaptation=float(neuron.threshold_adaptation),
            spike_counter=int(neuron.spike_counter),
            last_spike_tick=int(neuron.last_spike_tick),
            last_external_current=float(neuron.last_external_current),
            last_synaptic_current=float(neuron.last_synaptic_current),
        )
        for neuron_id, neuron in sorted(network.neurons.items())
    )
    synapse_states = tuple(
        RuntimeSynapseStateRecord(
            source_id=int(source_id),
            target_id=int(synapse.target_id),
            weight=float(synapse.weight),
            delay=int(synapse.delay),
            eligibility=float(synapse.eligibility),
            last_pre_spike=int(synapse.last_pre_spike),
        )
        for source_id in sorted(network.synapses)
        for synapse in sorted(
            network.synapses[source_id], key=lambda item: int(item.target_id)
        )
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
        synapse_states=synapse_states,
    )


def write_runtime_checkpoint(path: Path, checkpoint: RuntimeCheckpoint) -> None:
    """Write a deterministic version-3 JSON checkpoint sidecar."""

    payload: dict[str, object] = {
        "version": 3,
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
                "a": state.a,
                "b": state.b,
                "c": state.c,
                "d": state.d,
                "membrane_v": state.membrane_v,
                "recovery_u": state.recovery_u,
                "energy": state.energy,
                "spike_cost": state.spike_cost,
                "threshold_adaptation": state.threshold_adaptation,
                "spike_counter": state.spike_counter,
                "last_spike_tick": state.last_spike_tick,
                "last_external_current": state.last_external_current,
                "last_synaptic_current": state.last_synaptic_current,
            }
            for state in checkpoint.neuron_states
        ],
        "synapse_states": [
            {
                "source_id": state.source_id,
                "target_id": state.target_id,
                "weight": state.weight,
                "delay": state.delay,
                "eligibility": state.eligibility,
                "last_pre_spike": state.last_pre_spike,
            }
            for state in checkpoint.synapse_states
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


def _int_value(value: object, message: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError(message)
    try:
        return int(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(message) from exc


def _float_value(value: object, message: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError(message)
    try:
        return float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(message) from exc


def _optional_float(value: object, message: str) -> float | None:
    if value is None:
        return None
    return _float_value(value, message)


def _legacy_neuron_state(state: dict[str, object]) -> RuntimeNeuronStateRecord:
    """Read a v2 neuron state and fill exact static values from safe defaults."""

    return RuntimeNeuronStateRecord(
        neuron_id=_int_value(state.get("neuron_id"), "invalid neuron_id"),
        a=None,
        b=None,
        c=None,
        d=None,
        membrane_v=_float_value(state.get("membrane_v"), "invalid membrane_v"),
        recovery_u=_float_value(state.get("recovery_u"), "invalid recovery_u"),
        energy=_float_value(state.get("energy"), "invalid energy"),
        spike_cost=None,
        threshold_adaptation=_float_value(
            state.get("threshold_adaptation"), "invalid threshold adaptation"
        ),
        spike_counter=_int_value(state.get("spike_counter"), "invalid spike counter"),
        last_spike_tick=_int_value(
            state.get("last_spike_tick"), "invalid last spike tick"
        ),
        last_external_current=0.0,
        last_synaptic_current=0.0,
    )


def read_runtime_checkpoint(path: Path) -> RuntimeCheckpoint:
    """Read and validate runtime checkpoint sidecar version 1, 2, or 3."""

    raw_object: object = json.loads(path.read_text(encoding="utf-8"))
    raw = _mapping(raw_object, "runtime checkpoint must be an object")
    version = _int_value(raw.get("version", 0), "invalid runtime checkpoint version")
    if version not in {1, 2, 3}:
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
        pending.append(
            (
                _int_value(pair[0], "invalid pending-current neuron id"),
                _float_value(pair[1], "invalid pending-current value"),
            )
        )

    events: list[QueuedEventRecord] = []
    for item in queued_raw:
        event = _mapping(item, "invalid queued-event record")
        events.append(
            QueuedEventRecord(
                source_id=_int_value(event.get("source_id"), "invalid source_id"),
                target_id=_int_value(event.get("target_id"), "invalid target_id"),
                weight=_float_value(event.get("weight"), "invalid event weight"),
                delivery_tick=_int_value(
                    event.get("delivery_tick"), "invalid delivery tick"
                ),
            )
        )

    neuron_states: list[RuntimeNeuronStateRecord] = []
    if version >= 2:
        states_raw = _list(raw.get("neuron_states", []), "invalid neuron states")
        for item in states_raw:
            state = _mapping(item, "invalid neuron-state record")
            if version == 2:
                neuron_states.append(_legacy_neuron_state(state))
                continue
            neuron_states.append(
                RuntimeNeuronStateRecord(
                    neuron_id=_int_value(state.get("neuron_id"), "invalid neuron_id"),
                    a=_float_value(state.get("a"), "invalid neuron a"),
                    b=_float_value(state.get("b"), "invalid neuron b"),
                    c=_float_value(state.get("c"), "invalid neuron c"),
                    d=_float_value(state.get("d"), "invalid neuron d"),
                    membrane_v=_float_value(
                        state.get("membrane_v"), "invalid membrane_v"
                    ),
                    recovery_u=_float_value(
                        state.get("recovery_u"), "invalid recovery_u"
                    ),
                    energy=_float_value(state.get("energy"), "invalid energy"),
                    spike_cost=_float_value(
                        state.get("spike_cost"), "invalid spike cost"
                    ),
                    threshold_adaptation=_float_value(
                        state.get("threshold_adaptation"),
                        "invalid threshold adaptation",
                    ),
                    spike_counter=_int_value(
                        state.get("spike_counter"), "invalid spike counter"
                    ),
                    last_spike_tick=_int_value(
                        state.get("last_spike_tick"), "invalid last spike tick"
                    ),
                    last_external_current=_float_value(
                        state.get("last_external_current", 0.0),
                        "invalid last external current",
                    ),
                    last_synaptic_current=_float_value(
                        state.get("last_synaptic_current", 0.0),
                        "invalid last synaptic current",
                    ),
                )
            )

    synapse_states: list[RuntimeSynapseStateRecord] = []
    if version >= 3:
        synapses_raw = _list(raw.get("synapse_states", []), "invalid synapse states")
        for item in synapses_raw:
            state = _mapping(item, "invalid synapse-state record")
            synapse_states.append(
                RuntimeSynapseStateRecord(
                    source_id=_int_value(state.get("source_id"), "invalid source_id"),
                    target_id=_int_value(state.get("target_id"), "invalid target_id"),
                    weight=_float_value(state.get("weight"), "invalid synapse weight"),
                    delay=_int_value(state.get("delay"), "invalid synapse delay"),
                    eligibility=_float_value(
                        state.get("eligibility"), "invalid synapse eligibility"
                    ),
                    last_pre_spike=_int_value(
                        state.get("last_pre_spike"), "invalid last_pre_spike"
                    ),
                )
            )

    gauss_next = _optional_float(rng_raw.get("gauss_next"), "invalid gauss_next")
    return RuntimeCheckpoint(
        current_tick=_int_value(raw.get("current_tick"), "invalid current_tick"),
        total_spikes=_int_value(raw.get("total_spikes"), "invalid total_spikes"),
        total_events_processed=_int_value(
            raw.get("total_events_processed"), "invalid total_events_processed"
        ),
        rng=RandomStateRecord(
            version=_int_value(rng_raw.get("version"), "invalid RNG version"),
            state=tuple(
                _int_value(value, "invalid RNG state value") for value in state_raw
            ),
            gauss_next=gauss_next,
        ),
        pending_currents=tuple(pending),
        input_cells=tuple(
            _int_value(value, "invalid input cell") for value in input_raw
        ),
        output_cells=tuple(
            _int_value(value, "invalid output cell") for value in output_raw
        ),
        queued_events=tuple(events),
        neuron_states=tuple(neuron_states),
        synapse_states=tuple(synapse_states),
    )
