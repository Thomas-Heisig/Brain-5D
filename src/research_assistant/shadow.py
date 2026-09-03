"""Non-executing shadow mode for scientific AI proposals."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .contracts import Interpretation, Observation, Proposal, ScientificContract
from .firewall import AIAuthority, ScientificAIFirewall


@dataclass(frozen=True, slots=True)
class ShadowResult:
    """A marked shadow output that has not been applied to system state."""

    contract: ScientificContract
    executed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {"executed": self.executed, "contract": self.contract.to_dict()}


class ShadowMode:
    """Allow observation, interpretation and proposals without execution."""

    def __init__(self) -> None:
        self._firewall = ScientificAIFirewall(AIAuthority.PROPOSAL_ONLY)

    def observe(self, payload: object, *, source: str = "shadow") -> ShadowResult:
        self._firewall.authorize("observe")
        return ShadowResult(
            Observation.create(payload=payload, source=source, authority="read_only")
        )

    def interpret(self, payload: object, *, source: str = "shadow") -> ShadowResult:
        self._firewall.authorize("interpret")
        return ShadowResult(
            Interpretation.create(payload=payload, source=source, authority="read_only")
        )

    def propose(self, payload: object, *, source: str = "shadow") -> ShadowResult:
        self._firewall.authorize("propose")
        return ShadowResult(
            Proposal.create(payload=payload, source=source, authority="proposal_only")
        )
