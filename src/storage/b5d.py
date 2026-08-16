"""Robust Brain-5D binary snapshot container (``.b5d``), format V1.

Format V1 is a deterministic, little-endian, memory-mappable snapshot format.
It deliberately contains only immutable snapshot sections. Delta journaling,
checksums and crash-recovery markers belong to the V2 journal layer and do not
change this V1 snapshot contract.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
import mmap
from pathlib import Path
import struct
import time
from typing import Iterator, Mapping, Protocol, Sequence, TypeAlias, runtime_checkable

from .optical_codec import (
    RECORD_SIZE as OPTICAL_RECORD_SIZE,
    OpticalPointState,
    decode_optical_record,
    encode_optical_record,
    state_from_neuron,
)

ENDIANNESS = "<"
BYTE_ORDER = "little"
MAGIC = b"BRAIN5D\x00"
FORMAT_VERSION = 1
HEADER_SIZE = 128
CORE_EXTENSION_SIZE = 32
RESTARTABLE_NEURON_RECORD_SIZE = OPTICAL_RECORD_SIZE + CORE_EXTENSION_SIZE
SYNAPSE_RECORD_SIZE = 40
ALIGNMENT = 64
MAX_METADATA_SIZE = 64 * 1024
MAX_UINT64 = (1 << 64) - 1

FLAG_RESTART_CAPABLE = 0x0001
_KNOWN_FLAGS = FLAG_RESTART_CAPABLE

# 128 bytes exactly:
# magic, version, header_size, flags,
# created_ns, snapshot_tick, neuron_count, synapse_count,
# neuron_record_size, synapse_record_size,
# five dimensions, alignment padding,
# metadata_offset, metadata_size, neuron_offset, synapse_offset, file_size,
# reserved padding.
_HEADER_STRUCT = struct.Struct("<8sHHIQQQQII5H6xQQQQQ16x")
_CORE_EXTENSION_STRUCT = struct.Struct("<5fIq")
# source_id, target_id, weight, eligibility, delay, padding,
# last_pre_spike, reserved padding.
_SYNAPSE_STRUCT = struct.Struct("<QQffH2xq4x")
_NEURON_ID_STRUCT = struct.Struct("<Q")

JSONScalar: TypeAlias = str | int | float | bool | None
JSONValue: TypeAlias = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]
JSONMapping: TypeAlias = Mapping[str, JSONValue]


class B5DFormatError(ValueError):
    """Raised when a `.b5d` file violates the frozen V1 format contract."""


@runtime_checkable
class NeuronSnapshotLike(Protocol):
    """Minimum neuron surface required by the V1 snapshot writer."""

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


@runtime_checkable
class SynapseSnapshotLike(Protocol):
    """Minimum synapse surface required by the V1 snapshot writer."""

    target_id: int
    weight: float
    delay: int
    eligibility: float
    last_pre_spike: int


class NetworkSnapshotLike(Protocol):
    """Network surface consumed by :class:`B5DSnapshotWriter`."""

    dimensions: tuple[int, int, int, int, int]
    current_tick: int
    neurons: Mapping[int, NeuronSnapshotLike]
    synapses: Mapping[int, Sequence[SynapseSnapshotLike]]


@dataclass(frozen=True, slots=True)
class B5DHeader:
    """Decoded immutable `.b5d` file-header information."""

    version: int
    flags: int
    created_ns: int
    snapshot_tick: int
    neuron_count: int
    synapse_count: int
    neuron_record_size: int
    synapse_record_size: int
    dimensions: tuple[int, int, int, int, int]
    metadata_offset: int
    metadata_size: int
    neuron_offset: int
    synapse_offset: int
    file_size: int

    @property
    def restart_capable(self) -> bool:
        """Return whether neuron records contain the core-state extension."""
        return bool(self.flags & FLAG_RESTART_CAPABLE)


@dataclass(frozen=True, slots=True)
class B5DNeuronRecord:
    """Decoded neuron snapshot from one fixed-size `.b5d` record."""

    neuron_id: int
    tick: int
    optical: OpticalPointState
    a: float | None = None
    b: float | None = None
    c: float | None = None
    d: float | None = None
    spike_cost: float | None = None
    spike_counter: int | None = None
    last_spike_tick: int | None = None


@dataclass(frozen=True, slots=True)
class B5DSynapseRecord:
    """Decoded fixed-size synapse snapshot."""

    source_id: int
    target_id: int
    weight: float
    eligibility: float
    delay: int
    last_pre_spike: int


def assert_format_invariants() -> None:
    """Raise if compile-time record sizes no longer match frozen V1 sizes."""
    expected = {
        "header": (HEADER_SIZE, _HEADER_STRUCT.size),
        "optical": (128, OPTICAL_RECORD_SIZE),
        "restart": (160, RESTARTABLE_NEURON_RECORD_SIZE),
        "core_extension": (32, _CORE_EXTENSION_STRUCT.size),
        "synapse": (40, _SYNAPSE_STRUCT.size),
    }
    for name, (declared, actual) in expected.items():
        if declared != actual:
            raise RuntimeError(
                f".b5d V1 invariant broken for {name}: "
                f"declared={declared}, actual={actual}"
            )
    if ENDIANNESS != "<" or BYTE_ORDER != "little":
        raise RuntimeError(".b5d V1 must remain little-endian")


def _align(value: int, alignment: int = ALIGNMENT) -> int:
    """Round *value* up to the next alignment boundary."""
    if value < 0:
        raise ValueError("value must be non-negative")
    if alignment <= 0:
        raise ValueError("alignment must be positive")
    return ((value + alignment - 1) // alignment) * alignment


def _validate_uint64(value: int, label: str) -> int:
    """Return *value* if it is representable as an unsigned 64-bit integer."""
    if not 0 <= value <= MAX_UINT64:
        raise ValueError(f"{label} must fit uint64: {value}")
    return value


def _validate_finite(value: float, label: str) -> float:
    """Return *value* when it is finite and safe for persistent state."""
    if not math.isfinite(value):
        raise ValueError(f"{label} must be finite: {value}")
    return value


def _network_dimensions(network: NetworkSnapshotLike) -> tuple[int, int, int, int, int]:
    dims = tuple(int(value) for value in network.dimensions)
    if len(dims) != 5:
        raise ValueError("network dimensions must contain exactly five values")
    if any(value < 1 or value > 65535 for value in dims):
        raise ValueError("each dimension must be in range 1..65535")
    return (dims[0], dims[1], dims[2], dims[3], dims[4])


def _encode_core_extension(neuron: NeuronSnapshotLike) -> bytes:
    spike_counter = int(neuron.spike_counter)
    if not 0 <= spike_counter <= 0xFFFFFFFF:
        raise ValueError("spike_counter must fit uint32")
    return _CORE_EXTENSION_STRUCT.pack(
        _validate_finite(float(neuron.a), "neuron.a"),
        _validate_finite(float(neuron.b), "neuron.b"),
        _validate_finite(float(neuron.c), "neuron.c"),
        _validate_finite(float(neuron.d), "neuron.d"),
        _validate_finite(float(neuron.spike_cost), "neuron.spike_cost"),
        spike_counter,
        int(neuron.last_spike_tick),
    )


def _decode_core_extension(
    data: bytes,
) -> tuple[float, float, float, float, float, int, int]:
    if len(data) != CORE_EXTENSION_SIZE:
        raise B5DFormatError("truncated core-extension record")
    a, b, c, d, spike_cost, spike_counter, last_spike_tick = (
        _CORE_EXTENSION_STRUCT.unpack(data)
    )
    return (
        float(a),
        float(b),
        float(c),
        float(d),
        float(spike_cost),
        int(spike_counter),
        int(last_spike_tick),
    )


def _encode_synapse(source_id: int, synapse: SynapseSnapshotLike) -> bytes:
    source = _validate_uint64(int(source_id), "source_id")
    target = _validate_uint64(int(synapse.target_id), "target_id")
    delay = int(synapse.delay)
    if not 1 <= delay <= 65535:
        raise ValueError("synapse delay must fit uint16 and be >= 1")
    return _SYNAPSE_STRUCT.pack(
        source,
        target,
        _validate_finite(float(synapse.weight), "synapse.weight"),
        _validate_finite(float(synapse.eligibility), "synapse.eligibility"),
        delay,
        int(synapse.last_pre_spike),
    )


def _decode_synapse(data: bytes) -> B5DSynapseRecord:
    if len(data) != SYNAPSE_RECORD_SIZE:
        raise B5DFormatError("truncated synapse record")
    source_id, target_id, weight, eligibility, delay, last_pre_spike = (
        _SYNAPSE_STRUCT.unpack(data)
    )
    return B5DSynapseRecord(
        source_id=int(source_id),
        target_id=int(target_id),
        weight=float(weight),
        eligibility=float(eligibility),
        delay=int(delay),
        last_pre_spike=int(last_pre_spike),
    )


def _validate_json_value(value: object) -> JSONValue:
    """Validate JSON-decoded data and return a strictly typed JSON value."""
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, list):
        return [_validate_json_value(item) for item in value]
    if isinstance(value, dict):
        result: dict[str, JSONValue] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise B5DFormatError("metadata object keys must be strings")
            result[key] = _validate_json_value(item)
        return result
    raise B5DFormatError(f"unsupported metadata value type: {type(value).__name__}")


def _encode_metadata(metadata: JSONMapping | None) -> bytes:
    """Serialize metadata deterministically and enforce the V1 size limit."""
    payload = dict(metadata or {})
    raw = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    if len(raw) > MAX_METADATA_SIZE:
        raise ValueError(
            f"metadata exceeds V1 limit: {len(raw)} > {MAX_METADATA_SIZE} bytes"
        )
    return raw


def _decode_metadata(data: bytes) -> dict[str, JSONValue]:
    """Decode UTF-8 JSON metadata and enforce an object at the top level."""
    try:
        decoded: object = json.loads(data.decode("utf-8")) if data else {}
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise B5DFormatError(f"invalid metadata: {exc}") from exc
    value = _validate_json_value(decoded)
    if not isinstance(value, dict):
        raise B5DFormatError(".b5d metadata must be a JSON object")
    return value


def _build_header_bytes(header: B5DHeader) -> bytes:
    """Pack one exact 128-byte V1 header."""
    return _HEADER_STRUCT.pack(
        MAGIC,
        header.version,
        HEADER_SIZE,
        header.flags,
        header.created_ns,
        header.snapshot_tick,
        header.neuron_count,
        header.synapse_count,
        header.neuron_record_size,
        header.synapse_record_size,
        *header.dimensions,
        header.metadata_offset,
        header.metadata_size,
        header.neuron_offset,
        header.synapse_offset,
        header.file_size,
    )


def _parse_header_bytes(data: bytes) -> B5DHeader:
    """Decode and structurally validate one V1 header."""
    if len(data) != HEADER_SIZE:
        raise B5DFormatError(f"file too small for {HEADER_SIZE}-byte .b5d header")
    values = _HEADER_STRUCT.unpack(data)
    magic = values[0]
    version = int(values[1])
    header_size = int(values[2])
    flags = int(values[3])
    if magic != MAGIC:
        raise B5DFormatError("invalid .b5d magic")
    if any(data[66:72]) or any(data[112:128]):
        raise B5DFormatError("reserved header bytes must be zero")
    if version != FORMAT_VERSION:
        raise B5DFormatError(f"unsupported .b5d format version: {version}")
    if header_size != HEADER_SIZE:
        raise B5DFormatError(f"unsupported .b5d header size: {header_size}")
    if flags & ~_KNOWN_FLAGS:
        raise B5DFormatError(f"unknown .b5d V1 flags: 0x{flags:08x}")

    created_ns = int(values[4])
    snapshot_tick = int(values[5])
    neuron_count = int(values[6])
    synapse_count = int(values[7])
    neuron_record_size = int(values[8])
    synapse_record_size = int(values[9])
    dimensions = (
        int(values[10]),
        int(values[11]),
        int(values[12]),
        int(values[13]),
        int(values[14]),
    )
    metadata_offset = int(values[15])
    metadata_size = int(values[16])
    neuron_offset = int(values[17])
    synapse_offset = int(values[18])
    file_size = int(values[19])

    expected_neuron_size = (
        RESTARTABLE_NEURON_RECORD_SIZE
        if flags & FLAG_RESTART_CAPABLE
        else OPTICAL_RECORD_SIZE
    )
    if neuron_record_size != expected_neuron_size:
        raise B5DFormatError(
            "neuron record size is inconsistent with restart-capable flag"
        )
    if synapse_record_size != SYNAPSE_RECORD_SIZE:
        raise B5DFormatError(f"unsupported synapse record size: {synapse_record_size}")
    if metadata_size > MAX_METADATA_SIZE:
        raise B5DFormatError(
            f"metadata exceeds V1 limit: {metadata_size} > {MAX_METADATA_SIZE} bytes"
        )
    if any(dimension < 1 for dimension in dimensions):
        raise B5DFormatError("all five dimensions must be positive")

    return B5DHeader(
        version=version,
        flags=flags,
        created_ns=created_ns,
        snapshot_tick=snapshot_tick,
        neuron_count=neuron_count,
        synapse_count=synapse_count,
        neuron_record_size=neuron_record_size,
        synapse_record_size=synapse_record_size,
        dimensions=dimensions,
        metadata_offset=metadata_offset,
        metadata_size=metadata_size,
        neuron_offset=neuron_offset,
        synapse_offset=synapse_offset,
        file_size=file_size,
    )


class B5DSnapshotWriter:
    """Write deterministic Brain-5D V1 snapshot containers."""

    def __init__(self, *, restart_capable: bool = True) -> None:
        self.restart_capable = bool(restart_capable)
        assert_format_invariants()

    def estimate_size(
        self,
        neuron_count: int,
        synapse_count: int,
        *,
        metadata_size: int = 0,
    ) -> int:
        """Estimate final file size for the supplied record counts."""
        if neuron_count < 0 or synapse_count < 0 or metadata_size < 0:
            raise ValueError("record counts and metadata size must be non-negative")
        if metadata_size > MAX_METADATA_SIZE:
            raise ValueError("metadata_size exceeds the V1 limit")
        neuron_record_size = (
            RESTARTABLE_NEURON_RECORD_SIZE
            if self.restart_capable
            else OPTICAL_RECORD_SIZE
        )
        neuron_offset = _align(HEADER_SIZE + metadata_size)
        synapse_offset = _align(neuron_offset + neuron_count * neuron_record_size)
        return synapse_offset + synapse_count * SYNAPSE_RECORD_SIZE

    def write(
        self,
        path: str | Path,
        network: NetworkSnapshotLike,
        *,
        optical_states: Mapping[int, OpticalPointState] | None = None,
        metadata: JSONMapping | None = None,
        created_ns: int | None = None,
    ) -> B5DHeader:
        """Write *network* to *path* and return the emitted V1 header."""
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)

        neuron_ids = sorted(int(neuron_id) for neuron_id in network.neurons)
        _validate_uint64(len(neuron_ids), "neuron_count")
        if len(neuron_ids) != len(set(neuron_ids)):
            raise ValueError("duplicate neuron IDs are not permitted")
        for neuron_id in neuron_ids:
            _validate_uint64(neuron_id, "neuron_id")

        neuron_id_set = set(neuron_ids)
        synapse_pairs: list[tuple[int, SynapseSnapshotLike]] = []
        for source_id in sorted(int(value) for value in network.synapses):
            if source_id not in neuron_id_set:
                raise ValueError(f"synapse source does not exist: {source_id}")
            outgoing = sorted(
                network.synapses[source_id], key=lambda item: int(item.target_id)
            )
            for synapse in outgoing:
                if int(synapse.target_id) not in neuron_id_set:
                    raise ValueError(
                        f"synapse target does not exist: {int(synapse.target_id)}"
                    )
                synapse_pairs.append((source_id, synapse))

        _validate_uint64(len(synapse_pairs), "synapse_count")
        dimensions = _network_dimensions(network)
        tick = _validate_uint64(int(network.current_tick), "current_tick")
        metadata_bytes = _encode_metadata(metadata)
        metadata_offset = HEADER_SIZE
        neuron_offset = _align(metadata_offset + len(metadata_bytes))
        neuron_record_size = (
            RESTARTABLE_NEURON_RECORD_SIZE
            if self.restart_capable
            else OPTICAL_RECORD_SIZE
        )
        synapse_offset = _align(neuron_offset + len(neuron_ids) * neuron_record_size)
        file_size = self.estimate_size(
            len(neuron_ids),
            len(synapse_pairs),
            metadata_size=len(metadata_bytes),
        )
        flags = FLAG_RESTART_CAPABLE if self.restart_capable else 0
        timestamp = time.time_ns() if created_ns is None else int(created_ns)
        _validate_uint64(timestamp, "created_ns")

        header = B5DHeader(
            version=FORMAT_VERSION,
            flags=flags,
            created_ns=timestamp,
            snapshot_tick=tick,
            neuron_count=len(neuron_ids),
            synapse_count=len(synapse_pairs),
            neuron_record_size=neuron_record_size,
            synapse_record_size=SYNAPSE_RECORD_SIZE,
            dimensions=dimensions,
            metadata_offset=metadata_offset,
            metadata_size=len(metadata_bytes),
            neuron_offset=neuron_offset,
            synapse_offset=synapse_offset,
            file_size=file_size,
        )

        with destination.open("wb") as handle:
            handle.write(_build_header_bytes(header))
            handle.write(metadata_bytes)
            handle.write(b"\x00" * (neuron_offset - handle.tell()))
            for neuron_id in neuron_ids:
                neuron = network.neurons[neuron_id]
                optical = optical_states.get(neuron_id) if optical_states else None
                if optical is None:
                    optical = state_from_neuron(neuron)
                handle.write(encode_optical_record(neuron_id, tick, optical))
                if self.restart_capable:
                    handle.write(_encode_core_extension(neuron))
            handle.write(b"\x00" * (synapse_offset - handle.tell()))
            for source_id, synapse in synapse_pairs:
                handle.write(_encode_synapse(source_id, synapse))

        actual_size = destination.stat().st_size
        if actual_size != file_size:
            raise RuntimeError(
                f".b5d size mismatch: expected {file_size}, wrote {actual_size}"
            )
        return header


class B5DReader:
    """Memory-mapped random-access reader for frozen Brain-5D V1 snapshots."""

    def __init__(self, path: str | Path) -> None:
        assert_format_invariants()
        self.path = Path(path)
        self._handle = self.path.open("rb")
        file_size = self.path.stat().st_size
        if file_size < HEADER_SIZE:
            self._handle.close()
            raise B5DFormatError(f"file too small: {file_size} < {HEADER_SIZE} bytes")
        self._mmap = mmap.mmap(self._handle.fileno(), 0, access=mmap.ACCESS_READ)
        self._metadata: dict[str, JSONValue] = {}
        try:
            self.header = _parse_header_bytes(self._mmap[:HEADER_SIZE])
            self._validate_sections()
            self._metadata = self._read_metadata()
        except Exception:
            self.close()
            raise

    def __enter__(self) -> "B5DReader":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: object,
    ) -> None:
        self.close()

    @property
    def closed(self) -> bool:
        """Return whether the mmap and file handle have been closed."""
        return self._mmap.closed and self._handle.closed

    @property
    def metadata(self) -> dict[str, JSONValue]:
        """Return a copy of validated snapshot metadata."""
        return dict(self._metadata)

    @property
    def neuron_count(self) -> int:
        """Return the number of fixed-size neuron records."""
        return self.header.neuron_count

    @property
    def synapse_count(self) -> int:
        """Return the number of fixed-size synapse records."""
        return self.header.synapse_count

    def close(self) -> None:
        """Release the mmap and underlying file handle idempotently."""
        if not self._mmap.closed:
            self._mmap.close()
        if not self._handle.closed:
            self._handle.close()

    def _validate_sections(self) -> None:
        if len(self._mmap) != self.header.file_size:
            raise B5DFormatError(
                "file-size mismatch: "
                f"header={self.header.file_size}, actual={len(self._mmap)}"
            )
        if self.header.metadata_offset != HEADER_SIZE:
            raise B5DFormatError("invalid metadata offset")
        if self.header.neuron_offset % ALIGNMENT != 0:
            raise B5DFormatError("neuron section is not 64-byte aligned")
        if self.header.synapse_offset % ALIGNMENT != 0:
            raise B5DFormatError("synapse section is not 64-byte aligned")

        metadata_end = self.header.metadata_offset + self.header.metadata_size
        neurons_end = (
            self.header.neuron_offset
            + self.header.neuron_count * self.header.neuron_record_size
        )
        synapses_end = (
            self.header.synapse_offset
            + self.header.synapse_count * self.header.synapse_record_size
        )
        if metadata_end > self.header.neuron_offset:
            raise B5DFormatError("metadata overlaps neuron section")
        if neurons_end > self.header.synapse_offset:
            raise B5DFormatError("neuron section overlaps synapse section")
        if synapses_end != self.header.file_size:
            raise B5DFormatError("file truncated or header counts are inconsistent")

    def _read_metadata(self) -> dict[str, JSONValue]:
        start = self.header.metadata_offset
        end = start + self.header.metadata_size
        return _decode_metadata(bytes(self._mmap[start:end]))

    def _neuron_offset_for_index(self, index: int) -> int:
        if not 0 <= index < self.header.neuron_count:
            raise IndexError("neuron record index out of range")
        return self.header.neuron_offset + index * self.header.neuron_record_size

    def _neuron_id_at_index(self, index: int) -> int:
        offset = self._neuron_offset_for_index(index)
        return int(_NEURON_ID_STRUCT.unpack_from(self._mmap, offset)[0])

    def _synapse_offset_for_index(self, index: int) -> int:
        if not 0 <= index < self.header.synapse_count:
            raise IndexError("synapse record index out of range")
        return self.header.synapse_offset + index * SYNAPSE_RECORD_SIZE

    def _synapse_source_at_index(self, index: int) -> int:
        return int(
            _NEURON_ID_STRUCT.unpack_from(
                self._mmap, self._synapse_offset_for_index(index)
            )[0]
        )

    def get_neuron(self, neuron_id: int) -> B5DNeuronRecord | None:
        """Return one neuron by ID using O(log n) binary search."""
        low = 0
        high = self.header.neuron_count - 1
        target = int(neuron_id)
        while low <= high:
            mid = (low + high) // 2
            current = self._neuron_id_at_index(mid)
            if current < target:
                low = mid + 1
            elif current > target:
                high = mid - 1
            else:
                return self._decode_neuron_index(mid)
        return None

    def _decode_neuron_index(self, index: int) -> B5DNeuronRecord:
        offset = self._neuron_offset_for_index(index)
        optical_end = offset + OPTICAL_RECORD_SIZE
        raw_optical = bytes(self._mmap[offset:optical_end])
        if len(raw_optical) != OPTICAL_RECORD_SIZE:
            raise B5DFormatError("truncated optical neuron record")
        neuron_id, tick, optical = decode_optical_record(raw_optical)
        if not self.header.restart_capable:
            return B5DNeuronRecord(
                neuron_id=int(neuron_id), tick=int(tick), optical=optical
            )
        core_end = optical_end + CORE_EXTENSION_SIZE
        extension = bytes(self._mmap[optical_end:core_end])
        a, b, c, d, spike_cost, spike_counter, last_spike_tick = _decode_core_extension(
            extension
        )
        return B5DNeuronRecord(
            neuron_id=int(neuron_id),
            tick=int(tick),
            optical=optical,
            a=a,
            b=b,
            c=c,
            d=d,
            spike_cost=spike_cost,
            spike_counter=spike_counter,
            last_spike_tick=last_spike_tick,
        )

    def iter_neurons(self) -> Iterator[B5DNeuronRecord]:
        """Yield neuron records in ascending neuron-ID order."""
        for index in range(self.header.neuron_count):
            yield self._decode_neuron_index(index)

    def _decode_synapse_index(self, index: int) -> B5DSynapseRecord:
        offset = self._synapse_offset_for_index(index)
        end = offset + SYNAPSE_RECORD_SIZE
        return _decode_synapse(bytes(self._mmap[offset:end]))

    def iter_synapses(self) -> Iterator[B5DSynapseRecord]:
        """Yield all synapse records in source/target sort order."""
        for index in range(self.header.synapse_count):
            yield self._decode_synapse_index(index)

    def get_synapses(self, source_id: int) -> Iterator[B5DSynapseRecord]:
        """Yield one source neuron's synapses via binary-search range lookup."""
        target = int(source_id)
        low = 0
        high = self.header.synapse_count
        while low < high:
            mid = (low + high) // 2
            if self._synapse_source_at_index(mid) < target:
                low = mid + 1
            else:
                high = mid
        index = low
        while index < self.header.synapse_count:
            if self._synapse_source_at_index(index) != target:
                break
            yield self._decode_synapse_index(index)
            index += 1

    def validate_invariants(self, *, full_scan: bool = True) -> None:
        """Validate V1 structure and optionally scan sorted record invariants.

        Structural header/offset/metadata validation already runs during open.
        ``full_scan=True`` additionally verifies neuron-ID uniqueness/order,
        synapse source/target ordering, referential integrity, and zero padding.
        """
        assert_format_invariants()
        self._validate_sections()
        if not full_scan:
            return

        metadata_end = self.header.metadata_offset + self.header.metadata_size
        neurons_end = (
            self.header.neuron_offset
            + self.header.neuron_count * self.header.neuron_record_size
        )
        if any(self._mmap[metadata_end : self.header.neuron_offset]):
            raise B5DFormatError("non-zero metadata alignment padding")
        if any(self._mmap[neurons_end : self.header.synapse_offset]):
            raise B5DFormatError("non-zero neuron alignment padding")

        previous_neuron_id: int | None = None
        neuron_ids: set[int] = set()
        for index in range(self.header.neuron_count):
            neuron_id = self._neuron_id_at_index(index)
            if previous_neuron_id is not None and neuron_id <= previous_neuron_id:
                raise B5DFormatError("neuron IDs must be strictly increasing")
            neuron_ids.add(neuron_id)
            previous_neuron_id = neuron_id

        previous_pair: tuple[int, int] | None = None
        for index in range(self.header.synapse_count):
            offset = self._synapse_offset_for_index(index)
            raw = self._mmap[offset : offset + SYNAPSE_RECORD_SIZE]
            if any(raw[26:28]) or any(raw[36:40]):
                raise B5DFormatError("reserved synapse bytes must be zero")
            synapse = self._decode_synapse_index(index)
            pair = (synapse.source_id, synapse.target_id)
            if previous_pair is not None and pair < previous_pair:
                raise B5DFormatError(
                    "synapse records must be sorted by source_id, target_id"
                )
            if synapse.source_id not in neuron_ids:
                raise B5DFormatError(
                    f"synapse source missing from neuron table: {synapse.source_id}"
                )
            if synapse.target_id not in neuron_ids:
                raise B5DFormatError(
                    f"synapse target missing from neuron table: {synapse.target_id}"
                )
            previous_pair = pair


__all__ = [
    "ALIGNMENT",
    "B5DFormatError",
    "B5DHeader",
    "B5DNeuronRecord",
    "B5DReader",
    "B5DSnapshotWriter",
    "B5DSynapseRecord",
    "BYTE_ORDER",
    "CORE_EXTENSION_SIZE",
    "ENDIANNESS",
    "FORMAT_VERSION",
    "HEADER_SIZE",
    "JSONMapping",
    "JSONValue",
    "MAGIC",
    "MAX_METADATA_SIZE",
    "NetworkSnapshotLike",
    "NeuronSnapshotLike",
    "OPTICAL_RECORD_SIZE",
    "RESTARTABLE_NEURON_RECORD_SIZE",
    "SYNAPSE_RECORD_SIZE",
    "SynapseSnapshotLike",
    "assert_format_invariants",
]
