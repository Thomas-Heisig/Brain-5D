"""Typed adapters from runtime subsystem statistics to dashboard models."""

from __future__ import annotations

from typing import Protocol

from .models import HomeostasisMetrics


class HomeostasisStatsLike(Protocol):
    """Fields consumed from the homeostasis engine stats snapshot."""

    enabled: bool
    updates: int
    target_rate_hz: float
    mean_rate_hz: float
    mean_rate_error_hz: float
    mean_threshold_adaptation: float
    target_energy: float
    mean_energy: float
    mean_energy_error: float
    active_neurons: int


def homeostasis_metrics(stats: HomeostasisStatsLike) -> HomeostasisMetrics:
    """Convert regulator statistics into the immutable dashboard contract."""
    return HomeostasisMetrics(
        enabled=stats.enabled,
        target_rate_hz=stats.target_rate_hz,
        mean_rate_hz=stats.mean_rate_hz,
        mean_rate_error_hz=stats.mean_rate_error_hz,
        mean_threshold_adaptation=stats.mean_threshold_adaptation,
        target_energy=stats.target_energy,
        mean_energy=stats.mean_energy,
        mean_energy_error=stats.mean_energy_error,
        active_neurons=stats.active_neurons,
        updates=stats.updates,
    )
