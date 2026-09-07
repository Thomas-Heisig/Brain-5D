"""Publication discovery, immutable previews and complete derived reader tests."""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import pytest

from scripts.publication_bundle import (
    MASTER,
    PACKAGE,
    PUBLICATIONS,
    build_reader,
    digest,
    reader_files,
    safe_path,
    split_sections,
)
from src.dashboard.file_manager import FileManager
from src.dashboard.file_rendering import FilePreviewService, file_is_read_only
from src.dashboard.research_source import ResearchSource


def test_publication_discovery_and_tree(tmp_path: Path) -> None:
    root = tmp_path / "research"
    folder = root / "publications" / PACKAGE
    folder.mkdir(parents=True)
    (folder / MASTER).write_text("# Scientific publication\n", encoding="utf-8")
    source = ResearchSource(root)
    documents = source.list_documents()
    assert len(documents) == 1
    assert documents[0].category == "publications"
    assert documents[0].path == f"publications/{PACKAGE}/{MASTER}"
    categories = source.registry_summary()["categories"]
    assert isinstance(categories, dict)
    assert categories["publications"] == 1
    tree = FileManager(source, None, tmp_path / "docs").get_tree("research")
    assert any(child["name"] == "publications" for child in tree["children"])


@pytest.mark.parametrize("suffix", ["md", "json", "bib", "tex", "docx", "zip"])
def test_publication_paths_are_immutable(suffix: str) -> None:
    assert file_is_read_only("research", f"publications/{PACKAGE}/file.{suffix}")
    assert not file_is_read_only("docs", f"publications/file.{suffix}")


def test_publication_markdown_preview_is_read_only(tmp_path: Path) -> None:
    path = tmp_path / "publications" / "reader" / "README.md"
    path.parent.mkdir(parents=True)
    path.write_text("# Reader\n", encoding="utf-8")
    preview = FilePreviewService({"research": tmp_path}).preview(
        "research", "publications/reader/README.md"
    )
    assert preview["kind"] == "markdown"
    assert preview["read_only"] is True
    assert preview["editable"] is False
    assert preview["truncated"] is False


def test_publication_archive_preview(tmp_path: Path) -> None:
    path = tmp_path / "publications" / "archives" / "bundle.zip"
    path.parent.mkdir(parents=True)
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr("book.md", "# Publication\n")
    path.write_bytes(output.getvalue())
    preview = FilePreviewService({"research": tmp_path}).preview(
        "research", "publications/archives/bundle.zip"
    )
    assert preview["kind"] == "archive"
    assert preview["read_only"] is True
    assert preview["member_count"] == 1


def test_reader_preserves_sections_and_code_headings() -> None:
    text = '<a id="one"></a>\n\n# One\n\n```python\n# Not a chapter\n```\n\n<a id="two"></a>\n\n# Two\nEnd.\n'
    sections = split_sections(text)
    assert len(sections) == 2
    assert "".join(section[3] for section in sections) == text
    assert sections[1][3].startswith('<a id="two">')


def test_reader_rewrites_images_and_cross_chapter_links() -> None:
    source = b'<a id="one"></a>\n\n# One\n[Next](#two)\n![figure](abbildungen/image.png)\n\n<a id="two"></a>\n\n# Two\n'
    files = reader_files(source)
    first = files["section-000.md"].decode()
    assert "section-001.md#two" in first
    assert f"../{PACKAGE}/abbildungen/image.png" in first
    manifest = json.loads(files["manifest.json"])
    assert manifest["source_sha256"] == digest(source)
    assert manifest["section_count"] == 2


def test_reader_detects_stale_or_missing_parts(tmp_path: Path) -> None:
    snapshot = tmp_path / PUBLICATIONS / PACKAGE
    snapshot.mkdir(parents=True)
    (snapshot / MASTER).write_text("# One\nBody.\n# Two\nEnd.\n", encoding="utf-8")
    assert build_reader(tmp_path) == 2
    assert build_reader(tmp_path, check=True) == 2
    (tmp_path / PUBLICATIONS / "reader" / "section-001.md").write_text(
        "changed", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="Stale"):
        build_reader(tmp_path, check=True)


def test_reader_fails_instead_of_silently_truncating() -> None:
    with pytest.raises(ValueError, match="too large"):
        reader_files(b"# Oversized\n" + b"x" * 250000)


@pytest.mark.parametrize("path", ["../escape", "/absolute"])
def test_manifest_paths_cannot_escape(tmp_path: Path, path: str) -> None:
    with pytest.raises(ValueError, match="Unsafe"):
        safe_path(tmp_path, path)
