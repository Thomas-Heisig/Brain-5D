"""Approval and audit gateways for AI proposals."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Callable, Mapping

from .advisor import ActionProposal


@dataclass(frozen=True, slots=True)
class ApprovedIntervention:
    """Human-approved description; it contains no executable callback."""

    proposal_id: str
    reviewer_id: str
    tick: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "reviewer_id": self.reviewer_id,
            "tick": self.tick,
            "approved": True,
            "executed": False,
        }


class InterventionGateway:
    """Gate proposals before an external, separately authorized executor."""

    def __init__(
        self,
        capabilities: set[str],
        *,
        max_per_tick_window: int = 1,
        policy: Callable[[ActionProposal], bool] | None = None,
        safety_envelope: Callable[[ActionProposal], bool] | None = None,
    ) -> None:
        if max_per_tick_window < 1:
            raise ValueError("Rate limit must be positive")
        self._capabilities = frozenset(capabilities)
        self._limit = max_per_tick_window
        self._policy = policy or (lambda _proposal: True)
        self._safety_envelope = safety_envelope or (lambda _proposal: True)
        self._audit: list[dict[str, Any]] = []
        self._approvals: dict[str, ApprovedIntervention] = {}

    def submit(self, proposal: ActionProposal, *, tick: int) -> str:
        if tick < 0:
            raise ValueError("Gateway tick must not be negative")
        action = proposal.action
        payload = {"proposal_id": proposal.proposal.contract_id, "tick": tick}
        if not self._policy(proposal):
            raise PermissionError("Experiment policy rejected intervention proposal")
        if not self._safety_envelope(proposal):
            raise PermissionError("Safety envelope rejected intervention proposal")
        if (
            len([entry for entry in self._audit if entry["tick"] == tick])
            >= self._limit
        ):
            raise PermissionError("Intervention rate limit exceeded")
        if action not in self._capabilities:
            raise PermissionError("Intervention capability not granted")
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode()
        ).hexdigest()
        self._audit.append(
            {**payload, "proposal_digest": action, "audit_digest": digest}
        )
        return proposal.proposal.contract_id

    def approve(
        self, proposal_id: str, *, reviewer_id: str, tick: int
    ) -> ApprovedIntervention:
        if not reviewer_id.strip() or tick < 0:
            raise ValueError("Reviewer ID must be non-empty and tick non-negative")
        if not any(entry["proposal_id"] == proposal_id for entry in self._audit):
            raise KeyError("Unknown intervention proposal")
        approval = ApprovedIntervention(proposal_id, reviewer_id, tick)
        self._approvals[proposal_id] = approval
        return approval

    @property
    def audit(self) -> tuple[Mapping[str, Any], ...]:
        return tuple(dict(entry) for entry in self._audit)


@dataclass(frozen=True, slots=True)
class MemoryWriteProposal:
    """Digest-only memory write proposal awaiting external approval."""

    key: str
    value_digest: str
    source: str

    def to_dict(self) -> dict[str, str | bool]:
        return {
            "key": self.key,
            "value_digest": self.value_digest,
            "source": self.source,
            "approved": False,
            "executed": False,
        }


class MemoryWriteGateway:
    """Collect AI memory proposals without mutating memory state."""

    def propose(self, *, key: str, value: object, source: str) -> MemoryWriteProposal:
        if not key.strip() or not source.strip():
            raise ValueError("Memory key and source must not be empty")
        value_digest = hashlib.sha256(
            json.dumps(value, sort_keys=True, ensure_ascii=True, default=str).encode()
        ).hexdigest()
        return MemoryWriteProposal(key, value_digest, source)
