"""Read-only aggregation for experiment series and research organization."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast


class ExperimentOrganizerService:
    """Build series-level views without changing experiment artifacts."""

    def __init__(self, research_root: Path) -> None:
        self.root = research_root
        self.workflows = research_root / "workflows"

    def list_series(self) -> list[dict[str, Any]]:
        """Return workflow series with independently assessable child results."""
        if not self.workflows.is_dir():
            return []
        series: list[dict[str, Any]] = []
        for path in sorted(self.workflows.glob("*.json"), reverse=True):
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(raw, dict):
                continue
            data = cast(dict[str, Any], raw)
            results_value = data.get("results", [])
            if isinstance(results_value, list):
                result_items = cast(list[object], results_value)
                results = [
                    cast(dict[str, Any], item)
                    for item in result_items
                    if isinstance(item, dict)
                ]
            else:
                results = []
            completed = int(
                data.get(
                    "completed",
                    sum(item.get("status") == "completed" for item in results),
                )
            )
            failed = int(data.get("failed", len(results) - completed))
            status = (
                "completed"
                if completed > 0 and failed == 0
                else "partial" if completed else "failed"
            )
            assessment = (
                "HUMAN_REVIEW_REQUIRED"
                if status == "completed"
                else "EXECUTION_REVIEW_REQUIRED"
            )
            series.append(
                {
                    "series_id": str(data.get("workflow_id") or path.stem),
                    "created_at": str(data.get("created_at") or ""),
                    "protocols": cast(list[Any], data.get("protocols", [])),
                    "requested_ticks": data.get("requested_ticks"),
                    "seeds": data.get("seeds"),
                    "completed": completed,
                    "failed": failed,
                    "status": status,
                    "assessment_status": assessment,
                    "assessment_boundary": "technical execution only; no automatic evidence promotion",
                    "results": results,
                    "report": f"workflows/{path.name}",
                }
            )
        return series
