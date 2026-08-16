"""Self-organization and controlled structural plasticity."""

from .engine import SelfOrganizationEngine
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
    "ProposalKind",
    "ProposalDecision",
    "ProposalApprovalPolicy",
    "SelfOrganizationEngine",
    "SelfOrganizationCoordinator",
    "SelfOrganizationParameters",
    "SelfOrganizationPolicy",
    "SelfOrganizationPolicyConfig",
    "SelfOrganizationSnapshot",
    "StructuralAction",
    "StructuralChange",
    "StructuralPlasticityEngine",
    "StructuralPlasticityConfig",
    "StructuralProposal",
]
