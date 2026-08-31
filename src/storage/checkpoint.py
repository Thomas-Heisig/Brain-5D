"""Typed runtime checkpoint sidecar for deterministic restore-and-continue."""

from __future__ import annotations

import json
import random
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, cast, runtime_checkable


class CheckpointEventLike(Protocol):
    """Queued spike event fields required by the checkpoint sidecar."""

    source_id: int
    target_id: int
    weight: float
    delivery_tick: int


class CheckpointNetworkLike(Protocol):
    """Runtime fields required for the base checkpoint contract."""

    rng: random.Random
    current_tick: int
    total_spikes: int
    total_events_processed: int
    pending_currents: Mapping[int, float]
    input_cells: set[int]
    output_cells: set[int]
    event_slots: Sequence[Sequence[CheckpointEventLike]]


class CheckpointNeuronLike(Protocol):
    """Exact neuron fields required for deterministic continuation."""

    neuron_id: int
    a: float
    b: float
    c: float
    d: float
    v: float
    u: float
    energy: float
    spike_cost: float
    spike_counter: int
    last_spike_tick: int
    threshold_adaptation: float
    last_external_current: float
    last_synaptic_current: float
    firing_rate_estimate: float
    pre_trace: float
    post_trace: float
    _spike_count_window: int
    _last_update_tick: int


class CheckpointSynapseLike(Protocol):
    """Exact synapse fields required for deterministic continuation."""

    target_id: int
    weight: float
    delay: int
    eligibility: float
    last_pre_spike: int


@runtime_checkable
class ExactCheckpointNetworkLike(Protocol):
    """Optional exact network surface available on the real core."""

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
class NeuronRuntimeRecord:
    """Exact neuron state overlaid after compact snapshot recovery."""

    neuron_id: int
    a: float
    b: float
    c: float
    d: float
    membrane_v: float
    recovery_u: float
    energy: float
    spike_cost: float
    threshold_adaptation: float
    spike_counter: int
    last_spike_tick: int
    last_external_current: float
    last_synaptic_current: float
    # Internal neuron state required for deterministic continuation
    firing_rate_estimate: float = 0.0
    spike_count_window: int = 0
    last_update_tick: int = 0
    pre_trace: float = 0.0
    post_trace: float = 0.0


@dataclass(frozen=True, slots=True)
class SynapseRuntimeRecord:
    """Exact synapse state overlaid after compact snapshot recovery."""

    source_id: int
    target_id: int
    weight: float
    delay: int
    eligibility: float
    last_pre_spike: int


@dataclass(frozen=True, slots=True)
class HomeostasisRuntimeRecord:
    """Homeostasis engine state for deterministic continuation."""

    neuron_id: int
    rate_hz: float


@dataclass(frozen=True, slots=True)
class PendingRewardRecord:
    """A reward signal pending future application."""

    value: float
    tick: int


@dataclass(frozen=True, slots=True)
class LearningRuntimeRecord:
    """Learning engine state for deterministic continuation.

    Includes per-synapse traces and pending reward signals that
    affect future synaptic weight changes.
    """

    pre_id: int
    target_id: int
    last_pre_tick: int | None
    last_post_tick: int | None
    eligibility_value: float
    eligibility_last_tick: int | None


@dataclass(frozen=True, slots=True)
class RuntimeCheckpoint:
    """Runtime state required for deterministic restore-and-continue.

    Version history:
        1: Initial checkpoint format
        2: Added neuron_states and synapse_states
        3: Added pending_currents, input_cells, output_cells
        4: Added homeostasis_state and learning_state
    """

    version: int
    current_tick: int
    total_spikes: int
    total_events_processed: int
    rng: RandomStateRecord
    pending_currents: tuple[tuple[int, float], ...]
    input_cells: tuple[int, ...]
    output_cells: tuple[int, ...]
    queued_events: tuple[QueuedEventRecord, ...]
    neuron_states: tuple[NeuronRuntimeRecord, ...] = ()
    synapse_states: tuple[SynapseRuntimeRecord, ...] = ()
    homeostasis_state: tuple[HomeostasisRuntimeRecord, ...] = ()
    learning_state: tuple[LearningRuntimeRecord, ...] = ()
    pending_rewards: tuple[PendingRewardRecord, ...] = ()


