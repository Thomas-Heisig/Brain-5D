"""Live runtime projection service for the Brain-5D dashboard.

This module provides a read-only projection service that queries the
in-memory NeuralNetwork directly — never from a .b5d snapshot file.
It is the authoritative source for the LIVE visualization mode.

Key design decisions:
1. Read-only — never mutates network state.
2. Bounded output — aggregation happens server-side.
3. Source provenance — every response identifies itself as LIVE_RUNTIME.
4. TelemetryFrameStore — post-tick hook captures immutable frames at a
   configurable cadence.
5. ActivityWindowAccumulator — true rolling N-tick spike count with
   O(spikes_this_tick) per-tick complexity. No per-neuron history in Neuron.
"""

from __future__ import annotations

import math
import threading
import time
from collections import deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol, cast

from src.core.spatial_index import unpack_coords
from src.dashboard.models import JSONValue

if TYPE_CHECKING:
    from src.controller.runtime import PostTickHook


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
    @property
    def is_inhibitory(self) -> bool: ...


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
# Activity Window Accumulator
# ============================================================================


class ActivityWindowAccumulator:
    """True rolling N-tick spike count accumulator.

    Per-tick complexity: O(spikes_this_tick) — only neurons that actually
    spiked are touched. No per-neuron history stored in Neuron.

    Maintains a deque of (tick, spike_ids) entries. On each tick:
    1. Expire entries whose tick <= current_tick - window_ticks
    2. Decrement their neuron counts
    3. Record current spike_ids
    4. Increment current counts

    Example:
        >>> acc = ActivityWindowAccumulator(window_ticks=20)
        >>> acc.record_tick(100, [1, 2, 3])
        >>> acc.spikes_in_window(1)
        1
        >>> acc.firing_rate(1)
        0.05
    """

    def __init__(self, window_ticks: int = 20) -> None:
        if window_ticks <= 0:
            raise ValueError(f"window_ticks must be > 0, got {window_ticks}")
        self.window_ticks = window_ticks
        self._window: deque[tuple[int, tuple[int, ...]]] = deque()
        self._counts: dict[int, int] = {}

    @property
    def total_spikes(self) -> int:
        """Total spikes across all neurons in the current window."""
        return sum(self._counts.values())

    @property
    def current_window_size(self) -> int:
        """Number of ticks currently in the window."""
        return len(self._window)

    def reset(self) -> None:
        """Clear all accumulated data."""
        self._window.clear()
        self._counts.clear()

    def record_tick(self, tick: int, spike_ids: Sequence[int]) -> None:
        """Record spike_ids for one tick and advance the window.

        Args:
            tick: Current simulation tick.
            spike_ids: IDs of neurons that spiked this tick.
        """
        # Expire entries outside the window
        cutoff = tick - self.window_ticks
        while self._window and self._window[0][0] <= cutoff:
            _expired_tick, expired_ids = self._window.popleft()  # noqa: F841
            for nid in expired_ids:
                if nid in self._counts:
                    self._counts[nid] -= 1
                    if self._counts[nid] <= 0:
                        del self._counts[nid]

        # Record this tick
        ids_tuple = tuple(spike_ids)
        self._window.append((tick, ids_tuple))
        for nid in ids_tuple:
            self._counts[nid] = self._counts.get(nid, 0) + 1

    def spikes_in_window(self, neuron_id: int) -> int:
        """Return the spike count for a neuron in the current window."""
        return self._counts.get(neuron_id, 0)

    def firing_rate(self, neuron_id: int) -> float:
        """Return firing rate in spikes/tick for a neuron."""
        return self.spikes_in_window(neuron_id) / self.window_ticks


# ============================================================================
# Telemetry Frame
# ============================================================================


@dataclass(frozen=True, slots=True)
class TelemetryFrame:
    """Immutable tick snapshot for coherent dashboard reads.

    Captures all data needed for a single projection from one tick.
    The activity field contains per-neuron rolling window spike counts.
    """
    tick: int
    neurons: tuple[tuple[int, float, float, float, int, int], ...]
    synapses: tuple[tuple[int, int, float], ...]
    activity: tuple[tuple[int, int], ...]
    dimensions: tuple[int, int, int, int, int]
    activity_window_ticks: int = 20
    dt_ms: float = 1.0


