"""Executable follow-up experiments derived from EXP-GEN-0021.

These runners are deliberately small, deterministic and intervention based.  They
produce ScientificRun records and never promote their own output to evidence.
"""

from __future__ import annotations

import random
import statistics
import time
from pathlib import Path
from typing import Any, Mapping

from src.core import NeuralNetwork
from src.core.synapse import SynapseConfig
from src.embodiment import (
    InteroceptionFrame,
    derive_functional_state,
    derive_regulatory_state,
    normalize_vital_signals,
)
from src.experiments import msba_lab as _msba_lab
from src.experiments.learning_lab import (
    probe_learning_response,
    run_learning_experiment,
    train_learning_weights,
)
from src.research.canonical_state import canonical_state_digest
from src.research.experiment_suite import ScientificRun
from src.research.network_probe import NetworkImpulseProbe
from src.research.protocol_registry import validate_operational_protocol

Config = Mapping[str, Any]
Coord5D = tuple[int, int, int, int, int]


class _Runtime:
    def __init__(self, network: NeuralNetwork) -> None:
        self.network = network

    def inject_current_batch(self, currents: Mapping[int, float]) -> None:
        self.network.inject_current_batch(dict(currents))

    def step(self) -> dict[str, Any]:
        return self.network.step().to_dict()


def _three_node_network(
    config: Config,
    seed: int,
    *,
    dimensions: Coord5D = (3, 1, 1, 1, 1),
    recurrent_weight: float | None = None,
    recurrent_delay: int = 1,
) -> NeuralNetwork:
    values = dict(config)
    values["dimensions"] = list(dimensions)
    values["initial_neurons"] = 0
    simulation = dict(values.get("simulation", {}))
    simulation["max_delay"] = max(int(simulation.get("max_delay", 5)), recurrent_delay)
    values["simulation"] = simulation
    network = NeuralNetwork(values, random.Random(seed))
    coords: tuple[Coord5D, Coord5D, Coord5D] = (
        (0, 0, 0, 0, 0),
        (1, 0, 0, 0, 0) if dimensions[0] >= 2 else (0, 1, 0, 0, 0),
        (
            dimensions[0] - 1,
            dimensions[1] - 1,
            dimensions[2] - 1,
            dimensions[3] - 1,
            dimensions[4] - 1,
        ),
    )
    ids = [network.add_neuron(coord) for coord in coords]
    network.input_cells.add(ids[0])
    network.output_cells.add(ids[2])
    syn_cfg = SynapseConfig(w_max=200.0)
    network.connect(ids[0], ids[1], 100.0, 1, config=syn_cfg)
    network.connect(ids[1], ids[2], 100.0, 1, config=syn_cfg)
    if recurrent_weight is not None and recurrent_weight > 0.0:
        network.connect(
            ids[2], ids[0], recurrent_weight, recurrent_delay, config=syn_cfg
        )
    return network


def _probe(network: NeuralNetwork, ticks: int) -> dict[str, Any]:
    before = canonical_state_digest(network)
    signature = NetworkImpulseProbe(
        source_neuron=min(network.input_cells),
        current=100.0,
        max_ticks=ticks,
        min_ticks=ticks,
        state_digest=lambda: canonical_state_digest(network),
    ).run(_Runtime(network))
    return {
        "before": before,
        "after": canonical_state_digest(network),
        "metrics": {"ticks_requested": ticks, **signature.to_dict()},
    }


