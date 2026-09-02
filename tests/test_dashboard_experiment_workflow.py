"""Tests for controlled dashboard experiment workflow publication."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.dashboard.experiment_workflow import (
    ExperimentWorkflowService,
    WorkflowValidationError,
)


def _write_registry(root: Path) -> None:
    registry = root / "registry"
    registry.mkdir(parents=True)
    (registry / "questions.yaml").write_text(
        "- id: RQ-SNN-001\n  domain: snn\n  question: Does it run?\n  relevance: test\n"
        "- id: RQ-SNN-002\n  domain: snn\n  question: Does it link?\n  relevance: test\n",
        encoding="utf-8",
    )
    (registry / "hypotheses.yaml").write_text(
        "- id: H-SNN-001-A\n  research_question: RQ-SNN-001\n  hypothesis: It advances ticks.\n",
        encoding="utf-8",
    )


def test_run_writes_traceable_manifest_plan_and_report(tmp_path: Path) -> None:
    _write_registry(tmp_path)
    service = ExperimentWorkflowService(tmp_path)
    state = {"tick": 10, "neurons": 100, "synapses": 250}

    def run_ticks(ticks: int) -> None:
        state["tick"] += ticks

    result = service.run(
        {
            "experiment_id": "EXP-SNN-0001",
            "question_id": "RQ-SNN-001",
            "hypothesis_id": "H-SNN-001-A",
            "title": "Tick advance",
            "conditions": "seed=7; fixed configuration",
            "ticks": 25,
            "notes": "Expected controlled advance.",
        },
        run_ticks,
        dict(state),
        lambda: dict(state),
    )

    experiment_dir = tmp_path / "experiments" / "EXP-SNN-0001"
    manifest = json.loads((experiment_dir / "manifest.json").read_text(encoding="utf-8"))
    report = (experiment_dir / "report.md").read_text(encoding="utf-8")
    assert result["report"] == "experiments/EXP-SNN-0001/report.md"
    assert manifest["experiment_status"] == "completed"
    assert manifest["research_questions"] == ["RQ-SNN-001"]
    assert manifest["hypotheses"] == ["H-SNN-001-A"]
    assert manifest["results"]["observed_ticks"] == 25
    assert "## Ergebnis" in report
    assert "KI-Ausgaben" in report


def test_run_rejects_hypothesis_from_a_different_question(tmp_path: Path) -> None:
    _write_registry(tmp_path)
    service = ExperimentWorkflowService(tmp_path)

    with pytest.raises(WorkflowValidationError, match="does not belong"):
        service.run(
            {
                "experiment_id": "EXP-SNN-0002",
                "question_id": "RQ-SNN-002",
                "hypothesis_id": "H-SNN-001-A",
                "title": "Invalid link",
                "conditions": "fixed",
                "ticks": 1,
            },
            lambda _ticks: None,
            {"tick": 0, "neurons": 0, "synapses": 0},
            lambda: {"tick": 0, "neurons": 0, "synapses": 0},
        )


def test_run_generates_an_id_when_the_ui_field_is_empty(tmp_path: Path) -> None:
    _write_registry(tmp_path)
    service = ExperimentWorkflowService(tmp_path)

    result = service.run(
        {
            "experiment_id": "",
            "question_id": "RQ-SNN-001",
            "hypothesis_id": "H-SNN-001-A",
            "title": "Generated identifier",
            "conditions": "fixed",
            "ticks": 1,
        },
        lambda _ticks: None,
        {"tick": 0, "neurons": 0, "synapses": 0},
        lambda: {"tick": 1, "neurons": 0, "synapses": 0},
    )

    assert result["experiment_id"] == "EXP-GEN-0001"
    assert (tmp_path / "experiments" / "EXP-GEN-0001" / "report.md").is_file()