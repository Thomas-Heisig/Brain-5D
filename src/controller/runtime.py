"""Thread-safe runtime controller for interactive Brain-5D operation.

The controller owns *when* ticks run, not the network implementation itself.
It is intentionally dependency-light and works against a small typed Protocol.

This provides a clean separation between:
- The simulation core (network, neurons, synapses)
- The control layer (start, pause, stop, step, run_ticks)
- The presentation layer (dashboard, telemetry)

The controller runs in a separate daemon thread and provides thread-safe
access to the simulation state via locks and events.

Example:
    >>> from src.controller import RuntimeController
    >>> controller = RuntimeController(network)
    >>> controller.start()
    >>> time.sleep(1)
    >>> controller.pause()
    >>> controller.run_ticks(10)
    >>> controller.stop()

Integration with dashboard:
    >>> from src.dashboard.operator_bridge import OperatorBridge
    >>> bridge = OperatorBridge(controller=controller)
    >>> serve_dashboard(host="127.0.0.1", port=8765, structural_bridge=bridge)
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Protocol

# ============================================================================
# Protocols (Minimal contracts for loose coupling)
# ============================================================================


class StepResultLike(Protocol):
    """Minimal result contract required by the controller."""

    @property
    def spikes_this_tick(self) -> int: ...


class RuntimeNetworkLike(Protocol):
    """Read/write boundary used by RuntimeController.

    Properties are used instead of mutable Protocol attributes so concrete
    dict/list implementations do not fail Pyright because of invariance.
    """

    @property
    def current_tick(self) -> int: ...

    @property
    def synapse_count(self) -> int: ...

    @property
    def queued_event_count(self) -> int: ...

    @property
    def neuron_count(self) -> int: ...

    def step(self) -> StepResultLike: ...

    def step_batch(self, count: int) -> tuple[StepResultLike, ...]: ...


class HomeostasisLike(Protocol):
    """Minimal homeostasis contract required by the controller."""

    @property
    def enabled(self) -> bool: ...

    def update(self, step_result: StepResultLike) -> None: ...


# ============================================================================
# Enums
# ============================================================================


class ControllerState(str, Enum):
    """Possible states of the runtime controller."""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

    @property
    def is_active(self) -> bool:
        """Return True if the controller is in a running or paused state."""
        return self in {ControllerState.RUNNING, ControllerState.PAUSED}

    @property
    def is_terminated(self) -> bool:
        """Return True if the controller is stopped or in error state."""
        return self in {ControllerState.STOPPED, ControllerState.ERROR}


class ControllerCommand(str, Enum):
    """Commands that can be sent to the runtime controller."""

    START = "start"
    PAUSE = "pause"
    RESUME = "resume"
    STOP = "stop"
    STEP = "step"
    RUN_TICKS = "run_ticks"
    SNAPSHOT = "snapshot"

    @classmethod
    def from_string(cls, value: str) -> ControllerCommand | None:
        """Convert a string to a ControllerCommand, or return None."""
        try:
            return cls(value)
        except ValueError:
            return None


# ============================================================================
# Telemetry
# ============================================================================


@dataclass(frozen=True, slots=True)
class RuntimeTelemetry:
    """Snapshot of runtime telemetry data.

    Attributes:
        tick: Current simulation tick.
        ticks_per_second: Achieved tick rate (ticks per second).
        batch_duration_ms: Time taken for the last batch in milliseconds.
        spikes_this_batch: Number of spikes in the last batch.
        neurons: Total number of neurons in the network.
        synapses: Total number of synapses in the network.
        queue_depth: Number of queued spike events.
        controller_state: Current state of the controller.
        requested_ticks: Total ticks requested by manual commands.
        completed_ticks: Total ticks completed.
        last_error: Last error message (if any).
    """

    tick: int
    ticks_per_second: float
    batch_duration_ms: float
    spikes_this_batch: int
    neurons: int
    synapses: int
    queue_depth: int
    controller_state: ControllerState
    requested_ticks: int
    completed_ticks: int
    last_error: str | None = None
    target_hz: float | None = None
    simulation_speed_ratio: float = 0.0
    tick_latency_ms: float = 0.0
    jitter_ms: float = 0.0
    compute_saturation: float = 0.0
    runtime_mode: str = "MAX"
    tick_profile: dict[str, float] | None = None
    max_possible_hz: float | None = None

    def to_dict(self) -> dict[str, int | float | str | None]:
        """Convert to dictionary for JSON serialization."""
        return {
            "tick": self.tick,
            "ticks_per_second": self.ticks_per_second,
            "batch_duration_ms": self.batch_duration_ms,
            "spikes_this_batch": self.spikes_this_batch,
            "neurons": self.neurons,
            "synapses": self.synapses,
            "queue_depth": self.queue_depth,
            "controller_state": self.controller_state.value,
            "requested_ticks": self.requested_ticks,
            "completed_ticks": self.completed_ticks,
            "last_error": self.last_error,
            "target_hz": self.target_hz,
            "simulation_speed_ratio": self.simulation_speed_ratio,
            "tick_latency_ms": self.tick_latency_ms,
            "jitter_ms": self.jitter_ms,
            "compute_saturation": self.compute_saturation,
            "runtime_mode": self.runtime_mode,
            "tick_profile": self.tick_profile,
            "max_possible_hz": self.max_possible_hz,
        }

    def to_json(self) -> dict[str, int | float | str | None]:
        """Alias for to_dict() for DashboardControlService compatibility."""
        return self.to_dict()


# ============================================================================
# Callback Types
# ============================================================================

SnapshotCallback = Callable[[], None]
"""Callback for snapshot requests."""

PostTickHook = Callable[[int, Any], None]
"""Callback after each tick, receives current tick number and the StepResult.

