"""Reward signals for Brain 5D three-factor plasticity.

This module provides the RewardSignal dataclass, which represents an
immutable scalar reward emitted at a specific simulation tick.

Reward signals are used for three-factor plasticity (reward-modulated STDP),
where a reward signal modulates weight changes based on eligibility traces.

The reward signal is:
- Immutable – Once created, it cannot be modified.
- Tick-aligned – Associated with a specific simulation tick.
- Finite – Validates that the reward value is finite.

Design Principles:
1. Rewards are data, not commands – They represent a scalar value at a tick.
2. Immutable – Safe for concurrent use and debugging.
3. Delayed – Can be checked for due-ness with a configurable delay.

Example:
    >>> from src.learning.reward import RewardSignal, create_reward
    >>> reward = create_reward(value=1.0, tick=100)
    >>> reward.is_due(current_tick=105, delay_ticks=5)
    True
    >>> reward.is_due(current_tick=104, delay_ticks=5)
    False
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

# ============================================================================
# Reward Signal
# ============================================================================


@dataclass(frozen=True, slots=True)
class RewardSignal:
    """Immutable scalar reward emitted at one simulation tick.

    This dataclass represents a reward signal that can be used in
    three-factor plasticity rules. It is associated with a specific
    simulation tick and can be checked for due-ness with a delay.

    Attributes:
        value: The scalar reward value (must be finite).
        tick: The simulation tick at which the reward was emitted.

    Raises:
        ValueError: If the reward value is not finite or the tick is negative.

    Example:
        >>> reward = RewardSignal(value=0.5, tick=100)
        >>> reward.due_tick(delay_ticks=5)
        105
    """

    value: float
    tick: int

    def __post_init__(self) -> None:
        """Validate the reward signal after initialization."""
        if not math.isfinite(self.value):
            raise ValueError("reward value must be finite")
        if self.tick < 0:
            raise ValueError("reward tick must be >= 0")

    def due_tick(self, delay_ticks: int) -> int:
        """Return the tick at which this reward becomes effective.

        Args:
            delay_ticks: The number of ticks to delay the reward (must be >= 0).

        Returns:
            The tick at which the reward is due.

        Raises:
            ValueError: If delay_ticks is negative.

        Example:
            >>> reward = RewardSignal(1.0, 100)
            >>> reward.due_tick(5)
            105
        """
        if delay_ticks < 0:
            raise ValueError(f"delay_ticks must be >= 0, got {delay_ticks}")
        return self.tick + delay_ticks

    def is_due(self, current_tick: int, delay_ticks: int) -> bool:
        """Return whether the configured reward delay has elapsed.

        Args:
            current_tick: The current simulation tick (must be >= 0).
            delay_ticks: The number of ticks to delay the reward (must be >= 0).

        Returns:
            True if the reward is due at the current tick, False otherwise.

        Raises:
            ValueError: If current_tick is negative or delay_ticks is negative.

        Example:
            >>> reward = RewardSignal(1.0, 100)
            >>> reward.is_due(current_tick=105, delay_ticks=5)
            True
            >>> reward.is_due(current_tick=104, delay_ticks=5)
            False
        """
        if current_tick < 0:
            raise ValueError("current_tick must be >= 0")
        if delay_ticks < 0:
            raise ValueError("delay_ticks must be >= 0")
        return current_tick >= self.due_tick(delay_ticks)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization.

        Returns:
            A dictionary with the reward value and tick.

        Example:
            >>> reward = RewardSignal(1.0, 100)
            >>> reward.to_dict()
            {'value': 1.0, 'tick': 100}
        """
        return {
            "value": self.value,
            "tick": self.tick,
        }

    def __repr__(self) -> str:
        """Return a string representation of the reward signal."""
        return f"RewardSignal(value={self.value}, tick={self.tick})"


# ============================================================================
# Factory Function
# ============================================================================


def create_reward(value: float, tick: int) -> RewardSignal:
    """Create a reward signal with the given value and tick.

    This is a convenience factory function for creating RewardSignal
    instances.

    Args:
        value: The scalar reward value (must be finite).
        tick: The simulation tick at which the reward is emitted (must be >= 0).

    Returns:
        A new RewardSignal instance.

    Raises:
        ValueError: If the value is not finite or the tick is negative.

    Example:
        >>> reward = create_reward(0.5, 100)
        >>> print(reward)
        RewardSignal(value=0.5, tick=100)
    """
    return RewardSignal(value=value, tick=tick)


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "RewardSignal",
    "create_reward",
]
