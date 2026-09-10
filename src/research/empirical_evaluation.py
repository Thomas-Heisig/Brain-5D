"""Bounded exploratory experiments; execution never grants EVID authority.

Geometry changes connectivity, not the persisted five-coordinate neuron IDs.
Association probes use the native LearningEngine and a newly constructed SNN.
Brian2 is an optional, explicitly limited single-neuron numerical comparator.
"""

from __future__ import annotations

import hashlib
import importlib
import itertools
import json
import math
import random
import statistics
import time
from collections.abc import Mapping, Sequence
from dataclasses import replace
from typing import Any

from src.core import NeuralNetwork
from src.core.neuron import Neuron, NeuronConfig
from src.core.synapse import SynapseConfig
from src.experiments.learning_lab import train_learning_weights
from src.research.experiment_suite import ScientificRun

EVALUATION_SEEDS = tuple(range(20_001, 20_011))
DIMENSIONS = (2, 3, 4, 5, 6, 8)
ASSOCIATION_CONDITIONS = (
    "learning_on",
    "learning_off",
    "sham_replay",
    "weight_reset",
    "weight_shuffle",
)


def digest(value: object) -> str:
    """Hash a finite JSON value, not an interpretation or a success label."""
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def paired_summary(
    treatment: Sequence[float], control: Sequence[float], seed: int = 910
) -> dict[str, Any]:
    """Paired seed-level differences, percentile bootstrap and exact sign flips.

    This is exploratory inference. Trials within a seed are not replicates.
    Zero variance does not acquire a fabricated standardized effect size.
    """
    if len(treatment) != len(control) or len(treatment) < 2:
        raise ValueError("At least two complete matched seed pairs are required")
    delta = [float(a) - float(b) for a, b in zip(treatment, control)]
    if not all(math.isfinite(x) for x in delta):
        raise ValueError("Non-finite paired observation")
    mean = statistics.mean(delta)
    sd = statistics.stdev(delta)
    rng = random.Random(seed)
    samples = sorted(
        statistics.mean(rng.choices(delta, k=len(delta))) for _ in range(2000)
    )
    pvalue: float | None = None
    if len(delta) <= 16:
        observed = abs(sum(delta))
        extreme = sum(
            abs(sum(x * sign for x, sign in zip(delta, signs))) >= observed - 1e-12
            for signs in itertools.product((-1, 1), repeat=len(delta))
        )
        pvalue = extreme / (2 ** len(delta))
    return {
        "n_seed_pairs": len(delta),
        "mean_difference": mean,
        "bootstrap_percentile_95_ci": [samples[49], samples[1949]],
        "bootstrap_resamples": 2000,
        "bootstrap_seed": seed,
        "exact_two_sided_sign_flip_p": pvalue,
        "paired_standardized_effect_dz": mean / sd if sd > 0 else None,
        "degenerate_difference_variance": sd == 0,
        "unit": "independent_environment_and_initialization_seed",
        "interpretation": "exploratory; no automatic hypothesis or EVID acceptance",
    }


def holm_adjust(pvalues: Sequence[float]) -> list[float]:
    """Holm step-down adjustment within one declared comparison family."""
    if any(not math.isfinite(p) or not 0 <= p <= 1 for p in pvalues):
        raise ValueError("Invalid probability")
    result = [0.0] * len(pvalues)
    previous = 0.0
    for rank, index in enumerate(sorted(range(len(pvalues)), key=lambda i: pvalues[i])):
        previous = min(1.0, max(previous, (len(pvalues) - rank) * pvalues[index]))
        result[index] = previous
    return result


