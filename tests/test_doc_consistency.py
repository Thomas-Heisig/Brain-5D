"""Focused tests for the repository documentation consistency checker."""

from __future__ import annotations

from pathlib import Path

from scripts.check_doc_consistency import check_markdown_links


def test_markdown_link_checker_accepts_existing_local_target(tmp_path: Path) -> None:
    target = tmp_path / "target.md"
    source = tmp_path / "source.md"
    target.write_text("# target\n", encoding="utf-8")
    source.write_text("[target](target.md#section)\n", encoding="utf-8")

    assert check_markdown_links((source,), root=tmp_path) == []


def test_markdown_link_checker_reports_missing_target(tmp_path: Path) -> None:
    source = tmp_path / "source.md"
    source.write_text("[missing](missing.md)\n", encoding="utf-8")

    errors = check_markdown_links((source,), root=tmp_path)

    assert len(errors) == 1
    assert "missing link target: missing.md" in errors[0]


def test_markdown_link_checker_reports_repository_escape(tmp_path: Path) -> None:
    source = tmp_path / "source.md"
    source.write_text("[outside](../outside.md)\n", encoding="utf-8")

    errors = check_markdown_links((source,), root=tmp_path)

    assert len(errors) == 1
    assert "link escapes repository" in errors[0]