def run_recurrence_map(
    config: Config,
    seeds: tuple[int, ...] = (42, 43, 44),
    ticks: int = 256,
) -> list[ScientificRun]:
    """Map decay/transient/persistent recurrence across weight and delay interventions."""
    runs: list[ScientificRun] = []
    for seed in seeds:
        for weight in (0.0, 50.0, 75.0, 100.0, 125.0):
            for delay in (1, 2, 4):
                network = _three_node_network(
                    config,
                    seed,
                    recurrent_weight=None if weight == 0.0 else weight,
                    recurrent_delay=delay,
                )
                result = _probe(network, ticks)
                metrics = dict(result["metrics"])
                last = metrics.get("last_response_latency")
                metrics.update(
                    {
                        "recurrent_weight": weight,
                        "recurrent_delay": delay,
                        "activity_fraction": (
                            float(last) / float(ticks)
                            if isinstance(last, int) and ticks > 0
                            else 0.0
                        ),
                        "persistence_class": (
                            "persistent_to_window"
                            if isinstance(last, int) and last >= ticks - 1
                            else (
                                "transient"
                                if isinstance(last, int) and last > 2
                                else "immediate_decay"
                            )
                        ),
                    }
                )
                runs.append(
                    ScientificRun(
                        "EXP-REC-0001",
                        f"w{weight:g}_d{delay}",
                        seed,
                        metrics,
                        str(result["before"]),
                        str(result["after"]),
                    )
                )
    return runs


def run_generalization(
    config: Config,
    seeds: tuple[int, ...] = (42, 43, 44),
) -> list[ScientificRun]:
    """Train once, then evaluate frozen weights on registered perturbation probes."""
    runs: list[ScientificRun] = []
    for seed in seeds:
        values = dict(config)
        values["seed"] = seed
        exp = dict(values.get("learning_experiment", {}))
        base_drive = float(exp.get("drive_current", 100.0))
        pre_count = int(exp.get("presynaptic_neurons", 48))
        initial_weight = float(exp.get("initial_weight", 0.05))
        initial_weights = tuple(initial_weight for _ in range(pre_count))
        for condition in ("learning_on", "learning_off", "sham_replay"):
            trained_weights, learning, partitions = train_learning_weights(
                values, condition
            )
            initial_mean = statistics.mean(initial_weights)
            final_mean = statistics.mean(trained_weights)
            for drive_scale in (0.85, 1.0, 1.15):
                probe_config = dict(values)
                probe_exp = dict(exp)
                probe_exp["drive_current"] = base_drive * drive_scale
                probe_config["learning_experiment"] = probe_exp
                baseline_spiked, baseline_peak_v, baseline_tick = (
                    probe_learning_response(probe_config, initial_weights)
                )
                trained_spiked, trained_peak_v, trained_tick = probe_learning_response(
                    probe_config, trained_weights
                )
                runs.append(
                    ScientificRun(
                        "EXP-GENL-0001",
                        f"{condition}_drive_{drive_scale:.2f}",
                        seed,
                        {
                            "probe_drive_scale": drive_scale,
                            "held_out_perturbation": drive_scale != 1.0,
                            "training_drive_scale": 1.0,
                            "success_before": baseline_spiked,
                            "success_after": trained_spiked,
                            "p_success_before": float(baseline_spiked),
                            "p_success_after": float(trained_spiked),
                            "generalization_success": trained_spiked,
                            "baseline_target_peak_v": baseline_peak_v,
                            "trained_target_peak_v": trained_peak_v,
                            "baseline_target_spike_tick": baseline_tick,
                            "trained_target_spike_tick": trained_tick,
                            "initial_mean_weight": initial_mean,
                            "final_mean_weight": final_mean,
                            "mean_weight_delta": final_mean - initial_mean,
                            "rewards_received": learning.stats.rewards_received,
                            "reward_weight_updates": learning.stats.reward_weight_updates,
                            "train_trial_count": len(partitions["train"]),
                            "validation_trial_count": len(partitions["validation"]),
                            "holdout_trial_count": len(partitions["holdout"]),
                            "probe_after_training_only": True,
                        },
                        "",
                        "",
                    )
                )
    return runs


