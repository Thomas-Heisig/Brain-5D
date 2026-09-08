"""Tests for immutable experiment archive operations."""

from __future__ import annotations

import json
from pathlib import Path

from src.dashboard.experiment_archive import ExperimentArchiveService


def test_archive_and_restore_preserve_experiment_contents(tmp_path: Path) -> None:
    experiment = tmp_path / "experiments" / "EXP-ARCHIVE-0001"
    experiment.mkdir(parents=True)
    manifest = {"experiment_id": "EXP-ARCHIVE-0001", "experiment_status": "completed"}
    payload = {"runs": [{"seed": 42, "condition": "control"}]}
    (experiment / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (experiment / "DATA.json").write_text(json.dumps(payload), encoding="utf-8")

    service = ExperimentArchiveService(tmp_path)
    archived = service.archive_experiment("EXP-ARCHIVE-0001", "completed run cleanup")

    assert archived["experiment_id"] == "EXP-ARCHIVE-0001"
    assert not experiment.exists()
    archived_path = tmp_path / "archive" / "experiments" / "EXP-ARCHIVE-0001"
    assert (
        json.loads((archived_path / "DATA.json").read_text(encoding="utf-8")) == payload
    )
    assert service.list_archived()[0]["reason"] == "completed run cleanup"

    restored = service.restore_experiment("EXP-ARCHIVE-0001")

    assert restored == {
        "experiment_id": "EXP-ARCHIVE-0001",
        "archived": False,
        "restored": True,
    }
    assert (
        json.loads((experiment / "manifest.json").read_text(encoding="utf-8"))
        == manifest
    )
    assert json.loads((experiment / "DATA.json").read_text(encoding="utf-8")) == payload
    assert service.list_archived() == []
