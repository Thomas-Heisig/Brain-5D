"""Tests for controlled dashboard experiment workflow publication."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

from src.dashboard.experiment_workflow import (
    ExperimentWorkflowService,
    WorkflowValidationError,
    write_experiment_summary,
)
from src.dashboard.research_source import ResearchSource
from src.dashboard.server import DashboardRequestHandler
from src.research_assistant.airr import write_artifact_review


def _report_backend(_prompt: str) -> tuple[dict[str, Any], dict[str, str | float]]:
    return (
        {
            "assessment": "Post-hoc summary",
            "observations": ["The run completed."],
            "effect_direction": "not_determined",
            "methodological_concerns": [],
            "alternative_explanations": [],
            "recommended_experiments": [],
            "requested_evidence": ["Human review"],
            "confidence": 0.1,
        },
        {"provider": "test", "model": "fixture"},
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
    (registry / "claims.yaml").write_text("[]\n", encoding="utf-8")


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
    manifest = json.loads(
        (experiment_dir / "manifest.json").read_text(encoding="utf-8")
    )
    report = (experiment_dir / "report.md").read_text(encoding="utf-8")
    assert result["report"] == "experiments/EXP-SNN-0001/report.md"
    assert manifest["experiment_status"] == "completed"
    assert manifest["research_questions"] == ["RQ-SNN-001"]
    assert manifest["hypotheses"] == ["H-SNN-001-A"]
    assert manifest["results"]["observed_ticks"] == 25
    assert manifest["created_at"]
    assert "## Ergebnis" in report
    assert "## Reproduzierbarkeit" in report
    assert "## Evidenzstatus" in report
    assert "KI-Ausgaben" in report


def test_run_can_append_ai_report_only_after_completed_run(tmp_path: Path) -> None:
    _write_registry(tmp_path)
    service = ExperimentWorkflowService(tmp_path)
    state = {"tick": 0, "neurons": 1, "synapses": 1}

    result = service.run(
        {
            "experiment_id": "EXP-SNN-REPORT-0001",
            "question_id": "RQ-SNN-001",
            "hypothesis_id": "H-SNN-001-A",
            "title": "Report hook fixture",
            "conditions": "fixed",
            "ticks": 1,
        },
        lambda ticks: state.__setitem__("tick", state["tick"] + ticks),
        dict(state),
        lambda: dict(state),
    )

    assert result["experiment_id"] == "EXP-SNN-REPORT-0001"
    experiment_dir = tmp_path / "experiments" / "EXP-SNN-REPORT-0001"
    assert (experiment_dir / "manifest.json").is_file()

    handler = cast(Any, DashboardRequestHandler.__new__(DashboardRequestHandler))
    handler.server = SimpleNamespace(
        research_source=ResearchSource(tmp_path),
        research_ai_backend=_report_backend,
    )
    ai_result = handler._append_ai_report(  # pyright: ignore[reportPrivateUsage]
        "EXP-SNN-REPORT-0001"
    )

    assert ai_result["status"] == "generated", ai_result
    report_id = str(ai_result["report_id"])
    report_dir = tmp_path / "experiments" / "EXP-SNN-REPORT-0001" / "reports"
    saved = json.loads((report_dir / f"{report_id}.json").read_text(encoding="utf-8"))
    assert saved["status"] == "review_pending"
    assert saved["scientific_evidence"] is False
    assert (report_dir / f"{report_id}.md").is_file()


def test_human_review_can_be_attached_to_any_experiment_artifact(
    tmp_path: Path,
) -> None:
    artifact = tmp_path / "experiments" / "EXP-REVIEW-0001" / "summary.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("# Zusammenfassung\n", encoding="utf-8")

    review_path = write_artifact_review(
        tmp_path,
        "experiments/EXP-REVIEW-0001/summary.md",
        {
            "review_status": "accepted_as_interpretation",
            "reviewer": "Dr. Test",
            "comments": "Inhalt und Zuordnung geprueft.",
        },
    )

    review = json.loads(review_path.read_text(encoding="utf-8"))
    assert review["artifact_path"].endswith("/summary.md")
    assert review["review_status"] == "accepted_as_interpretation"
    assert review["artifact_content_digest"]


def test_summary_falls_back_from_empty_airr_lists_to_limitations(tmp_path: Path) -> None:
    experiment_dir = tmp_path / "experiments" / "EXP-SUMMARY-0001"
    report_dir = experiment_dir / "reports"
    report_dir.mkdir(parents=True)
    (experiment_dir / "manifest.json").write_text(
        json.dumps({"experiment_status": "completed"}), encoding="utf-8"
    )
    (report_dir / "AIRR-2026-0001.json").write_text(
        json.dumps(
            {
                "content": {
                    "executive_summary": "Interpretation only.",
                    "ai_confidence": 0.3,
                    "missing_evidence": [],
                    "recommended_follow_up": [],
                    "interpretation": {
                        "observations": [
                            {"type": "Limitations", "value": "Raw traces are missing."}
                        ]
                    },
                }
            }
        ),
        encoding="utf-8",
    )

    write_experiment_summary(
        tmp_path,
        "EXP-SUMMARY-0001",
        {"status": "generated", "report_id": "AIRR-2026-0001"},
    )

    summary = (experiment_dir / "summary.md").read_text(encoding="utf-8")
    assert "AIRR-Limitation dokumentieren: Raw traces are missing." in summary
    assert "Keine expliziten Folgeexperimente im AIRR angegeben." in summary


def test_experiments_are_listed_by_creation_date(tmp_path: Path) -> None:
    for experiment_id, created_at in (
        ("EXP-OLD", "2026-09-01T00:00:00+00:00"),
        ("EXP-NEW", "2026-09-03T00:00:00+00:00"),
    ):
        directory = tmp_path / "experiments" / experiment_id
        directory.mkdir(parents=True)
        (directory / "manifest.json").write_text(
            json.dumps({"created_at": created_at}), encoding="utf-8"
        )

    experiments = ResearchSource(tmp_path).list_experiments()

    assert [item["id"] for item in experiments] == ["EXP-NEW", "EXP-OLD"]


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


def test_catalog_publishes_the_next_generated_experiment_id(tmp_path: Path) -> None:
    _write_registry(tmp_path)

    catalog = ExperimentWorkflowService(tmp_path).catalog()

    assert catalog["next_experiment_id"] == "EXP-GEN-0001"


def test_science_suite_publishes_all_artifacts_without_unconfigured_ai(
    tmp_path: Path,
) -> None:
    _write_registry(tmp_path)
    service = ExperimentWorkflowService(tmp_path)

    result = service.run_science(
        {
            "experiment_id": "EXP-PING-0001",
            "question_id": "RQ-SNN-001",
            "hypothesis_id": "H-SNN-001-A",
            "title": "Impulse response",
            "conditions": "seed=42; recurrence controlled",
            "ticks": 8,
        },
        seeds=(42,),
    )

    experiment_dir = tmp_path / "experiments" / "EXP-PING-0001"
    manifest = json.loads(
        (experiment_dir / "manifest.json").read_text(encoding="utf-8")
    )
    data = json.loads(
        (experiment_dir / "DATA" / "runs.json").read_text(encoding="utf-8")
    )
    assert result["data_id"] == "DATA-EXP-PING-0001"
    assert manifest["experiment_status"] == "completed"
    assert manifest["artifacts"]["data"] == "DATA/runs.json"
    assert manifest["artifacts"]["workflow"] == "workflow.json"
    assert manifest["artifacts"]["report"] == "report.md"
    assert len(manifest["config"]["sha256"]) == 64
    assert len(manifest["source_freeze_sha"]) == 64
    assert len(manifest["provenance_digests"]["data"]) == 64
    assert len(data) == 2
    assert (experiment_dir / "report.md").is_file()
    assert (experiment_dir / "summary.md").is_file()
    assert (experiment_dir / "workflow.json").is_file()
    assert result["ai_report"] == {
        "status": "unavailable",
        "reason": "AI backend not configured",
    }


def test_science_suite_accepts_generated_experiment_id(tmp_path: Path) -> None:
    _write_registry(tmp_path)
    service = ExperimentWorkflowService(tmp_path)

    result = service.run_science(
        {
            "experiment_id": "EXP-GEN-0001",
            "question_id": "RQ-SNN-001",
            "hypothesis_id": "H-SNN-001-A",
            "title": "Generated impulse response",
            "conditions": "seed=42",
            "ticks": 8,
            "protocol": "science_suite_v1",
        },
        seeds=(42,),
    )

    assert result["experiment_id"] == "EXP-GEN-0001"
    runs = json.loads(
        (tmp_path / "experiments" / "EXP-GEN-0001" / "DATA" / "runs.json").read_text(
            encoding="utf-8"
        )
    )
    assert len(runs) == 2
    assert {run["experiment_id"] for run in runs} == {"EXP-GEN-0001"}


def test_science_suite_uses_selected_seeds_and_ticks(tmp_path: Path) -> None:
    _write_registry(tmp_path)
    service = ExperimentWorkflowService(tmp_path)

    result = service.run_science(
        {
            "experiment_id": "EXP-GEN-0002",
            "question_id": "RQ-SNN-001",
            "hypothesis_id": "H-SNN-001-A",
            "title": "Configured impulse response",
            "conditions": "Seeds 7-8; measurement window 3 ticks",
            "ticks": 3,
            "seeds": "7-8",
            "protocol": "science_suite_v1",
        }
    )

    experiment_dir = tmp_path / "experiments" / "EXP-GEN-0002"
    runs = json.loads(
        (experiment_dir / "DATA" / "runs.json").read_text(encoding="utf-8")
    )
    workflow = json.loads(
        (experiment_dir / "workflow.json").read_text(encoding="utf-8")
    )
    assert result["experiment_id"] == "EXP-GEN-0002"
    assert {run["seed"] for run in runs} == {7, 8}
    assert workflow["seeds"] == [7, 8]
    assert workflow["ticks"] == 3


def test_science_suite_persists_deterministic_spike_sequence_evidence(
    tmp_path: Path,
) -> None:
    _write_registry(tmp_path)
    service = ExperimentWorkflowService(tmp_path)

    service.run_science(
        {
            "experiment_id": "EXP-GEN-0003",
            "question_id": "RQ-SNN-001",
            "hypothesis_id": "H-SNN-001-A",
            "title": "Observable impulse response",
            "conditions": "Seeds 42,43,44; identical impulse conditions",
            "ticks": 1000,
            "protocol": "science_suite_v1",
        }
    )

    runs = json.loads(
        (
            tmp_path
            / "experiments"
            / "EXP-GEN-0003"
            / "DATA"
            / "runs.json"
        ).read_text(encoding="utf-8")
    )
    ping_runs = [run for run in runs if run["condition"] == "recurrence_off"]
    assert ping_runs
    assert all(run["metrics"]["spike_sequence"] for run in ping_runs)
    assert all(run["metrics"]["reproducible_across_seeds"] for run in ping_runs)
    assert len({run["metrics"]["spike_sequence_digest"] for run in ping_runs}) == 1


def test_science_all_covers_every_registered_suite_group(tmp_path: Path) -> None:
    _write_registry(tmp_path)
    service = ExperimentWorkflowService(tmp_path)

    result = service.run_science(
        {
            "experiment_id": "EXP-GEN-ALL-0001",
            "question_id": "RQ-SNN-001",
            "hypothesis_id": "H-SNN-001-A",
            "title": "Complete science suite",
            "conditions": "All registered science-suite runners",
            "ticks": 2,
            "seeds": "42",
            "protocol": "science_all_v1",
        }
    )

    experiment_dir = tmp_path / "experiments" / "EXP-GEN-ALL-0001"
    runs = json.loads(
        (experiment_dir / "DATA" / "runs.json").read_text(encoding="utf-8")
    )
    workflow = json.loads(
        (experiment_dir / "workflow.json").read_text(encoding="utf-8")
    )
    groups = {run["condition"].split(":", 1)[0] for run in runs}
    assert result["experiment_id"] == "EXP-GEN-ALL-0001"
    assert groups == {"ping", "temporal", "stdp", "learning", "time", "5d", "regulation"}
    assert workflow["protocol"] == "science_all_v1"


def test_science_protocol_selection_overrides_manual_label_prefix(
    tmp_path: Path,
) -> None:
    _write_registry(tmp_path)
    service = ExperimentWorkflowService(tmp_path)

    result = service.run_science(
        {
            "experiment_id": "EXP-MANUAL-0001",
            "question_id": "RQ-SNN-001",
            "hypothesis_id": "H-SNN-001-A",
            "title": "Manual time calibration",
            "conditions": "seed=42",
            "ticks": 100,
            "protocol": "science_time_v1",
        },
        seeds=(42,),
    )

    runs = json.loads(
        (tmp_path / "experiments" / "EXP-MANUAL-0001" / "DATA" / "runs.json").read_text(
            encoding="utf-8"
        )
    )
    assert result["experiment_id"] == "EXP-MANUAL-0001"
    assert len(runs) == 1
    assert {run["condition"] for run in runs} == {"100"}


def test_science_suite_generates_post_hoc_ai_report_with_explicit_backend(
    tmp_path: Path,
) -> None:
    _write_registry(tmp_path)
    service = ExperimentWorkflowService(tmp_path, _report_backend)

    result = service.run_science(
        {
            "experiment_id": "EXP-PING-0001",
            "question_id": "RQ-SNN-001",
            "hypothesis_id": "H-SNN-001-A",
            "title": "Impulse response with AIRR",
            "conditions": "seed=42",
            "ticks": 8,
        },
        seeds=(42,),
    )

    ai_report = cast(dict[str, Any], result["ai_report"])
    assert ai_report["status"] == "generated"
    report_id = str(ai_report["report_id"])
    report_dir = tmp_path / "experiments" / "EXP-PING-0001" / "reports"
    assert (report_dir / f"{report_id}.json").is_file()
    assert (report_dir / f"{report_id}.md").is_file()
    manifest = json.loads(
        (tmp_path / "experiments" / "EXP-PING-0001" / "manifest.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest["artifacts"]["ai_report_json"] == (
        f"experiments/EXP-PING-0001/reports/{report_id}.json"
    )
    summary = (tmp_path / "experiments" / "EXP-PING-0001" / "summary.md").read_text(
        encoding="utf-8"
    )
    assert "## Versuchsuebersicht" in summary
    assert "- Status: `completed`" in summary
    assert "Angeforderte zusaetzliche Nachweise:" in summary
    assert "Empfohlene Folgeexperimente:" in summary
    assert f"{report_id}.md" in summary
    assert "Post-hoc summary" in summary

    report = json.loads(
        (report_dir / f"{report_id}.json").read_text(encoding="utf-8")
    )
    assert report["content"]["epistemic_status"]["experiment_data"] == "PRESENT"
    assert report["content"]["data_basis"]["data"]["runs"]
    assert report["content"]["experimental_design"]["protocol"] == "science_suite_v1"
    assert report["content"]["reproducibility"]["configuration_sha256"] != (
        "NOT_AVAILABLE"
    )