def run_replication(
    config: Config,
    seeds: tuple[int, ...] = tuple(range(20)),
    ticks: int = 256,
) -> list[ScientificRun]:
    """Replicate recurrence with genuinely varying initialization seeds."""
    runs: list[ScientificRun] = []
    for seed in seeds:
        for weight in (0.0, 100.0):
            network = _three_node_network(
                config,
                seed,
                recurrent_weight=None if weight == 0.0 else weight,
                recurrent_delay=1,
            )
            result = _probe(network, ticks)
            metrics = dict(result["metrics"])
            metrics["replication_seed"] = seed
            metrics["treatment"] = "recurrence_on" if weight else "recurrence_off"
            runs.append(
                ScientificRun(
                    "EXP-REPL-0001",
                    str(metrics["treatment"]),
                    seed,
                    metrics,
                    str(result["before"]),
                    str(result["after"]),
                )
            )
    return runs


def run_5d_matched(
    config: Config,
    seeds: tuple[int, ...] = tuple(range(30)),
    ticks: int = 64,
) -> list[ScientificRun]:
    """Compare dimension embeddings while holding the three-node graph constant."""
    shapes: dict[str, Coord5D] = {
        "1d": (3, 1, 1, 1, 1),
        "2d": (2, 2, 1, 1, 1),
        "3d": (2, 2, 2, 1, 1),
        "5d": (2, 2, 2, 2, 2),
    }
    runs: list[ScientificRun] = []
    for seed in seeds:
        for label, shape in shapes.items():
            network = _three_node_network(config, seed, dimensions=shape)
            result = _probe(network, ticks)
            metrics = dict(result["metrics"])
            metrics.update(
                {
                    "dimensions": list(shape),
                    "matched_neuron_count": 3,
                    "matched_synapse_count": 2,
                    "matched_degree_pattern": "chain_1_1_0",
                    "matched_weight_pattern": [100.0, 100.0],
                }
            )
            runs.append(
                ScientificRun(
                    "EXP-5D-0005",
                    label,
                    seed,
                    metrics,
                    str(result["before"]),
                    str(result["after"]),
                )
            )
    return runs


def run_regulation_recovery(
    config: Config,
    seeds: tuple[int, ...] = (42, 43, 44),
    ticks: int = 128,
) -> list[ScientificRun]:
    """Measure a defined regulatory feedback intervention against a disabled control."""
    readings: dict[str, dict[str, Any]] = {
        "nominal": {
            "cpu_percent": 20.0,
            "memory_percent": 30.0,
            "temperature_c": 40.0,
            "network_up": True,
        },
        "pressure": {
            "cpu_percent": 95.0,
            "memory_percent": 92.0,
            "temperature_c": 90.0,
            "network_up": False,
        },
    }
    runs: list[ScientificRun] = []
    for seed in seeds:
        for enabled in (False, True):
            network = _three_node_network(config, seed, recurrent_weight=100.0)
            before = canonical_state_digest(network)
            source = min(network.input_cells)
            total_spikes = 0
            pressure_spikes = 0
            recovery_spikes = 0
            for tick in range(ticks):
                phase = "pressure" if ticks // 3 <= tick < 2 * ticks // 3 else "nominal"
                frame = InteroceptionFrame(
                    tick, normalize_vital_signals(readings[phase])
                )
                regulatory = derive_regulatory_state(frame)
                functional = derive_functional_state(frame)
                current = 100.0
                if enabled and phase == "pressure":
                    pressure = regulatory.values.get("resource_pressure")
                    if isinstance(pressure, (int, float)):
                        current *= max(0.25, 1.0 - 0.5 * float(pressure))
                    current *= max(0.5, 1.0 - 0.25 * float(functional.uncertainty))
                network.inject_current(source, current)
                count = len(network.step().spike_ids)
                total_spikes += count
                if phase == "pressure":
                    pressure_spikes += count
                elif tick >= 2 * ticks // 3:
                    recovery_spikes += count
            runs.append(
                ScientificRun(
                    "EXP-REG-0002",
                    "regulation_on" if enabled else "regulation_off",
                    seed,
                    {
                        "ticks_executed": ticks,
                        "total_spikes": total_spikes,
                        "pressure_phase_spikes": pressure_spikes,
                        "recovery_phase_spikes": recovery_spikes,
                        "recovery_ratio": (
                            recovery_spikes / pressure_spikes
                            if pressure_spikes
                            else None
                        ),
                        "feedback_definition": "pressure scales source current only in regulation_on",
                    },
                    before,
                    canonical_state_digest(network),
                )
            )
    return runs


