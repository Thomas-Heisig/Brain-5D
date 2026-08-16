"""Actuator adapter contracts for controlled environment actions."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .models import ActionCommand, ActuatorResult


@runtime_checkable
class ActuatorAdapter(Protocol):
    """Minimal actuator interface used by the embodiment layer."""

    @property
    def actuator_id(self) -> str:
        """Return the stable actuator identifier."""
        ...

    @property
    def active(self) -> bool:
        """Return whether the actuator is currently available."""
        ...

    def apply(self, command: ActionCommand) -> ActuatorResult:
        """Apply one explicitly supplied action command."""
        ...
