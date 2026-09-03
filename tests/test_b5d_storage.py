"""Robustness and round-trip tests for the frozen `.b5d` V1 snapshot format."""

from __future__ import annotations

import os
import random
import struct
import time
from dataclasses import dataclass
from pathlib import Path

import pytest

from src.storage.b5d import (
    ALIGNMENT,
    BYTE_ORDER,
    ENDIANNESS,
    FORMAT_VERSION,
    HEADER_SIZE,
    MAGIC,
    MAX_METADATA_SIZE,
    OPTICAL_RECORD_SIZE,
    RESTARTABLE_NEURON_RECORD_SIZE,
    SYNAPSE_RECORD_SIZE,
    B5DFormatError,
    B5DReader,
    B5DSnapshotWriter,
    assert_format_invariants,
)
from src.storage.layout import StorageLayout, validate_scope_transition
from src.storage.optical_codec import OpticalPointState


def test_storage_layout_separates_controlled_roots(tmp_path: Path) -> None:
    layout = StorageLayout(tmp_path)
    assert layout.operator_state == tmp_path / "operator" / "state.b5d"
    assert layout.experiment("EXP-0001") == tmp_path / "experiment" / "EXP-0001"
    assert layout.experiment_state("EXP-0001") == tmp_path / "experiment" / "EXP-0001" / "state"
    assert layout.experiment_data("EXP-0001") == tmp_path / "experiment" / "EXP-0001" / "DATA"
    assert layout.experiment_evidence("EXP-0001") == tmp_path / "experiment" / "EXP-0001" / "EVID"
    layout.ensure_directories()
    assert layout.operator_journal.is_dir()
    assert layout.operator_checkpoints.is_dir()
    assert layout.dev_disposable.is_dir()
    with pytest.raises(ValueError, match="safe EXP"):
        layout.experiment("../outside")


def test_storage_scope_transitions_are_fail_closed() -> None:
    validate_scope_transition("OPERATOR", "EXPERIMENT", "snapshot")
    validate_scope_transition("OPERATOR", "EXPERIMENT", "fork")
    with pytest.raises(ValueError, match="DEV to OPERATOR"):
        validate_scope_transition("DEV", "OPERATOR", "copy")
    with pytest.raises(ValueError, match="merge"):
        validate_scope_transition("EXPERIMENT", "OPERATOR", "merge")
    with pytest.raises(ValueError, match="snapshot or fork"):
        validate_scope_transition("OPERATOR", "EXPERIMENT", "merge")


@dataclass(slots=True)
class FakeNeuron:
    """Typed neuron stand-in containing the state required by `.b5d` V1."""

    neuron_id: int
    a: float = 0.02
    b: float = 0.2
    c: float = -65.0
    d: float = 8.0
    v: float = -60.0
    u: float = -12.0
    energy: float = 0.8
    spike_cost: float = 0.001
    spike_counter: int = 7
    last_spike_tick: int = 42
    threshold_adaptation: float = 0.1


@dataclass(slots=True)
class FakeSynapse:
    """Typed synapse stand-in matching persisted fields."""

    target_id: int
    weight: float
    delay: int
    eligibility: float = 0.0
    last_pre_spike: int = -1


@dataclass(slots=True)
class FakeNetwork:
    """Small deterministic network used by storage tests."""

    dimensions: tuple[int, int, int, int, int]
    current_tick: int
    neurons: dict[int, FakeNeuron]
    synapses: dict[int, list[FakeSynapse]]


def _network() -> FakeNetwork:
    n10 = FakeNeuron(10)
    n20 = FakeNeuron(20, v=-55.0, spike_counter=9, last_spike_tick=50)
    return FakeNetwork(
        dimensions=(10, 10, 10, 10, 10),
        current_tick=51,
        neurons={20: n20, 10: n10},
        synapses={
            20: [],
            10: [
                FakeSynapse(
                    20,
                    weight=0.25,
                    delay=3,
                    eligibility=-0.4,
                    last_pre_spike=49,
                )
            ],
        },
    )


def _read_mutable(path: Path) -> bytearray:
    return bytearray(path.read_bytes())


def test_format_invariants_and_endianness() -> None:
    """Frozen record sizes and byte order must never drift inside V1."""
    assert_format_invariants()
    assert HEADER_SIZE == 128
    assert OPTICAL_RECORD_SIZE == 128
    assert RESTARTABLE_NEURON_RECORD_SIZE == 160
    assert SYNAPSE_RECORD_SIZE == 40
    assert ENDIANNESS == "<"
    assert BYTE_ORDER == "little"


