"""Controlled structural plasticity with operator approval and undo history."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol, assert_never

from src.core.spatial_index import unpack_coords
from src.storage.structural_journal import (
    StructuralChangeKind,
    StructuralChangeRecord,
    StructuralJournal,
)

from .policy import ProposalKind, StructuralProposal
from .undo import StructuralUndoManager


class StructuralManipulator(Protocol):
    """Small mutation boundary to keep the engine independent from implementation."""

    def create_neuron_near(self, neuron_id: int | None) -> int: ...
    def remove_neuron(self, neuron_id: int) -> bool: ...
    def sprout_synapse(
        self, source_id: int | None, target_id: int | None
    ) -> tuple[int, int]: ...
    def prune_synapse(
        self, source_id: int | None, target_id: int | None
    ) -> tuple[int, int]: ...
    def undo(self) -> bool: ...
    def create_neuron(self, coord: tuple[int, int, int, int, int]) -> int: ...
    def delete_neuron(self, neuron_id: int) -> None: ...
    def create_synapse(
        self, source_id: int, target_id: int, weight: float, delay: int
    ) -> None: ...
    def delete_synapse(self, source_id: int, target_id: int) -> None: ...


class ChangeKind(str, Enum):
    NEURON_ADDED = "neuron_added"
    NEURON_REMOVED = "neuron_removed"
    SYNAPSE_ADDED = "synapse_added"
    SYNAPSE_REMOVED = "synapse_removed"


@dataclass(frozen=True, slots=True)
class StructuralChange:
    tick: int
    proposal_id: str
    kind: ChangeKind
    description: str
    neuron_id: int | None = None
    source_id: int | None = None
    target_id: int | None = None


@dataclass(frozen=True, slots=True)
class PlasticitySafetyLimits:
    max_changes_per_tick: int = 1
    allow_neurogenesis: bool = True
    allow_neuron_pruning: bool = False
    allow_synapse_sprouting: bool = True
    allow_synapse_pruning: bool = True


class StructuralPlasticityEngine:
    """Apply only explicitly approved proposals through the Manipulator boundary."""

    def __init__(
        self,
        manipulator: StructuralManipulator,
        limits: PlasticitySafetyLimits | None = None,
        journal: StructuralJournal | None = None,
    ) -> None:
        self._manipulator = manipulator
        self._limits = limits or PlasticitySafetyLimits()
        self._history: list[StructuralChange] = []
        self._changes_by_tick: dict[int, int] = {}
        self._journal = journal
        self._records: list[StructuralChangeRecord] = []
        self._undo: StructuralUndoManager | None = (
            StructuralUndoManager(journal, self) if journal is not None else None
        )

    @property
    def manipulator(self) -> StructuralManipulator:
        """The underlying structural manipulator instance."""
        return self._manipulator

    @property
    def journal(self) -> StructuralJournal | None:
        """The structural journal instance, if any."""
        return self._journal

    def apply_proposal(
        self, tick: int, proposal: StructuralProposal, *, approved: bool
    ) -> StructuralChange | None:
        if not approved:
            return None
        used = self._changes_by_tick.get(tick, 0)
        if used >= self._limits.max_changes_per_tick:
            raise RuntimeError("structural change rate limit reached")

        change = self._apply(tick, proposal)
        if change is not None:
            self._history.append(change)
            self._changes_by_tick[tick] = used + 1
            record = self._record_for_change(change, proposal)
            if self._journal is not None:
                self._journal.append_and_commit(record)
            self._records.append(record)
        return change

    def undo_last_change(self, tick: int | None = None) -> bool:
        if self._undo is not None:
            undo_tick = tick
            if undo_tick is None:
                history = self._journal.history(1) if self._journal is not None else ()
                undo_tick = history[-1].tick + 1 if history else 0
            return self._undo.undo_last(undo_tick).success
        if not self._history:
            return False
        if not self._manipulator.undo():
            return False
        self._history.pop()
        return True

    def history(self, limit: int = 100) -> tuple[StructuralChangeRecord, ...]:
        if limit <= 0:
            return ()
        if self._journal is not None:
            return self._journal.history(limit)
        return tuple(self._records[-limit:])

    def apply_structural_record(self, record: StructuralChangeRecord) -> bool:
        """Apply one persisted structural operation through the manipulator."""
        if record.kind is StructuralChangeKind.NEURON_ADD:
            if record.coord is None:
                return False
            neuron_id = self._manipulator.create_neuron(record.coord)
            return record.neuron_id is None or neuron_id == record.neuron_id
        if record.kind is StructuralChangeKind.NEURON_REMOVE:
            if record.neuron_id is None:
                return False
            self._manipulator.delete_neuron(record.neuron_id)
            return True
        if record.kind is StructuralChangeKind.SYNAPSE_ADD:
            if (
                record.source_id is None
                or record.target_id is None
                or record.weight is None
                or record.delay is None
            ):
                return False
            self._manipulator.create_synapse(
                record.source_id,
                record.target_id,
                record.weight,
                record.delay,
            )
            return True
        if record.kind is StructuralChangeKind.SYNAPSE_REMOVE:
            if record.source_id is None or record.target_id is None:
                return False
            self._manipulator.delete_synapse(record.source_id, record.target_id)
            return True
        assert_never(record.kind)

    def _record_for_change(
        self,
        change: StructuralChange,
        proposal: StructuralProposal,
    ) -> StructuralChangeRecord:
        sequence = (
            self._journal.scan().last_sequence + 1
            if self._journal is not None
            else len(self._records) + 1
        )
        if change.kind is ChangeKind.NEURON_ADDED:
            if change.neuron_id is None:
                raise RuntimeError("neuron addition did not report a neuron id")
            return StructuralChangeRecord(
                sequence=sequence,
                tick=change.tick,
                kind=StructuralChangeKind.NEURON_ADD,
                neuron_id=change.neuron_id,
                coord=unpack_coords(change.neuron_id),
                reason=proposal.reason,
                proposal_id=proposal.proposal_id,
                approved_by="operator",
            )
        if change.kind is ChangeKind.NEURON_REMOVED:
            return StructuralChangeRecord(
                sequence=sequence,
                tick=change.tick,
                kind=StructuralChangeKind.NEURON_REMOVE,
                neuron_id=change.neuron_id,
                reason=proposal.reason,
                proposal_id=proposal.proposal_id,
                approved_by="operator",
            )
        if change.source_id is None or change.target_id is None:
            raise RuntimeError("synapse change did not report endpoint ids")
        kind = (
            StructuralChangeKind.SYNAPSE_ADD
            if change.kind is ChangeKind.SYNAPSE_ADDED
            else StructuralChangeKind.SYNAPSE_REMOVE
        )
        return StructuralChangeRecord(
            sequence=sequence,
            tick=change.tick,
            kind=kind,
            source_id=change.source_id,
            target_id=change.target_id,
            reason=proposal.reason,
            proposal_id=proposal.proposal_id,
            approved_by="operator",
        )

    def _apply(
        self, tick: int, proposal: StructuralProposal
    ) -> StructuralChange | None:
        if proposal.kind == ProposalKind.NEUROGENESIS:
            if not self._limits.allow_neurogenesis:
                return None
            new_id = self._manipulator.create_neuron_near(proposal.neuron_id)
            return StructuralChange(
                tick,
                proposal.proposal_id,
                ChangeKind.NEURON_ADDED,
                f"created neuron {new_id}",
                neuron_id=new_id,
            )
        if proposal.kind == ProposalKind.PRUNING:
            if not self._limits.allow_neuron_pruning or proposal.neuron_id is None:
                return None
            if not self._manipulator.remove_neuron(proposal.neuron_id):
                return None
            return StructuralChange(
                tick,
                proposal.proposal_id,
                ChangeKind.NEURON_REMOVED,
                f"removed neuron {proposal.neuron_id}",
                neuron_id=proposal.neuron_id,
            )
        if proposal.kind == ProposalKind.SYNAPSE_SPROUTING:
            if not self._limits.allow_synapse_sprouting:
                return None
            source, target = self._manipulator.sprout_synapse(
                proposal.neuron_id, proposal.target_id
            )
            return StructuralChange(
                tick,
                proposal.proposal_id,
                ChangeKind.SYNAPSE_ADDED,
                f"created synapse {source}->{target}",
                source_id=source,
                target_id=target,
            )
        if proposal.kind == ProposalKind.SYNAPSE_PRUNING:
            if not self._limits.allow_synapse_pruning:
                return None
            source, target = self._manipulator.prune_synapse(
                proposal.neuron_id, proposal.target_id
            )
            return StructuralChange(
                tick,
                proposal.proposal_id,
                ChangeKind.SYNAPSE_REMOVED,
                f"removed synapse {source}->{target}",
                source_id=source,
                target_id=target,
            )
        # All known ProposalKind values are handled above.
        return None  # pragma: no cover
