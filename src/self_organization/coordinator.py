"""Auditable coordinator for structural proposals.

Execution is disabled by default.  This allows alpha.3 to expose proposals in the
Dashboard before enabling mutations in production runs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from src.dashboard.models import JSONValue

from .policy import StructuralAction, StructuralProposal

ProposalExecutor = Callable[[StructuralProposal], int]


@dataclass(frozen=True, slots=True)
class SelfOrganizationSnapshot:
    """Public coordinator telemetry."""

    enabled: bool
    dry_run: bool
    proposals_seen: int
    proposals_executed: int
    mutations_applied: int
    last_proposal: StructuralProposal | None

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
    """Gate and account structural mutations from policy proposals."""

    def __init__(
        self,
        executor: ProposalExecutor | None = None,
        *,
        enabled: bool = True,
        dry_run: bool = True,
    ) -> None:
        self._executor = executor
        self._enabled = enabled
        self._dry_run = dry_run
        self._proposals_seen = 0
        self._proposals_executed = 0
        self._mutations_applied = 0
        self._last_proposal: StructuralProposal | None = None

    def configure(self, *, enabled: bool | None = None, dry_run: bool | None = None) -> None:
        """Change execution gates without replacing the policy."""
        if enabled is not None:
            self._enabled = enabled
        if dry_run is not None:
            self._dry_run = dry_run

    def submit(self, proposal: StructuralProposal) -> SelfOrganizationSnapshot:
        """Account and optionally execute a structural proposal."""
        self._proposals_seen += 1
        self._last_proposal = proposal
        if (
            not self._enabled
            or self._dry_run
            or proposal.action is StructuralAction.NONE
        ):
            return self.snapshot()
        if self._executor is None:
            raise RuntimeError("Self-organization execution is enabled without an executor.")
        applied = self._executor(proposal)
        if applied < 0:
            raise ValueError("proposal executor returned a negative mutation count")
        self._proposals_executed += 1
        self._mutations_applied += applied
        return self.snapshot()

    def snapshot(self) -> SelfOrganizationSnapshot:
        """Return immutable dashboard telemetry."""
        return SelfOrganizationSnapshot(
            enabled=self._enabled,
            dry_run=self._dry_run,
            proposals_seen=self._proposals_seen,
            proposals_executed=self._proposals_executed,
            mutations_applied=self._mutations_applied,
            last_proposal=self._last_proposal,
        )
