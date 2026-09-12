"""Scientific metrics derived from live MHRN telemetry.

Only values derivable from the live network and the retained telemetry window
are returned as measured. Metrics requiring longer histories, controls, or
external baselines remain explicitly unavailable.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from statistics import mean, pstdev
from typing import Any

from src.core.spatial_index import unpack_coords

from .live_projection import ActivityWindowAccumulator
from .models import JSONValue


def _finite(value: float | int | None) -> float | int | None:
    if value is None:
        return None
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def _summary(values: list[float]) -> dict[str, JSONValue]:
    if not values:
        return {"available": False, "value": None, "n": 0}
    average = mean(values)
    deviation = pstdev(values) if len(values) > 1 else 0.0
    return {
        "available": True,
        "value": _finite(average),
        "std": _finite(deviation),
        "n": len(values),
    }


def _coefficient_of_variation(values: list[float]) -> dict[str, JSONValue]:
    if len(values) < 2:
        return {"available": False, "value": None, "n": len(values)}
    average = mean(values)
    if average == 0:
        return {"available": False, "value": None, "n": len(values)}
    return {
        "available": True,
        "value": _finite(pstdev(values) / average),
        "n": len(values),
    }


def _victor_purpura(left: list[int], right: list[int], q: float) -> float:
    previous = [float(index) for index in range(len(right) + 1)]
    for left_index, left_tick in enumerate(left, start=1):
        current = [float(left_index)]
        for right_index, right_tick in enumerate(right, start=1):
            current.append(
                min(
                    current[-1] + 1.0,
                    previous[right_index] + 1.0,
                    previous[right_index - 1] + q * abs(left_tick - right_tick),
                )
            )
        previous = current
    return previous[-1]


def _van_rossum(left: list[int], right: list[int], tau_ticks: float) -> float:
    if not left and not right:
        return 0.0
    end = max(left + right)
    left_set = Counter(left)
    right_set = Counter(right)
    decay = math.exp(-1.0 / max(tau_ticks, 1.0))
    left_state = 0.0
    right_state = 0.0
    squared = 0.0
    for tick in range(min(left + right), end + 1):
        left_state = left_state * decay + left_set[tick]
        right_state = right_state * decay + right_set[tick]
        squared += (left_state - right_state) ** 2
    return math.sqrt(squared / max(tau_ticks, 1.0))


def _spike_metrics(
    events: list[tuple[int, tuple[int, ...]]],
) -> dict[str, JSONValue]:
    trains: dict[int, list[int]] = defaultdict(list)
    tick_counts: Counter[int] = Counter()
    for tick, neuron_ids in events:
        tick_counts[tick] = len(neuron_ids)
        for neuron_id in neuron_ids:
            trains[neuron_id].append(tick)

    intervals = [
        float(current - previous)
        for train in trains.values()
        for previous, current in zip(train, train[1:])
        if current > previous
    ]
    count_values = [float(count) for count in tick_counts.values()]
    mean_count = mean(count_values) if count_values else 0.0
    fano = (
        pstdev(count_values) ** 2 / mean_count
        if len(count_values) > 1 and mean_count > 0
        else None
    )

    train_values = list(trains.values())
    pair_values = [
        (left, right)
        for index, left in enumerate(train_values[:32])
        for right in train_values[index + 1 : 32]
    ]
    avalanche_sizes: list[int] = []
    current_avalanche = 0
    previous_tick: int | None = None
    for tick, count in sorted(tick_counts.items()):
        if count <= 0:
            continue
        if previous_tick is None or tick != previous_tick + 1:
            if current_avalanche:
                avalanche_sizes.append(current_avalanche)
            current_avalanche = 0
        current_avalanche += count
        previous_tick = tick
    if current_avalanche:
        avalanche_sizes.append(current_avalanche)

    branching_values = [
        tick_counts[next_tick] / tick_counts[tick]
        for tick, next_tick in zip(sorted(tick_counts), sorted(tick_counts)[1:])
        if next_tick == tick + 1 and tick_counts[tick] > 0
    ]
    return {
        "window": {
            "ticks": len(events),
            "start_tick": events[0][0] if events else None,
            "end_tick": events[-1][0] if events else None,
            "events": sum(len(neuron_ids) for _, neuron_ids in events),
        },
        "isi_ticks": _summary(intervals),
        "cv_isi": _coefficient_of_variation(intervals),
        "fano_factor": {
            "available": fano is not None,
            "value": _finite(fano),
            "n": len(count_values),
            "definition": "variance/mean of population spike counts per tick",
        },
        "burst_train_count": sum(1 for train in train_values if len(train) >= 3),
        "victor_purpura": {
            "available": bool(pair_values),
            "value": _finite(mean([_victor_purpura(a, b, 1.0) for a, b in pair_values])) if pair_values else None,
            "q_per_tick": 1.0,
            "pairs": len(pair_values),
        },
        "van_rossum": {
            "available": bool(pair_values),
            "value": _finite(mean([_van_rossum(a, b, 10.0) for a, b in pair_values])) if pair_values else None,
            "tau_ticks": 10.0,
            "pairs": len(pair_values),
        },
        "avalanche": {
            "available": bool(avalanche_sizes),
            "count": len(avalanche_sizes),
            "mean_size": _finite(mean(avalanche_sizes)) if avalanche_sizes else None,
            "max_size": max(avalanche_sizes) if avalanche_sizes else None,
        },
        "branching_parameter": {
            "available": bool(branching_values),
            "value": _finite(mean(branching_values)) if branching_values else None,
            "n": len(branching_values),
        },
        "population_entropy_bits": _population_entropy(count_values),
    }


def _population_entropy(values: list[float]) -> dict[str, JSONValue]:
    if not values:
        return {"available": False, "value": None, "n": 0}
    counts = Counter(values)
    total = len(values)
    entropy = -sum((count / total) * math.log2(count / total) for count in counts.values())
    return {"available": True, "value": _finite(entropy), "n": total}


def _topology_metrics(network: Any) -> dict[str, JSONValue]:
    neurons = getattr(network, "neurons", {})
    synapses = getattr(network, "synapses", {})
    neuron_count = len(neurons)
    out_degree: Counter[int] = Counter()
    in_degree: Counter[int] = Counter()
    weights: list[float] = []
    distances: list[int] = []
    edge_count = 0
    for source_id, synapse_list in synapses.items():
        for synapse in synapse_list:
            target_id = int(getattr(synapse, "target_id", 0))
            edge_count += 1
            out_degree[int(source_id)] += 1
            in_degree[target_id] += 1
            weights.append(float(getattr(synapse, "weight", 0.0)))
            source_coords = unpack_coords(int(source_id))
            target_coords = unpack_coords(target_id)
            distances.append(sum(abs(a - b) for a, b in zip(source_coords, target_coords)))
    density = edge_count / (neuron_count * max(neuron_count - 1, 1)) if neuron_count else None
    return {
        "synaptic_density": _finite(density),
        "mean_fan_out": _finite(edge_count / neuron_count) if neuron_count else None,
        "mean_fan_in": _finite(edge_count / neuron_count) if neuron_count else None,
        "max_fan_out": max(out_degree.values()) if out_degree else None,
        "max_fan_in": max(in_degree.values()) if in_degree else None,
        "weight": _summary(weights),
        "five_d": {
            "available": bool(distances),
            "mean_manhattan_synapse_distance": _finite(mean(distances)) if distances else None,
            "dimension_count": len(getattr(network, "dimensions", ())),
            "edge_count": edge_count,
        },
        "clustering_coefficient": None,
        "modularity": None,
        "small_worldness": None,
        "motif_count": None,
        "rich_club": None,
        "effective_connectivity": None,
        "information_flow": None,
    }


def build_scientific_metrics(
    network: Any,
    accumulator: ActivityWindowAccumulator | None,
    snapshot: Any,
    telemetry: dict[str, Any] | None,
) -> dict[str, JSONValue]:
    events = accumulator.recent_events() if accumulator is not None else []
    snapshot_json = snapshot.to_json()
    network_state = snapshot_json.get("network", {})
    if not isinstance(network_state, dict):
        network_state = {}
    spike_metrics = _spike_metrics(events)
    topology = _topology_metrics(network)
    topology["clustering_coefficient"] = network_state.get("clustering_coefficient")
    topology["mean_path_length"] = network_state.get("mean_path_length")
    return {
        "source": "live_runtime",
        "tick": getattr(network, "current_tick", snapshot_json.get("system", {}).get("tick", 0)),
        "network": snapshot_json.get("network", {}),
        "spike_trains": spike_metrics,
        "topology": topology,
        "criticality": {
            "avalanche": spike_metrics["avalanche"],
            "branching_parameter": spike_metrics["branching_parameter"],
            "lyapunov_exponent": None,
            "attractor_landscape": None,
            "dimensionality": None,
        },
        "learning": snapshot_json.get("learning", {}),
        "homeostasis": snapshot_json.get("homeostasis", {}),
        "experiment": snapshot_json.get("experiment", {}),
        "statistics": {
            "multi_seed": None,
            "confidence_intervals": None,
            "effect_sizes": None,
            "power": None,
            "null_models": None,
            "surrogate_data": None,
        },
        "provenance": {
            "telemetry": telemetry or {"status": "unavailable"},
            "unknown_policy": "Unavailable values are null and carry no measured claim.",
        },
    }