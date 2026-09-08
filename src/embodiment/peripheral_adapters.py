"""Experiment-only peripheral adapters for Neural Symbiosis studies.

The production runtime must never instantiate these adapters. They exist only
for preregistered experiments and expose no MHRN core object or synapse state.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Final

from .models import JSONValue

PRODUCTION_PERIPHERAL_ACTIVATION_ENABLED: Final = False
_EXPERIMENT_ONLY_ADAPTERS: Final = frozenset(
    {"DeterministicPeripheralAdapter", "VirtualLogicAdapter"}
)


def _required_text(value: str, field: str) -> str:
    result = value.strip()
    if not result:
        raise ValueError(f"{field} must not be empty")
    return result


def _sha256_hex(value: str, field: str) -> str:
    candidate = value.strip().lower()
    if len(candidate) != 64 or any(
        char not in "0123456789abcdef" for char in candidate
    ):
        raise ValueError(f"{field} must be a 64-character SHA-256 hex digest")
    return candidate


@dataclass(frozen=True, slots=True)
class AdapterDeclaration:
    """Frozen identity of one peripheral network or virtual processing area."""

    area_id: str
    adapter_class: str
    framework: str
    model: str
    version: str
    artifact_sha256: str
    endpoint_identity: str
    modality: str
    transform: str = "identity"

    def __post_init__(self) -> None:
        for field in (
            "area_id",
            "adapter_class",
            "framework",
            "model",
            "version",
            "endpoint_identity",
            "modality",
            "transform",
        ):
            object.__setattr__(
                self, field, _required_text(str(getattr(self, field)), field)
            )
        object.__setattr__(
            self,
            "artifact_sha256",
            _sha256_hex(self.artifact_sha256, "artifact_sha256"),
        )
        if self.adapter_class not in _EXPERIMENT_ONLY_ADAPTERS:
            raise ValueError(
                f"adapter_class is not an approved experiment-only adapter: {self.adapter_class}"
            )
        if self.transform not in {"identity", "threshold_features", "virtual_logic"}:
            raise ValueError(
                f"unsupported experiment adapter transform: {self.transform}"
            )

    def provenance(self) -> dict[str, JSONValue]:
        record: dict[str, JSONValue] = {
            "area_id": self.area_id,
            "adapter_class": self.adapter_class,
            "framework": self.framework,
            "model": self.model,
            "version": self.version,
            "artifact_sha256": self.artifact_sha256,
            "endpoint_identity": self.endpoint_identity,
            "modality": self.modality,
            "transform": self.transform,
            "scope": "experiment_only",
            "production_activation_enabled": False,
        }
        encoded = json.dumps(record, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
        record["provenance_sha256"] = hashlib.sha256(encoded).hexdigest()
        return record


class DeterministicPeripheralAdapter:
    """Small deterministic adapter used only to exercise the gateway contract."""

    def __init__(self, declaration: AdapterDeclaration) -> None:
        self.declaration = declaration

    @property
    def area_id(self) -> str:
        return self.declaration.area_id

    @property
    def architecture(self) -> str:
        return self.declaration.model

    def process(self, payload: JSONValue, tick: int) -> JSONValue:
        if tick < 0:
            raise ValueError("tick must be non-negative")
        if self.declaration.transform == "identity":
            return payload
        if self.declaration.transform == "virtual_logic":
            truth = bool(payload)
            return {"truth": truth, "tick": tick}
        return self._threshold_features(payload, tick)

    @staticmethod
    def _threshold_features(payload: JSONValue, tick: int) -> JSONValue:
        if not isinstance(payload, list):
            raise ValueError("threshold_features requires a JSON list")
        features: list[JSONValue] = []
        for item in payload:
            if isinstance(item, bool) or not isinstance(item, (int, float)):
                raise ValueError("threshold_features requires numeric list values")
            features.append(1 if float(item) >= 0.0 else -1)
        return {"features": features, "tick": tick}


class VirtualLogicAdapter(DeterministicPeripheralAdapter):
    """Declared virtual-area adapter with the same experiment-only boundary."""


class ExperimentAdapterFactory:
    """Instantiate declared adapters only when an experiment gate is explicit."""

    @staticmethod
    def create(
        declaration: AdapterDeclaration,
        *,
        experiment_mode: bool,
        production_activation: bool = False,
    ) -> DeterministicPeripheralAdapter:
        if production_activation or PRODUCTION_PERIPHERAL_ACTIVATION_ENABLED:
            raise RuntimeError("production peripheral activation is disabled")
        if not experiment_mode:
            raise RuntimeError("peripheral adapters require explicit experiment mode")
        adapter_type = (
            VirtualLogicAdapter
            if declaration.adapter_class == "VirtualLogicAdapter"
            else DeterministicPeripheralAdapter
        )
        return adapter_type(declaration)


def declaration_artifact_hash(value: object) -> str:
    """Hash a declarative model artifact without executing or importing it."""

    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


__all__ = [
    "AdapterDeclaration",
    "DeterministicPeripheralAdapter",
    "ExperimentAdapterFactory",
    "PRODUCTION_PERIPHERAL_ACTIVATION_ENABLED",
    "VirtualLogicAdapter",
    "declaration_artifact_hash",
]
