"""Coordinator between dry-run proposals and controlled structural mutation."""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import Callable

from src.dashboard.models import JSONValue

from .approval import ProposalApprovalPolicy
from .policy import (
    LegacyStructuralProposal,
    PolicyReport,
    StructuralAction,
    StructuralProposal,
)

ProposalExecutor = Callable[[LegacyStructuralProposal], int]


@dataclass(frozen=True, slots=True)
class ProposalDecision:
    proposal_id: str
    accepted: bool
    reason: str


@dataclass(frozen=True, slots=True)
class SelfOrganizationSnapshot:
    """Public coordinator telemetry for the dashboard."""

    enabled: bool
    dry_run: bool
    proposals_seen: int
    proposals_executed: int
    mutations_applied: int
    last_proposal: LegacyStructuralProposal | None

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "enabled": self.enabled,
            "dry_run": self.dry_run,
            "proposals_seen": self.proposals_seen,
            "proposals_executed": self.proposals_executed,
            "mutations_applied": self.mutations_applied,
            "last_proposal": (
                self.last_proposal.to_json() if self.last_proposal is not None else None
            ),
        }


class SelfOrganizationCoordinator:
    """Store latest proposals and require explicit operator approval."""

    def __init__(
        self,
        executor: ProposalExecutor | None = None,
        *,
        enabled: bool = True,
        dry_run: bool = True,
    ) -> None:
        self._lock = RLock()
        self._latest: PolicyReport | None = None
        self._decisions: list[ProposalDecision] = []
        self._executor = executor
        self._enabled = enabled
        self._dry_run = dry_run
        self._proposals_seen = 0
        self._proposals_executed = 0
        self._mutations_applied = 0
        self._last_proposal: LegacyStructuralProposal | None = None

    def configure(
        self,
        *,
        enabled: bool | None = None,
        dry_run: bool | None = None,
    ) -> None:
        """Change execution gates without replacing the policy."""
        with self._lock:
            if enabled is not None:
                self._enabled = enabled
            if dry_run is not None:
                self._dry_run = dry_run

    def submit(self, proposal: LegacyStructuralProposal) -> SelfOrganizationSnapshot:
        """Account and optionally execute a legacy structural proposal."""
        with self._lock:
            self._proposals_seen += 1
            self._last_proposal = proposal
            if (
                not self._enabled
                or self._dry_run
                or proposal.action is StructuralAction.NONE
            ):
                return self._snapshot_unlocked()
            if self._executor is None:
                raise RuntimeError(
                    "Self-organization execution is enabled without an executor."
                )
            applied = self._executor(proposal)
            if applied < 0:
                raise ValueError("proposal executor returned a negative mutation count")
            self._proposals_executed += 1
            self._mutations_applied += applied
            return self._snapshot_unlocked()

    def snapshot(self) -> SelfOrganizationSnapshot:
        """Return immutable dashboard telemetry."""
        with self._lock:
            return self._snapshot_unlocked()

    def _snapshot_unlocked(self) -> SelfOrganizationSnapshot:
        return SelfOrganizationSnapshot(
            enabled=self._enabled,
            dry_run=self._dry_run,
            proposals_seen=self._proposals_seen,
            proposals_executed=self._proposals_executed,
            mutations_applied=self._mutations_applied,
            last_proposal=self._last_proposal,
        )

    def publish(self, report: PolicyReport) -> None:
        with self._lock:
            self._latest = report

    def latest(self) -> PolicyReport | None:
        with self._lock:
            return self._latest

    def find(self, proposal_id: str) -> StructuralProposal | None:
        report = self.latest()
        if report is None:
            return None
        return next((p for p in report.proposals if p.proposal_id == proposal_id), None)

    def record_decision(
        self, proposal_id: str, accepted: bool, reason: str
    ) -> ProposalDecision:
        decision = ProposalDecision(proposal_id, accepted, reason)
        with self._lock:
            self._decisions.append(decision)
        return decision

    def approve(self, proposal_id: str, reason: str = "operator approval") -> bool:
        """Record approval only when the proposal is currently published."""
        if self.find(proposal_id) is None:
            return False
        self.record_decision(proposal_id, True, reason)
        return True

    def reject(self, proposal_id: str, reason: str = "operator rejection") -> bool:
        """Record rejection only when the proposal is currently published."""
        if self.find(proposal_id) is None:
            return False
        self.record_decision(proposal_id, False, reason)
        return True

    def auto_process(
        self,
        policy: ProposalApprovalPolicy,
        *,
        safety_ok: bool,
        cooldown_ok: bool,
        kind_allowed: bool,
    ) -> tuple[ProposalDecision, ...]:
        """Evaluate current proposals without applying structural mutations."""
        report = self.latest()
        if report is None:
            return ()
        decisions: list[ProposalDecision] = []
        for proposal in report.proposals:
            approval = policy.evaluate(
                proposal,
                safety_ok=safety_ok,
                cooldown_ok=cooldown_ok,
                kind_allowed=kind_allowed,
            )
            decisions.append(
                self.record_decision(
                    proposal.proposal_id,
                    approval.approved,
                    approval.reason,
                )
            )
        return tuple(decisions)

    def decisions(self) -> tuple[ProposalDecision, ...]:
        with self._lock:
            return tuple(self._decisions)
