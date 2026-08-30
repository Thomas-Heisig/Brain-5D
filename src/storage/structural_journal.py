"""Crash-tolerant append-only journal for structural Brain-5D changes."""

from __future__ import annotations

import json
import os
import struct
import time
import zlib
from collections.abc import Callable, Iterator
from dataclasses import asdict, dataclass, field, replace
from enum import Enum
from pathlib import Path
from typing import TypeAlias, cast

Coord5D: TypeAlias = tuple[int, int, int, int, int]

_MAGIC = b"B5DSJNL1"
_VERSION = 1
_HEADER = struct.Struct("<8sH6x")
_RECORD_HEADER = struct.Struct("<BQQII")  # type, sequence, tick, payload_len, crc32
_TYPE_CHANGE = 1
_TYPE_COMMIT = 2
_MAX_PAYLOAD = 16 * 1024 * 1024


class StructuralJournalError(RuntimeError):
    """Raised for invalid or corrupt structural journals."""


class StructuralChangeKind(str, Enum):
    NEURON_ADD = "neuron_add"
    NEURON_REMOVE = "neuron_remove"
    SYNAPSE_ADD = "synapse_add"
    SYNAPSE_REMOVE = "synapse_remove"


@dataclass(frozen=True, slots=True)
class SynapseSnapshot:
    source_id: int
    target_id: int
    weight: float
    delay: int


@dataclass(frozen=True, slots=True)
class NeuronStructuralSnapshot:
    neuron_id: int
    coord: Coord5D
    parameters: dict[str, float] = field(default_factory=lambda: {})
    incoming: tuple[SynapseSnapshot, ...] = ()
    outgoing: tuple[SynapseSnapshot, ...] = ()


@dataclass(frozen=True, slots=True)
class StructuralChangeRecord:
    sequence: int
    tick: int
    kind: StructuralChangeKind
    neuron_id: int | None = None
    source_id: int | None = None
    target_id: int | None = None
    coord: Coord5D | None = None
    weight: float | None = None
    delay: int | None = None
    reason: str = ""
    proposal_id: str | None = None
    approved_by: str | None = None
    automatic: bool = False
    undo_of_sequence: int | None = None
    neuron_snapshot: NeuronStructuralSnapshot | None = None
    timestamp_ns: int = 0

    def with_timestamp(self) -> StructuralChangeRecord:
        if self.timestamp_ns:
            return self
        return replace(self, timestamp_ns=time.time_ns())


