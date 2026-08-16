"""Typed dashboard control service for runtime and self-organization commands."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from src.dashboard.models import JSONValue
from src.runtime.control import RuntimeController
from src.self_organization.coordinator import SelfOrganizationCoordinator

ControlAction = Literal[
    "step",
    "run",
    "pause",
    "stop",
    "configure",
    "snapshot",
    "self_organization",
]


@dataclass(frozen=True, slots=True)
class ControlResponse:
    """HTTP-independent control response."""

    ok: bool
    status: int
    payload: dict[str, JSONValue]


class DashboardControlService:
    """Validate dashboard commands before they reach runtime components."""

    def __init__(
        self,
        runtime: RuntimeController,
        self_organization: SelfOrganizationCoordinator | None = None,
    ) -> None:
        self._runtime = runtime
        self._self_organization = self_organization

    def state(self) -> dict[str, JSONValue]:
        """Return all control-plane telemetry."""
        payload: dict[str, JSONValue] = {
            "runtime": self._runtime.snapshot().to_json(),
        }
        if self._self_organization is not None:
            payload["self_organization"] = self._self_organization.snapshot().to_json()
        return payload

    def execute(self, body: object) -> ControlResponse:
        """Validate and execute one dashboard command."""
        if not isinstance(body, dict):
            return self._error(400, "JSON body must be an object.")
        action = body.get("action")
        if not isinstance(action, str):
            return self._error(400, "Missing string field 'action'.")

        try:
            if action == "step":
                ticks = self._int_field(body, "ticks", default=1, minimum=1)
                state = self._runtime.step(ticks)
            elif action == "run":
                loop_size = self._optional_int_field(
                    body,
                    "loop_size",
                    minimum=1,
                )
                state = self._runtime.run(loop_size=loop_size)
            elif action == "pause":
                state = self._runtime.pause()
            elif action == "stop":
                state = self._runtime.stop()
            elif action == "configure":
                loop_size = self._optional_int_field(
                    body,
                    "loop_size",
                    minimum=1,
                )
                delay_ms = self._optional_float_field(
                    body,
                    "delay_ms",
                    minimum=0.0,
                )
                state = self._runtime.configure(
                    loop_size=loop_size,
                    delay_ms=delay_ms,
                )
            elif action == "snapshot":
                state = self._runtime.request_snapshot()
            elif action == "self_organization":
                return self._configure_self_organization(body)
            else:
                return self._error(400, f"Unknown control action: {action}")
        except (TypeError, ValueError, RuntimeError) as exc:
            return self._error(409, str(exc))

        return ControlResponse(
            ok=True,
            status=200,
            payload={"ok": True, "runtime": state.to_json()},
        )

    def _configure_self_organization(
        self, body: dict[object, object]
    ) -> ControlResponse:
        coordinator = self._self_organization
        if coordinator is None:
            return self._error(503, "Self-organization coordinator is not available.")
        enabled = self._optional_bool_field(body, "enabled")
        dry_run = self._optional_bool_field(body, "dry_run")
        coordinator.configure(enabled=enabled, dry_run=dry_run)
        return ControlResponse(
            ok=True,
            status=200,
            payload={
                "ok": True,
                "self_organization": coordinator.snapshot().to_json(),
            },
        )

    @staticmethod
    def _int_field(
        body: dict[object, object],
        name: str,
        *,
        default: int,
        minimum: int,
    ) -> int:
        value = body.get(name, default)
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"'{name}' must be an integer.")
        if value < minimum:
            raise ValueError(f"'{name}' must be >= {minimum}.")
        return value

    @staticmethod
    def _optional_int_field(
        body: dict[object, object],
        name: str,
        *,
        minimum: int,
    ) -> int | None:
        value = body.get(name)
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"'{name}' must be an integer.")
        if value < minimum:
            raise ValueError(f"'{name}' must be >= {minimum}.")
        return value

    @staticmethod
    def _optional_float_field(
        body: dict[object, object],
        name: str,
        *,
        minimum: float,
    ) -> float | None:
        value = body.get(name)
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"'{name}' must be numeric.")
        result = float(value)
        if result < minimum:
            raise ValueError(f"'{name}' must be >= {minimum}.")
        return result

    @staticmethod
    def _optional_bool_field(
        body: dict[object, object],
        name: str,
    ) -> bool | None:
        value = body.get(name)
        if value is None:
            return None
        if not isinstance(value, bool):
            raise TypeError(f"'{name}' must be boolean.")
        return value

    @staticmethod
    def _error(status: int, message: str) -> ControlResponse:
        return ControlResponse(
            ok=False,
            status=status,
            payload={"ok": False, "error": message},
        )
