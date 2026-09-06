from pathlib import Path

from src.research.catalog_audit import audit_research_catalog, main
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


def test_catalog_audit_cli_writes_machine_readable_report(tmp_path: Path) -> None:
    registry_dir = tmp_path / "research" / "registry"
    registry_dir.mkdir(parents=True)
    _write(
        registry_dir / "questions.yaml",
        "- id: RQ-TEST-001\n  domain: Test\n  question: Registered?\n  relevance: test\n",
    )
    _write(
        registry_dir / "hypotheses.yaml",
        "- id: H-TEST-001-A\n  research_question: RQ-TEST-001\n  hypothesis: Registered\n",
    )
    _write(tmp_path / "docs" / "notes.md", "RQ-TEST-001 H-TEST-001-A")
    output = tmp_path / "artifacts" / "research-catalog-audit.json"

    assert main(["--repo-root", str(tmp_path), "--output", str(output)]) == 0

    report = output.read_text(encoding="utf-8")
    assert '"clean": true' in report
    assert '"missing_questions": []' in report
    assert '"missing_hypotheses": []' in report


def test_catalog_audit_allowlist_requires_kind_and_reason(tmp_path: Path) -> None:
    registry_dir = tmp_path / "research" / "registry"
    registry_dir.mkdir(parents=True)
    _write(
        registry_dir / "questions.yaml",
        "- id: RQ-TEST-001\n  domain: Test\n  question: Registered?\n  relevance: test\n",
    )
    _write(
        registry_dir / "hypotheses.yaml",
        "- id: H-TEST-001-A\n  research_question: RQ-TEST-001\n  hypothesis: Registered\n",
    )
    _write(tmp_path / "docs" / "notes.md", "RQ-HIST-001 H-HIST-001-A")
    _write(
        registry_dir / "catalog_audit_allowlist.yaml",
        "- id: RQ-HIST-001\n  kind: question\n  reason: historical fixture\n"
        "- id: H-HIST-001-A\n  kind: hypothesis\n  reason: negative fixture\n",
    )

    audit = audit_research_catalog(tmp_path)

    assert audit.clean
    assert audit.missing_questions == ()
    assert audit.missing_hypotheses == ()
    assert audit.allowlisted_questions == ("RQ-HIST-001",)
    assert audit.allowlisted_hypotheses == ("H-HIST-001-A",)
