"""Persistent storage primitives for Brain-5D."""

from .b5d import (
    ALIGNMENT,
    B5DFormatError,
    B5DHeader,
    B5DNeuronRecord,
    B5DReader,
    B5DSnapshotWriter,
    B5DSynapseRecord,
    BYTE_ORDER,
    FORMAT_VERSION,
    HEADER_SIZE,
    MAX_METADATA_SIZE,
    RESTARTABLE_NEURON_RECORD_SIZE,
    SYNAPSE_RECORD_SIZE,
    assert_format_invariants,
)
from .optical_codec import (
    RECORD_SIZE,
    SPECTRAL_BINS,
    OpticalPointState,
    decode_optical_record,
    encode_optical_record,
    state_from_neuron,
)

__all__ = [
    "ALIGNMENT",
    "B5DFormatError",
    "B5DHeader",
    "B5DNeuronRecord",
    "B5DReader",
    "B5DSnapshotWriter",
    "B5DSynapseRecord",
    "BYTE_ORDER",
    "FORMAT_VERSION",
    "HEADER_SIZE",
    "MAX_METADATA_SIZE",
    "RECORD_SIZE",
    "RESTARTABLE_NEURON_RECORD_SIZE",
    "SPECTRAL_BINS",
    "SYNAPSE_RECORD_SIZE",
    "OpticalPointState",
    "assert_format_invariants",
    "decode_optical_record",
    "encode_optical_record",
    "state_from_neuron",
]
