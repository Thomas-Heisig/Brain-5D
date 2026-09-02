"""Read-only AI assistance for scientific research artifacts."""

from .assistant import ResearchAssistant
from .models import AIAnalysisRecord, ResearchPacket

__all__ = ["AIAnalysisRecord", "ResearchAssistant", "ResearchPacket"]
