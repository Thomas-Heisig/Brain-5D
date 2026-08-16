"""Integration tests for structural plasticity persistence and replay."""

from pathlib import Path

from src.self_organization.plasticity import StructuralPlasticityEngine
from src.self_organization.policy import ProposalKind, StructuralProposal
from src.storage.structural_journal import StructuralChangeKind, StructuralJournal


class Manipulator:
    def __init__(self) -> None:
        self.created: set[int] = set()

    def create_neuron_near(self, neuron_id: int | None) -> int:
        created_id = 1 if neuron_id is None else neuron_id + 1
        self.created.add(created_id)
        return created_id

    def remove_neuron(self, neuron_id: int) -> bool:
        self.created.discard(neuron_id)
        return True

    def sprout_synapse(
        self, source_id: int | None, target_id: int | None
    ) -> tuple[int, int]:
        return source_id or 1, target_id or 2

    def prune_synapse(
        self, source_id: int | None, target_id: int | None
    ) -> tuple[int, int]:
        return source_id or 1, target_id or 2

    def undo(self) -> bool:
        return True

    def create_neuron(self, coord: tuple[int, int, int, int, int]) -> int:
        neuron_id = coord[0]
        self.created.add(neuron_id)
        return neuron_id

    def delete_neuron(self, neuron_id: int) -> None:
        self.created.discard(neuron_id)

    def create_synapse(
        self, source_id: int, target_id: int, weight: float, delay: int
    ) -> None:
        pass

    def delete_synapse(self, source_id: int, target_id: int) -> None:
        pass


def test_successful_proposal_is_committed_and_persistently_undoable(
    tmp_path: Path,
) -> None:
    journal = StructuralJournal(tmp_path / "structural.journal")
    manipulator = Manipulator()
    engine = StructuralPlasticityEngine(manipulator, journal=journal)
    proposal = StructuralProposal("p1", ProposalKind.NEUROGENESIS, neuron_id=0)

    change = engine.apply_proposal(10, proposal, approved=True)

    assert change is not None
    assert journal.history()[0].kind is StructuralChangeKind.NEURON_ADD
    assert engine.undo_last_change(tick=11)
    assert journal.history()[-1].kind is StructuralChangeKind.NEURON_REMOVE
    assert journal.history()[-1].undo_of_sequence == 1