# ============================================================================
# Frame capture
# ============================================================================


def capture_frame(
    network: NetworkAccess,
    activity_accumulator: ActivityWindowAccumulator | None = None,
    dt_ms: float = 1.0,
) -> TelemetryFrame:
    """Capture a telemetry frame from the live network.

    Args:
        network: The live network to capture from.
        activity_accumulator: Optional rolling activity accumulator.
            When provided, the frame includes per-neuron window spike counts.
        dt_ms: Simulation time step in milliseconds. Default 1.0.

    Returns:
        A TelemetryFrame with neuron data.
    """
    tick = network.current_tick
    neurons = tuple(
        (nid, n.v, n.energy, n.u, n.spike_counter, n.last_spike_tick)
        for nid, n in sorted(network.neurons.items())
    )
    syns = tuple(
        (src_id, syn.target_id, syn.weight)
        for src_id, syns in sorted(network.synapses.items())
        for syn in syns
    )
    activity = tuple(
        (nid, activity_accumulator.spikes_in_window(nid))
        for nid, _ in sorted(network.neurons.items())
    ) if activity_accumulator is not None else ()
    window_ticks = activity_accumulator.window_ticks if activity_accumulator is not None else 20
    return TelemetryFrame(
        tick=tick, neurons=neurons, synapses=syns,
        activity=activity, dimensions=network.dimensions,
        activity_window_ticks=window_ticks,
        dt_ms=dt_ms,
    )


# ============================================================================
# Telemetry Frame Store — post-tick hook with cadence
# ============================================================================


