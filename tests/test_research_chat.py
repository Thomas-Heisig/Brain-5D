"""Contracts for the grounded Research Self-Knowledge chat."""

import pytest

from src.research_assistant.chat import ResearchChat


class Doc:
    def __init__(self, path: str, kind: str = "md") -> None:
        self.path = path
        self.kind = kind
        self.file_type = type("FileType", (), {"value": "markdown"})()


class Source:
    def __init__(self, files: dict[str, str]) -> None:
        self.files = files

    def list_documents(self, recursive: bool = False) -> list[Doc]:
        del recursive
        return [Doc(path) for path in self.files]

    def read_content(self, relative_path: str) -> str:
        return self.files[relative_path]


def test_chat_prompt_contains_research_and_docs_and_forbids_execution() -> None:
    prompts: list[str] = []

    def backend(prompt: str) -> tuple[str, dict[str, str | float]]:
        prompts.append(prompt)
        return "grounded answer", {"provider": "test"}

    research = Source({"registry/questions.yaml": "RQ-1"})
    docs = Source({"README.md": "Brain-5D"})
    chat = ResearchChat(research, docs, backend)
    answer, metadata = chat.answer("What is the current research status?")

    assert answer == "grounded answer"
    assert metadata["provider"] == "test"
    assert "RQ-1" in prompts[0] and "Brain-5D" in prompts[0]
    assert "never execute an experiment from free text" in prompts[0]
    assert "WEB SOURCES must never appear under EVIDENCE" in prompts[0]


def test_chat_rejects_empty_message() -> None:
    chat = ResearchChat(Source({}), Source({}), lambda prompt: (prompt, {}))
    with pytest.raises(ValueError, match="must not be empty"):
        chat.answer("  ")
