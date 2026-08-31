"""Canonical structural composition factory.

This module extracts the structural self-organization composition logic
from ``src.main`` so that both production startup and E2E tests use
exactly the same composition path.

The factory creates:

    Brain5DManipulator
    StructuralJournal
    StructuralPlasticityEngine
    SelfOrganizationCoordinator
    OperatorBridge (optional)

All components reference the same live ``NeuralNetwork`` instance.

This is NOT a test helper. It is the production composition path.
``src.main`` delegates to this factory; tests verify the factory output.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from src.controller.runtime import RuntimeController
from src.core.network import NeuralNetwork
from src.dashboard.operator_bridge import OperatorBridge
from src.manipulation.manipulator import Brain5DManipulator
from src.self_organization.coordinator import SelfOrganizationCoordinator
from src.self_organization.plasticity import (
    PlasticitySafetyLimits,
    StructuralPlasticityEngine,
)
from src.self_organization.policy import (
    LegacyStructuralProposal,
    ProposalKind,
    StructuralProposal,
)
from src.storage.structural_journal import StructuralJournal


def compose_structural_subsystem(
    network: NeuralNetwork,
    journal_path: Path,
    *,
    coordinator_enabled: bool = True,
    coordinator_dry_run: bool = False,
    max_changes_per_tick: int = 1,
    allow_neurogenesis: bool = True,
    allow_neuron_pruning: bool = True,
    allow_synapse_sprouting: bool = True,
    allow_synapse_pruning: bool = True,
    create_controller: bool = False,
    create_bridge: bool = False,
) -> dict[str, Any]:
    """Compose the canonical structural subsystem.

    This is the single production composition function. Both ``src.main``
    and E2E tests call this — tests do NOT recreate a parallel architecture.

    Args:
        network: The live NeuralNetwork (shared by all components).
        journal_path: Path for the StructuralJournal file.
        coordinator_enabled: Whether the coordinator accepts proposals.
        coordinator_dry_run: If True, coordinator stores but never executes.
        max_changes_per_tick: Rate limit for structural changes.
        allow_neurogenesis: Permit neuron creation proposals.
        allow_neuron_pruning: Permit neuron removal proposals.
        allow_synapse_sprouting: Permit synapse creation proposals.
        allow_synapse_pruning: Permit synapse removal proposals.
        create_controller: If True, create a RuntimeController for the network.
        create_bridge: If True, create an OperatorBridge wrapping everything.

    Returns:
        A dict with keys: manipulator, journal, plasticity, coordinator,
        and optionally controller, bridge.
    """
    manipulator = Brain5DManipulator(network)
    journal = StructuralJournal(journal_path)

    plasticity = StructuralPlasticityEngine(
        manipulator=manipulator,
        journal=journal,
        limits=PlasticitySafetyLimits(
            max_changes_per_tick=max_changes_per_tick,
            allow_neurogenesis=allow_neurogenesis,
            allow_neuron_pruning=allow_neuron_pruning,
            allow_synapse_sprouting=allow_synapse_sprouting,
            allow_synapse_pruning=allow_synapse_pruning,
        ),
    )

    def _plasticity_executor(proposal: LegacyStructuralProposal) -> int:
        """Adapter: translate LegacyStructuralProposal to apply_proposal call."""
        kind_map = {
            "neurogenesis": ProposalKind.NEUROGENESIS,
            "prune": ProposalKind.PRUNING,
        }
        sp = StructuralProposal(
            proposal_id=f"legacy-{proposal.tick}-{proposal.action.value}",
            kind=kind_map.get(proposal.action.value, ProposalKind.NEUROGENESIS),
            reason=proposal.reason,
        )
        change = plasticity.apply_proposal(
            tick=int(network.current_tick),
            proposal=sp,
            approved=True,
        )
        return 1 if change is not None else 0

    coordinator = SelfOrganizationCoordinator(
        executor=_plasticity_executor,
        enabled=coordinator_enabled,
        dry_run=coordinator_dry_run,
    )

    result: dict[str, Any] = {
        "manipulator": manipulator,
        "journal": journal,
        "plasticity": plasticity,
        "coordinator": coordinator,
    }

    if create_controller:
        result["controller"] = RuntimeController(network)

    if create_bridge:
        controller = result.get("controller")
        if controller is None:
            controller = RuntimeController(network)
            result["controller"] = controller
        result["bridge"] = OperatorBridge(
            controller=cast(RuntimeController, controller),
            coordinator=coordinator,
            plasticity=plasticity,
        )

    return result
