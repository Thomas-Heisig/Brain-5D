from pathlib import Path

from src.storage.structural_journal import (
    StructuralChangeKind,
    StructuralChangeRecord,
    StructuralJournal,
)
from src.storage.structural_recovery import StructuralRecoveryManager


class Target:
    def __init__(self) -> None:
        self.sequences: list[int] = []

    def apply_structural_record(self, record: StructuralChangeRecord) -> bool:
        self.sequences.append(record.sequence)
        return True


def test_replay_only_committed_records(tmp_path: Path) -> None:
    path = tmp_path / "structural.journal"
    journal = StructuralJournal(path)
    journal.append_and_commit(
        StructuralChangeRecord(
            sequence=1,
            tick=1,
            kind=StructuralChangeKind.NEURON_ADD,
            coord=(0, 0, 0, 0, 0),
        )
    )
    journal.append(
        StructuralChangeRecord(
            sequence=2,
            tick=2,
            kind=StructuralChangeKind.NEURON_ADD,
            coord=(1, 0, 0, 0, 0),
        )
    )
    target = Target()
    report = StructuralRecoveryManager().replay(target, path)
    assert target.sequences == [1]
    assert report.ignored_uncommitted_records == 1
