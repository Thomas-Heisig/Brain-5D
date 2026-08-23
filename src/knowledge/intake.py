"""Validation-only knowledge intake boundary.

Network access is deliberately absent in alpha.6. Future Wikipedia or web adapters must
produce SourceRecord + KnowledgeItem values before any downstream learning stimulus is
created.

This module provides the KnowledgeIntakeValidator, which creates provenance-bearing
KnowledgeItem instances from raw content drafts. All validation is performed before
any item enters the knowledge pipeline.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Any

from .models import KnowledgeItem, SourceRecord

# ============================================================================
# Knowledge Draft
# ============================================================================


@dataclass(frozen=True, slots=True)
class KnowledgeDraft:
    """Raw knowledge content before validation and ingestion.

    Attributes:
        source_type: Type of source (e.g., 'wikipedia', 'web', 'document').
        locator: Source identifier (URL, file path, DOI, etc.).
        title: Title or heading of the content.
        content: The raw content text.
        language: ISO 639-1 language code (default: 'und' for undetermined).
        confidence: Confidence score between 0.0 and 1.0.
    """

    source_type: str
    locator: str
    title: str
    content: str
    language: str = "und"
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "source_type": self.source_type,
            "locator": self.locator,
            "title": self.title,
            "content": self.content,
            "language": self.language,
            "confidence": self.confidence,
        }


# ============================================================================
# Knowledge Intake Validator
# ============================================================================


class KnowledgeIntakeValidator:
    """Create provenance-bearing items from already retrieved content.

    This validator ensures that all incoming knowledge meets quality standards
    before being converted into KnowledgeItem instances. It creates a
    cryptographic content hash for provenance tracking.

    Example:
        >>> validator = KnowledgeIntakeValidator()
        >>> draft = KnowledgeDraft(
        ...     source_type="wikipedia",
        ...     locator="https://en.wikipedia.org/wiki/Paris",
        ...     title="Paris",
        ...     content="Paris is the capital of France."
        ... )
        >>> item = validator.create_item(
        ...     item_id="item_001",
        ...     source_id="src_001",
        ...     draft=draft
        ... )
        >>> print(item.content)
        Paris is the capital of France.
    """

    def create_item(
        self,
        *,
        item_id: str,
        source_id: str,
        draft: KnowledgeDraft,
    ) -> KnowledgeItem:
        """Create a provenance-bearing KnowledgeItem from a draft.

        Args:
            item_id: Unique identifier for the knowledge item.
            source_id: Unique identifier for the source.
            draft: The raw knowledge draft to validate and convert.

        Returns:
            A fully validated KnowledgeItem with provenance.

        Raises:
            ValueError: If the content is empty, confidence is out of bounds,
                or required fields are missing.
        """
        # Validate content
        if not draft.content or not draft.content.strip():
            raise ValueError("knowledge content must not be empty")

        # Validate confidence
        if not 0.0 <= draft.confidence <= 1.0:
            raise ValueError(
                f"confidence must be between 0 and 1, got {draft.confidence}"
            )

        # Validate title
        if not draft.title or not draft.title.strip():
            raise ValueError("knowledge title must not be empty")

        # Validate source_type
        if not draft.source_type or not draft.source_type.strip():
            raise ValueError("source_type must not be empty")

        # Create content hash
        digest = hashlib.sha256(draft.content.encode("utf-8")).hexdigest()

        # Create SourceRecord with provenance
        source = SourceRecord(
            source_id=source_id,
            source_type=draft.source_type,
            locator=draft.locator,
            retrieved_at_ns=time.time_ns(),
            content_sha256=digest,
        )

        # Create KnowledgeItem
        return KnowledgeItem(
            item_id=item_id,
            source=source,
            title=draft.title,
            content=draft.content,
            language=draft.language,
            confidence=draft.confidence,
        )


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "KnowledgeDraft",
    "KnowledgeIntakeValidator",
    "KnowledgeItem",
    "SourceRecord",
]
