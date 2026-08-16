"""Eligibility traces for Brain 5D Sprint 2B.

The trace is updated lazily. Mathematically this is equivalent to decaying it
on every tick, but it avoids O(E) work across all synapses when only a small
fraction of the network spikes.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(slots=True)
class EligibilityTrace:
    """Exponentially decaying eligibility trace.

    ``tau_ticks`` is the decay time constant in simulation ticks. ``add`` first
    advances the trace to the requested tick and then adds the event value.
    """

    tau_ticks: float = 200.0
    value: float = 0.0
    last_tick: int | None = None

    def __post_init__(self) -> None:
        if self.tau_ticks <= 0.0:
            raise ValueError("tau_ticks must be > 0")

    def advance(self, tick: int) -> float:
        """Decay the trace up to ``tick`` and return the current value."""
        self._validate_tick(tick)
        if self.last_tick is None:
            self.last_tick = tick
            return self.value
        if tick < self.last_tick:
            raise ValueError("tick must be monotonic")
        dt = tick - self.last_tick
        if dt:
            self.value *= math.exp(-dt / self.tau_ticks)
            self.last_tick = tick
        return self.value

    def add(self, amount: float, tick: int) -> float:
        """Advance to ``tick``, add ``amount`` and return the new trace value."""
        self.advance(tick)
        self.value += float(amount)
        return self.value

    def read(self, tick: int | None = None) -> float:
        """Return the trace, optionally decayed to ``tick`` first."""
        if tick is not None:
            self.advance(tick)
        return self.value

    def reset(self) -> None:
        self.value = 0.0
        self.last_tick = None

    @staticmethod
    def _validate_tick(tick: int) -> None:
        if not isinstance(tick, int):
            raise TypeError("tick must be an int")
        if tick < 0:
            raise ValueError("tick must be >= 0")
