"""Population grouping helpers kept independent from the NeuralNetwork implementation."""

from __future__ import annotations

from collections.abc import Mapping

from .models import RegionActivity, SpikeSample


def build_region_activity(
    *,
    region_id: str,
    neuron_ids: tuple[int, ...],
    spikes: tuple[SpikeSample, ...],
    rates_hz: Mapping[int, float],
) -> RegionActivity:
    """Aggregate one region without retaining mutable SNN references."""
    region_set = set(neuron_ids)
    region_spikes = tuple(s for s in spikes if s.neuron_id in region_set)
    active = {s.neuron_id for s in region_spikes}
    mean_rate = (
        sum(rates_hz.get(neuron_id, 0.0) for neuron_id in neuron_ids) / len(neuron_ids)
        if neuron_ids
        else 0.0
    )
    return RegionActivity(
        region_id=region_id,
        neuron_count=len(neuron_ids),
        active_neurons=len(active),
        spike_count=len(region_spikes),
        mean_rate_hz=mean_rate,
    )
