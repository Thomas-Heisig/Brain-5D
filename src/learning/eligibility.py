"""Eligibility traces for Brain 5D Sprint 2B.

The trace is updated lazily. Mathematically this is equivalent to decaying it
on every tick, but it avoids O(E) work across all synapses when only a small
fraction of the network spikes.

Eligibility traces are used in three-factor (reward-modulated) learning to
bridge the temporal gap between a spike event and a delayed reward signal.
The trace accumulates recent activity and decays exponentially over time.

Design Principles:
1. Lazy Update – The trace is only decayed when read or updated, not on every tick.
2. Monotonic Tick Order – Ticks must be non-decreasing for each trace.
3. Exponential Decay – Decay follows `exp(-dt / tau_ticks)`.
4. Thread-Safe by Design – Immutable read/write pattern with single-threaded access.

Example:
    >>> from src.learning import EligibilityTrace
    >>> trace = EligibilityTrace(tau_ticks=200.0)
    >>> trace.add(0.5, tick=10)   # Add 0.5 at tick 10
    >>> trace.add(0.3, tick=20)   # Add 0.3 at tick 20 (decayed from 10 to 20)
    >>> trace.read(tick=30)       # Read value at tick 30 (further decayed)
    >>> trace.reset()             # Reset to zero
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

# ============================================================================
# Eligibility Trace
# ============================================================================


@dataclass(slots=True)
class EligibilityTrace:
    """Exponentially decaying eligibility trace.

    The trace implements lazy decay: it only decays when explicitly advanced
    to a new tick. This is mathematically equivalent to decaying on every tick
    but significantly more efficient when only a fraction of traces are used.

    The trace value represents accumulated synaptic activity that can be
    used for reward-modulated plasticity. It decays exponentially with
    time constant `tau_ticks`.

    Attributes:
        tau_ticks: Decay time constant in simulation ticks (must be > 0).
        value: Current trace value (decayed).
        last_tick: Last tick to which the trace was advanced, or None if never.

    Example:
        >>> trace = EligibilityTrace(tau_ticks=100.0)
        >>> trace.add(1.0, tick=0)      # value = 1.0
        >>> trace.add(0.5, tick=10)     # decays from 0 to 10, then adds 0.5
        >>> trace.read(tick=20)         # decays from 10 to 20
        >>> trace.reset()               # resets to zero
    """

    tau_ticks: float = 200.0
    value: float = 0.0
    last_tick: int | None = None

    def __post_init__(self) -> None:
        """Validate the trace parameters after initialization."""
        if self.tau_ticks <= 0.0:
            raise ValueError(f"tau_ticks must be > 0, got {self.tau_ticks}")
        if not math.isfinite(self.tau_ticks):
            raise ValueError("tau_ticks must be finite")

    # ========================================================================
    # Core Methods
    # ========================================================================

    def advance(self, tick: int) -> float:
        """Decay the trace up to ``tick`` and return the current value.

        This method applies exponential decay from the last tick to the
        requested tick. If the trace has never been advanced, the value
        remains unchanged.

        Args:
            tick: The current simulation tick (must be >= 0 and monotonic).

        Returns:
            The trace value after advancing to the given tick.

        Raises:
            TypeError: If tick is not an integer.
            ValueError: If tick is negative or less than the last tick.

        Example:
            >>> trace = EligibilityTrace(tau_ticks=100.0)
            >>> trace.value = 1.0
            >>> trace.advance(tick=10)   # decays from 0 to 10
            0.9048...
        """
        self._validate_tick(tick)

        if self.last_tick is None:
            self.last_tick = tick
            return self.value

        if tick < self.last_tick:
            raise ValueError(
                f"tick must be monotonic: last_tick={self.last_tick}, tick={tick}"
            )

        dt = tick - self.last_tick
        if dt > 0:
            self.value *= math.exp(-dt / self.tau_ticks)
            self.last_tick = tick

        return self.value

    def add(self, amount: float, tick: int) -> float:
        """Advance to ``tick``, add ``amount`` and return the new trace value.

        This is the primary method for updating the trace: it first decays
        to the current tick, then adds the specified amount.

        Args:
            amount: The value to add to the trace (can be positive or negative).
            tick: The current simulation tick (must be >= 0 and monotonic).

        Returns:
            The new trace value after decay and addition.

        Example:
            >>> trace = EligibilityTrace(tau_ticks=100.0)
            >>> trace.add(1.0, tick=0)      # value = 1.0
            >>> trace.add(0.5, tick=10)     # decays to 0.9048, then adds 0.5 -> 1.4048
        """
        self.advance(tick)
        self.value += float(amount)
        return self.value

    def read(self, tick: int | None = None) -> float:
        """Return the trace value, optionally decayed to ``tick`` first.

        This method reads the trace without modifying it (except for decay).
        If no tick is provided, returns the current value without any update.

        Args:
            tick: Optional tick to advance to before reading.

        Returns:
            The trace value at the given tick (or current value).

        Example:
            >>> trace = EligibilityTrace(tau_ticks=100.0)
            >>> trace.value = 1.0
            >>> trace.read(tick=10)   # decays to 0.9048
            0.9048...
        """
        if tick is not None:
            self.advance(tick)
        return self.value

    def reset(self) -> None:
        """Reset the trace value and timestamp to the initial state.

        After reset, the trace has value 0.0 and no last_tick.
        This is useful between learning episodes.

        Example:
            >>> trace = EligibilityTrace()
            >>> trace.add(1.0, tick=0)
            >>> trace.reset()
            >>> trace.value
            0.0
        """
        self.value = 0.0
        self.last_tick = None

    def copy(self) -> EligibilityTrace:
        """Create a deep copy of this trace.

        Returns:
            A new EligibilityTrace instance with the same state.

        Example:
            >>> trace = EligibilityTrace(tau_ticks=100.0, value=0.5, last_tick=10)
            >>> copy = trace.copy()
            >>> copy.value == trace.value
            True
        """
        return EligibilityTrace(
            tau_ticks=self.tau_ticks,
            value=self.value,
            last_tick=self.last_tick,
        )

    # ========================================================================
    # Serialization
    # ========================================================================

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization.

        Returns:
            A dictionary with all trace state.

        Example:
            >>> trace = EligibilityTrace(tau_ticks=100.0, value=0.5, last_tick=10)
            >>> trace.to_dict()
            {'tau_ticks': 100.0, 'value': 0.5, 'last_tick': 10}
        """
        return {
            "tau_ticks": self.tau_ticks,
            "value": self.value,
            "last_tick": self.last_tick,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EligibilityTrace:
        """Deserialize from a dictionary.

        Args:
            data: Dictionary with trace state.

        Returns:
            A new EligibilityTrace instance.

        Example:
            >>> data = {'tau_ticks': 100.0, 'value': 0.5, 'last_tick': 10}
            >>> trace = EligibilityTrace.from_dict(data)
            >>> trace.value
            0.5
        """
        return cls(
            tau_ticks=data.get("tau_ticks", 200.0),
            value=data.get("value", 0.0),
            last_tick=data.get("last_tick"),
        )

    # ========================================================================
    # Validation
    # ========================================================================

    @staticmethod
    def _validate_tick(tick: int) -> None:
        """Validate a tick value.

        Args:
            tick: The tick value to validate.

        Raises:
            ValueError: If tick is negative.
        """
        if tick < 0:
            raise ValueError(f"tick must be >= 0, got {tick}")

    # ========================================================================
    # String Representation
    # ========================================================================

    def __repr__(self) -> str:
        """Return a string representation of the trace."""
        return (
            f"EligibilityTrace(tau={self.tau_ticks}, "
            f"value={self.value:.6f}, "
            f"last_tick={self.last_tick})"
        )


# ============================================================================
# Factory Function
# ============================================================================


def create_eligibility_trace(tau_ticks: float = 200.0) -> EligibilityTrace:
    """Create a new eligibility trace with the given time constant.

    This is a convenience factory function for creating EligibilityTrace
    instances.

    Args:
        tau_ticks: Decay time constant in ticks (must be > 0).

    Returns:
        A new EligibilityTrace instance.

    Example:
        >>> trace = create_eligibility_trace(tau_ticks=150.0)
        >>> trace.add(1.0, tick=0)
    """
    return EligibilityTrace(tau_ticks=tau_ticks)


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "EligibilityTrace",
    "create_eligibility_trace",
]
