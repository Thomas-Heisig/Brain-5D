from pathlib import Path

from scripts.generate_catalog_audit_report import load_allow_list, report_data
from src.research.catalog_audit import audit_research_catalog
from src.research.registry import ResearchRegistry


def test_catalog_audit_report_accepts_explicit_historical_and_fixture_ids(
    tmp_path: Path,
) -> None:
    historical_id = "RQ-" + "HIST-001"
    historical_hypothesis_id = "H-" + "HIST-001-A"
    fixture_id = "RQ-" + "FIXTURE-001"
    registry_dir = tmp_path / "research" / "registry"
    registry_dir.mkdir(parents=True)
    (registry_dir / "questions.yaml").write_text("[]\n", encoding="utf-8")
    (registry_dir / "hypotheses.yaml").write_text("[]\n", encoding="utf-8")
    (tmp_path / "notes.md").write_text(
        " ".join((historical_id, historical_hypothesis_id, fixture_id)),
        encoding="utf-8",
    )
    allow_path = tmp_path / "allow.yaml"
    allow_path.write_text(
        f"historical_only:\n  {historical_id}: legacy design\n"
        f"test_fixtures:\n  {historical_hypothesis_id}: fixture\n"
        f"  {fixture_id}: fixture\n",
        encoding="utf-8",
    )

    audit = audit_research_catalog(tmp_path, ResearchRegistry(registry_dir).load_all())
    data = report_data(audit, load_allow_list(allow_path))

    assert data["status"] == "clean"
    assert data["disallowed_missing"] == {}


def test_catalog_audit_report_keeps_unknown_ids_blocking(tmp_path: Path) -> None:
    unknown_id = "RQ-" + "UNKNOWN-001"
    registry_dir = tmp_path / "research" / "registry"
    registry_dir.mkdir(parents=True)
    (registry_dir / "questions.yaml").write_text("[]\n", encoding="utf-8")
    (registry_dir / "hypotheses.yaml").write_text("[]\n", encoding="utf-8")
    (tmp_path / "notes.md").write_text(unknown_id, encoding="utf-8")
    allow_path = tmp_path / "allow.yaml"
    allow_path.write_text("historical_only: {}\ntest_fixtures: {}\n", encoding="utf-8")

    audit = audit_research_catalog(tmp_path, ResearchRegistry(registry_dir).load_all())
    data = report_data(audit, load_allow_list(allow_path))

    assert data["status"] == "failed"
    assert data["disallowed_missing"] == {unknown_id: ["notes.md"]}


def test_manuscript_proposal_cannot_silence_an_operational_reference(
    tmp_path: Path,
) -> None:
    identifier = "H-" + "SYN-01"
    registry_dir = tmp_path / "research" / "registry"
    registry_dir.mkdir(parents=True)
    (registry_dir / "questions.yaml").write_text("[]\n", encoding="utf-8")
    (registry_dir / "hypotheses.yaml").write_text("[]\n", encoding="utf-8")
    publication = tmp_path / "research" / "publications"
    publication.mkdir()
    (publication / "manuscript.md").write_text(identifier, encoding="utf-8")
    allow_path = registry_dir / "catalog_audit_allow_list.yaml"
    allow_path.write_text(
        f"publication_proposals:\n  {identifier}: proposed, not registered\n",
        encoding="utf-8",
    )
    registry = ResearchRegistry(registry_dir).load_all()
    allow = load_allow_list(allow_path)
    report = report_data(audit_research_catalog(tmp_path, registry), allow)
    assert report["status"] == "clean"
    assert (
        report["publication_proposals"][identifier]["status"]
        == "PROPOSED_NOT_REGISTERED"
    )
    assert identifier not in registry.hypotheses
    (tmp_path / "runnable_protocol.yaml").write_text(identifier, encoding="utf-8")
    report = report_data(audit_research_catalog(tmp_path, registry), allow)
    assert report["status"] == "failed"
    assert identifier in report["disallowed_missing"]
