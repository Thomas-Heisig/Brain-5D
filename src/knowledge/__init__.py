"""Knowledge intake and provenance tracking for Brain-5D.

This package provides validation, provenance tracking, and management
of external knowledge before it enters the learning pipeline.
"""

from .intake import KnowledgeDraft, KnowledgeIntakeValidator
from .models import KnowledgeItem, SourceRecord

__all__ = [
    "KnowledgeDraft",
    "KnowledgeIntakeValidator",
    "KnowledgeItem",
    "SourceRecord",
]
