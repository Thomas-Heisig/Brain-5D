"""Canonical Scientific State Definition and Full-State Digest.

This module defines *exactly* what ``State(t)`` means for Brain-5D
scientific experiments, and provides a deterministic SHA-256 digest
for verifying deterministic execution.

Phase 3 — Canonical Scientific State
=====================================
The state contract includes:

GLOBAL
- current_tick
- dimensions
- config SHA-256
- Brain-5D version

NEURONS
- deterministic neuron order (sorted by neuron_id)
- neuron_id, a, b, c, d, v, u, energy, spike_cost
- spike_counter, last_spike_tick, threshold_adaptation
- last_external_current, last_synaptic_current

SYNAPSES
- deterministic synapse identity/order (sorted by source_id, target_id)
- source_id, target_id, weight, delay, eligibility, last_pre_spike

EVENT SYSTEM
- pending delayed spike events
- event queue ordering (sorted by delivery_tick, source_id, target_id)

RNG
- complete Python random.Random state (getstate())

LEARNING
- STDP traces, eligibility traces, reward state

HOMEOSTASIS
- per-neuron smoothed rates, thresholds, energy state

STRUCTURAL
- topology digest, journal cursor, pending proposals

Phase 4 — Full-State Digest
=============================
``canonical_state_digest(runtime) -> SHA-256``

Properties:
- deterministic serialization
- stable field ordering
- stable neuron ordering (sorted by neuron_id)
- stable synapse ordering (sorted by source_id, target_id)
- stable event ordering (sorted by delivery_tick, source_id, target_id)
- no object memory addresses
- no Python repr-dependent serialization
- no wall-clock timestamps
- no Dashboard/UI data
- no nondeterministic dictionary iteration
"""

from __future__ import annotations

import hashlib
import json
import random
from collections.abc import Mapping, Sequence
from typing import Any, Protocol

# ============================================================================
# State Protocols — What the digest function needs to read
# ============================================================================


class CanonicalNeuronLike(Protocol):
    """Minimal neuron surface required for deterministic state capture."""

    @property
    def neuron_id(self) -> int: ...
    @property
    def a(self) -> float: ...
    @property
    def b(self) -> float: ...
    @property
    def c(self) -> float: ...
    @property
    def d(self) -> float: ...
    @property
    def v(self) -> float: ...
    @property
    def u(self) -> float: ...
    @property
    def energy(self) -> float: ...
    @property
    def spike_cost(self) -> float: ...
    @property
    def spike_counter(self) -> int: ...
    @property
    def last_spike_tick(self) -> int: ...
    @property
    def threshold_adaptation(self) -> float: ...
    @property
    def last_external_current(self) -> float: ...
    @property
    def last_synaptic_current(self) -> float: ...


class CanonicalSynapseLike(Protocol):
    """Minimal synapse surface required for deterministic state capture."""

    @property
    def target_id(self) -> int: ...
    @property
    def weight(self) -> float: ...
    @property
    def delay(self) -> int: ...
    @property
    def eligibility(self) -> float: ...
    @property
    def last_pre_spike(self) -> int: ...


class CanonicalSpikeEventLike(Protocol):
    """Queued spike event for deterministic state capture."""

    @property
    def source_id(self) -> int: ...
    @property
    def target_id(self) -> int: ...
    @property
    def weight(self) -> float: ...
    @property
    def delivery_tick(self) -> int: ...


class CanonicalNetworkLike(Protocol):
    """Minimal network surface required for full-state digest."""

    @property
    def current_tick(self) -> int: ...
    @property
    def dimensions(self) -> tuple[int, int, int, int, int]: ...
    @property
    def total_spikes(self) -> int: ...
    @property
    def total_events_processed(self) -> int: ...
    @property
    def rng(self) -> random.Random: ...
    @property
    def neurons(self) -> Mapping[int, CanonicalNeuronLike]: ...
    @property
    def synapses(self) -> Mapping[int, Sequence[CanonicalSynapseLike]]: ...
    @property
    def event_slots(self) -> Sequence[Sequence[CanonicalSpikeEventLike]]: ...
    @property
    def pending_currents(self) -> dict[int, float]: ...
    @property
    def input_cells(self) -> set[int]: ...
    @property
    def output_cells(self) -> set[int]: ...


# ============================================================================
# Canonical State Capture
# ============================================================================


def _canonical_neuron_state(neurons: Mapping[int, CanonicalNeuronLike]) -> list[dict[str, Any]]:
    """Capture neuron state in deterministic order (sorted by neuron_id).

    Returns a list of dicts with exact float/int values, no repr().
    """
    return [
        {
            "neuron_id": nid,
            "a": neuron.a,
            "b": neuron.b,
            "c": neuron.c,
            "d": neuron.d,
            "v": neuron.v,
            "u": neuron.u,
            "energy": neuron.energy,
            "spike_cost": neuron.spike_cost,
            "spike_counter": neuron.spike_counter,
            "last_spike_tick": neuron.last_spike_tick,
            "threshold_adaptation": neuron.threshold_adaptation,
            "last_external_current": neuron.last_external_current,
            "last_synaptic_current": neuron.last_synaptic_current,
        }
        for nid, neuron in sorted(neurons.items())
    ]