def capture_runtime_checkpoint(
    network: CheckpointNetworkLike,
    *,
    homeostasis_rates: dict[int, float] | None = None,
    learning_states: list[dict[str, object]] | None = None,
    pending_rewards: list[dict[str, object]] | None = None,
) -> RuntimeCheckpoint:
    """Capture runtime state and exact core state when available.

    Args:
        network: The network to capture state from.
        homeostasis_rates: Optional dict of neuron_id -> smoothed firing rate
            from the homeostasis engine.
        learning_states: Optional list of learning engine state dicts,
            each containing pre_id, target_id, last_pre_tick, last_post_tick,
            and eligibility_value.
        pending_rewards: Optional list of pending reward signal dicts,
            each containing value and tick.

    Returns:
        A RuntimeCheckpoint with version 4 (includes homeostasis + learning).
    """
    version, raw_state, gauss_next = network.rng.getstate()
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
    neuron_states: tuple[NeuronRuntimeRecord, ...] = ()
    synapse_states: tuple[SynapseRuntimeRecord, ...] = ()
    if isinstance(network, ExactCheckpointNetworkLike):
        neuron_states = tuple(
            NeuronRuntimeRecord(
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
                firing_rate_estimate=float(neuron.firing_rate_estimate),
                spike_count_window=int(
                    neuron._spike_count_window  # pyright: ignore[reportPrivateUsage]
                ),
                last_update_tick=int(
                    neuron._last_update_tick  # pyright: ignore[reportPrivateUsage]
                ),
                pre_trace=float(neuron.pre_trace),
                post_trace=float(neuron.post_trace),
            )
            for neuron_id, neuron in sorted(network.neurons.items())
        )
        synapse_states = tuple(
            SynapseRuntimeRecord(
                source_id=int(source_id),
                target_id=int(synapse.target_id),
                weight=float(synapse.weight),
                delay=int(synapse.delay),
                eligibility=float(synapse.eligibility),
                last_pre_spike=int(synapse.last_pre_spike),
            )
            for source_id, synapses in sorted(network.synapses.items())
            for synapse in synapses
        )

    # Capture homeostasis state
    homeostasis_state: tuple[HomeostasisRuntimeRecord, ...] = ()
    if homeostasis_rates is not None:
        homeostasis_state = tuple(
            HomeostasisRuntimeRecord(neuron_id=int(nid), rate_hz=float(rate))
            for nid, rate in sorted(homeostasis_rates.items())
        )

    # Capture learning state
    learning_state: tuple[LearningRuntimeRecord, ...] = ()
    if learning_states is not None:
        learning_state = tuple(
            LearningRuntimeRecord(
                pre_id=int(cast("int | str", s["pre_id"])),
                target_id=int(cast("int | str", s["target_id"])),
                last_pre_tick=(
                    int(cast("int | str", s["last_pre_tick"]))
                    if s.get("last_pre_tick") is not None
                    else None
                ),
                last_post_tick=(
                    int(cast("int | str", s["last_post_tick"]))
                    if s.get("last_post_tick") is not None
                    else None
                ),
                eligibility_value=float(
                    cast("int | float | str", s.get("eligibility_value", 0.0))
                ),
                eligibility_last_tick=(
                    int(cast("int | str", s["eligibility_last_tick"]))
                    if s.get("eligibility_last_tick") is not None
                    else None
                ),
            )
            for s in learning_states
        )

    # Capture pending rewards
    pending_reward_records: tuple[PendingRewardRecord, ...] = ()
    if pending_rewards is not None:
        pending_reward_records = tuple(
            PendingRewardRecord(
                value=float(cast("int | float | str", r["value"])),
                tick=int(cast("int | str", r["tick"])),
            )
            for r in pending_rewards
        )

    return RuntimeCheckpoint(
        version=4,
        current_tick=int(network.current_tick),
        total_spikes=int(network.total_spikes),
        total_events_processed=int(network.total_events_processed),
        rng=RandomStateRecord(
            int(version), tuple(int(value) for value in raw_state), gauss_next
        ),
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
        homeostasis_state=homeostasis_state,
        learning_state=learning_state,
        pending_rewards=pending_reward_records,
    )


