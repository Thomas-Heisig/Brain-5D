from dataclasses import dataclass

import pytest

from src.controller.runtime import ControllerState, RuntimeController


@dataclass
class Result:
    spikes_this_tick: int = 1


class Network:
    def __init__(self) -> None:
        self._tick = 0

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

    def step(self) -> Result:
        self._tick += 1
        return Result()


def test_operator_can_run_exact_ticks() -> None:
    controller = RuntimeController(Network())
    telemetry = controller.run_ticks(5)
    assert telemetry.tick == 5
    assert telemetry.spikes_this_batch == 5
    assert controller.state == ControllerState.IDLE


def test_alpha5_runtime_aliases_preserve_bounded_execution() -> None:
    controller = RuntimeController(Network(), max_manual_ticks=10)

    assert controller.single_step().tick == 1
    assert controller.run_loop(9).tick == 10
    with pytest.raises(ValueError):
        controller.run_ticks(11)
