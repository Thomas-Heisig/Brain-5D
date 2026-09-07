"""Instrument and governance tests; no empirical consciousness experiments."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from src.research.cognition_governance import (
    CognitionGovernanceError,
    assess_candidate,
    cognition_catalog,
    guard_cognition_launch,
    guard_cognition_promotion,
)
from src.research.cognition_metrics import (
    SignalContract,
    accuracy_by_delay,
    compare_evoked,
    confidence_scores,
    dmts_trials,
    oddball_schedule,
    paired_effect,
    signal_detection,
)
from src.research.registry import ResearchRegistry

ROOT = Path(__file__).resolve().parents[1]


def test_dmts_balances_each_sample_and_delay() -> None:
    trials, key = dmts_trials(17)
    assert len(trials) == 192
    for delay in (0, 10, 100):
        for sample in range(4):
            selected = [
                t for t in trials if t.sample == sample and t.delay_ticks == delay
            ]
            assert sum(key[t.trial_id] for t in selected) == 8
            assert len(selected) == 16


def test_generators_reproduce_and_vary() -> None:
    assert dmts_trials(17) == dmts_trials(17)
    assert dmts_trials(17) != dmts_trials(18)
    assert oddball_schedule(17) == oddball_schedule(17)
    assert oddball_schedule(17) != oddball_schedule(18)


def test_dmts_omissions_and_constant_baseline() -> None:
    trials, key = dmts_trials(17)
    assert all(v["accuracy"] == 1 for v in accuracy_by_delay(trials, key, key).values())
    assert all(v["accuracy"] == 0 for v in accuracy_by_delay(trials, key, {}).values())
    constant = {t.trial_id: 1 for t in trials}
    assert all(
        v["accuracy"] == 0.5 for v in accuracy_by_delay(trials, key, constant).values()
    )


@pytest.mark.parametrize("delays", [(), (0, 0), (-1,), (True,)])
def test_invalid_delays_rejected(delays: tuple[int, ...]) -> None:
    with pytest.raises(ValueError):
        dmts_trials(1, delays=delays)


def test_incomplete_key_rejected() -> None:
    trials, key = dmts_trials(1)
    key.pop(0)
    with pytest.raises(ValueError):
        accuracy_by_delay(trials, key, {})


def test_oddball_counts_and_identity_reversal() -> None:
    sequence, flags = oddball_schedule(9)
    reversed_sequence, reversed_flags = oddball_schedule(9, standard=1, deviant=0)
    assert len(sequence) == 200 and sum(flags) == 40
    assert flags == reversed_flags
    assert all(a != b for a, b in zip(sequence, reversed_sequence))


@pytest.mark.parametrize("deviants", [0, 200, -1, True])
def test_invalid_oddball_rejected(deviants: int) -> None:
    with pytest.raises(ValueError):
        oddball_schedule(1, deviants=deviants)


def test_signal_detection_known_cases() -> None:
    assert signal_detection(5, 5, 5, 5)["d_prime"] == 0
    assert signal_detection(10, 0, 0, 10)["d_prime"] > 0
    with pytest.raises(ValueError):
        signal_detection(0, 0, 1, 2)


def test_confidence_ties_single_class_and_oracle_fixture() -> None:
    assert confidence_scores([0, 1], [0, 1])["brier"] == 0
    tied = confidence_scores([0, 1], [0.5, 0.5])
    assert tied["brier"] == 0.25 and tied["type2_auroc"] == 0.5
    assert confidence_scores([1, 1], [0.8, 0.9])["type2_auroc"] is None
    assert tied["meta_d_prime"] is None


@pytest.mark.parametrize("values", [[float("nan")], [1.1], [-0.1]])
def test_bad_confidence_rejected(values: list[float]) -> None:
    with pytest.raises(ValueError):
        confidence_scores([1], values)


def test_paired_effect_not_inference() -> None:
    result = paired_effect([1, 2], [3, 4])
    assert result["mean_difference"] == 2 and result["standard_error"] == 0
    assert paired_effect([1], [2])["standard_error"] is None
    assert "p_value" not in result


def test_eeg_contract_and_descriptive_values() -> None:
    measured = SignalContract("measured_eeg", "uV", 1000, "dataset/montage", "frozen")
    predicted = replace(
        measured, kind="forward_model_eeg", observation_model="forward-v1"
    )
    result = compare_evoked(
        [1, 3, 2], [1, 3, 2], reference_contract=measured, candidate_contract=predicted
    )
    assert result["rmse"] == 0 and result["correlation"] == 1
    assert "not_equivalence" in str(result["interpretation"])
    for invalid in (
        replace(predicted, kind="spike_sum"),
        replace(predicted, kind="lfp_proxy"),
        replace(predicted, units="V"),
        replace(predicted, sampling_hz=500),
    ):
        with pytest.raises(ValueError):
            compare_evoked(
                [1, 3, 2],
                [1, 3, 2],
                reference_contract=measured,
                candidate_contract=invalid,
            )


@pytest.mark.parametrize(
    "question,protocol",
    [
        ("RQ-CNS-105", "runtime_ticks_v1"),
        ("RQ-CNS-102", "science_all_v1"),
        ("RQ-WEL-101", "science_suite_v1"),
        ("RQ-EPI-101", "runtime_ticks_v1"),
        ("RQ-SNN-001", "cog_cns_105_v1"),
    ],
)
def test_no_generic_fallback(tmp_path: Path, question: str, protocol: str) -> None:
    with pytest.raises(CognitionGovernanceError, match="ADAPTER_NOT_VALIDATED"):
        guard_cognition_launch(tmp_path, question, protocol)


@pytest.mark.parametrize("state", ["HOLD", "REVIEW_REQUIRED", "unknown"])
def test_hold_blocks_legacy_new_launch(tmp_path: Path, state: str) -> None:
    folder = tmp_path / "ethics"
    folder.mkdir()
    (folder / "operational_state.json").write_text(
        json.dumps({"state": state}), encoding="utf-8"
    )
    with pytest.raises(CognitionGovernanceError):
        guard_cognition_launch(tmp_path, "RQ-SNN-001", "runtime_ticks_v1")


def test_legacy_without_program_still_available(tmp_path: Path) -> None:
    guard_cognition_launch(tmp_path, "RQ-SNN-001", "runtime_ticks_v1")


def test_promotion_guard() -> None:
    with pytest.raises(CognitionGovernanceError):
        guard_cognition_promotion("H-CNS-105-A", "CLAIM-CNS-105")
    guard_cognition_promotion("H-SNN-001-A", "CLAIM-SNN-001")


def complete_candidate() -> dict[str, object]:
    """Constructed metadata, never real raw-data or review verification."""
    review: dict[str, object] = {
        "status": "PENDING",
        "reviewer": None,
        "artifact": None,
        "independence": "not established",
        "authentication": "not performed",
    }
    return {
        "schema_version": "1.0",
        "candidate_id": "CAND-CNS-FIXTURE",
        "protocol_id": "cog_cns_105_v1",
        "question_id": "RQ-CNS-105",
        "hypothesis_id": "H-CNS-105-A",
        "source_commit": "0" * 40,
        "analysis_hash": "0" * 64,
        "raw_artifacts": [
            {"path": "fixture.json", "sha256": "0" * 64, "role": "primary_observation"}
        ],
        "claim_scope": "functional_or_theory_conditional",
        "consciousness_verdict": "not_established",
        "limitations": ["constructed"],
        "alternatives": ["null model"],
        "theory_assumptions": ["none about phenomenal experience"],
        "measurement_validity": {
            "observation_model": "fixture",
            "units": "dimensionless",
            "holdout": "not a native study",
            "independent_unit": "fixture",
            "uncertainty": "not empirical",
            "controls": ["negative fixture"],
        },
        "replication": dict(review),
        "human_review": dict(review),
        "ethics_review": dict(review),
    }


def test_candidate_never_accepts_or_authenticates() -> None:
    assert assess_candidate({})["status"] == "INCOMPLETE"
    candidate = complete_candidate()
    result = assess_candidate(candidate)
    assert result["status"] == "READY_FOR_EXTERNAL_REVIEW"
    assert result["accepted_evidence"] is False
    assert result["reviewer_identity_authenticated"] is False
    assert result["raw_artifact_bytes_verified"] is False
    candidate["consciousness_verdict"] = "conscious"
    assert assess_candidate(candidate)["status"] == "INCOMPLETE"


@pytest.mark.parametrize(
    "field",
    [
        "source_commit",
        "raw_artifacts",
        "measurement_validity",
        "human_review",
        "limitations",
    ],
)
def test_candidate_malformed_field_cannot_pass(field: str) -> None:
    candidate = complete_candidate()
    candidate[field] = "fake-approval"
    assert assess_candidate(candidate)["status"] == "INCOMPLETE"


def test_candidate_cannot_self_accept() -> None:
    candidate = complete_candidate()
    candidate["accepted_evidence"] = True
    assert assess_candidate(candidate)["status"] == "INCOMPLETE"
    candidate = complete_candidate()
    candidate["hypothesis_id"] = "H-CNS-106-A"
    assert assess_candidate(candidate)["status"] == "INCOMPLETE"


def test_missing_installed_ethics_state_fails_closed(tmp_path: Path) -> None:
    program = tmp_path / "protocols/COGNITION_CONSCIOUSNESS_V1.json"
    program.parent.mkdir()
    program.write_text("{}", encoding="utf-8")
    with pytest.raises(CognitionGovernanceError, match="state missing"):
        guard_cognition_launch(tmp_path, "RQ-SNN-001", "runtime_ticks_v1")


def test_malformed_ethics_state_fails_closed(tmp_path: Path) -> None:
    state = tmp_path / "ethics/operational_state.json"
    state.parent.mkdir()
    state.write_text('{"state": []}', encoding="utf-8")
    with pytest.raises(CognitionGovernanceError):
        guard_cognition_launch(tmp_path, "RQ-SNN-001", "runtime_ticks_v1")


def test_instrument_resource_budgets() -> None:
    with pytest.raises(ValueError, match="budget"):
        dmts_trials(1, repeats=100001)
    with pytest.raises(ValueError, match="budget"):
        oddball_schedule(1, trials=100001)


def test_auc_matches_pairwise_reference_with_ties() -> None:
    labels = [0, 1, 0, 1, 1, 0]
    probabilities = [0.2, 0.7, 0.7, 0.5, 0.7, 0.1]
    positive = [p for p, y in zip(probabilities, labels) if y]
    negative = [p for p, y in zip(probabilities, labels) if not y]
    expected = sum((p > n) + 0.5 * (p == n) for p in positive for n in negative) / (
        len(positive) * len(negative)
    )
    assert confidence_scores(labels, probabilities)["type2_auroc"] == expected


def test_registry_program_links_and_sources() -> None:
    registry = ResearchRegistry(ROOT / "research" / "registry").load_all()
    catalogue = cognition_catalog(ROOT / "research")
    assert len(catalogue) == 22
    assert not registry.link_issues()
    for entry in catalogue:
        question = registry.questions[entry["research_question"]]
        hypothesis = registry.hypotheses[entry["hypothesis"]]
        assert question.status == "open" and hypothesis.status == "untested"
        assert not question.evidence and not hypothesis.evidence
        assert entry["native_adapter_validated"] is False
        assert entry["consciousness_inference"] == "not_established"
        assert all(source in registry.sources for source in question.literature)


def test_dashboard_boundary_and_visible_catalog() -> None:
    from src.dashboard.experiment_workflow import (
        ExperimentWorkflowService,
        WorkflowValidationError,
    )

    service = ExperimentWorkflowService(ROOT / "research")
    catalogue = service.catalog()
    assert "cognition_protocols" in catalogue
    body: dict[str, object] = {
        "experiment_id": "EXP-CNS-TEST",
        "question_id": "RQ-CNS-105",
        "hypothesis_id": "H-CNS-105-A",
        "protocol": "runtime_ticks_v1",
        "ticks": 1,
        "title": "test",
        "conditions": "test",
        "exploratory": True,
        "ethics_approved": True,
    }
    with pytest.raises(WorkflowValidationError, match="ADAPTER_NOT_VALIDATED"):
        service.run_science(body)


@pytest.mark.parametrize(
    "entrypoint", ["evaluate_experiment", "promote_validated_experiment"]
)
def test_evidence_entrypoints_block_before_any_write(entrypoint: str) -> None:
    from src.research.evidence_engine import EvidenceEngine

    engine = EvidenceEngine(ResearchRegistry(ROOT / "research" / "registry").load_all())
    method = getattr(engine, entrypoint)
    with pytest.raises(CognitionGovernanceError, match="REVIEW_REQUIRED"):
        method(
            "EXP-NOT-CREATED", "CLAIM-CNS-105", "H-CNS-105-A", "fixture is not evidence"
        )
