"""Direct tests for the alpha.5 structural operator bridge."""

from pathlib import Path
from dataclasses import dataclass

from src.controller.runtime import RuntimeController
from src.dashboard.operator_bridge import OperatorBridge
from src.self_organization.coordinator import SelfOrganizationCoordinator
from src.self_organization.plasticity import StructuralPlasticityEngine
from src.self_organization.policy import PolicyReport, ProposalKind, StructuralProposal
from src.storage.structural_journal import StructuralJournal


@dataclass
class Result:
    spikes_this_tick: int = 0


class Network:
    current_tick = 0
    synapse_count = 0
    queued_event_count = 0
    neuron_count = 0

    def step(self) -> Result:
        self.current_tick += 1
        return Result()


class Manipulator:
    def create_neuron_near(self, neuron_id: int | None) -> int:
        return 1 if neuron_id is None else neuron_id + 1

    def remove_neuron(self, neuron_id: int) -> bool:
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
        return coord[0]

    def delete_neuron(self, neuron_id: int) -> None:
        pass

    def create_synapse(
        self, source_id: int, target_id: int, weight: float, delay: int
    ) -> None:
        pass

    def delete_synapse(self, source_id: int, target_id: int) -> None:
        pass


def test_bridge_applies_approved_proposal_and_exposes_history(tmp_path: Path) -> None:
    coordinator = SelfOrganizationCoordinator()
    coordinator.publish(
        PolicyReport(
            tick=1,
            proposals=(
                StructuralProposal("p1", ProposalKind.NEUROGENESIS, neuron_id=0),
            ),
            neurogenesis_pressure=1.0,
            pruning_pressure=0.0,
            synapse_sprouting_pressure=0.0,
            synapse_pruning_pressure=0.0,
        )
    )
    plasticity = StructuralPlasticityEngine(
        Manipulator(),
        journal=StructuralJournal(tmp_path / "structural.journal"),
    )
    bridge = OperatorBridge(RuntimeController(Network()), coordinator, plasticity)

    result = bridge.approve_structural("p1")

    assert result.ok
    assert bridge.structural_history(10)[0]["proposal_id"] == "p1"
    assert coordinator.decisions()[-1].accepted
