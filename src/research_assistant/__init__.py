"""Read-only AI assistance for scientific research artifacts."""

from .airr import AIResearchReport, AIRRPipeline, render_markdown, write_human_review
from .assistant import AnalysisBackend, ResearchAssistant
from .models import AIAnalysisRecord, ResearchPacket
from .statistics import summarize, write_statistics
from .chat import ChatBackend, ResearchChat

__all__ = [
    "AIAnalysisRecord",
    "AnalysisBackend",
    "AIRRPipeline",
    "AIResearchReport",
    "ResearchAssistant",
    "ResearchPacket",
    "render_markdown",
    "write_human_review",
    "summarize",
    "write_statistics",
    "ChatBackend",
    "ResearchChat",
]
