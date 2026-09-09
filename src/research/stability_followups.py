"""Exploratory post-AIRR stability experiments for MHRN.

The registered ``sustained_activity_stability_v1`` protocol established that its
observed trajectories remained finite and topologically stable over 100,000
ticks. Its no-input arm is nevertheless quiescent after burn-in, so numerical
stability and sustained active dynamics must not be represented by one Boolean.

This module provides deliberately non-registered follow-up runners that separate
those concepts and add stimulus-dose, stimulus-class and parameter-robustness
screens. They emit ``ScientificRun`` records only; they do not create EVID or
modify preregistrations.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal, cast

import yaml

from src.core import NeuralNetwork
from src.core.synapse import SynapseConfig
from src.research.canonical_state import canonical_state_digest
from src.research.experiment_suite import ScientificRun

Config = Mapping[str, Any]
Coord5D = tuple[int, int, int, int, int]
StimulusMode = Literal["none", "tonic", "rhythmic", "noise"]


def _mean(values: Sequence[float]) -> float:
    return statistics.fmean(values) if values else 0.0


def _relative_drift(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    baseline = max(abs(_mean(values)), 1e-12)
    return abs(float(values[-1]) - float(values[0])) / baseline


def _network(
    config: Config,
    seed: int,
    *,
    weight_scale: float = 1.0,
) -> NeuralNetwork:
    """Build the same small deterministic chain used by the stability protocol."""
    values = dict(config)
    values["dimensions"] = [3, 1, 1, 1, 1]
    values["initial_neurons"] = 0
    simulation = dict(cast(Mapping[str, Any], values.get("simulation", {})))
    simulation["max_delay"] = max(int(simulation.get("max_delay", 5)), 1)
    values["simulation"] = simulation

    network = NeuralNetwork(values, random.Random(seed))
    coords: tuple[Coord5D, Coord5D, Coord5D] = (
        (0, 0, 0, 0, 0),
        (1, 0, 0, 0, 0),
        (2, 0, 0, 0, 0),
    )
    ids = [network.add_neuron(coord) for coord in coords]
    network.input_cells.add(ids[0])
    network.output_cells.add(ids[2])
    synapse_config = SynapseConfig(w_max=250.0)
    weight = 100.0 * weight_scale
    network.connect(ids[0], ids[1], weight, 1, config=synapse_config)
    network.connect(ids[1], ids[2], weight, 1, config=synapse_config)
    return network


def _synapse_count(network: NeuralNetwork) -> int:
    return sum(len(bucket) for bucket in network.synapses.values())


def _stimulus_current(
    mode: StimulusMode,
    *,
    tick: int,
    drive_current: float,
    rng: random.Random,
) -> float:
    if mode == "none":
        return 0.0
    if mode == "tonic":
        return drive_current
    if mode == "rhythmic":
        return drive_current if tick % 100 < 50 else 0.0
    if mode == "noise":
        return drive_current * rng.uniform(0.5, 1.5)
    raise ValueError(f"Unsupported stimulus mode: {mode}")


def _classify_regime(
    *,
    numerical_stability: bool,
    post_burn_in_mean_spikes: float,
    active_window_fraction: float,
    spike_cv: float,
    spike_relative_drift: float,
) -> str:
    if not numerical_stability:
        return "numerically_unstable"
    if post_burn_in_mean_spikes <= 0.0:
        return "quiescent"
    if (
        active_window_fraction >= 0.90
        and spike_cv <= 0.35
        and spike_relative_drift <= 0.35
    ):
        return "stable_active"
    if active_window_fraction < 0.50:
        return "intermittent"
    return "active_variable"


def _simulate_condition(
    config: Config,
    *,
    experiment_id: str,
    condition: str,
    seed: int,
    ticks: int,
    mode: StimulusMode,
    drive_current: float,
    weight_scale: float = 1.0,
    drive_scale: float = 1.0,
    seed_effect_expected: bool = False,
) -> ScientificRun:
    if ticks < 1_000:
        raise ValueError("stability follow-ups require at least 1,000 ticks")
    if drive_current < 0.0:
        raise ValueError("drive_current must be >= 0")
    if weight_scale <= 0.0 or drive_scale <= 0.0:
        raise ValueError("weight_scale and drive_scale must be > 0")

    network = _network(config, seed, weight_scale=weight_scale)
    before = canonical_state_digest(network)
    source = min(network.input_cells)
    initial_neuron_count = len(network.neurons)
    initial_synapse_count = _synapse_count(network)

    window_ticks = 1_000 if ticks >= 10_000 else max(100, ticks // 10)
    burn_in_ticks = min(10_000, max(window_ticks, ticks // 10))
    rng = random.Random(seed ^ 0x51A81E)
    window_spikes: list[int] = []
    window_mean_v: list[float] = []
    current_window_spikes = 0
    current_window_v: list[float] = []
    total_spikes = 0
    first_active_tick: int | None = None
    last_active_tick: int | None = None
    runtime_error: str | None = None
    executed_ticks = 0

    for tick in range(1, ticks + 1):
        current = _stimulus_current(
            mode,
            tick=tick,
            drive_current=drive_current * drive_scale,
            rng=rng,
        )
        if current > 0.0:
            network.inject_current_batch({source: current})
        try:
            result = network.step()
        except Exception as exc:
            runtime_error = f"{type(exc).__name__}: {exc}"
            break

        executed_ticks += 1
        spike_count = len(result.spike_ids)
        total_spikes += spike_count
        current_window_spikes += spike_count
        if spike_count:
            if first_active_tick is None:
                first_active_tick = tick
            last_active_tick = tick

        voltages = [float(neuron.v) for neuron in network.neurons.values()]
        current_window_v.append(_mean(voltages))
        if tick % window_ticks == 0:
            window_spikes.append(current_window_spikes)
            window_mean_v.append(_mean(current_window_v))
            current_window_spikes = 0
            current_window_v = []

    if runtime_error is None and current_window_v:
        window_spikes.append(current_window_spikes)
        window_mean_v.append(_mean(current_window_v))

    burn_windows = min(len(window_spikes), burn_in_ticks // window_ticks)
    observed_windows = window_spikes[burn_windows:]
    observed_v = window_mean_v[burn_windows:]
    mean_spikes = _mean([float(value) for value in observed_windows])
    spike_cv = (
        statistics.pstdev(observed_windows) / mean_spikes
        if mean_spikes > 0.0 and len(observed_windows) > 1
        else 0.0
    )
    spike_drift = _relative_drift([float(value) for value in observed_windows])
    active_window_fraction = (
        sum(1 for value in observed_windows if value > 0) / len(observed_windows)
        if observed_windows
        else 0.0
    )
    silent_window_fraction = 1.0 - active_window_fraction if observed_windows else 1.0

    neuron_values = [float(neuron.v) for neuron in network.neurons.values()]
    weights = [
        float(synapse.weight)
        for bucket in network.synapses.values()
        for synapse in bucket
    ]
    finite_state = all(math.isfinite(value) for value in (*neuron_values, *weights))
    topology_unchanged = (
        len(network.neurons) == initial_neuron_count
        and _synapse_count(network) == initial_synapse_count
    )
    numerical_stability = (
        runtime_error is None
        and executed_ticks >= ticks
        and finite_state
        and topology_unchanged
    )
    activity_regime = _classify_regime(
        numerical_stability=numerical_stability,
        post_burn_in_mean_spikes=mean_spikes,
        active_window_fraction=active_window_fraction,
        spike_cv=spike_cv,
        spike_relative_drift=spike_drift,
    )
    active_dynamics = activity_regime == "stable_active"

    metrics: dict[str, Any] = {
        "ticks_requested": ticks,
        "ticks_executed": executed_ticks,
        "window_ticks": window_ticks,
        "burn_in_ticks": burn_in_ticks,
        "stimulus_mode": mode,
        "drive_current": drive_current,
        "drive_scale": drive_scale,
        "effective_drive_current": drive_current * drive_scale,
        "weight_scale": weight_scale,
        "total_spikes": total_spikes,
        "window_spike_counts": window_spikes,
        "window_mean_v": window_mean_v,
        "post_burn_in_window_count": len(observed_windows),
        "post_burn_in_mean_spikes": mean_spikes,
        "post_burn_in_spike_cv": spike_cv,
        "post_burn_in_spike_relative_drift": spike_drift,
        "post_burn_in_voltage_relative_drift": _relative_drift(observed_v),
        "active_window_fraction": active_window_fraction,
        "silent_window_fraction": silent_window_fraction,
        "first_active_tick": first_active_tick,
        "last_active_tick": last_active_tick,
        "finite_state": finite_state,
        "topology_unchanged": topology_unchanged,
        "neuron_v_min": min(neuron_values) if neuron_values else 0.0,
        "neuron_v_max": max(neuron_values) if neuron_values else 0.0,
        "weight_min": min(weights) if weights else 0.0,
        "weight_max": max(weights) if weights else 0.0,
        "numerical_stability_pass": numerical_stability,
        "active_dynamics_pass": active_dynamics,
        "activity_regime": activity_regime,
        "seed_effect_expected": seed_effect_expected,
        "interpretation_contract": (
            "numerical_stability_pass and active_dynamics_pass are distinct; "
            "quiescence is not evidence of sustained active spiking"
        ),
    }
    return ScientificRun(
        experiment_id,
        condition,
        seed,
        metrics,
        before,
        canonical_state_digest(network),
        runtime_error,
    )


def run_drive_response_curve(
    config: Config,
    seeds: tuple[int, ...] = (101, 102, 103),
    ticks: int = 20_000,
    drive_levels: tuple[float, ...] = (0.0, 25.0, 50.0, 75.0, 100.0),
) -> list[ScientificRun]:
    """Map the transition from quiescence to stable/variable activity by drive."""
    if not drive_levels:
        raise ValueError("drive_levels must not be empty")
    runs: list[ScientificRun] = []
    for seed in seeds:
        for drive in drive_levels:
            mode: StimulusMode = "none" if drive == 0.0 else "tonic"
            runs.append(
                _simulate_condition(
                    config,
                    experiment_id="EXP-SNN-DRIVE-NEXT",
                    condition=f"drive_{drive:g}",
                    seed=seed,
                    ticks=ticks,
                    mode=mode,
                    drive_current=float(drive),
                    seed_effect_expected=False,
                )
            )
    return runs


def run_stimulus_class_stability(
    config: Config,
    seeds: tuple[int, ...] = (101, 102, 103),
    ticks: int = 20_000,
    drive_current: float = 50.0,
) -> list[ScientificRun]:
    """Compare no-input, tonic, rhythmic and seeded stochastic stimulation."""
    modes: tuple[StimulusMode, ...] = ("none", "tonic", "rhythmic", "noise")
    runs: list[ScientificRun] = []
    for seed in seeds:
        for mode in modes:
            runs.append(
                _simulate_condition(
                    config,
                    experiment_id="EXP-SNN-STIMULUS-NEXT",
                    condition=f"stimulus_{mode}",
                    seed=seed,
                    ticks=ticks,
                    mode=mode,
                    drive_current=0.0 if mode == "none" else drive_current,
                    seed_effect_expected=mode == "noise",
                )
            )
    return runs


def run_parameter_robustness(
    config: Config,
    seeds: tuple[int, ...] = (101, 102, 103),
    ticks: int = 20_000,
    drive_current: float = 50.0,
    jitter_fraction: float = 0.05,
) -> list[ScientificRun]:
    """Perturb drive and synaptic weight jointly to test local robustness.

    Unlike the fixed three-node conditions, these seed-bound perturbations are
    designed to produce genuinely different parameterizations across seed labels.
    """
    if not 0.0 < jitter_fraction < 1.0:
        raise ValueError("jitter_fraction must be between 0 and 1")
    runs: list[ScientificRun] = []
    for seed in seeds:
        rng = random.Random(seed ^ 0xA17B05)
        weight_scale = 1.0 + rng.uniform(-jitter_fraction, jitter_fraction)
        drive_scale = 1.0 + rng.uniform(-jitter_fraction, jitter_fraction)
        runs.append(
            _simulate_condition(
                config,
                experiment_id="EXP-SNN-ROBUST-NEXT",
                condition="parameter_jitter",
                seed=seed,
                ticks=ticks,
                mode="tonic",
                drive_current=drive_current,
                weight_scale=weight_scale,
                drive_scale=drive_scale,
                seed_effect_expected=True,
            )
        )
    return runs


def _parse_seeds(value: str) -> tuple[int, ...]:
    text = value.strip()
    if not text:
        raise ValueError("seed expression must not be empty")
    if "-" in text and "," not in text:
        start_text, end_text = text.split("-", 1)
        start, end = int(start_text), int(end_text)
        if end < start:
            raise ValueError("seed range end must be >= start")
        return tuple(range(start, end + 1))
    result = tuple(int(item.strip()) for item in text.split(",") if item.strip())
    if not result:
        raise ValueError("seed expression resolved to no seeds")
    return result


def _load_config(path: Path) -> dict[str, Any]:
    raw: object = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("configuration root must be a mapping")
    return cast(dict[str, Any], raw)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run non-registered post-AIRR SNN stability follow-up screens."
    )
    parser.add_argument(
        "experiment",
        choices=("drive-response", "stimulus-class", "parameter-robustness"),
    )
    parser.add_argument("--config", default="configs/learning_experiment.yaml")
    parser.add_argument("--ticks", type=int, default=20_000)
    parser.add_argument("--seeds", default="101-103")
    parser.add_argument("--output", default=None)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point for deterministic exploratory follow-up execution."""
    args = _parser().parse_args(list(argv) if argv is not None else None)
    config = _load_config(Path(str(args.config)).resolve())
    seeds = _parse_seeds(str(args.seeds))
    ticks = int(args.ticks)
    experiment = str(args.experiment)

    if experiment == "drive-response":
        runs = run_drive_response_curve(config, seeds=seeds, ticks=ticks)
    elif experiment == "stimulus-class":
        runs = run_stimulus_class_stability(config, seeds=seeds, ticks=ticks)
    else:
        runs = run_parameter_robustness(config, seeds=seeds, ticks=ticks)

    payload = [
        {
            "experiment_id": run.experiment_id,
            "condition": run.condition,
            "seed": run.seed,
            "metrics": run.metrics,
            "state_digest_before": run.state_digest_before,
            "state_digest_after": run.state_digest_after,
            "runtime_error": run.runtime_error,
        }
        for run in runs
    ]
    encoded = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    output_value = args.output
    if output_value:
        output = Path(str(output_value)).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