The second argument is the StepResult-like object returned by network.step().
Hooks should accept ``**kwargs`` for forward compatibility.
"""

PreTickHook = Callable[[int], None]
"""Callback before each tick, receives current tick number before stepping."""

ErrorCallback = Callable[[Exception], None]
"""Callback when an error occurs in the runtime loop."""


# ============================================================================
# Runtime Controller
# ============================================================================


class RuntimeController:
    """Own the simulation clock and expose safe operator commands.

    This controller provides thread-safe control over the Brain-5D simulation:
    - Start/stop continuous execution in a daemon thread
    - Pause/resume execution
    - Execute finite batches of ticks synchronously
    - Request snapshots at safe boundaries
    - Register post-tick hooks

    The controller is designed to be used with the dashboard's OperatorBridge
    for interactive control.

    Thread-safety:
        All public methods are thread-safe. The controller uses an RLock
        for state access and threading.Event for pause/stop signaling.

    Example:
        >>> controller = RuntimeController(network, homeostasis)
        >>> controller.add_hook(lambda tick: print(f"Tick {tick}"))
        >>> controller.start()
        >>> time.sleep(2)
        >>> controller.run_ticks(100)  # runs synchronously
        >>> controller.pause()
        >>> controller.resume()
        >>> controller.stop()
    """

    def __init__(
        self,
        network: RuntimeNetworkLike,
        homeostasis: HomeostasisLike | None = None,
        *,
        batch_size: int = 10,
        loop_delay_ms: float = 0.0,
        target_hz: float | None = None,
        telemetry_interval_ticks: int = 10,
        snapshot_callback: SnapshotCallback | None = None,
        max_manual_ticks: int = 100_000,
    ) -> None:
        """Initialize the runtime controller.

        Args:
            network: The network instance (must implement RuntimeNetworkLike).
            homeostasis: Optional homeostasis engine for rate regulation.
            batch_size: Number of ticks per batch in continuous mode.
            loop_delay_ms: Delay between batches in continuous mode.
            telemetry_interval_ticks: How often to update telemetry.
            snapshot_callback: Callback for snapshot requests.
            max_manual_ticks: Maximum ticks allowed in a single run_ticks call.

        Raises:
            ValueError: If batch_size, loop_delay_ms, telemetry_interval_ticks,
                or max_manual_ticks have invalid values.
        """
        if batch_size <= 0:
            raise ValueError(f"batch_size must be > 0, got {batch_size}")
        if telemetry_interval_ticks <= 0:
            raise ValueError(
                f"telemetry_interval_ticks must be > 0, got {telemetry_interval_ticks}"
            )
        if loop_delay_ms < 0:
            raise ValueError(f"loop_delay_ms must be >= 0, got {loop_delay_ms}")
        if target_hz is not None and target_hz <= 0:
            raise ValueError(f"target_hz must be > 0 or None, got {target_hz}")
        if max_manual_ticks <= 0:
            raise ValueError(f"max_manual_ticks must be > 0, got {max_manual_ticks}")

        self.network: RuntimeNetworkLike = network
        self.homeostasis: HomeostasisLike | None = homeostasis
        self._batch_size: int = batch_size
        self._loop_delay_ms: float = loop_delay_ms
        self._target_hz: float | None = target_hz
        self._telemetry_interval_ticks: int = telemetry_interval_ticks
        self._snapshot_callback: SnapshotCallback | None = snapshot_callback
        self._max_manual_ticks: int = max_manual_ticks

        self._state: ControllerState = ControllerState.IDLE
        self._lock: threading.RLock = threading.RLock()
        self._stop_event: threading.Event = threading.Event()
        self._pause_event: threading.Event = threading.Event()
        self._thread: threading.Thread | None = None
        self._hooks: list[PostTickHook] = []
        self._pre_hooks: list[PreTickHook] = []
        self._error_callbacks: list[ErrorCallback] = []
        self._snapshot_requested: bool = False
        self._requested_ticks: int = 0
        self._completed_ticks: int = 0
        self._last_tick_latency_ms: float = 0.0
        self._tick_latency_samples: list[float] = []
        self._phase_totals_ms: dict[str, float] = {}
        self._telemetry: RuntimeTelemetry = self._make_telemetry(0.0, 0.0, 0)

    # ========================================================================
    # Properties
    # ========================================================================

    @property
    def state(self) -> ControllerState:
        """Get the current controller state (thread-safe)."""
        with self._lock:
            return self._state

    @property
    def telemetry(self) -> RuntimeTelemetry:
        """Get the latest telemetry snapshot (thread-safe)."""
        with self._lock:
            return self._telemetry

    @property
    def is_running(self) -> bool:
        """Check if the controller is currently running (thread-safe)."""
        with self._lock:
            return self._state == ControllerState.RUNNING

    @property
    def is_paused(self) -> bool:
        """Check if the controller is currently paused (thread-safe)."""
        with self._lock:
            return self._state == ControllerState.PAUSED

    @property
    def is_idle(self) -> bool:
        """Check if the controller is idle (thread-safe)."""
        with self._lock:
            return self._state == ControllerState.IDLE

    # ========================================================================
    # Hook Management
    # ========================================================================

    def add_hook(self, hook: PostTickHook) -> None:
        """Register a hook that runs after each tick.

        Args:
            hook: Callback receiving the current tick number and StepResult.
        """
        with self._lock:
            if hook not in self._hooks:
                self._hooks.append(hook)

    def remove_hook(self, hook: PostTickHook) -> bool:
        """Remove a previously registered hook.

        Returns:
            True if the hook was removed, False if not found.
        """
        with self._lock:
            try:
                self._hooks.remove(hook)
                return True
            except ValueError:
                return False

    def clear_hooks(self) -> None:
        """Remove all registered hooks."""
        with self._lock:
            self._hooks.clear()

    def add_pre_hook(self, hook: PreTickHook) -> None:
        """Register a hook that runs before each tick.

        Args:
            hook: Callback receiving the current tick number before stepping.
        """
        with self._lock:
            if hook not in self._pre_hooks:
                self._pre_hooks.append(hook)

    def remove_pre_hook(self, hook: PreTickHook) -> bool:
        """Remove a previously registered pre-tick hook.

        Returns:
            True if the hook was removed, False if not found.
        """
        with self._lock:
            try:
                self._pre_hooks.remove(hook)
                return True
            except ValueError:
                return False

    def add_error_callback(self, callback: ErrorCallback) -> None:
        """Register a callback for runtime errors.

        Args:
            callback: Function receiving the exception.
        """
        with self._lock:
            if callback not in self._error_callbacks:
                self._error_callbacks.append(callback)

    # ========================================================================
    # Control Commands
    # ========================================================================

    def start(self) -> RuntimeTelemetry:
        """Start continuous execution in a daemon thread.

        If the controller is already running, this is a no-op.
        If the controller is paused, it resumes execution.
        If the controller is stopped, it creates a new thread.

        Returns:
            Current telemetry snapshot.
        """
        with self._lock:
            if self._state == ControllerState.RUNNING:
                return self._telemetry

            if self._state == ControllerState.PAUSED:
                self._state = ControllerState.RUNNING
                self._pause_event.clear()
                return self._telemetry

            if self._thread is not None and self._thread.is_alive():
                self._state = ControllerState.RUNNING
                self._pause_event.clear()
                return self._telemetry

            # Start new thread
            self._stop_event.clear()
            self._pause_event.clear()
            self._state = ControllerState.RUNNING
            self._thread = threading.Thread(
                target=self._run_loop,
                name="brain5d-runtime",
                daemon=True,
            )
            self._thread.start()
            return self._telemetry

    def pause(self) -> RuntimeTelemetry:
        """Pause continuous execution.

        The controller remains in a paused state until resume() is called.

        Returns:
            Current telemetry snapshot.
        """
        with self._lock:
            if self._state == ControllerState.RUNNING:
                self._state = ControllerState.PAUSED
                self._pause_event.set()
            return self._telemetry

    def resume(self) -> RuntimeTelemetry:
        """Resume continuous execution after pause.

        Returns:
            Current telemetry snapshot.
        """
        with self._lock:
            if self._state == ControllerState.PAUSED:
                self._state = ControllerState.RUNNING
                self._pause_event.clear()
            return self._telemetry

    def stop(self) -> RuntimeTelemetry:
        """Stop continuous execution gracefully.

        The controller thread will exit after completing the current batch.

        Returns:
            Current telemetry snapshot.
        """
        with self._lock:
            self._stop_event.set()
            self._pause_event.set()
            self._state = ControllerState.STOPPED
            return self._telemetry

    def step_once(self) -> RuntimeTelemetry:
        """Execute exactly one tick synchronously.

        This method is only available when the controller is not running
        continuously.

        Returns:
            Updated telemetry after the step.

        Raises:
            RuntimeError: If the controller is currently running.
        """
        if self.state == ControllerState.RUNNING:
            raise RuntimeError("step_once is unavailable while running")
        return self.run_ticks(1)

    def single_step(self) -> RuntimeTelemetry:
        """Alias for step_once (for compatibility with OperatorBridge)."""
        return self.step_once()

    def run_ticks(self, count: int) -> RuntimeTelemetry:
        """Execute a finite batch of ticks synchronously.

        This method is only available when the controller is not running
        continuously.

        Args:
            count: Number of ticks to execute (1 - max_manual_ticks).

        Returns:
            Updated telemetry after the batch.

        Raises:
            TypeError: If count is not an integer.
            ValueError: If count is out of range.
            RuntimeError: If the controller is currently running.
        """
        if isinstance(count, bool):
            raise TypeError("count must be an integer")
        if not 0 < count <= self._max_manual_ticks:
            raise ValueError(f"count must be in [1, {self._max_manual_ticks}]")
        if self.state == ControllerState.RUNNING:
            raise RuntimeError("run_ticks is unavailable while running")

        with self._lock:
            self._requested_ticks += count

        started = time.perf_counter()
        spikes = self._execute_ticks(count)
        elapsed_ms = (time.perf_counter() - started) * 1000.0

        with self._lock:
            self._completed_ticks += count
            self._telemetry = self._make_telemetry(elapsed_ms, elapsed_ms, spikes)
            return self._telemetry

    def run_loop(self, count: int | None = None) -> RuntimeTelemetry:
        """Run a finite batch or start continuous execution.

        This is a convenience method that delegates to either run_ticks
        (if count is provided) or start() (if count is None).

        Args:
            count: Optional number of ticks to run. If provided, runs
                synchronously via run_ticks. If None, starts continuous
                execution.

        Returns:
            Current telemetry.
        """
        if count is not None:
            return self.run_ticks(count)
        self.start()
        return self.telemetry

    def request_snapshot(self) -> RuntimeTelemetry:
        """Request a snapshot at the next safe controller boundary.

        If the controller is not running, the snapshot is taken immediately.

        Returns:
            Current telemetry snapshot.
        """
        with self._lock:
            self._snapshot_requested = True

        # If not running, flush immediately
        if self.state != ControllerState.RUNNING:
            self._flush_snapshot_request()

        return self.telemetry

    # ========================================================================
    # Internal Methods
    # ========================================================================

    def _run_loop(self) -> None:
        """Main loop for the daemon thread."""
        last_tick = self.network.current_tick

        try:
            while not self._stop_event.is_set():
                # Check pause
                if self._pause_event.is_set():
                    time.sleep(0.05)
                    continue

                # Execute batch
                started = time.perf_counter()
                spikes = self._execute_ticks(self._batch_size)
                elapsed_ms = (time.perf_counter() - started) * 1000.0

                # Update telemetry
                with self._lock:
                    self._completed_ticks += self._batch_size
                    tick_delta = self.network.current_tick - last_tick
                    if tick_delta >= self._telemetry_interval_ticks:
                        self._telemetry = self._make_telemetry(
                            elapsed_ms,
                            elapsed_ms,
                            spikes,
                        )
                        last_tick = self.network.current_tick

                # Flush snapshot request
                self._flush_snapshot_request()

                # Apply an optional target clock without changing SNN dt.
                target_delay_ms = 0.0
                if self._target_hz is not None:
                    target_batch_ms = self._batch_size * 1000.0 / self._target_hz
                    target_delay_ms = max(0.0, target_batch_ms - elapsed_ms)
                delay_ms = max(self._loop_delay_ms, target_delay_ms)
                if delay_ms:
                    time.sleep(delay_ms / 1000.0)

        except Exception as exc:
            # Handle errors and propagate to callbacks
            with self._lock:
                self._state = ControllerState.ERROR
                old = self._telemetry
                self._telemetry = RuntimeTelemetry(
                    tick=old.tick,
                    ticks_per_second=old.ticks_per_second,
                    batch_duration_ms=old.batch_duration_ms,
                    spikes_this_batch=old.spikes_this_batch,
                    neurons=old.neurons,
                    synapses=old.synapses,
                    queue_depth=old.queue_depth,
                    controller_state=ControllerState.ERROR,
                    requested_ticks=old.requested_ticks,
                    completed_ticks=old.completed_ticks,
                    last_error=str(exc),
                    target_hz=old.target_hz,
                    simulation_speed_ratio=old.simulation_speed_ratio,
                    tick_latency_ms=old.tick_latency_ms,
                    jitter_ms=old.jitter_ms,
                    compute_saturation=old.compute_saturation,
                    runtime_mode=old.runtime_mode,
                    tick_profile=old.tick_profile,
                    max_possible_hz=old.max_possible_hz,
                )

            # Notify error callbacks
            with self._lock:
                callbacks = tuple(self._error_callbacks)
            for callback in callbacks:
                try:
                    callback(exc)
                except Exception:
                    pass
            return

        with self._lock:
            self._state = ControllerState.STOPPED

    def _execute_ticks(self, count: int) -> int:
        """Execute a number of ticks and return total spikes."""
        spikes_total = 0
        self._phase_totals_ms = {}

        with self._lock:
            pre_hooks = tuple(self._pre_hooks)
            hooks = tuple(self._hooks)

        batched_results: tuple[StepResultLike, ...] | None = None
        if not pre_hooks and count > 1:
            batch_step = getattr(self.network, "step_batch", None)
            if callable(batch_step):
                network_started = time.perf_counter()
                batched_results = tuple(batch_step(count))
                network_elapsed_ms = (time.perf_counter() - network_started) * 1000.0
                reported_core_ms = sum(
                    float(getattr(result, "core_step_ms", 0.0))
                    for result in batched_results
                )
                self._phase_totals_ms["network_step"] = (
                    reported_core_ms if reported_core_ms > 0 else network_elapsed_ms
                )

        results = batched_results if batched_results is not None else (None,) * count
        for batched_result in results:
            tick_started = time.perf_counter()
            # Check stop signal
            if self._stop_event.is_set() and self.state == ControllerState.RUNNING:
                break

            # Run pre-tick hooks (e.g. stimulus)
            for hook in pre_hooks:
                phase_started = time.perf_counter()
                try:
                    hook(self.network.current_tick)
                except Exception:
                    pass  # Hook errors are isolated
                self._record_phase("pre_tick_hooks", phase_started)

            # Execute one tick
            if batched_result is None:
                network_started = time.perf_counter()
                result = self.network.step()
                self._record_phase("network_step", network_started)
            else:
                result = batched_result
                self._phase_totals_ms["network_step"] = self._phase_totals_ms.get(
                    "network_step", 0.0
                ) + float(getattr(result, "core_step_ms", 0.0))
            spikes_total += result.spikes_this_tick
            self._record_phase("tick_segment", tick_started)

            # Update homeostasis
            if self.homeostasis is not None and self.homeostasis.enabled:
                phase_started = time.perf_counter()
                self.homeostasis.update(result)
                self._record_phase("homeostasis", phase_started)

            # Run post-tick hooks
            post_started = time.perf_counter()
            for i in range(len(hooks)):
                try:
                    hooks[i](self.network.current_tick, result)
                except Exception:
                    pass  # Hook errors are isolated
            self._record_phase("post_tick_hooks", post_started)

            tick_latency_ms = (time.perf_counter() - tick_started) * 1000.0
            self._last_tick_latency_ms = tick_latency_ms
            self._tick_latency_samples.append(tick_latency_ms)
            if len(self._tick_latency_samples) > 1000:
                self._tick_latency_samples.pop(0)

        return spikes_total

    def _record_phase(self, phase: str, started: float) -> None:
        """Accumulate coarse runtime phase timings for the latest profile."""
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        self._phase_totals_ms[phase] = self._phase_totals_ms.get(phase, 0.0) + elapsed_ms

    def _flush_snapshot_request(self) -> None:
        """Execute the snapshot callback if requested."""
        with self._lock:
            requested = self._snapshot_requested
            self._snapshot_requested = False

        if requested and self._snapshot_callback is not None:
            try:
                self._snapshot_callback()
            except Exception:
                pass  # Callback errors are isolated

    def _make_telemetry(
        self,
        batch_duration_ms: float,
        elapsed_ms: float,
        spikes: int,
    ) -> RuntimeTelemetry:
        """Create a telemetry snapshot."""
        tps: float = 0.0
        if elapsed_ms > 0:
            tps = self._batch_size * 1000.0 / elapsed_ms
        latency = self._last_tick_latency_ms
        jitter = 0.0
        if len(self._tick_latency_samples) > 1:
            mean = sum(self._tick_latency_samples) / len(self._tick_latency_samples)
            jitter = (
                sum((sample - mean) ** 2 for sample in self._tick_latency_samples)
                / len(self._tick_latency_samples)
            ) ** 0.5
        target = self._target_hz
        ratio = tps / 1000.0 if target is None else tps / (1.0 / 0.001)
        saturation = (
            0.0
            if target is None or target == 0
            else min(1.0, target / max(tps, 0.001))
        )
        mode = "MAX" if target is None else ("COMPUTE LIMITED" if tps < target * 0.98 else "TARGETED")
        max_possible_hz = 1000.0 / latency if latency > 0 else None

        return RuntimeTelemetry(
            tick=self.network.current_tick,
            ticks_per_second=tps,
            batch_duration_ms=batch_duration_ms,
            spikes_this_batch=spikes,
            neurons=self.network.neuron_count,
            synapses=self.network.synapse_count,
            queue_depth=self.network.queued_event_count,
            controller_state=self._state,
            requested_ticks=self._requested_ticks,
            completed_ticks=self._completed_ticks,
            target_hz=target,
            simulation_speed_ratio=ratio,
            tick_latency_ms=latency,
            jitter_ms=jitter,
            compute_saturation=saturation,
            runtime_mode=mode,
            tick_profile=dict(self._phase_totals_ms),
            max_possible_hz=max_possible_hz,
        )

    # ========================================================================
    # Snapshot (for OperatorBridge compatibility)
    # ========================================================================

    def snapshot(self) -> RuntimeTelemetry:
        """Return the current telemetry snapshot (for OperatorBridge).

        Returns:
            Current telemetry data.
        """
        return self.telemetry

    # ========================================================================
    # DashboardControlService Compatibility
    # ========================================================================

    def step(self, ticks: int = 1) -> RuntimeTelemetry:
        """Execute a finite batch of ticks synchronously (alias for run_ticks).

        This method provides compatibility with DashboardControlService which
        expects a ``step(ticks)`` signature.

        Args:
            ticks: Number of ticks to execute.

        Returns:
            Updated telemetry after the batch.

        Raises:
            RuntimeError: If the controller is currently running continuously.
        """
        return self.run_ticks(ticks)

    def run(self, *, loop_size: int | None = None) -> RuntimeTelemetry:  # noqa: ARG001
        """Start continuous execution (alias for start).

        This method provides compatibility with DashboardControlService which
        expects a ``run()`` signature.

        Args:
            loop_size: Ignored in this implementation; continuous execution
                uses the batch_size configured at construction time.

        Returns:
            Current telemetry.
        """
        self.start()
        return self.telemetry

    def configure(self, **kwargs: Any) -> RuntimeTelemetry:
        """Configure runtime parameters (for OperatorBridge).

        Args:
            loop_size: Override batch_size.
            delay_ms: Override loop_delay_ms.

        Returns:
            Current telemetry snapshot.
        """
        with self._lock:
            if "loop_size" in kwargs:
                loop_size = kwargs["loop_size"]
                if loop_size is not None:
                    if not isinstance(loop_size, int) or loop_size <= 0:
                        raise ValueError(
                            f"loop_size must be a positive int, got {loop_size}"
                        )
                    self._batch_size = loop_size
            if "delay_ms" in kwargs:
                delay_ms = kwargs["delay_ms"]
                if delay_ms is not None:
                    if not isinstance(delay_ms, (int, float)) or delay_ms < 0:
                        raise ValueError(f"delay_ms must be >= 0, got {delay_ms}")
                    self._loop_delay_ms = float(delay_ms)
            if "target_hz" in kwargs:
                target_hz = kwargs["target_hz"]
                if target_hz is not None and (
                    not isinstance(target_hz, (int, float)) or target_hz <= 0
                ):
                    raise ValueError("target_hz must be > 0 or None")
                self._target_hz = float(target_hz) if target_hz is not None else None
            self._telemetry = replace(
                self._telemetry,
                target_hz=self._target_hz,
                runtime_mode="MAX" if self._target_hz is None else "TARGETED",
            )
            return self._telemetry


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    # Protocols
    "StepResultLike",
    "RuntimeNetworkLike",
    "HomeostasisLike",
    # Enums
    "ControllerState",
    "ControllerCommand",
    # Telemetry
    "RuntimeTelemetry",
    # Callbacks
    "SnapshotCallback",
    "PostTickHook",
    "PreTickHook",
    "ErrorCallback",
    # Main class
    "RuntimeController",
]
