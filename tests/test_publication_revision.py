"""Regression tests for edition integrity; fixtures are not scientific data."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from scripts.publication_revision import (
    EDITION,
    PUBLICATIONS,
    build_export,
    contained,
    verify_edition,
)


@pytest.fixture
def edition_root(tmp_path: Path) -> Path:
    """Build a small complete edition to exercise positive and negative paths."""
    folder = tmp_path / PUBLICATIONS / EDITION
    original = tmp_path / PUBLICATIONS / "reader"
    folder.mkdir(parents=True)
    original.mkdir()
    order = [f"section-{i:03d}.md" for i in range(51)]
    revised = [0, 1, 2, 3, 4, 6, 19, 40]
    for i, name in enumerate(order):
        text = f'<a id="test-{i}"></a>\n# Section {i}\nFixture text.\n'
        (folder / name).write_text(text, encoding="utf-8")
        if i < 46:
            (original / name).write_text(text, encoding="utf-8")
    toc = "\n".join(f"[Section]({name})" for name in order) + "\n"
    (folder / "README.md").write_text(toc, encoding="utf-8")
    (folder / "section-004.md").write_text(toc, encoding="utf-8")
    support = ["methodenpruefung.py", "methodenpruefung.json", "literatur_revision.bib"]
    source = Path(__file__).resolve().parents[1] / PUBLICATIONS / EDITION
    for name in support[:2]:
        shutil.copyfile(source / name, folder / name)
    (folder / support[2]).write_text("% fixture\n", encoding="utf-8")
    manifest = {
        "section_order": order,
        "section_count": 51,
        "revised_sections": [f"section-{i:03d}.md" for i in revised],
        "added_sections": order[46:],
        "inherited_reader": "../reader",
        "supporting_files": support,
        "automatic_evidence_promotion": False,
        "empirical_brain5d_experiments_executed_in_revision": False,
    }
    (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return tmp_path


def test_complete_edition_and_real_witnesses(edition_root: Path) -> None:
    result = verify_edition(edition_root)
    assert result["sections"] == 51
    assert result["inherited"] == 38
    assert result["witnesses"] == 28


def test_inherited_text_cannot_be_silently_changed(edition_root: Path) -> None:
    path = edition_root / PUBLICATIONS / EDITION / "section-005.md"
    path.write_text("Changed", encoding="utf-8")
    with pytest.raises(ValueError, match="Modified inherited"):
        verify_edition(edition_root)


def test_missing_chapter_is_rejected(edition_root: Path) -> None:
    (edition_root / PUBLICATIONS / EDITION / "section-050.md").unlink()
    with pytest.raises(ValueError, match="inventory"):
        verify_edition(edition_root)


@pytest.mark.parametrize("target", ["missing.md", "section-047.md#missing"])
def test_broken_links_and_anchors(edition_root: Path, target: str) -> None:
    path = edition_root / PUBLICATIONS / EDITION / "section-046.md"
    path.write_text(f"[Broken]({target})\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Broken"):
        verify_edition(edition_root)


def test_incomplete_toc_is_rejected(edition_root: Path) -> None:
    path = edition_root / PUBLICATIONS / EDITION / "README.md"
    path.write_text("# Incomplete\n", encoding="utf-8")
    with pytest.raises(ValueError, match="table of contents"):
        verify_edition(edition_root)


@pytest.mark.parametrize(
    "field",
    ["automatic_evidence_promotion", "empirical_brain5d_experiments_executed_in_revision"],
)
def test_scientific_status_cannot_be_promoted(edition_root: Path, field: str) -> None:
    path = edition_root / PUBLICATIONS / EDITION / "manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest[field] = True
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError):
        verify_edition(edition_root)


def test_report_is_recomputed_not_merely_trusted(edition_root: Path) -> None:
    path = edition_root / PUBLICATIONS / EDITION / "methodenpruefung.json"
    report = json.loads(path.read_text(encoding="utf-8"))
    report["preregistered"] = True
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    with pytest.raises(subprocess.CalledProcessError):
        verify_edition(edition_root)


def test_script_hash_is_verified(edition_root: Path) -> None:
    path = edition_root / PUBLICATIONS / EDITION / "methodenpruefung.py"
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="hash differ"):
        verify_edition(edition_root)


def test_export_preserves_all_sections_and_internal_links(edition_root: Path) -> None:
    text = build_export(edition_root, "a" * 40)
    assert text.count('<a id="edition-section-') == 51
    assert "](section-" not in text
    assert "](#edition-section-050)" in text
    assert "Derived export" in text


def test_export_requires_an_exact_commit(edition_root: Path) -> None:
    with pytest.raises(ValueError, match="exact Git commit"):
        build_export(edition_root, "main")


def test_paths_cannot_escape_repository(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Unsafe"):
        contained(tmp_path, tmp_path / ".." / "escape.md")
