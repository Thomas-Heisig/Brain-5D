"""Small orchestration shell for environment episodes.

The agent deliberately contains no autonomous external-action policy yet.  It
only executes explicitly supplied commands through a configured environment.
"""

from __future__ import annotations

from dataclasses import dataclass

from .environment import EnvironmentAdapter
from .models import ActionCommand, EmbodimentMetrics, EnvironmentObservation


@dataclass(slots=True)
class EmbodimentAgent:
    """Track an environment loop while policy learning remains external."""

    environment: EnvironmentAdapter
    episode: int = 0
    episode_reward: float = 0.0
    last_observation: EnvironmentObservation | None = None
    last_action: ActionCommand | None = None

    def reset(self, seed: int | None = None) -> EnvironmentObservation:
        """Start a new environment episode."""
        self.episode += 1
        self.episode_reward = 0.0
        self.last_action = None
        self.last_observation = self.environment.reset(seed)
        return self.last_observation

    def step(self, action: ActionCommand) -> EnvironmentObservation:
        """Apply an explicit action and capture its feedback."""
        observation = self.environment.step(action)
        self.last_action = action
        self.last_observation = observation
        self.episode_reward += observation.reward
        return observation

    def metrics(self) -> EmbodimentMetrics:
        """Build a dashboard-ready read-only metrics snapshot."""
        observation = self.last_observation
        action = self.last_action
        return EmbodimentMetrics(
            environment_kind=self.environment.kind.value,
            episode=self.episode,
            episode_reward=self.episode_reward,
            last_reward=0.0 if observation is None else observation.reward,
            last_action="" if action is None else action.action,
        )
