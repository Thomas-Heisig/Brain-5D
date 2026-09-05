"""Small, deterministic runners for the currently executable science protocols."""

from __future__ import annotations

import argparse
import json
import random
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, cast

import yaml

from src.core import NeuralNetwork
from src.embodiment import (
    InteroceptionFrame,
    derive_drives,
    derive_functional_state,
    derive_regulatory_state,
    normalize_vital_signals,
)
from src.experiments.learning_lab import run_learning_experiment
from src.research.canonical_state import canonical_state_digest
from src.research.network_probe import NetworkImpulseProbe, NetworkResponseSignature
from src.research.temporal import (
    TemporalComparator,
    TemporalStateFrame,
    TemporalStateMemory,
)

Config = Mapping[str, Any]
Coord5D = tuple[int, int, int, int, int]


class _ProbeRuntime:
    """Adapt the real network StepResult to the probe's narrow protocol."""

    def __init__(self, network: NeuralNetwork) -> None:
        self.network = network

    def inject_current_batch(self, currents: Mapping[int, float]) -> None:
        self.network.inject_current_batch(dict(currents))

    def step(self) -> dict[str, Any]:
        return self.network.step().to_dict()


@dataclass(frozen=True, slots=True)
class ScientificRun:
    experiment_id: str
    condition: str
    seed: int
    metrics: dict[str, Any]
    state_digest_before: str
    state_digest_after: str
    runtime_error: str | None = None


def _network(
    config: Config,
    seed: int,
    *,
    recurrence: bool = False,
    dimensions: Coord5D = (3, 1, 1, 1, 1),
    random_graph: bool = False,
) -> NeuralNetwork:
    impulse_weight = 100.0
    values = dict(config)
    values["dimensions"] = list(dimensions)
    values["initial_neurons"] = 0
    values.setdefault("simulation", {})
    simulation = dict(values["simulation"])
    simulation["max_delay"] = 5
    values["simulation"] = simulation
    network = NeuralNetwork(values, random.Random(seed))
    if dimensions[0] > 2:
        relay = (1, 0, 0, 0, 0)
    elif dimensions[1] > 1:
        relay = (0, 1, 0, 0, 0)
    else:
        relay = (0, 0, 1, 0, 0)
    coordinates: tuple[Coord5D, Coord5D, Coord5D] = (
        (0, 0, 0, 0, 0),
        relay,
        cast(Coord5D, tuple(size - 1 for size in dimensions)),
    )
    neurons: list[int] = []
    for coord in coordinates:
        existing = network.get_neuron_at_coord(coord)
        neurons.append(
            existing.neuron_id if existing is not None else network.add_neuron(coord)
        )
    network.input_cells.add(neurons[0])
    network.output_cells.add(neurons[2])
    if random_graph:
        network.connect(neurons[0], neurons[2], impulse_weight, 1)
        network.connect(neurons[2], neurons[1], impulse_weight, 1)
    else:
        network.connect(neurons[0], neurons[1], impulse_weight, 1)
        network.connect(neurons[1], neurons[2], impulse_weight, 1)
    if recurrence:
        network.connect(neurons[2], neurons[1], impulse_weight, 1)
    return network


def _digest(network: NeuralNetwork) -> str:
    return canonical_state_digest(network)


def run_ping(
    config: Config, seeds: tuple[int, ...] = (42, 43, 44)
) -> list[ScientificRun]:
    """Measure reproducible impulse responses with and without recurrence."""
    runs: list[ScientificRun] = []
    for seed in seeds:
        for recurrence in (False, True):
            network = _network(config, seed, recurrence=recurrence)
            before = _digest(network)
            source = min(network.input_cells)
            signature: NetworkResponseSignature = NetworkImpulseProbe(
                source_neuron=source,
                current=100.0,
                max_ticks=8,
                state_digest=lambda: _digest(network),
            ).run(_ProbeRuntime(network))
            runs.append(
                ScientificRun(
                    "EXP-PING-0001",
                    "recurrence_on" if recurrence else "recurrence_off",
                    seed,
                    signature.to_dict(),
                    before,
                    _digest(network),
                )
            )
    return runs


