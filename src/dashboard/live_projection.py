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
            _expired_tick, expired_ids = self._window.popleft()
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
    from src.self_organization.runtime_adapter import RuntimeErrorEvent, get_error_buffer

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


def make_telemetry_hook(store: TelemetryFrameStore, network: NetworkAccess):
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
# IO Flow Analysis
# ============================================================================


@dataclass(frozen=True, slots=True)
class IOFlowData:
    tick: int
    input_activity: tuple[tuple[int, float, tuple[int, int, int, int, int]], ...]
    output_activity: tuple[tuple[int, float, tuple[int, int, int, int, int]], ...]
    hidden_activity: tuple[tuple[int, float, tuple[int, int, int, int, int]], ...]
    input_mean_rate: float
    output_mean_rate: float
    hidden_mean_rate: float
    propagation_active: bool
    input_count: int
    output_count: int
    hidden_count: int
    source: str = "live_runtime"

    def to_json(self) -> dict[str, object]:
        return {
            "source": self.source,
            "tick": self.tick,
            "input_activity": [
                {"neuron_id": nid, "activity": act, "coord": list(c)}
                for nid, act, c in self.input_activity
            ],
            "output_activity": [
                {"neuron_id": nid, "activity": act, "coord": list(c)}
                for nid, act, c in self.output_activity
            ],
            "hidden_activity": [
                {"neuron_id": nid, "activity": act, "coord": list(c)}
                for nid, act, c in self.hidden_activity
            ],
            "input_mean_rate": self.input_mean_rate,
            "output_mean_rate": self.output_mean_rate,
            "hidden_mean_rate": self.hidden_mean_rate,
            "propagation_active": self.propagation_active,
            "input_count": self.input_count,
            "output_count": self.output_count,
            "hidden_count": self.hidden_count,
        }


def compute_io_flow(network, activity_accumulator=None):
    tick = network.current_tick
    input_activity = []
    output_activity = []
    hidden_activity = []
    input_sum = 0.0
    output_sum = 0.0
    hidden_sum = 0.0
    input_count = 0
    output_count = 0
    hidden_count = 0
    for nid, neuron in network.neurons.items():
        coords = unpack_coords(nid)
        if activity_accumulator is not None:
            act = activity_accumulator.firing_rate(nid)
        elif neuron.last_spike_tick >= 0:
            age = max(0, tick - neuron.last_spike_tick)
            act = float(__import__("numpy").exp(-age / 50.0))
        else:
            act = 0.0
        is_input = getattr(neuron, "is_input", False) or coords[0] == 0
        is_output = getattr(neuron, "is_output", False) or coords[0] == network.dimensions[0] - 1
        if is_input:
            input_activity.append((nid, act, coords))
            input_sum += act
            input_count += 1
        elif is_output:
            output_activity.append((nid, act, coords))
            output_sum += act
            output_count += 1
        else:
            hidden_activity.append((nid, act, coords))
            hidden_sum += act
            hidden_count += 1
    input_activity.sort(key=lambda x: x[1], reverse=True)
    output_activity.sort(key=lambda x: x[1], reverse=True)
    hidden_activity.sort(key=lambda x: x[1], reverse=True)
    max_per_layer = 200
    input_activity = input_activity[:max_per_layer]
    output_activity = output_activity[:max_per_layer]
    hidden_activity = hidden_activity[:max_per_layer]
    input_mean = input_sum / max(1, input_count)
    output_mean = output_sum / max(1, output_count)
    hidden_mean = hidden_sum / max(1, hidden_count)
    propagation_active = input_mean > 0.001 and hidden_mean > 0.001 and output_mean > 0.001
    return IOFlowData(
        tick=tick, input_activity=tuple(input_activity),
        output_activity=tuple(output_activity),
        hidden_activity=tuple(hidden_activity),
        input_mean_rate=input_mean, output_mean_rate=output_mean,
        hidden_mean_rate=hidden_mean,
        propagation_active=propagation_active,
        input_count=input_count, output_count=output_count,
        hidden_count=hidden_count,
    )


