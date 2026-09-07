"""Read-only catalog facets; execution progress never grants evidence status."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, cast

from .protocol_registry import protocol_catalog
from .registry import ResearchRegistry

MAX_MANIFESTS = 4096
MAX_RECORD_BYTES = 262144
CATALOG_FACET_FIELDS = (
    "domain",
    "status",
    "evidence_status",
    "experiment_progress",
)


def _record(path: Path) -> dict[str, Any]:
    try:
        if path.is_symlink() or path.stat().st_size > MAX_RECORD_BYTES:
            return {}
        value: Any = json.loads(path.read_text(encoding="utf-8"))
        return cast(dict[str, Any], value) if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def question_facets(root: Path, registry: ResearchRegistry) -> list[dict[str, Any]]:
    """Join bounded manifest metadata with canonical questions and protocols.

    EVID files without a separately validated review remain legacy/unreviewed.
    This projection does not invoke promotion, modify the registry or claim
    that a completed run supports its hypothesis.
    """
    operational = {str(item["research_question"]) for item in protocol_catalog(root)}
    counts: dict[str, Counter[str]] = {key: Counter() for key in registry.questions}
    manifests = sorted((root / "experiments").glob("*/manifest.json"))
    scan_complete = len(manifests) <= MAX_MANIFESTS
    for path in manifests[:MAX_MANIFESTS]:
        record = _record(path)
        questions = record.get("research_questions", [])
        if not isinstance(questions, list):
            continue
        status = str(record.get("experiment_status", "unknown"))
        for question_id in cast(list[object], questions):
            if isinstance(question_id, str) and question_id in counts:
                counts[question_id][status] += 1
    evidence: dict[str, set[str]] = {key: set() for key in registry.questions}
    for question in registry.questions.values():
        evidence[question.id].update(question.evidence)
        for hypothesis in registry.hypotheses_for_question(question.id):
            evidence[question.id].update(hypothesis.evidence)
    for path in sorted((root / "registry" / "evidence").glob("EVID-*.json")):
        record = _record(path)
        hypothesis_id = record.get("hypothesis_id")
        linked_hypothesis = registry.hypotheses.get(str(hypothesis_id))
        if linked_hypothesis and linked_hypothesis.research_question in evidence:
            evidence[linked_hypothesis.research_question].add(
                str(record.get("evidence_id", path.stem))
            )
    result: list[dict[str, Any]] = []
    for question in registry.questions.values():
        progress = counts[question.id]
        state = "not_run"
        if progress:
            state = "data_available" if progress["completed"] else "incomplete"
            if progress["running"]:
                state = "running"
        result.append(
            {
                "id": question.id,
                "label": question.question,
                "domain": question.domain,
                "status": question.status,
                "operational": question.id in operational,
                "evidence_status": (
                    "review_required" if evidence[question.id] else "none"
                ),
                "evidence_ids": sorted(evidence[question.id]),
                "experiment_progress": state,
                "experiment_counts": dict(progress),
                "manifest_scan_complete": scan_complete,
                "progress_is_not_evidence": True,
            }
        )
    return result


def question_facet_options(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Return stable option values for the catalog's backend-owned facets."""
    return {
        field: sorted(
            {
                str(row[field])
                for row in rows
                if row.get(field) is not None and str(row[field])
            }
        )
        for field in CATALOG_FACET_FIELDS
    }