def dimensional_edges(
    seed: int,
    dimensions: int,
    neurons: int = 128,
    out_degree: int = 8,
    *,
    random_graph: bool = False,
) -> list[tuple[int, int, float, int]]:
    """Match N, directed edge count, out-degree, weight and delay multisets.

    The first D coordinates of the same seeded eight-coordinate cloud define
    nearest neighbours. In-degree/motifs are intentionally not held constant:
    they are consequences of this connectivity construction, not isolated causes.
    """
    if dimensions not in DIMENSIONS or not 1 <= out_degree < neurons:
        raise ValueError("Unsupported dimension or graph budget")
    rng = random.Random(seed)
    coordinates = [tuple(rng.random() for _ in range(8)) for _ in range(neurons)]
    edges: list[tuple[int, int, float, int]] = []
    for source in range(neurons):
        candidates = [index for index in range(neurons) if index != source]
        if random_graph:
            random.Random(seed * 1009 + source).shuffle(candidates)
        else:
            candidates.sort(
                key=lambda target: (
                    sum(
                        (coordinates[source][axis] - coordinates[target][axis]) ** 2
                        for axis in range(dimensions)
                    ),
                    target,
                )
            )
        for rank, target in enumerate(candidates[:out_degree]):
            edges.append((source, target, 20.0, 1 + rank % 4))
    return edges


