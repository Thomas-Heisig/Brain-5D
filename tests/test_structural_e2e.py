"""Alpha.5 Structural End-to-End Verification — Ten Proofs.

This module proves that structural changes flow exclusively through
the canonical Alpha.5 path:

    Measurement / HomeostasisSignal
        ↓
    SelfOrganizationPolicy
        ↓
    Proposal
        ↓
    SelfOrganizationCoordinator
        ↓
    Approval Gate
        ↓
    StructuralPlasticityEngine
        ↓
    Brain5DManipulator
        ↓
    Network
        ↓
    StructuralJournal

It does NOT test the legacy SelfOrganizationEngine.run_cycle() path.
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
from src.self_organization.plasticity import StructuralPlasticityEngine
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
# Topology Digest — structural equality only (no dynamic state)
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
# Helper — small deterministic network
# =========================================================================


def _make_network() -> NeuralNetwork:
    """Create a small deterministic network for structural E2E tests."""
    from src.core import Brain5DConfig

    config = Brain5DConfig.from_dict({
        "dimensions": [5, 1, 1, 1, 1],
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
