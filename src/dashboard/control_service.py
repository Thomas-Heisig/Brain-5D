"""Typed dashboard control service for runtime and self-organization commands.

This module provides a validation layer between HTTP dashboard requests and
the Brain-5D runtime components. It handles command validation, type checking,
and error handling for all control operations.

The DashboardControlService is used by the HTTP server to process operator
commands and return consistent responses. It works alongside the
OperatorBridge (which handles structural plasticity) to provide complete
dashboard control functionality.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, cast

from src.controller.runtime import RuntimeController
from src.dashboard.models import JSONValue
from src.self_organization.coordinator import SelfOrganizationCoordinator

# ============================================================================
# Type Aliases
# ============================================================================

ControlAction = Literal[
    "step",
    "run",
    "pause",
    "stop",
    "configure",
    "snapshot",
    "self_organization",
]
"""Valid control actions that can be executed by the service."""

JSONBody = dict[str, Any]
"""Type alias for JSON request bodies."""


# ============================================================================
# Custom Exceptions
# ============================================================================


class ControlError(Exception):
    """Base exception for control service errors."""


class ValidationError(ControlError):
    """Raised when a command parameter is invalid."""


class UnknownActionError(ControlError):
    """Raised when an unknown control action is requested."""


class CoordinatorUnavailableError(ControlError):
    """Raised when the self-organization coordinator is not available."""


# ============================================================================
# Control Response
# ============================================================================


@dataclass(frozen=True, slots=True)
class ControlResponse:
    """HTTP-independent control response.

    This immutable data class represents the result of executing a control
    command. It contains a success flag, HTTP status code, and a JSON payload.

    Attributes:
        ok: True if the command succeeded, False otherwise.
        status: HTTP status code (200, 400, 409, 503, etc.).
        payload: JSON-serializable response data.
    """

    ok: bool
    status: int
    payload: dict[str, JSONValue]

    def to_json(self) -> dict[str, JSONValue]:
        """Convert to a JSON-serializable dictionary.

        This includes the ok flag, status code, and payload merged together.
        """
        result: dict[str, JSONValue] = {"ok": self.ok, "status": self.status}
        result.update(self.payload)
        return result

    @classmethod
    def success(cls, payload: dict[str, JSONValue] | None = None) -> ControlResponse:
        """Create a successful response."""
        return cls(ok=True, status=200, payload=payload or {"ok": True})

    @classmethod
    def error(
        cls, status: int, message: str, details: dict[str, JSONValue] | None = None
    ) -> ControlResponse:
        """Create an error response."""
        payload: dict[str, JSONValue] = {"ok": False, "error": message}
        if details is not None:
            payload["details"] = details
        return cls(ok=False, status=status, payload=payload)

    @property
    def is_success(self) -> bool:
        """Return True if the response indicates success."""
        return self.ok

    @property
    def is_error(self) -> bool:
        """Return True if the response indicates an error."""
        return not self.ok


# ============================================================================
# Control Service
# ============================================================================


class DashboardControlService:
    """Validate dashboard commands before they reach runtime components.

    This service provides a clean, type-safe interface for executing control
    commands on the Brain-5D runtime. It validates all command parameters
    before forwarding to the runtime components.

    The service supports:
    - Runtime control: step, run, pause, stop, configure, snapshot
    - Self-organization control: enable/disable, dry-run mode

    Example:
        >>> service = DashboardControlService(runtime_controller)
        >>> response = service.execute({"action": "step", "ticks": 10})
        >>> if response.ok:
        ...     print("Step completed")
    """

    def __init__(
        self,
        runtime: RuntimeController,
        self_organization: SelfOrganizationCoordinator | None = None,
    ) -> None:
        """Initialize the control service.

        Args:
            runtime: The runtime controller instance.
            self_organization: Optional self-organization coordinator.
        """
        self._runtime = runtime
        self._self_organization = self_organization

    # =========================================================================
    # State Queries
    # =========================================================================

    def state(self) -> dict[str, JSONValue]:
        """Return all control-plane telemetry.

        Returns:
            A dictionary containing runtime state and, if available,
            self-organization state.
        """
        payload: dict[str, JSONValue] = {
            "runtime": cast(JSONValue, self._runtime.snapshot().to_json()),
        }
        if self._self_organization is not None:
            payload["self_organization"] = cast(
                JSONValue, self._self_organization.snapshot().to_json()
            )
        return payload

    def runtime_status(self) -> dict[str, JSONValue]:
        """Return only runtime status.

        Returns:
            A dictionary with runtime status information.
        """
        return cast(dict[str, JSONValue], self._runtime.snapshot().to_json())

    def self_organization_status(self) -> dict[str, JSONValue] | None:
        """Return self-organization status if available.

        Returns:
            Self-organization snapshot or None if not configured.
        """
        if self._self_organization is not None:
            return (
                self._self_organization.snapshot().to_json()
            )  # pyright: ignore[return-value]
        return None

    # =========================================================================
    # Command Execution
    # =========================================================================

    def execute(self, body: object) -> ControlResponse:
        """Validate and execute one dashboard command.

        Accepts both ``{"action": "..."}`` and ``{"command": "..."}`` for
        backward compatibility. The canonical contract is:

        .. code-block:: json

            {"command": "run_ticks", "ticks": 100}

        Args:
            body: The request body, expected to be a dictionary with 'action'
                or 'command' and optional parameters.

        Returns:
            ControlResponse with the result of the command.
        """
        # Validate body type
        if not isinstance(body, dict):
            return ControlResponse.error(400, "JSON body must be an object.")

        # Cast to JSONBody for the type checker
        body_dict = cast(JSONBody, body)

        # Accept both "action" (legacy) and "command" (canonical)
        action = body_dict.get("command") or body_dict.get("action")
        if not isinstance(action, str):
            return ControlResponse.error(
                400, "Missing string field 'command' (or legacy 'action')."
            )

        # Dispatch to the appropriate handler
        try:
            if action in ("step", "single_step"):
                return self._handle_step(body_dict)
            elif action in ("run", "start", "resume"):
                return self._handle_run(body_dict)
            elif action == "run_ticks":
                return self._handle_run_ticks(body_dict)
            elif action == "pause":
                return self._handle_pause()
            elif action == "stop":
                return self._handle_stop()
            elif action == "configure":
                return self._handle_configure(body_dict)
            elif action == "snapshot":
                return self._handle_snapshot()
            elif action == "self_organization":
                return self._handle_self_organization(body_dict)
            else:
                return ControlResponse.error(400, f"Unknown control action: {action}")

        except ValidationError as e:
            return ControlResponse.error(400, str(e))
        except (TypeError, ValueError) as e:
            return ControlResponse.error(400, str(e))
        except CoordinatorUnavailableError as e:
            return ControlResponse.error(503, str(e))
        except (RuntimeError, ControlError) as e:
            return ControlResponse.error(409, str(e))
        except Exception as e:
            return ControlResponse.error(500, f"Internal error: {e}")

    # =========================================================================
    # Command Handlers
    # =========================================================================

    def _handle_step(self, body: JSONBody) -> ControlResponse:
        """Handle the 'step' command."""
        ticks = self._int_field(body, "ticks", default=1, minimum=1)
        state = self._runtime.step(ticks)
        return ControlResponse.success(
            cast(
                dict[str, JSONValue],
                {"ok": True, "runtime": state.to_json(), "ticks": ticks},
            )
        )

    def _handle_run_ticks(self, body: JSONBody) -> ControlResponse:
        """Handle the 'run_ticks' command (canonical contract)."""
        ticks = self._int_field(body, "ticks", default=100, minimum=1)
        state = self._runtime.run_ticks(ticks)
        return ControlResponse.success(
            cast(
                dict[str, JSONValue],
                {"ok": True, "runtime": state.to_json(), "ticks": ticks},
            )
        )

    def _handle_run(self, body: JSONBody) -> ControlResponse:
        """Handle the 'run' command."""
        loop_size = self._optional_int_field(body, "loop_size", minimum=1)
        state = self._runtime.run(loop_size=loop_size)
        return ControlResponse.success(
            cast(
                dict[str, JSONValue],
                {"ok": True, "runtime": state.to_json(), "loop_size": loop_size},
            )
        )

    def _handle_pause(self) -> ControlResponse:
        """Handle the 'pause' command."""
        state = self._runtime.pause()
        return ControlResponse.success(
            cast(
                dict[str, JSONValue],
                {"ok": True, "runtime": state.to_json(), "paused": True},
            )
        )

    def _handle_stop(self) -> ControlResponse:
        """Handle the 'stop' command."""
        state = self._runtime.stop()
        return ControlResponse.success(
            cast(
                dict[str, JSONValue],
                {"ok": True, "runtime": state.to_json(), "stopped": True},
            )
        )

    def _handle_configure(self, body: JSONBody) -> ControlResponse:
        """Handle the 'configure' command."""
        loop_size = self._optional_int_field(body, "loop_size", minimum=1)
        delay_ms = self._optional_float_field(body, "delay_ms", minimum=0.0)
        state = self._runtime.configure(loop_size=loop_size, delay_ms=delay_ms)
        return ControlResponse.success(
            cast(
                dict[str, JSONValue],
                {
                    "ok": True,
                    "runtime": state.to_json(),
                    "configured": {"loop_size": loop_size, "delay_ms": delay_ms},
                },
            )
        )

    def _handle_snapshot(self) -> ControlResponse:
        """Handle the 'snapshot' command."""
        state = self._runtime.request_snapshot()
        return ControlResponse.success(
            cast(
                dict[str, JSONValue],
                {"ok": True, "runtime": state.to_json(), "snapshot_requested": True},
            )
        )

    def _handle_self_organization(self, body: JSONBody) -> ControlResponse:
        """Handle the 'self_organization' command."""
        coordinator = self._self_organization
        if coordinator is None:
            raise CoordinatorUnavailableError(
                "Self-organization coordinator is not available."
            )

        enabled = self._optional_bool_field(body, "enabled")
        dry_run = self._optional_bool_field(body, "dry_run")

        coordinator.configure(enabled=enabled, dry_run=dry_run)

        return ControlResponse.success(
            {
                "ok": True,
                "self_organization": coordinator.snapshot().to_json(),
                "configured": {
                    "enabled": enabled if enabled is not None else "unchanged",
                    "dry_run": dry_run if dry_run is not None else "unchanged",
                },
            }
        )

    # =========================================================================
    # Field Validation Helpers
    # =========================================================================

    @staticmethod
    def _int_field(
        body: JSONBody,
        name: str,
        *,
        default: int,
        minimum: int,
    ) -> int:
        """Extract and validate a required integer field.

        Args:
            body: The request body.
            name: Field name.
            default: Default value if field is not present.
            minimum: Minimum allowed value.

        Returns:
            The validated integer value.

        Raises:
            TypeError: If the field is not an integer.
            ValueError: If the value is below the minimum.
        """
        value = body.get(name, default)
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"'{name}' must be an integer.")
        if value < minimum:
            raise ValueError(f"'{name}' must be >= {minimum}.")
        return int(value)

    @staticmethod
    def _optional_int_field(
        body: JSONBody,
        name: str,
        *,
        minimum: int,
    ) -> int | None:
        """Extract and validate an optional integer field.

        Args:
            body: The request body.
            name: Field name.
            minimum: Minimum allowed value.

        Returns:
            The validated integer value, or None if not present.

        Raises:
            TypeError: If the field is not an integer.
            ValueError: If the value is below the minimum.
        """
        value = body.get(name)
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"'{name}' must be an integer.")
        if value < minimum:
            raise ValueError(f"'{name}' must be >= {minimum}.")
        return int(value)

    @staticmethod
    def _optional_float_field(
        body: JSONBody,
        name: str,
        *,
        minimum: float,
    ) -> float | None:
        """Extract and validate an optional float field.

        Args:
            body: The request body.
            name: Field name.
            minimum: Minimum allowed value.

        Returns:
            The validated float value, or None if not present.

        Raises:
            TypeError: If the field is not numeric.
            ValueError: If the value is below the minimum.
        """
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
        body: JSONBody,
        name: str,
    ) -> bool | None:
        """Extract and validate an optional boolean field.

        Args:
            body: The request body.
            name: Field name.

        Returns:
            The validated boolean value, or None if not present.

        Raises:
            TypeError: If the field is not boolean.
        """
        value = body.get(name)
        if value is None:
            return None
        if not isinstance(value, bool):
            raise TypeError(f"'{name}' must be boolean.")
        return value

    @staticmethod
    def _optional_string_field(
        body: JSONBody,
        name: str,
        *,
        allowed_values: list[str] | None = None,
    ) -> str | None:
        """Extract and validate an optional string field.

        Args:
            body: The request body.
            name: Field name.
            allowed_values: Optional list of allowed values.

        Returns:
            The validated string value, or None if not present.

        Raises:
            TypeError: If the field is not a string.
            ValueError: If the value is not in allowed_values.
        """
        value = body.get(name)
        if value is None:
            return None
        if not isinstance(value, str):
            raise TypeError(f"'{name}' must be a string.")
        if allowed_values is not None and value not in allowed_values:
            raise ValueError(f"'{name}' must be one of: {', '.join(allowed_values)}")
        return value


# ============================================================================
# Factory Function
# ============================================================================


def create_control_service(
    runtime: RuntimeController,
    self_organization: SelfOrganizationCoordinator | None = None,
) -> DashboardControlService:
    """Create a configured DashboardControlService.

    Args:
        runtime: The runtime controller instance.
        self_organization: Optional self-organization coordinator.

    Returns:
        Configured DashboardControlService instance.

    Example:
        >>> service = create_control_service(runtime_controller)
        >>> response = service.execute({"action": "step", "ticks": 5})
    """
    return DashboardControlService(runtime, self_organization)


# ============================================================================
# Integration Helper
# ============================================================================


def control_response_to_http(
    response: ControlResponse,
) -> tuple[int, dict[str, JSONValue]]:
    """Convert a ControlResponse to HTTP status and body.

    This helper is useful for integrating with HTTP frameworks.

    Args:
        response: The control response.

    Returns:
        A tuple of (status_code, body_dict).
    """
    return response.status, response.to_json()


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "ControlAction",
    "ControlError",
    "ControlResponse",
    "CoordinatorUnavailableError",
    "DashboardControlService",
    "UnknownActionError",
    "ValidationError",
    "control_response_to_http",
    "create_control_service",
]
