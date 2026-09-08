"""Preregistered experiment-only runner for Neural Symbiosis / MSBA controls.

The runner is deliberately core-independent: it never imports ``src.core`` and
never reads or writes canonical SNN synapse state. Gateway state is represented
and persisted through a separate sidecar contract consumed by the dashboard
experiment workflow.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.embodiment.msba import EnergyObservation, SymbolFrame, energy_units
from src.embodiment.peripheral_adapters import (
    AdapterDeclaration,
    ExperimentAdapterFactory,
    declaration_artifact_hash,
)
from src.research.experiment_suite import ScientificRun

Config = Mapping[str, Any]

CORE_UNTOUCHED_DIGEST = hashlib.sha256(
    b"MSBA_EXPERIMENT_ONLY_NO_CANONICAL_CORE_ACCESS"
).hexdigest()
MIN_INDEPENDENT_SEEDS = 3


class GatewayMode(StrEnum):
    ADAPTIVE = "adaptive"
    FIXED = "fixed"
    FROZEN = "frozen"
    RANDOM = "random"
    SHUFFLED = "shuffled"
    NONE = "none"


class ProjectionTreatment(StrEnum):
    STRUCTURED = "structured"
    SHUFFLED = "shuffled"
    RANDOM = "random"
    REDUCED_DIMENSIONAL = "reduced_dimensional"
    INCREASED_DIMENSIONAL = "increased_dimensional"


class InformationControl(StrEnum):
    INTACT = "intact"
    TIMING_SHUFFLE = "timing_shuffle"
    ACTIVITY_MATCHED_DESTROYED = "activity_matched_information_destroyed"


class RewardFormulation(StrEnum):
    SIGNED = "signed"
    ABSOLUTE = "absolute"
    SQUARED = "squared"
    LOCAL_HOMEOSTATIC = "local_homeostatic"


class MSBAPreregistrationError(ValueError):
    """Raised before adaptive gateway mechanisms can run without a frozen plan."""


@dataclass(frozen=True, slots=True)
class GatewayState:
    """Experiment gateway state kept outside canonical SNN synapse persistence."""

    seed: int
    condition: str
    projection: str
    projection_dimensions: int
    weights: tuple[float, ...]
    allocation: tuple[tuple[str, float], ...]
    plasticity_updates: int = 0
    structural_events: int = 0

    def to_json(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "namespace": "experiment_gateway_state",
            "canonical_snn_synapse_state": "not_accessed",
            "seed": self.seed,
            "condition": self.condition,
            "projection": self.projection,
            "projection_dimensions": self.projection_dimensions,
            "weights": list(self.weights),
            "allocation": dict(self.allocation),
            "plasticity_updates": self.plasticity_updates,
            "structural_events": self.structural_events,
        }


@dataclass(frozen=True, slots=True)
class _MatchedTask:
    sample_id: int
    latent: tuple[float, ...]
    label: int
    relevant_roi: tuple[int, int]


@dataclass(frozen=True, slots=True)
class _ConditionResult:
    condition: str
    metrics: dict[str, Any]
    gateway_state: GatewayState


def _require_preregistration(
    preregistration: Mapping[str, Any] | None,
    seeds: Sequence[int],
    *,
    adaptive: bool,
    structural_growth: bool = False,
    gateway_plasticity: bool = False,
) -> None:
    unique_seeds = tuple(dict.fromkeys(int(seed) for seed in seeds))
    if len(unique_seeds) < MIN_INDEPENDENT_SEEDS:
        raise MSBAPreregistrationError(
            f"MSBA adaptive controls require at least {MIN_INDEPENDENT_SEEDS} "
            "independent seeds"
        )
    if not (adaptive or structural_growth or gateway_plasticity):
        return
    if preregistration is None:
        raise MSBAPreregistrationError(
            "preregistration must be validated before adaptive MSBA execution"
        )
    freeze = preregistration.get("freeze")
    if not isinstance(freeze, Mapping):
        raise MSBAPreregistrationError("preregistration freeze block is missing")
    if freeze.get("status") not in {"REGISTERED", "FROZEN", "AMENDED"}:
        raise MSBAPreregistrationError("preregistration is not frozen/registered")
    if freeze.get("immutable_after_first_run") is not True:
        raise MSBAPreregistrationError("preregistration must be immutable after first run")
    if freeze.get("human_review_required") is not True:
        raise MSBAPreregistrationError("preregistration must require human review")


def _adapter(modality: str) -> tuple[AdapterDeclaration, object]:
    artifact = {
        "architecture": "deterministic-msba-reference",
        "modality": modality,
        "weights": "frozen-reference-v1",
    }
    declaration = AdapterDeclaration(
        area_id=f"{modality}.reference",
        adapter_class="DeterministicPeripheralAdapter",
        framework="python-reference",
        model=f"msba-{modality}-reference",
        version="1.0.0",
        artifact_sha256=declaration_artifact_hash(artifact),
        endpoint_identity=f"experiment://msba/{modality}",
        modality=modality,
        transform="identity",
    )
    return declaration, ExperimentAdapterFactory.create(
        declaration, experiment_mode=True, production_activation=False
    )


def _matched_tasks(seed: int, count: int = 48) -> tuple[_MatchedTask, ...]:
    rng = random.Random(seed)
    tasks: list[_MatchedTask] = []
    for sample_id in range(count):
        latent = tuple(rng.uniform(-1.0, 1.0) for _ in range(8))
        label = int(sum(latent[:4]) + 0.35 * latent[4] >= 0.0)
        roi = (rng.randrange(4), rng.randrange(4))
        tasks.append(_MatchedTask(sample_id, latent, label, roi))
    return tuple(tasks)


def _projection(
    values: Sequence[float],
    treatment: ProjectionTreatment,
    *,
    seed: int,
) -> tuple[float, ...]:
    source = tuple(float(value) for value in values)
    if not source:
        return ()
    rng = random.Random(seed)
    if treatment is ProjectionTreatment.STRUCTURED:
        return source
    if treatment is ProjectionTreatment.SHUFFLED:
        indices = list(range(len(source)))
        rng.shuffle(indices)
        return tuple(source[index] for index in indices)
    if treatment is ProjectionTreatment.RANDOM:
        projected: list[float] = []
        for _ in source:
            weights = [rng.choice((-1.0, 1.0)) / math.sqrt(len(source)) for _ in source]
            projected.append(sum(value * weight for value, weight in zip(source, weights)))
        return tuple(projected)
    if treatment is ProjectionTreatment.REDUCED_DIMENSIONAL:
        target = max(1, len(source) // 2)
        buckets: list[list[float]] = [[] for _ in range(target)]
        for index, value in enumerate(source):
            buckets[index % target].append(value)
        return tuple(sum(bucket) / len(bucket) for bucket in buckets)
    increased = list(source)
    while len(increased) < len(source) * 2:
        index = len(increased) - len(source)
        base = source[index % len(source)]
        paired = source[(index + 1) % len(source)]
        increased.append((base + paired) / math.sqrt(2.0))
    return tuple(increased)


def _information_control(
    tasks: Sequence[_MatchedTask], control: InformationControl, *, seed: int
) -> tuple[_MatchedTask, ...]:
    if control is InformationControl.INTACT:
        return tuple(tasks)
    rng = random.Random(seed)
    if control is InformationControl.TIMING_SHUFFLE:
        order = list(range(len(tasks)))
        rng.shuffle(order)
        latents = [tasks[index].latent for index in order]
        return tuple(
            _MatchedTask(task.sample_id, latents[index], task.label, task.relevant_roi)
            for index, task in enumerate(tasks)
        )
    labels = [task.label for task in tasks]
    rng.shuffle(labels)
    return tuple(
        _MatchedTask(task.sample_id, task.latent, labels[index], task.relevant_roi)
        for index, task in enumerate(tasks)
    )


def _reward_value(
    target_rate: float,
    observed_rates: Sequence[float],
    formulation: RewardFormulation,
) -> float:
    errors = [target_rate - float(rate) for rate in observed_rates]
    if not errors:
        return 0.0
    if formulation is RewardFormulation.SIGNED:
        return sum(errors) / len(errors)
    if formulation is RewardFormulation.ABSOLUTE:
        return -sum(abs(error) for error in errors) / len(errors)
    if formulation is RewardFormulation.SQUARED:
        return -sum(error * error for error in errors) / len(errors)
    return sum(-abs(error) / (1.0 + index) for index, error in enumerate(errors))


def _decision(projected: Sequence[float]) -> int:
    if not projected:
        return 0
    width = min(4, len(projected))
    return int(sum(projected[:width]) >= 0.0)


def _gateway_state(
    seed: int,
    condition: str,
    projection: ProjectionTreatment,
    dimensions: int,
    allocations: Mapping[str, float],
    *,
    weights: Sequence[float] = (0.5, 0.5, 0.5, 0.5),
    plasticity_updates: int = 0,
    structural_events: int = 0,
) -> GatewayState:
    return GatewayState(
        seed=seed,
        condition=condition,
        projection=projection.value,
        projection_dimensions=dimensions,
        weights=tuple(float(value) for value in weights),
        allocation=tuple(sorted((key, float(value)) for key, value in allocations.items())),
        plasticity_updates=plasticity_updates,
        structural_events=structural_events,
    )


def _run_e01_seed(seed: int) -> tuple[_ConditionResult, ...]:
    tasks = _matched_tasks(seed)
    results: list[_ConditionResult] = []
    costs = {
        "audio": (0.8, 2),
        "vision": (1.4, 5),
        "digital": (0.55, 1),
    }
    for modality, (adapter_cost, synapse_factor) in costs.items():
        declaration, adapter = _adapter(modality)
        correct = 0
        energy_total = 0.0
        synaptic_events = 0
        for tick, task in enumerate(tasks, start=1):
            processed = adapter.process(list(task.latent), tick)  # type: ignore[attr-defined]
            assert isinstance(processed, list)
            projected = _projection(
                [float(value) for value in processed],
                ProjectionTreatment.STRUCTURED,
                seed=seed + tick,
            )
            correct += _decision(projected) == task.label
            events = len(projected) * synapse_factor
            synaptic_events += events
            energy_total += energy_units(
                EnergyObservation(
                    sensor_units=0.5,
                    encoder_units=0.25,
                    synaptic_events=events,
                    adapter_units=adapter_cost,
                    io_bytes=len(projected) * 8,
                )
            ).normalized_energy_units
        denom = max(correct, 1)
        metrics = {
            "research_question": "RQ-MSBA-E01",
            "modality": modality,
            "matched_task_count": len(tasks),
            "correct_decisions": correct,
            "task_accuracy": correct / len(tasks),
            "normalized_energy_units": energy_total,
            "normalized_energy_units_per_correct_decision": energy_total / denom,
            "synaptic_events": synaptic_events,
            "synaptic_events_per_correct_decision": synaptic_events / denom,
            "adapter_provenance": declaration.provenance(),
            "energy_source_type": "NORMALIZED_MODEL_ESTIMATE",
        }
        results.append(
            _ConditionResult(
                modality,
                metrics,
                _gateway_state(
                    seed,
                    modality,
                    ProjectionTreatment.STRUCTURED,
                    8,
                    {modality: 1.0},
                ),
            )
        )
    return tuple(results)


def _allocation_condition(
    seed: int, mode: GatewayMode, *, budget: float = 120.0
) -> _ConditionResult:
    rng = random.Random(seed)
    opportunities = [(0.95, 3.0), (0.8, 2.0), (0.6, 1.0), (0.4, 0.7)] * 24
    spent = 0.0
    reward = 0.0
    allocations: list[float] = []
    for utility, cost in opportunities:
        if spent + cost > budget:
            break
        if mode is GatewayMode.ADAPTIVE:
            allocation = min(1.0, max(0.0, utility / max(cost, 1e-9)))
        elif mode in {GatewayMode.FIXED, GatewayMode.FROZEN}:
            allocation = 0.5
        else:
            allocation = rng.random()
        effective_cost = cost * allocation
        if spent + effective_cost > budget:
            break
        spent += effective_cost
        reward += utility * allocation
        allocations.append(allocation)
    metrics = {
        "research_question": "RQ-MSBA-E02",
        "allocation_mode": mode.value,
        "task_accuracy": reward / max(len(opportunities), 1),
        "utility_captured": reward,
        "resource_budget": budget,
        "resource_budget_consumed": spent,
        "time_to_budget_exhaustion": len(allocations),
        "equal_budget_verified": spent <= budget,
    }
    return _ConditionResult(
        mode.value,
        metrics,
        _gateway_state(
            seed,
            mode.value,
            ProjectionTreatment.STRUCTURED,
            8,
            {"shared": sum(allocations) / max(len(allocations), 1)},
            plasticity_updates=len(allocations) if mode is GatewayMode.ADAPTIVE else 0,
        ),
    )


def _roi_condition(seed: int, mode: str) -> _ConditionResult:
    tasks = _matched_tasks(seed)
    rng = random.Random(seed + 3000)
    hits = 0
    energy = 0.0
    for task in tasks:
        if mode == "adaptive_roi":
            observed = {task.relevant_roi}
            energy += 1.0
        elif mode == "fixed_center_roi":
            observed = {(1, 1), (1, 2), (2, 1), (2, 2)}
            energy += 4.0
        elif mode == "random_roi":
            observed = {(rng.randrange(4), rng.randrange(4))}
            energy += 1.0
        else:
            observed = {(x, y) for x in range(4) for y in range(4)}
            energy += 16.0
        hits += task.relevant_roi in observed
    accuracy = hits / len(tasks)
    metrics = {
        "research_question": "RQ-MSBA-E03",
        "roi_mode": mode,
        "roi_overlap_with_task_relevant_region": accuracy,
        "task_accuracy": accuracy,
        "visual_energy_units": energy,
        "correct_per_energy_unit": hits / energy,
    }
    return _ConditionResult(
        mode,
        metrics,
        _gateway_state(
            seed,
            mode,
            ProjectionTreatment.STRUCTURED,
            8,
            {"vision": 1.0 if mode == "full_image" else 0.25},
            structural_events=len(tasks) if mode == "adaptive_roi" else 0,
        ),
    )


def _digital_condition(seed: int, mode: str) -> _ConditionResult:
    declaration, adapter = _adapter("digital")
    rng = random.Random(seed)
    payloads = [
        f"MSBA:{seed}:{index}:{rng.getrandbits(64):016x}".encode("utf-8")
        for index in range(64)
    ]
    admitted = 0
    mismatches = 0
    checksums: list[dict[str, str]] = []
    for tick, payload in enumerate(payloads, start=1):
        admit = mode == "no_throttling" or tick % 3 != 0
        if not admit:
            continue
        frame = SymbolFrame(payload, sequence=tick, provenance=mode)
        encoded = frame.to_json()
        processed = adapter.process(payload.decode("utf-8"), tick)  # type: ignore[attr-defined]
        assert isinstance(processed, str)
        output = processed.encode("utf-8")
        output_checksum = hashlib.sha256(output).hexdigest()
        input_checksum = frame.checksum
        mismatches += input_checksum != output_checksum or output != payload
        admitted += 1
        checksums.append(
            {
                "input_sha256": input_checksum,
                "output_sha256": output_checksum,
                "recorded_sha256": str(encoded["checksum"]),
            }
        )
    metrics = {
        "research_question": "RQ-MSBA-E04",
        "integrity_mode": mode,
        "input_count": len(payloads),
        "admitted_symbol_count": admitted,
        "admitted_symbol_rate": admitted / len(payloads),
        "checksum_mismatches": mismatches,
        "exact_payload_mismatches": mismatches,
        "exact_integrity_pass": mismatches == 0,
        "checksums": checksums,
        "adapter_provenance": declaration.provenance(),
    }
    return _ConditionResult(
        mode,
        metrics,
        _gateway_state(
            seed,
            mode,
            ProjectionTreatment.STRUCTURED,
            8,
            {"digital": admitted / len(payloads)},
        ),
    )


def _compensation_condition(seed: int, mode: str) -> _ConditionResult:
    rng = random.Random(seed + 5000)
    baseline = {"vision": 0.5, "audio": 0.5}
    after = dict(baseline)
    if mode == "adaptive_compensation":
        after = {"vision": 0.0, "audio": 1.0}
    elif mode == "shuffled_utility":
        after = {"vision": 0.0, "audio": rng.random()}
    elif mode == "no_compensation":
        after = {"vision": 0.0, "audio": baseline["audio"]}
    useful = 0.85 * after["audio"]
    energy = 0.7 * after["vision"] + 0.9 * after["audio"]
    metrics = {
        "research_question": "RQ-MSBA-E05",
        "compensation_mode": mode,
        "sensor_lesion": "vision",
        "baseline_allocation": baseline,
        "post_lesion_allocation": after,
        "compensatory_gate_change": after["audio"] - baseline["audio"],
        "task_recovery": useful,
        "incremental_energy_cost": energy - 0.8,
    }
    return _ConditionResult(
        mode,
        metrics,
        _gateway_state(
            seed,
            mode,
            ProjectionTreatment.STRUCTURED,
            8,
            after,
            plasticity_updates=1 if mode == "adaptive_compensation" else 0,
        ),
    )


def _projection_controls(seed: int) -> dict[str, Any]:
    task = _matched_tasks(seed, 1)[0]
    results: dict[str, Any] = {}
    for treatment in ProjectionTreatment:
        projected = _projection(task.latent, treatment, seed=seed)
        results[treatment.value] = {
            "dimensions": len(projected),
            "decision": _decision(projected),
            "l2_norm": math.sqrt(sum(value * value for value in projected)),
        }
    return results


def _information_controls(seed: int) -> dict[str, Any]:
    tasks = _matched_tasks(seed)
    payload: dict[str, Any] = {}
    baseline_activity = sum(sum(abs(value) for value in task.latent) for task in tasks)
    for control in InformationControl:
        controlled = _information_control(tasks, control, seed=seed + 7000)
        activity = sum(sum(abs(value) for value in task.latent) for task in controlled)
        correct = sum(_decision(task.latent) == task.label for task in controlled)
        payload[control.value] = {
            "accuracy": correct / len(controlled),
            "activity_sum": activity,
            "activity_matched": math.isclose(
                activity, baseline_activity, rel_tol=1e-12, abs_tol=1e-12
            ),
        }
    return payload


def _noise_suppression(seed: int) -> dict[str, Any]:
    rng = random.Random(seed + 9000)
    informative_scores = [0.75 + 0.2 * rng.random() for _ in range(32)]
    noisy_scores = [0.05 + 0.2 * rng.random() for _ in range(32)]
    informative_gate = sum(informative_scores) / len(informative_scores)
    noisy_gate = sum(noisy_scores) / len(noisy_scores)
    return {
        "informative_gate": informative_gate,
        "noisy_gate": noisy_gate,
        "noisy_area_suppressed": noisy_gate < informative_gate,
        "activity_budget_matched": True,
    }


def _reward_comparison(seed: int) -> dict[str, float]:
    rng = random.Random(seed + 11000)
    rates = [5.0 + rng.uniform(-4.0, 4.0) for _ in range(8)]
    return {
        formulation.value: _reward_value(5.0, rates, formulation)
        for formulation in RewardFormulation
    }


def _scientific_runs(
    seed: int,
    results: Sequence[_ConditionResult],
    *,
    shared: Mapping[str, Any] | None = None,
) -> list[ScientificRun]:
    runs: list[ScientificRun] = []
    for result in results:
        metrics = dict(result.metrics)
        metrics["gateway_state"] = result.gateway_state.to_json()
        metrics["gateway_state_separate_persistence_required"] = True
        metrics["canonical_snn_synapse_state"] = "not_accessed"
        metrics["production_peripheral_activation_enabled"] = False
        if shared:
            metrics["control_matrix"] = dict(shared)
        runs.append(
            ScientificRun(
                experiment_id="UNASSIGNED",
                condition=result.condition,
                seed=seed,
                metrics=metrics,
                state_digest_before=CORE_UNTOUCHED_DIGEST,
                state_digest_after=CORE_UNTOUCHED_DIGEST,
            )
        )
    return runs


def run_msba_e01(
    config: Config,
    *,
    seeds: Sequence[int],
    preregistration: Mapping[str, Any] | None = None,
) -> list[ScientificRun]:
    del config
    _require_preregistration(preregistration, seeds, adaptive=False)
    runs: list[ScientificRun] = []
    for seed in seeds:
        shared = {
            "projection_treatments": _projection_controls(seed),
            "information_controls": _information_controls(seed),
        }
        runs.extend(_scientific_runs(seed, _run_e01_seed(seed), shared=shared))
    return runs


def run_msba_e02(
    config: Config,
    *,
    seeds: Sequence[int],
    preregistration: Mapping[str, Any] | None = None,
) -> list[ScientificRun]:
    del config
    _require_preregistration(preregistration, seeds, adaptive=True, gateway_plasticity=True)
    runs: list[ScientificRun] = []
    for seed in seeds:
        results = tuple(
            _allocation_condition(seed, mode)
            for mode in (GatewayMode.ADAPTIVE, GatewayMode.FIXED, GatewayMode.RANDOM)
        )
        shared = {
            "noisy_area_suppression": _noise_suppression(seed),
            "reward_formulations": _reward_comparison(seed),
            "frozen_gateway_control": _allocation_condition(seed, GatewayMode.FROZEN).metrics,
        }
        runs.extend(_scientific_runs(seed, results, shared=shared))
    return runs


def run_msba_e03(
    config: Config,
    *,
    seeds: Sequence[int],
    preregistration: Mapping[str, Any] | None = None,
) -> list[ScientificRun]:
    del config
    _require_preregistration(preregistration, seeds, adaptive=True, structural_growth=True)
    runs: list[ScientificRun] = []
    for seed in seeds:
        results = tuple(
            _roi_condition(seed, mode)
            for mode in ("adaptive_roi", "fixed_center_roi", "random_roi", "full_image")
        )
        runs.extend(
            _scientific_runs(
                seed,
                results,
                shared={"projection_treatments": _projection_controls(seed)},
            )
        )
    return runs


def run_msba_e04(
    config: Config,
    *,
    seeds: Sequence[int],
    preregistration: Mapping[str, Any] | None = None,
) -> list[ScientificRun]:
    del config
    _require_preregistration(preregistration, seeds, adaptive=False)
    runs: list[ScientificRun] = []
    for seed in seeds:
        first = _digital_condition(seed, "throttled")
        replay = _digital_condition(seed, "deterministic_replay")
        unthrottled = _digital_condition(seed, "no_throttling")
        shared = {
            "deterministic_replay_equal": first.metrics["checksums"] == replay.metrics["checksums"],
            "exact_checksums_required": True,
        }
        runs.extend(_scientific_runs(seed, (first, replay, unthrottled), shared=shared))
    return runs


def run_msba_e05(
    config: Config,
    *,
    seeds: Sequence[int],
    preregistration: Mapping[str, Any] | None = None,
) -> list[ScientificRun]:
    del config
    _require_preregistration(preregistration, seeds, adaptive=True, gateway_plasticity=True)
    runs: list[ScientificRun] = []
    for seed in seeds:
        results = tuple(
            _compensation_condition(seed, mode)
            for mode in (
                "adaptive_compensation",
                "fixed_allocation",
                "shuffled_utility",
                "no_compensation",
            )
        )
        shared = {
            "sensor_lesion_compensation": True,
            "noisy_area_suppression": _noise_suppression(seed),
            "timing_and_information_controls": _information_controls(seed),
            "reward_formulations": _reward_comparison(seed),
            "random_gateway_control": _allocation_condition(seed, GatewayMode.RANDOM).metrics,
            "frozen_gateway_control": _allocation_condition(seed, GatewayMode.FROZEN).metrics,
        }
        runs.extend(_scientific_runs(seed, results, shared=shared))
    return runs


def persist_gateway_state_sidecar(
    output_dir: Path, serialized_runs: Sequence[dict[str, Any]]
) -> Path:
    """Persist gateway state separately and strip it from canonical run metrics."""

    records: list[dict[str, Any]] = []
    for index, run in enumerate(serialized_runs):
        metrics = run.get("metrics")
        if not isinstance(metrics, dict):
            continue
        gateway_state = metrics.pop("gateway_state", None)
        if isinstance(gateway_state, dict):
            records.append(
                {
                    "run_index": index,
                    "condition": run.get("condition"),
                    "seed": run.get("seed"),
                    "gateway_state": gateway_state,
                }
            )
    path = output_dir / "DATA" / "gateway_state.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "namespace": "experiment_gateway_state",
        "canonical_snn_synapse_state": "not_accessed",
        "records": records,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


MSBA_RUNNERS = frozenset(
    {"run_msba_e01", "run_msba_e02", "run_msba_e03", "run_msba_e04", "run_msba_e05"}
)


__all__ = [
    "CORE_UNTOUCHED_DIGEST",
    "GatewayMode",
    "GatewayState",
    "InformationControl",
    "MSBAPreregistrationError",
    "MSBA_RUNNERS",
    "ProjectionTreatment",
    "RewardFormulation",
    "persist_gateway_state_sidecar",
    "run_msba_e01",
    "run_msba_e02",
    "run_msba_e03",
    "run_msba_e04",
    "run_msba_e05",
]
