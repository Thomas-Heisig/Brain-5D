"""Live runtime projection service for the Brain-5D dashboard.

This module provides a read-only projection service that queries the
in-memory NeuralNetwork directly — never from a .b5d snapshot file.
It is the authoritative source for the LIVE visualization mode.

Key design decisions:
1. Read-only — never mutates network state.
2. Bounded output — aggregation happens server-side.
3. No caching — every call reads fresh state (lightweight field access).
4. Source provenance — every response identifies itself as LIVE_RUNTIME.
5. TelemetryFrame — atomically captured tick snapshot to avoid incoherent
   reads across a concurrently stepping simulation.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Protocol, cast

from src.core.spatial_index import unpack_coords
from src.dashboard.models import JSONValue


class NeuronAccess(Protocol):
    """Minimal neuron interface required for live projection."""
    @property
    def v(self) -> float: ...
    @property
    def u(self) -> float: ...
    @property
    def energy(self) -> float: ...
    @property
    def spike_counter(self) -> int: ...
    @property
    def last_spike_tick(self) -> int: ...


class SynapseAccess(Protocol):
    """Minimal synapse interface required for live projection."""
    @property
    def weight(self) -> float: ...
    @property
    def target_id(self) -> int: ...


class NetworkAccess(Protocol):
    """Minimal network interface required for live projection."""
    @property
    def neurons(self) -> Mapping[int, NeuronAccess]: ...
    @property
    def synapses(self) -> Mapping[int, Sequence[SynapseAccess]]: ...
    @property
    def current_tick(self) -> int: ...
    @property
    def dimensions(self) -> tuple[int, int, int, int, int]: ...


# ============================================================================
# Telemetry Frame — atomic tick snapshot
# ============================================================================


@dataclass(frozen=True, slots=True)
class TelemetryFrame:
    """Atomically captured tick snapshot for coherent dashboard reads.

    Captures all data needed for a single projection from one tick,
    so the dashboard never sees a partially-updated network.
    """
    tick: int
    neurons: tuple[tuple[int, float, float, float, int, int, int], ...]
    synapses: tuple[tuple[int, int, float], ...]
    dimensions: tuple[int, int, int, int, int]


def capture_frame(network: NetworkAccess, prev_spike_counters: dict[int, int] | None = None) -> TelemetryFrame:
    """Capture a telemetry frame from the live network.

    Args:
        network: The live network to capture from.
        prev_spike_counters: Previous spike_counter values per neuron ID.
            When provided, the frame includes spike_delta (spikes since
            last frame) instead of total spike_counter.

    Returns:
        A TelemetryFrame with neuron data.
    """
    tick = network.current_tick
    neurons = tuple(
        (
            nid, n.v, n.energy, n.u, n.spike_counter, n.last_spike_tick,
            n.spike_counter - prev_spike_counters.get(nid, 0)
            if prev_spike_counters is not None else 0,
        )
        for nid, n in sorted(network.neurons.items())
    )
    syns = tuple(
        (src_id, syn.target_id, syn.weight)
        for src_id, syns in sorted(network.synapses.items())
        for syn in syns
    )
    return TelemetryFrame(
        tick=tick, neurons=neurons, synapses=syns,
        dimensions=network.dimensions,
    )


# ============================================================================
# Telemetry Frame Store — post-tick hook for atomic frame capture
# ============================================================================


class TelemetryFrameStore:
    """Holds the latest TelemetryFrame, updated atomically after each tick.

    Designed to be called from a RuntimeController post-tick hook.
    The store tracks spike_counter deltas so the activity projection
    can compute firing rates from spikes-per-window without requiring
    per-neuron spike history in the core Neuron.

    Usage in main.py::

        store = TelemetryFrameStore()
        controller.add_hook(lambda tick, result: store.on_tick_complete(network))
    """

    def __init__(self) -> None:
        self._frame: TelemetryFrame | None = None
        self._prev_spike_counters: dict[int, int] = {}

    @property
    def latest_frame(self) -> TelemetryFrame | None:
        """Return the most recently captured frame, or None."""
        return self._frame

    def on_tick_complete(self, network: NetworkAccess) -> None:
        """Called after each network tick to atomically capture a frame.

        This runs in the controller's simulation thread, immediately after
        ``network.step()`` completes. The frame captures state from a
        single, just-completed tick.
        """
        self._frame = capture_frame(network, self._prev_spike_counters)
        # Update previous counters for next delta computation
        self._prev_spike_counters = {
            nid: n.spike_counter
            for nid, n in network.neurons.items()
        }


# ============================================================================
# Projection kinds
# ============================================================================


class ProjectionKind:
    ACTIVITY = "activity"
    ENERGY = "energy"
    MEMBRANE = "membrane"
    SPIKE = "spike"
    WEIGHT = "weight"

_VALID_KINDS = frozenset({
    ProjectionKind.ACTIVITY, ProjectionKind.ENERGY,
    ProjectionKind.MEMBRANE, ProjectionKind.SPIKE,
    ProjectionKind.WEIGHT,
})


class Aggregation:
    MEAN = "mean"
    MAX = "max"
    SUM = "sum"
    SPIKE_COUNT = "spike_count"
    ACTIVE_FRACTION = "active_fraction"

_VALID_AGGREGATIONS = frozenset({
    Aggregation.MEAN, Aggregation.MAX, Aggregation.SUM,
    Aggregation.SPIKE_COUNT, Aggregation.ACTIVE_FRACTION,
})


# ============================================================================
# Response model
# ============================================================================


@dataclass(frozen=True, slots=True)
class LiveProjection:
    """Bounded, JSON-ready live projection response.

    Attributes:
        source: Always "live_runtime".
        tick: The network tick at query time.
        kind: The projection kind.
        dimensions: The network's 5D dimensions.
        projection: Projection metadata (axes, aggregation, bins).
        range: Value range metadata (min, max, mean) over non-empty bins only.
        sample_count: Number of neurons sampled.
        values: 2D array of aggregated values (null for empty bins).
        mask: 2D boolean array — true where bin has data.
    """
    source: str = "live_runtime"
    tick: int = 0
    kind: str = ""
    dimensions: tuple[int, int, int, int, int] = (0, 0, 0, 0, 0)
    projection: dict[str, object] = field(default_factory=dict)  # type: ignore[type-arg]
    range: dict[str, float] = field(default_factory=dict)  # type: ignore[type-arg]
    sample_count: int = 0
    values: list[list[float | None]] = field(default_factory=list)  # type: ignore[type-arg]
    mask: list[list[bool]] = field(default_factory=list)  # type: ignore[type-arg]

    def to_json(self) -> dict[str, JSONValue]:
        return cast("dict[str, JSONValue]", {
            "source": self.source,
            "tick": self.tick,
            "kind": self.kind,
            "dimensions": list(self.dimensions),
            "projection": dict(self.projection),
            "range": dict(self.range),
            "sample_count": self.sample_count,
            "values": [list(row) for row in self.values],
            "mask": [list(row) for row in self.mask],
        })


# ============================================================================
# Live projection service
# ============================================================================


class LiveProjectionService:
    """Read-only live projection service for the dashboard.

    Queries the in-memory NeuralNetwork directly via TelemetryFrame.
    Never reads from .b5d snapshots.
    """

    def __init__(self, network: NetworkAccess, activity_window_ticks: int = 20,
                 frame_store: TelemetryFrameStore | None = None) -> None:
        self.network = network
        self.activity_window_ticks = activity_window_ticks
        self._frame_store = frame_store

    # ========================================================================
    # Public API
    # ========================================================================

    def project(
        self,
        kind: str = "activity",
        dim_x: int = 0,
        dim_y: int = 1,
        bins: int = 50,
        aggregation: str = Aggregation.MEAN,
    ) -> LiveProjection:
        if kind not in _VALID_KINDS:
            raise ValueError(
                f"Unknown projection kind: {kind!r}. Valid: {sorted(_VALID_KINDS)}"
            )
        if aggregation not in _VALID_AGGREGATIONS:
            raise ValueError(
                f"Unknown aggregation: {aggregation!r}. Valid: {sorted(_VALID_AGGREGATIONS)}"
            )
        if dim_x == dim_y:
            raise ValueError(f"dim_x ({dim_x}) and dim_y ({dim_y}) must differ")
        if not (0 <= dim_x <= 4) or not (0 <= dim_y <= 4):
            raise ValueError(f"dimensions must be 0..4, got dim_x={dim_x}, dim_y={dim_y}")

        bins = max(5, min(200, bins))

        # Read the latest telemetry frame (from store or direct capture)
        frame = self._get_frame()
        dims = frame.dimensions
        dim_size_x = dims[dim_x]
        dim_size_y = dims[dim_y]

        # Bin accumulators
        sums: list[list[float]] = [[0.0] * bins for _ in range(bins)]
        max_vals: list[list[float]] = [[float("-inf")] * bins for _ in range(bins)]
        counts: list[list[int]] = [[0] * bins for _ in range(bins)]

        sample_count = 0

        if kind == ProjectionKind.WEIGHT:
            sample_count, _, _ = self._project_weights(
                frame, dim_x, dim_y, dim_size_x, dim_size_y,
                bins, aggregation, sums, max_vals, counts,
            )
        else:
            sample_count, _, _ = self._project_neurons(
                frame, kind, dim_x, dim_y, dim_size_x, dim_size_y,
                bins, aggregation, sums, max_vals, counts,
            )

        # Build final values with null for empty bins
        values: list[list[float | None]] = []
        mask: list[list[bool]] = []
        current_min = float("inf")
        current_max = float("-inf")
        total = 0.0
        n = 0

        for y in range(bins):
            row: list[float | None] = []
            row_mask: list[bool] = []
            for x in range(bins):
                if counts[y][x] > 0:
                    val = self._final_value(aggregation, sums[y][x], max_vals[y][x], counts[y][x])
                    row.append(val)
                    row_mask.append(True)
                    if val < current_min:
                        current_min = val
                    if val > current_max:
                        current_max = val
                    total += val
                    n += 1
                else:
                    row.append(None)
                    row_mask.append(False)
            values.append(row)
            mask.append(row_mask)

        mean_val = total / n if n > 0 else 0.0
        if current_min == float("inf"):
            current_min = 0.0
        if current_max == float("-inf"):
            current_max = 0.0

        return LiveProjection(
            source="live_runtime",
            tick=frame.tick,
            kind=kind,
            dimensions=dims,
            projection={
                "axes": [f"dim_{dim_x}", f"dim_{dim_y}"],
                "aggregation": aggregation,
                "bins": bins,
            },
            range={"min": current_min, "max": current_max, "mean": mean_val},
            sample_count=sample_count,
            values=values,
            mask=mask,
        )

    @staticmethod
    def _final_value(aggregation: str, s: float, m: float, c: int) -> float:
        """Compute the final bin value from accumulators."""
        if aggregation == Aggregation.SUM or aggregation == Aggregation.SPIKE_COUNT:
            return s
        if aggregation == Aggregation.MAX:
            return m
        if aggregation == Aggregation.ACTIVE_FRACTION:
            return s / c if c > 0 else 0.0
        # mean (default)
        return s / c

    # ========================================================================
    # Internal: neuron projection (from TelemetryFrame)
    # ========================================================================

    def _project_neurons(
        self,
        frame: TelemetryFrame,
        kind: str,
        dim_x: int, dim_y: int,
        dim_size_x: int, dim_size_y: int,
        bins: int,
        aggregation: str,
        sums: list[list[float]],
        max_vals: list[list[float]],
        counts: list[list[int]],
    ) -> tuple[int, float, float]:
        sample_count = 0
        global_min = float("inf")
        global_max = float("-inf")

        for nid, v, energy, u, spike_counter, last_spike_tick, spike_delta in frame.neurons:
            coords = unpack_coords(nid)
            x_coord = coords[dim_x]
            y_coord = coords[dim_y]

            bin_x = min(bins - 1, int(x_coord * bins / max(1, dim_size_x)))
            bin_y = min(bins - 1, int(y_coord * bins / max(1, dim_size_y)))

            value = self._neuron_value(kind, v, energy, spike_counter, last_spike_tick, frame.tick, spike_delta)
            _ = u  # keep linter happy; u is available for future use
            if math.isnan(value) or math.isinf(value):
                continue

            if aggregation == Aggregation.MAX:
                if value > max_vals[bin_y][bin_x]:
                    max_vals[bin_y][bin_x] = value
                    counts[bin_y][bin_x] = 1
            elif aggregation == Aggregation.ACTIVE_FRACTION:
                is_active = 1.0 if value > 0.0 else 0.0
                sums[bin_y][bin_x] += is_active
                counts[bin_y][bin_x] += 1
            else:
                sums[bin_y][bin_x] += value
                counts[bin_y][bin_x] += 1

            if value < global_min:
                global_min = value
            if value > global_max:
                global_max = value
            sample_count += 1

        if global_min == float("inf"):
            global_min = 0.0
        if global_max == float("-inf"):
            global_max = 0.0

        return sample_count, global_min, global_max

    def _get_frame(self) -> TelemetryFrame:
        """Get the current telemetry frame.

        Reads from the TelemetryFrameStore if available, otherwise
        falls back to direct capture.
        """
        if self._frame_store is not None:
            frame = self._frame_store.latest_frame
            if frame is not None:
                return frame
        return capture_frame(self.network)

    def _neuron_value(
        self, kind: str,
        v: float, energy: float,
        spike_counter: int, last_spike_tick: int,
        current_tick: int,
        spike_delta: int = 0,
    ) -> float:
        """Extract the raw value from neuron fields for the given kind."""
        if kind == ProjectionKind.ENERGY:
            return energy
        if kind == ProjectionKind.MEMBRANE:
            return v
        if kind == ProjectionKind.SPIKE:
            return float(spike_counter)
        if kind == ProjectionKind.ACTIVITY:
            return self._firing_rate(spike_delta, current_tick)
        return 0.0

    def _firing_rate(self, spike_delta: int, current_tick: int) -> float:
        """Compute firing rate in spikes/tick over the activity window.

        Uses spike_delta (spikes since last frame capture) divided by
        the activity window. This is a rate in spikes/tick.
        For dt=1ms: 1 spike/tick = 1000 Hz.
        """
        window = self.activity_window_ticks
        if spike_delta == 0:
            return 0.0
        return spike_delta / window

    # ========================================================================
    # Internal: weight projection
    # ========================================================================

    def _project_weights(
        self,
        frame: TelemetryFrame,
        dim_x: int, dim_y: int,
        dim_size_x: int, dim_size_y: int,
        bins: int,
        aggregation: str,
        sums: list[list[float]],
        max_vals: list[list[float]],
        counts: list[list[int]],
    ) -> tuple[int, float, float]:
        """Project synaptic weights into 2D bins (mean outgoing per source)."""
        sample_count = 0
        global_min = float("inf")
        global_max = float("-inf")

        # Build per-neuron outgoing weight aggregates from frame
        neuron_weight_sum: dict[int, float] = {}
        neuron_weight_count: dict[int, int] = {}
        for src_id, _tgt_id, weight in frame.synapses:
            neuron_weight_sum[src_id] = neuron_weight_sum.get(src_id, 0.0) + weight
            neuron_weight_count[src_id] = neuron_weight_count.get(src_id, 0) + 1

        for nid, _v, _energy, _u, _spike_counter, _last_spike_tick, _spike_delta in frame.neurons:
            coords = unpack_coords(nid)
            x_coord = coords[dim_x]
            y_coord = coords[dim_y]

            bin_x = min(bins - 1, int(x_coord * bins / max(1, dim_size_x)))
            bin_y = min(bins - 1, int(y_coord * bins / max(1, dim_size_y)))

            wsum = neuron_weight_sum.get(nid, 0.0)
            wcount = neuron_weight_count.get(nid, 0)
            value = wsum / max(1, wcount)

            if aggregation == Aggregation.MAX:
                if value > max_vals[bin_y][bin_x]:
                    max_vals[bin_y][bin_x] = value
                    counts[bin_y][bin_x] = 1
            else:
                sums[bin_y][bin_x] += value
                counts[bin_y][bin_x] += 1

            if value < global_min:
                global_min = value
            if value > global_max:
                global_max = value
            sample_count += 1

        if global_min == float("inf"):
            global_min = 0.0
        if global_max == float("-inf"):
            global_max = 0.0

        return sample_count, global_min, global_max
