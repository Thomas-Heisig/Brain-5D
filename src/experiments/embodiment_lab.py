"""Protocol runner for the deterministic EXP-EMB-0001 boundary experiment."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, cast

from src.embodiment import (
    ActionCommand,
    ActuatorResult,
    ConnectionDescriptor,
    ConnectionKind,
    ConnectionStatus,
    ControlledEmbodimentAgent,
    DeterministicTargetEnvironment,
    RelationshipClass,
    SystemSensorAdapter,
)
from src.experience import ExperienceEngine
from src.research.experiment_recorder import ExperimentRecorder


@dataclass
class _ProtocolNetwork:
    """Deterministic network boundary used by the registered protocol."""

    injected: list[dict[int, float]] = field(default_factory=list)
    steps: int = 0

    def inject_current_batch(self, currents: dict[int, float]) -> None:
        self.injected.append(currents)

    def step(self) -> dict[str, tuple[int, ...]]:
        self.steps += 1
        return {"output_spike_ids": (1,)}


@dataclass
class _RewardRecorder:
    rewards: list[tuple[float, int]] = field(default_factory=list)

    def set_reward(self, value: float, tick: int) -> None:
        self.rewards.append((value, tick))


@dataclass(frozen=True)
class ProtocolRun:
    run_id: str
    condition: str
    repetition: int
    frames: tuple[dict[str, Any], ...]
    rewards: tuple[tuple[float, int], ...]
    target_reached: bool
    environment_reward_received: float
    action_audit_valid: bool
    action_count: int
    network_steps: int
    runtime_error: str | None
    action_acceptance_receipts: tuple[dict[str, Any], ...]
    observed_effect_receipts: tuple[dict[str, Any], ...]


def _agent(
    authorized: bool, actuator_failure: bool = False
) -> ControlledEmbodimentAgent:
    descriptor = ConnectionDescriptor(
        connection_id="target-actuator",
        name="Deterministic target actuator",
        kind=ConnectionKind.ACTUATOR,
        relationship=RelationshipClass.CONTROLLABLE,
        status=ConnectionStatus.CONNECTED,
        capabilities=("right",),
        available=True,
        authorized=authorized,
        active=True,
    )

    class Actuator:
        actuator_id = "target-actuator"
        active = True

        def apply(self, command: ActionCommand) -> ActuatorResult:
            if actuator_failure:
                return ActuatorResult(False, "simulated actuator failure")
            return ActuatorResult(True, command.action)

    agent = ControlledEmbodimentAgent(
        DeterministicTargetEnvironment(), Actuator(), descriptor
    )
    agent.reset(seed=42)
    return agent


def _run_condition(run_id: str, condition: str, repetition: int) -> ProtocolRun:
    authorized = condition == "authorized"
    sensor = SystemSensorAdapter(lambda tick: {"signal": tick})
    if condition == "sensor_loss":
        sensor._active = False
    network = _ProtocolNetwork()
    learning = _RewardRecorder()
    engine = ExperienceEngine(
        sensor=sensor,
        network=network,
        encoder=lambda frame: {0: float(cast(dict[str, int], frame.payload)["signal"])},
        decoder=lambda result, frame: ActionCommand(
            "target-actuator", frame.tick, "right"
        ),
        embodiment=_agent(authorized, actuator_failure=condition == "actuator_failure"),
        learning=cast(Any, learning),
    )

    frames: list[dict[str, Any]] = []
    action_acceptance_receipts: list[dict[str, Any]] = []
    observed_effect_receipts: list[dict[str, Any]] = []
    try:
        engine.reset(seed=42)
        for tick in range(1, 4):
            record = engine.step(tick)
            frames.append({"tick": record.frame.tick, "payload": record.frame.payload})
            receipt = engine.embodiment.last_receipt
            if receipt is None:
                raise RuntimeError("embodiment did not produce an action receipt")
            action_acceptance_receipts.append(
                {
                    "command_id": receipt.command_id,
                    "accepted": receipt.accepted,
                    "error": receipt.error,
                }
            )
            observed_effect_receipts.append(
                {
                    "command_id": receipt.command_id,
                    "completed": receipt.completed,
                    "effect_observed": receipt.effect_observed,
                    "latency": receipt.latency,
                }
            )
        observation = engine.last_step.observation if engine.last_step else None
        return ProtocolRun(
            run_id=run_id,
            condition=condition,
            repetition=repetition,
            frames=tuple(frames),
            rewards=tuple(learning.rewards),
            target_reached=observation is not None and observation.terminated,
            environment_reward_received=sum(value for value, _ in learning.rewards),
            action_audit_valid=engine.embodiment.audit.verify(),
            action_count=len(engine.embodiment.audit.records),
            network_steps=network.steps,
            runtime_error=None,
            action_acceptance_receipts=tuple(action_acceptance_receipts),
            observed_effect_receipts=tuple(observed_effect_receipts),
        )
    except Exception as error:  # pragma: no cover - protocol records failures as data
        return ProtocolRun(
            run_id=run_id,
            condition=condition,
            repetition=repetition,
            frames=tuple(frames),
            rewards=tuple(learning.rewards),
            target_reached=False,
            environment_reward_received=0.0,
            action_audit_valid=False,
            action_count=len(engine.embodiment.audit.records),
            network_steps=network.steps,
            runtime_error=f"{type(error).__name__}: {error}",
            action_acceptance_receipts=tuple(action_acceptance_receipts),
            observed_effect_receipts=tuple(observed_effect_receipts),
        )


def run_protocol(
    output_dir: Path,
    *,
    independent_runs: int = 20,
    repetitions_per_condition: int = 3,
) -> dict[str, Any]:
    """Execute all registered conditions and write DATA artifacts."""
    conditions = (
        "authorized",
        "unauthorized",
        "actuator_failure",
        "sensor_loss",
        "sensor_reproducibility",
    )
    runs: list[ProtocolRun] = []
    for independent in range(independent_runs):
        for repetition in range(repetitions_per_condition):
            for condition in conditions:
                run_id = f"EMB-{independent + 1:03d}-{repetition + 1:02d}-{condition}"
                runs.append(_run_condition(run_id, condition, repetition + 1))

    output_dir.mkdir(parents=True, exist_ok=True)
    data_path = output_dir / "DATA" / "runs.jsonl"
    data_path.parent.mkdir(parents=True, exist_ok=True)
    with data_path.open("w", encoding="utf-8") as handle:
        for run in runs:
            handle.write(json.dumps(asdict(run), ensure_ascii=False) + "\n")

    by_condition: dict[str, list[ProtocolRun]] = {
        condition: [run for run in runs if run.condition == condition]
        for condition in conditions
    }
    analysis = {
        "experiment_id": "EXP-EMB-0001",
        "status": "completed",
        "run_count": len(runs),
        "conditions": {
            condition: {
                "runs": len(condition_runs),
                "target_reached_rate": sum(run.target_reached for run in condition_runs)
                / len(condition_runs),
                "total_reward": sum(
                    run.environment_reward_received for run in condition_runs
                ),
                "all_audits_valid": all(
                    run.action_audit_valid for run in condition_runs
                ),
                "all_one_tick_hooks": all(
                    run.network_steps == 3 for run in condition_runs
                ),
                "runtime_errors": sum(
                    run.runtime_error is not None for run in condition_runs
                ),
                "accepted_action_count": sum(
                    receipt["accepted"]
                    for run in condition_runs
                    for receipt in run.action_acceptance_receipts
                ),
                "observed_effect_count": sum(
                    receipt["effect_observed"] is True
                    for run in condition_runs
                    for receipt in run.observed_effect_receipts
                ),
                "acceptance_receipts_complete": all(
                    len(run.action_acceptance_receipts) == 3 for run in condition_runs
                ),
                "effect_receipts_complete": all(
                    len(run.observed_effect_receipts) == 3 for run in condition_runs
                ),
            }
            for condition, condition_runs in by_condition.items()
        },
        "sensor_frames_reproducible": all(
            run.frames == by_condition["sensor_reproducibility"][0].frames
            for run in by_condition["sensor_reproducibility"]
        ),
        "evidence_eligible": False,
        "evidence_reason": "DATA run only; EVID requires clean source freeze and review",
    }
    analysis_path = output_dir / "DATA" / "analysis.json"
    analysis_path.write_text(json.dumps(analysis, indent=2), encoding="utf-8")

    recorder = ExperimentRecorder("EXP-EMB-0001", output_dir=output_dir)
    recorder.record_research_links(
        research_questions=["RQ-EMB-001"], hypotheses=["H-EMB-001-A"]
    )
    recorder.record_simulation_params(
        independent_runs=independent_runs,
        repetitions_per_condition=repetitions_per_condition,
        conditions=list(conditions),
    )
    recorder.record_artifact("data", str(data_path.relative_to(output_dir)))
    recorder.record_artifact("analysis", str(analysis_path.relative_to(output_dir)))
    recorder.record_results(**analysis)
    recorder.mark_completed().save()

    report = output_dir / "report.md"
    report.write_text(
        "# EXP-EMB-0001 Report\n\n"
        "The registered deterministic conditions were executed and stored as DATA. "
        "No EVID artifact was created because the evidence policy requires a clean "
        "source freeze and independent reviewed runs.\n",
        encoding="utf-8",
    )
    return analysis


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="research/experiments/EXP-EMB-0001")
    parser.add_argument("--independent-runs", type=int, default=20)
    parser.add_argument("--repetitions-per-condition", type=int, default=3)
    args = parser.parse_args()
    analysis = run_protocol(
        Path(args.output_dir),
        independent_runs=args.independent_runs,
        repetitions_per_condition=args.repetitions_per_condition,
    )
    print(json.dumps(analysis, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
