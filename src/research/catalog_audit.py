"""Repository-wide audit for research-question and hypothesis references.

The audit is read-only. It discovers RQ/H identifiers in text files and compares
them with the canonical ResearchRegistry. Historical experiment/report files are
reported as references but are never rewritten or promoted automatically.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from .registry import ResearchRegistry

RQ_PATTERN = re.compile(r"\bRQ-[A-Z0-9]+(?:-[A-Z0-9]+)+\b")
H_PATTERN = re.compile(r"\bH-[A-Z0-9]+(?:-[A-Z0-9]+)+\b")
_TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".yaml",
    ".yml",
    ".json",
    ".py",
    ".js",
    ".html",
    ".toml",
}
_SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "build"}


@dataclass(frozen=True, slots=True)
class ResearchReference:
    identifier: str
    kind: str
    path: str

    def to_dict(self) -> dict[str, str]:
        return {
            "identifier": self.identifier,
            "kind": self.kind,
            "path": self.path,
        }


@dataclass(frozen=True, slots=True)
class ResearchCatalogAudit:
    question_references: tuple[ResearchReference, ...]
    hypothesis_references: tuple[ResearchReference, ...]
    missing_questions: tuple[str, ...]
    missing_hypotheses: tuple[str, ...]
    link_issues: tuple[dict[str, str], ...]

    @property
    def clean(self) -> bool:
        problems = (
            self.missing_questions,
            self.missing_hypotheses,
            self.link_issues,
        )
        return not any(problems)

    def to_dict(self) -> dict[str, object]:
        question_refs = [item.to_dict() for item in self.question_references]
        hypothesis_refs = [item.to_dict() for item in self.hypothesis_references]
        return {
            "clean": self.clean,
            "question_reference_count": len(self.question_references),
            "hypothesis_reference_count": len(self.hypothesis_references),
            "missing_questions": list(self.missing_questions),
            "missing_hypotheses": list(self.missing_hypotheses),
            "link_issues": list(self.link_issues),
            "question_references": question_refs,
            "hypothesis_references": hypothesis_refs,
        }


def audit_research_catalog(
    repo_root: Path,
    registry: ResearchRegistry | None = None,
) -> ResearchCatalogAudit:
    """Scan repository text and compare discovered identifiers with the registry."""

    root = repo_root.resolve()
    registry_dir = root / "research" / "registry"
    active_registry = registry or ResearchRegistry(registry_dir).load_all()
    question_refs: list[ResearchReference] = []
    hypothesis_refs: list[ResearchReference] = []
    found_questions: set[str] = set()
    found_hypotheses: set[str] = set()

    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in _TEXT_SUFFIXES:
            continue
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        relative = path.relative_to(root).as_posix()
        for identifier in sorted(set(RQ_PATTERN.findall(text))):
            found_questions.add(identifier)
            question_refs.append(ResearchReference(identifier, "question", relative))
        for identifier in sorted(set(H_PATTERN.findall(text))):
            found_hypotheses.add(identifier)
            hypothesis_refs.append(
                ResearchReference(identifier, "hypothesis", relative)
            )

    known_questions = set(active_registry.questions)
    known_hypotheses = set(active_registry.hypotheses)
    missing_questions = tuple(sorted(found_questions - known_questions))
    missing_hypotheses = tuple(sorted(found_hypotheses - known_hypotheses))
    return ResearchCatalogAudit(
        question_references=tuple(question_refs),
        hypothesis_references=tuple(hypothesis_refs),
        missing_questions=missing_questions,
        missing_hypotheses=missing_hypotheses,
        link_issues=tuple(active_registry.link_issues()),
    )


__all__ = [
    "H_PATTERN",
    "RQ_PATTERN",
    "ResearchCatalogAudit",
    "ResearchReference",
    "audit_research_catalog",
]


def main(argv: list[str] | None = None) -> int:
    """Write a repository-wide catalog audit report for CI or local review."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root to scan (default: current directory).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="JSON report path to write.",
    )
    parser.add_argument(
        "--fail-on-findings",
        action="store_true",
        help="Return a non-zero exit code when the audit is not clean.",
    )
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()
    audit = audit_research_catalog(repo_root)
    report = {
        "repo_root": str(repo_root),
        "audit": audit.to_dict(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "Research catalog audit: "
        f"clean={audit.clean}, missing_questions={len(audit.missing_questions)}, "
        f"missing_hypotheses={len(audit.missing_hypotheses)}, "
        f"link_issues={len(audit.link_issues)}"
    )
    if args.fail_on_findings and not audit.clean:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
