"""Persistent inverse-operation based undo for structural changes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.storage.structural_journal import (
    StructuralChangeKind,
    StructuralChangeRecord,
    StructuralJournal,
)


class StructuralExecutor(Protocol):
    def apply_structural_record(self, record: StructuralChangeRecord) -> bool: ...


@dataclass(frozen=True, slots=True)
class UndoResult:
    success: bool
    original_sequence: int | None
    inverse_sequence: int | None
    message: str


def inverse_record(
    record: StructuralChangeRecord, next_sequence: int, tick: int
) -> StructuralChangeRecord | None:
    if record.kind is StructuralChangeKind.NEURON_ADD:
        return StructuralChangeRecord(
            sequence=next_sequence,
            tick=tick,
            kind=StructuralChangeKind.NEURON_REMOVE,
            neuron_id=record.neuron_id,
            coord=record.coord,
            reason="undo neuron_add",
            approved_by="undo",
            undo_of_sequence=record.sequence,
        )
    if record.kind is StructuralChangeKind.SYNAPSE_ADD:
        return StructuralChangeRecord(
            sequence=next_sequence,
            tick=tick,
            kind=StructuralChangeKind.SYNAPSE_REMOVE,
            source_id=record.source_id,
            target_id=record.target_id,
            weight=record.weight,
            delay=record.delay,
            reason="undo synapse_add",
            approved_by="undo",
            undo_of_sequence=record.sequence,
        )
    if record.kind is StructuralChangeKind.SYNAPSE_REMOVE:
        if record.weight is None or record.delay is None:
            return None
        return StructuralChangeRecord(
            sequence=next_sequence,
            tick=tick,
            kind=StructuralChangeKind.SYNAPSE_ADD,
            source_id=record.source_id,
            target_id=record.target_id,
            weight=record.weight,
            delay=record.delay,
            reason="undo synapse_remove",
            approved_by="undo",
            undo_of_sequence=record.sequence,
        )
    if record.kind is StructuralChangeKind.NEURON_REMOVE:
        snapshot = record.neuron_snapshot
        if snapshot is None:
            return None
        return StructuralChangeRecord(
            sequence=next_sequence,
            tick=tick,
            kind=StructuralChangeKind.NEURON_ADD,
            neuron_id=snapshot.neuron_id,
            coord=snapshot.coord,
            reason="undo neuron_remove",
            approved_by="undo",
            undo_of_sequence=record.sequence,
            neuron_snapshot=snapshot,
        )
    # All known StructuralChangeKind values are handled above.


class StructuralUndoManager:
    def __init__(
        self, journal: StructuralJournal, executor: StructuralExecutor
    ) -> None:
        self.journal = journal
        self.executor = executor

    def undo_last(self, tick: int) -> UndoResult:
        history = self.journal.history(1000)
        undone = {
            item.undo_of_sequence
            for item in history
            if item.undo_of_sequence is not None
        }
        original = next(
            (
                item
                for item in reversed(history)
                if item.sequence not in undone and item.undo_of_sequence is None
            ),
            None,
        )
        if original is None:
            return UndoResult(False, None, None, "no undoable structural change")
        inverse = inverse_record(original, self.journal.scan().last_sequence + 1, tick)
        if inverse is None:
            return UndoResult(
                False,
                original.sequence,
                None,
                "insufficient data for inverse operation",
            )
        if not self.executor.apply_structural_record(inverse):
            return UndoResult(
                False, original.sequence, None, "executor rejected inverse operation"
            )
        self.journal.append_and_commit(inverse)
        return UndoResult(
            True, original.sequence, inverse.sequence, "structural change undone"
        )
