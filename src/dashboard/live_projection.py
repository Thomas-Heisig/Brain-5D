"""Live runtime projection service for the Brain-5D dashboard.

This module provides a read-only projection service that queries the
in-memory NeuralNetwork directly — never from a .b5d snapshot file.
It is the authoritative source for the LIVE visualization mode.

Key design decisions:
1. Read-only — never mutates network state.
2. Bounded output — aggregation happens server-side.
3. No caching — every call reads fresh state (lightweight field access).
4. Source provenance — every response identifies itself as LIVE_RUNTIME.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol, TypeAlias

from src.dashboard.models import JSONValue


# ============================================================================
# Types
# ============================================================================


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


class NetworkAccess(Protocol):
    """Minimal network interface required for live projection."""

    @property
    def neurons(self) -> dict[int, NeuronAccess]: ...
    @property
    def synapses(self) -> dict[int, Sequence[Any]]: ...
    @property
    def current_tick(self) -> int: ...
    @property
    def dimensions(self) -> tuple[int, int, int, int, int]: ...


# ============================================================================
# Projection kinds
# ============================================================================


class ProjectionKind:
    """Canonical live projection kind identifiers."""

    ACTIVITY = "activity"
    ENERGY = "energy"
    MEMBRANE = "membrane"
    SPIKE = "spike"
    WEIGHT = "weight"


_VALID_KINDS = frozenset({
    ProjectionKind.ACTIVITY,
    ProjectionKind.ENERGY,
    ProjectionKind.MEMBRANE,
    ProjectionKind.SPIKE,
    ProjectionKind.WEIGHT,
})


# ============================================================================
# Aggregation methods
# ============================================================================


class Aggregation:
    """Canonical aggregation method identifiers."""

    MEAN = "mean"
    MAX = "max"
    SUM = "sum"
    SPIKE_COUNT = "spike_count"
    ACTIVE_FRACTION = "active_fraction"


_VALID_AGGREGATIONS = frozenset({
    Aggregation.MEAN,
    Aggregation.MAX,
    Aggregation.SUM,
    Aggregation.SPIKE_COUNT,
    Aggregation.ACTIVE_FRACTION,
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
        kind: The projection kind (activity, energy, membrane, spike, weight).
        dimensions: The network's 5D dimensions.
        projection: Projection metadata (axes, aggregation, bins).
        range: Value range metadata (min, max, mean).
        sample_count: Number of neurons sampled.
        values: 2D array of aggregated values.
    """

    source: str = "live_runtime"
    tick: int = 0
    kind: str = ""
    dimensions: tuple[int, int, int, int, int] = (0, 0, 0, 0, 0)
    projection: dict[str, object] = field(default_factory=dict)
    range: dict[str, float] = field(default_factory=dict)
    sample_count: int = 0
    values: list[list[float]] = field(default_factory=list)

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "source": self.source,
            "tick": self.tick,
            "kind": self.kind,
            "dimensions": list(self.dimensions),
            "projection": {
                k: v for k, v in self.projection.items()
            },
            "range": {
                k: v for k, v in self.range.items()
            },
            "sample_count": self.sample_count,
            "values": [list(row) for row in self.values],
        }


# ============================================================================
# Live projection service
# ============================================================================


