"""Typed read-only signals emitted by the homeostasis subsystem."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HomeostasisSignal:
    """Aggregated homeostasis state exposed to higher-level policies.

    This object is observational only. Consumers must not mutate the
    neural network through this signal.
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