# ============================================================================
# Population Overview
# ============================================================================


@dataclass(frozen=True, slots=True)
class PopulationData:
    tick: int
    populations: tuple["_PopulationEntry", ...]
    ei_ratio: float | None
    total_excitatory: int
    total_inhibitory: int
    source: str = "live_runtime"
    status: str = "active"

    def to_json(self) -> dict[str, object]:
        return {
            "source": self.source,
            "tick": self.tick,
            "populations": [p.to_json() for p in self.populations],
            "ei_ratio": self.ei_ratio,
            "total_excitatory": self.total_excitatory,
            "total_inhibitory": self.total_inhibitory,
            "status": self.status,
        }


@dataclass(frozen=True, slots=True)
class _PopulationEntry:
    name: str
    count: int
    mean_rate: float
    mean_energy: float
    mean_v: float
    active_count: int
    active_fraction: float

    def to_json(self) -> dict[str, object]:
        return {
            "name": self.name,
            "count": self.count,
            "mean_rate": self.mean_rate,
            "mean_energy": self.mean_energy,
            "mean_v": self.mean_v,
            "active_count": self.active_count,
            "active_fraction": self.active_fraction,
        }


def compute_population_data(network, activity_accumulator=None):
    from collections import defaultdict
    tick = network.current_tick
    pop_data = defaultdict(
        lambda: {"count": 0, "rate_sum": 0.0, "energy_sum": 0.0, "v_sum": 0.0, "active": 0}
    )
    for nid, neuron in network.neurons.items():
        coords = unpack_coords(nid)
        neuron_type = getattr(neuron, "neuron_type", None)
        if neuron_type is not None:
            type_name = str(neuron_type).lower()
        else:
            if coords[0] == 0:
                type_name = "sensory_input"
            elif coords[0] == network.dimensions[0] - 1:
                type_name = "motor_output"
            elif hasattr(neuron, "is_inhibitory") and neuron.is_inhibitory:
                type_name = "inhibitory"
            else:
                type_name = "excitatory"
        if activity_accumulator is not None:
            rate = activity_accumulator.firing_rate(nid)
        elif neuron.last_spike_tick >= 0:
            age = max(0, tick - neuron.last_spike_tick)
            rate = float(__import__("numpy").exp(-age / 50.0))
        else:
            rate = 0.0
        entry = pop_data[type_name]
        entry["count"] += 1
        entry["rate_sum"] += rate
        entry["energy_sum"] += neuron.energy
        entry["v_sum"] += getattr(neuron, "v", 0.0)
        if rate > 0.01:
            entry["active"] += 1
    populations = []
    exc_count = 0
    inh_count = 0
    for name, data in sorted(pop_data.items()):
        count = data["count"]
        mean_rate = data["rate_sum"] / max(1, count)
        mean_energy = data["energy_sum"] / max(1, count)
        mean_v = data["v_sum"] / max(1, count)
        active_count = data["active"]
        active_fraction = active_count / max(1, count)
        populations.append(_PopulationEntry(
            name=name, count=count, mean_rate=mean_rate,
            mean_energy=mean_energy, mean_v=mean_v,
            active_count=active_count, active_fraction=active_fraction,
        ))
        if "excit" in name.lower():
            exc_count += count
        elif "inhib" in name.lower():
            inh_count += count
    if inh_count == 0:
        return PopulationData(
            tick=tick, populations=tuple(populations),
            ei_ratio=None,
            total_excitatory=exc_count, total_inhibitory=inh_count,
            status="unavailable",
        )
    ei_ratio = exc_count / inh_count
    return PopulationData(
        tick=tick, populations=tuple(populations),
        ei_ratio=ei_ratio,
        total_excitatory=exc_count, total_inhibitory=inh_count,
    )


