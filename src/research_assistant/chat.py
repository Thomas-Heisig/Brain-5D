"""Bounded research chat with repository-wide read-only retrieval."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, cast

from .contracts import AIExposure, AIInteractionRecord, CausalTaint
from .firewall import ScientificAIFirewall
from .governance import KnowledgeOrigin, NetworkMode, RetrievalRecord
from .repository_context import RepositoryContext, RepositoryKnowledgeView


class _ResearchDocument(Protocol):
    path: str
    kind: str


class _ResearchSource(Protocol):
    def root(self) -> Path: ...
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
    """Construct grounded repository prompts; responses have no mutation authority."""

    research: _ResearchSource
    docs: _DocsSource
    backend: ChatBackend
    max_context_chars: int = 80_000
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
        repository = self._repository_context(question)
        prompt = self._prompt(question, repository)
        answer, metadata = self.backend(prompt)
        retrieval = self._retrieval_record(repository)
        metadata = {
            **metadata,
            "retrieval": retrieval.to_dict(),
            "repository_retrieval": {
                "digest": repository.digest,
                "indexed_files": repository.indexed_files,
                "selected_files": list(repository.selected_files),
                "omitted_large_files": repository.omitted_large_files,
                "authority": "read_only_non_evidentiary",
            },
        }
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

    def _repository_context(self, question: str) -> RepositoryContext:
        root = self.research.root().parent
        return RepositoryKnowledgeView(
            root,
            max_context_chars=max(8_000, self.max_context_chars),
        ).retrieve(question)

    def _retrieval_record(self, repository: RepositoryContext) -> RetrievalRecord:
        web_enabled = bool(self.web_context.strip())
        mode = NetworkMode.LIVE_NETWORK if web_enabled else NetworkMode.FROZEN_CORPUS
        snapshot_digest = hashlib.sha256(
            json.dumps(
                {
                    "repository_digest": repository.digest,
                    "system_context": self.system_context,
                    "web_context": self.web_context,
                    "conversation_context": self.conversation_context,
                },
                sort_keys=True,
                ensure_ascii=True,
            ).encode("utf-8")
        ).hexdigest()
        source_count = len(repository.selected_files) + (1 if web_enabled else 0)
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

    def _prompt(self, message: str, repository: RepositoryContext) -> str:
        context = repository.text
        if self.system_context:
            context = f"SYSTEM READ-ONLY CONTEXT:\n{self.system_context}\n\n{context}"
        if self.web_context:
            context = f"WEB SOURCES (external and unverified):\n{self.web_context}\n\n{context}"
        if self.conversation_context:
            context = (
                "CHAT HIERARCHY (conversation context, not evidence):\n"
                f"{self.conversation_context}\n\n{context}"
            )
        if self.handoff_prompt.strip():
            context = (
                "HANDOFF INSTRUCTIONS (editable operator context, not evidence):\n"
                f"{self.handoff_prompt.strip()}\n\n{context}"
            )
        mode_instructions = {
            "short": "Response mode: SHORT. Answer in at most 5 concise bullet points. Lead with the direct answer and omit background.",
            "detailed": "Response mode: DETAILED. Explain the answer with relevant context, status, exact repository paths, uncertainty, and a concise conclusion.",
            "scientific": "Response mode: SCIENTIFIC. Separate research question, method/protocol, DATA, EVIDENCE, limitations, AI interpretation, and human conclusion. Never upgrade inconclusive or untested status.",
        }[self.response_mode]
        return (
            (f"{self.system_prompt.strip()}\n" if self.system_prompt.strip() else "")
            + "You are the MHRN Research Self-Knowledge Assistant.\n"
            "You are an AI assistant, not a person and not a scientific authority.\n"
            "The repository retrieval layer can inspect the whole eligible repository tree, but only selected bounded snippets are supplied per question.\n"
            "Answer only from supplied read-only context and cite exact repository paths.\n"
            "Large/binary files may be represented by index metadata/digests; never pretend their omitted bytes were read.\n"
            "If WEB SOURCES are supplied, cite their URLs and label them external/unverified.\n"
            "Clearly distinguish internal DATA, accepted EVIDENCE, source code/docs, WEB SOURCES, AI interpretation, and human conclusion.\n"
            "Source code, docs, AI output and web content are never automatically scientific EVID.\n"
            "Never invent values or experiment results. Never execute experiments from free text.\n"
            f"{mode_instructions}\n"
            "For current-running questions use only explicit SYSTEM READ-ONLY CONTEXT runtime/session fields. Completed experiments do not prove a live run.\n"
            f"User question: {message}\n\nRepository context:\n{context[: self.max_context_chars]}"
        )


def chat_backend_from_text_backend(backend: Callable[[str], Any]) -> ChatBackend:
    """Adapt a shared provider backend returning text or ``(text, metadata)``."""

    def call(prompt: str) -> tuple[str, dict[str, Any]]:
        result = backend(prompt)
        if isinstance(result, tuple):
            tuple_result = cast(tuple[object, ...], result)
            if len(tuple_result) != 2:
                raise ValueError("Chat backend must return text or (text, metadata).")
            text, metadata = tuple_result
            if isinstance(text, str) and isinstance(metadata, dict):
                typed_metadata = cast(dict[object, Any], metadata)
                return text, {str(key): value for key, value in typed_metadata.items()}
        if isinstance(result, str):
            return result, {}
        raise ValueError("Chat backend must return text or (text, metadata).")

    return call
