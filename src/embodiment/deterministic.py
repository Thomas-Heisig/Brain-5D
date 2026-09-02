"""Deterministic environment used for the first Alpha.7 loop proof."""

from __future__ import annotations

from dataclasses import dataclass

from .environment import EnvironmentAdapter
from .models import ActionCommand, EnvironmentKind, EnvironmentObservation


@dataclass(slots=True)
class DeterministicTargetEnvironment(EnvironmentAdapter):
    """One-dimensional target task with deterministic seeded reset."""

    target: int = 3
    position: int = 0
    tick: int = 0

    @property
    def environment_id(self) -> str:
        return "deterministic-target-v1"

    @property
    def kind(self) -> EnvironmentKind:
        return EnvironmentKind.SIMULATED

    def reset(self, seed: int | None = None) -> EnvironmentObservation:
        self.position = 0 if seed is None else seed % 2
        self.tick = 0
        return self._observation(0.0)

    def step(self, action: ActionCommand) -> EnvironmentObservation:
        self.tick += 1
        if action.action == "right":
            self.position += 1
        elif action.action == "left":
            self.position -= 1
        reward = 1.0 if self.position == self.target else 0.0
        return self._observation(reward)

    def _observation(self, reward: float) -> EnvironmentObservation:
        return EnvironmentObservation(
            tick=self.tick,
            state={"position": self.position, "target": self.target},
            reward=reward,
            terminated=self.position == self.target,
        )