def _encode_record(record: StructuralChangeRecord) -> bytes:
    raw = asdict(record)
    raw["kind"] = record.kind.value
    if record.coord is not None:
        raw["coord"] = list(record.coord)
    return json.dumps(raw, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _decode_snapshot(raw: object) -> NeuronStructuralSnapshot | None:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise StructuralJournalError("invalid neuron_snapshot")
    snapshot = cast(dict[str, object], raw)
    coord = _decode_coord(snapshot.get("coord"), "neuron snapshot coord")
    parameters_raw = snapshot.get("parameters", {})
    if not isinstance(parameters_raw, dict):
        raise StructuralJournalError("invalid neuron snapshot parameters")
    parameters_data = cast(dict[object, object], parameters_raw)
    parameters = {
        str(key): _decode_float(value, "neuron parameter")
        for key, value in parameters_data.items()
    }

    def decode_synapses(value: object) -> tuple[SynapseSnapshot, ...]:
        if not isinstance(value, list):
            return ()
        out: list[SynapseSnapshot] = []
        for item in cast(list[object], value):
            if not isinstance(item, dict):
                raise StructuralJournalError("invalid synapse snapshot")
            synapse = cast(dict[str, object], item)
            out.append(
                SynapseSnapshot(
                    source_id=_decode_int(synapse.get("source_id"), "source_id"),
                    target_id=_decode_int(synapse.get("target_id"), "target_id"),
                    weight=_decode_float(synapse.get("weight"), "weight"),
                    delay=_decode_int(synapse.get("delay"), "delay"),
                )
            )
        return tuple(out)

    return NeuronStructuralSnapshot(
        neuron_id=_decode_int(snapshot.get("neuron_id"), "neuron_id"),
        coord=coord,
        parameters=parameters,
        incoming=decode_synapses(snapshot.get("incoming", [])),
        outgoing=decode_synapses(snapshot.get("outgoing", [])),
    )


def _decode_record(payload: bytes) -> StructuralChangeRecord:
    try:
        decoded = cast(object, json.loads(payload.decode("utf-8")))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise StructuralJournalError("invalid structural journal JSON") from exc
    if not isinstance(decoded, dict):
        raise StructuralJournalError("structural record must be an object")
    raw = cast(dict[str, object], decoded)
    coord_value = raw.get("coord")
    coord: Coord5D | None = None
    if coord_value is not None:
        coord = _decode_coord(coord_value, "coord")
    return StructuralChangeRecord(
        sequence=_decode_int(raw.get("sequence"), "sequence"),
        tick=_decode_int(raw.get("tick"), "tick"),
        kind=StructuralChangeKind(str(raw["kind"])),
        neuron_id=_decode_optional_int(raw.get("neuron_id"), "neuron_id"),
        source_id=_decode_optional_int(raw.get("source_id"), "source_id"),
        target_id=_decode_optional_int(raw.get("target_id"), "target_id"),
        coord=coord,
        weight=_decode_optional_float(raw.get("weight"), "weight"),
        delay=_decode_optional_int(raw.get("delay"), "delay"),
        reason=str(raw.get("reason", "")),
        proposal_id=None if raw.get("proposal_id") is None else str(raw["proposal_id"]),
        approved_by=None if raw.get("approved_by") is None else str(raw["approved_by"]),
        automatic=_decode_bool(raw.get("automatic", False), "automatic"),
        undo_of_sequence=_decode_optional_int(
            raw.get("undo_of_sequence"), "undo_of_sequence"
        ),
        neuron_snapshot=_decode_snapshot(raw.get("neuron_snapshot")),
        timestamp_ns=_decode_int(raw.get("timestamp_ns", 0), "timestamp_ns"),
    )


def _decode_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise StructuralJournalError(f"{name} must be an integer")
    try:
        return int(value)
    except ValueError as exc:
        raise StructuralJournalError(f"{name} must be an integer") from exc


def _decode_optional_int(value: object, name: str) -> int | None:
    return None if value is None else _decode_int(value, name)


def _decode_float(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise StructuralJournalError(f"{name} must be numeric")
    try:
        return float(value)
    except ValueError as exc:
        raise StructuralJournalError(f"{name} must be numeric") from exc


def _decode_optional_float(value: object, name: str) -> float | None:
    return None if value is None else _decode_float(value, name)


def _decode_bool(value: object, name: str) -> bool:
    if not isinstance(value, bool):
        raise StructuralJournalError(f"{name} must be a boolean")
    return value


def _decode_coord(value: object, name: str) -> Coord5D:
    if not isinstance(value, list):
        raise StructuralJournalError(f"{name} must contain five integers")
    coords = cast(list[object], value)
    if len(coords) != 5:
        raise StructuralJournalError(f"{name} must contain five integers")
    return (
        _decode_int(coords[0], name),
        _decode_int(coords[1], name),
        _decode_int(coords[2], name),
        _decode_int(coords[3], name),
        _decode_int(coords[4], name),
    )


@dataclass(frozen=True, slots=True)
class StructuralJournalScan:
    committed: tuple[StructuralChangeRecord, ...]
    uncommitted_records: int
    last_sequence: int


class StructuralJournal:
    """Append-only structural journal with per-record CRC and explicit commits."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            with self.path.open("wb") as handle:
                handle.write(_HEADER.pack(_MAGIC, _VERSION))
                handle.flush()
                os.fsync(handle.fileno())
        self._validate_header()

    def _validate_header(self) -> None:
        with self.path.open("rb") as handle:
            header = handle.read(_HEADER.size)
        if len(header) != _HEADER.size:
            raise StructuralJournalError("truncated structural journal header")
        magic, version = _HEADER.unpack(header)
        if magic != _MAGIC or version != _VERSION:
            raise StructuralJournalError("unsupported structural journal format")

    def append(self, record: StructuralChangeRecord) -> None:
        scan = self.scan()
        expected = scan.last_sequence + 1
        if record.sequence != expected:
            raise StructuralJournalError(
                f"sequence must be {expected}, got {record.sequence}"
            )
        payload = _encode_record(record)
        if len(payload) > _MAX_PAYLOAD:
            raise StructuralJournalError("structural record payload too large")
        crc = zlib.crc32(payload) & 0xFFFFFFFF
        header = _RECORD_HEADER.pack(
            _TYPE_CHANGE, record.sequence, record.tick, len(payload), crc
        )
        with self.path.open("ab") as handle:
            handle.write(header)
            handle.write(payload)
            handle.flush()

    def commit(self, sequence: int, tick: int) -> None:
        payload = b""
        crc = zlib.crc32(payload) & 0xFFFFFFFF
        header = _RECORD_HEADER.pack(_TYPE_COMMIT, sequence, tick, 0, crc)
        with self.path.open("ab") as handle:
            handle.write(header)
            handle.flush()
            os.fsync(handle.fileno())

    def append_and_commit(self, record: StructuralChangeRecord) -> None:
        self.append(record)
        self.commit(record.sequence, record.tick)

    def flush(self) -> None:
        """Durably flush all committed structural records to disk."""
        with self.path.open("ab") as handle:
            handle.flush()
            os.fsync(handle.fileno())

    def scan(self) -> StructuralJournalScan:
        committed: list[StructuralChangeRecord] = []
        pending: list[StructuralChangeRecord] = []
        last_sequence = 0
        with self.path.open("rb") as handle:
            handle.seek(_HEADER.size)
            while True:
                offset = handle.tell()
                raw_header = handle.read(_RECORD_HEADER.size)
                if not raw_header:
                    break
                if len(raw_header) != _RECORD_HEADER.size:
                    break
                record_type, sequence, tick, payload_len, expected_crc = (
                    _RECORD_HEADER.unpack(raw_header)
                )
                if payload_len > _MAX_PAYLOAD:
                    raise StructuralJournalError(
                        f"payload too large at offset {offset}"
                    )
                payload = handle.read(payload_len)
                if len(payload) != payload_len:
                    break
                actual_crc = zlib.crc32(payload) & 0xFFFFFFFF
                if actual_crc != expected_crc:
                    raise StructuralJournalError(f"CRC mismatch at offset {offset}")
                if record_type == _TYPE_CHANGE:
                    record = _decode_record(payload)
                    if record.sequence != sequence or record.tick != tick:
                        raise StructuralJournalError("record header/payload mismatch")
                    if sequence != last_sequence + 1:
                        raise StructuralJournalError(
                            "non-monotonic structural journal sequence"
                        )
                    pending.append(record)
                    last_sequence = sequence
                elif record_type == _TYPE_COMMIT:
                    if payload_len != 0:
                        raise StructuralJournalError(
                            "commit marker must not contain payload"
                        )
                    if sequence > last_sequence:
                        raise StructuralJournalError(
                            "commit points past known sequence"
                        )
                    committed.extend(
                        item for item in pending if item.sequence <= sequence
                    )
                    pending = [item for item in pending if item.sequence > sequence]
                else:
                    raise StructuralJournalError(
                        f"unknown structural record type {record_type}"
                    )
        return StructuralJournalScan(tuple(committed), len(pending), last_sequence)

    def iter_committed(self) -> Iterator[StructuralChangeRecord]:
        yield from self.scan().committed

    def history(self, limit: int = 100) -> tuple[StructuralChangeRecord, ...]:
        if limit <= 0:
            return ()
        records = self.scan().committed
        return records[-limit:]


class StructuralSnapshotLifecycle:
    """Compose durable structural, base snapshot, and checkpoint persistence."""

    def __init__(
        self,
        journal: StructuralJournal,
        write_snapshot: Callable[[], None],
        write_checkpoint: Callable[[], None],
        report_completion: Callable[[], None] | None = None,
    ) -> None:
        self._journal = journal
        self._write_snapshot = write_snapshot
        self._write_checkpoint = write_checkpoint
        self._report_completion = report_completion

    def __call__(self) -> None:
        self._journal.flush()
        self._write_snapshot()
        self._write_checkpoint()
        if self._report_completion is not None:
            self._report_completion()
