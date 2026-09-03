"""Read-only AI assistance for scientific research artifacts."""

from .airr import AIResearchReport, AIRRPipeline, render_markdown, write_human_review
from .assistant import AnalysisBackend, ResearchAssistant
from .authority import (
    AuthorityRule,
    authority_for,
    authority_matrix,
    validate_authority_matrix,
)
from .chat import ChatBackend, ResearchChat, chat_backend_from_text_backend
from .contracts import (
    AIExposure,
    AIInferenceFailureEvent,
    AIInteractionRecord,
    AIReproducibility,
    CausalTaint,
    Evidence,
    Interpretation,
    Intervention,
    Observation,
    Proposal,
)
from .firewall import AIAuthority, AIFirewallViolation, AIResource, ScientificAIFirewall
from .models import AIAnalysisRecord, ResearchPacket
from .observation_stream import (
    ObservationStream,
    ObservationStreamError,
    ObservationStreamRecord,
)
from .replay_backend import FrozenAIReplayBackend, FrozenAIReplayError
from .statistics import summarize, write_statistics

__all__ = [
    "AIAnalysisRecord",
    "AIAuthority",
    "AIFirewallViolation",
    "AIResource",
    "AIExposure",
        "AIInferenceFailureEvent",
    "AIInteractionRecord",
    "AIReproducibility",
    "AnalysisBackend",
    "AIRRPipeline",
    "AIResearchReport",
    "AuthorityRule",
    "ResearchAssistant",
    "ResearchPacket",
    "FrozenAIReplayBackend",
    "FrozenAIReplayError",
    "ObservationStream",
    "ObservationStreamError",
    "ObservationStreamRecord",
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
    "authority_for",
    "authority_matrix",
    "validate_authority_matrix",
]