class TelemetryFrameStore:
    """Holds the latest TelemetryFrame, updated at a configurable cadence.

    Architecture::

        EVERY TICK:
            ActivityWindowAccumulator.record_tick() — O(spikes_this_tick)

        EVERY capture_interval_ticks:
            Full neuron/synapse traversal — O(neurons + synapses)
            → immutable TelemetryFrame
            → atomically replace latest_frame

    Post-tick hook errors are routed through the structured error buffer
    as RuntimeErrorEvent(component=\"live_telemetry\", phase=\"post_tick_capture\").

    Usage::

        store = TelemetryFrameStore(capture_interval_ticks=50)
        controller.add_hook(lambda tick, result: store.on_tick_complete(network, result))
    """

    def __init__(
        self,
        capture_interval_ticks: int = 5,
        activity_window_ticks: int = 20,
    ) -> None:
        if capture_interval_ticks <= 0:
            raise ValueError(f"capture_interval_ticks must be > 0, got {capture_interval_ticks}")
        if capture_interval_ticks > activity_window_ticks:
            raise ValueError(
                f"capture_interval_ticks ({capture_interval_ticks}) must be <= "
                f"activity_window_ticks ({activity_window_ticks}) — "
                "otherwise spikes can expire before being captured in a frame"
            )
        self.capture_interval_ticks = capture_interval_ticks
        self.activity_window_ticks = activity_window_ticks
        self._lock = threading.RLock()
        self._frame: TelemetryFrame | None = None
        self._accumulator = ActivityWindowAccumulator(window_ticks=activity_window_ticks)
        self._ticks_observed: int = 0
        self._frames_captured: int = 0
        self._last_capture_duration_ms: float = 0.0
        self._last_observed_tick: int = 0
        self._dt_ms: float = 1.0

    @property
    def accumulator(self) -> ActivityWindowAccumulator:
        """Expose the internal accumulator for dashboard read access."""
        return self._accumulator

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def latest_frame(self) -> TelemetryFrame | None:
        """Return the most recently captured frame, or None if not yet primed."""
        with self._lock:
            return self._frame

    @property
    def stats(self) -> dict[str, object]:
        """Telemetry statistics (uses internal last_observed_tick as fallback)."""
        with self._lock:
            return self._stats_locked(self._last_observed_tick)

    def stats_at(self, runtime_tick: int) -> dict[str, object]:
        """Telemetry statistics relative to an authoritative runtime tick.

        Args:
            runtime_tick: The current network/controller tick. This is the
                authoritative reference for staleness — not the hook's own
                ``_last_observed_tick``, which would freeze if the hook fails.

        Returns:
            Stats dict with ``status`` (live/stale/unavailable) and
            ``frame_age_ticks`` computed against ``runtime_tick``.
        """
        with self._lock:
            return self._stats_locked(runtime_tick)

    def _stats_locked(self, runtime_tick: int) -> dict[str, object]:
        """Compute stats dict (caller must hold _lock).

        Args:
            runtime_tick: Authoritative tick for staleness computation.
        """
        frame_tick = self._frame.tick if self._frame else None
        frame_age = max(0, runtime_tick - frame_tick) if frame_tick is not None else 0
        if frame_tick is None:
            status = "unavailable"
        elif frame_age <= 2 * self.capture_interval_ticks:
            status = "live"
        else:
            status = "stale"
        return {
            "latest_frame_tick": frame_tick,
            "last_observed_tick": self._last_observed_tick,
            "runtime_tick": runtime_tick,
            "frame_age_ticks": frame_age,
            "status": status,
            "capture_interval_ticks": self.capture_interval_ticks,
            "activity_window_ticks": self.activity_window_ticks,
            "frames_captured": self._frames_captured,
            "ticks_observed": self._ticks_observed,
            "last_capture_duration_ms": self._last_capture_duration_ms,
        }

    # ------------------------------------------------------------------
    # Priming
    # ------------------------------------------------------------------

    def set_dt_ms(self, dt_ms: float) -> None:
        """Set the simulation dt_ms for Hz conversion."""
        self._dt_ms = dt_ms

    def prime(self, network: NetworkAccess) -> None:
        """Explicitly capture Tick-0 frame before simulation starts.

        Ensures /api/live/projection can respond before any tick executes.
        """
        with self._lock:
            self._frame = capture_frame(network, activity_accumulator=self._accumulator, dt_ms=self._dt_ms)
            self._frames_captured = 1

    # ------------------------------------------------------------------
    # Post-tick hook
    # ------------------------------------------------------------------

    def on_tick_complete(
        self,
        network: NetworkAccess,
        result: object,
    ) -> None:
        """Called after each network tick.

        Lightweight per-tick: updates the rolling activity window.
        Full frame capture only every capture_interval_ticks.

        Args:
            network: The live network.
            result: The StepResult from the completed tick.
        """
        tick = network.current_tick
        spike_ids = getattr(result, 'spike_ids', ())

        with self._lock:
            self._ticks_observed += 1
            self._last_observed_tick = tick
            self._accumulator.record_tick(tick, spike_ids)

            # Full frame capture only at cadence
            if self._ticks_observed % self.capture_interval_ticks == 0:
                start = time.perf_counter()
                self._frame = capture_frame(network, activity_accumulator=self._accumulator, dt_ms=self._dt_ms)
                self._last_capture_duration_ms = (time.perf_counter() - start) * 1000.0
                self._frames_captured += 1


# ============================================================================
# Error visibility — route telemetry hook exceptions to error buffer
# ============================================================================


def _emit_telemetry_error(tick: int, exception: Exception) -> None:
    """Emit a structured RuntimeErrorEvent for a telemetry hook failure.

    The error is non-fatal: scientific simulation continues.
    """
    import traceback

    from src.self_organization.runtime_adapter import (
        RuntimeErrorEvent,
        get_error_buffer,
    )

    tb_text = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
    import hashlib
    tb_hash = hashlib.sha256(tb_text.encode("utf-8")).hexdigest()

    event = RuntimeErrorEvent(
        timestamp=time.monotonic_ns(),
        tick=tick,
        component="live_telemetry",
        phase="post_tick_capture",
        exception_type=f"{type(exception).__module__}.{type(exception).__qualname__}",
        message=str(exception),
        fatal=False,
        traceback_hash=tb_hash,
    )
    get_error_buffer().push(event)


# ============================================================================
# Safe hook wrapper
# ============================================================================


