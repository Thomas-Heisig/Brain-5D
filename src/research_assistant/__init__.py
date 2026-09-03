"""Read-only AI assistance for scientific research artifacts."""

from .advisor import ActionProposal, CognitiveAdvisor
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
from .gateways import (
    ApprovedIntervention,
    InterventionGateway,
    MemoryWriteGateway,
    MemoryWriteProposal,
)
from .governance import (
    KnowledgeOrigin,
    NetworkMode,
    PreregistrationLock,
    PromptRegistry,
    RetrievalRecord,
    VersionedPrompt,
    validate_network_mode,
)
from .models import AIAnalysisRecord, ResearchPacket
from .observation_stream import (
    ObservationStream,
    ObservationStreamError,
    ObservationStreamRecord,
)
from .replay_backend import FrozenAIReplayBackend, FrozenAIReplayError
from .shadow import (
    ShadowMode,
    ShadowProposalMetrics,
    ShadowResult,
    evaluate_shadow_proposals,
)
from .statistics import summarize, write_statistics

__all__ = [
    "AIAnalysisRecord",
    "ActionProposal",
    "ApprovedIntervention",
    "AIAuthority",
    "AIFirewallViolation",
    "AIResource",
    "KnowledgeOrigin",
    "InterventionGateway",
    "MemoryWriteGateway",
    "MemoryWriteProposal",
    "NetworkMode",
    "PreregistrationLock",
    "PromptRegistry",
    "RetrievalRecord",
    "VersionedPrompt",
    "validate_network_mode",
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
    "CognitiveAdvisor",
    "FrozenAIReplayBackend",
    "FrozenAIReplayError",
    "ShadowMode",
    "ShadowProposalMetrics",
    "ShadowResult",
    "evaluate_shadow_proposals",
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