def write_runtime_checkpoint(path: Path, checkpoint: RuntimeCheckpoint) -> None:
    """Write a deterministic JSON runtime sidecar."""
    payload: dict[str, object] = {
        "version": checkpoint.version,
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
                "firing_rate_estimate": state.firing_rate_estimate,
                "spike_count_window": state.spike_count_window,
                "last_update_tick": state.last_update_tick,
                "pre_trace": state.pre_trace,
                "post_trace": state.post_trace,
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
        "homeostasis_state": [
            {
                "neuron_id": state.neuron_id,
                "rate_hz": state.rate_hz,
            }
            for state in checkpoint.homeostasis_state
        ],
        "learning_state": [
            {
                "pre_id": state.pre_id,
                "target_id": state.target_id,
                "last_pre_tick": state.last_pre_tick,
                "last_post_tick": state.last_post_tick,
                "eligibility_value": state.eligibility_value,
                "eligibility_last_tick": state.eligibility_last_tick,
            }
            for state in checkpoint.learning_state
        ],
        "pending_rewards": [
            {
                "value": r.value,
                "tick": r.tick,
            }
            for r in checkpoint.pending_rewards
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )


def _mapping(value: object, name: str) -> dict[str, object]:
    """Validate and cast a JSON object to dict[str, object]."""
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    # Cast to dict[str, object] after validation
    value = cast(dict[str, object], value)
    result: dict[str, object] = {}
    for key, item in value.items():
        # key is already str due to the cast, so no need for isinstance check
        result[key] = item
    return result


def _list(value: object, name: str) -> list[object]:
    """Validate and cast a JSON array to list[object]."""
    if not isinstance(value, list):
        raise ValueError(f"{name} must be a list")
    return cast(list[object], value)


def _int(value: object, name: str) -> int:
    """Validate and cast a JSON value to int."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    return value


def _float(value: object, name: str) -> float:
    """Validate and cast a JSON value to float."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    return float(value)


def _optional_float(value: object, name: str) -> float | None:
    """Validate and cast a JSON value to optional float."""
    if value is None:
        return None
    return _float(value, name)


def read_runtime_checkpoint(path: Path) -> RuntimeCheckpoint:
    """Read and strictly validate checkpoint versions 1 through 4."""
    loaded: object = json.loads(path.read_text(encoding="utf-8"))
    raw = _mapping(loaded, "checkpoint")
    version = _int(raw.get("version", 0), "version")
    if version not in {1, 2, 3, 4}:
        raise ValueError("unsupported runtime checkpoint")
    rng_raw = _mapping(raw.get("rng"), "rng")
    state_raw = _list(rng_raw.get("state"), "rng.state")

    pending: list[tuple[int, float]] = []
    for index, item in enumerate(_list(raw.get("pending_currents", []), "pending")):
        pair = _list(item, f"pending_currents[{index}]")
        if len(pair) != 2:
            raise ValueError("invalid pending-current record")
        pending.append(
            (
                _int(pair[0], f"pending_currents[{index}].id"),
                _float(pair[1], f"pending_currents[{index}].value"),
            )
        )

    events: list[QueuedEventRecord] = []
    for index, item in enumerate(_list(raw.get("queued_events", []), "events")):
        event = _mapping(item, f"queued_events[{index}]")
        events.append(
            QueuedEventRecord(
                source_id=_int(event.get("source_id"), "event.source_id"),
                target_id=_int(event.get("target_id"), "event.target_id"),
                weight=_float(event.get("weight"), "event.weight"),
                delivery_tick=_int(event.get("delivery_tick"), "event.delivery_tick"),
            )
        )

    neuron_states: list[NeuronRuntimeRecord] = []
    for index, item in enumerate(_list(raw.get("neuron_states", []), "neurons")):
        state = _mapping(item, f"neuron_states[{index}]")
        neuron_states.append(
            NeuronRuntimeRecord(
                neuron_id=_int(state.get("neuron_id"), "neuron.neuron_id"),
                a=_float(state.get("a"), "neuron.a"),
                b=_float(state.get("b"), "neuron.b"),
                c=_float(state.get("c"), "neuron.c"),
                d=_float(state.get("d"), "neuron.d"),
                membrane_v=_float(state.get("membrane_v"), "neuron.v"),
                recovery_u=_float(state.get("recovery_u"), "neuron.u"),
                energy=_float(state.get("energy"), "neuron.energy"),
                spike_cost=_float(state.get("spike_cost"), "neuron.spike_cost"),
                threshold_adaptation=_float(
                    state.get("threshold_adaptation"), "neuron.threshold"
                ),
                spike_counter=_int(state.get("spike_counter"), "neuron.spike_counter"),
                last_spike_tick=_int(
                    state.get("last_spike_tick"), "neuron.last_spike_tick"
                ),
                last_external_current=_float(
                    state.get("last_external_current", 0.0),
                    "neuron.last_external_current",
                ),
                last_synaptic_current=_float(
                    state.get("last_synaptic_current", 0.0),
                    "neuron.last_synaptic_current",
                ),
                firing_rate_estimate=_float(
                    state.get("firing_rate_estimate", 0.0),
                    "neuron.firing_rate_estimate",
                ),
                spike_count_window=_int(
                    state.get("spike_count_window", 0),
                    "neuron.spike_count_window",
                ),
                last_update_tick=_int(
                    state.get("last_update_tick", 0),
                    "neuron.last_update_tick",
                ),
                pre_trace=_float(
                    state.get("pre_trace", 0.0),
                    "neuron.pre_trace",
                ),
                post_trace=_float(
                    state.get("post_trace", 0.0),
                    "neuron.post_trace",
                ),
            )
        )

    synapse_states: list[SynapseRuntimeRecord] = []
    for index, item in enumerate(_list(raw.get("synapse_states", []), "synapses")):
        state = _mapping(item, f"synapse_states[{index}]")
        synapse_states.append(
            SynapseRuntimeRecord(
                source_id=_int(state.get("source_id"), "synapse.source_id"),
                target_id=_int(state.get("target_id"), "synapse.target_id"),
                weight=_float(state.get("weight"), "synapse.weight"),
                delay=_int(state.get("delay"), "synapse.delay"),
                eligibility=_float(state.get("eligibility"), "synapse.eligibility"),
                last_pre_spike=_int(
                    state.get("last_pre_spike"), "synapse.last_pre_spike"
                ),
            )
        )

    input_raw = _list(raw.get("input_cells", []), "input_cells")
    output_raw = _list(raw.get("output_cells", []), "output_cells")

    # Read homeostasis state (version 4+)
    homeostasis_state: list[HomeostasisRuntimeRecord] = []
    for index, item in enumerate(
        _list(raw.get("homeostasis_state", []), "homeostasis")
    ):
        state = _mapping(item, f"homeostasis_state[{index}]")
        homeostasis_state.append(
            HomeostasisRuntimeRecord(
                neuron_id=_int(state.get("neuron_id"), "homeostasis.neuron_id"),
                rate_hz=_float(state.get("rate_hz"), "homeostasis.rate_hz"),
            )
        )

    # Read learning state (version 4+)
    learning_state: list[LearningRuntimeRecord] = []
    for index, item in enumerate(_list(raw.get("learning_state", []), "learning")):
        state = _mapping(item, f"learning_state[{index}]")
        learning_state.append(
            LearningRuntimeRecord(
                pre_id=_int(state.get("pre_id"), "learning.pre_id"),
                target_id=_int(state.get("target_id"), "learning.target_id"),
                last_pre_tick=(
                    _int(state["last_pre_tick"], "learning.last_pre_tick")
                    if state.get("last_pre_tick") is not None
                    else None
                ),
                last_post_tick=(
                    _int(state["last_post_tick"], "learning.last_post_tick")
                    if state.get("last_post_tick") is not None
                    else None
                ),
                eligibility_value=_float(
                    state.get("eligibility_value", 0.0), "learning.eligibility_value"
                ),
                eligibility_last_tick=(
                    _int(
                        state["eligibility_last_tick"], "learning.eligibility_last_tick"
                    )
                    if state.get("eligibility_last_tick") is not None
                    else None
                ),
            )
        )

    # Read pending rewards (version 4+)
    pending_rewards: list[PendingRewardRecord] = []
    for index, item in enumerate(
        _list(raw.get("pending_rewards", []), "pending_rewards")
    ):
        r = _mapping(item, f"pending_rewards[{index}]")
        pending_rewards.append(
            PendingRewardRecord(
                value=_float(r.get("value", 0.0), "pending_reward.value"),
                tick=_int(r.get("tick", 0), "pending_reward.tick"),
            )
        )

    return RuntimeCheckpoint(
        version=version,
        current_tick=_int(raw.get("current_tick"), "current_tick"),
        total_spikes=_int(raw.get("total_spikes"), "total_spikes"),
        total_events_processed=_int(
            raw.get("total_events_processed"), "total_events_processed"
        ),
        rng=RandomStateRecord(
            version=_int(rng_raw.get("version"), "rng.version"),
            state=tuple(_int(value, "rng.state item") for value in state_raw),
            gauss_next=_optional_float(rng_raw.get("gauss_next"), "rng.gauss_next"),
        ),
        pending_currents=tuple(pending),
        input_cells=tuple(_int(value, "input cell") for value in input_raw),
        output_cells=tuple(_int(value, "output cell") for value in output_raw),
        queued_events=tuple(events),
        neuron_states=tuple(neuron_states),
        synapse_states=tuple(synapse_states),
        homeostasis_state=tuple(homeostasis_state),
        learning_state=tuple(learning_state),
        pending_rewards=tuple(pending_rewards),
    )
