"""Public naming migration regression checks; never scientific evidence."""

from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

import pytest

from scripts.publication_naming import export_markdown, verify
from src.identity import (
    PROJECT_NAME,
    PROJECT_SUBTITLE_DE,
    PROJECT_TITLE,
    legacy_environment_aliases,
)
from src.version import (
    BRAIN5D_VERSION,
    BRAIN5D_VERSION_DISPLAY,
    MHRN_VERSION,
    MHRN_VERSION_DISPLAY,
)

ROOT = Path(__file__).resolve().parents[1]


def test_current_identity_and_distribution() -> None:
    identity: dict[str, Any] = json.loads(
        (ROOT / "project_identity.json").read_text(encoding="utf-8")
    )
    assert PROJECT_NAME == identity["project"]["short_name"] == "MHRN"
    assert PROJECT_TITLE == identity["project"]["title_en"]
    assert PROJECT_SUBTITLE_DE == identity["project"]["subtitle_de"]
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]
    assert project["name"] == "mhrn-core"
    assert project["version"] == MHRN_VERSION == BRAIN5D_VERSION
    assert MHRN_VERSION_DISPLAY == BRAIN5D_VERSION_DISPLAY


@pytest.mark.parametrize("new_value", ["", "0", "1", "custom"])
def test_environment_new_prefix_precedes_legacy_without_logging(new_value: str) -> None:
    environment = {
        "MHRN_TEST": new_value,
        "BRAIN5D_TEST": "legacy",
        "OTHER": "untouched",
    }
    assert legacy_environment_aliases(environment) == {"BRAIN5D_TEST": new_value}
    assert environment["BRAIN5D_TEST"] == "legacy"
    assert legacy_environment_aliases({"BRAIN5D_ONLY": "retained"}) == {}


def test_current_edition_and_historical_integrity() -> None:
    result = verify(ROOT)
    assert result["sections"] == 57
    assert result["historical_files"] > 41


def test_full_export_contains_bilingual_title_and_all_chapters() -> None:
    text = export_markdown(ROOT, "a" * 40)
    assert "Recursive Epistemics in Embodied Spiking Neural Architectures" in text
    assert "Rekursive Epistemik in verkörperten" in text
    for index in range(57):
        assert f'id="edition-section-{index:03d}"' in text
    assert "](section-" not in text


def test_export_rejects_unpinned_revision() -> None:
    with pytest.raises(ValueError, match="exact source commit"):
        export_markdown(ROOT, "main")


def test_both_launcher_names_remain_callable() -> None:
    for name in ("mhrn_launcher.py", "brain5d_launcher.py"):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / name), "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        assert "start" in result.stdout


def test_visible_dashboard_names_and_hf_card() -> None:
    html = (ROOT / "src/dashboard/static/index.html").read_text(encoding="utf-8")
    assert "MHRN Operator Dashboard" in html
    assert PROJECT_TITLE in html
    assert PROJECT_SUBTITLE_DE in html
    card = (ROOT / "HF_README.md").read_text(encoding="utf-8")
    assert "title: MHRN" in card
    assert "library_name: mhrn-core" in card
    assert "# " + PROJECT_TITLE in card
    assert "## " + PROJECT_SUBTITLE_DE in card


def test_no_scientific_promotion_by_renaming() -> None:
    identity: dict[str, Any] = json.loads(
        (ROOT / "project_identity.json").read_text(encoding="utf-8")
    )
    assert identity["scientific_scope"]["renaming_is_new_evidence"] is False
    assert identity["compatibility"]["unchanged_storage_format"] == ".b5d"
    manifest: dict[str, Any] = json.loads(
        (
            ROOT
            / "research/publications/2026-09-08_recursive-epistemics_v1.3/manifest.json"
        ).read_text(encoding="utf-8")
    )
    assert manifest["new_empirical_findings"] is False
    assert manifest["automatic_evidence_promotion"] is False


def test_configuration_alias_preserves_existing_class_identity() -> None:
    from src.core.network import Brain5DConfig, MHRNConfig

    assert MHRNConfig is Brain5DConfig
    assert MHRNConfig(dimensions=(2, 2, 2, 2, 2)).dimensions == (2, 2, 2, 2, 2)


def test_publication_citation_distinguishes_package_from_treatise() -> None:
    folder = ROOT / "research/publications/2026-09-08_recursive-epistemics_v1.3"
    citation = json.loads((folder / "CITATION.cff").read_text(encoding="utf-8"))
    identity = json.loads((ROOT / "project_identity.json").read_text(encoding="utf-8"))
    assert citation["type"] == "software"
    assert citation["preferred-citation"]["type"] == "report"
    assert (
        citation["preferred-citation"]["title"] == identity["publication"]["title_en"]
    )
    assert (
        citation["preferred-citation"]["abstract"]
        == identity["publication"]["subtitle_de"]
    )
