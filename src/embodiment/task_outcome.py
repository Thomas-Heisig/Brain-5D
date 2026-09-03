"""Deterministic task outcome verification from environment observations."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from .models import EnvironmentObservation, JSONValue


def _empty_expected_state() -> dict[str, JSONValue]:
    return {}


@dataclass(frozen=True, slots=True)
class TaskOutcome:
    """Verified technical outcome; it is not a claim about internal state."""

    known: bool
    success: bool
    reward: float
    reason: str

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "known": self.known,
            "success": self.success,
            "reward": self.reward,
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class TaskOutcomeVerifier:
    """Derive task success and reward exclusively from observed environment data."""

    expected_state: Mapping[str, JSONValue] = field(
        default_factory=_empty_expected_state
    )
    success_reward: float = 1.0
    failure_reward: float = 0.0

    def __post_init__(self) -> None:
        if self.success_reward < self.failure_reward:
            raise ValueError("success_reward must be >= failure_reward")

    def verify(self, observation: EnvironmentObservation) -> TaskOutcome:
        """Return a deterministic outcome without trusting incoming reward values."""
        matches = all(
            observation.state.get(key) == value
            for key, value in self.expected_state.items()
        )
        success = observation.terminated and matches
        reason = "terminated state matched" if success else "task condition not met"
        reward = (
            (self.success_reward if success else self.failure_reward)
            if self.expected_state
            else observation.reward
        )
        return TaskOutcome(
            known=True,
            success=success,
            reward=reward,
            reason=reason,
        )


__all__ = ["TaskOutcome", "TaskOutcomeVerifier"]
