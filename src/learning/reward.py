"""Reward signals for Brain 5D three-factor plasticity."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RewardSignal:
    """Immutable scalar reward emitted at one simulation tick."""

    value: float
    tick: int

    def __post_init__(self) -> None:
        if not math.isfinite(self.value):
            raise ValueError("reward value must be finite")
        if self.tick < 0:
            raise ValueError("reward tick must be >= 0")

    def due_tick(self, delay_ticks: int) -> int:
        """Return the tick at which this reward becomes effective."""
        if delay_ticks < 0:
            raise ValueError("delay_ticks must be >= 0")
        return self.tick + delay_ticks

    def is_due(self, current_tick: int, delay_ticks: int) -> bool:
        """Return whether the configured reward delay has elapsed."""
        if current_tick < 0:
            raise ValueError("current_tick must be >= 0")
        return current_tick >= self.due_tick(delay_ticks)
