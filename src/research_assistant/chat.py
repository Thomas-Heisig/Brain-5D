"""Bounded research chat with read-only knowledge and explicit run actions."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, Protocol


class _ResearchDocument(Protocol):
    path: str
    kind: str


class _ResearchSource(Protocol):
    def list_documents(self) -> Sequence[_ResearchDocument]: ...
    def read_content(self, relative_path: str) -> str: ...


class _DocDocument(Protocol):
    path: str
    file_type: Any


class _DocsSource(Protocol):
    def list_documents(self, recursive: bool = False) -> Sequence[_DocDocument]: ...
    def read_content(self, path: str) -> str: ...

ChatBackend = Callable[[str], tuple[str, dict[str, str | float]]]


@dataclass(frozen=True, slots=True)
class ResearchChat:
    """Construct grounded prompts; no chat response has mutation authority."""

    research: _ResearchSource
    docs: _DocsSource
    backend: ChatBackend
    max_context_chars: int = 24_000
    system_context: str = ""

    def answer(self, message: str) -> tuple[str, dict[str, str | float]]:
        question = message.strip()
        if not question:
            raise ValueError("Chat message must not be empty.")
        prompt = self._prompt(question)
        return self.backend(prompt)

    def _prompt(self, message: str) -> str:
        context = self._context()
        if self.system_context:
            context = f"SYSTEM READ-ONLY CONTEXT:\n{self.system_context}\n\n{context}"
        return (
            "You are the Brain-5D Research Self-Knowledge Assistant.\n"
            "You are an AI assistant, not a person and not a trained researcher.\n"
            "Answer only from the supplied repository context and cite exact paths.\n"
            "Return clean Markdown only, using short paragraphs, headings, and bullet lists.\n"
            "For research questions use exactly these headings when relevant: ## DATA, ## EVIDENCE, ## AI interpretation, ## Human conclusion.\n"
            "Do not use horizontal rules, decorative emojis, or raw JSON unless requested.\n"
            "Clearly distinguish DATA, EVIDENCE, AI interpretation, and human conclusion.\n"
            "Never claim that AI output is evidence. Never invent values or experiment results.\n"
            "You may explain registered experiments, but never execute an experiment from free text.\n"
            f"User question: {message}\n\nRepository context:\n{context}"
        )

    def _context(self) -> str:
        chunks: list[str] = []
        for document in self.research.list_documents():
            if document.kind not in {"md", "json", "yaml", "yml", "txt"}:
                continue
            try:
                content = self.research.read_content(document.path)
            except (OSError, UnicodeError):
                continue
            chunks.append(f"[{document.path}]\n{content[:4000]}")
        for document in self.docs.list_documents(recursive=True):
            if document.file_type.value not in {"markdown", "text", "json", "yaml"}:
                continue
            try:
                content = self.docs.read_content(document.path)
            except (OSError, UnicodeError, ValueError):
                continue
            chunks.append(f"[docs/{document.path}]\n{content[:4000]}")
        return "\n\n".join(chunks)[: self.max_context_chars]


def chat_backend_from_text_backend(backend: Callable[[str], Any]) -> ChatBackend:
    """Adapt a text backend that returns either text or ``(text, metadata)``."""
    def call(prompt: str) -> tuple[str, dict[str, str | float]]:
        result = backend(prompt)
        if isinstance(result, tuple) and len(result) == 2:
            text: Any = result[0]
            metadata: Any = result[1]
            if isinstance(text, str) and isinstance(metadata, dict):
                return text, {str(key): value for key, value in metadata.items() if isinstance(value, (str, float))}
        if isinstance(result, str):
            return result, {}
        raise ValueError("Chat backend must return text or (text, metadata).")
    return call
