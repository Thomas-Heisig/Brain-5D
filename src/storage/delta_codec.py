"""Typed binary payload codecs for Brain-5D journal deltas."""

from __future__ import annotations

from dataclasses import dataclass
import struct

from .b5d import B5DNeuronRecord, B5DSynapseRecord
from .delta_journal import DeltaRecord, DeltaType
from .optical_codec import (
    RECORD_SIZE as OPTICAL_RECORD_SIZE,
    OpticalPointState,
    decode_optical_record,
    encode_optical_record,
)

_NEURON_STATE_STRUCT = struct.Struct("<QdddQq")
_SYNAPSE_WEIGHT_STRUCT = struct.Struct("<QQddq")
_NEURON_REMOVE_STRUCT = struct.Struct("<Q")
_SYNAPSE_REMOVE_STRUCT = struct.Struct("<QQ")
_SYNAPSE_ADD_STRUCT = struct.Struct("<QQddIq")
_NEURON_ADD_CORE_STRUCT = struct.Struct("<dddddQq")
_SPIKE_EVENT_STRUCT = struct.Struct("<Q")


@dataclass(frozen=True, slots=True)
class NeuronStateDelta:
    """Dynamic state update for one existing neuron."""

    neuron_id: int
    membrane_v: float
    recovery_u: float
    energy: float
    spike_counter: int
    last_spike_tick: int


@dataclass(frozen=True, slots=True)
class SynapseWeightDelta:
    """Weight/eligibility update for one existing synapse."""

    source_id: int
    target_id: int
    weight: float
    eligibility: float
    last_pre_spike: int


@dataclass(frozen=True, slots=True)
class SynapseAddDelta:
    """Complete state required to add one synapse."""

    source_id: int
    target_id: int
    weight: float
    eligibility: float
    delay: int
    last_pre_spike: int


@dataclass(frozen=True, slots=True)
class SynapseRemoveDelta:
    """Identity of one synapse to remove."""

    source_id: int
    target_id: int


@dataclass(frozen=True, slots=True)
class NeuronRemoveDelta:
    """Identity of one neuron to remove."""

    neuron_id: int


@dataclass(frozen=True, slots=True)
class NeuronAddDelta:
    """Complete restart-capable state for one newly added neuron."""

    neuron_id: int
    tick: int
    optical: OpticalPointState
    a: float
    b: float
    c: float
    d: float
    spike_cost: float
    spike_counter: int
    last_spike_tick: int


@dataclass(frozen=True, slots=True)
class SpikeEventDelta:
    """Observed spike event retained for deterministic replay diagnostics."""

    neuron_id: int


def encode_neuron_state(tick: int, value: NeuronStateDelta) -> DeltaRecord:
    """Encode a neuron-state delta into one journal record."""
    payload = _NEURON_STATE_STRUCT.pack(
        value.neuron_id,
        value.membrane_v,
        value.recovery_u,
        value.energy,
        value.spike_counter,
        value.last_spike_tick,
    )
    return DeltaRecord(DeltaType.NEURON_STATE, tick, payload)


def decode_neuron_state(payload: bytes) -> NeuronStateDelta:
    """Decode one neuron-state payload."""
    if len(payload) != _NEURON_STATE_STRUCT.size:
        raise ValueError("invalid NEURON_STATE payload size")
    values = _NEURON_STATE_STRUCT.unpack(payload)
    return NeuronStateDelta(
        neuron_id=int(values[0]),
        membrane_v=float(values[1]),
        recovery_u=float(values[2]),
        energy=float(values[3]),
        spike_counter=int(values[4]),
        last_spike_tick=int(values[5]),
    )


def encode_synapse_weight(tick: int, value: SynapseWeightDelta) -> DeltaRecord:
    """Encode a synapse weight/eligibility update."""
    return DeltaRecord(
        DeltaType.SYNAPSE_WEIGHT,
        tick,
        _SYNAPSE_WEIGHT_STRUCT.pack(
            value.source_id,
            value.target_id,
            value.weight,
            value.eligibility,
            value.last_pre_spike,
        ),
    )


def decode_synapse_weight(payload: bytes) -> SynapseWeightDelta:
    """Decode one synapse weight payload."""
    if len(payload) != _SYNAPSE_WEIGHT_STRUCT.size:
        raise ValueError("invalid SYNAPSE_WEIGHT payload size")
    source_id, target_id, weight, eligibility, last_pre_spike = (
        _SYNAPSE_WEIGHT_STRUCT.unpack(payload)
    )
    return SynapseWeightDelta(
        int(source_id),
        int(target_id),
        float(weight),
        float(eligibility),
        int(last_pre_spike),
    )


def encode_synapse_add(tick: int, value: SynapseAddDelta) -> DeltaRecord:
    """Encode one synapse addition."""
    return DeltaRecord(
        DeltaType.SYNAPSE_ADD,
        tick,
        _SYNAPSE_ADD_STRUCT.pack(
            value.source_id,
            value.target_id,
            value.weight,
            value.eligibility,
            value.delay,
            value.last_pre_spike,
        ),
    )


