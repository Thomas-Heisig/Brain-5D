"""Typed, immutable models for deterministic SNN signal interpretation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SpikeSample:
    """One observed spike event used to construct a signal frame."""

    tick: int
    neuron_id: int


@dataclass(frozen=True, slots=True)
class RegionActivity:
    """Aggregated activity for a named or synthetic region."""

    region_id: str
    neuron_count: int
    active_neurons: int
    spike_count: int
    mean_rate_hz: float


@dataclass(frozen=True, slots=True)
class SignalFrame:
    """Deterministic feature view of SNN activity.

    This object is the only intended input from raw SNN activity into a future language
    organ. It deliberately carries measurements rather than mutable network objects.
    """

    tick_from: int
    tick_to: int
    neuron_ids: tuple[int, ...]
    population_rate_hz: float
    spike_count: int
    burst_index: float
    synchrony: float
    mean_energy: float
    mean_threshold_adaptation: float
    active_regions: tuple[RegionActivity, ...]
