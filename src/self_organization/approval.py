"""Explicit approval policy for structural proposals."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class ProposalLike(Protocol):
    @property
    def confidence(self) -> float: ...
    @property
    def kind(self) -> object: ...


@dataclass(frozen=True, slots=True)
class StructuralPlasticityConfig:
    enabled: bool = False
    dry_run: bool = True
    auto_approval: bool = False
    auto_approval_threshold: float = 0.8
    max_changes_per_tick: int = 5
    max_neuron_additions_per_tick: int = 2
    max_neuron_removals_per_tick: int = 0
    max_synapse_additions_per_tick: int = 5
    max_synapse_removals_per_tick: int = 5
    min_neurons: int = 100
    max_neurons: int = 10_000
    allow_neuron_pruning: bool = False
    allow_synapse_pruning: bool = True
    cooldown_ticks: int = 100


@dataclass(frozen=True, slots=True)
class ApprovalDecision:
    approved: bool
    automatic: bool
    reason: str


class ProposalApprovalPolicy:
    """Approves only explicitly allowed, safe high-confidence proposals."""

    def __init__(self, config: StructuralPlasticityConfig) -> None:
        self.config = config

    def evaluate(
        self,
        proposal: ProposalLike,
        *,
        safety_ok: bool,
        cooldown_ok: bool,
        kind_allowed: bool,
    ) -> ApprovalDecision:
        if not self.config.enabled:
            return ApprovalDecision(False, False, "structural plasticity disabled")
        if self.config.dry_run:
            return ApprovalDecision(False, False, "dry-run mode")
        if not self.config.auto_approval:
            return ApprovalDecision(False, False, "manual approval required")
        if not safety_ok:
            return ApprovalDecision(False, True, "safety limits rejected proposal")
        if not cooldown_ok:
            return ApprovalDecision(False, True, "cooldown active")
        if not kind_allowed:
            return ApprovalDecision(False, True, "proposal kind disabled")
        if proposal.confidence < self.config.auto_approval_threshold:
            return ApprovalDecision(False, True, "confidence below threshold")
        return ApprovalDecision(True, True, "auto-approval threshold satisfied")
