from pathlib import Path

import pytest

from src.research_assistant.assistant import ResearchAssistant


def test_research_assistant_reads_registry_fragments_and_rejects_duplicates(
    tmp_path: Path,
) -> None:
    root = tmp_path / "research"
    registry = root / "registry"
    registry.mkdir(parents=True)
    (registry / "questions.yaml").write_text(
        "- id: RQ-BASE\n  question: base\n", encoding="utf-8"
    )
    (registry / "questions.extra.yaml").write_text(
        "- id: RQ-FRAGMENT\n  question: fragment\n", encoding="utf-8"
    )
    assistant = ResearchAssistant(root)
    rows = assistant._read_yaml_family("registry/questions.yaml")
    assert [row["id"] for row in rows] == ["RQ-BASE", "RQ-FRAGMENT"]
    (registry / "questions.duplicate.yaml").write_text(
        "- id: RQ-BASE\n  question: duplicate\n", encoding="utf-8"
    )
    with pytest.raises(
        ValueError, match="Duplicate research registry identifier RQ-BASE"
    ):
        assistant._read_yaml_family("registry/questions.yaml")
