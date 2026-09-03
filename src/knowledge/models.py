"""Immutable provenance models for future knowledge-intake adapters.

This module defines the core data structures for representing external
knowledge items and their provenance sources. All models are frozen
and slot-based for performance and immutability.

These models are used by the KnowledgeIntakeValidator to create
provenance-bearing knowledge items before they enter the learning pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class SourceRecord:
    """Provenance record for a knowledge source.

    Attributes:
        source_id: Unique identifier for the source.
        source_type: Type of source (e.g., 'wikipedia', 'web', 'document', 'pdf').
        locator: Source identifier (URL, file path, DOI, ISBN, etc.).
        retrieved_at_ns: Timestamp of retrieval in nanoseconds since epoch.
        content_sha256: SHA-256 hash of the content for integrity verification.
    """

    source_id: str
    source_type: str
    locator: str
    retrieved_at_ns: int
    content_sha256: str
    captured_at_ns: int = 0
    processed_at_ns: int = 0
    mime_type: str = "application/octet-stream"
    source_version: str = "not_reported"
    trust_classification: str = "UNKNOWN"
    extraction_method: str = "not_reported"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "source_id": self.source_id,
            "source_type": self.source_type,
            "locator": self.locator,
            "retrieved_at_ns": self.retrieved_at_ns,
            "content_sha256": self.content_sha256,
            "captured_at_ns": self.captured_at_ns,
            "processed_at_ns": self.processed_at_ns,
            "mime_type": self.mime_type,
            "source_version": self.source_version,
            "trust_classification": self.trust_classification,
            "extraction_method": self.extraction_method,
        }


@dataclass(frozen=True, slots=True)
class KnowledgeItem:
    """A validated knowledge item with provenance.

    Attributes:
        item_id: Unique identifier for the knowledge item.
        source: The provenance source record.
        title: Title or heading of the content.
        content: The validated content text.
        language: ISO 639-1 language code (e.g., 'en', 'de', 'fr').
        confidence: Confidence score between 0.0 and 1.0.
        learning_session_id: Optional ID of the learning session that consumed this item.
    """

    item_id: str
    source: SourceRecord
    title: str
    content: str
    language: str
    confidence: float
    learning_session_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            "item_id": self.item_id,
            "source": self.source.to_dict(),
            "title": self.title,
            "content": self.content,
            "language": self.language,
            "confidence": self.confidence,
        }
        if self.learning_session_id is not None:
            result["learning_session_id"] = self.learning_session_id
        return result


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "KnowledgeItem",
    "SourceRecord",
]
