from pathlib import Path

from src.self_organization.undo import StructuralUndoManager
from src.storage.structural_journal import (
    StructuralChangeKind,
    StructuralChangeRecord,
    StructuralJournal,
)


class Executor:
    def __init__(self) -> None:
        self.applied: list[StructuralChangeRecord] = []

    def apply_structural_record(self, record: StructuralChangeRecord) -> bool:
        self.applied.append(record)
        return True


def test_undo_add_neuron_appends_inverse(tmp_path: Path) -> None:
    journal = StructuralJournal(tmp_path / "structural.journal")
    journal.append_and_commit(
        StructuralChangeRecord(
            sequence=1,
            tick=1,
            kind=StructuralChangeKind.NEURON_ADD,
            neuron_id=42,
            coord=(1, 1, 1, 1, 1),
        )
    )
    executor = Executor()
    result = StructuralUndoManager(journal, executor).undo_last(tick=2)
    assert result.success
    assert journal.history()[-1].kind is StructuralChangeKind.NEURON_REMOVE
    assert journal.history()[-1].undo_of_sequence == 1
