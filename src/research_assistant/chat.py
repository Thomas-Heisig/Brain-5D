"""Bounded research chat with read-only knowledge and explicit run actions."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, Protocol, cast

from .contracts import AIExposure, AIInteractionRecord, CausalTaint
from .firewall import ScientificAIFirewall
from .governance import KnowledgeOrigin, NetworkMode, RetrievalRecord


class _ResearchDocument(Protocol):
    path: str
    kind: str


class _ResearchSource(Protocol):
    def list_documents(self) -> Sequence[_ResearchDocument]: ...
    def read_content(self, path: str) -> str: ...


class _DocDocument(Protocol):
    path: str
    file_type: Any


class _DocsSource(Protocol):
    def list_documents(self, recursive: bool = False) -> Sequence[_DocDocument]: ...
    def read_content(self, path: str) -> str: ...

ChatBackend = Callable[[str], tuple[str, dict[str, Any]]]


@dataclass(frozen=True, slots=True)
class ResearchChat:
    """Construct grounded prompts; no chat response has mutation authority."""

    research: _ResearchSource
    docs: _DocsSource
    backend: ChatBackend
    max_context_chars: int = 24_000
    system_context: str = ""
    web_context: str = ""
    system_prompt: str = ""
    conversation_context: str = ""
    handoff_prompt: str = ""
    response_mode: str = "detailed"
    firewall: ScientificAIFirewall = ScientificAIFirewall()

    def answer(self, message: str) -> tuple[str, dict[str, Any]]:
        question = message.strip()
        if not question:
            raise ValueError("Chat message must not be empty.")
        if self.response_mode not in {"short", "detailed", "scientific"}:
            raise ValueError("Unsupported response mode.")
        self.firewall.assert_read_only()
        self.firewall.authorize("interpret")
        prompt = self._prompt(question)
        answer, metadata = self.backend(prompt)
        retrieval = self._retrieval_record()
        metadata = {**metadata, "retrieval": retrieval.to_dict()}
        interaction = AIInteractionRecord.create(
            role="research_ai",
            experiment_id=None,
            tick=None,
            input_value=question,
            prompt=prompt,
            output_value=answer,
            model_provenance=metadata,
            authority="read_only",
            exposure=AIExposure.OBSERVER_ONLY,
            causal_effect=CausalTaint.OBSERVED,
        )
        return answer, {**metadata, "ai_interaction": interaction.to_dict()}

    def _retrieval_record(self) -> RetrievalRecord:
        context = self._context()
        web_enabled = bool(self.web_context.strip())
        mode = NetworkMode.LIVE_NETWORK if web_enabled else NetworkMode.FROZEN_CORPUS
        source_count = sum(
            1
            for document in self.research.list_documents()
            if document.kind in {"md", "json", "yaml", "yml", "txt"}
        )
        source_count += sum(
            1
            for document in self.docs.list_documents(recursive=True)
            if document.file_type.value in {"markdown", "text", "json", "yaml"}
        )
        if web_enabled:
            source_count += 1
        snapshot_digest = hashlib.sha256(
            json.dumps(
                {"context": context, "web_context": self.web_context},
                sort_keys=True,
                ensure_ascii=True,
            ).encode("utf-8")
        ).hexdigest()
        return RetrievalRecord(
            enabled=True,
            mode=mode,
            snapshot_digest=snapshot_digest,
            source_count=source_count,
            knowledge_origin=(
                KnowledgeOrigin.EXTERNAL_RETRIEVAL
                if web_enabled
                else KnowledgeOrigin.SYSTEM_STATE
            ),
        )

    def _prompt(self, message: str) -> str:
        context = self._context()
        if self.system_context:
            context = f"SYSTEM READ-ONLY CONTEXT:\n{self.system_context}\n\n{context}"
        if self.web_context:
            context = f"WEB SOURCES (external and unverified):\n{self.web_context}\n\n{context}"
        if self.conversation_context:
            context = f"CHAT HIERARCHY (conversation context, not evidence):\n{self.conversation_context}\n\n{context}"
        if self.handoff_prompt.strip():
            context = f"HANDOFF INSTRUCTIONS (editable operator context, not evidence):\n{self.handoff_prompt.strip()}\n\n{context}"
        mode_instructions = {
            "short": "Response mode: SHORT. Answer in at most 5 concise bullet points. Lead with the direct answer and omit background.",
            "detailed": "Response mode: DETAILED. Explain the answer with relevant context, status, sources, uncertainty, and a concise conclusion.",
            "scientific": "Response mode: SCIENTIFIC. Separate research question, method/protocol, DATA, EVIDENCE, limitations, AI interpretation, and human conclusion. Never upgrade inconclusive or untested status.",
        }[self.response_mode]
        return (
            f"{self.system_prompt.strip()}\n" if self.system_prompt.strip() else ""
        ) + (
            "You are the Brain-5D Research Self-Knowledge Assistant.\n"
            "You are an AI assistant, not a person and not a trained researcher.\n"
            "Answer only from the supplied repository context and cite exact paths.\n"
            "If WEB SOURCES are supplied, cite their URLs and label them as external and unverified.\n"
            "Return clean Markdown only, using short paragraphs, headings, and bullet lists.\n"
            "For research questions use exactly these headings when relevant: ## DATA, ## EVIDENCE, ## WEB SOURCES (EXTERNAL, UNVERIFIED), ## AI interpretation, ## Human conclusion.\n"
            "Do not use horizontal rules, decorative emojis, or raw JSON unless requested.\n"
            "Clearly distinguish internal DATA, internal EVIDENCE, WEB SOURCES, AI interpretation, and human conclusion.\n"
            "WEB SOURCES must never appear under EVIDENCE and are never scientific evidence.\n"
            "Never claim that AI output or web content is evidence. Never invent values or experiment results.\n"
            "You may explain registered experiments, but never execute an experiment from free text.\n"
            f"{mode_instructions}\n"
            "For questions about what is currently running, use only the SYSTEM READ-ONLY CONTEXT runtime/session fields. Completed experiments, registry entries, claims, and evidence do not prove that an experiment is running now. If no active session is explicitly listed, answer: 'Kein aktiver Lauf im bereitgestellten Runtime-Status nachweisbar.'\n"
            f"User question: {message}\n\nRepository context:\n{context}"
        )

    def _context(self) -> str:
        research_chunks: list[str] = []
        docs_chunks: list[str] = []
        for document in self.research.list_documents():
            if document.kind not in {"md", "json", "yaml", "yml", "txt"}:
                continue
            try:
                content = self.research.read_content(document.path)
            except (OSError, UnicodeError):
                continue
            research_chunks.append(f"[RESEARCH: {document.path}]\n{content[:4000]}")
        for document in self.docs.list_documents(recursive=True):
            if document.file_type.value not in {"markdown", "text", "json", "yaml"}:
                continue
            try:
                content = self.docs.read_content(document.path)
            except (OSError, UnicodeError, ValueError):
                continue
            docs_chunks.append(f"[DOCS: docs/{document.path}]\n{content[:4000]}")
        sections = [
            "SCIENTIFIC RESEARCH SOURCES (claims, protocols, DATA/EVIDENCE records; scientific authority is limited by their stated status):\n" + "\n\n".join(research_chunks),
            "DOCUMENTATION SOURCES (technical and operational reference; not scientific evidence):\n" + "\n\n".join(docs_chunks),
        ]
        return "\n\n".join(sections)[: self.max_context_chars]


def chat_backend_from_text_backend(backend: Callable[[str], Any]) -> ChatBackend:
    """Adapt a text backend that returns either text or ``(text, metadata)``."""
    def call(prompt: str) -> tuple[str, dict[str, Any]]:
        result = backend(prompt)
        if isinstance(result, tuple):
            tuple_result = cast(tuple[object, ...], result)
            if len(tuple_result) != 2:
                raise ValueError("Chat backend must return text or (text, metadata).")
            text, metadata = tuple_result
            if isinstance(text, str) and isinstance(metadata, dict):
                typed_metadata = cast(dict[object, Any], metadata)
                return text, {
                    str(key): value for key, value in typed_metadata.items()
                }
        if isinstance(result, str):
            return result, {}
        raise ValueError("Chat backend must return text or (text, metadata).")
    return call
