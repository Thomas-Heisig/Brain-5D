"""Self-organization and controlled structural plasticity."""

from .approval import (
    ApprovalDecision,
    ProposalApprovalPolicy,
    StructuralPlasticityConfig,
)
from .coordinator import (
    ProposalDecision,
    SelfOrganizationCoordinator,
    SelfOrganizationSnapshot,
)
from .engine import SelfOrganizationEngine
from .morphology import MorphologyBudget, MorphologyLedger, StructuralCostModel
from .plasticity import (
    ChangeKind,
    PlasticitySafetyLimits,
    StructuralChange,
    StructuralPlasticityEngine,
)
from .policy import (
    PolicyReport,
    ProposalKind,
    SelfOrganizationParameters,
    SelfOrganizationPolicy,
    SelfOrganizationPolicyConfig,
    StructuralAction,
    StructuralProposal,
)

__all__ = [
    "ApprovalDecision",
    "ChangeKind",
    "PlasticitySafetyLimits",
    "PolicyReport",
    "MorphologyBudget",
    "MorphologyLedger",
    "ProposalApprovalPolicy",
    "ProposalDecision",
    "ProposalKind",
    "SelfOrganizationCoordinator",
    "SelfOrganizationEngine",
    "SelfOrganizationParameters",
    "SelfOrganizationPolicy",
    "SelfOrganizationPolicyConfig",
    "SelfOrganizationSnapshot",
    "StructuralAction",
    "StructuralChange",
    "StructuralCostModel",
    "StructuralPlasticityConfig",
    "StructuralPlasticityEngine",
    "StructuralProposal",
]