def make_telemetry_hook(store: TelemetryFrameStore, network: NetworkAccess) -> PostTickHook:
    """Create a post-tick hook that safely calls the store.

    Exceptions are routed to the structured error buffer instead of
    being silently swallowed by RuntimeController's except Exception: pass.
    """
    def hook(tick: int, result: object) -> None:
        try:
            store.on_tick_complete(network, result)
        except Exception as exc:
            _emit_telemetry_error(tick, exc)
    return hook


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
        metric: Metric metadata (name, unit, window_ticks, etc.).
        range: Value range metadata (min, max, mean) over non-empty bins only.
        sample_count: Number of neurons sampled.
        values: 2D array of aggregated values (null for empty bins).
        mask: 2D boolean array — true where bin has data.
        telemetry: Telemetry statistics (cadence, frames, etc.).
    """
    source: str = "live_runtime"
    tick: int = 0
    kind: str = ""
    dimensions: tuple[int, int, int, int, int] = (0, 0, 0, 0, 0)
    projection: dict[str, object] = field(default_factory=dict)  # type: ignore[type-arg]
    metric: dict[str, object] = field(default_factory=dict)  # type: ignore[type-arg]
    range: dict[str, float] = field(default_factory=dict)  # type: ignore[type-arg]
    sample_count: int = 0
    values: list[list[float | None]] = field(default_factory=list)  # type: ignore[type-arg]
    mask: list[list[bool]] = field(default_factory=list)  # type: ignore[type-arg]
    telemetry: dict[str, object] = field(default_factory=dict)  # type: ignore[type-arg]

    def to_json(self) -> dict[str, JSONValue]:
        return cast("dict[str, JSONValue]", {
            "source": self.source,
            "tick": self.tick,
            "kind": self.kind,
            "dimensions": list(self.dimensions),
            "projection": dict(self.projection),
            "metric": dict(self.metric),
            "range": dict(self.range),
            "sample_count": self.sample_count,
            "values": [list(row) for row in self.values],
            "mask": [list(row) for row in self.mask],
            "telemetry": dict(self.telemetry),
        })


# ============================================================================
# Live projection service
# ============================================================================


class LiveProjectionService:
    """Read-only live projection service for the dashboard.

    Reads from TelemetryFrameStore when available.
    Falls back to direct capture ONLY when no store is configured
    (isolated unit tests). Production path always uses the store.
    """

    def __init__(
        self,
        network: NetworkAccess,
        frame_store: TelemetryFrameStore | None = None,
    ) -> None:
        self.network = network
        self.frame_store = frame_store
        self._current_window_ticks: int = 20

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

        # Read from store or direct capture — ONE frame per projection
        frame = self._get_frame()
        self._current_window_ticks = frame.activity_window_ticks
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

        # Metric metadata — derived exclusively from the frame/store
        _window_ticks = frame.activity_window_ticks
        _dt_ms = frame.dt_ms
        window_ms = _window_ticks * _dt_ms
        metric_info: dict[str, object] = {
            "name": kind,
            "window_ticks": _window_ticks,
            "window_ms": window_ms,
        }
        if kind == ProjectionKind.ACTIVITY:
            metric_info["unit"] = "spikes/tick"
            metric_info["unit_hz"] = f"spikes/tick * 1000/{_dt_ms} Hz"

        # Telemetry stats — use network.current_tick for authoritative staleness
        telemetry_stats: dict[str, object] = {}
        if self.frame_store is not None:
            telemetry_stats = dict(self.frame_store.stats_at(self.network.current_tick))

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
            metric=metric_info,
            range={"min": current_min, "max": current_max, "mean": mean_val},
            sample_count=sample_count,
            values=values,
            mask=mask,
            telemetry=telemetry_stats,
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

        # Build a lookup of neuron_id -> spikes_in_window from frame.activity
        activity_map: dict[int, int] = dict(frame.activity)

        for nid, v, energy, u, spike_counter, last_spike_tick in frame.neurons:
            coords = unpack_coords(nid)
            x_coord = coords[dim_x]
            y_coord = coords[dim_y]

            bin_x = min(bins - 1, int(x_coord * bins / max(1, dim_size_x)))
            bin_y = min(bins - 1, int(y_coord * bins / max(1, dim_size_y)))

            value = self._neuron_value(kind, v, energy, spike_counter, last_spike_tick, frame.tick, activity_map.get(nid, 0))
            _ = u
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

        Reads from the TelemetryFrameStore when configured (production).
        Falls back to direct capture ONLY for isolated unit tests
        (no store configured).
        """
        if self.frame_store is not None:
            frame = self.frame_store.latest_frame
            if frame is not None:
                return frame
            raise RuntimeError(
                "TelemetryFrameStore configured but has no frame. "
                "Ensure store.prime() is called before first project()."
            )
        # Direct capture fallback — only for unit tests without a store
        return capture_frame(self.network)

    def _neuron_value(
        self, kind: str,
        v: float, energy: float,
        spike_counter: int, last_spike_tick: int,
        current_tick: int,
        spikes_in_window: int = 0,
    ) -> float:
        """Extract the raw value from neuron fields for the given kind."""
        if kind == ProjectionKind.ENERGY:
            return energy
        if kind == ProjectionKind.MEMBRANE:
            return v
        if kind == ProjectionKind.SPIKE:
            return float(spike_counter)
        if kind == ProjectionKind.ACTIVITY:
            return spikes_in_window / self._current_window_ticks
        return 0.0

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

        for nid, _v, _energy, _u, _spike_counter, _last_spike_tick in frame.neurons:
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


