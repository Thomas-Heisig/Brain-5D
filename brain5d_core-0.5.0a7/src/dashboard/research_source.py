"""Read-only research registry and report source for the dashboard.

Exposes the Brain-5D Scientific Evidence Framework (B5D-SEF) artifacts
located under ``research/`` to the operator dashboard. The source is
strictly read-only and resolves paths defensively so a missing or
partially populated research tree never crashes the dashboard.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import JSONValue


@dataclass(frozen=True)
class ResearchDocument:
    """One research artifact exposed to the dashboard."""

    name: str
    path: str
    kind: str
    size_bytes: int
    category: str


class ResearchSource:
    """Read-only view over the ``research/`` directory tree.

    Categories:
        registry   — YAML registry files (questions, hypotheses, ...)
        generated  — auto-generated markdown reports
        experiments — experiment manifests
        literature  — BibTeX databases
        schemas     — JSON schemas
    """

    _CATEGORIES: tuple[str, ...] = (
        "registry",
        "generated",
        "experiments",
        "reports",
        "analysis",
        "benchmarks",
        "literature",
        "schemas",
    )

    def __init__(self, research_root: Path) -> None:
        self._root = research_root.resolve()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        """Return True when the research root exists and is a directory."""
        return self._root.is_dir()

    def root(self) -> Path:
        return self._root

    def list_documents(self) -> list[ResearchDocument]:
        """List all research artifacts grouped by category."""
        if not self.is_available():
            return []

        documents: list[ResearchDocument] = []
        for category in self._CATEGORIES:
            directory = self._root / category
            if not directory.is_dir():
                continue
            for entry in sorted(directory.rglob("*")):
                if not entry.is_file():
                    continue
                rel = entry.relative_to(self._root)
                documents.append(
                    ResearchDocument(
                        name=entry.name,
                        path=str(rel).replace("\\", "/"),
                        kind=entry.suffix.lstrip(".") or "file",
                        size_bytes=entry.stat().st_size,
                        category=category,
                    )
                )
        return documents

    def read_content(self, relative_path: str) -> str:
        """Read a research file as UTF-8 text with path-traversal protection."""
        resolved = self._safe_resolve(relative_path)
        if resolved is None:
            raise FileNotFoundError(f"Research document not found: {relative_path}")
        return resolved.read_text(encoding="utf-8")

    def read_bytes(self, relative_path: str) -> bytes:
        resolved = self._safe_resolve(relative_path)
        if resolved is None:
            raise FileNotFoundError(f"Research document not found: {relative_path}")
        return resolved.read_bytes()

    def registry_summary(self) -> dict[str, JSONValue]:
        """Return a compact summary of registry counts for the dashboard."""
        summary: dict[str, JSONValue] = {
            "available": self.is_available(),
            "root": str(self._root),
            "categories": {},
        }
        if not self.is_available():
            return summary

        counts: dict[str, JSONValue] = {}
        for category in self._CATEGORIES:
            directory = self._root / category
            if directory.is_dir():
                counts[category] = sum(
                    1 for entry in directory.rglob("*") if entry.is_file()
                )
            else:
                counts[category] = 0
        summary["categories"] = counts
        return summary

    def generated_reports(self) -> list[dict[str, JSONValue]]:
        """List auto-generated markdown reports with metadata."""
        directory = self._root / "generated"
        if not directory.is_dir():
            return []

        reports: list[dict[str, JSONValue]] = []
        for entry in sorted(directory.glob("*.md")):
            reports.append(
                {
                    "name": entry.stem,
                    "path": str(entry.relative_to(self._root)).replace("\\", "/"),
                    "size_bytes": entry.stat().st_size,
                }
            )
        return reports

    def ai_reports(
        self, experiment_id: str | None = None
    ) -> list[dict[str, JSONValue]]:
        """List canonical AIRR JSON/Markdown pairs without exposing write access."""
        directory = self._root / "reports"
        if not directory.is_dir():
            return []
        reports: list[dict[str, JSONValue]] = []
        for entry in sorted(directory.glob("*/AIRR-*.json")):
            if entry.name.endswith(".review.json"):
                continue
            current_experiment = entry.parent.name
            if experiment_id is not None and current_experiment != experiment_id:
                continue
            reports.append(
                {
                    "report_id": entry.stem,
                    "experiment_id": current_experiment,
                    "json_path": str(entry.relative_to(self._root)).replace("\\", "/"),
                    "markdown_path": str(
                        entry.with_suffix(".md").relative_to(self._root)
                    ).replace("\\", "/"),
                    "size_bytes": entry.stat().st_size,
                }
            )
        return reports

    def experiment_manifest(self, experiment_id: str) -> dict[str, JSONValue] | None:
        """Load one experiment manifest.json if present."""
        candidate = self._root / "experiments" / experiment_id / "manifest.json"
        if not candidate.is_file():
            return None
        try:
            data: Any = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        return data  # type: ignore[no-any-return]

    def list_experiments(self) -> list[dict[str, JSONValue]]:
        """List experiment directories that contain a manifest."""
        directory = self._root / "experiments"
        if not directory.is_dir():
            return []

        experiments: list[dict[str, JSONValue]] = []
        for entry in sorted(directory.iterdir()):
            manifest = entry / "manifest.json"
            if not manifest.is_file():
                continue
            try:
                data: Any = json.loads(manifest.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            experiments.append(
                {
                    "id": entry.name,
                    "path": str(entry.relative_to(self._root)).replace("\\", "/"),
                    "manifest": data,
                }
            )
        return experiments

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _safe_resolve(self, relative_path: str) -> Path | None:
        if not relative_path or ".." in relative_path:
            return None
        candidate = (self._root / relative_path).resolve()
        try:
            candidate.relative_to(self._root)
        except ValueError:
            return None
        if not candidate.is_file():
            return None
        return candidate


def create_research_source(research_root: Path | None) -> ResearchSource | None:
    """Create a ResearchSource if the root exists, else None."""
    if research_root is None or not research_root.exists():
        return None
    return ResearchSource(research_root)