def build_empirical_network(
    config: Mapping[str, Any], neurons: int, seed: int
) -> tuple[NeuralNetwork, list[int]]:
    values = dict(config)
    if not 1 <= neurons <= 256**5:
        raise ValueError("Neuron count exceeds the canonical five-axis ID space")
    # Canonical persisted IDs allocate eight bits to each coordinate.
    values["dimensions"] = [
        min(256, max(1, (neurons + 256**axis - 1) // 256**axis)) for axis in range(5)
    ]
    values["initial_neurons"] = 0
    values["simulation"] = {"max_delay": 20, "dt_ms": 1.0, "debug_invariants": True}
    net = NeuralNetwork(values, random.Random(seed))
    ids = [
        net.add_neuron(
            (
                index % 256,
                (index // 256) % 256,
                (index // 256**2) % 256,
                (index // 256**3) % 256,
                (index // 256**4) % 256,
            )
        )
        for index in range(neurons)
    ]
    return net, ids


def run_dimensional_ablation(
    config: Mapping[str, Any],
    seeds: tuple[int, ...] = EVALUATION_SEEDS,
    ticks: int = 256,
) -> list[ScientificRun]:
    """Compare actual D-guided graphs plus identical-graph label controls."""
    if ticks < 32:
        raise ValueError("At least 32 ticks are required")
    runs: list[ScientificRun] = []
    neurons = 128
    for seed in seeds:
        selected = random.Random(seed + 700_000).sample(range(neurons), 16)
        sources, outputs = selected[:8], set(selected[8:])
        fixed = dimensional_edges(seed, 5)
        cases = [
            (f"geometry_{dim}d", dim, dimensional_edges(seed, dim))
            for dim in DIMENSIONS
        ]
        cases += [(f"fixed_graph_label_{dim}d", dim, fixed) for dim in DIMENSIONS]
        cases.append(("random_graph", 5, dimensional_edges(seed, 5, random_graph=True)))
        for condition, dimensions, edges in cases:
            net, ids = build_empirical_network(config, neurons, seed)
            for source, target, weight, delay in edges:
                net.connect(
                    ids[source],
                    ids[target],
                    weight,
                    delay,
                    config=SynapseConfig(w_max=100.0),
                )
            reverse_ids = {value: index for index, value in enumerate(ids)}
            per_tick: list[int] = []
            output_spikes = 0
            active: set[int] = set()
            first_output_tick: int | None = None
            spike_trace: list[list[int]] = []
            started = time.perf_counter()
            for tick in range(ticks):
                if tick in (0, ticks // 2):
                    net.inject_current_batch({ids[index]: 100.0 for index in sources})
                result = net.step()
                observed = sorted(reverse_ids[value] for value in result.spike_ids)
                spike_trace.append(observed)
                active.update(observed)
                per_tick.append(len(observed))
                count = len(set(observed) & outputs)
                output_spikes += count
                if count and first_output_tick is None:
                    first_output_tick = tick
            elapsed = time.perf_counter() - started
            finite = all(
                math.isfinite(n.v) and math.isfinite(n.u) for n in net.neurons.values()
            )
            metrics = {
                "dimensions_external_geometry": dimensions,
                "core_id_dimensions": 5,
                "neurons": neurons,
                "synapses": len(edges),
                "out_degree": 8,
                "weight": 20.0,
                "delay_multiset_per_source": [1, 2, 3, 4, 1, 2, 3, 4],
                "ticks_executed": ticks,
                "total_spikes": sum(per_tick),
                "active_neuron_fraction": len(active) / neurons,
                "output_spikes": output_spikes,
                "first_output_tick": first_output_tick,
                "finite_state": finite,
                "spikes_per_tick": per_tick,
                "spike_trace": spike_trace,
                "response_digest": digest(spike_trace),
                "graph_digest": digest(edges),
                "edges": edges,
                "input_indices": sources,
                "output_indices": sorted(outputs),
                "simulation_seconds": elapsed,
                "learning_enabled": False,
                "interpretation_limit": "Propagation only, not task accuracy; N-D geometry creates edges but does not migrate 5D storage. In-degree and motifs are not matched.",
            }
            runs.append(
                ScientificRun(
                    "EXP-EVAL-DIM-001",
                    condition,
                    seed,
                    metrics,
                    digest(edges),
                    digest(spike_trace),
                )
            )
    return runs


def _association_probe(
    config: Mapping[str, Any],
    weights: Sequence[float],
    active: Sequence[int],
    injection_ticks: Sequence[int],
    seed: int,
) -> bool:
    net, ids = build_empirical_network(config, len(weights) + 1, seed)
    target = ids[-1]
    for index, weight in enumerate(weights):
        net.connect(ids[index], target, weight, 1, config=SynapseConfig(w_max=1.0))
    observed = False
    for tick in range(12):
        net.inject_current_batch(
            {
                ids[index]: 100.0
                for index, when in zip(active, injection_ticks)
                if when == tick
            }
        )
        observed = target in net.step().spike_ids or observed
    return observed


def run_association_generalization(
    config: Mapping[str, Any],
    seeds: tuple[int, ...] = EVALUATION_SEEDS,
) -> list[ScientificRun]:
    """Teacher-paired acquisition, then frozen positive/negative novel probes.

    Test episodes are not used by LearningEngine. The teacher is absent during
    every test. Off/sham/reset/permuted controls use the same held-out inputs.
    This is an engineered association task, not autonomous embodied learning.
    """
    runs: list[ScientificRun] = []
    for seed in seeds:
        rng = random.Random(seed)
        initial = rng.uniform(0.025, 0.075)
        count = rng.randint(44, 52)
        values = dict(config)
        exp = dict(values.get("learning_experiment", {}))
        exp.update(
            {
                "initial_weight": initial,
                "presynaptic_neurons": count,
                "drive_current": 100.0,
            }
        )
        values["learning_experiment"] = exp
        values["seed"] = seed
        test_rng = random.Random(seed + 800_000)
        trials: list[dict[str, Any]] = []
        for index in range(40):
            label = index % 2
            population = range(count) if label else range(count, 2 * count)
            admitted = test_rng.randint(count - 8, count)
            active = sorted(test_rng.sample(list(population), admitted))
            times = [test_rng.randrange(3) for _ in active]
            trials.append(
                {
                    "trial": index,
                    "label": label,
                    "active": active,
                    "injection_ticks": times,
                }
            )
        learned, engine, _ = train_learning_weights(values, "learning_on")
        off, off_engine, _ = train_learning_weights(values, "learning_off")
        sham, sham_engine, _ = train_learning_weights(values, "sham_replay")
        controls = {
            "learning_on": list(learned) + [initial] * count,
            "learning_off": list(off) + [initial] * count,
            "sham_replay": list(sham) + [initial] * count,
            "weight_reset": [initial] * (2 * count),
            "weight_shuffle": list(learned) + [initial] * count,
        }
        random.Random(seed + 900_000).shuffle(controls["weight_shuffle"])
        engines = {
            "learning_on": engine,
            "learning_off": off_engine,
            "sham_replay": sham_engine,
            "weight_reset": engine,
            "weight_shuffle": engine,
        }
        for condition, weights in controls.items():
            before = digest(weights)
            observations: list[dict[str, Any]] = []
            for trial in trials:
                predicted = _association_probe(
                    values, weights, trial["active"], trial["injection_ticks"], seed
                )
                observations.append(
                    {
                        **trial,
                        "predicted": int(predicted),
                        "correct": int(predicted) == trial["label"],
                    }
                )
            metrics = {
                "test_accuracy": sum(item["correct"] for item in observations)
                / len(observations),
                "true_positive_rate": sum(
                    item["predicted"] for item in observations if item["label"] == 1
                )
                / 20,
                "false_positive_rate": sum(
                    item["predicted"] for item in observations if item["label"] == 0
                )
                / 20,
                "initial_weight": initial,
                "presynaptic_count_per_class": count,
                "probe_trained_population_weight_mean": statistics.mean(
                    weights[:count]
                ),
                "probe_trained_population_weight_delta": statistics.mean(
                    weights[:count]
                )
                - initial,
                "acquisition_reward_weight_updates": engines[
                    condition
                ].stats.reward_weight_updates,
                "post_acquisition_intervention": (
                    condition
                    if condition in ("weight_reset", "weight_shuffle")
                    else "none"
                ),
                "training_teacher_present": True,
                "test_teacher_present": False,
                "test_learning_engine_attached": False,
                "fresh_network_per_test_episode": True,
                "actual_test_episodes": len(observations),
                "evaluation_ticks_per_episode": 12,
                "test_input_digest": digest(trials),
                "weights": weights,
                "weight_digest_before_test": before,
                "weight_digest_after_test": digest(weights),
                "trials": observations,
                "interpretation_limit": "Synthetic rewarded association with external teacher and designed input populations; not open-world cognition or independent replication.",
            }
            runs.append(
                ScientificRun(
                    "EXP-EVAL-LEARN-001",
                    condition,
                    seed,
                    metrics,
                    before,
                    digest(weights),
                )
            )
    return runs


def run_brian2_conformance(
    config: Mapping[str, Any],
    seeds: tuple[int, ...] = EVALUATION_SEEDS[:3],
) -> list[ScientificRun]:
    """Compare 1-ms split-Euler single-neuron trajectories, not full frameworks."""
    del config
    try:
        brian: Any = importlib.import_module("brian2")
        np: Any = importlib.import_module("numpy")
    except ImportError as exc:
        raise RuntimeError(
            "BRIAN2_DEPENDENCY_MISSING: install the declared Brian2 baseline dependency"
        ) from exc
    brian.prefs.codegen.target = "numpy"
    result: list[ScientificRun] = []
    for seed in seeds:
        rng = random.Random(seed)
        currents = [
            [2.0, 5.0, 10.0, 20.0, rng.choice((0.0, 10.0, 50.0))] for _ in range(1000)
        ]
        native = [Neuron(index) for index in range(5)]
        disabled = replace(
            NeuronConfig(), threshold_adaptation_rate=0.0, homeostasis_learning_rate=0.0
        )
        for neuron in native:
            neuron.set_config(disabled)
        native_v: list[list[float]] = []
        native_u: list[list[float]] = []
        native_spikes: list[tuple[int, int]] = []
        started = time.perf_counter()
        for tick, row in enumerate(currents):
            for index, current in enumerate(row):
                if native[index].step(current, tick + 1):
                    native_spikes.append((tick, index))
            native_v.append([n.v for n in native])
            native_u.append([n.u for n in native])
        native_seconds = time.perf_counter() - started
        stimulus = brian.TimedArray(np.asarray(currents), dt=brian.ms)
        group = brian.NeuronGroup(
            5,
            "v : 1\nu : 1\nI : 1",
            threshold="v >= 30",
            reset="v = -65; u += 8",
            dt=brian.ms,
            namespace={"stimulus": stimulus},
        )
        group.v = -65
        group.u = -13
        update = group.run_regularly(
            "I = stimulus(t, i)\nv += 0.5*(0.04*v*v + 5*v + 140 - u + I)\nv += 0.5*(0.04*v*v + 5*v + 140 - u + I)\nu += 0.02*(0.2*v - u)",
            dt=brian.ms,
            when="groups",
            order=0,
        )
        states = brian.StateMonitor(group, ("v", "u"), record=True, when="end")
        spikes = brian.SpikeMonitor(group)
        network = brian.Network(group, update, states, spikes)
        started = time.perf_counter()
        network.run(1000 * brian.ms)
        brian_seconds = time.perf_counter() - started
        brian_v = states.v.T.tolist()
        brian_u = states.u.T.tolist()
        brian_spikes = [
            (int(round(float(t / brian.ms))), int(i))
            for t, i in zip(spikes.t, spikes.i)
        ]
        max_v = float(np.max(np.abs(np.asarray(native_v) - np.asarray(brian_v))))
        max_u = float(np.max(np.abs(np.asarray(native_u) - np.asarray(brian_u))))
        metrics = {
            "brian2_version": str(brian.__version__),
            "backend": "numpy",
            "cells": 5,
            "ticks_executed": 1000,
            "dt_ms": 1.0,
            "max_abs_voltage_error": max_v,
            "max_abs_recovery_error": max_u,
            "spike_events_equal": native_spikes == brian_spikes,
            "conformance_within_1e_8": native_spikes == brian_spikes
            and max_v <= 1e-8
            and max_u <= 1e-8,
            "native_seconds": native_seconds,
            "brian2_run_seconds_including_codegen": brian_seconds,
            "native_voltages": native_v,
            "brian2_voltages": brian_v,
            "native_recovery": native_u,
            "brian2_recovery": brian_u,
            "native_spikes": native_spikes,
            "brian2_spikes": brian_spikes,
            "input_currents": currents,
            "input_digest": digest(currents),
            "interpretation_limit": "Single-neuron numerical conformance with matched split-Euler update, adaptation disabled. Not a full-network learning/speed/energy benchmark; implementation is not independent authorship.",
        }
        result.append(
            ScientificRun(
                "EXP-EVAL-BRIAN-001",
                "matched_split_euler",
                seed,
                metrics,
                digest(currents),
                digest(native_spikes),
            )
        )
    return result


def run_active_scaling(
    config: Mapping[str, Any],
    seeds: tuple[int, ...] = EVALUATION_SEEDS[:3],
) -> list[ScientificRun]:
    """Active sparse workloads through 100k neurons; no extrapolation to brains."""
    psutil: Any = importlib.import_module("psutil")
    runs: list[ScientificRun] = []
    for seed in seeds:
        for count in (128, 1024, 5000, 25000, 100000):
            started = time.perf_counter()
            net, ids = build_empirical_network(config, count, seed)
            for source in range(count):
                for rank, offset in enumerate((1, 17, 31, 61)):
                    net.connect(
                        ids[source],
                        ids[(source + offset) % count],
                        25.0,
                        rank + 1,
                        config=SynapseConfig(w_max=100.0),
                    )
            construction_seconds = time.perf_counter() - started
            rss_built = int(psutil.Process().memory_info().rss)
            sources = random.Random(seed).sample(ids, 8)
            spikes: list[int] = []
            started = time.perf_counter()
            for tick in range(32):
                if tick % 16 == 0:
                    net.inject_current_batch({source: 100.0 for source in sources})
                spikes.append(len(net.step().spike_ids))
            elapsed = time.perf_counter() - started
            metrics = {
                "neurons": count,
                "synapses": count * 4,
                "address_encoding": "canonical_5d_base256_v2",
                "coordinate_repair_not_nd_migration": True,
                "ticks_executed": 32,
                "construction_seconds": construction_seconds,
                "step_seconds": elapsed,
                "ticks_per_second": 32 / elapsed,
                "neuron_updates_per_second": count * 32 / elapsed,
                "rss_after_build_bytes": rss_built,
                "rss_after_run_bytes": int(psutil.Process().memory_info().rss),
                "total_spikes": sum(spikes),
                "spikes_per_tick": spikes,
                "events_processed": net.total_events_processed,
                "finite_state": all(
                    math.isfinite(n.v) and math.isfinite(n.u)
                    for n in net.neurons.values()
                ),
                "interpretation_limit": "32-tick sparse active engineering workload, no long-horizon learning/real-time guarantee. RSS is sampled process memory, not an isolated allocation peak. No energy-in-joules claim.",
            }
            runs.append(
                ScientificRun("EXP-EVAL-SCALE-001", f"n{count}", seed, metrics, "", "")
            )
            del net
    return runs
