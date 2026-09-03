"""Contracts for the grounded Research Self-Knowledge chat."""

import pytest

from src.research_assistant.chat import ResearchChat
from src.research_assistant.contracts import AIExposure, AIInteractionRecord, CausalTaint


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
    assert metadata["ai_interaction"]["authority"] == "read_only"
    assert metadata["ai_interaction"]["exposure"] == "observer_only"
    assert metadata["ai_interaction"]["causal_effect"] == "OBSERVED"
    assert "RQ-1" in prompts[0] and "Brain-5D" in prompts[0]
    assert "never execute an experiment from free text" in prompts[0]
    assert "WEB SOURCES must never appear under EVIDENCE" in prompts[0]


def test_chat_rejects_empty_message() -> None:
    chat = ResearchChat(Source({}), Source({}), lambda prompt: (prompt, {}))
    with pytest.raises(ValueError, match="must not be empty"):
        chat.answer("  ")

def test_chat_context_labels_research_and_docs() -> None:
    chat = ResearchChat(Source({"research.md": "research"}), Source({"docs.md": "docs"}), lambda prompt: (prompt, {}))
    prompt = chat._prompt("Welche Quellen wurden verwendet?")
    assert "SCIENTIFIC RESEARCH SOURCES" in prompt
    assert "DOCUMENTATION SOURCES" in prompt


def test_chat_rejects_unknown_response_mode() -> None:
    chat = ResearchChat(Source({}), Source({}), lambda prompt: (prompt, {}), response_mode="brief")
    with pytest.raises(ValueError, match="Unsupported response mode"):
        chat.answer("Status?")


def test_ai_interaction_record_is_digest_only_and_json_compatible() -> None:
    record = AIInteractionRecord.create(
        role="research_ai",
        experiment_id="EXP-1",
        tick=12,
        input_value={"state": 1},
        prompt="Interpret the observation.",
        output_value={"assessment": "uncertain"},
        model_provenance={"provider": "ollama", "model": "test"},
        authority="read_only",
        exposure=AIExposure.OBSERVER_ONLY,
        causal_effect=CausalTaint.OBSERVED,
    )

    payload = record.to_dict()
    assert payload["exposure"] == "observer_only"
    assert payload["causal_effect"] == "OBSERVED"
    assert "Interpret the observation." not in record.to_json()
    assert len(record.input_digest) == 64
    assert len(record.prompt_digest) == 64
    assert len(record.output_digest) == 64


def test_ai_interaction_record_rejects_invalid_authority_and_tick() -> None:
    with pytest.raises(ValueError, match="authority must not be empty"):
        AIInteractionRecord.create(
            role="research_ai",
            experiment_id=None,
            tick=None,
            input_value=None,
            prompt="prompt",
            output_value=None,
            model_provenance={},
            authority=" ",
        )
    with pytest.raises(ValueError, match="tick must not be negative"):
        AIInteractionRecord.create(
            role="research_ai",
            experiment_id=None,
            tick=-1,
            input_value=None,
            prompt="prompt",
            output_value=None,
            model_provenance={},
            authority="read_only",
        )