def test_restartable_snapshot_roundtrip(tmp_path: Path) -> None:
    """Restart snapshots preserve topology and mutable neuron state."""
    path = tmp_path / "snapshot.b5d"
    header = B5DSnapshotWriter(restart_capable=True).write(
        path,
        _network(),  # type: ignore[arg-type]
        metadata={"experiment": "unit-test", "seed": 42},
        created_ns=123456789,
    )

    assert header.version == FORMAT_VERSION
    assert header.restart_capable
    assert header.neuron_record_size == RESTARTABLE_NEURON_RECORD_SIZE
    assert header.synapse_record_size == SYNAPSE_RECORD_SIZE
    assert header.neuron_count == 2
    assert header.synapse_count == 1

    with B5DReader(path) as reader:
        assert reader.metadata == {"experiment": "unit-test", "seed": 42}
        assert reader.header.snapshot_tick == 51
        assert reader.header.dimensions == (10, 10, 10, 10, 10)
        reader.validate_invariants()

        neuron = reader.get_neuron(20)
        assert neuron is not None
        assert neuron.neuron_id == 20
        assert neuron.tick == 51
        assert neuron.a == pytest.approx(0.02)  # type: ignore[reportUnknownMemberType]
        assert neuron.spike_counter == 9
        assert neuron.last_spike_tick == 50
        assert neuron.optical.membrane_v == pytest.approx(-55.0, abs=0.01)  # type: ignore[reportUnknownMemberType]

        assert [item.neuron_id for item in reader.iter_neurons()] == [10, 20]
        synapse = list(reader.iter_synapses())[0]
        assert synapse.source_id == 10
        assert synapse.target_id == 20
        assert synapse.weight == pytest.approx(0.25)  # type: ignore[reportUnknownMemberType]
        assert synapse.eligibility == pytest.approx(-0.4)  # type: ignore[reportUnknownMemberType]
        assert synapse.delay == 3
        assert synapse.last_pre_spike == 49


def test_optical_only_snapshot_is_128_bytes_per_neuron(tmp_path: Path) -> None:
    """Optical mode keeps the existing optical codec byte-for-byte."""
    path = tmp_path / "optical-only.b5d"
    header = B5DSnapshotWriter(restart_capable=False).write(path, _network())  # type: ignore[arg-type]

    assert not header.restart_capable
    assert header.neuron_record_size == OPTICAL_RECORD_SIZE
    with B5DReader(path) as reader:
        neuron = reader.get_neuron(10)
        assert neuron is not None
        assert neuron.a is None
        assert neuron.optical.energy == pytest.approx(0.8, abs=2e-5)  # type: ignore[reportUnknownMemberType]


def test_custom_optical_sidecar_is_persisted(tmp_path: Path) -> None:
    """Manipulator sidecar state can override derived optical state."""
    path = tmp_path / "sidecar.b5d"
    state = OpticalPointState(brightness=0.75, coherence=0.5)
    B5DSnapshotWriter().write(path, _network(), optical_states={10: state})  # type: ignore[arg-type]

    with B5DReader(path) as reader:
        neuron = reader.get_neuron(10)
        assert neuron is not None
        assert neuron.optical.brightness == pytest.approx(0.75, abs=2e-5)  # type: ignore[reportUnknownMemberType]
        assert neuron.optical.coherence == pytest.approx(0.5, abs=2e-5)  # type: ignore[reportUnknownMemberType]


def test_records_are_sorted_and_binary_searchable(tmp_path: Path) -> None:
    """Writer sorts neuron IDs and reader random access uses that invariant."""
    network = _network()
    network.neurons[5] = FakeNeuron(5)
    network.synapses[5] = []
    path = tmp_path / "sorted.b5d"
    B5DSnapshotWriter().write(path, network)  # type: ignore[arg-type]

    with B5DReader(path) as reader:
        assert [item.neuron_id for item in reader.iter_neurons()] == [5, 10, 20]
        assert reader.get_neuron(5) is not None
        assert reader.get_neuron(999) is None
        reader.validate_invariants()


