"""Guarded preparation contracts for Brain-5D learning runs.

The learning preparation layer sits *before* the existing LearningEngine.  It may
organize objectives, source provenance, baselines, training/evaluation phases and
stopping criteria, but it has no authority to write neural patterns, synaptic
weights, injected currents or reward values.

AI assistance is deliberately proposal-only.  Approval produces a reproducible
``PreparedLearningPlan``; it does not execute the plan or mutate the runtime.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Sequence, cast

from src.knowledge.models import KnowledgeItem


class LearningPlanOrigin(str, Enum):
    """Origin of a learning-preparation proposal."""

    HUMAN = "human"
    AI_ASSISTED = "ai_assisted"


class LearningDataPartition(str, Enum):
    """Explicit data partition used by a prepared learning run."""

    TRAIN = "train"
    VALIDATION = "validation"
    HOLDOUT = "holdout"


@dataclass(frozen=True, slots=True)
class LearningSourceRef:
    """Provenance-only reference to material that may become an observation source."""

    source_id: str
    digest: str
    origin: str
    partition: LearningDataPartition
    trust: str = "UNKNOWN"

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError("source_id must not be empty")
        if not self.digest.strip():
            raise ValueError("source digest must not be empty")
        if not self.origin.strip():
            raise ValueError("source origin must not be empty")

    def to_dict(self) -> dict[str, str]:
        return {
            "source_id": self.source_id,
            "digest": self.digest,
            "origin": self.origin,
            "partition": self.partition.value,
            "trust": self.trust,
        }

    @classmethod
    def from_knowledge_item(
        cls,
        item: KnowledgeItem,
        *,
        partition: LearningDataPartition = LearningDataPartition.TRAIN,
    ) -> LearningSourceRef:
        """Derive a learning reference from validated knowledge provenance."""
        return cls(
            source_id=item.source.source_id,
            digest=item.source.content_sha256,
            origin=f"knowledge:{item.source.source_type}",
            partition=partition,
            trust=item.source.trust_classification,
        )

    @classmethod
    def from_environment_capture(
        cls,
        capture: Mapping[str, Any],
        *,
        partition: LearningDataPartition = LearningDataPartition.TRAIN,
    ) -> LearningSourceRef:
        """Derive a reference from an immutable environment-capture record."""
        environment_id = _required_capture_field(capture, "environment_id")
        capture_id = _required_capture_field(capture, "capture_id")
        digest = _required_capture_field(capture, "digest")
        trust = str(capture.get("trust", "CONTROLLED"))
        return cls(
            source_id=f"{environment_id}:{capture_id}",
            digest=digest,
            origin=f"environment:{environment_id}",
            partition=partition,
            trust=trust,
        )


@dataclass(frozen=True, slots=True)
class LearningObjective:
    """A measurable goal without a prescribed neural representation."""

    objective_id: str
    description: str
    success_metric: str
    evaluation_question: str

    def __post_init__(self) -> None:
        for name, value in (
            ("objective_id", self.objective_id),
            ("description", self.description),
            ("success_metric", self.success_metric),
            ("evaluation_question", self.evaluation_question),
        ):
            if not value.strip():
                raise ValueError(f"{name} must not be empty")

    def to_dict(self) -> dict[str, str]:
        return {
            "objective_id": self.objective_id,
            "description": self.description,
            "success_metric": self.success_metric,
            "evaluation_question": self.evaluation_question,
        }


@dataclass(frozen=True, slots=True)
class LearningPreparationProposal:
    """Non-executable proposal describing how learning should be *prepared*."""

    plan_id: str
    objective: LearningObjective
    sources: tuple[LearningSourceRef, ...]
    baseline_protocol: str
    exposure_protocol: str
    evaluation_protocol: str
    stopping_rule: str
    controls: tuple[str, ...]
    origin: LearningPlanOrigin
    rationale: str = ""
    ai_interaction_id: str | None = None
    authority: str = "proposal_only"

    def __post_init__(self) -> None:
        if not self.plan_id.strip():
            raise ValueError("plan_id must not be empty")
        for name, value in (
            ("baseline_protocol", self.baseline_protocol),
            ("exposure_protocol", self.exposure_protocol),
            ("evaluation_protocol", self.evaluation_protocol),
            ("stopping_rule", self.stopping_rule),
        ):
            if not value.strip():
                raise ValueError(f"{name} must not be empty")
        if self.authority != "proposal_only":
            raise ValueError("learning preparation proposals are proposal_only")
        if self.origin is LearningPlanOrigin.AI_ASSISTED and not self.ai_interaction_id:
            raise ValueError("AI-assisted proposals require ai_interaction_id provenance")

    @property
    def digest(self) -> str:
        payload = self.to_dict(include_digest=False)
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def to_dict(self, *, include_digest: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "plan_id": self.plan_id,
            "objective": self.objective.to_dict(),
            "sources": [source.to_dict() for source in self.sources],
            "baseline_protocol": self.baseline_protocol,
            "exposure_protocol": self.exposure_protocol,
            "evaluation_protocol": self.evaluation_protocol,
            "stopping_rule": self.stopping_rule,
            "controls": list(self.controls),
            "origin": self.origin.value,
            "rationale": self.rationale,
            "ai_interaction_id": self.ai_interaction_id,
            "authority": self.authority,
            "executed": False,
        }
        if include_digest:
            payload["digest"] = self.digest
        return payload


@dataclass(frozen=True, slots=True)
class PreparedLearningPlan:
    """Human-approved preparation artifact; still has no runtime mutation authority."""

    proposal: LearningPreparationProposal
    approved_by: str
    approval_note: str = ""

    def __post_init__(self) -> None:
        if not self.approved_by.strip():
            raise ValueError("approved_by must not be empty")

    @property
    def digest(self) -> str:
        payload = {
            "proposal_digest": self.proposal.digest,
            "approved_by": self.approved_by,
            "approval_note": self.approval_note,
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal": self.proposal.to_dict(),
            "approved_by": self.approved_by,
            "approval_note": self.approval_note,
            "digest": self.digest,
            "runtime_authority": "none",
            "executed": False,
        }


class LearningPreparationGuard:
    """Fail closed when a preparation payload attempts direct neural mutation.

    The guard validates mapping keys, not prose.  An AI may discuss why STDP or
    rewards are relevant, but a proposal must not carry executable fields such as
    a weight matrix, a target spike train, injected currents or reward values.
    """

    _FORBIDDEN_KEYS = frozenset(
        {
            "weight",
            "weights",
            "synapse_weight",
            "synapse_weights",
            "weight_matrix",
            "spike",
            "spikes",
            "spike_pattern",
            "spike_train",
            "target_spikes",
            "target_pattern",
            "current",
            "currents",
            "injected_current",
            "injected_currents",
            "reward",
            "reward_value",
            "reward_values",
            "eligibility",
            "eligibility_trace",
            "plasticity_update",
            "set_weight",
        }
    )

    @classmethod
    def validate_mapping(cls, payload: Mapping[str, Any]) -> None:
        """Reject direct neural-control fields anywhere in a nested proposal."""

        cls._validate_value(payload, path="proposal")

    @classmethod
    def validate_partition_leakage(
        cls,
        sources: Sequence[LearningSourceRef],
        *,
        ai_label_digests: set[str] | None = None,
        gold_label_digests: set[str] | None = None,
    ) -> None:
        """Reject digest overlap and labels exposed through the holdout set."""
        seen: dict[str, LearningDataPartition] = {}
        for source in sources:
            previous = seen.get(source.digest)
            if previous is not None and previous is not source.partition:
                raise ValueError("data leakage detected across learning partitions")
            seen[source.digest] = source.partition

        holdout = {
            source.digest
            for source in sources
            if source.partition is LearningDataPartition.HOLDOUT
        }
        forbidden = (ai_label_digests or set()) | (gold_label_digests or set())
        if holdout & forbidden:
            raise ValueError("learning holdout must not contain label records")

    @classmethod
    def _validate_value(cls, value: Any, *, path: str) -> None:
        if isinstance(value, Mapping):
            typed_value = cast(Mapping[Any, Any], value)
            for key, child in typed_value.items():
                normalized = str(key).strip().lower()
                if normalized in cls._FORBIDDEN_KEYS:
                    raise PermissionError(
                        f"learning preparation cannot carry direct neural mutation field: {path}.{key}"
                    )
                cls._validate_value(child, path=f"{path}.{key}")
            return
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            typed_value = cast(Sequence[Any], value)
            for index, child in enumerate(typed_value):
                cls._validate_value(child, path=f"{path}[{index}]")


class LearningPreparationService:
    """Create, approve, and persist preparation artifacts without executing learning."""

    def __init__(self, storage_root: Path | None = None) -> None:
        self._storage_root = storage_root

    def persist_proposal(self, proposal: LearningPreparationProposal) -> Path:
        """Persist one immutable proposal and return its artifact path."""
        return self._persist(proposal.plan_id, proposal.to_dict())

    def persist_approved(self, plan: PreparedLearningPlan) -> Path:
        """Persist one approved plan without granting runtime authority."""
        return self._persist(f"{plan.proposal.plan_id}-approved", plan.to_dict())

    def load_proposal(self, plan_id: str) -> LearningPreparationProposal:
        """Load a proposal for explicit human approval."""
        payload = self._load(plan_id)
        proposal_payload = payload.get("proposal", payload)
        if not isinstance(proposal_payload, Mapping):
            raise ValueError("stored preparation proposal must be an object")
        return self._proposal_from_dict(cast(Mapping[str, Any], proposal_payload))

    def list_plans(self) -> list[dict[str, Any]]:
        """Return stored preparation artifacts in stable order."""
        if self._storage_root is None or not self._storage_root.is_dir():
            return []
        return [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(self._storage_root.glob("*.json"))
        ]

    def _persist(self, plan_id: str, payload: dict[str, Any]) -> Path:
        if self._storage_root is None:
            raise ValueError("storage_root is required for persistence")
        self._storage_root.mkdir(parents=True, exist_ok=True)
        path = self._storage_root / f"{plan_id}.json"
        if path.exists():
            raise FileExistsError(f"learning preparation already exists: {plan_id}")
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def _load(self, plan_id: str) -> dict[str, Any]:
        if self._storage_root is None:
            raise ValueError("storage_root is required for persistence")
        path = self._storage_root / f"{plan_id}.json"
        if not path.is_file():
            raise FileNotFoundError(plan_id)
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise ValueError("stored preparation must be an object")
        return cast(dict[str, Any], loaded)

    @staticmethod
    def _proposal_from_dict(payload: Mapping[str, Any]) -> LearningPreparationProposal:
        objective_payload = payload.get("objective")
        if not isinstance(objective_payload, Mapping):
            raise ValueError("objective object is required")
        sources_payload = payload.get("sources", [])
        if not isinstance(sources_payload, Sequence) or isinstance(sources_payload, (str, bytes)):
            raise ValueError("sources must be a list")
        typed_sources = cast(Sequence[Any], sources_payload)
        sources = tuple(
            LearningPreparationService._source_from_dict(
                cast(Mapping[str, Any], source)
            )
            for source in typed_sources
            if isinstance(source, Mapping)
        )
        typed_objective = cast(Mapping[str, Any], objective_payload)
        return LearningPreparationProposal(
            plan_id=str(payload["plan_id"]),
            objective=LearningObjective(
                objective_id=str(typed_objective["objective_id"]),
                description=str(typed_objective["description"]),
                success_metric=str(typed_objective["success_metric"]),
                evaluation_question=str(typed_objective["evaluation_question"]),
            ),
            sources=sources,
            baseline_protocol=str(payload["baseline_protocol"]),
            exposure_protocol=str(payload["exposure_protocol"]),
            evaluation_protocol=str(payload["evaluation_protocol"]),
            stopping_rule=str(payload["stopping_rule"]),
            controls=tuple(str(value) for value in payload.get("controls", [])),
            origin=LearningPlanOrigin(str(payload.get("origin", LearningPlanOrigin.HUMAN.value))),
            rationale=str(payload.get("rationale", "")),
            ai_interaction_id=payload.get("ai_interaction_id"),
        )

    @staticmethod
    def _source_from_dict(source: Mapping[str, Any]) -> LearningSourceRef:
        return LearningSourceRef(
            source_id=str(source["source_id"]),
            digest=str(source["digest"]),
            origin=str(source["origin"]),
            partition=LearningDataPartition(str(source["partition"])),
            trust=str(source.get("trust", "UNKNOWN")),
        )

    def create_proposal(
        self,
        *,
        plan_id: str,
        objective: LearningObjective,
        sources: Sequence[LearningSourceRef],
        baseline_protocol: str,
        exposure_protocol: str,
        evaluation_protocol: str,
        stopping_rule: str,
        controls: Sequence[str] = (),
        origin: LearningPlanOrigin = LearningPlanOrigin.HUMAN,
        rationale: str = "",
        ai_interaction_id: str | None = None,
        raw_proposal_payload: Mapping[str, Any] | None = None,
    ) -> LearningPreparationProposal:
        if raw_proposal_payload is not None:
            LearningPreparationGuard.validate_mapping(raw_proposal_payload)
        LearningPreparationGuard.validate_partition_leakage(sources)
        return LearningPreparationProposal(
            plan_id=plan_id,
            objective=objective,
            sources=tuple(sources),
            baseline_protocol=baseline_protocol,
            exposure_protocol=exposure_protocol,
            evaluation_protocol=evaluation_protocol,
            stopping_rule=stopping_rule,
            controls=tuple(str(value) for value in controls),
            origin=origin,
            rationale=rationale,
            ai_interaction_id=ai_interaction_id,
        )
    def approve(
        self,
        proposal: LearningPreparationProposal,
        *,
        approved_by: str,
        approval_note: str = "",
    ) -> PreparedLearningPlan:
        return PreparedLearningPlan(
            proposal=proposal,
            approved_by=approved_by,
            approval_note=approval_note,
        )


def _required_capture_field(capture: Mapping[str, Any], name: str) -> str:
    value = capture.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"environment capture {name} must be a non-empty string")
    return value.strip()


__all__ = [
    "LearningDataPartition",
    "LearningObjective",
    "LearningPlanOrigin",
    "LearningPreparationGuard",
    "LearningPreparationProposal",
    "LearningPreparationService",
    "LearningSourceRef",
    "PreparedLearningPlan",
]
