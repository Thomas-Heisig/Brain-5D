from pathlib import Path

from src.research.catalog_audit import audit_research_catalog
from src.research.registry import ResearchRegistry


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_catalog_audit_reports_unregistered_references(tmp_path: Path) -> None:
    registry_dir = tmp_path / "research" / "registry"
    registry_dir.mkdir(parents=True)
    _write(
        registry_dir / "questions.yaml",
        "- id: RQ-TEST-001\n  domain: Test\n  question: Registered?\n  relevance: test\n  hypotheses: [H-TEST-001-A]\n  status: open\n",
    )
    _write(
        registry_dir / "hypotheses.yaml",
        "- id: H-TEST-001-A\n  research_question: RQ-TEST-001\n  hypothesis: Registered hypothesis\n",
    )
    _write(tmp_path / "docs" / "notes.md", "RQ-TEST-001 RQ-MISSING-001 H-MISSING-001")

    registry = ResearchRegistry(registry_dir).load_all()
    audit = audit_research_catalog(tmp_path, registry)

    assert audit.missing_questions == ("RQ-MISSING-001",)
    assert audit.missing_hypotheses == ("H-MISSING-001",)
    assert not audit.clean


def test_repo_audit_recognizes_canonical_msba_entries() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit = audit_research_catalog(repo_root)

    assert "RQ-MSBA-E01" not in audit.missing_questions
    assert "H-MSBA-E01-A" not in audit.missing_hypotheses
