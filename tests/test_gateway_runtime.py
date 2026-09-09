from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import pytest

from src.embodiment.gateway_runtime import (
    GatewayCondition,
    GatewayGuardError,
    GatewayLimits,
    GatewayRuntime,
    GatewayState,
)


def _preregistration() -> dict[str, Any]:
    return {
        "research_question": "RQ-GW-001",
        "hypothesis": "H-GW-001-A",
        "protocol_id": "gateway_controls_v1",
        "conditions": [
            {"id": "frozen"},
            {"id": "random"},
            {"id": "shuffle"},
            {"id": "plastic"},
        ],
        "seed_strategy": {"minimum_independent_seeds": 3, "seeds": [101, 102, 103]},
        "stopping_rule": {"ticks": 100},
        "inclusion_criteria": ["valid adapter"],
        "exclusion_criteria": ["invalid trace"],
        "primary_outcomes": ["task_accuracy"],
        "ai_authority_boundaries": {"promotion": False, "writes": False},
        "freeze": {
            "status": "FROZEN",
            "immutable_after_first_run": True,
            "human_review_required": True,
        },
    }


def _status(runtime: GatewayRuntime) -> dict[str, Any]:
    return cast(dict[str, Any], runtime.status())


def test_gateway_is_disabled_and_productive_activation_is_locked() -> None:
    runtime = GatewayRuntime()
    status = _status(runtime)
    assert runtime.state is GatewayState.DISABLED
    assert status["gateway_plasticity_allowed"] is False
    assert status["productive_gateway"] == {
        "available": False,
        "reason": "experimental_validation_incomplete",
    }


def test_controls_are_deterministic_and_plasticity_requires_frozen_contract() -> None:
    for condition in GatewayCondition:
        runtime = GatewayRuntime()
        if condition is GatewayCondition.PLASTIC:
            with pytest.raises(GatewayGuardError):
                runtime.activate(
                    condition,
                    experiment_id="EXP-GW-001",
                    seed=101,
                    experiment_mode=True,
                )
            runtime.activate(
                condition,
                experiment_id="EXP-GW-001",
                seed=101,
                preregistration=_preregistration(),
                experiment_mode=True,
            )
            assert runtime.state is GatewayState.ACTIVE_PLASTIC
        else:
            runtime.activate(
                condition,
                experiment_id="EXP-GW-001",
                seed=101,
                experiment_mode=True,
            )
            assert runtime.state.value == f"active_{condition.value}"

    first = GatewayRuntime()
    second = GatewayRuntime()
    first.activate("random", experiment_id="EXP-GW-001", seed=42, experiment_mode=True)
    second.activate("random", experiment_id="EXP-GW-001", seed=42, experiment_mode=True)
    assert first.status()["topology"] == second.status()["topology"]


def test_pause_resume_checkpoint_is_deterministic() -> None:
    first = GatewayRuntime()
    first.activate(
        "plastic",
        experiment_id="EXP-GW-002",
        seed=101,
        preregistration=_preregistration(),
        experiment_mode=True,
    )
    first.step([1.0, 0.0], [0.0, 1.0], reward=0.25)
    first.pause()
    checkpoint = first.checkpoint()
    first.resume()

    second = GatewayRuntime()
    second.restore(checkpoint)
    second.resume()
    assert first.step([1.0, 0.5], [0.25, 1.0], reward=-0.1) == second.step(
        [1.0, 0.5], [0.25, 1.0], reward=-0.1
    )


def test_structural_journal_is_bounded_and_limits_throttle() -> None:
    runtime = GatewayRuntime(
        limits=GatewayLimits(max_events_per_tick=1, max_queue_depth=1),
        journal_capacity=2,
    )
    runtime.activate("frozen", experiment_id="EXP-GW-003", seed=7, experiment_mode=True)
    runtime.pause()
    runtime.resume()
    runtime.stop()
    status = _status(runtime)
    assert len(status["journal"]) == 2
    runtime.activate("frozen", experiment_id="EXP-GW-003", seed=7, experiment_mode=True)
    status = cast(dict[str, Any], runtime.step([1.0, 1.0], [1.0, 1.0], queue_depth=2))
    assert status["metrics"]["dropped_events"] > 0
    assert status["metrics"]["throttled_ticks"] > 0


def test_gateway_checkpoint_persists_and_restores(tmp_path: Path) -> None:
    path = tmp_path / "gateway.json"
    runtime = GatewayRuntime()
    runtime.activate(
        "random", experiment_id="EXP-GW-004", seed=42, experiment_mode=True
    )
    runtime.persist(path)
    restored = GatewayRuntime.load(path)
    assert restored.status() == runtime.status()
