"""Read-only AI assistance for scientific research artifacts."""

from .airr import AIResearchReport, AIRRPipeline, render_markdown, write_human_review
from .assistant import AnalysisBackend, ResearchAssistant
from .chat import ChatBackend, ResearchChat, chat_backend_from_text_backend
from .contracts import (
    AIExposure,
    AIInteractionRecord,
    CausalTaint,
    Evidence,
    Intervention,
    Interpretation,
    Observation,
    Proposal,
)
from .firewall import AIAuthority, AIFirewallViolation, ScientificAIFirewall
from .models import AIAnalysisRecord, ResearchPacket
from .statistics import summarize, write_statistics

__all__ = [
    "AIAnalysisRecord",
    "AIAuthority",
    "AIFirewallViolation",
    "AIExposure",
    "AIInteractionRecord",
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
    "chat_backend_from_text_backend",
    "CausalTaint",
    "Evidence",
    "Intervention",
    "Interpretation",
    "Observation",
    "Proposal",
    "ScientificAIFirewall",
]
