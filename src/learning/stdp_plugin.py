"""Isolated pair-based STDP laboratory for Brain 5D Sprint 2A.

This module deliberately has no dependency on ``src.core``. It provides a
small, deterministic reference implementation that can be validated before
plasticity is connected to the production network in a later sprint.

The STDP implementation is pair-based and uses the standard asymmetric
rule (Song & Abbott, 2000). It supports:
- Pair-based STDP with separate LTP and LTD time constants
- Weight clamping with min and max bounds
- Tick-based timing with integer ticks
- Standalone validation before production integration

Design Principles:
1. No dependency on ``src.core`` – Fully isolated for testing.
2. Deterministic – Given the same tick sequence, produces the same updates.
3. Validated – Can be used to verify STDP behavior before network integration.

Example:
    >>> from src.learning.stdp_plugin import STDPParameters, STDPSynapse
    >>> params = STDPParameters(a_plus=0.1, a_minus=0.12, tau_plus=20.0, tau_minus=20.0)
    >>> synapse = STDPSynapse.from_parameters(weight=0.5, params=params)
    >>> synapse.pre_spike(tick=10)   # LTD if post spiked earlier
    >>> synapse.post_spike(tick=15)  # LTP if pre spiked earlier
    >>> print(synapse.weight)
    0.500...
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


# ============================================================================
# STDP Parameters
# ============================================================================

@dataclass(frozen=True, slots=True)
class STDPParameters:
    """Configuration for the asymmetric pair-based STDP rule.

    This parameter bundle implements the standard STDP rule from Song & Abbott (2000):
        LTP:  Δw = A+ * exp(-Δt / τ+)  for Δt > 0
        LTD:  Δw = -A- * exp(Δt / τ-)  for Δt < 0

    Attributes:
        a_plus: LTP amplitude (positive, default: 0.1).
        a_minus: LTD amplitude (positive, default: 0.12).
        tau_plus: LTP time constant in ticks (default: 20.0).
        tau_minus: LTD time constant in ticks (default: 20.0).
        min_weight: Minimum weight (default: 0.0).
        max_weight: Maximum weight (default: 1.0).
    """

    a_plus: float = 0.1
    a_minus: float = 0.12
    tau_plus: float = 20.0
    tau_minus: float = 20.0
    min_weight: float = 0.0
    max_weight: float = 1.0

    def __post_init__(self) -> None:
        """Validate parameters after initialization."""
        self._validate()

    def _validate(self) -> None:
        """Reject invalid parameter combinations."""
        if self.a_plus < 0.0:
            raise ValueError("a_plus must be >= 0")
        if self.a_minus < 0.0:
            raise ValueError("a_minus must be >= 0")
        if self.tau_plus <= 0.0:
            raise ValueError("tau_plus must be > 0")
        if self.tau_minus <= 0.0:
            raise ValueError("tau_minus must be > 0")
        if self.min_weight > self.max_weight:
            raise ValueError("min_weight must be <= max_weight")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "a_plus": self.a_plus,
            "a_minus": self.a_minus,
            "tau_plus": self.tau_plus,
            "tau_minus": self.tau_minus,
            "min_weight": self.min_weight,
            "max_weight": self.max_weight,
        }


# ============================================================================
# STDP Synapse
# ============================================================================

@dataclass(slots=True)
class STDPSynapse:
    """A single isolated synapse implementing nearest-neighbour pair STDP.

    This synapse implements nearest-neighbour STDP, where each spike is
    paired with the most recent spike from the other side.

    Spike processing:
        - ``pre_spike`` pairs an incoming presynaptic spike with the most
          recent postsynaptic spike and therefore produces LTD when POST
          occurred first (dt < 0).
        - ``post_spike`` pairs an incoming postsynaptic spike with the most
          recent presynaptic spike and therefore produces LTP when PRE
          occurred first (dt > 0).

    The returned value from each spike method is the *actually applied*
    weight change after clamping.

    Attributes:
        weight: Current synaptic weight.
        a_plus: LTP amplitude.
        a_minus: LTD amplitude.
        tau_plus: LTP time constant.
        tau_minus: LTD time constant.
        max_weight: Maximum weight (clamping upper bound).
        min_weight: Minimum weight (clamping lower bound).
        last_pre_spike: Tick of the last presynaptic spike, or None.
        last_post_spike: Tick of the last postsynaptic spike, or None.
    """

    weight: float
    a_plus: float = 0.1
    a_minus: float = 0.12
    tau_plus: float = 20.0
    tau_minus: float = 20.0
    max_weight: float = 1.0
    min_weight: float = 0.0
    last_pre_spike: int | None = None
    last_post_spike: int | None = None

    def __post_init__(self) -> None:
        """Validate parameters and initial weight."""
        self._validate_parameters()

        if not self.min_weight <= self.weight <= self.max_weight:
            raise ValueError(
                f"initial weight {self.weight} must be inside "
                f"[{self.min_weight}, {self.max_weight}]"
            )

    # ========================================================================
    # Factory Methods
    # ========================================================================

    @classmethod
    def from_parameters(cls, weight: float, params: STDPParameters) -> STDPSynapse:
        """Create a laboratory synapse from an immutable parameter bundle.

        Args:
            weight: Initial synaptic weight.
            params: STDP parameters bundle.

        Returns:
            A new STDPSynapse with the configured parameters.

        Example:
            >>> params = STDPParameters(a_plus=0.1, a_minus=0.12)
            >>> synapse = STDPSynapse.from_parameters(0.5, params)
        """
        return cls(
            weight=weight,
            a_plus=params.a_plus,
            a_minus=params.a_minus,
            tau_plus=params.tau_plus,
            tau_minus=params.tau_minus,
            min_weight=params.min_weight,
            max_weight=params.max_weight,
        )

    # ========================================================================
    # STDP Methods
    # ========================================================================

    def pre_spike(self, tick: int) -> float:
        """Register a presynaptic spike and apply LTD for an earlier POST spike.

        This implements the LTD branch of STDP: if a postsynaptic spike
        occurred before the presynaptic spike (dt < 0), the weight is
        depressed.

        Args:
            tick: The current tick (must be >= 0).

        Returns:
            The actually applied weight change (after clamping).

        Raises:
            ValueError: If tick is negative.
        """
        if tick < 0:
            raise ValueError("tick must be >= 0")
        delta_w = 0.0

        # LTD: POST before PRE (dt = t_post - t_pre < 0)
        if self.last_post_spike is not None:
            dt = self.last_post_spike - tick  # t_post - t_pre
            if dt < 0:
                delta_w = -self.a_minus * math.exp(dt / self.tau_minus)

        self.last_pre_spike = tick
        return self._apply_delta(delta_w)

    def post_spike(self, tick: int) -> float:
        """Register a postsynaptic spike and apply LTP for an earlier PRE spike.

        This implements the LTP branch of STDP: if a presynaptic spike
        occurred before the postsynaptic spike (dt > 0), the weight is
        potentiated.

        Args:
            tick: The current tick (must be >= 0).

        Returns:
            The actually applied weight change (after clamping).

        Raises:
            ValueError: If tick is negative.
        """
        if tick < 0:
            raise ValueError("tick must be >= 0")
        delta_w = 0.0

        # LTP: PRE before POST (dt = t_post - t_pre > 0)
        if self.last_pre_spike is not None:
            dt = tick - self.last_pre_spike  # t_post - t_pre
            if dt > 0:
                delta_w = self.a_plus * math.exp(-dt / self.tau_plus)

        self.last_post_spike = tick
        return self._apply_delta(delta_w)

    # ========================================================================
    # State Management
    # ========================================================================

    def reset_timing(self) -> None:
        """Forget spike timestamps without changing the current weight."""
        self.last_pre_spike = None
        self.last_post_spike = None

    def reset(self, weight: float | None = None) -> None:
        """Reset timestamps and optionally replace the synaptic weight.

        Args:
            weight: Optional new weight. If provided, must be within bounds.

        Raises:
            ValueError: If the new weight is outside [min_weight, max_weight].
        """
        if weight is not None:
            if not self.min_weight <= weight <= self.max_weight:
                raise ValueError(
                    f"reset weight {weight} must be inside "
                    f"[{self.min_weight}, {self.max_weight}]"
                )
            self.weight = weight
        self.reset_timing()

    def set_weight(self, weight: float) -> float:
        """Set the weight to a new value, clamping to bounds.

        Args:
            weight: Desired new weight.

        Returns:
            The actual weight after clamping.
        """
        old_weight = self.weight
        self.weight = max(self.min_weight, min(self.max_weight, weight))
        return self.weight - old_weight

    # ========================================================================
    # Serialization
    # ========================================================================

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "weight": self.weight,
            "a_plus": self.a_plus,
            "a_minus": self.a_minus,
            "tau_plus": self.tau_plus,
            "tau_minus": self.tau_minus,
            "max_weight": self.max_weight,
            "min_weight": self.min_weight,
            "last_pre_spike": self.last_pre_spike,
            "last_post_spike": self.last_post_spike,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> STDPSynapse:
        """Deserialize from a dictionary."""
        return cls(
            weight=data["weight"],
            a_plus=data.get("a_plus", 0.1),
            a_minus=data.get("a_minus", 0.12),
            tau_plus=data.get("tau_plus", 20.0),
            tau_minus=data.get("tau_minus", 20.0),
            max_weight=data.get("max_weight", 1.0),
            min_weight=data.get("min_weight", 0.0),
            last_pre_spike=data.get("last_pre_spike"),
            last_post_spike=data.get("last_post_spike"),
        )

    # ========================================================================
    # Internal Helpers
    # ========================================================================

    def _apply_delta(self, delta_w: float) -> float:
        """Apply a weight delta with clamping."""
        old_weight = self.weight
        unclamped = old_weight + delta_w
        self.weight = max(self.min_weight, min(self.max_weight, unclamped))
        return self.weight - old_weight

    def _validate_parameters(self) -> None:
        """Validate STDP parameters."""
        if self.a_plus < 0.0:
            raise ValueError("a_plus must be >= 0")
        if self.a_minus < 0.0:
            raise ValueError("a_minus must be >= 0")
        if self.tau_plus <= 0.0:
            raise ValueError("tau_plus must be > 0")
        if self.tau_minus <= 0.0:
            raise ValueError("tau_minus must be > 0")
        if self.min_weight > self.max_weight:
            raise ValueError("min_weight must be <= max_weight")

    # ========================================================================
    # String Representation
    # ========================================================================

    def __repr__(self) -> str:
        return (
            f"STDPSynapse(weight={self.weight:.4f}, "
            f"pre={self.last_pre_spike}, "
            f"post={self.last_post_spike})"
        )


# ============================================================================
# Factory Function
# ============================================================================

def create_stdp_synapse(
    weight: float = 0.5,
    a_plus: float = 0.1,
    a_minus: float = 0.12,
    tau_plus: float = 20.0,
    tau_minus: float = 20.0,
    min_weight: float = 0.0,
    max_weight: float = 1.0,
) -> STDPSynapse:
    """Create a STDP synapse with the given parameters.

    This is a convenience factory function for creating an STDPSynapse
    without explicitly instantiating the class.

    Args:
        weight: Initial weight (default: 0.5).
        a_plus: LTP amplitude (default: 0.1).
        a_minus: LTD amplitude (default: 0.12).
        tau_plus: LTP time constant (default: 20.0).
        tau_minus: LTD time constant (default: 20.0).
        min_weight: Minimum weight (default: 0.0).
        max_weight: Maximum weight (default: 1.0).

    Returns:
        A new STDPSynapse instance.

    Example:
        >>> synapse = create_stdp_synapse(weight=0.7, a_plus=0.15)
        >>> synapse.pre_spike(10)
        >>> synapse.post_spike(15)
    """
    return STDPSynapse(
        weight=weight,
        a_plus=a_plus,
        a_minus=a_minus,
        tau_plus=tau_plus,
        tau_minus=tau_minus,
        min_weight=min_weight,
        max_weight=max_weight,
    )


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "STDPParameters",
    "STDPSynapse",
    "create_stdp_synapse",
]