"""Review inbox aggregation for research artifacts.

The inbox is intentionally read-only. Decisions are still written through the
existing append-only human-review writers in ``research_assistant.airr``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast


def _json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return cast(dict[str, Any], value) if isinstance(value, dict) else None


def build_review_inbox(research_root: Path) -> dict[str, Any]:
    root = research_root.resolve()
    experiments = root / "experiments"
    items: list[dict[str, Any]] = []
    if not experiments.is_dir():
        return {"open": 0, "completed": 0, "items": []}

    completed = 0
    for report_path in sorted(experiments.glob("*/reports/AIRR-*.json")):
        if report_path.name.endswith(".review.json"):
            continue
        report = _json(report_path)
        if not report:
            continue
        experiment_id = report_path.parents[1].name
        report_id = str(report.get("report_id") or report_path.stem)
        review_path = report_path.with_name(f"{report_id}.review.json")
        if review_path.is_file():
            completed += 1
            continue
        if report.get("human_review_required") is not True:
            continue
        if report.get("status") != "review_pending":
            continue
        content_value = report.get("content")
        content = (
            cast(dict[str, Any], content_value)
            if isinstance(content_value, dict)
            else {}
        )
        items.append(
            {
                "kind": "airr",
                "experiment_id": experiment_id,
                "report_id": report_id,
                "artifact_path": str(report_path.relative_to(root)).replace("\\", "/"),
                "research_question_id": report.get("research_question_id"),
                "generated_at": report.get("generated_at"),
                "title": f"{experiment_id} · {report_id}",
                "summary": content.get("executive_summary"),
                "review_endpoint": f"/api/research/ai-reports/{experiment_id}/{report_id}/review",
            }
        )

    for target in sorted(experiments.glob("*/**/*")):
        if not target.is_file() or target.name.endswith(".review.json"):
            continue
        if target.suffix.lower() not in {".md", ".json"}:
            continue
        review_path = target.with_name(f"{target.name}.review.json")
        if review_path.is_file():
            completed += 1
            continue
        payload = _json(target) if target.suffix.lower() == ".json" else None
        explicit = bool(
            isinstance(payload, dict)
            and (
                payload.get("human_review") == "PENDING"
                or payload.get("human_review_status") in {"PENDING", "NOT_PERFORMED"}
                or payload.get("evidence_readiness") == "BLOCKED_HUMAN_REVIEW"
            )
        )
        if not explicit:
            continue
        relative = str(target.relative_to(root)).replace("\\", "/")
        items.append(
            {
                "kind": "artifact",
                "experiment_id": target.relative_to(experiments).parts[0],
                "artifact_path": relative,
                "title": target.name,
                "summary": "Explicit human review required by the artifact metadata.",
                "review_endpoint": "/api/research/reviews",
            }
        )

    items.sort(
        key=lambda item: (str(item.get("experiment_id")), str(item.get("title")))
    )
    return {"open": len(items), "completed": completed, "items": items}
