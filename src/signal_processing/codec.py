"""Serialization helpers for SignalFrame values."""

from __future__ import annotations

from typing import TypeAlias

from .models import SignalFrame

JSONScalar: TypeAlias = str | int | float | bool | None
JSONValue: TypeAlias = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]


def signal_frame_to_json(frame: SignalFrame) -> dict[str, JSONValue]:
    """Convert a signal frame to JSON-compatible data without exposing runtime objects."""
    return {
        "tick_from": frame.tick_from,
        "tick_to": frame.tick_to,
        "neuron_ids": list(frame.neuron_ids),
        "population_rate_hz": frame.population_rate_hz,
        "spike_count": frame.spike_count,
        "burst_index": frame.burst_index,
        "synchrony": frame.synchrony,
        "mean_energy": frame.mean_energy,
        "mean_threshold_adaptation": frame.mean_threshold_adaptation,
        "active_regions": [
            {
                "region_id": region.region_id,
                "neuron_count": region.neuron_count,
                "active_neurons": region.active_neurons,
                "spike_count": region.spike_count,
                "mean_rate_hz": region.mean_rate_hz,
            }
            for region in frame.active_regions
        ],
    }
