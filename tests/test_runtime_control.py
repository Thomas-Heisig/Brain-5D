"""Tests for the interactive runtime controller."""

from __future__ import annotations

from threading import Event
from time import monotonic, sleep

from src.runtime.control import ControlMode, RuntimeController


def _wait_until(predicate: object, timeout: float = 1.0) -> None:
    if not callable(predicate):
        raise TypeError("predicate must be callable")
    deadline = monotonic() + timeout
    while monotonic() < deadline:
        if predicate():
            return
        sleep(0.005)
    raise AssertionError("condition was not reached before timeout")


def test_exact_step_executes_requested_ticks() -> None:
    counter = 0

    def step() -> None:
        nonlocal counter
        counter += 1

    controller = RuntimeController(step, initial_loop_size=4)
    try:
        controller.step(7)
        _wait_until(lambda: counter == 7)
        snapshot = controller.snapshot()
        assert snapshot.mode is ControlMode.PAUSED
        assert snapshot.ticks_executed == 7
        assert snapshot.queued_ticks == 0
    finally:
        controller.close()


def test_run_pause_and_configure() -> None:
    counter = 0

    def step() -> None:
        nonlocal counter
        counter += 1

    controller = RuntimeController(step, initial_loop_size=2, initial_delay_ms=0.1)
    try:
        controller.configure(loop_size=3, delay_ms=0.0)
        controller.run()
        _wait_until(lambda: counter >= 10)
        controller.pause()
        paused_at = counter
        sleep(0.03)
        assert counter <= paused_at + 1
        snapshot = controller.snapshot()
        assert snapshot.mode is ControlMode.PAUSED
        assert snapshot.loop_size == 3
    finally:
        controller.close()


def test_snapshot_capability_is_explicit() -> None:
    called = Event()
    controller = RuntimeController(lambda: None, snapshot_callback=called.set)
    try:
        assert controller.snapshot().can_snapshot is True
        controller.request_snapshot()
        assert called.is_set()
    finally:
        controller.close()
