"""Immutable provenance models for future knowledge-intake adapters."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SourceRecord:
    source_id: str
    source_type: str
    locator: str
    retrieved_at_ns: int
    content_sha256: str


@dataclass(frozen=True, slots=True)
class KnowledgeItem:
    item_id: str
    source: SourceRecord
    title: str
    content: str
    language: str
    confidence: float
    learning_session_id: str | None = None