def run_temporal_order(
    config: Config,
    seeds: tuple[int, ...] = (42, 43, 44),
    ticks: int = 32,
) -> list[ScientificRun]:
    """Test spike-carrying A->B versus B->A and shuffled timing sequences."""
    runs: list[ScientificRun] = []
    for seed in seeds:
        for condition, schedule in {
            "forward": (0, 4),
            "reverse": (4, 0),
            "simultaneous": (0, 0),
        }.items():
            network = _three_node_network(config, seed)
            before = canonical_state_digest(network)
            input_id = min(network.input_cells)
            spikes: list[int] = []
            for tick in range(ticks):
                if tick in schedule:
                    network.inject_current(input_id, 100.0)
                spikes.extend(network.step().spike_ids)
            runs.append(
                ScientificRun(
                    "EXP-TEMP-0002",
                    condition,
                    seed,
                    {
                        "ticks_executed": ticks,
                        "schedule": list(schedule),
                        "total_spikes": len(spikes),
                        "output_spike_count": sum(
                            1 for spike in spikes if spike in network.output_cells
                        ),
                        "sequence_digest": canonical_state_digest(network),
                    },
                    before,
                    canonical_state_digest(network),
                )
            )
    return runs


def run_performance_profile(
    config: Config,
    seeds: tuple[int, ...] = (42, 43, 44),
    ticks: int = 10_000,
) -> list[ScientificRun]:
    """Profile construction, core stepping and digest/serialization-adjacent phases."""
    runs: list[ScientificRun] = []
    for seed in seeds:
        started = time.perf_counter()
        network = _three_node_network(config, seed, recurrent_weight=100.0)
        construction = time.perf_counter() - started
        before = canonical_state_digest(network)
        source = min(network.input_cells)
        network.inject_current(source, 100.0)
        started = time.perf_counter()
        spike_count = 0
        for _ in range(ticks):
            spike_count += len(network.step().spike_ids)
        step_seconds = time.perf_counter() - started
        started = time.perf_counter()
        after = canonical_state_digest(network)
        digest_seconds = time.perf_counter() - started
        total = construction + step_seconds + digest_seconds
        runs.append(
            ScientificRun(
                "EXP-PERF-0001",
                "subsystem_profile",
                seed,
                {
                    "ticks_executed": ticks,
                    "total_spikes": spike_count,
                    "construction_seconds": construction,
                    "core_step_seconds": step_seconds,
                    "digest_seconds": digest_seconds,
                    "measured_total_seconds": total,
                    "ticks_per_second": ticks / step_seconds if step_seconds else 0.0,
                },
                before,
                after,
            )
        )
    return runs


def run_recurrence_scale(
    config: Config,
    seeds: tuple[int, ...] = (42, 43, 44),
    ticks: int = 256,
) -> list[ScientificRun]:
    """Scale recurrence delay as a controlled proxy for loop length."""
    runs: list[ScientificRun] = []
    for seed in seeds:
        for delay in (1, 2, 4, 8):
            network = _three_node_network(
                config, seed, recurrent_weight=100.0, recurrent_delay=delay
            )
            result = _probe(network, ticks)
            metrics = dict(result["metrics"])
            metrics["loop_delay_ticks"] = delay
            runs.append(
                ScientificRun(
                    "EXP-REC-0002",
                    f"loop_delay_{delay}",
                    seed,
                    metrics,
                    str(result["before"]),
                    str(result["after"]),
                )
            )
    return runs


