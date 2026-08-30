"""Tests for typed dashboard runtime commands."""

from time import monotonic, sleep

from src.dashboard.control_service import DashboardControlService
from src.runtime.control import RuntimeController


def test_control_service_rejects_invalid_action() -> None:
    controller = RuntimeController(lambda: None)
    try:
        service = DashboardControlService(controller)  # type: ignore[arg-type]
        response = service.execute({"action": "warp-core"})
        assert response.ok is False
        assert response.status == 400
    finally:
        controller.close()


def test_control_service_steps_runtime() -> None:
    counter = 0

    def step() -> None:
        nonlocal counter
        counter += 1

    controller = RuntimeController(step, initial_loop_size=10)
    try:
        service = DashboardControlService(controller)  # type: ignore[arg-type]
        response = service.execute({"action": "step", "ticks": 5})
        assert response.ok is True
        deadline = monotonic() + 1.0
        while counter < 5 and monotonic() < deadline:
            sleep(0.005)
        assert counter == 5
    finally:
        controller.close()
