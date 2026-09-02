"""Fail-closed authorization and safety boundary for embodiment I/O."""

from __future__ import annotations

from dataclasses import dataclass, field

from .actuator import ActuatorAdapter
from .audit import ActionAuditTrail
from .connections import ConnectionDescriptor
from .environment import EnvironmentAdapter
from .models import ActionCommand, ActuatorResult, EnvironmentObservation, SensorFrame
from .sensor import SensorAdapter


@dataclass(slots=True)
class ControlledSensorAdapter:
    """Fail-closed authorization boundary for sensor sampling."""

    sensor: SensorAdapter
    descriptor: ConnectionDescriptor

    def sample(self, tick: int) -> SensorFrame | None:
        if (
            not self.descriptor.available
            or not self.descriptor.authorized
            or not self.descriptor.active
            or not self.sensor.active
        ):
            return None
        if self.sensor.modality not in self.descriptor.modalities:
            return None
        return self.sensor.sample(tick)


@dataclass(slots=True)
class ControlledEmbodimentAgent:
    """Execute only authorized, capable and rate-limited external actions."""

    environment: EnvironmentAdapter
    actuator: ActuatorAdapter
    descriptor: ConnectionDescriptor
    audit: ActionAuditTrail = field(default_factory=ActionAuditTrail)
    max_actions_per_tick: int = 1
    require_human_override: bool = False
    _emergency_stopped: bool = False
    _approved_override_ticks: set[int] = field(default_factory=set[int])
    _calls_by_tick: dict[int, int] = field(default_factory=dict[int, int])

    def __post_init__(self) -> None:
        if self.max_actions_per_tick <= 0:
            raise ValueError("max_actions_per_tick must be positive")

    def reset(self, seed: int | None = None) -> EnvironmentObservation:
        return self.environment.reset(seed)

    def emergency_stop(self) -> None:
        self._emergency_stopped = True

    def clear_emergency_stop(self, *, human_approved: bool) -> None:
        if not human_approved:
            raise PermissionError("human approval is required to clear emergency stop")
        self._emergency_stopped = False

    def approve_override(self, tick: int, *, human_approved: bool) -> None:
        if not human_approved:
            raise PermissionError("human approval is required for override")
        self._approved_override_ticks.add(tick)

    def step(self, command: ActionCommand) -> EnvironmentObservation | None:
        result, reason = self._authorize(command)
        if result is not None:
            self.audit.append(
                self.descriptor.connection_id,
                command,
                result,
                accepted=False,
                reason=reason,
            )
            return None
        actuator_result = self.actuator.apply(command)
        self.audit.append(
            self.descriptor.connection_id,
            command,
            actuator_result,
            accepted=actuator_result.accepted,
            reason="accepted" if actuator_result.accepted else actuator_result.message,
        )
        if not actuator_result.accepted:
            return None
        self._calls_by_tick[command.tick] = self._calls_by_tick.get(command.tick, 0) + 1
        return self.environment.step(command)

    def _authorize(self, command: ActionCommand) -> tuple[ActuatorResult | None, str]:
        if self._emergency_stopped:
            return ActuatorResult(False, "emergency stop active"), "emergency_stop"
        if not self.descriptor.available or not self.descriptor.authorized:
            return ActuatorResult(False, "actuator is not authorized"), "unauthorized"
        if not self.descriptor.active or not self.actuator.active:
            return ActuatorResult(False, "actuator is inactive"), "inactive"
        if command.action not in self.descriptor.capabilities:
            return (
                ActuatorResult(False, "capability is not granted"),
                "capability_denied",
            )
        if (
            self.require_human_override
            and command.tick not in self._approved_override_ticks
        ):
            return ActuatorResult(False, "human override required"), "override_required"
        if self._calls_by_tick.get(command.tick, 0) >= self.max_actions_per_tick:
            return ActuatorResult(False, "rate limit exceeded"), "rate_limited"
        return None, ""