def test_synapse_range_lookup_is_source_scoped(tmp_path: Path) -> None:
    """Fixed sorted records support O(log n + degree) source lookup."""
    network = _network()
    network.neurons[30] = FakeNeuron(30)
    network.synapses[20] = [FakeSynapse(30, 0.7, 2)]
    network.synapses[30] = []
    path = tmp_path / "synapses.b5d"
    B5DSnapshotWriter().write(path, network)  # type: ignore[arg-type]

    with B5DReader(path) as reader:
        ten = list(reader.get_synapses(10))
        twenty = list(reader.get_synapses(20))
        missing = list(reader.get_synapses(999))
    assert [(item.source_id, item.target_id) for item in ten] == [(10, 20)]
    assert [(item.source_id, item.target_id) for item in twenty] == [(20, 30)]
    assert missing == []


def test_duplicate_neuron_ids_in_corrupt_file_are_rejected(tmp_path: Path) -> None:
    """Full validation detects duplicate IDs even if a file was externally altered."""
    path = tmp_path / "duplicate.b5d"
    B5DSnapshotWriter().write(path, _network())  # type: ignore[arg-type]
    with B5DReader(path) as reader:
        second_offset = reader.header.neuron_offset + reader.header.neuron_record_size
        first_id = struct.pack("<Q", 10)
    raw = _read_mutable(path)
    raw[second_offset : second_offset + 8] = first_id
    path.write_bytes(raw)

    with B5DReader(path) as reader:
        with pytest.raises(B5DFormatError, match="strictly increasing"):
            reader.validate_invariants()


def test_writer_rejects_dangling_synapse_target(tmp_path: Path) -> None:
    """Snapshots cannot persist topology that points to missing neurons."""
    network = _network()
    network.synapses[10].append(FakeSynapse(999, 0.2, 1))
    with pytest.raises(ValueError, match="target does not exist"):
        B5DSnapshotWriter().write(tmp_path / "dangling.b5d", network)  # type: ignore[arg-type]


def test_metadata_limit_and_invalid_json_are_rejected(tmp_path: Path) -> None:
    """Metadata is bounded, UTF-8 JSON and object-shaped."""
    oversized = {"payload": "x" * MAX_METADATA_SIZE}
    with pytest.raises(ValueError, match="metadata exceeds V1 limit"):
        B5DSnapshotWriter().write(
            tmp_path / "too-large.b5d", _network(), metadata=oversized  # type: ignore[arg-type]
        )

    path = tmp_path / "invalid-json.b5d"
    B5DSnapshotWriter().write(path, _network(), metadata={"a": 1})  # type: ignore[arg-type]
    with B5DReader(path) as reader:
        start = reader.header.metadata_offset
        size = reader.header.metadata_size
    raw = _read_mutable(path)
    raw[start : start + size] = b"!" * size
    path.write_bytes(raw)
    with pytest.raises(B5DFormatError, match="invalid metadata"):
        B5DReader(path)


def test_invalid_magic_version_and_short_header_are_rejected(tmp_path: Path) -> None:
    """Reader fails fast for foreign, future-major and truncated files."""
    short = tmp_path / "short.b5d"
    short.write_bytes(MAGIC)
    with pytest.raises(B5DFormatError, match="file too small"):
        B5DReader(short)

    bad_magic = tmp_path / "bad-magic.b5d"
    B5DSnapshotWriter().write(bad_magic, _network())  # type: ignore[arg-type]
    raw = _read_mutable(bad_magic)
    raw[:8] = b"INVALID!"
    bad_magic.write_bytes(raw)
    with pytest.raises(B5DFormatError, match="invalid .b5d magic"):
        B5DReader(bad_magic)

    bad_version = tmp_path / "bad-version.b5d"
    B5DSnapshotWriter().write(bad_version, _network())  # type: ignore[arg-type]
    raw = _read_mutable(bad_version)
    struct.pack_into("<H", raw, 8, FORMAT_VERSION + 1)
    bad_version.write_bytes(raw)
    with pytest.raises(B5DFormatError, match="unsupported .b5d format version"):
        B5DReader(bad_version)


def test_truncated_neuron_and_synapse_sections_are_rejected(tmp_path: Path) -> None:
    """Header counts cannot silently read beyond a truncated file."""
    neuron_path = tmp_path / "truncated-neuron.b5d"
    B5DSnapshotWriter().write(neuron_path, _network())  # type: ignore[arg-type]
    neuron_path.write_bytes(neuron_path.read_bytes()[:-20])
    with pytest.raises(B5DFormatError, match="file-size mismatch"):
        B5DReader(neuron_path)

    synapse_path = tmp_path / "truncated-synapse.b5d"
    B5DSnapshotWriter().write(synapse_path, _network())  # type: ignore[arg-type]
    synapse_path.write_bytes(synapse_path.read_bytes()[:-1])
    with pytest.raises(B5DFormatError, match="file-size mismatch"):
        B5DReader(synapse_path)


