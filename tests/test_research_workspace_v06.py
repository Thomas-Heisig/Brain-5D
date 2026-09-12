from __future__ import annotations

import json
from pathlib import Path

from src.dashboard.experiment_archive import ExperimentArchiveService
from src.dashboard.research_source import ResearchSource

STATIC = Path("src/dashboard/static")


def test_research_workspace_is_owned_by_central_workspace_router() -> None:
    router = (STATIC / "frontend" / "workspace-router.js").read_text(encoding="utf-8")
    controller = (STATIC / "box-state-controller.js").read_text(encoding="utf-8")
    for route in ("observatory", "experiments", "network", "dynamics", "inspect", "data", "files", "registry"):
        assert f'["{route}",' in router
    assert 'label: "Wissenschaft"' in router
    assert "research-workspace-tabs" not in controller
    assert "installResearchWorkspaceStyle" not in controller
    assert "brain5d:open-file" in (STATIC / "frontend" / "modules" / "research-docs.js").read_text(encoding="utf-8")


def test_metadata_archive_filters_work_view_without_moving_artifacts(
    tmp_path: Path,
) -> None:
    experiment = tmp_path / "experiments" / "EXP-VIEW-0001"
    experiment.mkdir(parents=True)
    manifest = {
        "experiment_id": "EXP-VIEW-0001",
        "experiment_status": "completed",
        "created_at": "2026-09-09T10:00:00Z",
    }
    (experiment / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    source = ResearchSource(tmp_path)
    service = ExperimentArchiveService(tmp_path)

    assert [item["id"] for item in source.list_experiments()] == ["EXP-VIEW-0001"]
    service.archive_experiment("EXP-VIEW-0001", "finished")

    assert (experiment / "manifest.json").is_file()
    assert source.list_experiments() == []
    assert service.list_archived()[0]["canonical_path"] == "experiments/EXP-VIEW-0001"

    service.restore_experiment("EXP-VIEW-0001")
    assert [item["id"] for item in source.list_experiments()] == ["EXP-VIEW-0001"]
