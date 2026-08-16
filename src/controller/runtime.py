"""Thread-safe runtime controller for interactive Brain-5D operation.

The controller owns *when* ticks run, not the network implementation itself.
It is intentionally dependency-light and works against a small typed Protocol.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Protocol


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


class HomeostasisLike(Protocol):
    @property
    def enabled(self) -> bool: ...

    def update(self, tick: int, dt_ms: float = 1.0) -> None: ...


class ControllerState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class ControllerCommand(str, Enum):
    START = "start"
    PAUSE = "pause"
    RESUME = "resume"
    STOP = "stop"
    STEP = "step"
    RUN_TICKS = "run_ticks"
    SNAPSHOT = "snapshot"


@dataclass(frozen=True, slots=True)
class RuntimeTelemetry:
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


SnapshotCallback = Callable[[], None]
PostTickHook = Callable[[int], None]


class RuntimeController:
    """Own the simulation clock and expose safe operator commands."""

    def __init__(
        self,
        network: RuntimeNetworkLike,
        homeostasis: HomeostasisLike | None = None,
        *,
        batch_size: int = 10,
        loop_delay_ms: float = 0.0,
        telemetry_interval_ticks: int = 10,
        snapshot_callback: SnapshotCallback | None = None,
        max_manual_ticks: int = 1_000,
    ) -> None:
        if batch_size <= 0:
            raise ValueError("batch_size must be > 0")
        if telemetry_interval_ticks <= 0:
            raise ValueError("telemetry_interval_ticks must be > 0")
        if loop_delay_ms < 0:
            raise ValueError("loop_delay_ms must be >= 0")
        if max_manual_ticks <= 0:
            raise ValueError("max_manual_ticks must be > 0")

        self.network = network
        self.homeostasis = homeostasis
        self._batch_size = batch_size
        self._loop_delay_ms = loop_delay_ms
        self._telemetry_interval_ticks = telemetry_interval_ticks
        self._snapshot_callback = snapshot_callback
        self._max_manual_ticks = max_manual_ticks

        self._state = ControllerState.IDLE
        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._hooks: list[PostTickHook] = []
        self._snapshot_requested = False
        self._requested_ticks = 0
        self._completed_ticks = 0
        self._telemetry = self._make_telemetry(0.0, 0.0, 0)

    @property
    def state(self) -> ControllerState:
        with self._lock:
            return self._state

    @property
    def telemetry(self) -> RuntimeTelemetry:
        with self._lock:
            return self._telemetry

    def add_hook(self, hook: PostTickHook) -> None:
        with self._lock:
            self._hooks.append(hook)

    def start(self) -> None:
        """Start continuous execution in a daemon thread."""
        with self._lock:
            if self._state == ControllerState.RUNNING:
                return
            if self._thread is not None and self._thread.is_alive():
                self._state = ControllerState.RUNNING
                self._pause_event.clear()
                return
            self._stop_event.clear()
            self._pause_event.clear()
            self._state = ControllerState.RUNNING
            self._thread = threading.Thread(
                target=self._run_loop,
                name="brain5d-runtime",
                daemon=True,
            )
            self._thread.start()

    def pause(self) -> None:
        with self._lock:
            if self._state == ControllerState.RUNNING:
                self._state = ControllerState.PAUSED
                self._pause_event.set()

    def resume(self) -> None:
        with self._lock:
            if self._state == ControllerState.PAUSED:
                self._state = ControllerState.RUNNING
                self._pause_event.clear()

    def stop(self) -> None:
        with self._lock:
            self._stop_event.set()
            self._pause_event.set()
            self._state = ControllerState.STOPPED

    def step_once(self) -> RuntimeTelemetry:
        """Execute exactly one tick while not continuously running."""
        if self.state == ControllerState.RUNNING:
            raise RuntimeError("step_once is unavailable while running")
        return self.run_ticks(1)

    def single_step(self) -> RuntimeTelemetry:
        """Execute exactly one tick through the alpha.5 control contract."""
        return self.step_once()

    def run_ticks(self, count: int) -> RuntimeTelemetry:
        """Execute a finite operator-requested batch synchronously."""
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
        """Start continuous execution or run one bounded finite batch."""
        if count is not None:
            return self.run_ticks(count)
        self.start()
        return self.telemetry

    def request_snapshot(self) -> None:
        """Request a snapshot at the next safe controller boundary."""
        with self._lock:
            self._snapshot_requested = True
        if self.state != ControllerState.RUNNING:
            self._flush_snapshot_request()

    def _run_loop(self) -> None:
        last_tick = self.network.current_tick
        try:
            while not self._stop_event.is_set():
                if self._pause_event.is_set():
                    time.sleep(0.05)
                    continue
                started = time.perf_counter()
                spikes = self._execute_ticks(self._batch_size)
                elapsed_ms = (time.perf_counter() - started) * 1000.0
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
                self._flush_snapshot_request()
                if self._loop_delay_ms:
                    time.sleep(self._loop_delay_ms / 1000.0)
        except Exception as exc:  # controller boundary: persist the error state
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
                )
            return
        with self._lock:
            self._state = ControllerState.STOPPED

    def _execute_ticks(self, count: int) -> int:
        spikes_total = 0
        for _ in range(count):
            if self._stop_event.is_set() and self.state == ControllerState.RUNNING:
                break
            result = self.network.step()
            spikes_total += result.spikes_this_tick
            if self.homeostasis is not None and self.homeostasis.enabled:
                self.homeostasis.update(self.network.current_tick)
            with self._lock:
                hooks = tuple(self._hooks)
            for hook in hooks:
                hook(self.network.current_tick)
        return spikes_total

    def _flush_snapshot_request(self) -> None:
        with self._lock:
            requested = self._snapshot_requested
            self._snapshot_requested = False
        if requested and self._snapshot_callback is not None:
            self._snapshot_callback()

    def _make_telemetry(
        self,
        batch_duration_ms: float,
        elapsed_ms: float,
        spikes: int,
    ) -> RuntimeTelemetry:
        tps = 0.0
        if elapsed_ms > 0:
            tps = self._batch_size * 1000.0 / elapsed_ms
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
        )
