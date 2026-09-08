"""Tests for independently assessable experiment-series summaries."""

from __future__ import annotations

import json
from pathlib import Path

from src.dashboard.experiment_organizer import ExperimentOrganizerService


def test_series_summary_keeps_child_results_and_review_boundary(tmp_path: Path) -> None:
    workflows = tmp_path / "workflows"
    workflows.mkdir()
    (workflows / "EXP-SERIES-0001.json").write_text(
        json.dumps(
            {
                "workflow_id": "EXP-SERIES-0001",
                "created_at": "2026-09-08T12:00:00+00:00",
                "protocols": ["protocol_a", "protocol_b"],
                "requested_ticks": 32,
                "seeds": "42-51",
                "completed": 2,
                "failed": 0,
                "results": [
                    {"protocol": "protocol_a", "experiment_id": "EXP-SERIES-0001-01", "status": "completed"},
                    {"protocol": "protocol_b", "experiment_id": "EXP-SERIES-0001-02", "status": "completed"},
                ],
            }
        ),
        encoding="utf-8",
    )

    series = ExperimentOrganizerService(tmp_path).list_series()

    assert len(series) == 1
    item = series[0]
    assert item["series_id"] == "EXP-SERIES-0001"
    assert item["status"] == "completed"
    assert item["assessment_status"] == "HUMAN_REVIEW_REQUIRED"
    assert item["completed"] == 2
    assert item["failed"] == 0
    assert len(item["results"]) == 2
    assert "no automatic evidence promotion" in item["assessment_boundary"]
