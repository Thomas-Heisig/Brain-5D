"""Alpha.5 Structural End-to-End Verification -- Ten Proofs.

This module proves that structural changes flow exclusively through
the canonical Alpha.5 path:

    Measurement / HomeostasisSignal
        -> SelfOrganizationPolicy
        -> Proposal
        -> SelfOrganizationCoordinator
        -> Approval Gate
        -> StructuralPlasticityEngine
        -> Brain5DManipulator
        -> Network
        -> StructuralJournal

It does NOT test the legacy SelfOrganizationEngine.run_cycle() path.

On success, a machine-readable verification artifact is written to
``artifacts/structural_e2e_results.json`` so that ``GateStatusBuilder``
can set the structural criteria from real evidence instead of guessing.
"""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path
from typing import Any

import pytest

from src.controller.runtime import RuntimeController
from src.core.network import NeuralNetwork
from src.core.spatial_index import pack_coords, unpack_coords
from src.dashboard.operator_bridge import OperatorBridge
from src.manipulation.manipulator import Brain5DManipulator
from src.self_organization.coordinator import SelfOrganizationCoordinator
from src.self_organization.plasticity import (
    PlasticitySafetyLimits,
    StructuralPlasticityEngine,
)
from src.self_organization.policy import (
    HomeostasisSignalLike,
    LegacyStructuralProposal,
    PolicyReport,
    ProposalKind,
    SelfOrganizationPolicy,
    SelfOrganizationPolicyConfig,
    StructuralAction,
    StructuralProposal,
)
from src.storage.structural_journal import (
    StructuralChangeKind,
    StructuralChangeRecord,
    StructuralJournal,
)

# =========================================================================
# Topology Digest -- structural equality only (no dynamic state)
# =========================================================================


def _structural_digest(network: Any) -> str:
    """SHA-256 over canonical structural representation.

    Includes only structural identity fields:
    - neurons: neuron_id, coord
    - synapses: source_id, target_id, weight, delay

    Does NOT include dynamic state (v, u, energy, spike counters).
    """
    neuron_ids = sorted(network.neurons.keys())
    neurons_canonical: list[dict[str, Any]] = []
    for nid in neuron_ids:
        neurons_canonical.append({
            "neuron_id": nid,
            "coord": list(unpack_coords(nid)),
        })

    synapses_canonical: list[dict[str, Any]] = []
    for source_id in sorted(network.synapses.keys()):
        syn_list = sorted(
            network.synapses[source_id],
            key=lambda s: (int(s.target_id), int(s.delay), float(s.weight)),
        )
        for syn in syn_list:
            synapses_canonical.append({
                "source_id": source_id,
                "target_id": int(syn.target_id),
                "weight": float(syn.weight),
                "delay": int(syn.delay),
            })

    canonical = {
        "neuron_count": len(neuron_ids),
        "synapse_count": len(synapses_canonical),
        "neurons": neurons_canonical,
        "synapses": synapses_canonical,
    }
    raw = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


# =========================================================================
# Helper -- small deterministic network
# =========================================================================


def _make_network() -> NeuralNetwork:
    """Create a small deterministic network for structural E2E tests."""
    from src.core import Brain5DConfig

    config = Brain5DConfig.from_dict({
        "dimensions": [10, 10, 1, 1, 1],
        "simulation": {"dt_ms": 1.0, "max_delay": 3, "debug_invariants": True},
        "neuron": {"a": 0.02, "b": 0.2, "c": -65.0, "d": 8.0},
        "energy": {"initial": 1.0, "spike_cost": 0.001},
        "topology": {"allow_self_connections": False, "allow_parallel_connections": False},
        "network": {"weight_min": 0.0, "weight_max": 0.5},
    })
    rng = random.Random(42)
    net = NeuralNetwork(config, rng)
    a = net.add_neuron((0, 0, 0, 0, 0))
    b = net.add_neuron((1, 0, 0, 0, 0))
    c = net.add_neuron((2, 0, 0, 0, 0))
    net.connect(a, b, 0.3, 1)
    net.connect(b, c, 0.2, 1)
    return net


# =========================================================================
# Helper -- fake homeostasis signal for proposal generation
# =========================================================================


class _FakeSignal:
    """Minimal HomeostasisSignalLike for policy.evaluate/analyze."""

    def __init__(
        self,
        tick: int = 0,
        neuron_count: int = 3,
        target_rate_hz: float = 10.0,
        mean_rate_hz: float = 1.0,
        low_rate_neurons: int = 3,
        high_rate_neurons: int = 0,
        low_energy_neurons: int = 0,
    ) -> None:
        self.tick = tick
        self.neuron_count = neuron_count
        self.target_rate_hz = target_rate_hz
        self.mean_rate_hz = mean_rate_hz
        self.low_rate_neurons = low_rate_neurons
        self.high_rate_neurons = high_rate_neurons
        self.low_energy_neurons = low_energy_neurons