# ============================================================================
# IO Flow analysis
# ============================================================================


@dataclass(frozen=True, slots=True)
class IOFlowResult:
    """Input-output signal flow analysis result.

    Exposes both the canonical input/output totals and the input/hidden/output
    breakdown that the dashboard UI renders.
    """
    input_rate: float
    output_rate: float
    total_input_spikes: int
    total_output_spikes: int
    current_tick: int
    input_count: int = 0
    hidden_count: int = 0
    output_count: int = 0
    input_mean_rate: float = 0.0
    hidden_mean_rate: float = 0.0
    output_mean_rate: float = 0.0
    propagation_active: bool = False
    source: str = "live_runtime"

    def to_json(self) -> dict[str, JSONValue]:
        return cast("dict[str, JSONValue]", {
            "input_rate": self.input_rate,
            "output_rate": self.output_rate,
            "total_input_spikes": self.total_input_spikes,
            "total_output_spikes": self.total_output_spikes,
            "current_tick": self.current_tick,
            "input_count": self.input_count,
            "hidden_count": self.hidden_count,
            "output_count": self.output_count,
            "input_mean_rate": self.input_mean_rate,
            "hidden_mean_rate": self.hidden_mean_rate,
            "output_mean_rate": self.output_mean_rate,
            "propagation_active": self.propagation_active,
            "source": self.source,
        })


def compute_io_flow(
    network: NetworkAccess,
    accumulator: ActivityWindowAccumulator | None = None,
) -> IOFlowResult:
    """Compute input-output signal flow analysis.

    Splits neurons into input / hidden / output populations based on the
    network's ``input_cells`` / ``output_cells`` sets. The hidden population
    is everything that is neither input nor output.
    """
    input_cells = getattr(network, "input_cells", set())
    output_cells = getattr(network, "output_cells", set())

    total_input = 0
    total_hidden = 0
    total_output = 0
    input_count = 0
    hidden_count = 0
    output_count = 0

    for nid, neuron in network.neurons.items():
        spike_count = int(neuron.spike_counter)
        if nid in input_cells:
            total_input += spike_count
            input_count += 1
        elif nid in output_cells:
            total_output += spike_count
            output_count += 1
        else:
            total_hidden += spike_count
            hidden_count += 1

    tick = max(network.current_tick, 1)
    propagation_active = total_input > 0 or total_output > 0

    return IOFlowResult(
        input_rate=total_input / tick,
        output_rate=total_output / tick,
        total_input_spikes=total_input,
        total_output_spikes=total_output,
        current_tick=network.current_tick,
        input_count=input_count,
        hidden_count=hidden_count,
        output_count=output_count,
        input_mean_rate=total_input / max(input_count, 1),
        hidden_mean_rate=total_hidden / max(hidden_count, 1),
        output_mean_rate=total_output / max(output_count, 1),
        propagation_active=propagation_active,
    )


