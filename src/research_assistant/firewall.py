"""Execution boundary for AI components used by scientific read-only flows."""

from __future__ import annotations

from enum import StrEnum


class AIAuthority(StrEnum):
    """Capabilities exposed to an AI component."""

    READ_ONLY = "read_only"
    PROPOSAL_ONLY = "proposal_only"
    HUMAN_APPROVED = "human_approved"


class AIFirewallViolation(PermissionError):
    """Raised when an AI component requests a mutation capability."""


class ScientificAIFirewall:
    """Allow bounded interpretation while rejecting direct mutation requests."""

    _READ_ACTIONS = frozenset({"read", "observe", "interpret", "cite"})
    _MUTATION_ACTIONS = frozenset(
        {"write", "execute", "apply", "run", "mutate", "reward", "memory_write"}
    )

    def __init__(self, authority: AIAuthority = AIAuthority.READ_ONLY) -> None:
        self.authority = authority

    def authorize(self, action: str) -> None:
        """Authorize an explicit capability; prompts cannot expand this policy."""
        normalized = action.strip().lower()
        if normalized in self._MUTATION_ACTIONS or normalized not in self._READ_ACTIONS:
            raise AIFirewallViolation(
                f"AI authority {self.authority.value} cannot perform '{action}'."
            )

    def assert_read_only(self) -> None:
        """Verify that the configured component has no mutation authority."""
        if self.authority is not AIAuthority.READ_ONLY:
            raise AIFirewallViolation(
                f"Expected read_only authority, got {self.authority.value}."
            )
