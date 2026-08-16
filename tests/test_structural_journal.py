from pathlib import Path

import pytest

from src.storage.structural_journal import (
    StructuralChangeKind,
    StructuralChangeRecord,
    StructuralJournal,
    StructuralJournalError,
    StructuralSnapshotLifecycle,
)


def record(sequence: int, tick: int = 1) -> StructuralChangeRecord:
    return StructuralChangeRecord(
        sequence=sequence,
        tick=tick,
        kind=StructuralChangeKind.NEURON_ADD,
        neuron_id=sequence,
        coord=(1, 2, 3, 4, 5),
    )


def test_append_commit_reopen(tmp_path: Path) -> None:
    path = tmp_path / "structural.journal"
    journal = StructuralJournal(path)
    journal.append_and_commit(record(1))
    reopened = StructuralJournal(path)
    assert reopened.history() == (record(1),)


def test_uncommitted_tail_is_ignored(tmp_path: Path) -> None:
    journal = StructuralJournal(tmp_path / "structural.journal")
    journal.append(record(1))
    scan = journal.scan()
    assert scan.committed == ()
    assert scan.uncommitted_records == 1


def test_non_monotonic_sequence_rejected(tmp_path: Path) -> None:
    journal = StructuralJournal(tmp_path / "structural.journal")
    with pytest.raises(StructuralJournalError):
        journal.append(record(2))


def test_snapshot_lifecycle_persists_in_required_order(tmp_path: Path) -> None:
    events: list[str] = []

    class RecordingJournal(StructuralJournal):
        def flush(self) -> None:
            super().flush()
            events.append("structural")

    lifecycle = StructuralSnapshotLifecycle(
        RecordingJournal(tmp_path / "structural.journal"),
        lambda: events.append("snapshot"),
        lambda: events.append("checkpoint"),
        lambda: events.append("complete"),
    )

    lifecycle()

    assert events == ["structural", "snapshot", "checkpoint", "complete"]
