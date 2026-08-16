"""Pure feature calculations used by the signal interpreter."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

from .models import SpikeSample


def population_rate_hz(
    spikes: Iterable[SpikeSample], *, neuron_count: int, duration_ms: float
) -> float:
    """Return population-averaged firing rate in hertz."""
    if neuron_count <= 0 or duration_ms <= 0.0:
        return 0.0
    spike_count = sum(1 for _ in spikes)
    seconds = duration_ms / 1000.0
    return spike_count / (neuron_count * seconds)


def burst_index(spikes: Iterable[SpikeSample]) -> float:
    """Return a bounded heuristic burst score based on same-tick spike concentration."""
    counts = Counter(sample.tick for sample in spikes)
    total = sum(counts.values())
    if total == 0:
        return 0.0
    peak = max(counts.values(), default=0)
    return min(1.0, peak / total)


def synchrony(spikes: Iterable[SpikeSample], *, neuron_count: int) -> float:
    """Return a bounded same-tick synchrony score for the observed population."""
    if neuron_count <= 0:
        return 0.0
    per_tick: dict[int, set[int]] = {}
    for sample in spikes:
        per_tick.setdefault(sample.tick, set()).add(sample.neuron_id)
    if not per_tick:
        return 0.0
    peak = max(len(ids) for ids in per_tick.values())
    return min(1.0, peak / neuron_count)