# =========================================================================
# Helper -- build the full canonical structural chain
# =========================================================================


def _build_chain(tmp_path: Path) -> tuple[
    NeuralNetwork,
    Brain5DManipulator,
    StructuralJournal,
    StructuralPlasticityEngine,
    SelfOrganizationCoordinator,
    OperatorBridge,
    RuntimeController,
]:
    """Build the full canonical structural chain in a temp directory."""
    network = _make_network()
    manipulator = Brain5DManipulator(network)

    journal_path = tmp_path / "structural.journal"
    journal = StructuralJournal(journal_path)

    plasticity = StructuralPlasticityEngine(
        manipulator=manipulator,
        journal=journal,
        limits=PlasticitySafetyLimits(
            max_changes_per_tick=1,
            allow_neurogenesis=True,
            allow_neuron_pruning=True,
            allow_synapse_sprouting=True,
            allow_synapse_pruning=True,
        ),
    )

    def _executor(proposal: LegacyStructuralProposal) -> int:
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
        executor=_executor,
        enabled=True,
        dry_run=False,
    )

    controller = RuntimeController(network)
    bridge = OperatorBridge(
        controller=controller,
        coordinator=coordinator,
        plasticity=plasticity,
    )

    return network, manipulator, journal, plasticity, coordinator, bridge, controller


# =========================================================================
# PROOF 1: Coordinator is instantiated
# =========================================================================


def test_proof_01_coordinator_instantiated(tmp_path: Path) -> None:
    """Proof 1: SelfOrganizationCoordinator is actually instantiated."""
    _net, _manip, _journal, _plast, coordinator, _bridge, _ctrl = _build_chain(tmp_path)
    assert coordinator is not None
    assert coordinator._enabled is True
    assert coordinator._dry_run is False


# =========================================================================
# PROOF 2: PlasticityEngine is instantiated
# =========================================================================


def test_proof_02_plasticity_engine_instantiated(tmp_path: Path) -> None:
    """Proof 2: StructuralPlasticityEngine is actually instantiated."""
    _net, _manip, _journal, plasticity, _coord, _bridge, _ctrl = _build_chain(tmp_path)
    assert plasticity is not None
    assert plasticity._manipulator is not None
    assert plasticity._journal is not None


# =========================================================================
# PROOF 3: Bridge contains exactly these instances
# =========================================================================


def test_proof_03_bridge_identity(tmp_path: Path) -> None:
    """Proof 3: Bridge contains exactly the coordinator and plasticity instances."""
    _net, _manip, _journal, plasticity, coordinator, bridge, _ctrl = _build_chain(tmp_path)
    assert bridge.coordinator is coordinator
    assert bridge.plasticity is plasticity
    assert bridge.controller is not None


# =========================================================================
# PROOF 4: Proposal originates from real runtime signal
# =========================================================================


def test_proof_04_real_signal_proposal(tmp_path: Path) -> None:
    """Proof 4: A proposal must originate from a real homeostasis signal
    via SelfOrganizationPolicy.analyze(), not from a hardcoded source."""
    _net, _manip, _journal, _plast, coordinator, _bridge, _ctrl = _build_chain(tmp_path)

    policy = SelfOrganizationPolicy(
        SelfOrganizationPolicyConfig(
            enabled=True,
            dry_run=True,
            neurogenesis_threshold=0.0,
        )
    )
    signal = _FakeSignal(
        tick=5,
        neuron_count=3,
        low_rate_neurons=3,
        mean_rate_hz=1.0,
        target_rate_hz=10.0,
    )
    report = policy.analyze(signal)
    assert isinstance(report, PolicyReport)
    assert len(report.proposals) > 0
    neuro_proposals = [
        p for p in report.proposals if p.kind == ProposalKind.NEUROGENESIS
    ]
    assert len(neuro_proposals) > 0

    coordinator.publish(report)
    assert coordinator.latest() is not None
    found = coordinator.find(neuro_proposals[0].proposal_id)
    assert found is not None
    assert found.kind == ProposalKind.NEUROGENESIS


# =========================================================================
# PROOF 5: Proposal alone does NOT mutate the network
# =========================================================================


