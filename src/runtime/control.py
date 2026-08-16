"""Thread-safe runtime controller used by the interactive dashboard.

The controller intentionally does not know about HTTP, dashboard rendering or the
concrete NeuralNetwork implementation.  It only coordinates a typed step callback.
This keeps the simulation core deterministic and allows the dashboard to request
bounded work without mutating the network from request-handler threads.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from threading import Condition, RLock, Thread
from time import perf_counter, sleep
from typing import Callable, Final, Literal

from src.dashboard.models import JSONValue

StepCallback = Callable[[], None]
OptionalCallback = Callable[[], None]


class ControlMode(StrEnum):
    """Current execution state of the simulation controller."""

    PAUSED = "paused"
    RUNNING = "running"
    STOPPED = "stopped"
    FAULTED = "faulted"


class ControlCommand(StrEnum):
    """Commands exposed by the dashboard control plane."""

    STEP = "step"
    RUN = "run"
    PAUSE = "pause"
    STOP = "stop"
    SNAPSHOT = "snapshot"


@dataclass(frozen=True, slots=True)
class ControlSnapshot:
    """Immutable public controller state."""

    mode: ControlMode
    ticks_executed: int
    queued_ticks: int
    loop_size: int
    delay_ms: float
    last_batch_ticks: int
    last_batch_ms: float
    total_runtime_ms: float
    fault: str | None
    can_snapshot: bool

    def to_json(self) -> dict[str, JSONValue]:
        """Return a JSON-ready dashboard representation."""
        return {
            "mode": self.mode.value,
            "ticks_executed": self.ticks_executed,
            "queued_ticks": self.queued_ticks,
            "loop_size": self.loop_size,
            "delay_ms": self.delay_ms,
            "last_batch_ticks": self.last_batch_ticks,
            "last_batch_ms": self.last_batch_ms,
            "total_runtime_ms": self.total_runtime_ms,
            "fault": self.fault,
            "can_snapshot": self.can_snapshot,
        }


class RuntimeController:
    """Own the simulation loop and expose safe bounded control operations.

    The simulation is stepped only by the controller worker.  HTTP request threads
    merely enqueue work or change controller state.  This avoids concurrent calls to
    ``network.step()`` and makes step/run/pause semantics deterministic.
    """

    _MIN_LOOP_SIZE: Final[int] = 1
    _MAX_LOOP_SIZE: Final[int] = 1_000_000
    _MAX_QUEUE: Final[int] = 10_000_000
    _MAX_DELAY_MS: Final[float] = 60_000.0

    def __init__(
        self,
        step_callback: StepCallback,
        *,
        snapshot_callback: OptionalCallback | None = None,
        stop_callback: OptionalCallback | None = None,
        initial_loop_size: int = 100,
        initial_delay_ms: float = 0.0,
    ) -> None:
        self._step_callback = step_callback
        self._snapshot_callback = snapshot_callback
        self._stop_callback = stop_callback
        self._lock = RLock()
        self._condition = Condition(self._lock)
        self._mode = ControlMode.PAUSED
        self._queued_ticks = 0
        self._ticks_executed = 0
        self._loop_size = self._validate_loop_size(initial_loop_size)
        self._delay_ms = self._validate_delay(initial_delay_ms)
        self._last_batch_ticks = 0
        self._last_batch_ms = 0.0
        self._total_runtime_ms = 0.0
        self._fault: str | None = None
        self._shutdown = False
        self._worker = Thread(
            target=self._worker_main,
            name="brain5d-runtime-controller",
            daemon=True,
        )
        self._worker.start()

    def snapshot(self) -> ControlSnapshot:
        """Return a consistent immutable state snapshot."""
        with self._lock:
            return ControlSnapshot(
                mode=self._mode,
                ticks_executed=self._ticks_executed,
                queued_ticks=self._queued_ticks,
                loop_size=self._loop_size,
                delay_ms=self._delay_ms,
                last_batch_ticks=self._last_batch_ticks,
                last_batch_ms=self._last_batch_ms,
                total_runtime_ms=self._total_runtime_ms,
                fault=self._fault,
                can_snapshot=self._snapshot_callback is not None,
            )

    def step(self, ticks: int = 1) -> ControlSnapshot:
        """Queue an exact number of ticks while remaining in paused mode."""
        count = self._validate_tick_count(ticks)
        with self._condition:
            self._ensure_operational()
            if self._mode is ControlMode.RUNNING:
                raise RuntimeError("Pause continuous execution before exact stepping.")
            self._queued_ticks = min(self._MAX_QUEUE, self._queued_ticks + count)
            self._condition.notify_all()
        return self.snapshot()

    def run(self, *, loop_size: int | None = None) -> ControlSnapshot:
        """Start continuous execution in bounded loop batches."""
        with self._condition:
            self._ensure_operational()
            if loop_size is not None:
                self._loop_size = self._validate_loop_size(loop_size)
            self._mode = ControlMode.RUNNING
            self._condition.notify_all()
        return self.snapshot()

    def pause(self) -> ControlSnapshot:
        """Pause continuous execution after the current tick."""
        with self._condition:
            self._ensure_operational()
            self._mode = ControlMode.PAUSED
            self._condition.notify_all()
        return self.snapshot()

    def stop(self) -> ControlSnapshot:
        """Stop execution and invoke the optional application stop callback."""
        callback: OptionalCallback | None
        with self._condition:
            if self._mode is ControlMode.STOPPED:
                return self.snapshot()
            self._mode = ControlMode.STOPPED
            self._queued_ticks = 0
            callback = self._stop_callback
            self._condition.notify_all()
        if callback is not None:
            callback()
        return self.snapshot()

    def request_snapshot(self) -> ControlSnapshot:
        """Create a storage snapshot through the application-provided callback."""
        callback = self._snapshot_callback
        if callback is None:
            raise RuntimeError("Snapshot capability is not configured.")
        with self._lock:
            self._ensure_operational()
        callback()
        return self.snapshot()

    def configure(
        self,
        *,
        loop_size: int | None = None,
        delay_ms: float | None = None,
    ) -> ControlSnapshot:
        """Adjust execution batch size and inter-tick pacing."""
        with self._condition:
            self._ensure_operational()
            if loop_size is not None:
                self._loop_size = self._validate_loop_size(loop_size)
            if delay_ms is not None:
                self._delay_ms = self._validate_delay(delay_ms)
            self._condition.notify_all()
        return self.snapshot()

    def close(self, timeout: float = 2.0) -> None:
        """Terminate the worker thread during application shutdown."""
        with self._condition:
            self._shutdown = True
            self._condition.notify_all()
        self._worker.join(timeout=timeout)

    def _worker_main(self) -> None:
        while True:
            with self._condition:
                self._condition.wait_for(self._has_work_or_shutdown)
                if self._shutdown:
                    return
                mode = self._mode
                if mode in {ControlMode.STOPPED, ControlMode.FAULTED}:
                    self._condition.wait(timeout=0.05)
                    continue
                if self._queued_ticks > 0:
                    batch = min(self._queued_ticks, self._loop_size)
                    self._queued_ticks -= batch
                elif mode is ControlMode.RUNNING:
                    batch = self._loop_size
                else:
                    continue
                delay_ms = self._delay_ms

            start = perf_counter()
            completed = 0
            try:
                for _ in range(batch):
                    with self._lock:
                        if self._mode in {
                            ControlMode.STOPPED,
                            ControlMode.FAULTED,
                        }:
                            break
                        if mode is ControlMode.RUNNING and self._mode is not ControlMode.RUNNING:
                            break
                    self._step_callback()
                    completed += 1
                    if delay_ms > 0.0:
                        sleep(delay_ms / 1000.0)
            except Exception as exc:  # controller boundary must contain core faults
                with self._condition:
                    self._mode = ControlMode.FAULTED
                    self._queued_ticks = 0
                    self._fault = f"{type(exc).__name__}: {exc}"
                    self._condition.notify_all()
                continue

            elapsed_ms = (perf_counter() - start) * 1000.0
            with self._condition:
                self._ticks_executed += completed
                self._last_batch_ticks = completed
                self._last_batch_ms = elapsed_ms
                self._total_runtime_ms += elapsed_ms

    def _has_work_or_shutdown(self) -> bool:
        return (
            self._shutdown
            or self._queued_ticks > 0
            or self._mode is ControlMode.RUNNING
            or self._mode in {ControlMode.STOPPED, ControlMode.FAULTED}
        )

    def _ensure_operational(self) -> None:
        if self._mode is ControlMode.STOPPED:
            raise RuntimeError("Runtime controller is stopped.")
        if self._mode is ControlMode.FAULTED:
            raise RuntimeError(self._fault or "Runtime controller is faulted.")

    @classmethod
    def _validate_tick_count(cls, ticks: int) -> int:
        if isinstance(ticks, bool) or not isinstance(ticks, int):
            raise TypeError("ticks must be an integer")
        if ticks < 1 or ticks > cls._MAX_QUEUE:
            raise ValueError(f"ticks must be in [1, {cls._MAX_QUEUE}]")
        return ticks

    @classmethod
    def _validate_loop_size(cls, loop_size: int) -> int:
        if isinstance(loop_size, bool) or not isinstance(loop_size, int):
            raise TypeError("loop_size must be an integer")
        if not cls._MIN_LOOP_SIZE <= loop_size <= cls._MAX_LOOP_SIZE:
            raise ValueError(
                f"loop_size must be in [{cls._MIN_LOOP_SIZE}, {cls._MAX_LOOP_SIZE}]"
            )
        return loop_size

    @classmethod
    def _validate_delay(cls, delay_ms: float) -> float:
        value = float(delay_ms)
        if not 0.0 <= value <= cls._MAX_DELAY_MS:
            raise ValueError(f"delay_ms must be in [0, {cls._MAX_DELAY_MS}]")
        return value
