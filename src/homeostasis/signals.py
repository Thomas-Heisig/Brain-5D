"""Typed read-only signals emitted by the homeostasis subsystem.

This module defines the HomeostasisSignal dataclass, which provides
aggregated, read-only homeostasis state for higher-level policies.
Consumers must not mutate the neural network through this signal.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class HomeostasisSignal:
    """Aggregated homeostasis state exposed to higher-level policies.

    This object is observational only. Consumers must not mutate the
    neural network through this signal.

    Attributes:
        tick: Current simulation tick.
        neuron_count: Total number of neurons.
        target_rate_hz: Target firing rate (Hz).
        mean_rate_hz: Mean firing rate across all neurons.
        rate_variance_hz2: Variance of firing rates.
        rate_error_hz: Mean rate minus target rate (positive = too high).
        mean_threshold_adaptation: Mean adaptive threshold offset.
        mean_energy: Mean energy across all neurons.
        mean_energy_error: Target energy minus mean energy.
        low_rate_neurons: Number of neurons below 50% of target rate.
        high_rate_neurons: Number of neurons above 150% of target rate.
        low_energy_neurons: Number of neurons below energy threshold.
        high_energy_neurons: Number of neurons above energy threshold.
    """

    tick: int = 0
    neuron_count: int = 0

    target_rate_hz: float = 5.0
    mean_rate_hz: float = 0.0
    rate_variance_hz2: float = 0.0
    rate_error_hz: float = 0.0

    mean_threshold_adaptation: float = 0.0

    mean_energy: float = 0.0
    mean_energy_error: float = 0.0

    low_rate_neurons: int = 0
    high_rate_neurons: int = 0
    low_energy_neurons: int = 0
    high_energy_neurons: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization.

        Returns:
            A dictionary with all field names as keys.
        """
        return {
            "tick": self.tick,
            "neuron_count": self.neuron_count,
            "target_rate_hz": self.target_rate_hz,
            "mean_rate_hz": self.mean_rate_hz,
            "rate_variance_hz2": self.rate_variance_hz2,
            "rate_error_hz": self.rate_error_hz,
            "mean_threshold_adaptation": self.mean_threshold_adaptation,
            "mean_energy": self.mean_energy,
            "mean_energy_error": self.mean_energy_error,
            "low_rate_neurons": self.low_rate_neurons,
            "high_rate_neurons": self.high_rate_neurons,
            "low_energy_neurons": self.low_energy_neurons,
            "high_energy_neurons": self.high_energy_neurons,
        }

    def to_json(self) -> dict[str, Any]:
        """Alias for to_dict() for dashboard compatibility."""
        return self.to_dict()


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "HomeostasisSignal",
]
