from dataclasses import dataclass

from src.self_organization.approval import (
    ProposalApprovalPolicy,
    StructuralPlasticityConfig,
)


@dataclass(frozen=True)
class Proposal:
    confidence: float
    kind: str = "neurogenesis"


def test_auto_approval_default_is_off() -> None:
    result = ProposalApprovalPolicy(StructuralPlasticityConfig()).evaluate(
        Proposal(1.0), safety_ok=True, cooldown_ok=True, kind_allowed=True
    )
    assert result.approved is False


def test_auto_approval_requires_threshold_and_safety() -> None:
    config = StructuralPlasticityConfig(
        enabled=True, dry_run=False, auto_approval=True, auto_approval_threshold=0.8
    )
    policy = ProposalApprovalPolicy(config)
    assert policy.evaluate(
        Proposal(0.9), safety_ok=True, cooldown_ok=True, kind_allowed=True
    ).approved
    assert not policy.evaluate(
        Proposal(0.7), safety_ok=True, cooldown_ok=True, kind_allowed=True
    ).approved
    assert not policy.evaluate(
        Proposal(0.9), safety_ok=False, cooldown_ok=True, kind_allowed=True
    ).approved
