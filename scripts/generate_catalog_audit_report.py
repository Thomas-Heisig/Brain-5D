"""Generate the CI report for the repository-wide RQ/H catalog audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.research.catalog_audit import (  # noqa: E402
    ResearchCatalogAudit,
    audit_research_catalog,
)

ALLOW_LIST_PATH = REPO_ROOT / "research" / "registry" / "catalog_audit_allow_list.yaml"
REPORT_DIR = REPO_ROOT / "research" / "generated"
MARKDOWN_PATH = REPORT_DIR / "CATALOG_AUDIT_REPORT.md"
JSON_PATH = REPORT_DIR / "CATALOG_AUDIT_REPORT.json"


def load_allow_list(path: Path) -> dict[str, dict[str, str]]:
    raw: Any = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError("Catalog audit allow-list must be a mapping")
    result: dict[str, dict[str, str]] = {}
    for category in ("historical_only", "test_fixtures"):
        entries = raw.get(category, {})
        if not isinstance(entries, dict):
            raise ValueError(f"Allow-list category must be a mapping: {category}")
        result[category] = {}
        for identifier, reason in entries.items():
            if not isinstance(identifier, str) or not isinstance(reason, str):
                raise ValueError(f"Invalid allow-list entry in {category}")
            if not reason.strip():
                raise ValueError(f"Allow-list reason is empty: {identifier}")
            result[category][identifier] = reason
    return result


def _references_for(audit: ResearchCatalogAudit, identifier: str) -> list[str]:
    references = (*audit.question_references, *audit.hypothesis_references)
    return sorted({item.path for item in references if item.identifier == identifier})


def report_data(
    audit: ResearchCatalogAudit, allow_list: dict[str, dict[str, str]]
) -> dict[str, Any]:
    missing = set(audit.missing_questions) | set(audit.missing_hypotheses)
    historical = set(allow_list["historical_only"])
    fixtures = set(allow_list["test_fixtures"])
    stale_allow_list = sorted((historical | fixtures) - missing)
    disallowed = sorted(missing - historical - fixtures)
    return {
        "status": "clean" if not disallowed and not audit.link_issues else "failed",
        "audit": {
            "clean": audit.clean,
            "question_reference_count": len(audit.question_references),
            "hypothesis_reference_count": len(audit.hypothesis_references),
            "missing_questions": list(audit.missing_questions),
            "missing_hypotheses": list(audit.missing_hypotheses),
            "link_issues": list(audit.link_issues),
        },
        "historical_only": {
            identifier: {
                "reason": allow_list["historical_only"][identifier],
                "references": _references_for(audit, identifier),
            }
            for identifier in sorted(missing & historical)
        },
        "test_fixtures": {
            identifier: {
                "reason": allow_list["test_fixtures"][identifier],
                "references": _references_for(audit, identifier),
            }
            for identifier in sorted(missing & fixtures)
        },
        "disallowed_missing": {
            identifier: _references_for(audit, identifier) for identifier in disallowed
        },
        "stale_allow_list": stale_allow_list,
    }


def _markdown_report(data: dict[str, Any]) -> str:
    audit = data["audit"]
    lines = [
        "# Repository Catalog Audit Report",
        "",
        f"**Status:** `{data['status'].upper()}`",
        "",
        "The canonical ResearchRegistry remains authoritative. Historical/design references and test-only fixtures are listed with explicit reasons; an unknown missing identifier fails CI.",
        "",
        "## Summary",
        f"- Question references: {audit['question_reference_count']}",
        f"- Hypothesis references: {audit['hypothesis_reference_count']}",
        f"- Missing questions: {len(audit['missing_questions'])}",
        f"- Missing hypotheses: {len(audit['missing_hypotheses'])}",
        f"- Registry link issues: {len(audit['link_issues'])}",
        f"- Disallowed missing identifiers: {len(data['disallowed_missing'])}",
        "",
    ]
    for title, key in (
        ("Historical/design references", "historical_only"),
        ("Test fixtures", "test_fixtures"),
    ):
        lines.extend([f"## {title}", ""])
        entries = data[key]
        if not entries:
            lines.append("None.")
        else:
            for identifier, details in entries.items():
                sources = ", ".join(f"`{path}`" for path in details["references"])
                lines.append(
                    f"- `{identifier}`: {details['reason']} Sources: {sources}"
                )
        lines.append("")
    lines.extend(["## Failures", ""])
    if data["disallowed_missing"]:
        for identifier, references in data["disallowed_missing"].items():
            source_list = ", ".join(f"`{path}`" for path in references)
            lines.append(f"- `{identifier}` in {source_list}")
    else:
        lines.append("None.")
    if audit["link_issues"]:
        lines.extend(["", "Registry link issues:"])
        lines.extend(f"- {issue}" for issue in audit["link_issues"])
    if data["stale_allow_list"]:
        lines.extend(["", "Stale allow-list entries:"])
        lines.extend(f"- `{identifier}`" for identifier in data["stale_allow_list"])
    lines.append("")
    return "\n".join(lines)


def generate_report(
    repo_root: Path = REPO_ROOT,
    allow_list_path: Path = ALLOW_LIST_PATH,
    report_dir: Path = REPORT_DIR,
) -> int:
    """Write Markdown/JSON reports and return a CI-compatible exit code."""
    allow_list = load_allow_list(allow_list_path)
    audit = audit_research_catalog(repo_root)
    data = report_data(audit, allow_list)
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / MARKDOWN_PATH.name).write_text(
        _markdown_report(data), encoding="utf-8"
    )
    (report_dir / JSON_PATH.name).write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Catalog audit: {data['status']}")
    return 0 if data["status"] == "clean" and not data["stale_allow_list"] else 1


if __name__ == "__main__":
    raise SystemExit(generate_report())