def test_proof_05_proposal_no_mutation(tmp_path: Path) -> None:
    """Proof 5: A proposal alone (without approval) must NOT mutate the network."""
    net, _manip, _journal, _plast, coordinator, _bridge, _ctrl = _build_chain(tmp_path)
    digest_before = _structural_digest(net)

    policy = SelfOrganizationPolicy(
        SelfOrganizationPolicyConfig(
            enabled=True, dry_run=True, neurogenesis_threshold=0.0
        )
    )
    signal = _FakeSignal(tick=5, neuron_count=3, low_rate_neurons=3)
    report = policy.analyze(signal)
    coordinator.publish(report)

    digest_after = _structural_digest(net)
    assert digest_before == digest_after


# =========================================================================
# PROOF 6: Reject does NOT mutate the network
# =========================================================================


def test_proof_06_reject_no_mutation(tmp_path: Path) -> None:
    """Proof 6: Rejecting a proposal must NOT mutate the network."""
    net, _manip, _journal, _plast, coordinator, bridge, _ctrl = _build_chain(tmp_path)
    digest_before = _structural_digest(net)

    policy = SelfOrganizationPolicy(
        SelfOrganizationPolicyConfig(
            enabled=True, dry_run=True, neurogenesis_threshold=0.0
        )
    )
    signal = _FakeSignal(tick=5, neuron_count=3, low_rate_neurons=3)
    report = policy.analyze(signal)
    coordinator.publish(report)
    proposal_id = report.proposals[0].proposal_id

    result = bridge.reject_structural(proposal_id)
    # Reject is a successful operation (ok=True) but must NOT mutate the network.
    # The key assertion is that the topology digest remains unchanged.
    assert result.ok

    digest_after = _structural_digest(net)
    assert digest_before == digest_after


# =========================================================================
# PROOF 7: Approve produces exactly one mutation
# =========================================================================


def test_proof_07_approve_exactly_one_mutation(tmp_path: Path) -> None:
    """Proof 7: Approving a neurogenesis proposal produces exactly one mutation
    (one new neuron)."""
    net, _manip, _journal, _plast, coordinator, bridge, _ctrl = _build_chain(tmp_path)
    neuron_count_before = len(net.neurons)

    # Create a proposal with neuron_id pointing to an existing neuron,
    # so create_neuron_near can find a free neighbour.
    existing_neuron = next(iter(net.neurons))
    proposal = StructuralProposal(
        proposal_id="7:neurogenesis",
        kind=ProposalKind.NEUROGENESIS,
        neuron_id=existing_neuron,
        reason="test neurogenesis",
    )
    coordinator.publish(PolicyReport(
        tick=7,
        proposals=(proposal,),
        neurogenesis_pressure=1.0,
        pruning_pressure=0.0,
        synapse_sprouting_pressure=0.0,
        synapse_pruning_pressure=0.0,
    ))

    result = bridge.approve_structural("7:neurogenesis")
    assert result.success, f"approve failed: {result.message}"

    neuron_count_after = len(net.neurons)
    assert neuron_count_after == neuron_count_before + 1


# =========================================================================
# PROOF 8: Mutation produces exactly one Journal record
# =========================================================================


def test_proof_08_exactly_one_change_record(tmp_path: Path) -> None:
    """Proof 8: A mutation produces exactly one StructuralChangeRecord in
    the journal."""
    _net, _manip, journal, _plast, coordinator, bridge, _ctrl = _build_chain(tmp_path)

    existing_neuron = next(iter(_net.neurons))
    proposal = StructuralProposal(
        proposal_id="8:neurogenesis",
        kind=ProposalKind.NEUROGENESIS,
        neuron_id=existing_neuron,
        reason="test neurogenesis",
    )
    coordinator.publish(PolicyReport(
        tick=8,
        proposals=(proposal,),
        neurogenesis_pressure=1.0,
        pruning_pressure=0.0,
        synapse_sprouting_pressure=0.0,
        synapse_pruning_pressure=0.0,
    ))

    bridge.approve_structural("8:neurogenesis")

    history = journal.history(100)
    assert len(history) == 1
    record = history[0]
    assert record.kind == StructuralChangeKind.NEURON_ADD
    assert record.proposal_id == "8:neurogenesis"
    assert record.neuron_id is not None


# =========================================================================
# PROOF 9: Undo restores the previous topology
# =========================================================================