# ============================================================================
# Population data
# ============================================================================


@dataclass(frozen=True, slots=True)
class PopulationResult:
    """Neuron population overview result.

    Provides both aggregate counts and the per-population cards the dashboard
    renders.
    """
    total_neurons: int
    excitatory_count: int
    inhibitory_count: int
    active_count: int
    mean_firing_rate: float
    current_tick: int
    populations: list[dict[str, object]] = field(default_factory=list)
    ei_ratio: float = 0.0
    total_excitatory: int = 0
    total_inhibitory: int = 0
    source: str = "live_runtime"

    def to_json(self) -> dict[str, JSONValue]:
        return cast("dict[str, JSONValue]", {
            "total_neurons": self.total_neurons,
            "excitatory_count": self.excitatory_count,
            "inhibitory_count": self.inhibitory_count,
            "active_count": self.active_count,
            "mean_firing_rate": self.mean_firing_rate,
            "current_tick": self.current_tick,
            "populations": cast(list[JSONValue], self.populations),
            "ei_ratio": self.ei_ratio,
            "total_excitatory": self.total_excitatory,
            "total_inhibitory": self.total_inhibitory,
            "source": self.source,
        })


def compute_population_data(
    network: NetworkAccess,
    accumulator: ActivityWindowAccumulator | None = None,
) -> PopulationResult:
    """Compute neuron population overview (E/I ratio, firing rates)."""
    total = len(network.neurons)
    excitatory = 0
    inhibitory = 0
    active = 0
    total_rate = 0.0

    excit_sum = 0.0
    excit_energy = 0.0
    excit_v = 0.0
    excit_active = 0
    excit_count = 0
    inhib_sum = 0.0
    inhib_energy = 0.0
    inhib_v = 0.0
    inhib_active = 0
    inhib_count = 0

    for neuron in network.neurons.values():
        rate = neuron.spike_counter / max(network.current_tick, 1)
        if neuron.is_inhibitory:
            inhibitory += 1
            inhib_count += 1
            inhib_sum += rate
            inhib_energy += neuron.energy
            inhib_v += neuron.v
            if neuron.spike_counter > 0:
                inhib_active += 1
                active += 1
        else:
            excitatory += 1
            excit_count += 1
            excit_sum += rate
            excit_energy += neuron.energy
            excit_v += neuron.v
            if neuron.spike_counter > 0:
                excit_active += 1
                active += 1
        total_rate += rate

    populations: list[dict[str, object]] = []
    if excit_count > 0:
        populations.append({
            "name": "excitatory",
            "count": excit_count,
            "mean_rate": excit_sum / excit_count,
            "mean_energy": excit_energy / excit_count,
            "mean_v": excit_v / excit_count,
            "active_count": excit_active,
            "active_fraction": excit_active / excit_count,
        })
    if inhib_count > 0:
        populations.append({
            "name": "inhibitory",
            "count": inhib_count,
            "mean_rate": inhib_sum / inhib_count,
            "mean_energy": inhib_energy / inhib_count,
            "mean_v": inhib_v / inhib_count,
            "active_count": inhib_active,
            "active_fraction": inhib_active / inhib_count,
        })

    tick = max(network.current_tick, 1)
    ei_ratio = excitatory / max(inhibitory, 1)
    return PopulationResult(
        total_neurons=total,
        excitatory_count=excitatory,
        inhibitory_count=inhibitory,
        active_count=active,
        mean_firing_rate=total_rate / tick / max(total, 1),
        current_tick=network.current_tick,
        populations=populations,
        ei_ratio=ei_ratio,
        total_excitatory=excitatory,
        total_inhibitory=inhibitory,
    )


# ============================================================================
# Rate histogram
# ============================================================================


