from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.research_assistant.airr import AIRRPipeline


def test_airr_writes_reviewable_fallback_when_backend_schema_is_invalid(tmp_path: Path) -> None:
    experiment = tmp_path / "experiments" / "EXP-AIR-0002"
    analysis = experiment / "analysis"
    analysis.mkdir(parents=True)
    (experiment / "manifest.json").write_text(
        json.dumps({
            "experiment_status": "completed",
            "research_questions": ["RQ-AIR-001"],
            "hypotheses": ["H-AIR-001-A"],
            "artifacts": {"data": "DATA/runs.json"},
            "git": {"commit": "fixture", "dirty": True},
        }),
        encoding="utf-8",
    )
    (experiment / "DATA").mkdir()
    (experiment / "DATA" / "runs.json").write_text("{}", encoding="utf-8")
    (analysis / "statistics.json").write_text(
        json.dumps({"generated_by": "deterministic_statistics_engine", "n": 1}),
        encoding="utf-8",
    )
    (tmp_path / "registry").mkdir()
    (tmp_path / "registry" / "questions.yaml").write_text(
        "- id: RQ-AIR-001\n  question: Test\n", encoding="utf-8"
    )
    (tmp_path / "registry" / "hypotheses.yaml").write_text(
        "- id: H-AIR-001-A\n  research_question: RQ-AIR-001\n  hypothesis: Test\n",
        encoding="utf-8",
    )
    (tmp_path / "registry" / "claims.yaml").write_text("[]\n", encoding="utf-8")

    def invalid_backend(_prompt: str) -> tuple[dict[str, Any], dict[str, str]]:
        return ({"invalid": True}, {"provider": "fixture", "model": "invalid"})

    report = AIRRPipeline(tmp_path).analyze("EXP-AIR-0002", invalid_backend)
    saved = json.loads(
        (experiment / "reports" / f"{report.report_id}.json").read_text(encoding="utf-8")
    )
    assert saved["status"] == "review_pending"
    assert saved["scientific_evidence"] is False
    assert len(saved["analysis_ids"]) == 3
    assert saved["content"]["interpretation"]["analysis_unavailable"] is True