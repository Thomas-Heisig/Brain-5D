"""Versioned governance contracts for reproducible AI research runs."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Mapping


class NetworkMode(StrEnum):
    """Explicit network policy for an AI or research run."""

    OFFLINE = "OFFLINE"
    FROZEN_CORPUS = "FROZEN_CORPUS"
    LIVE_NETWORK = "LIVE_NETWORK"


class ResearchRunMode(StrEnum):
    """Whether a run may change its protocol while being developed."""

    EXPLORATORY = "EXPLORATORY"
    CONFIRMATORY = "CONFIRMATORY"


class DataPartition(StrEnum):
    """Declared partition for data and labels used by a research run."""

    DEVELOPMENT = "DEVELOPMENT"
    VALIDATION = "VALIDATION"
    SCIENTIFIC_HOLDOUT = "SCIENTIFIC_HOLDOUT"


def validate_network_mode(mode: NetworkMode, *, scientific_run: bool) -> None:
    """Reject live network access for scientific runs unless explicitly non-scientific."""
    if scientific_run and mode is NetworkMode.LIVE_NETWORK:
        raise ValueError("Scientific runs require OFFLINE or FROZEN_CORPUS network mode")


class KnowledgeOrigin(StrEnum):
    """Declared origin of knowledge used by a run or response."""

    SNN_LEARNED = "SNN_LEARNED"
    LLM_PRIOR = "LLM_PRIOR"
    EXTERNAL_RETRIEVAL = "EXTERNAL_RETRIEVAL"
    HUMAN_INPUT = "HUMAN_INPUT"
    SENSOR_OBSERVATION = "SENSOR_OBSERVATION"
    SYSTEM_STATE = "SYSTEM_STATE"
    SIMULATED_ENVIRONMENT = "SIMULATED_ENVIRONMENT"
    DERIVED = "DERIVED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class VersionedPrompt:
    """An immutable prompt with a protocol version and canonical digest."""

    prompt_id: str
    version: int
    text: str
    protocol_digest: str

    @classmethod
    def create(cls, prompt_id: str, version: int, text: str) -> VersionedPrompt:
        if not prompt_id.strip() or not text.strip():
            raise ValueError("Prompt ID and text must not be empty")
        if version < 1:
            raise ValueError("Prompt version must be positive")
        canonical = json.dumps(
            {"prompt_id": prompt_id, "version": version, "text": text},
            sort_keys=True,
            ensure_ascii=True,
            separators=(",", ":"),
        )
        return cls(
            prompt_id=prompt_id,
            version=version,
            text=text,
            protocol_digest=hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "prompt_id": self.prompt_id,
            "version": self.version,
            "text": self.text,
            "protocol_digest": self.protocol_digest,
        }


class PromptRegistry:
    """In-memory immutable registry; duplicate IDs must be byte-identical."""

    def __init__(self) -> None:
        self._prompts: dict[tuple[str, int], VersionedPrompt] = {}

    def register(self, prompt: VersionedPrompt) -> str:
        key = (prompt.prompt_id, prompt.version)
        existing = self._prompts.get(key)
        if existing is not None and existing != prompt:
            raise ValueError("Prompt version is already registered with different content")
        self._prompts[key] = prompt
        return prompt.protocol_digest

    def get(self, prompt_id: str, version: int) -> VersionedPrompt:
        try:
            return self._prompts[(prompt_id, version)]
        except KeyError as exc:
            raise KeyError(f"Unknown prompt version: {prompt_id}@{version}") from exc

    def load_directory(self, directory: Path) -> None:
        """Load frozen ``*.vN.json`` prompt files without overwriting versions."""
        for path in sorted(directory.glob("*.json")):
            raw = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raise ValueError(f"Prompt file must contain an object: {path}")
            prompt = VersionedPrompt.create(
                str(raw.get("prompt_id", "")),
                int(raw.get("version", 0)),
                str(raw.get("text", "")),
            )
            expected_digest = raw.get("protocol_digest")
            if expected_digest != prompt.protocol_digest:
                raise ValueError(f"Prompt digest mismatch: {path}")
            self.register(prompt)


@dataclass(frozen=True, slots=True)
class PreregistrationLock:
    """Digest lock for hypotheses, metrics, seeds, stopping and exclusions."""

    protocol_id: str
    protocol_version: int
    protocol_digest: str
    locked: bool = True

    @classmethod
    def create(
        cls, protocol_id: str, protocol_version: int, protocol: Mapping[str, object]
    ) -> PreregistrationLock:
        if not protocol_id.strip() or protocol_version < 1:
            raise ValueError("Protocol ID must be non-empty and version positive")
        canonical = json.dumps(dict(protocol), sort_keys=True, ensure_ascii=True, separators=(",", ":"))
        return cls(
            protocol_id=protocol_id,
            protocol_version=protocol_version,
            protocol_digest=hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        )

    def validate(self, protocol: Mapping[str, object]) -> None:
        canonical = json.dumps(dict(protocol), sort_keys=True, ensure_ascii=True, separators=(",", ":"))
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        if self.locked and digest != self.protocol_digest:
            raise ValueError("Preregistration lock rejects changed protocol content")


@dataclass(frozen=True, slots=True)
class ConfirmatoryRunLock:
    """Immutable lock for confirmatory hypotheses, prompts, and analysis."""

    protocol_digest: str
    prompt_digest: str
    analysis_digest: str
    locked: bool = True

    @classmethod
    def create(
        cls,
        *,
        protocol: Mapping[str, object],
        prompt_digest: str,
        analysis_digest: str,
    ) -> ConfirmatoryRunLock:
        if not prompt_digest.strip() or not analysis_digest.strip():
            raise ValueError("Confirmatory lock requires prompt and analysis digests")
        canonical = json.dumps(dict(protocol), sort_keys=True, ensure_ascii=True, separators=(",", ":"))
        return cls(
            protocol_digest=hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
            prompt_digest=prompt_digest,
            analysis_digest=analysis_digest,
        )

    def validate(
        self,
        *,
        protocol: Mapping[str, object],
        prompt_digest: str,
        analysis_digest: str,
    ) -> None:
        canonical = json.dumps(dict(protocol), sort_keys=True, ensure_ascii=True, separators=(",", ":"))
        protocol_digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        if self.locked and (
            protocol_digest != self.protocol_digest
            or prompt_digest != self.prompt_digest
            or analysis_digest != self.analysis_digest
        ):
            raise ValueError("Confirmatory run lock rejects protocol, prompt, or analysis changes")


def validate_data_partition(partition: DataPartition, *, scientific_run: bool) -> None:
    """Prevent scientific runs from silently using development data."""
    if scientific_run and partition is DataPartition.DEVELOPMENT:
        raise ValueError("Scientific runs cannot use DEVELOPMENT data")


def validate_data_leakage(
    partition_digests: Mapping[DataPartition, set[str]],
    *,
    ai_label_digests: set[str] | None = None,
    gold_label_digests: set[str] | None = None,
) -> None:
    """Reject partition overlap and labels present in the scientific holdout."""
    seen: dict[str, DataPartition] = {}
    for partition, digests in partition_digests.items():
        for digest in digests:
            previous = seen.get(digest)
            if previous is not None and previous is not partition:
                raise ValueError("Data leakage detected across research partitions")
            seen[digest] = partition
    holdout = partition_digests.get(DataPartition.SCIENTIFIC_HOLDOUT, set())
    if holdout & (ai_label_digests or set()) or holdout & (gold_label_digests or set()):
        raise ValueError("Scientific holdout must not contain AI or gold-label records")


@dataclass(frozen=True, slots=True)
class RetrievalRecord:
    """Visible, versioned retrieval provenance; no hidden RAG is implied."""

    enabled: bool
    mode: NetworkMode
    snapshot_digest: str
    source_count: int
    knowledge_origin: KnowledgeOrigin

    def __post_init__(self) -> None:
        if self.source_count < 0:
            raise ValueError("Retrieval source_count must not be negative")
        if self.enabled and not self.snapshot_digest.strip():
            raise ValueError("Enabled retrieval requires a snapshot digest")
        if not self.enabled and self.source_count:
            raise ValueError("Disabled retrieval cannot contain sources")

    def to_dict(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "mode": self.mode.value,
            "snapshot_digest": self.snapshot_digest,
            "source_count": self.source_count,
            "knowledge_origin": self.knowledge_origin.value,
        }
