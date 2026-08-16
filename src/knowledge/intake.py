"""Validation-only knowledge intake boundary.

Network access is deliberately absent in alpha.6. Future Wikipedia or web adapters must
produce SourceRecord + KnowledgeItem values before any downstream learning stimulus is
created.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass

from .models import KnowledgeItem, SourceRecord


@dataclass(frozen=True, slots=True)
class KnowledgeDraft:
    source_type: str
    locator: str
    title: str
    content: str
    language: str = "und"
    confidence: float = 0.0


class KnowledgeIntakeValidator:
    """Create provenance-bearing items from already retrieved content."""

    def create_item(
        self, *, item_id: str, source_id: str, draft: KnowledgeDraft
    ) -> KnowledgeItem:
        if not draft.content.strip():
            raise ValueError("knowledge content must not be empty")
        if not 0.0 <= draft.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        digest = hashlib.sha256(draft.content.encode("utf-8")).hexdigest()
        source = SourceRecord(
            source_id=source_id,
            source_type=draft.source_type,
            locator=draft.locator,
            retrieved_at_ns=time.time_ns(),
            content_sha256=digest,
        )
        return KnowledgeItem(
            item_id=item_id,
            source=source,
            title=draft.title,
            content=draft.content,
            language=draft.language,
            confidence=draft.confidence,
        )
