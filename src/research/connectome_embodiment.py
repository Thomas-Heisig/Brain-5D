"""Experiment-only SNN/body screens with explicit causal controls.

Fixed six-neuron Izhikevich network, hand-designed error receptors and fixed
spike-to-torque decoder. These are engineering diagnostics, NOT fly replication,
learned body schema, biological equivalence, or a test of five-dimensional merit.
All changing world/readout states are recorded separately from neural state.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from src.core import NeuralNetwork
from src.core.synapse import SynapseConfig
from src.embodiment.joint_world import JointParameters, JointWorld
from src.research.canonical_state import canonical_state_digest
from src.research.connectome_reference import synthetic_graph, transform_graph
from src.research.experiment_suite import ScientificRun

PROGRAM = Path("protocols/CONNECTOME_EMBODIMENT_V1.json")
ROOT = Path(__file__).resolve().parents[2] / "research"
RUNNERS = {
    "embodied_closed_loop_v1": "run_embodied_closed_loop",
    "embodied_proprioception_v1": "run_embodied_proprioception",
    "embodied_perturbation_screen_v1": "run_embodied_perturbation",
    "connectome_topology_screen_v1": "run_connectome_topology",
    "embodied_controller_attribution_v1": "run_embodied_controller",
    "embodied_timing_v1": "run_embodied_timing",
}


def _digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, allow_nan=False, separators=(",", ":"))
    return hashlib.sha256(encoded.encode()).hexdigest()


def _network(
    config: Mapping[str, Any], seed: int, topology: str
) -> tuple[NeuralNetwork, list[int], dict[str, Any]]:
    values = dict(config)
    values.update(dimensions=[6, 1, 1, 1, 1], initial_neurons=0)
    values["simulation"] = {"dt_ms": 1.0, "max_delay": 20}
    values["stdp"] = {"enabled": False}
    graph = transform_graph(synthetic_graph(seed), topology, seed)
    network = NeuralNetwork(values, random.Random(seed))
    ids = [network.add_neuron((i, 0, 0, 0, 0)) for i in range(6)]
    network.input_cells.update(ids[:2])
    network.output_cells.update(ids[4:])
    for edge in graph.edges:
        network.connect(
            ids[int(edge.source)],
            ids[int(edge.target)],
            edge.weight,
            edge.delay_ticks,
            config=SynapseConfig(w_max=200.0),
        )
    return network, ids, graph.fingerprint()


@dataclass
class LoopResult:
    metrics: dict[str, Any]
    before: str
    after: str
    sensor_tape: list[tuple[float, float]] = field(
        default_factory=list[tuple[float, float]]
    )
    motor_tape: list[float] = field(default_factory=list[float])
    error: str | None = None


def _simulate(
    config: Mapping[str, Any],
    seed: int,
    ticks: int,
    condition: str,
    *,
    donor: LoopResult | None = None,
    perturb: bool = True,
) -> LoopResult:
    topology = (
        condition
        if condition
        in {"structured", "degree_preserving", "weight_shuffle", "random_edges"}
        else "structured"
    )
    network, ids, fingerprint = _network(config, seed, topology)
    body = JointWorld(JointParameters(), q_rad=random.Random(seed).uniform(-0.05, 0.05))
    before = canonical_state_digest(network)
    initial_body = body.state()
    sensor_period = (
        int(condition.removeprefix("sensor_").removesuffix("ms"))
        if condition.startswith("sensor_")
        else 1
    )
    physics_period = (
        int(condition.removeprefix("physics_").removesuffix("ms"))
        if condition.startswith("physics_")
        else 1
    )
    batch = (
        int(condition.removeprefix("batch_")) if condition.startswith("batch_") else 1
    )
    sensor_tape: list[tuple[float, float]] = []
    motor_tape: list[float] = []
    trace: list[dict[str, Any]] = []
    delayed: list[tuple[float, float]] = []
    permutation = list(range(ticks))
    random.Random(seed ^ 0x51F7).shuffle(permutation)
    sensor = (body.q_rad, body.omega_rad_s)
    filtered_motor = torque_sum = force_sum = squared_error = 0.0
    pending_steps = spikes = actions = delivered = 0
    activated: set[int] = set()
    failure: str | None = None
    executed = 0
    try:
        for start in range(0, ticks, batch):
            for t in range(start, min(start + batch, ticks)):
                # Event order: receptors -> neural step -> decoder -> physics -> trace.
                target = 0.25 if t < ticks // 2 else -0.25
                if t % sensor_period == 0:
                    sensor = (body.q_rad, body.omega_rad_s)
                sensor_tape.append(sensor)
                delayed.append(sensor)
                observed = sensor
                if condition == "feedback_absent":
                    observed = (0.0, 0.0)
                elif condition == "delayed_proprioception":
                    observed = delayed[max(0, t - 20)]
                elif condition in {"yoked_replay", "timing_shuffle"}:
                    if donor is None or len(donor.sensor_tape) != ticks:
                        raise ValueError("Complete precomputed donor tape required")
                    index = permutation[t] if condition == "timing_shuffle" else t
                    observed = donor.sensor_tape[index]
                error = target - observed[0]
                # Engineered transducer: declared error and velocity feedback.
                drive = 70.0 * error - 1.5 * observed[1]
                currents = {
                    ids[0]: 2.0 + max(0.0, min(80.0, drive)),
                    ids[1]: 2.0 + max(0.0, min(80.0, -drive)),
                }
                network.inject_current_batch(currents)
                step = network.step()
                spikes += step.spikes_this_tick
                activated.update(step.spike_ids)
                delivered += step.delivered_events
                filtered_motor = (
                    0.95 * filtered_motor
                    + float(ids[4] in step.spike_ids)
                    - float(ids[5] in step.spike_ids)
                )
                torque = 0.008 * filtered_motor
                if condition == "disconnected_motor":
                    torque = 0.0
                elif condition == "controller_only":
                    torque = 0.025 * (target - body.q_rad) - 0.003 * body.omega_rad_s
                elif condition == "shuffled_motor":
                    if donor is None or len(donor.motor_tape) != ticks:
                        raise ValueError("Complete precomputed motor tape required")
                    torque = donor.motor_tape[permutation[t]]
                motor_tape.append(torque)
                actions += int(torque != 0.0)
                torque_sum += torque
                force_sum += 0.003 if perturb and ticks // 4 <= t < ticks // 2 else 0.0
                pending_steps += 1
                gain = 1.0
                blocked = False
                if t >= ticks // 3:
                    if condition in {"weak_actuator", "restored_actuator"}:
                        gain = (
                            0.2
                            if condition == "weak_actuator" or t < 2 * ticks // 3
                            else 1.0
                        )
                    blocked = condition == "blocked_joint"
                applied: float | None = None
                if pending_steps == physics_period or t == ticks - 1:
                    applied = body.advance(
                        torque_sum / pending_steps,
                        pending_steps * 0.001,
                        external_torque_nm=force_sum / pending_steps,
                        actuator_gain=gain,
                        blocked=blocked,
                    )
                    torque_sum = force_sum = 0.0
                    pending_steps = 0
                squared_error += (target - body.q_rad) ** 2
                executed = t + 1
                trace.append(
                    {
                        "tick": executed,
                        "target_rad": target,
                        "q_rad": body.q_rad,
                        "omega_rad_s": body.omega_rad_s,
                        "observed_q_rad": observed[0],
                        "observed_omega_rad_s": observed[1],
                        "spike_ids": list(step.spike_ids),
                        "command_nm": torque,
                        "applied_nm": applied,
                        "actuator_gain": gain,
                        "blocked": blocked,
                    }
                )
    except (ValueError, ArithmeticError, RuntimeError) as exc:
        failure = f"{type(exc).__name__}: {exc}"
    after = canonical_state_digest(network)
    boundary = {
        "body": body.state(),
        "filtered_motor": filtered_motor,
        "sensor": sensor,
        "pending_steps": pending_steps,
        "neural_digest": after,
        "ticks": executed,
    }
    metrics: dict[str, Any] = {
        "ticks_requested": ticks,
        "ticks_executed": executed,
        "total_spikes": spikes,
        "activated_neuron_count": len(activated),
        "synaptic_events_delivered": delivered,
        "nonzero_action_ticks": actions,
        "tracking_rmse_rad": math.sqrt(squared_error / executed) if executed else None,
        "modelled_absolute_work_j": body.modelled_absolute_work_j,
        "measured_hardware_energy_j": None,
        "integrity_contact_count": body.contact_count,
        "torque_saturation_count": body.saturation_count,
        "neural_dt_ms": 1.0,
        "physics_period_ticks": physics_period,
        "sensor_period_ticks": sensor_period,
        "execution_batch_ticks": batch,
        "graph": fingerprint,
        "data_kind": "SYNTHETIC",
        "controller": (
            "PD_ONLY_IGNORES_SNN"
            if condition == "controller_only"
            else "FIXED_SPIKE_TO_TORQUE"
        ),
        "learning_enabled": False,
        "biological_replication": False,
        "gateway_state_before": {"body": initial_body, "filtered_motor": 0.0},
        "gateway_state_after": boundary,
        "closed_loop_state_sha256": _digest(boundary),
        "donor_tape_sha256": _digest(donor.sensor_tape) if donor is not None else None,
        "donor_motor_sha256": _digest(donor.motor_tape) if donor is not None else None,
        "donor_ticks_overhead": ticks if donor is not None else 0,
        "effective_config": dict(
            config,
            dimensions=[6, 1, 1, 1, 1],
            initial_neurons=0,
            simulation={"dt_ms": 1.0, "max_delay": 20},
            stdp={"enabled": False},
        ),
        "boundary_contract": {
            "version": "joint-v1",
            "input_gain": 70.0,
            "velocity_gain": 1.5,
            "tonic_current": 2.0,
            "decoder_decay": 0.95,
            "decoder_nm_per_unit": 0.008,
            "learning": "disabled",
            "UI_dependency": "none",
        },
        "trace": trace,
        "trace_sha256": _digest(trace),
        "units": {
            "angles": "rad",
            "angular_velocity": "rad/s",
            "torque": "N m",
            "modelled_work": "J",
        },
        "inference": "engineering_screen_only_no_EVID_promotion",
    }
    return LoopResult(metrics, before, after, sensor_tape, motor_tape, failure)


def run_protocol(
    protocol_id: str,
    config: Mapping[str, Any],
    seeds: tuple[int, ...] = (101, 102, 103),
    ticks: int = 600,
) -> list[ScientificRun]:
    """Execute every registered arm and retain errors; never adapt a protocol post hoc."""
    from src.research.connectome_governance import verify_design_lock
    from src.research.protocol_registry import (
        protocol_by_id,
        validate_operational_protocol,
    )

    verify_design_lock(ROOT)
    if protocol_id not in RUNNERS:
        raise ValueError("No native connectome/embodiment runner for this protocol")
    if type(ticks) is not int or not 60 <= ticks <= 10000:
        raise ValueError("Exploratory embodiment screens require 60..10000 ticks")
    if len(seeds) != len(set(seeds)) or any(type(s) is not int for s in seeds):
        raise ValueError("Seeds must be distinct integers")
    protocol = protocol_by_id(ROOT, protocol_id)
    if protocol is None:
        raise ValueError("Missing registered exploratory protocol")
    prereg = validate_operational_protocol(
        ROOT,
        question_id=protocol["research_question"],
        hypothesis_id=protocol["hypothesis"],
        protocol_id=protocol_id,
        seed_count=len(seeds),
    )
    runs: list[ScientificRun] = []
    prereg_hash = hashlib.sha256(
        (ROOT / protocol["preregistration"]).read_bytes()
    ).hexdigest()
    conditions = prereg["conditions"]
    donor_needed = any(
        c in {"yoked_replay", "timing_shuffle", "shuffled_motor"} for c in conditions
    )
    budget = len(seeds) * ticks * (len(conditions) + int(donor_needed))
    if budget > 250000:
        raise ValueError(
            "Native screen exceeds 250000 total neural ticks including donor runs"
        )
    for seed in seeds:
        needs_donor = any(
            c in {"yoked_replay", "timing_shuffle", "shuffled_motor"}
            for c in conditions
        )
        donor = (
            _simulate(config, seed, ticks, "closed_loop", perturb=False)
            if needs_donor
            else None
        )
        seed_results: list[tuple[str, LoopResult]] = []
        for condition in conditions:
            result = _simulate(config, seed, ticks, condition, donor=donor)
            result.metrics.update(
                protocol_id=protocol_id,
                preregistration_sha256=prereg_hash,
                donor_runtime_error=donor.error if donor is not None else None,
            )
            seed_results.append((condition, result))
        batch_digests = {
            result.metrics["closed_loop_state_sha256"]
            for condition, result in seed_results
            if condition.startswith("batch_")
        }
        for condition, result in seed_results:
            if protocol_id == "embodied_timing_v1":
                result.metrics["batch_digest_identity"] = len(batch_digests) == 1
            runs.append(
                ScientificRun(
                    "EXP-CONNECTOME-SCREEN",
                    condition,
                    seed,
                    result.metrics,
                    result.before,
                    result.after,
                    result.error,
                )
            )
    return runs


def persist_boundary_state(output_dir: Path, runs: list[dict[str, Any]]) -> Path:
    """Persist body/decoder state independently of the canonical SNN snapshot."""
    records = [
        {
            "seed": run["seed"],
            "condition": run["condition"],
            "before": run["metrics"]["gateway_state_before"],
            "after": run["metrics"]["gateway_state_after"],
            "boundary_contract": run["metrics"]["boundary_contract"],
            "neural_digest_before": run["state_digest_before"],
            "neural_digest_after": run["state_digest_after"],
        }
        for run in runs
    ]
    path = output_dir / "DATA/gateway_state.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "kind": "synthetic_joint_boundary",
                "canonical_snn_state": False,
                "resume_supported": False,
                "runs": records,
            },
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return path