class LiveProjectionService:
    """Read-only live projection service for the dashboard.

    Queries the in-memory NeuralNetwork directly. Never reads from
    .b5d snapshots. Every response is tagged as ``live_runtime``.

    The service is designed to be lightweight — it reads neuron and
    synapse state with simple field access, no disk I/O.

    Example:
        >>> service = LiveProjectionService(network)
        >>> proj = service.project(kind="energy", dim_x=0, dim_y=1, bins=20)
        >>> proj.source
        'live_runtime'
    """

    def __init__(self, network: NetworkAccess, activity_window_ticks: int = 20) -> None:
        """Initialize the live projection service.

        Args:
            network: The live NeuralNetwork instance.
            activity_window_ticks: Time window for spike-rate activity
                computation. Default 20 ticks.
        """
        self.network = network
        self.activity_window_ticks = activity_window_ticks

    # ========================================================================
    # Public API
    # ========================================================================

    def project(
        self,
        kind: str,
        dim_x: int = 0,
        dim_y: int = 1,
        bins: int = 50,
        aggregation: str = Aggregation.MEAN,
    ) -> LiveProjection:
        """Compute a 5D→2D aggregated projection from live runtime state.

        Args:
            kind: Projection kind. One of: activity, energy, membrane,
                spike, weight.
            dim_x: Index of the first projection axis (0-4).
            dim_y: Index of the second projection axis (0-4).
            bins: Number of bins per axis (default 50, max 200).
            aggregation: Aggregation method. One of: mean, max, sum,
                spike_count, active_fraction.

        Returns:
            A LiveProjection with bounded 2D values.

        Raises:
            ValueError: If kind is unknown or parameters are invalid.
        """
        if kind not in _VALID_KINDS:
            raise ValueError(
                f"Unknown projection kind: {kind!r}. "
                f"Valid: {sorted(_VALID_KINDS)}"
            )
        if aggregation not in _VALID_AGGREGATIONS:
            raise ValueError(
                f"Unknown aggregation: {aggregation!r}. "
                f"Valid: {sorted(_VALID_AGGREGATIONS)}"
            )
        bins = max(5, min(200, bins))

        dims = self.network.dimensions
        dim_size_x = dims[dim_x]
        dim_size_y = dims[dim_y]

        # Initialize bins
        sums: list[list[float]] = [[0.0] * bins for _ in range(bins)]
        counts: list[list[int]] = [[0] * bins for _ in range(bins)]

        sample_count = 0
        global_min = float("inf")
        global_max = float("-inf")

        # Determine which raw values to extract
        if kind == ProjectionKind.WEIGHT:
            sample_count, global_min, global_max = self._project_weights(
                dim_x, dim_y, dim_size_x, dim_size_y, bins, aggregation, sums, counts
            )
        else:
            sample_count, global_min, global_max = self._project_neurons(
                kind, dim_x, dim_y, dim_size_x, dim_size_y, bins, aggregation, sums, counts
            )

        # Compute final bin values
        values: list[list[float]] = []
        current_min = float("inf")
        current_max = float("-inf")
        total = 0.0
        n = 0

        for y in range(bins):
            row: list[float] = []
            for x in range(bins):
                if counts[y][x] > 0:
                    val = sums[y][x] / counts[y][x]
                else:
                    val = 0.0
                row.append(val)
                if val < current_min:
                    current_min = val
                if val > current_max:
                    current_max = val
                total += val
                n += 1
            values.append(row)

        mean_val = total / n if n > 0 else 0.0
        if current_min == float("inf"):
            current_min = 0.0
        if current_max == float("-inf"):
            current_max = 0.0

        return LiveProjection(
            source="live_runtime",
            tick=self.network.current_tick,
            kind=kind,
            dimensions=dims,
            projection={
                "axes": [f"dim_{dim_x}", f"dim_{dim_y}"],
                "aggregation": aggregation,
                "bins": bins,
            },
            range={
                "min": current_min,
                "max": current_max,
                "mean": mean_val,
            },
            sample_count=sample_count,
            values=values,
        )

    # ========================================================================
    # Internal: neuron projection
    # ========================================================================

    def _project_neurons(
        self,
        kind: str,
        dim_x: int,
        dim_y: int,
        dim_size_x: int,
        dim_size_y: int,
        bins: int,
        aggregation: str,
        sums: list[list[float]],
        counts: list[list[int]],
    ) -> tuple[int, float, float]:
        """Project per-neuron values into 2D bins."""
        sample_count = 0
        global_min = float("inf")
        global_max = float("-inf")

        for neuron_id, neuron in self.network.neurons.items():
            # Extract 5D coordinates from neuron_id
            coords = self._unpack_coord(neuron_id, self.network.dimensions)
            x_coord = coords[dim_x]
            y_coord = coords[dim_y]

            bin_x = min(bins - 1, int(x_coord * bins / max(1, dim_size_x)))
            bin_y = min(bins - 1, int(y_coord * bins / max(1, dim_size_y)))

            value = self._neuron_value(kind, neuron)
            if math.isnan(value) or math.isinf(value):
                continue

            if aggregation == Aggregation.MAX:
                if value > sums[bin_y][bin_x]:
                    sums[bin_y][bin_x] = value
                    counts[bin_y][bin_x] = 1
            elif aggregation == Aggregation.ACTIVE_FRACTION:
                if kind == ProjectionKind.SPIKE:
                    is_active = 1.0 if value > 0 else 0.0
                else:
                    is_active = 1.0 if value > 0.5 else 0.0
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

    def _neuron_value(self, kind: str, neuron: NeuronAccess) -> float:
        """Extract the raw value from a neuron for the given kind."""
        if kind == ProjectionKind.ENERGY:
            return neuron.energy
        if kind == ProjectionKind.MEMBRANE:
            return neuron.v
        if kind == ProjectionKind.SPIKE:
            return float(neuron.spike_counter)
        if kind == ProjectionKind.ACTIVITY:
            # Firing rate over the activity window
            age = max(0, self.network.current_tick - neuron.last_spike_tick)
            if age > self.activity_window_ticks:
                return 0.0
            return 1.0 / max(1, age)
        return 0.0

    # ========================================================================
    # Internal: weight projection
    # ========================================================================

    def _project_weights(
        self,
        dim_x: int,
        dim_y: int,
        dim_size_x: int,
        dim_size_y: int,
        bins: int,
        aggregation: str,
        sums: list[list[float]],
        counts: list[list[int]],
    ) -> tuple[int, float, float]:
        """Project synaptic weights into 2D bins (mean outgoing per source).

        Weights are edges, not neuron properties. This projection maps
        mean outgoing weight to each source neuron's (x, y) bin.
        """
        sample_count = 0
        global_min = float("inf")
        global_max = float("-inf")

        # Build per-neuron outgoing weight aggregates
        neuron_weight_sum: dict[int, float] = {}
        neuron_weight_count: dict[int, int] = {}
        for source_id, synapses in self.network.synapses.items():
            total = 0.0
            n = 0
            for syn in synapses:
                w = self._synapse_weight(syn)
                total += w
                n += 1
            neuron_weight_sum[source_id] = total
            neuron_weight_count[source_id] = n

        for neuron_id in self.network.neurons:
            coords = self._unpack_coord(neuron_id, self.network.dimensions)
            x_coord = coords[dim_x]
            y_coord = coords[dim_y]

            bin_x = min(bins - 1, int(x_coord * bins / max(1, dim_size_x)))
            bin_y = min(bins - 1, int(y_coord * bins / max(1, dim_size_y)))

            wsum = neuron_weight_sum.get(neuron_id, 0.0)
            wcount = neuron_weight_count.get(neuron_id, 0)
            value = wsum / max(1, wcount)

            if aggregation == Aggregation.MAX:
                if value > sums[bin_y][bin_x]:
                    sums[bin_y][bin_x] = value
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

    @staticmethod
    def _synapse_weight(synapse: Any) -> float:
        """Extract weight from a synapse-like object."""
        if hasattr(synapse, "weight"):
            return float(synapse.weight)
        return 0.0

    @staticmethod
    def _unpack_coord(neuron_id: int, dims: tuple[int, int, int, int, int]) -> tuple[int, ...]:
        """Extract 5D coordinates from a packed neuron ID.

        Uses the canonical linear_to_5d decomposition.
        """
        remaining = neuron_id
        coords: list[int] = []
        for d in reversed(dims):
            coords.insert(0, remaining % d)
            remaining //= d
        return tuple(coords)
