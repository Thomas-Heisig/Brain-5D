"""Crash-boundary tests for the append-only delta journal."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.storage.delta_journal import (
    COMMIT_MARKER_SIZE,
    ENTRY_HEADER_SIZE,
    JOURNAL_HEADER_SIZE,
    DeltaJournal,
    DeltaRecord,
    DeltaType,
    JournalCorruptionError,
    UncommittedTailError,
    assert_journal_format_invariants,
)


def _delta(tick: int, payload: bytes = b"x") -> DeltaRecord:
    return DeltaRecord(DeltaType.NEURON_STATE, tick, payload)


def test_journal_format_invariants() -> None:
    assert_journal_format_invariants()
    assert JOURNAL_HEADER_SIZE == 64
    assert ENTRY_HEADER_SIZE == 32
    assert COMMIT_MARKER_SIZE == 32


def test_append_commit_and_reopen(tmp_path: Path) -> None:
    path = tmp_path / "state.b5d.journal"
    with DeltaJournal(path, base_tick=10) as journal:
        assert journal.append(_delta(11, b"a")) == 1
        assert journal.append(_delta(12, b"b")) == 2
        marker = journal.commit()
        assert marker is not None
        assert marker.sequence == 2
    with DeltaJournal(path, base_tick=10) as journal:
        scan = journal.validate()
        assert [entry.payload for entry in scan.committed_entries] == [b"a", b"b"]
        assert not scan.has_uncommitted_tail


def test_tick_must_be_monotonic(tmp_path: Path) -> None:
    path = tmp_path / "tick.b5d.journal"
    with DeltaJournal(path) as journal:
        journal.append(_delta(5))
        with pytest.raises(ValueError, match="monotonic"):
            journal.append(_delta(4))


def test_preexisting_uncommitted_tail_blocks_append(tmp_path: Path) -> None:
    path = tmp_path / "tail.b5d.journal"
    with DeltaJournal(path) as journal:
        journal.append(_delta(1, b"committed"))
        journal.commit()
        journal.append(_delta(2, b"tail"))
    with DeltaJournal(path) as journal:
        with pytest.raises(UncommittedTailError):
            journal.append(_delta(3))
        assert journal.truncate_uncommitted_tail() > 0
        assert journal.append(_delta(3)) == 2


def test_partial_payload_is_recoverable_tail(tmp_path: Path) -> None:
    path = tmp_path / "partial.b5d.journal"
    with DeltaJournal(path) as journal:
        journal.append(_delta(1, b"ok"))
        journal.commit()
    with path.open("ab") as handle:
        handle.write(b"ENT1" + b"\x00" * 10)
    with DeltaJournal(path) as journal:
        scan = journal.validate()
        assert scan.tail_incomplete
        assert len(scan.committed_entries) == 1
        assert journal.truncate_uncommitted_tail() == 14


def test_committed_crc_corruption_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "crc.b5d.journal"
    with DeltaJournal(path) as journal:
        journal.append(_delta(1, b"payload"))
        journal.commit()
    raw = bytearray(path.read_bytes())
    payload_offset = JOURNAL_HEADER_SIZE + ENTRY_HEADER_SIZE
    raw[payload_offset] ^= 0x01
    path.write_bytes(raw)
    with pytest.raises(JournalCorruptionError, match="CRC mismatch"):
        with DeltaJournal(path) as journal:
            journal.validate()


def test_truncated_commit_falls_back_to_previous_commit(tmp_path: Path) -> None:
    path = tmp_path / "commit-tail.b5d.journal"
    with DeltaJournal(path) as journal:
        journal.append(_delta(1, b"first"))
        journal.commit()
        journal.append(_delta(2, b"second"))
        journal.commit()
    raw = path.read_bytes()
    path.write_bytes(raw[:-10])
    with DeltaJournal(path) as journal:
        scan = journal.validate()
        assert scan.tail_incomplete
        assert scan.last_commit is not None
        assert scan.last_commit.sequence == 1
        assert [entry.sequence for entry in scan.committed_entries] == [1]


def test_large_journal_100k_entries_opt_in(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Optional 100k-entry sequential write/read/recovery smoke test."""
    import os

    if os.environ.get("BRAIN5D_RUN_LARGE_STORAGE_TESTS") != "1":
        pytest.skip("set BRAIN5D_RUN_LARGE_STORAGE_TESTS=1 to enable")
    path = tmp_path / "large.b5d.journal"
    with DeltaJournal(path, fsync_on_commit=False) as journal:
        for tick in range(100_000):
            journal.append(DeltaRecord(DeltaType.SPIKE_EVENT, tick, b"12345678"))
        journal.commit()
    with DeltaJournal(path) as journal:
        scan = journal.validate()
        assert len(scan.committed_entries) == 100_000
        assert scan.last_commit is not None
        assert scan.last_commit.sequence == 100_000
