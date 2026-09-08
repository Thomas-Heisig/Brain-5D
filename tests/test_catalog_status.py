"""Catalog metadata is bounded, read-only and independent of evidence promotion."""

import json
import shutil
from pathlib import Path

from src.research.catalog_status import question_facets
from src.research.registry import ResearchRegistry


def test_catalog_facets_preserve_evidence_boundary(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1] / "research"
    for folder in ("registry", "protocols", "preregistrations"):
        shutil.copytree(root / folder, tmp_path / folder)
    experiment = tmp_path / "experiments" / "EXP-FACET-001"
    experiment.mkdir(parents=True)
    (experiment / "manifest.json").write_text(
        json.dumps(
            {"research_questions": ["RQ-MSBA-E01"], "experiment_status": "completed"}
        )
    )
    registry = ResearchRegistry(tmp_path / "registry").load_all()
    rows = {row["id"]: row for row in question_facets(tmp_path, registry)}
    assert len(rows) == len(registry.questions)
    assert rows["RQ-MSBA-E01"]["operational"] is True
    assert rows["RQ-MSBA-E01"]["experiment_progress"] == "data_available"
    assert rows["RQ-MSBA-E01"]["evidence_status"] == "none"
    assert rows["RQ-DET-001"]["evidence_status"] == "review_required"
    assert rows["RQ-SNN-001"]["operational"] is True
    assert all(row["progress_is_not_evidence"] for row in rows.values())
