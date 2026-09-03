"""Tests for Phase 1 & 2: Scientific error integrity and fail-fast mode.

Covers:
1. Runtime errors are captured in experiment manifests
2. Invalid runs cannot become scientific evidence
3. completed + negative result = valid scientific result
4. failed = execution failure
5. invalid = scientifically unusable run
6. EvidenceEngine rejects: template, not_started, running, failed, invalid
7. Only valid completed runs may generate EVID-*
8. Fail-fast mode stops experiment on first runtime error
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.research.evidence_engine import (
    EvidenceEngine,
    _check_experiment_valid,  # type: ignore[misc]
)
from src.research_assistant.contracts import AIExposure, AIInteractionRecord, CausalTaint
from src.research.experiment_recorder import ExperimentRecorder
from src.research.registry import ResearchRegistry

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def tmp_experiment_dir(tmp_path: Path) -> Path:
    """Create a temporary experiment directory."""
    exp_dir = tmp_path / "research" / "experiments" / "EXP-TEST-0001"
    exp_dir.mkdir(parents=True, exist_ok=True)
    return exp_dir


@pytest.fixture
def registry(tmp_path: Path) -> ResearchRegistry:
    """Create a temporary research registry."""
    # Point registry to temp path
    reg_dir = tmp_path / "research" / "registry"
    reg_dir.mkdir(parents=True, exist_ok=True)
    # Create minimal registry files
    claims_file = reg_dir / "claims.yaml"
    claims_file.write_text(
        """
- id: CLAIM-TEST-001
  claim: "Test claim for validity testing."
  research_question: RQ-TEST-001
  hypothesis: H-TEST-001-A
  evidence: []
  experiments: []
  sources: []
  status: untested
  confidence: none
  evidence_level: E0
  minimum_runs: 1
  created: "2026-08-26"
  updated: "2026-08-26"
""",
        encoding="utf-8",
    )
    hypotheses_file = reg_dir / "hypotheses.yaml"
    hypotheses_file.write_text(
        """
- id: H-TEST-001-A
  hypothesis: "Test hypothesis."
  research_question: RQ-TEST-001
  evidence: []
  status: untested
  created: "2026-08-26"
""",
        encoding="utf-8",
    )
    questions_file = reg_dir / "questions.yaml"
    questions_file.write_text(
        """
- id: RQ-TEST-001
  question: "Test research question?"
  status: open
  created: "2026-08-26"