def run_learning_interference(
    config: Config,
    seeds: tuple[int, ...] = (42, 43, 44),
) -> list[ScientificRun]:
    """Operational first interference screen using sequential perturbation tasks."""
    runs: list[ScientificRun] = []
    for seed in seeds:
        outcomes: list[bool] = []
        weights: list[float] = []
        for task_index, drive_scale in enumerate((1.0, 0.9, 1.1)):
            values = dict(config)
            values["seed"] = seed + task_index * 10_000
            exp = dict(values.get("learning_experiment", {}))
            exp["drive_current"] = float(exp.get("drive_current", 100.0)) * drive_scale
            exp["reset_trial_dynamics"] = True
            values["learning_experiment"] = exp
            result = run_learning_experiment(values, condition="learning_on")
            outcomes.append(bool(result.trained_target_spiked))
            weights.append(float(result.final_mean_weight))
        runs.append(
            ScientificRun(
                "EXP-LIFE-0001",
                "sequential_three_task_screen",
                seed,
                {
                    "task_successes": outcomes,
                    "task_final_mean_weights": weights,
                    "retained_success_fraction": sum(outcomes) / len(outcomes),
                    "weight_range": max(weights) - min(weights),
                    "interpretation_limit": "independent task instances; precursor screen, not yet shared-network catastrophic-forgetting proof",
                },
                "",
                "",
            )
        )
    return runs


def _run_msba_registered(
    config: Config,
    seeds: tuple[int, ...],
    *,
    question_id: str,
    hypothesis_id: str,
    protocol_id: str,
    runner_name: str,
) -> list[ScientificRun]:
    """Validate the frozen preregistration before any adaptive MSBA mechanism runs."""
    research_root = Path(__file__).resolve().parents[2] / "research"
    preregistration = validate_operational_protocol(
        research_root,
        question_id=question_id,
        hypothesis_id=hypothesis_id,
        protocol_id=protocol_id,
        seed_count=len(set(seeds)),
    )
    runner = getattr(_msba_lab, runner_name)
    runs = runner(config, seeds=seeds, preregistration=preregistration)
    return [
        ScientificRun(
            run.experiment_id,
            run.condition,
            run.seed,
            run.metrics,
            run.state_digest_before,
            run.state_digest_after,
            run.runtime_error,
        )
        for run in runs
    ]


def run_msba_e01(
    config: Config, seeds: tuple[int, ...] = (101, 102, 103)
) -> list[ScientificRun]:
    return _run_msba_registered(
        config,
        seeds,
        question_id="RQ-MSBA-E01",
        hypothesis_id="H-MSBA-E01-A",
        protocol_id="msba_energy_efficiency_v1",
        runner_name="run_msba_e01",
    )


def run_msba_e02(
    config: Config, seeds: tuple[int, ...] = (101, 102, 103)
) -> list[ScientificRun]:
    return _run_msba_registered(
        config,
        seeds,
        question_id="RQ-MSBA-E02",
        hypothesis_id="H-MSBA-E02-A",
        protocol_id="msba_resource_allocation_v1",
        runner_name="run_msba_e02",
    )


def run_msba_e03(
    config: Config, seeds: tuple[int, ...] = (101, 102, 103)
) -> list[ScientificRun]:
    return _run_msba_registered(
        config,
        seeds,
        question_id="RQ-MSBA-E03",
        hypothesis_id="H-MSBA-E03-A",
        protocol_id="msba_visual_roi_v1",
        runner_name="run_msba_e03",
    )


def run_msba_e04(
    config: Config, seeds: tuple[int, ...] = (101, 102, 103)
) -> list[ScientificRun]:
    return _run_msba_registered(
        config,
        seeds,
        question_id="RQ-MSBA-E04",
        hypothesis_id="H-MSBA-E04-A",
        protocol_id="msba_digital_integrity_v1",
        runner_name="run_msba_e04",
    )


