"""Environment contracts for embodied MHRN experiments."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .models import ActionCommand, EnvironmentKind, EnvironmentObservation


@runtime_checkable
class EnvironmentAdapter(Protocol):
    """Reset/step contract shared by simulation, physical, and digital worlds."""

    @property
    def environment_id(self) -> str:
        """Return a stable environment identifier."""
        raise NotImplementedError

    @property
    def kind(self) -> EnvironmentKind:
        """Return the environment category."""
        raise NotImplementedError

    def reset(self, seed: int | None = None) -> EnvironmentObservation:
        """Start a new episode and return its initial observation."""
        raise NotImplementedError

    def step(self, action: ActionCommand) -> EnvironmentObservation:
        """Advance the environment by applying one action."""
        raise NotImplementedError
