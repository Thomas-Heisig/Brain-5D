"""End-to-end contracts for AI Research Reports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from src.research_assistant import AIRRPipeline, write_human_review


def _fixture(root: Path) -> None:
    (root / "experiments" / "EXP-AIR-0001").mkdir(parents=True)
    (root / "generated" / "data").mkdir(parents=True)
    (root / "registry" / "evidence").mkdir(parents=True)
    (root / "experiments" / "EXP-AIR-0001" / "manifest.json").write_text(
        json.dumps(
            {
                "experiment_status": "completed",
                "research_questions": ["RQ-STDP-001"],
                "hypotheses": ["H-STDP-001-A"],
                "artifacts": {"data": "research/generated/data/DATA-AIR-0001.json"},
                "git": {"commit": "abc123", "dirty": False},
            }
        ),
        encoding="utf-8",
    )
    (root / "generated" / "data" / "DATA-AIR-0001.json").write_text(
        json.dumps({"weight": [1, 2, 3]}),
        encoding="utf-8",
    )
    analysis = root / "experiments" / "EXP-AIR-0001" / "analysis"
    analysis.mkdir()
    (analysis / "statistics.json").write_text(
        json.dumps(
            {
                "n": 3,
                "mean": 2.0,
                "generated_by": "deterministic_statistics_engine",
            }
        ),
        encoding="utf-8",
    )
    (root / "registry" / "questions.yaml").write_text(
        "- id: RQ-STDP-001\n  question: Does timing work?\n", encoding="utf-8"
    )
    (root / "registry" / "hypotheses.yaml").write_text(
        "- id: H-STDP-001-A\n  research_question: RQ-STDP-001\n  hypothesis: It works.\n",
        encoding="utf-8",
    )
    (root / "registry" / "claims.yaml").write_text(
        "- id: CLAIM-STDP-001\n  research_question: RQ-STDP-001\n  claim: Timing works.\n",
        encoding="utf-8",
    )


def _backend(_prompt: str) -> tuple[dict[str, Any], dict[str, str | float]]:
    return (
        {
            "assessment": "The data are compatible with the hypothesis.",
            "observations": ["The deterministic statistics report n=3."],
            "effect_direction": "positive",
            "methodological_concerns": ["Independent replications are absent."],
            "alternative_explanations": [
                "A deterministic fixture may explain the result."
            ],
            "recommended_experiments": ["Run independent clean-freeze repetitions."],
            "confidence": 0.73,
            "requested_evidence": ["Independent EVID records."],
        },
        {"provider": "test", "model": "fixture", "model_digest": "unknown"},
    )


def test_pipeline_writes_three_aiars_and_canonical_airr(tmp_path: Path) -> None:
    _fixture(tmp_path)
    report = AIRRPipeline(tmp_path).analyze("EXP-AIR-0001", _backend)
    report_dir = tmp_path / "reports" / "EXP-AIR-0001"
    saved = json.loads((report_dir / f"{report.report_id}.json").read_text())

    assert report.report_id == "AIRR-2026-0001"
    assert len(report.analysis_ids) == 3
    assert saved["ai_generated"] is True
    assert saved["scientific_evidence"] is False
    assert saved["human_review_required"] is True
    assert saved["status"] == "review_pending"
    assert saved["content"]["quantitative_results"] == {
        "n": 3,
        "mean": 2.0,
        "generated_by": "deterministic_statistics_engine",
    }
    markdown = (report_dir / f"{report.report_id}.md").read_text()
    assert markdown.startswith(
        "============================================================\nBRAIN-5D - AI GENERATED SCIENTIFIC ANALYSIS"
    )
    assert "## Observations" in markdown and "## Interpretation" in markdown

    original = (report_dir / f"{report.report_id}.json").read_text()
    review = write_human_review(
        tmp_path,
        "EXP-AIR-0001",
        report.report_id,
        {
            "review_status": "accepted_as_interpretation",
            "reviewer": "human",
            "comments": "Interpretation accepted; this is not scientific evidence.",
        },
    )
    assert review.name.endswith(".review.json")
    assert (report_dir / f"{report.report_id}.json").read_text() == original


def test_human_review_requires_bound_report_identity_and_comments(
    tmp_path: Path,
) -> None:
    _fixture(tmp_path)
    report = AIRRPipeline(tmp_path).analyze("EXP-AIR-0001", _backend)

    with pytest.raises(ValueError, match="comments"):
        write_human_review(
            tmp_path,
            "EXP-AIR-0001",
            report.report_id,
            {"review_status": "accepted_as_interpretation", "reviewer": "human"},
        )
    with pytest.raises(ValueError, match="does not exist"):
        write_human_review(
            tmp_path,
            "EXP-AIR-0001",
            "AIRR-2026-9999",
            {
                "review_status": "accepted_as_interpretation",
                "reviewer": "human",
                "comments": "Reviewed.",
            },
        )


def test_pipeline_rejects_unverified_quantitative_statistics(tmp_path: Path) -> None:
    _fixture(tmp_path)
    statistics_path = (
        tmp_path / "experiments" / "EXP-AIR-0001" / "analysis" / "statistics.json"
    )
    statistics_path.write_text(json.dumps({"n": 3, "mean": 2.0}), encoding="utf-8")

    with pytest.raises(ValueError, match="Statistics Engine"):
        AIRRPipeline(tmp_path).analyze("EXP-AIR-0001", _backend)


def test_pipeline_rejects_model_owned_quantitative_statistics(tmp_path: Path) -> None:
    _fixture(tmp_path)

    def model_statistics_backend(
        _prompt: str,
    ) -> tuple[dict[str, Any], dict[str, str | float]]:
        output, model = _backend(_prompt)
        output["quantitative_results"] = {"n": 999, "mean": 999.0}
        return output, model

    with pytest.raises(
        ValueError, match="LLM must not generate quantitative statistics"
    ):
        AIRRPipeline(tmp_path).analyze("EXP-AIR-0001", model_statistics_backend)
