"""Namespace exceptions must never hide real missing research entities."""

from pathlib import Path

import pytest

from scripts.generate_catalog_audit_report import report_data
from src.research.catalog_audit import audit_research_catalog
from src.research.registry import ResearchRegistry


@pytest.mark.parametrize("prefix", ["RQ-" + "EPI-1", "H-" + "EPI-1"])
@pytest.mark.parametrize(
    "extra_path", [None, "docs/claim.md", "research/protocols/run.json"]
)
def test_exact_namespace_is_scoped_to_its_defining_module(
    tmp_path: Path, prefix: str, extra_path: str | None
) -> None:
    registry_dir = tmp_path / "research/registry"
    registry_dir.mkdir(parents=True)
    (registry_dir / "questions.yaml").write_text("[]\n", encoding="utf-8")
    (registry_dir / "hypotheses.yaml").write_text("[]\n", encoding="utf-8")
    source = tmp_path / "src/research/cognition_governance.py"
    source.parent.mkdir(parents=True)
    source.write_text(f"PREFIXES = ({prefix!r},)\n", encoding="utf-8")
    if extra_path is not None:
        other = tmp_path / extra_path
        other.parent.mkdir(parents=True, exist_ok=True)
        other.write_text(prefix, encoding="utf-8")
    registry = ResearchRegistry(registry_dir).load_all()
    allow: dict[str, dict[str, str]] = {
        "historical_only": {},
        "test_fixtures": {},
        "publication_proposals": {},
    }
    result = report_data(audit_research_catalog(tmp_path, registry), allow)
    assert result["status"] == ("clean" if extra_path is None else "failed")
    assert (prefix in result["namespace_prefixes"]) == (extra_path is None)
    assert (prefix in result["disallowed_missing"]) == (extra_path is not None)
    assert registry.questions == {}
    assert registry.hypotheses == {}


def test_real_missing_entity_is_not_covered_by_a_namespace_prefix(tmp_path: Path) -> None:
    identifier = "RQ-" + "EPI-19999"
    registry_dir = tmp_path / "research/registry"
    registry_dir.mkdir(parents=True)
    source = tmp_path / "src/research/cognition_governance.py"
    source.parent.mkdir(parents=True)
    source.write_text(identifier, encoding="utf-8")
    registry = ResearchRegistry(registry_dir).load_all()
    allow: dict[str, dict[str, str]] = {
        "historical_only": {},
        "test_fixtures": {},
        "publication_proposals": {},
    }
    result = report_data(audit_research_catalog(tmp_path, registry), allow)
    assert result["status"] == "failed"
    assert identifier in result["disallowed_missing"]
    assert result["namespace_prefixes"] == {}