def decode_synapse_add(payload: bytes) -> SynapseAddDelta:
    """Decode one synapse addition."""
    if len(payload) != _SYNAPSE_ADD_STRUCT.size:
        raise ValueError("invalid SYNAPSE_ADD payload size")
    values = _SYNAPSE_ADD_STRUCT.unpack(payload)
    return SynapseAddDelta(
        source_id=int(values[0]),
        target_id=int(values[1]),
        weight=float(values[2]),
        eligibility=float(values[3]),
        delay=int(values[4]),
        last_pre_spike=int(values[5]),
    )


def encode_synapse_remove(tick: int, value: SynapseRemoveDelta) -> DeltaRecord:
    """Encode one synapse removal."""
    return DeltaRecord(
        DeltaType.SYNAPSE_REMOVE,
        tick,
        _SYNAPSE_REMOVE_STRUCT.pack(value.source_id, value.target_id),
    )


def decode_synapse_remove(payload: bytes) -> SynapseRemoveDelta:
    """Decode one synapse removal."""
    if len(payload) != _SYNAPSE_REMOVE_STRUCT.size:
        raise ValueError("invalid SYNAPSE_REMOVE payload size")
    source_id, target_id = _SYNAPSE_REMOVE_STRUCT.unpack(payload)
    return SynapseRemoveDelta(int(source_id), int(target_id))


def encode_neuron_remove(tick: int, value: NeuronRemoveDelta) -> DeltaRecord:
    """Encode one neuron removal."""
    return DeltaRecord(
        DeltaType.NEURON_REMOVE,
        tick,
        _NEURON_REMOVE_STRUCT.pack(value.neuron_id),
    )


def decode_neuron_remove(payload: bytes) -> NeuronRemoveDelta:
    """Decode one neuron removal."""
    if len(payload) != _NEURON_REMOVE_STRUCT.size:
        raise ValueError("invalid NEURON_REMOVE payload size")
    (neuron_id,) = _NEURON_REMOVE_STRUCT.unpack(payload)
    return NeuronRemoveDelta(int(neuron_id))


def encode_neuron_add(tick: int, value: NeuronAddDelta) -> DeltaRecord:
    """Encode a complete restart-capable neuron addition."""
    optical = encode_optical_record(value.neuron_id, value.tick, value.optical)
    core = _NEURON_ADD_CORE_STRUCT.pack(
        value.a,
        value.b,
        value.c,
        value.d,
        value.spike_cost,
        value.spike_counter,
        value.last_spike_tick,
    )
    return DeltaRecord(DeltaType.NEURON_ADD, tick, optical + core)


def decode_neuron_add(payload: bytes) -> NeuronAddDelta:
    """Decode a complete restart-capable neuron addition."""
    expected = OPTICAL_RECORD_SIZE + _NEURON_ADD_CORE_STRUCT.size
    if len(payload) != expected:
        raise ValueError("invalid NEURON_ADD payload size")
    neuron_id, tick, optical = decode_optical_record(payload[:OPTICAL_RECORD_SIZE])
    core = _NEURON_ADD_CORE_STRUCT.unpack(payload[OPTICAL_RECORD_SIZE:])
    return NeuronAddDelta(
        neuron_id=int(neuron_id),
        tick=int(tick),
        optical=optical,
        a=float(core[0]),
        b=float(core[1]),
        c=float(core[2]),
        d=float(core[3]),
        spike_cost=float(core[4]),
        spike_counter=int(core[5]),
        last_spike_tick=int(core[6]),
    )


def encode_spike_event(tick: int, value: SpikeEventDelta) -> DeltaRecord:
    """Encode one observed spike event."""
    return DeltaRecord(
        DeltaType.SPIKE_EVENT,
        tick,
        _SPIKE_EVENT_STRUCT.pack(value.neuron_id),
    )


def decode_spike_event(payload: bytes) -> SpikeEventDelta:
    """Decode one spike-event payload."""
    if len(payload) != _SPIKE_EVENT_STRUCT.size:
        raise ValueError("invalid SPIKE_EVENT payload size")
    (neuron_id,) = _SPIKE_EVENT_STRUCT.unpack(payload)
    return SpikeEventDelta(int(neuron_id))


def neuron_add_from_record(record: B5DNeuronRecord) -> NeuronAddDelta:
    """Create a topology-add delta from a restart-capable snapshot record."""
    a = record.a
    b = record.b
    c = record.c
    d = record.d
    spike_cost = record.spike_cost
    spike_counter = record.spike_counter
    last_spike_tick = record.last_spike_tick
    if (
        a is None
        or b is None
        or c is None
        or d is None
        or spike_cost is None
        or spike_counter is None
        or last_spike_tick is None
    ):
        raise ValueError("neuron add requires a restart-capable record")
    return NeuronAddDelta(
        neuron_id=record.neuron_id,
        tick=record.tick,
        optical=record.optical,
        a=a,
        b=b,
        c=c,
        d=d,
        spike_cost=spike_cost,
        spike_counter=spike_counter,
        last_spike_tick=last_spike_tick,
    )


def synapse_add_from_record(record: B5DSynapseRecord) -> SynapseAddDelta:
    """Create a topology-add delta from a snapshot synapse record."""
    return SynapseAddDelta(
        source_id=record.source_id,
        target_id=record.target_id,
        weight=record.weight,
        eligibility=record.eligibility,
        delay=record.delay,
        last_pre_spike=record.last_pre_spike,
    )
