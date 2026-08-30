"""Append-only delta journal for Brain-5D snapshot persistence.

The journal is deliberately separate from the frozen ``.b5d`` V1 snapshot
format.  A journal header is immutable after creation.  Data records and
commit markers are appended sequentially and protected with CRC32.
"""

from __future__ import annotations

import os
import struct
import time
from collections.abc import Iterator
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import BinaryIO

from .crc import compute_crc32, verify_crc32

BYTE_ORDER = "little"
ENDIANNESS = "<"
JOURNAL_VERSION = 1
JOURNAL_MAGIC = b"B5DJNL1\x00"
ENTRY_MAGIC = b"ENT1"
COMMIT_MAGIC = b"CMT1"
JOURNAL_HEADER_SIZE = 64
ENTRY_HEADER_SIZE = 32
COMMIT_MARKER_SIZE = 32
MAX_PAYLOAD_SIZE = 1_048_576
ENTRY_FLAG_NONE = 0

# magic, version, header_size, flags, created_ns, base_tick, reserved0,
# reserved1, padding
_JOURNAL_HEADER_STRUCT = struct.Struct("<8sHHIQQQQ16s")
# magic, sequence, tick, delta_type, flags, payload_size, crc32
_ENTRY_HEADER_STRUCT = struct.Struct("<4sQqHHII")
# magic, sequence, tick, committed_entry_count, crc32, padding
_COMMIT_STRUCT = struct.Struct("<4sQqII4s")

if _JOURNAL_HEADER_STRUCT.size != JOURNAL_HEADER_SIZE:
    raise RuntimeError("journal header layout must remain 64 bytes")
if _ENTRY_HEADER_STRUCT.size != ENTRY_HEADER_SIZE:
    raise RuntimeError("journal entry header layout must remain 32 bytes")
if _COMMIT_STRUCT.size != COMMIT_MARKER_SIZE:
    raise RuntimeError("journal commit marker layout must remain 32 bytes")


class DeltaType(IntEnum):
    """Stable identifiers for journal payload semantics."""

    NEURON_STATE = 1
    SYNAPSE_WEIGHT = 2
    NEURON_ADD = 3
    NEURON_REMOVE = 4
    SYNAPSE_ADD = 5
    SYNAPSE_REMOVE = 6
    PARAMETER = 7
    SPIKE_EVENT = 8


class JournalError(RuntimeError):
    """Base exception for journal failures."""


class JournalCorruptionError(JournalError):
    """Raised when committed or structurally required journal data is corrupt."""


class UncommittedTailError(JournalError):
    """Raised when append is attempted after an uncommitted tail."""


@dataclass(frozen=True, slots=True)
class JournalHeader:
    """Immutable journal-file header."""

    created_ns: int
    base_tick: int
    flags: int = 0


@dataclass(frozen=True, slots=True)
class DeltaRecord:
    """One typed journal delta before serialization."""

    delta_type: DeltaType
    tick: int
    payload: bytes

    def __post_init__(self) -> None:
        if self.tick < 0:
            raise ValueError("tick must be non-negative")
        if len(self.payload) > MAX_PAYLOAD_SIZE:
            raise ValueError(
                f"payload exceeds {MAX_PAYLOAD_SIZE} bytes: {len(self.payload)}"
            )


@dataclass(frozen=True, slots=True)
class JournalEntry:
    """One fully validated entry read from disk."""

    sequence: int
    tick: int
    delta_type: DeltaType
    flags: int
    payload: bytes
    crc32: int
    offset: int
    end_offset: int


@dataclass(frozen=True, slots=True)
class CommitMarker:
    """One validated commit marker."""

    sequence: int
    tick: int
    committed_entry_count: int
    offset: int
    end_offset: int