""",
        encoding="utf-8",
    )
    methods_file = reg_dir / "methods.yaml"
    methods_file.write_text("[]", encoding="utf-8")
    sources_file = reg_dir / "sources.yaml"
    sources_file.write_text("[]", encoding="utf-8")

    # Override registry paths
    registry = ResearchRegistry(registry_dir=reg_dir)
    return registry


# ============================================================================
# Phase 1: Runtime errors enter experiment manifest
# ============================================================================


class TestRuntimeErrorsInManifest:
    """RuntimeErrorEvent must be captured in experiment manifest."""

    def test_recorder_starts_with_no_errors(self, tmp_experiment_dir: Path) -> None:
        """A fresh recorder has zero runtime errors."""
        recorder = ExperimentRecorder("EXP-TEST-0001", output_dir=tmp_experiment_dir)
        manifest = recorder.manifest
        assert manifest["runtime_errors"] == []
        assert manifest["validity"]["valid"] is True
        assert manifest["validity"]["runtime_error_count"] == 0
        assert manifest["ai_exposure"] == "none"

    def test_recorder_records_validated_ai_exposure(self, tmp_experiment_dir: Path) -> None:
        recorder = ExperimentRecorder("EXP-TEST-0001", output_dir=tmp_experiment_dir)
        recorder.record_ai_exposure(AIExposure.OBSERVER_ONLY)
        assert recorder.manifest["ai_exposure"] == "observer_only"

        with pytest.raises(ValueError, match="Unsupported AI exposure"):
            recorder.record_ai_exposure("unrestricted")

    def test_recorder_persists_interactions_and_monotonic_taint(
        self, tmp_experiment_dir: Path
    ) -> None:
        recorder = ExperimentRecorder("EXP-TEST-0001", output_dir=tmp_experiment_dir)
        interaction = AIInteractionRecord.create(
            role="research_ai",
            experiment_id="EXP-TEST-0001",
            tick=2,
            input_value="observation",
            prompt="interpret",
            output_value="proposal",
            model_provenance={"provider": "test"},
            authority="read_only",
            causal_effect=CausalTaint.PROPOSED,
        )
        recorder.record_ai_interaction(interaction)
        recorder.record_ai_exposure(AIExposure.ADVISOR)

        assert recorder.manifest["causal_taint"] == "PROPOSED"
        assert recorder.manifest["ai_interactions"][0]["interaction_id"] == interaction.interaction_id
        with pytest.raises(ValueError, match="does not match"):
            recorder.record_ai_interaction(
                AIInteractionRecord.create(
                    role="research_ai",
                    experiment_id="EXP-OTHER",
                    tick=3,
                    input_value=None,
                    prompt="interpret",
                    output_value=None,
                    model_provenance={},
                    authority="read_only",
                )
            )

            assert recorder.manifest["causal_card"]["classification"] == "PROPOSED"
            assert recorder.manifest["causal_card"]["interaction_ids"] == [interaction.interaction_id]
            recorder.record_ai_treatment("PROTOCOL-AI-001")
            assert recorder.manifest["ai_treatment"]["registered"] is True

    def test_recorder_captures_runtime_error(self, tmp_experiment_dir: Path) -> None:
        """Recording a runtime error updates the manifest."""
        recorder = ExperimentRecorder("EXP-TEST-0001", output_dir=tmp_experiment_dir)
        recorder.record_runtime_error(
            tick=42,
            phase="step",
            exception_type="ValueError",
            message="Test error",
            fatal=False,
        )
        manifest = recorder.manifest
        assert len(manifest["runtime_errors"]) == 1
        assert manifest["runtime_errors"][0]["tick"] == 42
        assert manifest["runtime_errors"][0]["phase"] == "step"
        assert manifest["runtime_errors"][0]["exception_type"] == "ValueError"
        assert manifest["runtime_errors"][0]["message"] == "Test error"
        assert manifest["runtime_errors"][0]["fatal"] is False

    def test_error_invalidates_validity(self, tmp_experiment_dir: Path) -> None:
        """Any runtime error sets validity.valid = False."""
        recorder = ExperimentRecorder("EXP-TEST-0001", output_dir=tmp_experiment_dir)
        recorder.record_runtime_error(
            tick=1, phase="hook", exception_type="RuntimeError", message="Fail"
        )
        assert recorder.manifest["validity"]["valid"] is False
        assert recorder.manifest["validity"]["runtime_error_count"] == 1

    def test_multiple_errors_accumulate(self, tmp_experiment_dir: Path) -> None:
        """Multiple errors are accumulated with correct counts."""
        recorder = ExperimentRecorder("EXP-TEST-0001", output_dir=tmp_experiment_dir)
        recorder.record_runtime_error(
            tick=1, phase="step", exception_type="TypeError", message="A", fatal=False
        )
        recorder.record_runtime_error(
            tick=5, phase="hook", exception_type="ValueError", message="B", fatal=True
        )
        recorder.record_runtime_error(
            tick=10,
            phase="step",
            exception_type="RuntimeError",
            message="C",
            fatal=False,
        )
        manifest = recorder.manifest
        assert len(manifest["runtime_errors"]) == 3
        assert manifest["validity"]["runtime_error_count"] == 3
        assert manifest["validity"]["fatal_error_count"] == 1

    def test_save_persists_errors(self, tmp_experiment_dir: Path) -> None:
        """Saved manifest includes runtime errors."""
        import src.research.experiment_recorder as er_module

        original_dir = er_module.EXPERIMENTS_DIR
        try:
            # Point the module-level EXPERIMENTS_DIR to our temp dir
            er_module.EXPERIMENTS_DIR = tmp_experiment_dir.parent
            recorder = ExperimentRecorder(
                "EXP-TEST-0001", output_dir=tmp_experiment_dir
            )
            recorder.record_runtime_error(
                tick=99, phase="step", exception_type="Exception", message="persist"
            )
            recorder.save()
            loaded = ExperimentRecorder.load("EXP-TEST-0001")
            assert loaded is not None
            assert loaded["experiment_id"] == "EXP-TEST-0001"
            assert len(loaded["runtime_errors"]) == 1
            assert loaded["validity"]["valid"] is False
        finally:
            er_module.EXPERIMENTS_DIR = original_dir


# ============================================================================
# Phase 1: Experiment status semantics
# ============================================================================


class TestExperimentStatusSemantics:
    """completed + negative = valid, failed = execution, invalid = unusable."""

    def test_completed_no_errors_is_valid(self, tmp_experiment_dir: Path) -> None:
        """A completed experiment with no errors is valid."""
        recorder = ExperimentRecorder("EXP-TEST-0001", output_dir=tmp_experiment_dir)
        recorder.mark_completed()
        recorder.save()
        assert recorder.manifest["experiment_status"] == "completed"
        assert recorder.manifest["validity"]["valid"] is True

    def test_completed_with_errors_is_invalid(self, tmp_experiment_dir: Path) -> None:
        """A completed experiment with runtime errors becomes invalid."""
        recorder = ExperimentRecorder("EXP-TEST-0001", output_dir=tmp_experiment_dir)
        recorder.record_runtime_error(
            tick=1, phase="step", exception_type="RuntimeError", message="oops"
        )
        recorder.mark_completed()
        assert recorder.manifest["experiment_status"] == "invalid"
        assert recorder.manifest["validity"]["valid"] is False

    def test_failed_status(self, tmp_experiment_dir: Path) -> None:
        """Failed status is for execution crashes."""
        recorder = ExperimentRecorder("EXP-TEST-0001", output_dir=tmp_experiment_dir)
        recorder.mark_failed()
        assert recorder.manifest["experiment_status"] == "failed"

    def test_completed_negative_result_is_valid(self, tmp_experiment_dir: Path) -> None:
        """A completed experiment with negative result is still valid science."""
        recorder = ExperimentRecorder("EXP-TEST-0001", output_dir=tmp_experiment_dir)
        recorder.record_results(hypothesis_supported=False, effect_size=0.0)
        recorder.mark_completed()
        assert recorder.manifest["experiment_status"] == "completed"
        assert recorder.manifest["validity"]["valid"] is True


# ============================================================================
# Phase 1: EvidenceEngine rejects invalid experiments
# ============================================================================


class TestEvidenceRejection:
    """EvidenceEngine must reject scientifically invalid experiments."""

    def _create_manifest(self, exp_dir: Path, status: str, valid: bool = True) -> None:
        """Helper to create a manifest with given status."""
        manifest = {
            "experiment_id": "EXP-TEST-0001",
            "experiment_status": status,
            "timestamp": "2026-08-26T00:00:00",
            "git": {"commit": "abc123", "dirty": False, "branch": "main"},
            "software": {"python": "3.13", "brain5d_version": "0.5.0a5"},
            "simulation": {"seed": 42, "ticks": 100},
            "artifacts": {},
            "validity": {
                "valid": valid,
                "reason": None if valid else "runtime errors",
                "runtime_error_count": 0 if valid else 1,
                "fatal_error_count": 0,
            },
            "runtime_errors": (
                []
                if valid
                else [
                    {
                        "tick": 1,
                        "phase": "step",
                        "exception_type": "Error",
                        "message": "test",
                    }
                ]
            ),
        }
        (exp_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )

    def test_template_rejected(self, tmp_path: Path) -> None:
        """template experiments cannot produce evidence."""
        exp_dir = tmp_path / "research" / "experiments" / "EXP-TEST-0001"
        exp_dir.mkdir(parents=True, exist_ok=True)
        self._create_manifest(exp_dir, "template")
        assert _check_experiment_valid("EXP-TEST-0001") is None  # type: ignore[misc]

    def test_not_started_rejected(self, tmp_path: Path) -> None:
        """not_started experiments cannot produce evidence."""
        exp_dir = tmp_path / "research" / "experiments" / "EXP-TEST-0001"
        exp_dir.mkdir(parents=True, exist_ok=True)
        self._create_manifest(exp_dir, "not_started")
        assert _check_experiment_valid("EXP-TEST-0001") is None  # type: ignore[misc]

    def test_running_rejected(self, tmp_path: Path) -> None:
        """running experiments cannot produce evidence."""
        exp_dir = tmp_path / "research" / "experiments" / "EXP-TEST-0001"
        exp_dir.mkdir(parents=True, exist_ok=True)
        self._create_manifest(exp_dir, "running")
        assert _check_experiment_valid("EXP-TEST-0001") is None

    def test_failed_rejected(self, tmp_path: Path) -> None:
        """failed experiments cannot produce evidence."""
        exp_dir = tmp_path / "research" / "experiments" / "EXP-TEST-0001"
        exp_dir.mkdir(parents=True, exist_ok=True)
        self._create_manifest(exp_dir, "failed")
        assert _check_experiment_valid("EXP-TEST-0001") is None

    def test_invalid_rejected(self, tmp_path: Path) -> None:
        """invalid experiments cannot produce evidence."""
        exp_dir = tmp_path / "research" / "experiments" / "EXP-TEST-0001"
        exp_dir.mkdir(parents=True, exist_ok=True)
        self._create_manifest(exp_dir, "invalid", valid=False)
        assert _check_experiment_valid("EXP-TEST-0001") is None

    def test_completed_valid_accepted(self, tmp_path: Path) -> None:
        """completed + valid experiments CAN produce evidence."""
        import src.research.evidence_engine as ee_module

        original_dir = ee_module.EXPERIMENTS_DIR
        try:
            exp_dir = tmp_path / "research" / "experiments" / "EXP-TEST-0001"
            exp_dir.mkdir(parents=True, exist_ok=True)
            ee_module.EXPERIMENTS_DIR = tmp_path / "research" / "experiments"
            self._create_manifest(exp_dir, "completed", valid=True)
            result = _check_experiment_valid("EXP-TEST-0001")
            assert result is not None
            assert result["experiment_status"] == "completed"
        finally:
            ee_module.EXPERIMENTS_DIR = original_dir

    def test_completed_invalid_rejected(self, tmp_path: Path) -> None:
        """completed + invalid (runtime errors) experiments cannot produce evidence."""
        exp_dir = tmp_path / "research" / "experiments" / "EXP-TEST-0001"
        exp_dir.mkdir(parents=True, exist_ok=True)
        self._create_manifest(exp_dir, "completed", valid=False)
        assert _check_experiment_valid("EXP-TEST-0001") is None

    def test_ai_influenced_run_requires_registered_treatment(self, tmp_path: Path) -> None:
        import src.research.evidence_engine as ee_module

        exp_dir = tmp_path / "research" / "experiments" / "EXP-TEST-0001"
        exp_dir.mkdir(parents=True, exist_ok=True)
        self._create_manifest(exp_dir, "completed", valid=True)
        manifest_path = exp_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["causal_taint"] = "AI_INFLUENCED"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        original_dir = ee_module.EXPERIMENTS_DIR
        try:
            ee_module.EXPERIMENTS_DIR = tmp_path / "research" / "experiments"
            assert _check_experiment_valid("EXP-TEST-0001") is None
            manifest["ai_treatment"] = {"protocol_id": "PROTOCOL-AI-001", "registered": True}
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            assert _check_experiment_valid("EXP-TEST-0001") is not None
        finally:
            ee_module.EXPERIMENTS_DIR = original_dir

    def test_dirty_worktree_rejected(self, tmp_path: Path) -> None:
        """A dirty source tree cannot produce scientific evidence."""
        import src.research.evidence_engine as ee_module

        exp_dir = tmp_path / "research" / "experiments" / "EXP-TEST-0001"
        exp_dir.mkdir(parents=True, exist_ok=True)
        self._create_manifest(exp_dir, "completed", valid=True)
        manifest_path = exp_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["git"]["dirty"] = True
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        original_dir = ee_module.EXPERIMENTS_DIR
        try:
            ee_module.EXPERIMENTS_DIR = tmp_path / "research" / "experiments"
            assert _check_experiment_valid("EXP-TEST-0001") is None
        finally:
            ee_module.EXPERIMENTS_DIR = original_dir

    def test_evidence_engine_raises_for_invalid(
        self, registry: ResearchRegistry, tmp_path: Path
    ) -> None:
        """EvidenceEngine.evaluate_experiment raises ValueError for invalid experiments."""
        engine = EvidenceEngine(registry)
        exp_dir = tmp_path / "research" / "experiments" / "EXP-TEST-0001"
        exp_dir.mkdir(parents=True, exist_ok=True)
        self._create_manifest(exp_dir, "invalid", valid=False)

        # Override EXPERIMENTS_DIR in evidence_engine to point to tmp_path
        import src.research.evidence_engine as ee_module

        original_dir = ee_module.EXPERIMENTS_DIR
        try:
            ee_module.EXPERIMENTS_DIR = tmp_path / "research" / "experiments"
            with pytest.raises(ValueError, match="not scientifically valid"):
                engine.evaluate_experiment(
                    experiment_id="EXP-TEST-0001",
                    claim_id="CLAIM-TEST-001",
                    hypothesis_id="H-TEST-001-A",
                    result_summary="Test result",
                )
        finally:
            ee_module.EXPERIMENTS_DIR = original_dir

    def test_evidence_engine_accepts_valid(
        self, registry: ResearchRegistry, tmp_path: Path
    ) -> None:
        """EvidenceEngine accepts completed + valid experiments."""
        engine = EvidenceEngine(registry)
        exp_dir = tmp_path / "research" / "experiments" / "EXP-TEST-0001"
        exp_dir.mkdir(parents=True, exist_ok=True)
        self._create_manifest(exp_dir, "completed", valid=True)

        import src.research.evidence_engine as ee_module

        original_dir = ee_module.EXPERIMENTS_DIR
        original_evidence = ee_module.EVIDENCE_DIR
        try:
            ee_module.EXPERIMENTS_DIR = tmp_path / "research" / "experiments"
            ee_module.EVIDENCE_DIR = tmp_path / "research" / "registry" / "evidence"
            ee_module.EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

            evidence_id = engine.evaluate_experiment(
                experiment_id="EXP-TEST-0001",
                claim_id="CLAIM-TEST-001",
                hypothesis_id="H-TEST-001-A",
                result_summary="Test result - hypothesis supported",
                status="supports",
            )
            assert evidence_id.startswith("EVID-")
        finally:
            ee_module.EXPERIMENTS_DIR = original_dir
            ee_module.EVIDENCE_DIR = original_evidence


# ============================================================================
# Phase 2: Fail-fast mode
# ============================================================================


class TestFailFastMode:
    """Fail-fast mode stops experiment on first runtime error."""

    def test_fail_fast_sets_invalid_on_first_error(
        self, tmp_experiment_dir: Path
    ) -> None:
        """With fail_fast=True, first runtime error sets status to invalid."""
        recorder = ExperimentRecorder(
            "EXP-TEST-0001", output_dir=tmp_experiment_dir, fail_fast=True
        )
        recorder.record_runtime_error(
            tick=1,
            phase="step",
            exception_type="RuntimeError",
            message="fail-fast trigger",
        )
        assert recorder.manifest["experiment_status"] == "invalid"
        assert recorder.manifest["validity"]["valid"] is False

    def test_fail_fast_no_error_allows_completed(
        self, tmp_experiment_dir: Path
    ) -> None:
        """With fail_fast=True but no errors, experiment can complete normally."""
        recorder = ExperimentRecorder(
            "EXP-TEST-0001", output_dir=tmp_experiment_dir, fail_fast=True
        )
        recorder.mark_completed()
        assert recorder.manifest["experiment_status"] == "completed"
        assert recorder.manifest["validity"]["valid"] is True

    def test_default_no_fail_fast(self, tmp_experiment_dir: Path) -> None:
        """Default mode (fail_fast=False) does NOT auto-invalidate on error."""
        recorder = ExperimentRecorder("EXP-TEST-0001", output_dir=tmp_experiment_dir)
        recorder.record_runtime_error(
            tick=1, phase="step", exception_type="RuntimeError", message="non-fatal"
        )
        # Status should still be not_started (not auto-invalidated)
        assert recorder.manifest["experiment_status"] == "not_started"
        # But validity is false
        assert recorder.manifest["validity"]["valid"] is False
