"""Typed contracts for bounded scientific AI interactions."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, ClassVar, Mapping, Self


class AIExposure(StrEnum):
    """How much causal access an AI component has to an experiment."""

    NONE = "none"
    OBSERVER_ONLY = "observer_only"
    SEMANTIC_INTERFACE = "semantic_interface"
    ADVISOR = "advisor"
    BOUNDED_CONTROLLER = "bounded_controller"
    ADAPTIVE_CONTROLLER = "adaptive_controller"


class CausalTaint(StrEnum):
    """Scientific classification of AI influence on an experiment."""

    PURE = "PURE"
    OBSERVED = "OBSERVED"
    PROPOSED = "PROPOSED"
    AI_INFLUENCED = "AI_INFLUENCED"


class AIReproducibility(StrEnum):
    """Registered reproducibility level for AI participation in a run."""

    R0 = "R0"
    R1 = "R1"
    R2 = "R2"
    R3 = "R3"


class AIClockMode(StrEnum):
    """Clock semantics for asynchronous AI interaction timing."""

    LOGICAL_TIME = "LOGICAL_TIME"
    WALL_CLOCK = "WALL_CLOCK"


@dataclass(frozen=True, slots=True)
class ScientificContract:
    """Immutable, digest-backed data contract with no execution capability."""

    contract_id: str
    payload_digest: str
    source: str
    authority: str
    created_at: str
    kind: ClassVar[str] = "contract"

    def to_dict(self) -> dict[str, str]:
        return {"kind": self.kind, **asdict(self)}

    @classmethod
    def create(
        cls,
        *,
        payload: object,
        source: str,
        authority: str,
    ) -> Self:
        if not source.strip():
            raise ValueError("contract source must not be empty")
        if not authority.strip():
            raise ValueError("contract authority must not be empty")
        payload_digest = _digest(payload)
        identity = f"{cls.kind}|{source}|{authority}|{payload_digest}"
        contract_id = f"{cls.kind.upper()}-{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:16]}"
        return cls(
            contract_id=contract_id,
            payload_digest=payload_digest,
            source=source,
            authority=authority,
            created_at=datetime.now(timezone.utc).isoformat(),
        )


class Observation(ScientificContract):
    """Read-only observation; it carries no interpretation or action."""

    kind = "observation"


class Interpretation(ScientificContract):
    """Derived interpretation that is not evidence by itself."""

    kind = "interpretation"


class Proposal(ScientificContract):
    """Suggested next step; proposals require an external approval path."""

    kind = "proposal"


class Intervention(ScientificContract):
    """Description of a possible intervention, never an executable command."""

    kind = "intervention"


class Evidence(ScientificContract):
    """Reference to evidence whose scientific authority comes from its source."""

    kind = "evidence"


@dataclass(frozen=True, slots=True)
class ProvenanceNode:
    """Digest-only epistemic source or derived value in a provenance graph."""

    node_id: str
    node_type: str
    knowledge_origin: str
    payload_digest: str

    @classmethod
    def create(
        cls, *, node_id: str, node_type: str, knowledge_origin: str, payload: object
    ) -> ProvenanceNode:
        if not node_id.strip() or not node_type.strip():
            raise ValueError("Provenance node ID and type must not be empty")
        if not knowledge_origin.strip():
            raise ValueError("Provenance node knowledge_origin must not be empty")
        return cls(node_id, node_type, knowledge_origin, _digest(payload))

    def to_dict(self) -> dict[str, str]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "knowledge_origin": self.knowledge_origin,
            "payload_digest": self.payload_digest,
        }


@dataclass(frozen=True, slots=True)
class ProvenanceEdge:
    """Directed dependency between two epistemic provenance nodes."""

    source_id: str
    target_id: str
    relation: str

    def to_dict(self) -> dict[str, str]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation": self.relation,
        }


@dataclass(frozen=True, slots=True)
class EpistemicProvenanceGraph:
    """Append-only acyclic graph for claims, sources, experiments and derivations."""

    nodes: tuple[ProvenanceNode, ...] = ()
    edges: tuple[ProvenanceEdge, ...] = ()

    def add_node(self, node: ProvenanceNode) -> EpistemicProvenanceGraph:
        if any(existing.node_id == node.node_id for existing in self.nodes):
            raise ValueError(f"Provenance node already exists: {node.node_id}")
        return EpistemicProvenanceGraph(self.nodes + (node,), self.edges)

    def add_edge(self, edge: ProvenanceEdge) -> EpistemicProvenanceGraph:
        node_ids = {node.node_id for node in self.nodes}
        if edge.source_id not in node_ids or edge.target_id not in node_ids:
            raise ValueError("Provenance edge references an unknown node")
        if edge.source_id == edge.target_id:
            raise ValueError("Provenance graph cannot contain self-edges")
        if edge in self.edges:
            raise ValueError("Provenance edge already exists")
        candidate = EpistemicProvenanceGraph(self.nodes, self.edges + (edge,))
        candidate.validate()
        return candidate

    def validate(self) -> None:
        """Validate references and reject cycles that obscure derivation order."""
        node_ids = {node.node_id for node in self.nodes}
        if len(node_ids) != len(self.nodes):
            raise ValueError("Provenance graph contains duplicate node IDs")
        adjacency: dict[str, set[str]] = {node_id: set() for node_id in node_ids}
        for edge in self.edges:
            if edge.source_id not in node_ids or edge.target_id not in node_ids:
                raise ValueError("Provenance edge references an unknown node")
            adjacency[edge.source_id].add(edge.target_id)
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node_id: str) -> None:
            if node_id in visiting:
                raise ValueError("Provenance graph cannot contain cycles")
            if node_id in visited:
                return
            visiting.add(node_id)
            for child_id in adjacency[node_id]:
                visit(child_id)
            visiting.remove(node_id)
            visited.add(node_id)

        for node_id in node_ids:
            visit(node_id)

    def to_dict(self) -> dict[str, list[dict[str, str]]]:
        self.validate()
        return {
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
        }


@dataclass(frozen=True, slots=True)
class AIInteractionRecord:
    """Audit record for one AI interaction; it grants no execution authority."""

    interaction_id: str
    role: str
    experiment_id: str | None
    tick: int | None
    input_digest: str
    prompt_digest: str
    output_digest: str
    model_provenance: dict[str, Any]
    authority: str
    exposure: AIExposure
    causal_effect: CausalTaint
    clock_mode: AIClockMode
    response_application_tick: int | None
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation for journals and APIs."""
        payload = asdict(self)
        payload["exposure"] = self.exposure.value
        payload["causal_effect"] = self.causal_effect.value
        return payload

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=True)

    @classmethod
    def create(
        cls,
        *,
        role: str,
        experiment_id: str | None,
        tick: int | None,
        input_value: object,
        prompt: str,
        output_value: object,
        model_provenance: Mapping[str, Any],
        authority: str,
        exposure: AIExposure = AIExposure.OBSERVER_ONLY,
        causal_effect: CausalTaint = CausalTaint.OBSERVED,
        clock_mode: AIClockMode = AIClockMode.LOGICAL_TIME,
        response_application_tick: int | None = None,
    ) -> AIInteractionRecord:
        """Build a record from canonicalized values without storing their contents."""
        if not role.strip():
            raise ValueError("AI interaction role must not be empty")
        if not authority.strip():
            raise ValueError("AI interaction authority must not be empty")
        if tick is not None and tick < 0:
            raise ValueError("AI interaction tick must not be negative")
        if response_application_tick is not None and response_application_tick < 0:
            raise ValueError("AI response application tick must not be negative")

        input_digest = _digest(input_value)
        prompt_digest = _digest(prompt)
        output_digest = _digest(output_value)
        created_at = datetime.now(timezone.utc).isoformat()
        identity = "|".join(
            (
                role,
                experiment_id or "",
                str(tick) if tick is not None else "",
                input_digest,
                prompt_digest,
                output_digest,
            )
        )
        interaction_id = f"AIRC-{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:16]}"
        return cls(
            interaction_id=interaction_id,
            role=role,
            experiment_id=experiment_id,
            tick=tick,
            input_digest=input_digest,
            prompt_digest=prompt_digest,
            output_digest=output_digest,
            model_provenance=dict(model_provenance),
            authority=authority,
            exposure=exposure,
            causal_effect=causal_effect,
            clock_mode=clock_mode,
            response_application_tick=response_application_tick,
            created_at=created_at,
        )


@dataclass(frozen=True, slots=True)
class AIInferenceFailureEvent:
    """Digest-backed audit record for a failed AI inference attempt."""

    event_id: str
    request_id: str
    backend: str
    request_digest: str
    latency_ms: float
    retry_status: str
    error: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def create(
        cls,
        *,
        request_id: str,
        backend: str,
        request_digest: str,
        latency_ms: float,
        retry_status: str,
        error: str,
    ) -> AIInferenceFailureEvent:
        if not request_id.strip() or not backend.strip():
            raise ValueError("AI failure event identity must not be empty")
        if latency_ms < 0:
            raise ValueError("AI failure latency must not be negative")
        created_at = datetime.now(timezone.utc).isoformat()
        identity = "|".join((request_id, backend, request_digest, error, created_at))
        event_id = f"AIFE-{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:16]}"
        return cls(
            event_id=event_id,
            request_id=request_id,
            backend=backend,
            request_digest=request_digest,
            latency_ms=latency_ms,
            retry_status=retry_status,
            error=error,
            created_at=created_at,
        )


def _digest(value: object) -> str:
    if isinstance(value, str):
        canonical = value
    else:
        canonical = json.dumps(value, sort_keys=True, ensure_ascii=True, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
