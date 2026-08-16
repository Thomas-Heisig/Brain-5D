"""Deterministic adapter from measured SNN data to an immutable SignalFrame."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from .features import burst_index, population_rate_hz, synchrony
from .models import RegionActivity, SignalFrame, SpikeSample
from .temporal import window_duration_ms


class SignalInterpreter:
    """Build SignalFrame values without owning or mutating the runtime loop."""

    def build_frame(
        self,
        *,
        tick_from: int,
        tick_to: int,
        dt_ms: float,
        neuron_ids: Sequence[int],
        spikes: Sequence[SpikeSample],
        energies: Mapping[int, float],
        threshold_adaptations: Mapping[int, float],
        active_regions: Sequence[RegionActivity] = (),
    ) -> SignalFrame:
        ids = tuple(int(value) for value in neuron_ids)
        samples = tuple(spikes)
        duration_ms = window_duration_ms(tick_from, tick_to, dt_ms=dt_ms)
        mean_energy = (
            sum(energies.get(neuron_id, 0.0) for neuron_id in ids) / len(ids)
            if ids
            else 0.0
        )
        mean_threshold = (
            sum(threshold_adaptations.get(neuron_id, 0.0) for neuron_id in ids)
            / len(ids)
            if ids
            else 0.0
        )
        return SignalFrame(
            tick_from=tick_from,
            tick_to=tick_to,
            neuron_ids=ids,
            population_rate_hz=population_rate_hz(
                samples, neuron_count=len(ids), duration_ms=duration_ms
            ),
            spike_count=len(samples),
            burst_index=burst_index(samples),
            synchrony=synchrony(samples, neuron_count=len(ids)),
            mean_energy=mean_energy,
            mean_threshold_adaptation=mean_threshold,
            active_regions=tuple(active_regions),
        )
