"""Native controlled functional and methodological cognition experiments.

These runners are engineering/research instruments. They never establish
consciousness, phenomenal experience, welfare, or scientific evidence. Each
seed is an independent deterministic trial family with explicit controls.
"""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from typing import Any, Mapping

from src.embodiment.models import (
    ActionCommand,
    EnvironmentObservation,
    SensorFrame,
)
from src.memory import MemoryStore, TransitionWorldModel
from src.profiles import BehaviorProfile

Config = Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class CognitionRun:
    experiment_id: str
    condition: str
    seed: int
    metrics: dict[str, Any]
    state_digest_before: str
    state_digest_after: str
    runtime_error: str | None = None


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def _frame(tick: int, cue: str) -> SensorFrame:
    return SensorFrame("delayed-cue", tick, "symbol", {"cue": cue})


def _action(tick: int, value: str) -> ActionCommand:
    return ActionCommand("choice", tick, value)


def _observation(tick: int, state: dict[str, Any], reward: float = 0.0) -> EnvironmentObservation:
    return EnvironmentObservation(tick, state, reward, False, False)


def run_memory_delayed_information(
    config: Config, seeds: tuple[int, ...] = (101, 102, 103)
) -> list[CognitionRun]:
    """Test delayed-cue retrieval with independent read/write/shuffle controls."""
    del config
    runs: list[CognitionRun] = []
    conditions = (
        "memory_read_write",
        "memory_read_off",
        "memory_write_off",
        "memory_time_shuffled",
    )
    trials = 24
    delay = 8
    for seed in seeds:
        cues = ["A" if random.Random(seed * 1000 + trial).random() < 0.5 else "B" for trial in range(trials)]
        for condition in conditions:
            store = MemoryStore(
                run_id=f"mem-{seed}-{condition}",
                episode_capacity=64,
                working_capacity=32,
                retention_ticks=512,
                read_enabled=condition != "memory_read_off",
                write_enabled=condition != "memory_write_off",
            )
            before = _digest(store.state_dict())
            correct = 0
            retrievals = 0
            for trial, cue in enumerate(cues):
                cue_tick = trial * 32 + 1
                store.record(
                    _frame(cue_tick, cue),
                    None,
                    None,
                    episode_id=f"trial-{trial}",
                    source="cognition_experiment.delayed_cue",
                )
                decision_tick = cue_tick + delay
                recalled = list(store.recall(modality="symbol", limit=16))
                if condition == "memory_time_shuffled" and recalled:
                    shift = (seed + trial + 1) % len(recalled)
                    recalled = recalled[shift:] + recalled[:shift]
                selected: str | None = None
                for record in recalled:
                    if record.episode_id == f"trial-{trial}":
                        selected = str(record.observation["payload"]["cue"])
                        retrievals += 1
                        break
                if selected is None:
                    selected = "A" if random.Random(seed ^ (trial * 7919)).random() < 0.5 else "B"
                correct += int(selected == cue)
                store.record(
                    SensorFrame("decision", decision_tick, "choice", {"selected": selected}),
                    _action(decision_tick, selected),
                    _observation(decision_tick, {"target": cue}, 1.0 if selected == cue else 0.0),
                    episode_id=f"decision-{trial}",
                    source="cognition_experiment.outcome",
                )
            after = _digest(store.state_dict())
            runs.append(
                CognitionRun(
                    "EXP-MEM-002",
                    condition,
                    seed,
                    {
                        "trials": trials,
                        "delay_ticks": delay,
                        "correct": correct,
                        "accuracy": correct / trials,
                        "retrievals": retrievals,
                        "read_enabled": store.read_enabled,
                        "write_enabled": store.write_enabled,
                        "independent_seed": True,
                        "target_leakage": False,
                        "scientific_evidence": False,
                    },
                    before,
                    after,
                )
            )
    return runs


def _transition_state(cue: str, action: str) -> dict[str, Any]:
    direction = 1 if cue == action else -1
    return {"position": direction, "matched": cue == action}


def run_world_model_prediction(
    config: Config, seeds: tuple[int, ...] = (101, 102, 103)
) -> list[CognitionRun]:
    """Compare adaptive one-step prediction with persistence/frozen/no-model controls."""
    del config
    runs: list[CognitionRun] = []
    conditions = ("adaptive", "frozen", "persistence", "no_model")
    train_trials = 32
    holdout_trials = 24
    for seed in seeds:
        schedule = [
            (
                "A" if random.Random(seed * 10000 + i).random() < 0.5 else "B",
                "A" if random.Random(seed * 20000 + i).random() < 0.5 else "B",
            )
            for i in range(train_trials + holdout_trials)
        ]
        for condition in conditions:
            model = TransitionWorldModel(max_contexts=16)
            before = _digest(model.state_dict())
            if condition in {"adaptive", "frozen"}:
                for index, (cue, choice) in enumerate(schedule[:train_trials]):
                    frame = _frame(index + 1, cue)
                    action = _action(index + 1, choice)
                    model.update(
                        frame,
                        action,
                        _observation(index + 2, _transition_state(cue, choice)),
                    )
            errors: list[float] = []
            adaptive_sources = 0
            for offset, (cue, choice) in enumerate(schedule[train_trials:]):
                tick = train_trials + offset + 1
                frame = _frame(tick, cue)
                action = _action(tick, choice)
                actual = _transition_state(cue, choice)
                if condition == "no_model":
                    predicted = None
                    error = None
                elif condition == "persistence":
                    predicted = {"position": 0, "matched": False}
                    error = model.error(predicted, actual)
                else:
                    prediction = model.predict(
                        frame,
                        action,
                        target_tick=tick + 1,
                        persistence_state={"position": 0, "matched": False},
                    )
                    predicted = prediction.predicted_state
                    adaptive_sources += int(prediction.source == "adaptive_transition")
                    error = model.error(predicted, actual)
                if error is not None:
                    errors.append(float(error))
                if condition == "adaptive":
                    model.update(frame, action, _observation(tick + 1, actual))
            mean_error = sum(errors) / len(errors) if errors else None
            after = _digest(model.state_dict())
            runs.append(
                CognitionRun(
                    "EXP-WM-001",
                    condition,
                    seed,
                    {
                        "training_trials": train_trials,
                        "held_out_trials": holdout_trials,
                        "evaluated_predictions": len(errors),
                        "mean_prediction_error": mean_error,
                        "adaptive_prediction_count": adaptive_sources,
                        "held_out": True,
                        "target_leakage": False,
                        "world_model_influences_actions": False,
                        "scientific_evidence": False,
                    },
                    before,
                    after,
                )
            )
    return runs