def _canonical_synapse_state(
    synapses: Mapping[int, Sequence[CanonicalSynapseLike]],
) -> list[dict[str, Any]]:
    """Capture synapse state in deterministic order (sorted by source_id, target_id)."""
    result: list[dict[str, Any]] = []
    for source_id in sorted(synapses):
        for synapse in sorted(synapses[source_id], key=lambda s: s.target_id):
            result.append({
                "source_id": source_id,
                "target_id": synapse.target_id,
                "weight": synapse.weight,
                "delay": synapse.delay,
                "eligibility": synapse.eligibility,
                "last_pre_spike": synapse.last_pre_spike,
            })
    return result


def _canonical_event_state(
    event_slots: Sequence[Sequence[CanonicalSpikeEventLike]],
) -> list[dict[str, Any]]:
    """Capture queued events in deterministic order (delivery_tick, source_id, target_id).

    Flattens the circular buffer and sorts by (delivery_tick, source_id, target_id).
    """
    all_events: list[dict[str, Any]] = []
    for slot in event_slots:
        for event in slot:
            all_events.append({
                "source_id": event.source_id,
                "target_id": event.target_id,
                "weight": event.weight,
                "delivery_tick": event.delivery_tick,
            })
    all_events.sort(key=lambda e: (e["delivery_tick"], e["source_id"], e["target_id"]))
    return all_events


def _canonical_rng_state(rng: random.Random) -> dict[str, Any]:
    """Capture RNG state using getstate() with stable serialization."""
    version, raw_state, gauss_next = rng.getstate()
    return {
        "version": version,
        "state": list(raw_state),  # tuple of ints
        "gauss_next": gauss_next,
    }


def capture_canonical_state(
    network: CanonicalNetworkLike,
    *,
    config_sha256: str = "",
    brain5d_version: str = "",
    homeostasis_rates: dict[int, float] | None = None,
    learning_state: dict[str, Any] | None = None,
    structural_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Capture the complete canonical scientific state.

    This function collects ALL scientifically relevant state from the
    network and optional subsystems. The result is a JSON-serializable
    dict with deterministic ordering throughout.

    Args:
        network: The neural network (must implement CanonicalNetworkLike).
        config_sha256: SHA-256 of the active configuration file.
        brain5d_version: Brain-5D version string.
        homeostasis_rates: Optional dict of neuron_id -> smoothed firing rate.
        learning_state: Optional dict with learning engine state.
        structural_state: Optional dict with structural subsystem state.

    Returns:
        A JSON-serializable dict with deterministic ordering.
    """
    state: dict[str, Any] = {
        "global": {
            "current_tick": network.current_tick,
            "dimensions": list(network.dimensions),
            "config_sha256": config_sha256,
            "brain5d_version": brain5d_version,
            "total_spikes": network.total_spikes,
            "total_events_processed": network.total_events_processed,
        },
        "rng": _canonical_rng_state(network.rng),
        "neurons": _canonical_neuron_state(network.neurons),
        "synapses": _canonical_synapse_state(network.synapses),
        "events": _canonical_event_state(network.event_slots),
        "pending_currents": sorted(
            (int(k), float(v)) for k, v in network.pending_currents.items()
        ),
        "input_cells": sorted(int(v) for v in network.input_cells),
        "output_cells": sorted(int(v) for v in network.output_cells),
    }

    if homeostasis_rates is not None:
        state["homeostasis_rates"] = sorted(
            (int(k), float(v)) for k, v in homeostasis_rates.items()
        )

    if learning_state is not None:
        state["learning"] = learning_state

    if structural_state is not None:
        state["structural"] = structural_state

    return state


def canonical_state_digest(
    network: CanonicalNetworkLike,
    *,
    config_sha256: str = "",
    brain5d_version: str = "",
    homeostasis_rates: dict[int, float] | None = None,
    learning_state: dict[str, Any] | None = None,
    structural_state: dict[str, Any] | None = None,
) -> str:
    """Compute the SHA-256 digest of the canonical scientific state.

    This is a FULL scientific runtime digest — NOT the structural
    topology digest. It includes neurons, synapses, events, RNG,
    learning, homeostasis, and structural state.

    Properties:
    - deterministic serialization (stable JSON key order)
    - stable field ordering
    - stable neuron ordering (sorted by neuron_id)
    - stable synapse ordering (sorted by source_id, target_id)
    - stable event ordering (sorted by delivery_tick, source_id, target_id)
    - no object memory addresses
    - no Python repr-dependent serialization
    - no wall-clock timestamps
    - no Dashboard/UI data
    - no nondeterministic dictionary iteration

    Returns:
        Hex SHA-256 digest string.
    """
    state = capture_canonical_state(
        network,
        config_sha256=config_sha256,
        brain5d_version=brain5d_version,
        homeostasis_rates=homeostasis_rates,
        learning_state=learning_state,
        structural_state=structural_state,
    )
    # sort_keys=True ensures deterministic JSON serialization
    payload = json.dumps(state, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
