"""Proposal-only cognitive advisor boundary."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .contracts import Proposal
from .firewall import AIAuthority, ScientificAIFirewall


@dataclass(frozen=True, slots=True)
class ActionProposal:
    """Typed action description with no executable command or callback."""

    proposal: Proposal
    action: str
    rationale: str
    confidence: float

    @classmethod
    def create(
        cls,
        *,
        action: str,
        rationale: str,
        confidence: float,
        source: str = "cognitive_advisor",
    ) -> ActionProposal:
        if not action.strip() or not rationale.strip():
            raise ValueError("Action and rationale must not be empty")
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("Proposal confidence must be between 0 and 1")
        return cls(
            proposal=Proposal.create(
                payload={
                    "action": action,
                    "rationale": rationale,
                    "confidence": confidence,
                },
                source=source,
                authority="proposal_only",
            ),
            action=action,
            rationale=rationale,
            confidence=confidence,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal": self.proposal.to_dict(),
            "rationale": self.rationale,
            "confidence": self.confidence,
            "executed": False,
        }


class CognitiveAdvisor:
    """Create proposals while refusing every direct mutation capability."""

    def __init__(self) -> None:
        self._firewall = ScientificAIFirewall(AIAuthority.PROPOSAL_ONLY)

    def propose(
        self,
        *,
        action: str,
        rationale: str,
        confidence: float,
        source: str = "cognitive_advisor",
    ) -> ActionProposal:
        self._firewall.authorize("propose")
        return ActionProposal.create(
            action=action,
            rationale=rationale,
            confidence=confidence,
            source=source,
        )
