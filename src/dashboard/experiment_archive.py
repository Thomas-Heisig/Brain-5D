"""Immutable archive operations for completed research experiments."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast


class ExperimentArchiveError(ValueError):
    """Raised when an experiment archive operation is unsafe or invalid."""


class ExperimentArchiveService:
    """Move complete experiment directories without changing their contents."""

    def __init__(self, research_root: Path) -> None:
        self.root = research_root
        self.experiments = research_root / "experiments"
        self.archive = research_root / "archive" / "experiments"

    def _validate_id(self, experiment_id: str) -> str:
        if not experiment_id or experiment_id in {".", ".."}:
            raise ExperimentArchiveError("experiment_id is required")
        if (
            Path(experiment_id).name != experiment_id
            or "/" in experiment_id
            or "\\" in experiment_id
        ):
            raise ExperimentArchiveError("invalid experiment_id")
        return experiment_id

    def list_archived(self) -> list[dict[str, Any]]:
        if not self.archive.is_dir():
            return []
        items: list[dict[str, Any]] = []
        for directory in sorted(self.archive.iterdir()):
            if not directory.is_dir():
                continue
            metadata_path = directory / "archive.json"
            metadata: dict[str, Any] = {}
            if metadata_path.is_file():
                try:
                    loaded = json.loads(metadata_path.read_text(encoding="utf-8"))
                    if isinstance(loaded, dict):
                        metadata = cast(dict[str, Any], loaded)
                except (OSError, json.JSONDecodeError):
                    metadata = {}
            items.append(
                {"experiment_id": directory.name, "archived": True, **metadata}
            )
        return items

    def archive_experiment(
        self, experiment_id: str, reason: str = ""
    ) -> dict[str, Any]:
        experiment_id = self._validate_id(experiment_id)
        source = self.experiments / experiment_id
        target = self.archive / experiment_id
        if not (source / "manifest.json").is_file():
            raise ExperimentArchiveError(f"experiment not found: {experiment_id}")
        if target.exists():
            raise ExperimentArchiveError(
                f"experiment already archived: {experiment_id}"
            )
        self.archive.mkdir(parents=True, exist_ok=True)
        archived_at = datetime.now(timezone.utc).isoformat()
        shutil.move(str(source), str(target))
        metadata = {
            "experiment_id": experiment_id,
            "archived_at": archived_at,
            "reason": reason.strip() or "manual archive",
            "original_path": f"experiments/{experiment_id}",
        }
        (target / "archive.json").write_text(
            json.dumps(metadata, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
        )
        return metadata

    def restore_experiment(self, experiment_id: str) -> dict[str, Any]:
        experiment_id = self._validate_id(experiment_id)
        source = self.archive / experiment_id
        target = self.experiments / experiment_id
        if not (source / "manifest.json").is_file():
            raise ExperimentArchiveError(
                f"archived experiment not found: {experiment_id}"
            )
        if target.exists():
            raise ExperimentArchiveError(
                f"active experiment already exists: {experiment_id}"
            )
        metadata_path = source / "archive.json"
        if metadata_path.exists():
            metadata_path.unlink()
        shutil.move(str(source), str(target))
        return {"experiment_id": experiment_id, "archived": False, "restored": True}