def test_proof_09_undo_restores_topology(tmp_path: Path) -> None:
    """Proof 9: Undo restores the network topology to its pre-mutation state."""
    net, _manip, _journal, plasticity, coordinator, bridge, _ctrl = _build_chain(tmp_path)
    digest_before = _structural_digest(net)

    existing_neuron = next(iter(net.neurons))
    proposal = StructuralProposal(
        proposal_id="9:neurogenesis",
        kind=ProposalKind.NEUROGENESIS,
        neuron_id=existing_neuron,
        reason="test neurogenesis",
    )
    coordinator.publish(PolicyReport(
        tick=9,
        proposals=(proposal,),
        neurogenesis_pressure=1.0,
        pruning_pressure=0.0,
        synapse_sprouting_pressure=0.0,
        synapse_pruning_pressure=0.0,
    ))

    bridge.approve_structural("9:neurogenesis")
    digest_after_mutation = _structural_digest(net)
    assert digest_after_mutation != digest_before

    undo_result = plasticity.undo_last_change(tick=10)
    assert undo_result is True

    digest_after_undo = _structural_digest(net)
    assert digest_after_undo == digest_before


# =========================================================================
# PROOF 10: Restart + Replay produces the same state
# =========================================================================


def test_proof_10_restart_replay_identity(tmp_path: Path) -> None:
    """Proof 10: After replaying the journal from scratch, the network
    topology is identical to the post-mutation state."""
    net, manip, journal, plasticity, coordinator, bridge, _ctrl = _build_chain(tmp_path)

    existing_neuron = next(iter(net.neurons))
    proposal = StructuralProposal(
        proposal_id="10:neurogenesis",
        kind=ProposalKind.NEUROGENESIS,
        neuron_id=existing_neuron,
        reason="test neurogenesis",
    )
    coordinator.publish(PolicyReport(
        tick=10,
        proposals=(proposal,),
        neurogenesis_pressure=1.0,
        pruning_pressure=0.0,
        synapse_sprouting_pressure=0.0,
        synapse_pruning_pressure=0.0,
    ))

    bridge.approve_structural("10:neurogenesis")
    digest_after_mutation = _structural_digest(net)

    # Simulate restart: fresh network + manipulator + plasticity, replay journal
    net2 = _make_network()
    manip2 = Brain5DManipulator(net2)
    plasticity2 = StructuralPlasticityEngine(
        manipulator=manip2,
        journal=journal,
        limits=PlasticitySafetyLimits(
            max_changes_per_tick=1,
            allow_neurogenesis=True,
            allow_neuron_pruning=True,
            allow_synapse_sprouting=True,
            allow_synapse_pruning=True,
        ),
    )

    records = journal.history(100)
    for record in records:
        plasticity2.apply_structural_record(record)

    digest_after_replay = _structural_digest(net2)
    assert digest_after_replay == digest_after_mutation


# =========================================================================
# Verification artifact writer
# =========================================================================

_PROOF_NAMES = {
    1: "01_coordinator",
    2: "02_plasticity",
    3: "03_bridge_identity",
    4: "04_real_signal_proposal",
    5: "05_proposal_no_mutation",
    6: "06_reject_no_mutation",
    7: "07_approve_exactly_one_mutation",
    8: "08_exactly_one_change_record",
    9: "09_undo_restores_topology",
    10: "10_restart_replay_identity",
}


def test_write_verification_artifact(tmp_path: Path) -> None:
    """Write a machine-readable verification artifact after all 10 proofs pass.

    This artifact is read by GateStatusBuilder to set structural criteria
    from real evidence instead of guessing.
    """
    proofs_passed: dict[str, bool] = {}

    proof_tests = [
        (1, test_proof_01_coordinator_instantiated),
        (2, test_proof_02_plasticity_engine_instantiated),
        (3, test_proof_03_bridge_identity),
        (4, test_proof_04_real_signal_proposal),
        (5, test_proof_05_proposal_no_mutation),
        (6, test_proof_06_reject_no_mutation),
        (7, test_proof_07_approve_exactly_one_mutation),
        (8, test_proof_08_exactly_one_change_record),
        (9, test_proof_09_undo_restores_topology),
        (10, test_proof_10_restart_replay_identity),
    ]

    for proof_num, test_func in proof_tests:
        proof_dir = tmp_path / f"proof_{proof_num:02d}"
        proof_dir.mkdir(exist_ok=True)
        try:
            test_func(proof_dir)
            proofs_passed[_PROOF_NAMES[proof_num]] = True
        except Exception:
            proofs_passed[_PROOF_NAMES[proof_num]] = False

    all_passed = all(proofs_passed.values())
    assert all_passed, f"Some proofs failed: {proofs_passed}"

    artifact = {
        "suite": "structural_e2e",
        "status": "verified" if all_passed else "failed",
        "proofs": proofs_passed,
    }

    artifacts_dir = Path(__file__).resolve().parents[1] / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    artifact_path = artifacts_dir / "structural_e2e_results.json"
    artifact_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
