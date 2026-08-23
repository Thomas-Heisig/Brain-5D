"""Typed adapters from runtime subsystem statistics to dashboard models.

This module provides type-safe conversion functions that transform raw subsystem
statistics into the immutable data contracts expected by the dashboard.
All adapters include error handling and graceful fallbacks.
"""

from __future__ import annotations

from typing import Protocol

from .models import HomeostasisMetrics, SpikeMetrics, StructuralMetrics

# ============================================================================
# Protocols (Type Contracts)
# ============================================================================


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


class StructuralStatsLike(Protocol):
    """Fields consumed from the structural plasticity engine stats snapshot."""

    neuron_count: int
    synapse_count: int
    new_neurons: int
    pruned_neurons: int
    new_synapses: int
    pruned_synapses: int
    growth_budget: float
    used_budget: float
    structural_changes: int


class SpikeStatsLike(Protocol):
    """Fields consumed from the spike recording stats snapshot."""

    total_spikes: int
    active_neurons: int
    mean_firing_rate_hz: float
    burst_index: float
    synchrony: float
    spike_count_last_tick: int


# ============================================================================
# Adapter Functions
# ============================================================================


def homeostasis_metrics(stats: HomeostasisStatsLike | None) -> HomeostasisMetrics:
    """Convert regulator statistics into the immutable dashboard contract.

    Args:
        stats: Statistics snapshot from the homeostasis engine, or None.

    Returns:
        HomeostasisMetrics object with safe defaults for missing values.
    """
    if stats is None:
        return HomeostasisMetrics(
            enabled=False,
            target_rate_hz=0.0,
            actual_rate_hz=0.0,
            rate_error_hz=0.0,
            mean_rate_hz=0.0,
            mean_rate_error_hz=0.0,
            mean_threshold_adaptation=0.0,
            target_energy=0.0,
            mean_energy=0.0,
            mean_energy_error=0.0,
            active_neurons=0,
            updates=0,
        )

    return HomeostasisMetrics(
        enabled=bool(stats.enabled),
        target_rate_hz=float(stats.target_rate_hz),
        actual_rate_hz=float(stats.mean_rate_hz),
        rate_error_hz=float(stats.mean_rate_error_hz),
        mean_rate_hz=float(stats.mean_rate_hz),
        mean_rate_error_hz=float(stats.mean_rate_error_hz),
        mean_threshold_adaptation=float(stats.mean_threshold_adaptation),
        target_energy=float(stats.target_energy),
        mean_energy=float(stats.mean_energy),
        mean_energy_error=float(stats.mean_energy_error),
        active_neurons=int(stats.active_neurons),
        updates=int(stats.updates),
    )


def structural_metrics(stats: StructuralStatsLike | None) -> StructuralMetrics:
    """Convert structural plasticity statistics into dashboard model.

    Args:
        stats: Statistics snapshot from the structural plasticity engine, or None.

    Returns:
        StructuralMetrics object with safe defaults for missing values.
    """
    if stats is None:
        return StructuralMetrics(
            neuron_count=0,
            synapse_count=0,
            new_neurons=0,
            pruned_neurons=0,
            new_synapses=0,
            pruned_synapses=0,
            growth_budget=0.0,
            used_budget=0.0,
            structural_changes=0,
        )

    return StructuralMetrics(
        neuron_count=int(stats.neuron_count),
        synapse_count=int(stats.synapse_count),
        new_neurons=int(stats.new_neurons),
        pruned_neurons=int(stats.pruned_neurons),
        new_synapses=int(stats.new_synapses),
        pruned_synapses=int(stats.pruned_synapses),
        growth_budget=float(stats.growth_budget),
        used_budget=float(stats.used_budget),
        structural_changes=int(stats.structural_changes),
    )


def spike_metrics(stats: SpikeStatsLike | None) -> SpikeMetrics:
    """Convert spike recording statistics into dashboard model.

    Args:
        stats: Statistics snapshot from the spike recorder, or None.

    Returns:
        SpikeMetrics object with safe defaults for missing values.
    """
    if stats is None:
        return SpikeMetrics(
            total_spikes=0,
            active_neurons=0,
            mean_firing_rate_hz=0.0,
            burst_index=0.0,
            synchrony=0.0,
            spike_count_last_tick=0,
        )

    return SpikeMetrics(
        total_spikes=int(stats.total_spikes),
        active_neurons=int(stats.active_neurons),
        mean_firing_rate_hz=float(stats.mean_firing_rate_hz),
        burst_index=float(stats.burst_index),
        synchrony=float(stats.synchrony),
        spike_count_last_tick=int(stats.spike_count_last_tick),
    )


# ============================================================================
# Aggregated Adapter
# ============================================================================


def aggregate_metrics(
    homeostasis: HomeostasisStatsLike | None = None,
    structural: StructuralStatsLike | None = None,
    spikes: SpikeStatsLike | None = None,
) -> dict[str, HomeostasisMetrics | StructuralMetrics | SpikeMetrics]:
    """Aggregate all metrics into a single dictionary.

    Useful for batch conversion when the dashboard needs a full snapshot.

    Args:
        homeostasis: Homeostasis engine statistics.
        structural: Structural plasticity engine statistics.
        spikes: Spike recorder statistics.

    Returns:
        Dictionary with 'homeostasis', 'structural', and 'spikes' keys.
    """
    return {
        "homeostasis": homeostasis_metrics(homeostasis),
        "structural": structural_metrics(structural),
        "spikes": spike_metrics(spikes),
    }


# ============================================================================
# Validation Helpers
# ============================================================================


def sanitize_float(value: float | None, default: float = 0.0) -> float:
    """Sanitize a float value, replacing None with default."""
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def sanitize_int(value: int | None, default: int = 0) -> int:
    """Sanitize an integer value, replacing None with default."""
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def sanitize_bool(value: bool | None, default: bool = False) -> bool:
    """Sanitize a boolean value, replacing None with default."""
    if value is None:
        return default
    try:
        return bool(value)
    except (TypeError, ValueError):
        return default
