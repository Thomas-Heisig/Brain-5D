"""Isolated pair-based STDP laboratory for Brain 5D Sprint 2A.

This module deliberately has no dependency on ``src.core``.  It provides a
small, deterministic reference implementation that can be validated before
plasticity is connected to the production network in a later sprint.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class STDPParameters:
    """Configuration for the asymmetric pair-based STDP rule."""

    a_plus: float = 0.1
    a_minus: float = 0.12
    tau_plus: float = 20.0
    tau_minus: float = 20.0
    min_weight: float = 0.0
    max_weight: float = 1.0

    def __post_init__(self) -> None:
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


@dataclass(slots=True)
class STDPSynapse:
    """A single isolated synapse implementing nearest-neighbour pair STDP.

    ``pre_spike`` pairs an incoming presynaptic spike with the most recent
    postsynaptic spike and therefore produces LTD when POST occurred first.

    ``post_spike`` pairs an incoming postsynaptic spike with the most recent
    presynaptic spike and therefore produces LTP when PRE occurred first.

    The returned value is the *actually applied* weight change after clamping.
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
        self._validate_parameters()
        if not self.min_weight <= self.weight <= self.max_weight:
            raise ValueError("initial weight must be inside [min_weight, max_weight]")

    @classmethod
    def from_parameters(cls, weight: float, params: STDPParameters) -> "STDPSynapse":
        """Create a laboratory synapse from an immutable parameter bundle."""
        return cls(
            weight=weight,
            a_plus=params.a_plus,
            a_minus=params.a_minus,
            tau_plus=params.tau_plus,
            tau_minus=params.tau_minus,
            min_weight=params.min_weight,
            max_weight=params.max_weight,
        )

    def pre_spike(self, tick: int) -> float:
        """Register PRE at ``tick`` and apply LTD for an earlier POST spike."""
        self._validate_tick(tick)
        delta_w = 0.0

        if self.last_post_spike is not None:
            dt = self.last_post_spike - tick  # t_post - t_pre
            if dt < 0:
                delta_w = -self.a_minus * math.exp(dt / self.tau_minus)

        self.last_pre_spike = tick
        return self._apply_delta(delta_w)

    def post_spike(self, tick: int) -> float:
        """Register POST at ``tick`` and apply LTP for an earlier PRE spike."""
        self._validate_tick(tick)
        delta_w = 0.0

        if self.last_pre_spike is not None:
            dt = tick - self.last_pre_spike  # t_post - t_pre
            if dt > 0:
                delta_w = self.a_plus * math.exp(-dt / self.tau_plus)

        self.last_post_spike = tick
        return self._apply_delta(delta_w)

    def reset_timing(self) -> None:
        """Forget spike timestamps without changing the current weight."""
        self.last_pre_spike = None
        self.last_post_spike = None

    def reset(self, weight: float | None = None) -> None:
        """Reset timestamps and optionally replace the synaptic weight."""
        if weight is not None:
            if not self.min_weight <= weight <= self.max_weight:
                raise ValueError("reset weight must be inside [min_weight, max_weight]")
            self.weight = weight
        self.reset_timing()

    def _apply_delta(self, delta_w: float) -> float:
        old_weight = self.weight
        unclamped = old_weight + delta_w
        self.weight = max(self.min_weight, min(self.max_weight, unclamped))
        return self.weight - old_weight

    def _validate_parameters(self) -> None:
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

    @staticmethod
    def _validate_tick(tick: int) -> None:
        if not isinstance(tick, int):
            raise TypeError("tick must be an int")
        if tick < 0:
            raise ValueError("tick must be >= 0")
