"""Scientific authority matrix for AI and research system roles."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .firewall import AIAuthority


@dataclass(frozen=True, slots=True)
class AuthorityRule:
    """Allowed capability boundary for one system role."""

    role: str
    authority: str
    capabilities: tuple[str, ...]
    scientific_evidence: bool

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


_AUTHORITY_RULES = (
    AuthorityRule("SNN", "runtime", ("observe", "learn"), False),
    AuthorityRule("Statistics Engine", "deterministic", ("read", "compute"), False),
    AuthorityRule("Language Organ", AIAuthority.READ_ONLY.value, ("observe", "interpret"), False),
    AuthorityRule("Research Assistant", AIAuthority.READ_ONLY.value, ("read", "interpret", "cite"), False),
    AuthorityRule("Cognitive Advisor", AIAuthority.PROPOSAL_ONLY.value, ("read", "interpret", "propose"), False),
    AuthorityRule("Action Gateway", AIAuthority.HUMAN_APPROVED.value, ("validate", "apply"), False),
    AuthorityRule("Evidence Engine", "registered", ("read", "register"), True),
    AuthorityRule("Human Reviewer", "human", ("read", "review", "approve"), False),
)


def authority_matrix() -> tuple[AuthorityRule, ...]:
    """Return the immutable role matrix in documented order."""
    return _AUTHORITY_RULES


def authority_for(role: str) -> AuthorityRule:
    """Resolve a role or fail closed for unknown components."""
    for rule in _AUTHORITY_RULES:
        if rule.role == role:
            return rule
    raise KeyError(f"Unknown scientific authority role: {role}")


def validate_authority_matrix() -> None:
    """Enforce that AI roles cannot claim direct mutation or evidence authority."""
    ai_roles = {"Language Organ", "Research Assistant", "Cognitive Advisor"}
    for rule in _AUTHORITY_RULES:
        if rule.role in ai_roles and rule.scientific_evidence:
            raise ValueError(f"AI role cannot provide scientific evidence: {rule.role}")
        if rule.role in ai_roles and "apply" in rule.capabilities:
            raise ValueError(f"AI role cannot apply mutations: {rule.role}")