@dataclass(frozen=True, slots=True)
class RateHistogramResult:
    """Firing rate distribution histogram result."""
    bins: list[float]
    counts: list[int]
    num_bins: int
    current_tick: int
    mean_rate: float = 0.0
    std_rate: float = 0.0
    median_rate: float = 0.0
    active_count: int = 0
    silent_count: int = 0
    source: str = "live_runtime"

    def to_json(self) -> dict[str, JSONValue]:
        return cast("dict[str, JSONValue]", {
            "bins": self.bins,
            "counts": self.counts,
            "num_bins": self.num_bins,
            "current_tick": self.current_tick,
            "mean_rate": self.mean_rate,
            "std_rate": self.std_rate,
            "median_rate": self.median_rate,
            "active_count": self.active_count,
            "silent_count": self.silent_count,
            "source": self.source,
        })


def compute_rate_histogram(
    network: NetworkAccess,
    accumulator: ActivityWindowAccumulator | None = None,
    num_bins: int = 30,
) -> RateHistogramResult:
    """Compute firing rate distribution histogram."""
    rates = [
        neuron.spike_counter / max(network.current_tick, 1)
        for neuron in network.neurons.values()
    ]
    active_count = sum(1 for r in rates if r > 0)
    silent_count = len(rates) - active_count

    if not rates:
        return RateHistogramResult(
            bins=[0.0] * num_bins,
            counts=[0] * num_bins,
            num_bins=num_bins,
            current_tick=network.current_tick,
            active_count=active_count,
            silent_count=silent_count,
        )

    mean_rate = sum(rates) / len(rates)
    variance = sum((r - mean_rate) ** 2 for r in rates) / len(rates)
    std_rate = math.sqrt(variance)
    sorted_rates = sorted(rates)
    median_rate = sorted_rates[len(sorted_rates) // 2] if sorted_rates else 0.0

    min_rate = min(rates)
    max_rate = max(rates)
    bin_width = (max_rate - min_rate) / num_bins if max_rate > min_rate else 1.0

    bin_edges = [min_rate + i * bin_width for i in range(num_bins + 1)]
    counts = [0] * num_bins

    for r in rates:
        idx = min(int((r - min_rate) / bin_width), num_bins - 1) if max_rate > min_rate else 0
        counts[idx] += 1

    bin_centres = [(bin_edges[i] + bin_edges[i + 1]) / 2 for i in range(num_bins)]

    return RateHistogramResult(
        bins=bin_centres,
        counts=counts,
        num_bins=num_bins,
        current_tick=network.current_tick,
        mean_rate=mean_rate,
        std_rate=std_rate,
        median_rate=median_rate,
        active_count=active_count,
        silent_count=silent_count,
    )


# ============================================================================
# Spike raster
# ============================================================================


@dataclass(frozen=True, slots=True)
class SpikeRasterResult:
    """Spike raster (recent spike history) result."""
    neuron_ids: list[int]
    spike_ticks: list[int]
    total_events: int
    current_tick: int
    total_neurons: int = 0
    sample_count: int = 0
    window_ticks: int = 100
    tick: int = 0
    source: str = "live_runtime"

    def to_json(self) -> dict[str, JSONValue]:
        return cast("dict[str, JSONValue]", {
            "neuron_ids": self.neuron_ids,
            "spike_ticks": self.spike_ticks,
            "total_events": self.total_events,
            "current_tick": self.current_tick,
            "total_neurons": self.total_neurons,
            "sample_count": self.sample_count,
            "window_ticks": self.window_ticks,
            "tick": self.tick,
            "source": self.source,
        })


def compute_spike_raster(
    network: NetworkAccess,
    accumulator: ActivityWindowAccumulator | None = None,
) -> SpikeRasterResult:
    """Compute spike raster data from recent spike history."""
    neuron_ids: list[int] = []
    spike_ticks: list[int] = []

    for nid, neuron in network.neurons.items():
        if neuron.spike_counter > 0:
            neuron_ids.append(nid)
            spike_ticks.append(neuron.last_spike_tick)

    window_ticks = accumulator.window_ticks if accumulator is not None else 100
    return SpikeRasterResult(
        neuron_ids=neuron_ids,
        spike_ticks=spike_ticks,
        total_events=len(neuron_ids),
        current_tick=network.current_tick,
        total_neurons=len(network.neurons),
        sample_count=len(neuron_ids),
        window_ticks=window_ticks,
        tick=network.current_tick,
    )