# ============================================================================
# Firing Rate Histogram
# ============================================================================


@dataclass(frozen=True, slots=True)
class RateHistogramData:
    tick: int
    bins: tuple[float, ...]
    counts: tuple[int, ...]
    mean_rate: float
    median_rate: float
    std_rate: float
    silent_count: int
    active_count: int
    total_count: int
    source: str = "live_runtime"

    def to_json(self) -> dict[str, object]:
        return {
            "source": self.source,
            "tick": self.tick,
            "bins": list(self.bins),
            "counts": list(self.counts),
            "mean_rate": self.mean_rate,
            "median_rate": self.median_rate,
            "std_rate": self.std_rate,
            "silent_count": self.silent_count,
            "active_count": self.active_count,
            "total_count": self.total_count,
        }


def compute_rate_histogram(network, activity_accumulator=None, num_bins=30):
    tick = network.current_tick
    rates = []
    silent = 0
    for nid, neuron in network.neurons.items():
        if activity_accumulator is not None:
            rate = activity_accumulator.firing_rate(nid)
        elif neuron.last_spike_tick >= 0:
            age = max(0, tick - neuron.last_spike_tick)
            rate = float(__import__('numpy').exp(-age / 50.0))
        else:
            rate = 0.0
        if rate < 0.0001:
            silent += 1
        else:
            rates.append(rate)
    if not rates:
        bin_edges = [float(i) / num_bins for i in range(num_bins + 1)]
        return RateHistogramData(
            tick=tick, bins=tuple(bin_edges),
            counts=tuple([0] * num_bins),
            mean_rate=0.0, median_rate=0.0, std_rate=0.0,
            silent_count=silent, active_count=0, total_count=silent,
        )
    import statistics
    import numpy as np
    max_rate = max(rates) * 1.05 or 1.0
    bin_edges = [max_rate * i / num_bins for i in range(num_bins + 1)]
    bin_counts = [0] * num_bins
    for r in rates:
        idx = min(num_bins - 1, int(r * num_bins / max_rate))
        bin_counts[idx] += 1
    return RateHistogramData(
        tick=tick, bins=tuple(bin_edges),
        counts=tuple(bin_counts),
        mean_rate=float(np.mean(rates)),
        median_rate=float(np.median(rates)),
        std_rate=float(np.std(rates)),
        silent_count=silent, active_count=len(rates),
        total_count=silent + len(rates),
    )


# ============================================================================
# Spike Raster (recent spike history)
# ============================================================================


@dataclass(frozen=True, slots=True)
class SpikeRasterData:
    tick: int
    neuron_ids: tuple[int, ...]
    spike_ticks: tuple[int, ...]
    window_ticks: int
    sample_count: int
    total_neurons: int
    source: str = "live_runtime"
    status: str = "unavailable"

    def to_json(self) -> dict[str, object]:
        return {
            "source": self.source,
            "tick": self.tick,
            "neuron_ids": list(self.neuron_ids),
            "spike_ticks": list(self.spike_ticks),
            "window_ticks": self.window_ticks,
            "sample_count": self.sample_count,
            "total_neurons": self.total_neurons,
            "status": self.status,
        }


def compute_spike_raster(network, activity_accumulator=None, window_ticks=100, max_neurons=500):
    """Return unavailable — real timestamped spike events are not available
    in the dashboard telemetry pipeline. The ActivityWindowAccumulator only
    stores per-neuron spike counts, not per-event timestamps.

    Real timestamped spike events exist in SpikeHistory (src/telemetry/spike_history.py)
    but are not wired into the dashboard OperatorBridge.
    """
    tick = network.current_tick
    return SpikeRasterData(
        tick=tick, neuron_ids=(), spike_ticks=(),
        window_ticks=window_ticks,
        sample_count=0, total_neurons=len(network.neurons),
        status="unavailable",
    )
