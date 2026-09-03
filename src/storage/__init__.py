"""Persistent storage primitives for Brain-5D."""

from .b5d import (
    ALIGNMENT,
    BYTE_ORDER,
    FORMAT_VERSION,
    HEADER_SIZE,
    MAX_METADATA_SIZE,
    RESTARTABLE_NEURON_RECORD_SIZE,
    SYNAPSE_RECORD_SIZE,
    B5DFormatError,
    B5DHeader,
    B5DNeuronRecord,
    B5DReader,
    B5DSnapshotWriter,
    B5DSynapseRecord,
    assert_format_invariants,
)
from .crc import compute_crc32, verify_crc32
from .delta_codec import (
    NeuronAddDelta,
    NeuronRemoveDelta,
    NeuronStateDelta,
    SpikeEventDelta,
    SynapseAddDelta,
    SynapseRemoveDelta,
    SynapseWeightDelta,
)
from .delta_journal import (
    DeltaJournal,
    DeltaRecord,
    DeltaType,
    JournalCorruptionError,
    JournalError,
    UncommittedTailError,
    assert_journal_format_invariants,
)
from .layout import StorageLayout
from .lazy_view import B5DLazyProjector, StorageHeatmap, StorageHeatmapKind
from .optical_codec import (
    RECORD_SIZE,
    SPECTRAL_BINS,
    NeuronOpticalLike,
    OpticalPointState,
    decode_optical_record,
    encode_optical_record,
    state_from_neuron,
)
from .recovery import RecoveryInspection, RecoveryManager, RecoveryResult
from .runtime import StorageRuntimeConfig, StorageRuntimeStats, StorageSession
from .structural_journal import (
    NeuronStructuralSnapshot,
    StructuralChangeKind,
    StructuralChangeRecord,
    StructuralJournal,
    StructuralJournalError,
    StructuralJournalScan,
    StructuralSnapshotLifecycle,
    SynapseSnapshot,
)

__all__ = [
    "ALIGNMENT",
    "BYTE_ORDER",
    "FORMAT_VERSION",
    "HEADER_SIZE",
    "MAX_METADATA_SIZE",
    "RECORD_SIZE",
    "RESTARTABLE_NEURON_RECORD_SIZE",
    "SPECTRAL_BINS",
    "SYNAPSE_RECORD_SIZE",
    "B5DFormatError",
    "B5DHeader",
    "B5DLazyProjector",
    "B5DNeuronRecord",
    "B5DReader",
    "B5DSnapshotWriter",
    "B5DSynapseRecord",
    "DeltaJournal",
    "DeltaRecord",
    "DeltaType",
    "JournalCorruptionError",
    "JournalError",
    "NeuronAddDelta",
    "NeuronOpticalLike",
    "NeuronRemoveDelta",
    "NeuronStateDelta",
    "NeuronStructuralSnapshot",
    "OpticalPointState",
    "RecoveryInspection",
    "RecoveryManager",
    "RecoveryResult",
    "SpikeEventDelta",
    "StorageHeatmap",
    "StorageHeatmapKind",
    "StorageLayout",
    "StorageRuntimeConfig",
    "StorageRuntimeStats",
    "StorageSession",
    "StructuralChangeKind",
    "StructuralChangeRecord",
    "StructuralJournal",
    "StructuralJournalError",
    "StructuralJournalScan",
    "StructuralSnapshotLifecycle",
    "SynapseAddDelta",
    "SynapseRemoveDelta",
    "SynapseSnapshot",
    "SynapseWeightDelta",
    "UncommittedTailError",
    "assert_format_invariants",
    "assert_journal_format_invariants",
    "compute_crc32",
    "decode_optical_record",
    "encode_optical_record",
    "state_from_neuron",
    "verify_crc32",
]

from .async_runtime import (
    AsyncStorageConfig,
    AsyncStorageSession,
    StorageTelemetrySnapshot,
)
from .checkpoint import (
    RuntimeCheckpoint,
    capture_runtime_checkpoint,
    read_runtime_checkpoint,
    write_runtime_checkpoint,
)
from .compaction import (
    CompactionResult,
    StorageCompactor,
    StorageGeneration,
    StorageManifest,
)
from .core_restore import RestoredNeuralNetwork, restore_network

__all__ += [
    "AsyncStorageConfig",
    "AsyncStorageSession",
    "CompactionResult",
    "RestoredNeuralNetwork",
    "RuntimeCheckpoint",
    "StorageCompactor",
    "StorageGeneration",
    "StorageManifest",
    "StorageTelemetrySnapshot",
    "capture_runtime_checkpoint",
    "read_runtime_checkpoint",
    "restore_network",
    "write_runtime_checkpoint",
]
