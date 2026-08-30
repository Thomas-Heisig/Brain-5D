"""Real 5D network inspector for the Brain-5D operator dashboard.

This module provides data-backed inspection of the live Brain-5D network.
It surfaces real neuron 5D coordinates, membrane potentials, energies,
synapse weights/delays/eligibilities, and a real 5D→3D projection.

Design rules (Alpha.5 Dashboard Completion):
- No synthetic/demo data. Every value comes from the live ``NeuralNetwork``.
- Server-side pagination/sampling to avoid multi-million-object downloads.
- The projection is honestly labelled "Projection of 5D coordinates into 3D",
  never "echte 5D Ansicht".
- ``None`` is used for unavailable values so the frontend can render "—"
  instead of a fake measured zero.

The inspector reads the live network through the OperatorBridge's controller.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.core.spatial_index import unpack_coords
from src.dashboard.models import JSONValue

# ============================================================================
# Limits
# ============================================================================

_MAX_NEURONS_PER_PAGE = 5000
_MAX_SYNAPSES_PER_PAGE = 5000
_MAX_PROJECTION_SAMPLES = 2000
_DEFAULT_PAGE_SIZE = 500


# ============================================================================
# Payloads
# ============================================================================


@dataclass(frozen=True, slots=True)
class NetworkSummary:
    """High-level network summary computed from the live network."""

    dimensions: tuple[int, int, int, int, int]
    neuron_count: int
    synapse_count: int
    input_count: int
    output_count: int
    active_neurons: int
    silent_neurons: int
    queue_depth: int
    current_tick: int
    total_spikes: int
    mean_energy: float | None
    mean_v: float | None

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "dimensions": list(self.dimensions),
            "neuron_count": self.neuron_count,
            "synapse_count": self.synapse_count,
            "input_count": self.input_count,
            "output_count": self.output_count,
            "active_neurons": self.active_neurons,
            "silent_neurons": self.silent_neurons,
            "queue_depth": self.queue_depth,
            "current_tick": self.current_tick,
            "total_spikes": self.total_spikes,
            "mean_energy": self.mean_energy,
            "mean_v": self.mean_v,
            "source": "live_runtime",
        }


@dataclass(frozen=True, slots=True)
class NeuronPage:
    """One paginated page of neuron records."""

    neurons: list[JSONValue]
    total: int
    offset: int
    limit: int
    returned: int
    source: str

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "neurons": self.neurons,
            "total": self.total,
            "offset": self.offset,
            "limit": self.limit,
            "returned": self.returned,
            "source": self.source,
        }


@dataclass(frozen=True, slots=True)
class SynapsePage:
    """One paginated page of synapse records."""

    synapses: list[JSONValue]
    total: int
    offset: int
    limit: int
    returned: int
    source: str

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "synapses": self.synapses,
            "total": self.total,
            "offset": self.offset,
            "limit": self.limit,
            "returned": self.returned,
            "source": self.source,
        }


@dataclass(frozen=True, slots=True)
class ProjectionPayload:
    """Real 5D→3D projection of neuron coordinates."""

    points: list[JSONValue]
    sample_count: int
    total_count: int
    sampling_method: str
    mode: str
    source: str

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "points": self.points,
            "sample_count": self.sample_count,
            "total_count": self.total_count,
            "sampling_method": self.sampling_method,
            "mode": self.mode,
            "source": self.source,
            "label": "Projection of 5D coordinates into 3D",
        }


# ============================================================================
# Inspector
# ============================================================================


class NetworkInspector:
    """Inspect the live Brain-5D network with real 5D coordinates.

    The inspector is constructed with the live ``NeuralNetwork`` instance
    obtained through the OperatorBridge → RuntimeController → network chain.
    """

    def __init__(self, network: Any) -> None:
        """Initialize the inspector with a live network.

        Args:
            network: The live ``NeuralNetwork`` instance.
        """
        self.network = network

    # ------------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------------

    def summary(self, _last_result: Any | None = None) -> NetworkSummary:
        """Compute a real network summary from the live network."""
        net = self.network
        dims = tuple(net.dimensions)
        neuron_count = len(net.neurons)
        synapse_count = net.synapse_count
        input_count = len(net.input_cells)
        output_count = len(net.output_cells)
        queue_depth = net.queued_event_count
        current_tick = net.current_tick
        total_spikes = net.total_spikes

        # Active/silent: neurons that spiked at least once vs never.
        active = sum(1 for n in net.neurons.values() if n.spike_counter > 0)
        silent = neuron_count - active

        # Mean energy / mean v computed from live neurons (sampled if huge).
        mean_energy: float | None = None
        mean_v: float | None = None
        if neuron_count > 0:
            # For very large networks, sample to keep this O(1)-ish.
            sample = list(net.neurons.values())
            if len(sample) > 2000:
                # Stride sampling for a representative mean.
                stride = len(sample) // 2000
                sample = sample[::stride]
            mean_energy = sum(n.energy for n in sample) / len(sample)
            mean_v = sum(n.v for n in sample) / len(sample)

        return NetworkSummary(
            dimensions=dims,
            neuron_count=neuron_count,
            synapse_count=synapse_count,
            input_count=input_count,
            output_count=output_count,
            active_neurons=active,
            silent_neurons=silent,
            queue_depth=queue_depth,
            current_tick=current_tick,
            total_spikes=total_spikes,
            mean_energy=mean_energy,
            mean_v=mean_v,
        )

    # ------------------------------------------------------------------------
    # Neurons (paginated)
    # ------------------------------------------------------------------------

    def neurons(
        self,
        *,
        limit: int = _DEFAULT_PAGE_SIZE,
        offset: int = 0,
        active_only: bool = False,
    ) -> NeuronPage:
        """Return one paginated page of real neuron records.

        Each neuron record contains the real 5D coordinate plus v, u, energy,
        last_spike_tick, spike_counter, and active flag.
        """
        net = self.network
        limit = max(1, min(limit, _MAX_NEURONS_PER_PAGE))
        offset = max(0, offset)

        # Neurons are stored as dict[int, Neuron] keyed by packed 5D coord.
        # Sort by neuron_id (packed coord) for stable pagination.
        items = sorted(net.neurons.items())

        if active_only:
            items = [(nid, n) for nid, n in items if n.spike_counter > 0]

        total = len(items)
        page = items[offset : offset + limit]

        neurons: list[JSONValue] = []
        for nid, n in page:
            x1, x2, x3, x4, x5 = unpack_coords(nid)
            neurons.append(
                {
                    "neuron_id": nid,
                    "x1": x1,
                    "x2": x2,
                    "x3": x3,
                    "x4": x4,
                    "x5": x5,
                    "v": n.v,
                    "u": n.u,
                    "energy": n.energy,
                    "last_spike": n.last_spike_tick,
                    "spike_count": n.spike_counter,
                    "active": n.spike_counter > 0,
                    "is_input": nid in net.input_cells,
                    "is_output": nid in net.output_cells,
                    "neuron_type": n.neuron_type.name,
                }
            )

        return NeuronPage(
            neurons=neurons,
            total=total,
            offset=offset,
            limit=limit,
            returned=len(neurons),
            source="live_runtime",
        )

    # ------------------------------------------------------------------------
    # Synapses (paginated)
    # ------------------------------------------------------------------------

    def synapses(
        self,
        *,
        limit: int = _DEFAULT_PAGE_SIZE,
        offset: int = 0,
        source_id: int | None = None,
        target_id: int | None = None,
        min_weight: float | None = None,
    ) -> SynapsePage:
        """Return one paginated page of real synapse records.

        Each synapse record contains source_id, target_id, weight, delay,
        and eligibility (when available).
        """
        net = self.network
        limit = max(1, min(limit, _MAX_SYNAPSES_PER_PAGE))
        offset = max(0, offset)

        # Synapses stored as dict[int, list[Synapse]] keyed by presynaptic id.
        # Build a flat sorted list of (source_id, synapse) for stable pagination.
        # For large networks this is O(E); pagination avoids sending all at once.
        flat: list[tuple[int, Any]] = []
        for src_id, syn_list in net.synapses.items():
            if source_id is not None and src_id != source_id:
                continue
            for syn in syn_list:
                flat.append((src_id, syn))

        # Apply filters
        if target_id is not None or min_weight is not None:
            filtered: list[tuple[int, Any]] = []
            for src_id, syn in flat:
                if target_id is not None:
                    tgt = getattr(syn, "target_id", None)
                    if tgt != target_id:
                        continue
                if min_weight is not None:
                    w = getattr(syn, "weight", 0.0)
                    if w < min_weight:
                        continue
                filtered.append((src_id, syn))
            flat = filtered

        # Sort by (source_id, target_id) for stable pagination.
        flat.sort(key=lambda pair: (pair[0], getattr(pair[1], "target_id", 0)))

        total = len(flat)
        page = flat[offset : offset + limit]

        synapses: list[JSONValue] = []
        for src_id, syn in page:
            synapses.append(
                {
                    "source_id": src_id,
                    "target_id": getattr(syn, "target_id", None),
                    "weight": getattr(syn, "weight", None),
                    "delay": getattr(syn, "delay", None),
                    "eligibility": getattr(syn, "eligibility", None),
                    "age": getattr(syn, "age", None),
                }
            )

        return SynapsePage(
            synapses=synapses,
            total=total,
            offset=offset,
            limit=limit,
            returned=len(synapses),
            source="live_runtime",
        )

    # ------------------------------------------------------------------------
    # 5D → 3D Projection
    # ------------------------------------------------------------------------

    def projection(
        self,
        *,
        limit: int = _MAX_PROJECTION_SAMPLES,
        mode: str = "activity",
    ) -> ProjectionPayload:
        """Build a real 5D→3D projection by sampling live neurons.

        The projection maps the first three dimensions (x, y, z) to visible
        3D space axes. Dimensions 4 and 5 (d4, d5) are carried as filter
        attributes so the frontend can colour/size/layer them interactively.

        Args:
            limit: Maximum number of sampled points.
            mode: Projection mode: "activity" (colour by spike_count),
                "energy" (colour by energy), or "potential" (colour by v).
        """
        net = self.network
        limit = max(1, min(limit, _MAX_PROJECTION_SAMPLES))

        items = list(net.neurons.items())
        total = len(items)

        # Stride sampling for a deterministic, representative subset.
        if total > limit:
            stride = total / limit
            sampled = [items[int(i * stride)] for i in range(limit)]
            method = f"stride sampling (1/{stride:.2f})"
        else:
            sampled = items
            method = "full population"

        points: list[JSONValue] = []
        for nid, n in sampled:
            x1, x2, x3, x4, x5 = unpack_coords(nid)
            if mode == "energy":
                value: float = n.energy
            elif mode == "potential":
                value = n.v
            else:  # "activity" default
                value = float(n.spike_counter)

            points.append(
                {
                    "neuron_id": nid,
                    "x": x1,
                    "y": x2,
                    "z": x3,
                    "d4": x4,
                    "d5": x5,
                    "value": value,
                    "is_input": nid in net.input_cells,
                    "is_output": nid in net.output_cells,
                }
            )

        return ProjectionPayload(
            points=points,
            sample_count=len(points),
            total_count=total,
            sampling_method=method,
            mode=mode,
            source="live_runtime",
        )
