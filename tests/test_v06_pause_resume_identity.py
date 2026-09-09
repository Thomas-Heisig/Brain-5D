from __future__ import annotations

import hashlib
import threading
from dataclasses import dataclass

from src.controller.runtime import ControllerState, RuntimeController


@dataclass
class _Result:
    spikes_this_tick: int


class _DeterministicNetwork:
    def __init__(self) -> None:
        self._tick = 0
        self.accumulator = 17

    @property
    def current_tick(self) -> int:
        return self._tick

    @property
    def synapse_count(self) -> int:
        return 2

    @property
    def queued_event_count(self) -> int:
        return 0

    @property
    def neuron_count(self) -> int:
        return 3

    def step(self) -> _Result:
        self._tick += 1
        self.accumulator = (self.accumulator * 1103515245 + 12345 + self._tick) & 0xFFFFFFFF
        return _Result(spikes_this_tick=self.accumulator % 3)

    def digest(self) -> str:
        return hashlib.sha256(f"{self._tick}:{self.accumulator}".encode()).hexdigest()


def test_pause_resume_matches_uninterrupted_deterministic_state() -> None:
    baseline = _DeterministicNetwork()
    RuntimeController(baseline, batch_size=1).run_ticks(10)

    interrupted = _DeterministicNetwork()
    controller = RuntimeController(interrupted, batch_size=1)
    paused = threading.Event()
    completed = threading.Event()

    def control_hook(tick: int, _result: object) -> None:
        if tick == 5:
            controller.pause()
            paused.set()
        elif tick == 10:
            controller.stop()
            completed.set()

    controller.add_hook(control_hook)
    controller.start()
    assert paused.wait(2.0)
    assert controller.state == ControllerState.PAUSED
    assert interrupted.current_tick == 5

    controller.resume()
    assert completed.wait(2.0)
    assert interrupted.current_tick == 10
    assert interrupted.digest() == baseline.digest()