@dataclass(frozen=True, slots=True)
class JournalScan:
    """Result of one complete sequential journal scan."""

    entries: tuple[JournalEntry, ...]
    commits: tuple[CommitMarker, ...]
    complete_end_offset: int
    file_size: int
    tail_incomplete: bool

    @property
    def last_commit(self) -> CommitMarker | None:
        """Return the latest valid commit marker, if one exists."""
        return self.commits[-1] if self.commits else None

    @property
    def committed_entries(self) -> tuple[JournalEntry, ...]:
        """Return entries covered by the latest commit marker."""
        marker = self.last_commit
        if marker is None:
            return ()
        result = tuple(
            entry for entry in self.entries if entry.sequence <= marker.sequence
        )
        if len(result) != marker.committed_entry_count:
            raise JournalCorruptionError(
                "commit marker entry count does not match committed entries"
            )
        return result

    @property
    def committed_end_offset(self) -> int:
        """Return the byte offset immediately after the latest valid commit."""
        marker = self.last_commit
        return marker.end_offset if marker is not None else JOURNAL_HEADER_SIZE

    @property
    def has_uncommitted_tail(self) -> bool:
        """Return whether bytes or complete entries exist after the last commit."""
        return self.file_size > self.committed_end_offset


class DeltaJournal:
    """Append-only Brain-5D delta journal with explicit commit boundaries."""

    def __init__(
        self,
        path: str | Path,
        *,
        base_tick: int = 0,
        fsync_on_commit: bool = True,
    ) -> None:
        if base_tick < 0:
            raise ValueError("base_tick must be non-negative")
        self.path = Path(path)
        self.base_tick = base_tick
        self.fsync_on_commit = fsync_on_commit
        self._handle: BinaryIO | None = None
        self._header: JournalHeader | None = None
        self._scan: JournalScan | None = None
        self._last_sequence = 0
        self._last_tick = base_tick
        self._dirty_entry_count = 0
        self._preexisting_uncommitted_tail = False

    def __enter__(self) -> DeltaJournal:
        self.open()
        return self

    def __exit__(
        self,
        *_args: object,
    ) -> None:
        self.close()

    @property
    def closed(self) -> bool:
        """Return whether the journal has no open file handle."""
        return self._handle is None or self._handle.closed

    @property
    def header(self) -> JournalHeader:
        """Return the validated immutable journal header."""
        if self._header is None:
            raise JournalError("journal is not open")
        return self._header

    @property
    def last_sequence(self) -> int:
        """Return the highest complete entry sequence currently on disk."""
        return self._last_sequence

    @property
    def last_tick(self) -> int:
        """Return the highest complete entry tick currently on disk."""
        return self._last_tick

    @property
    def dirty_entry_count(self) -> int:
        """Return entries appended since the latest commit marker."""
        return self._dirty_entry_count

    def open(self) -> None:
        """Open an existing journal or create a new immutable header."""
        if not self.closed:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        existed = self.path.exists()
        self._handle = self.path.open("r+b" if existed else "w+b")
        try:
            if not existed:
                self._header = JournalHeader(
                    created_ns=time.time_ns(), base_tick=self.base_tick
                )
                self._write_new_header(self._header)
                self._handle.flush()
                if self.fsync_on_commit:
                    os.fsync(self._handle.fileno())
            else:
                self._header = self._read_header()
                if self._header.base_tick != self.base_tick and self.base_tick != 0:
                    raise JournalError(
                        f"journal base tick {self._header.base_tick} does not match "
                        f"requested {self.base_tick}"
                    )
            self._scan = self.scan()
            self._preexisting_uncommitted_tail = self._scan.has_uncommitted_tail
            self._restore_runtime_counters(self._scan)
        except Exception:
            self.close()
            raise

    def close(self) -> None:
        """Close the journal idempotently without implicitly committing data."""
        if self._handle is not None and not self._handle.closed:
            self._handle.close()
        self._handle = None

    def _require_handle(self) -> BinaryIO:
        if self._handle is None or self._handle.closed:
            raise JournalError("journal is not open")
        return self._handle

    def _write_new_header(self, header: JournalHeader) -> None:
        handle = self._require_handle()
        raw = _JOURNAL_HEADER_STRUCT.pack(
            JOURNAL_MAGIC,
            JOURNAL_VERSION,
            JOURNAL_HEADER_SIZE,
            header.flags,
            header.created_ns,
            header.base_tick,
            0,
            0,
            b"\x00" * 16,
        )
        handle.seek(0)
        handle.write(raw)

    def _read_header(self) -> JournalHeader:
        handle = self._require_handle()
        handle.seek(0, os.SEEK_END)
        size = handle.tell()
        if size < JOURNAL_HEADER_SIZE:
            raise JournalCorruptionError(
                f"journal is shorter than {JOURNAL_HEADER_SIZE}-byte header"
            )
        handle.seek(0)
        raw = handle.read(JOURNAL_HEADER_SIZE)
        if len(raw) != JOURNAL_HEADER_SIZE:
            raise JournalCorruptionError("journal header is truncated")
        (
            magic,
            version,
            header_size,
            flags,
            created_ns,
            base_tick,
            reserved0,
            reserved1,
            padding,
        ) = _JOURNAL_HEADER_STRUCT.unpack(raw)
        if magic != JOURNAL_MAGIC:
            raise JournalCorruptionError(f"invalid journal magic: {magic!r}")
        if version != JOURNAL_VERSION:
            raise JournalCorruptionError(f"unsupported journal version: {version}")
        if header_size != JOURNAL_HEADER_SIZE:
            raise JournalCorruptionError("invalid journal header size")
        if reserved0 != 0 or reserved1 != 0 or padding != b"\x00" * 16:
            raise JournalCorruptionError("journal reserved header bytes are non-zero")
        return JournalHeader(created_ns=created_ns, base_tick=base_tick, flags=flags)

    @staticmethod
    def _entry_crc_input(
        sequence: int,
        tick: int,
        delta_type: DeltaType,
        flags: int,
        payload: bytes,
    ) -> bytes:
        header_without_crc = _ENTRY_HEADER_STRUCT.pack(
            ENTRY_MAGIC,
            sequence,
            tick,
            int(delta_type),
            flags,
            len(payload),
            0,
        )
        return header_without_crc + payload

    @staticmethod
    def _commit_crc_input(
        sequence: int,
        tick: int,
        committed_entry_count: int,
    ) -> bytes:
        return _COMMIT_STRUCT.pack(
            COMMIT_MAGIC,
            sequence,
            tick,
            committed_entry_count,
            0,
            b"\x00" * 4,
        )

    def append(self, delta: DeltaRecord) -> int:
        """Append one uncommitted delta and return its new sequence number."""
        handle = self._require_handle()
        if self._preexisting_uncommitted_tail:
            raise UncommittedTailError(
                "journal contains a pre-existing uncommitted tail"
            )
        if delta.tick < self._last_tick:
            raise ValueError(
                f"tick must be monotonic: {delta.tick} < {self._last_tick}"
            )
        sequence = self._last_sequence + 1
        crc = compute_crc32(
            self._entry_crc_input(
                sequence,
                delta.tick,
                delta.delta_type,
                ENTRY_FLAG_NONE,
                delta.payload,
            )
        )
        raw_header = _ENTRY_HEADER_STRUCT.pack(
            ENTRY_MAGIC,
            sequence,
            delta.tick,
            int(delta.delta_type),
            ENTRY_FLAG_NONE,
            len(delta.payload),
            crc,
        )
        handle.seek(0, os.SEEK_END)
        handle.write(raw_header)
        handle.write(delta.payload)
        handle.flush()
        self._last_sequence = sequence
        self._last_tick = delta.tick
        self._dirty_entry_count += 1
        self._scan = None
        return sequence

    def commit(self) -> CommitMarker | None:
        """Durably commit all entries appended since the latest marker."""
        if self._dirty_entry_count == 0:
            return None
        handle = self._require_handle()
        handle.flush()
        if self.fsync_on_commit:
            os.fsync(handle.fileno())
        scan_before = self.scan()
        entries = scan_before.entries
        if not entries:
            raise JournalError("dirty journal contains no entries")
        latest = entries[-1]
        committed_entry_count = len(entries)
        crc = compute_crc32(
            self._commit_crc_input(
                latest.sequence,
                latest.tick,
                committed_entry_count,
            )
        )
        raw = _COMMIT_STRUCT.pack(
            COMMIT_MAGIC,
            latest.sequence,
            latest.tick,
            committed_entry_count,
            crc,
            b"\x00" * 4,
        )
        handle.seek(0, os.SEEK_END)
        offset = handle.tell()
        handle.write(raw)
        handle.flush()
        if self.fsync_on_commit:
            os.fsync(handle.fileno())
        marker = CommitMarker(
            sequence=latest.sequence,
            tick=latest.tick,
            committed_entry_count=committed_entry_count,
            offset=offset,
            end_offset=offset + COMMIT_MARKER_SIZE,
        )
        self._dirty_entry_count = 0
        self._scan = self.scan()
        return marker

    def scan(self) -> JournalScan:
        """Sequentially scan complete records while preserving crash-tail semantics."""
        handle = self._require_handle()
        handle.flush()
        handle.seek(0, os.SEEK_END)
        file_size = handle.tell()
        pos = JOURNAL_HEADER_SIZE
        entries: list[JournalEntry] = []
        commits: list[CommitMarker] = []
        tail_incomplete = False
        expected_sequence = 1
        last_tick = self.header.base_tick

        while pos < file_size:
            remaining = file_size - pos
            if remaining < 4:
                tail_incomplete = True
                break
            handle.seek(pos)
            magic = handle.read(4)
            if magic == ENTRY_MAGIC:
                if remaining < ENTRY_HEADER_SIZE:
                    tail_incomplete = True
                    break
                handle.seek(pos)
                raw_header = handle.read(ENTRY_HEADER_SIZE)
                if len(raw_header) != ENTRY_HEADER_SIZE:
                    tail_incomplete = True
                    break
                (
                    _,
                    sequence,
                    tick,
                    delta_type_raw,
                    flags,
                    payload_size,
                    crc,
                ) = _ENTRY_HEADER_STRUCT.unpack(raw_header)
                if sequence != expected_sequence:
                    raise JournalCorruptionError(
                        f"non-monotonic sequence at offset {pos}: "
                        f"expected {expected_sequence}, got {sequence}"
                    )
                if tick < last_tick:
                    raise JournalCorruptionError(
                        "non-monotonic tick at sequence "
                        f"{sequence}: {tick} < {last_tick}"
                    )
                if payload_size > MAX_PAYLOAD_SIZE:
                    raise JournalCorruptionError(
                        f"payload too large at sequence {sequence}: {payload_size}"
                    )
                record_end = pos + ENTRY_HEADER_SIZE + payload_size
                if record_end > file_size:
                    tail_incomplete = True
                    break
                payload = handle.read(payload_size)
                if len(payload) != payload_size:
                    tail_incomplete = True
                    break
                try:
                    delta_type = DeltaType(delta_type_raw)
                except ValueError as exc:
                    raise JournalCorruptionError(
                        f"invalid delta type {delta_type_raw} at sequence {sequence}"
                    ) from exc
                crc_input = self._entry_crc_input(
                    sequence, tick, delta_type, flags, payload
                )
                if not verify_crc32(crc_input, crc):
                    # Record length is still known, so keep scanning.  If a later
                    # commit covers this sequence, committed_entries validation will
                    # reject it.  Without a later commit this is an uncommitted tail.
                    entry = JournalEntry(
                        sequence=sequence,
                        tick=tick,
                        delta_type=delta_type,
                        flags=flags | 0x8000,
                        payload=payload,
                        crc32=crc,
                        offset=pos,
                        end_offset=record_end,
                    )
                else:
                    entry = JournalEntry(
                        sequence=sequence,
                        tick=tick,
                        delta_type=delta_type,
                        flags=flags,
                        payload=payload,
                        crc32=crc,
                        offset=pos,
                        end_offset=record_end,
                    )
                entries.append(entry)
                expected_sequence += 1
                last_tick = tick
                pos = record_end
                continue

            if magic == COMMIT_MAGIC:
                if remaining < COMMIT_MARKER_SIZE:
                    tail_incomplete = True
                    break
                handle.seek(pos)
                raw = handle.read(COMMIT_MARKER_SIZE)
                if len(raw) != COMMIT_MARKER_SIZE:
                    tail_incomplete = True
                    break
                (
                    _,
                    sequence,
                    tick,
                    committed_entry_count,
                    crc,
                    padding,
                ) = _COMMIT_STRUCT.unpack(raw)
                expected_crc = compute_crc32(
                    self._commit_crc_input(sequence, tick, committed_entry_count)
                )
                if padding != b"\x00" * 4 or crc != expected_crc:
                    tail_incomplete = True
                    break
                if committed_entry_count != len(entries):
                    raise JournalCorruptionError(
                        "commit entry count does not match preceding records"
                    )
                if committed_entry_count == 0:
                    raise JournalCorruptionError("zero-entry commit marker is invalid")
                if entries[-1].sequence != sequence or entries[-1].tick != tick:
                    raise JournalCorruptionError(
                        "commit marker does not reference the latest entry"
                    )
                corrupt_committed = [
                    entry.sequence
                    for entry in entries[:committed_entry_count]
                    if entry.flags & 0x8000
                ]
                if corrupt_committed:
                    raise JournalCorruptionError(
                        "CRC mismatch in committed entries: "
                        + ", ".join(str(value) for value in corrupt_committed)
                    )
                commits.append(
                    CommitMarker(
                        sequence=sequence,
                        tick=tick,
                        committed_entry_count=committed_entry_count,
                        offset=pos,
                        end_offset=pos + COMMIT_MARKER_SIZE,
                    )
                )
                pos += COMMIT_MARKER_SIZE
                continue

            tail_incomplete = True
            break

        return JournalScan(
            entries=tuple(entries),
            commits=tuple(commits),
            complete_end_offset=pos,
            file_size=file_size,
            tail_incomplete=tail_incomplete,
        )

    def _restore_runtime_counters(self, scan: JournalScan) -> None:
        self._last_sequence = scan.entries[-1].sequence if scan.entries else 0
        self._last_tick = (
            scan.entries[-1].tick if scan.entries else self.header.base_tick
        )
        committed_count = (
            scan.last_commit.committed_entry_count if scan.last_commit else 0
        )
        self._dirty_entry_count = max(0, len(scan.entries) - committed_count)

    def iter_entries(self) -> Iterator[JournalEntry]:
        """Yield all complete entries, including uncommitted records."""
        yield from self.scan().entries

    def iter_committed_entries(self) -> Iterator[JournalEntry]:
        """Yield only entries covered by the latest valid commit marker."""
        yield from self.scan().committed_entries

    def validate(self) -> JournalScan:
        """Return a validated scan or raise for corruption of committed state."""
        return self.scan()

    def truncate_uncommitted_tail(self) -> int:
        """Remove bytes after the latest commit and return bytes removed."""
        handle = self._require_handle()
        scan = self.scan()
        keep = scan.committed_end_offset
        removed = scan.file_size - keep
        if removed <= 0:
            return 0
        handle.truncate(keep)
        handle.flush()
        if self.fsync_on_commit:
            os.fsync(handle.fileno())
        self._scan = self.scan()
        self._preexisting_uncommitted_tail = False
        self._restore_runtime_counters(self._scan)
        return removed


def assert_journal_format_invariants() -> None:
    """Validate frozen alpha.2 journal structure sizes and byte order."""
    if ENDIANNESS != "<" or BYTE_ORDER != "little":
        raise RuntimeError("journal format must remain little-endian")
    if _JOURNAL_HEADER_STRUCT.size != JOURNAL_HEADER_SIZE:
        raise RuntimeError("journal header size changed")
    if _ENTRY_HEADER_STRUCT.size != ENTRY_HEADER_SIZE:
        raise RuntimeError("journal entry header size changed")
    if _COMMIT_STRUCT.size != COMMIT_MARKER_SIZE:
        raise RuntimeError("journal commit marker size changed")
