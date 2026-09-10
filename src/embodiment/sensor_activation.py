"""Explicit, fail-closed lifecycle control for registered sensors."""

from __future__ import annotations

from dataclasses import dataclass
from time import time_ns
from typing import Callable

from .connections import ConnectionDescriptor, ConnectionKind, ConnectionManager


def _allow_sensor(_descriptor: ConnectionDescriptor) -> bool:
    """Default policy used only when no stricter caller policy is supplied."""
    return True


@dataclass(frozen=True, slots=True)
class SensorActivationAudit:
    """One requested sensor transition, including rejected requests."""

    tick: int
    timestamp_ns: int
    connection_id: str
    requested_state: str
    previous_state: str
    new_state: str
    operator_source: str
    result: str
    error: str | None

    def to_json(self) -> dict[str, object]:
        return {
            "tick": self.tick,
            "timestamp_ns": self.timestamp_ns,
            "connection_id": self.connection_id,
            "requested_state": self.requested_state,
            "previous_state": self.previous_state,
            "new_state": self.new_state,
            "operator_source": self.operator_source,
            "result": self.result,
            "error": self.error,
        }


class SensorActivationService:
    """Control sensor activation without creating a second connection registry."""

    def __init__(
        self,
        connections: ConnectionManager,
        *,
        safety_policy: Callable[[ConnectionDescriptor], bool] | None = None,
    ) -> None:
        self.connections = connections
        self.safety_policy: Callable[[ConnectionDescriptor], bool] = (
            safety_policy or _allow_sensor
        )
        self._audit: list[SensorActivationAudit] = []

    @property
    def audit(self) -> tuple[SensorActivationAudit, ...]:
        return tuple(self._audit)

    def sensors(self) -> tuple[ConnectionDescriptor, ...]:
        return tuple(
            item
            for item in self.connections.snapshot()
            if item.kind == ConnectionKind.SENSOR
        )

    def get(self, connection_id: str) -> ConnectionDescriptor | None:
        descriptor = self.connections.get(connection_id)
        return (
            descriptor
            if descriptor is not None and descriptor.kind == ConnectionKind.SENSOR
            else None
        )

    def set_enabled(
        self,
        connection_id: str,
        enabled: bool,
        *,
        tick: int = 0,
        operator_source: str = "dashboard",
    ) -> tuple[ConnectionDescriptor, SensorActivationAudit]:
        current = self.get(connection_id)
        if current is None:
            raise KeyError(connection_id)
        previous_state = (
            "ACTIVE"
            if current.active
            else ("DISABLED" if current.enabled else current.health)
        )
        requested_state = "ACTIVE" if enabled else "DISABLED"
        error: str | None = None
        result = "accepted"
        updated = current
        if enabled:
            if not current.available:
                error = "adapter unavailable: sensor was not detected"
            elif not current.configured or not current.adapter_id:
                error = "adapter unavailable: no configured sensor adapter"
            elif not current.authorized:
                error = "authorization required before sensor activation"
            elif not self.safety_policy(current):
                error = "safety policy denied sensor activation"
            if error is not None:
                result = "rejected"
                updated = self.connections.update(
                    connection_id,
                    active=False,
                    enabled=False,
                    health=(
                        current.health
                        if current.health != "UNAVAILABLE"
                        else "UNAVAILABLE"
                    ),
                    last_error=error,
                    message=error,
                )
            else:
                updated = self.connections.update(
                    connection_id,
                    active=True,
                    enabled=True,
                    status=current.status,
                    health="ACTIVE",
                    last_error=None,
                    message="Sensor adapter active.",
                )
        else:
            updated = self.connections.update(
                connection_id,
                active=False,
                enabled=False,
                health="DISABLED",
                last_error=None,
                message="Sensor activation disabled by operator.",
            )
        audit = SensorActivationAudit(
            tick=tick,
            timestamp_ns=time_ns(),
            connection_id=connection_id,
            requested_state=requested_state,
            previous_state=previous_state,
            new_state="ACTIVE" if updated.active else updated.health,
            operator_source=operator_source,
            result=result,
            error=error,
        )
        self._audit.append(audit)
        return updated, audit


__all__ = ["SensorActivationAudit", "SensorActivationService"]
