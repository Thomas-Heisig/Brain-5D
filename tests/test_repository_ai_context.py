from __future__ import annotations

from pathlib import Path

from src.research_assistant.repository_context import RepositoryKnowledgeView


def test_repository_context_can_address_code_docs_and_research(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "research").mkdir()
    (tmp_path / "src" / "engine.py").write_text(
        "world_model_signal = 'transition predictor'\n", encoding="utf-8"
    )
    (tmp_path / "docs" / "architecture.md").write_text(
        "World model architecture and snapshot contract.\n", encoding="utf-8"
    )
    (tmp_path / "research" / "question.json").write_text(
        '{"question":"world model prediction"}\n', encoding="utf-8"
    )

    result = RepositoryKnowledgeView(tmp_path).retrieve("world model prediction")

    assert result.indexed_files == 3
    assert "src/engine.py" in result.selected_files
    assert "docs/architecture.md" in result.selected_files
    assert "research/question.json" in result.selected_files
    assert "REPOSITORY READ-ONLY RETRIEVAL" in result.text
    assert len(result.digest) == 64


def test_repository_context_excludes_secrets_and_bounds_large_content(
    tmp_path: Path,
) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / ".env").write_text("TOKEN=do-not-read\n", encoding="utf-8")
    (tmp_path / "src" / "large.md").write_text("needle " * 2000, encoding="utf-8")
    view = RepositoryKnowledgeView(
        tmp_path,
        max_file_bytes=128,
        per_file_chars=32,
        max_context_chars=2000,
    )

    result = view.retrieve("needle token")

    assert ".env" not in result.selected_files
    assert "do-not-read" not in result.text
    assert result.omitted_large_files == 1
    assert "binary_or_large_index_only=true" in result.text
    assert len(result.text) <= 2000


def test_repository_ai_does_not_read_private_review_exports_or_symlinks(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    private = root / "review_private"
    private.mkdir()
    (private / "participant.json").write_text('"PRIVATE_REVIEW_MARKER"')
    # A misfiled plaintext questionnaire export must also be excluded.
    (root / "export.json").write_text(
        '{"instrument_sha256":"fake", "participant_code":"PRIVATE_REVIEW_MARKER", "answers":{}}'
    )
    outside = tmp_path / "outside.txt"
    outside.write_text("PRIVATE_REVIEW_MARKER")
    link = root / "linked.txt"
    try:
        link.symlink_to(outside)
    except OSError:
        pass  # Other privacy assertions remain active without symlink capability.
    result = RepositoryKnowledgeView(root).retrieve("PRIVATE_REVIEW_MARKER")
    assert "PRIVATE_REVIEW_MARKER" not in result.text
    assert "export.json" not in result.selected_files
    assert "linked.txt" not in result.selected_files
    assert not any(path.startswith("review_private/") for path in result.selected_files)