def run_ping_v2(
    config: Config, seeds: tuple[int, ...] = (42, 43, 44)
) -> list[ScientificRun]:
    """Run recurrence treatments as identical replica pairs per seed."""
    runs: list[ScientificRun] = []
    for seed in seeds:
        for recurrence in (False, True):
            for replica in ("replica_a", "replica_b"):
                network = _network(config, seed, recurrence=recurrence)
                before = _digest(network)
                source = min(network.input_cells)
                signature = NetworkImpulseProbe(
                    source_neuron=source,
                    current=100.0,
                    max_ticks=8,
                    state_digest=lambda: _digest(network),
                ).run(_ProbeRuntime(network))
                runs.append(
                    ScientificRun(
                        "EXP-PING-0001-v2",
                        f"{'recurrence_on' if recurrence else 'recurrence_off'}_{replica}",
                        seed,
                        signature.to_dict(),
                        before,
                        _digest(network),
                    )
                )
    return runs


def run_time(
    config: Config,
    seeds: tuple[int, ...] = (42, 43, 44),
    tick_counts: tuple[int, ...] = (100, 1_000, 10_000, 100_000, 1_000_000),
) -> list[ScientificRun]:
    """Calibrate wall-clock throughput over the registered tick ladder."""
    runs: list[ScientificRun] = []
    for seed in seeds:
        for ticks in tick_counts:
            network = _network(config, seed)
            before = _digest(network)
            started = time.perf_counter()
            for _ in range(ticks):
                network.step()
            duration = time.perf_counter() - started
            runs.append(
                ScientificRun(
                    "EXP-TIME-0001",
                    str(ticks),
                    seed,
                    {
                        "ticks": ticks,
                        "duration_seconds": duration,
                        "ticks_per_second": ticks / duration,
                    },
                    before,
                    _digest(network),
                )
            )
    return runs


def run_5d(
    config: Config,
    seeds: tuple[int, ...] = tuple(range(30)),
) -> list[ScientificRun]:
    """Compare the same controlled chain embedded in dimensional spaces."""
    dimensions = {
        "1d": (3, 1, 1, 1, 1),
        "2d": (2, 2, 1, 1, 1),
        "3d": (2, 2, 2, 1, 1),
        "5d": (2, 2, 2, 2, 2),
        "random_graph": (2, 2, 2, 2, 2),
    }
    runs: list[ScientificRun] = []
    for seed in seeds:
        for condition, shape in dimensions.items():
            network = _network(
                config, seed, dimensions=shape, random_graph=condition == "random_graph"
            )
            before = _digest(network)
            signature = NetworkImpulseProbe(
                source_neuron=min(network.input_cells),
                current=100.0,
                max_ticks=8,
            ).run(_ProbeRuntime(network))
            runs.append(
                ScientificRun(
                    "EXP-5D-0001",
                    condition,
                    seed,
                    {"dimensions": list(shape), **signature.to_dict()},
                    before,
                    _digest(network),
                )
            )
    return runs


def run_regulation(
    config: Config,
    seeds: tuple[int, ...] = (42, 43, 44),
) -> list[ScientificRun]:
    """Measure bounded regulation outputs under pressure and unknown inputs."""
    del config
    readings_by_condition: dict[str, dict[str, Any]] = {
        "nominal": {
            "cpu_percent": 20.0,
            "memory_percent": 30.0,
            "temperature_c": 40.0,
            "network_up": True,
        },
        "chronic_pressure": {
            "cpu_percent": 95.0,
            "memory_percent": 92.0,
            "temperature_c": 90.0,
            "network_up": False,
        },
        "telemetry_unknown": {},
    }
    runs: list[ScientificRun] = []
    for seed in seeds:
        for condition, readings in readings_by_condition.items():
            frame = InteroceptionFrame(seed, normalize_vital_signals(readings))
            drives = derive_drives(frame)
            regulatory = derive_regulatory_state(frame)
            functional = derive_functional_state(frame)
            runs.append(
                ScientificRun(
                    "EXP-REG-0001",
                    condition,
                    seed,
                    {
                        "drives": drives.to_json(),
                        "regulatory_state": regulatory.to_json(),
                        "functional_state": functional.to_json(),
                    },
                    "",
                    "",
                )
            )
    return runs