def run_msba_e05(
    config: Config, seeds: tuple[int, ...] = (101, 102, 103)
) -> list[ScientificRun]:
    return _run_msba_registered(
        config,
        seeds,
        question_id="RQ-MSBA-E05",
        hypothesis_id="H-MSBA-E05-A",
        protocol_id="msba_modality_compensation_v1",
        runner_name="run_msba_e05",
    )


def run_embodied_closed_loop(
    config: Config, seeds: tuple[int, ...] = (101, 102, 103), ticks: int = 600
) -> list[ScientificRun]:
    """Run a registered exploratory SNN/body screen, never promote evidence."""
    from src.research.connectome_embodiment import run_protocol

    return run_protocol("embodied_closed_loop_v1", config, seeds, ticks)


def run_embodied_proprioception(
    config: Config, seeds: tuple[int, ...] = (101, 102, 103), ticks: int = 600
) -> list[ScientificRun]:
    """Run a registered exploratory SNN/body screen, never promote evidence."""
    from src.research.connectome_embodiment import run_protocol

    return run_protocol("embodied_proprioception_v1", config, seeds, ticks)


def run_embodied_perturbation(
    config: Config, seeds: tuple[int, ...] = (101, 102, 103), ticks: int = 600
) -> list[ScientificRun]:
    """Run a registered exploratory SNN/body screen, never promote evidence."""
    from src.research.connectome_embodiment import run_protocol

    return run_protocol("embodied_perturbation_screen_v1", config, seeds, ticks)


def run_connectome_topology(
    config: Config, seeds: tuple[int, ...] = (101, 102, 103), ticks: int = 600
) -> list[ScientificRun]:
    """Run a registered exploratory SNN/body screen, never promote evidence."""
    from src.research.connectome_embodiment import run_protocol

    return run_protocol("connectome_topology_screen_v1", config, seeds, ticks)


def run_embodied_controller(
    config: Config, seeds: tuple[int, ...] = (101, 102, 103), ticks: int = 600
) -> list[ScientificRun]:
    """Run a registered exploratory SNN/body screen, never promote evidence."""
    from src.research.connectome_embodiment import run_protocol

    return run_protocol("embodied_controller_attribution_v1", config, seeds, ticks)


def run_embodied_timing(
    config: Config, seeds: tuple[int, ...] = (101, 102, 103), ticks: int = 600
) -> list[ScientificRun]:
    """Run a registered exploratory SNN/body screen, never promote evidence."""
    from src.research.connectome_embodiment import run_protocol

    return run_protocol("embodied_timing_v1", config, seeds, ticks)


def run_eval_dimensional(
    config: Config,
    seeds: tuple[int, ...] = tuple(range(20001, 20011)),
    ticks: int = 256,
) -> list[ScientificRun]:
    """Execute the separately registered bounded empirical protocol."""
    from .empirical_evaluation import run_dimensional_ablation

    return run_dimensional_ablation(config, seeds, ticks)


def run_eval_association(
    config: Config, seeds: tuple[int, ...] = tuple(range(20001, 20011))
) -> list[ScientificRun]:
    """Execute the separately registered bounded empirical protocol."""
    from .empirical_evaluation import run_association_generalization

    return run_association_generalization(config, seeds)


def run_eval_brian2(
    config: Config, seeds: tuple[int, ...] = (20001, 20002, 20003)
) -> list[ScientificRun]:
    """Execute the separately registered bounded empirical protocol."""
    from .empirical_evaluation import run_brian2_conformance

    return run_brian2_conformance(config, seeds)


def run_eval_scaling(
    config: Config, seeds: tuple[int, ...] = (20001, 20002, 20003)
) -> list[ScientificRun]:
    """Execute the separately registered bounded empirical protocol."""
    from .empirical_evaluation import run_active_scaling

    return run_active_scaling(config, seeds)