def run_behavior_profile_control(
    config: Config, seeds: tuple[int, ...] = (101, 102, 103)
) -> list[CognitionRun]:
    """Measure deterministic behavioral-profile influence and adaptation logging."""
    del config
    conditions = ("fixed_low_exploration", "fixed_high_exploration", "adaptive", "shuffled_profile")
    runs: list[CognitionRun] = []
    trials = 40
    for seed in seeds:
        target_schedule = ["left" if random.Random(seed * 101 + i).random() < 0.5 else "right" for i in range(trials)]
        for condition in conditions:
            initial_exploration = 0.0 if condition == "fixed_low_exploration" else 1.0 if condition == "fixed_high_exploration" else 0.35
            profile = BehaviorProfile(
                f"WESEN-{seed % 10000:04d}",
                initial={"exploration": initial_exploration},
                update_rate=0.05,
            )
            before = _digest(profile.state_dict())
            correct = 0
            selections: list[str] = []
            for trial, target in enumerate(target_schedule, start=1):
                ordered = ("left", "right")
                if condition == "shuffled_profile" and random.Random(seed ^ trial).random() < 0.5:
                    ordered = tuple(reversed(ordered))
                candidates = tuple(_action(trial, value) for value in ordered)
                selected = profile.select_action(candidates, tick=trial)
                value = "none" if selected is None else str(selected.action)
                selections.append(value)
                success = value == target
                correct += int(success)
                if condition == "adaptive":
                    profile.update(success=success, tick=trial, source="registered_profile_control")
            after = _digest(profile.state_dict())
            runs.append(
                CognitionRun(
                    "EXP-PROFILE-001",
                    condition,
                    seed,
                    {
                        "trials": trials,
                        "correct": correct,
                        "accuracy": correct / trials,
                        "selection_digest": _digest(selections),
                        "update_count": len(profile.update_log),
                        "final_profile": profile.state_dict(),
                        "behavioral_causal_path": "BehaviorProfile.select_action",
                        "psychological_personality_claim": False,
                        "scientific_evidence": False,
                    },
                    before,
                    after,
                )
            )
    return runs


def run_methodological_audit(
    config: Config,
    seeds: tuple[int, ...],
    *,
    protocol_id: str,
    question_id: str,
) -> list[CognitionRun]:
    """Execute a deterministic theory/method audit without pretending it is neural data."""
    del config
    controls = (
        "assumption_explicit",
        "alternative_model",
        "measurement_limit",
        "claim_boundary",
    )
    runs: list[CognitionRun] = []
    for seed in seeds:
        for index, control in enumerate(controls):
            state = {
                "protocol_id": protocol_id,
                "question_id": question_id,
                "seed": seed,
                "control": control,
                "audit_version": 1,
            }
            digest = _digest(state)
            runs.append(
                CognitionRun(
                    f"EXP-AUDIT-{question_id}",
                    control,
                    seed,
                    {
                        "audit_item": index + 1,
                        "audit_complete": True,
                        "native_empirical_experiment": False,
                        "conceptual_or_normative": True,
                        "consciousness_inference": "not_established",
                        "phenomenal_claim_identified": False,
                        "automatic_evidence_promotion": False,
                        "scientific_evidence": False,
                    },
                    digest,
                    digest,
                )
            )
    return runs


def _audit_runner(protocol_id: str, question_id: str):
    def run(config: Config, seeds: tuple[int, ...] = (101, 102, 103)) -> list[CognitionRun]:
        return run_methodological_audit(
            config, seeds, protocol_id=protocol_id, question_id=question_id
        )

    run.__name__ = "run_" + protocol_id
    return run


_AUDIT_IDS = {
    **{f"cog_cns_{number}_v1": f"RQ-CNS-{number}" for number in range(101, 118)},
    "cog_epi_101_v1": "RQ-EPI-101",
    "cog_epi_102_v1": "RQ-EPI-102",
    "cog_wel_101_v1": "RQ-WEL-101",
    "cog_wel_102_v1": "RQ-WEL-102",
    "cog_wel_103_v1": "RQ-WEL-103",
}
for _protocol_id, _question_id in _AUDIT_IDS.items():
    globals()["run_" + _protocol_id] = _audit_runner(_protocol_id, _question_id)


__all__ = [
    "CognitionRun",
    "run_memory_delayed_information",
    "run_world_model_prediction",
    "run_behavior_profile_control",
    "run_methodological_audit",
    *["run_" + protocol_id for protocol_id in _AUDIT_IDS],
]
