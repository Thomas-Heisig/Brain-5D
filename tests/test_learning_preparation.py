from __future__ import annotations

import pytest

from src.learning import (
    LearningDataPartition,
    LearningObjective,
    LearningPlanOrigin,
    LearningPreparationGuard,
    LearningPreparationService,
    LearningSourceRef,
)


def _objective() -> LearningObjective:
    return LearningObjective(
        objective_id="OBJ-001",
        description="Discriminate two environment outcomes after controlled exposure.",
        success_metric="held-out task success",
        evaluation_question="Does performance improve over the pre-learning baseline?",
    )


def _source() -> LearningSourceRef:
    return LearningSourceRef(
        source_id="SRC-001",
        digest="abc123",
        origin="deterministic_environment",
        partition=LearningDataPartition.TRAIN,
        trust="CONTROLLED",
    )


def test_human_preparation_plan_is_non_executable_and_digest_bound() -> None:
    service = LearningPreparationService()
    proposal = service.create_proposal(
        plan_id="LP-001",
        objective=_objective(),
        sources=[_source()],
        baseline_protocol="Run a pre-learning behavior and impulse-response baseline.",
        exposure_protocol="Expose the system to the registered environment episodes.",
        evaluation_protocol="Repeat the same held-out evaluation after learning.",
        stopping_rule="Stop after the preregistered episode count.",
        controls=["learning_off", "same_seed"],
    )

    assert proposal.origin is LearningPlanOrigin.HUMAN
    assert proposal.authority == "proposal_only"
    assert proposal.to_dict()["executed"] is False
    assert len(proposal.digest) == 64

    approved = service.approve(proposal, approved_by="operator")
    assert approved.to_dict()["runtime_authority"] == "none"
    assert approved.to_dict()["executed"] is False
    assert len(approved.digest) == 64


def test_ai_preparation_requires_provenance_and_remains_proposal_only() -> None:
    service = LearningPreparationService()

    with pytest.raises(ValueError, match="ai_interaction_id"):
        service.create_proposal(
            plan_id="LP-AI-001",
            objective=_objective(),
            sources=[_source()],
            baseline_protocol="Measure the baseline first.",
            exposure_protocol="Prepare a sequence of controlled environment episodes.",
            evaluation_protocol="Evaluate on an isolated holdout partition.",
            stopping_rule="Use the preregistered stopping rule.",
            origin=LearningPlanOrigin.AI_ASSISTED,
        )

    proposal = service.create_proposal(
        plan_id="LP-AI-002",
        objective=_objective(),
        sources=[_source()],
        baseline_protocol="Measure the baseline first.",
        exposure_protocol="Prepare a sequence of controlled environment episodes.",
        evaluation_protocol="Evaluate on an isolated holdout partition.",
        stopping_rule="Use the preregistered stopping rule.",
        origin=LearningPlanOrigin.AI_ASSISTED,
        ai_interaction_id="AI-INTERACTION-001",
    )

    assert proposal.authority == "proposal_only"
    assert proposal.ai_interaction_id == "AI-INTERACTION-001"
    assert proposal.to_dict()["executed"] is False


@pytest.mark.parametrize(
    "payload",
    [
        {"weights": [0.1, 0.2]},
        {"training": {"spike_pattern": [1, 0, 1]}},
        {"training": {"injected_current": 4.2}},
        {"evaluation": [{"reward_value": 1.0}]},
        {"nested": {"plasticity_update": {"synapse_weight": 0.9}}},
    ],
)
def test_guard_rejects_direct_neural_or_reward_writes(payload: dict[str, object]) -> None:
    with pytest.raises(PermissionError):
        LearningPreparationGuard.validate_mapping(payload)


def test_guard_allows_protocol_metadata_and_provenance() -> None:
    LearningPreparationGuard.validate_mapping(
        {
            "objective": "learn a causal relation",
            "baseline": "pre-learning probe",
            "source": {"digest": "abc", "partition": "train"},
            "protocol": {"episodes": 50, "holdout": True},
            "evaluation": {"metric": "task_success", "repeat": 10},
        }
    )