def run_temporal(
    config: Config, seeds: tuple[int, ...] = (42, 43, 44)
) -> list[ScientificRun]:
    """Compare retained fast/medium/slow state references without rewinding."""
    runs: list[ScientificRun] = []
    for seed in seeds:
        network = _network(config, seed)
        before = _digest(network)
        memory = TemporalStateMemory(
            horizons={"fast": 2, "medium": 4, "slow": 6}, capacity=32
        )
        comparator = TemporalComparator()
        comparisons: list[dict[str, Any]] = []
        for _ in range(8):
            result = network.step()
            frame = TemporalStateFrame.from_mapping(
                network.current_tick,
                _digest(network),
                {
                    "mean_v": sum(neuron.v for neuron in network.neurons.values())
                    / len(network.neurons),
                    "spikes_this_tick": float(len(result.spike_ids)),
                    "synapse_count": float(network.synapse_count),
                },
            )
            for horizon in memory.horizons:
                comparisons.append(
                    comparator.compare(
                        frame, memory.reference(frame.tick, horizon), horizon=horizon
                    ).to_dict()
                )
            memory.append(frame)
        runs.append(
            ScientificRun(
                "EXP-TEMP-0001",
                "fast_medium_slow",
                seed,
                {
                    "comparisons": comparisons,
                    "novelty": "not_registered",
                    "prediction_error": "not_available",
                },
                before,
                _digest(network),
            )
        )
    return runs


def run_stdp(
    config: Config, seeds: tuple[int, ...] = (42, 43, 44)
) -> list[ScientificRun]:
    """Run the existing productive LearningEngine path for independent seeds."""
    runs: list[ScientificRun] = []
    for seed in seeds:
        values = dict(config)
        values["seed"] = seed
        result = run_learning_experiment(values)
        runs.append(
            ScientificRun(
                "EXP-STDP-0002",
                "productive_reward_stdp",
                seed,
                asdict(result),
                "",
                "",
            )
        )
    return runs


def run_learning_repeat(
    config: Config, seeds: tuple[int, ...] = (42, 43, 44)
) -> list[ScientificRun]:
    """Compare learning-on, learning-off and sham-replay controls."""
    runs: list[ScientificRun] = []
    for seed in seeds:
        for condition in ("learning_on", "learning_off", "sham_replay"):
            values = dict(config)
            values["seed"] = seed
            result = run_learning_experiment(values, condition=condition)
            runs.append(
                ScientificRun(
                    "EXP-STDP-0002",
                    condition,
                    seed,
                    {
                        "success_before": result.baseline_target_spiked,
                        "success_after": result.trained_target_spiked,
                        "p_success_before": float(result.baseline_target_spiked),
                        "p_success_after": float(result.trained_target_spiked),
                        "after_greater_than_before": result.trained_target_spiked
                        and not result.baseline_target_spiked,
                        "initial_mean_weight": result.initial_mean_weight,
                        "final_mean_weight": result.final_mean_weight,
                        "mean_weight_delta": result.mean_weight_delta,
                        "rewards_received": result.rewards_received,
                        "reward_weight_updates": result.reward_weight_updates,
                        "train_trial_count": result.train_trial_count,
                        "validation_trial_count": result.validation_trial_count,
                        "holdout_trial_count": result.holdout_trial_count,
                        "protocol_id": result.protocol_id,
                        "protocol_version": result.protocol_version,
                    },
                    "",
                    "",
                )
            )
    return runs


def run_learning(
    config: Config, seeds: tuple[int, ...] = (42, 43, 44)
) -> list[ScientificRun]:
    """Run the registered full-stack LearningEngine experiment from the operator workflow."""
    runs: list[ScientificRun] = []
    for seed in seeds:
        values = dict(config)
        values["seed"] = seed
        result = run_learning_experiment(values)
        runs.append(
            ScientificRun(
                "EXP-LEARN-0001",
                "operator_learning_run",
                seed,
                asdict(result),
                "",
                "",
            )
        )
    return runs


def write_data(path: Path, runs: list[ScientificRun]) -> None:
    """Write deterministic run records as one JSON document."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps([asdict(run) for run in runs], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _load(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise TypeError("configuration root must be a mapping")
    return cast(dict[str, Any], loaded)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/learning_experiment.yaml")
    parser.add_argument(
        "--output", default="research/generated/data/science_suite.json"
    )
    args = parser.parse_args()
    config = _load(Path(args.config))
    started = time.perf_counter()
    runs = (
        run_ping(config)
        + run_temporal(config)
        + run_stdp(config)
        + run_learning_repeat(config)
        + run_time(config)
        + run_5d(config)
        + run_regulation(config)
    )
    write_data(Path(args.output), runs)
    print(
        json.dumps(
            {
                "runs": len(runs),
                "duration_seconds": time.perf_counter() - started,
                "output": args.output,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
