"""Alpha.5 proposal decision integration tests."""

from src.self_organization.approval import (
    ProposalApprovalPolicy,
    StructuralPlasticityConfig,
)
from src.self_organization.coordinator import SelfOrganizationCoordinator
from src.self_organization.policy import (
    PolicyReport,
    ProposalKind,
    StructuralProposal,
)


def _coordinator() -> SelfOrganizationCoordinator:
    coordinator = SelfOrganizationCoordinator()
    coordinator.publish(
        PolicyReport(
            tick=10,
            proposals=(
                StructuralProposal(
                    "p1",
                    ProposalKind.NEUROGENESIS,
                    confidence=0.9,
                ),
            ),
            neurogenesis_pressure=1.0,
            pruning_pressure=0.0,
            synapse_sprouting_pressure=0.0,
            synapse_pruning_pressure=0.0,
        )
    )
    return coordinator


def test_manual_decisions_require_a_published_proposal() -> None:
    coordinator = _coordinator()

    assert coordinator.approve("p1")
    assert not coordinator.reject("missing")
    assert coordinator.decisions()[-1].accepted


def test_auto_process_records_decision_without_mutation() -> None:
    coordinator = _coordinator()
    policy = ProposalApprovalPolicy(
        StructuralPlasticityConfig(
            enabled=True,
            dry_run=False,
            auto_approval=True,
        )
    )

    decisions = coordinator.auto_process(
        policy,
        safety_ok=True,
        cooldown_ok=True,
        kind_allowed=True,
    )

    assert len(decisions) == 1
    assert decisions[0].accepted
