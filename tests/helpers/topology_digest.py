"""Canonical topology digest for deterministic structural equality comparisons.

Produces a SHA-256 digest over the canonical serialized structural
representation of a NeuralNetwork. This is used in:

- proposal non-mutation tests
- reject invariant tests
- undo invariant tests
- restart/replay invariant tests
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


def topology_digest(network: Any) -> str:
    """Compute a deterministic SHA-256 digest of the network topology.

    The digest is based on a canonical JSON representation:
    - neurons: sorted by neuron_id, each with their coordinate
    - synapses: sorted by (source_id, target_id, delay, weight)

    Args:
        network: A NeuralNetwork-like object with .neurons and .synapses.

    Returns:
        Hex SHA-256 digest string.
    """
    from src.core.spatial_index import unpack_coords

    # Canonical neuron list
    neuron_ids = sorted(network.neurons.keys())
    neurons_canonical: list[dict[str, Any]] = []
    for nid in neuron_ids:
        neurons_canonical.append(
            {
                "neuron_id": nid,
                "coord": list(unpack_coords(nid)),
            }
        )

    # Canonical synapse list
    synapses_canonical: list[dict[str, Any]] = []
    for source_id in sorted(network.synapses.keys()):
        syn_list = sorted(
            network.synapses[source_id],
            key=lambda s: (int(s.target_id), int(s.delay), float(s.weight)),
        )
        for syn in syn_list:
            synapses_canonical.append(
                {
                    "source_id": source_id,
                    "target_id": int(syn.target_id),
                    "weight": float(syn.weight),
                    "delay": int(syn.delay),
                }
            )

    canonical = {
        "neuron_count": len(neuron_ids),
        "synapse_count": len(synapses_canonical),
        "neurons": neurons_canonical,
        "synapses": synapses_canonical,
    }

    raw = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()
