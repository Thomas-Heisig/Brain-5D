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
    "StructuralPlasticityConfig",
    "StructuralPlasticityEngine",
    "StructuralProposal",
]