def test_non_zero_alignment_padding_is_rejected_by_full_scan(tmp_path: Path) -> None:
    """Reserved alignment gaps stay zero in the frozen format."""
    path = tmp_path / "padding.b5d"
    B5DSnapshotWriter().write(path, _network(), metadata={"x": 1})  # type: ignore[arg-type]
    with B5DReader(path) as reader:
        padding_start = reader.header.metadata_offset + reader.header.metadata_size
        assert padding_start < reader.header.neuron_offset
    raw = _read_mutable(path)
    raw[padding_start] = 0x7F
    path.write_bytes(raw)
    with B5DReader(path) as reader:
        with pytest.raises(B5DFormatError, match="alignment padding"):
            reader.validate_invariants()


def test_context_manager_and_close_are_resource_safe(tmp_path: Path) -> None:
    """Reader handles close deterministically and close() is idempotent."""
    path = tmp_path / "resources.b5d"
    B5DSnapshotWriter().write(path, _network())  # type: ignore[arg-type]
    reader = B5DReader(path)
    assert not reader.closed
    with reader:
        assert reader.neuron_count == 2
        assert not reader.closed
    assert reader.closed
    reader.close()
    assert reader.closed
    path.unlink()


def test_fixed_timestamp_produces_byte_deterministic_snapshot(tmp_path: Path) -> None:
    """Identical state and timestamp produce identical V1 bytes."""
    first = tmp_path / "first.b5d"
    second = tmp_path / "second.b5d"
    writer = B5DSnapshotWriter()
    kwargs = {"metadata": {"a": 1}, "created_ns": 123456789}
    writer.write(first, _network(), **kwargs)  # type: ignore[arg-type]
    writer.write(second, _network(), **kwargs)  # type: ignore[arg-type]
    assert first.read_bytes() == second.read_bytes()


def test_offsets_are_aligned_and_size_is_exact(tmp_path: Path) -> None:
    """Section offsets follow the 64-byte alignment contract."""
    path = tmp_path / "alignment.b5d"
    header = B5DSnapshotWriter().write(path, _network(), metadata={"abc": "def"})  # type: ignore[arg-type]
    assert header.neuron_offset % ALIGNMENT == 0
    assert header.synapse_offset % ALIGNMENT == 0
    assert header.file_size == path.stat().st_size


@pytest.mark.skipif(
    os.environ.get("BRAIN5D_RUN_LARGE_STORAGE_TEST") != "1",
    reason="set BRAIN5D_RUN_LARGE_STORAGE_TEST=1 for the 50k storage smoke test",
)
def test_large_storage_50k_neurons(tmp_path: Path) -> None:
    """Exercise mmap/random access on 50k neurons without flaky time limits."""
    rng = random.Random(42)
    count = 50_000
    neurons = {
        neuron_id: FakeNeuron(
            neuron_id,
            v=-70.0 + rng.random() * 20.0,
            energy=0.5 + rng.random() * 0.5,
        )
        for neuron_id in range(count)
    }
    synapses: dict[int, list[FakeSynapse]] = {neuron_id: [] for neuron_id in neurons}
    for source_id in range(0, count - 5, 10):
        synapses[source_id] = [
            FakeSynapse(source_id + offset + 1, 0.1 * (offset + 1), offset + 1)
            for offset in range(5)
        ]
    network = FakeNetwork(
        dimensions=(10, 10, 10, 10, 10),
        current_tick=100,
        neurons=neurons,
        synapses=synapses,
    )
    path = tmp_path / "large.b5d"

    started = time.perf_counter()
    B5DSnapshotWriter(restart_capable=False).write(path, network, created_ns=1)  # type: ignore[arg-type]
    write_seconds = time.perf_counter() - started

    started = time.perf_counter()
    with B5DReader(path) as reader:
        assert reader.neuron_count == count
        for neuron_id in (0, 17, 999, 25_000, 49_999):
            record = reader.get_neuron(neuron_id)
            assert record is not None
            assert record.neuron_id == neuron_id
        assert sum(1 for _ in reader.iter_neurons()) == count
        reader.validate_invariants()
    read_seconds = time.perf_counter() - started

    print(
        f"50k .b5d smoke: size={path.stat().st_size / (1024 * 1024):.2f} MiB, "
        f"write={write_seconds:.3f}s, read+validate={read_seconds:.3f}s"
    )
