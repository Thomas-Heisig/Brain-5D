"""Environment contracts for embodied Brain-5D experiments."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .models import ActionCommand, EnvironmentKind, EnvironmentObservation


@runtime_checkable
class EnvironmentAdapter(Protocol):
    """Reset/step contract shared by simulation, physical, and digital worlds."""

    @property
    def environment_id(self) -> str:
        """Return a stable environment identifier."""

    @property
    def kind(self) -> EnvironmentKind:
        """Return the environment category."""

    def reset(self, seed: int | None = None) -> EnvironmentObservation:
        """Start a new episode and return its initial observation."""

    def step(self, action: ActionCommand) -> EnvironmentObservation:
        """Advance the environment by applying one action."""
