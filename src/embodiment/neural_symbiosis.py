"""Embodiment-only contracts for peripheral neural-network symbiosis.

This module deliberately does not import or mutate the Brain-5D neural core.
It describes peripheral neural/virtual processing areas, read-only topology
publication and pure gateway mathematics that experiments may opt into later.

Cataloguing an area or calculating a candidate gateway update is not evidence
that the core learned to use it.
"""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol, cast, runtime_checkable

from .models import JSONValue


class AreaKind(StrEnum):
    """Kinds of peripheral processing areas exposed by the embodiment layer."""

    NEURAL = "neural"
    VIRTUAL = "virtual"


class PipelineDirection(StrEnum):
    """Direction of information flow relative to the Brain-5D core."""

    AFFERENT = "afferent"
    EFFERENT = "efferent"
    COGNITIVE = "cognitive"


@runtime_checkable
class NetworkAreaAdapter(Protocol):
    """Framework-neutral adapter contract for any peripheral network type."""

    @property
    def area_id(self) -> str:
        """Return the stable area identifier."""
        ...

    @property
    def architecture(self) -> str:
        """Return an implementation-defined architecture/family label."""
        ...

    def process(self, payload: JSONValue, tick: int) -> JSONValue:
        """Process one payload without direct access to Brain-5D core state."""
        ...


@dataclass(frozen=True, slots=True)
class AreaDescriptor:
    """One neural or virtual peripheral area available to a pipeline."""

    area_id: str
    name: str
    kind: AreaKind
    architecture: str
    roles: tuple[str, ...]
    input_modalities: tuple[str, ...]
    output_modalities: tuple[str, ...]
    dedicated_connections: tuple[str, ...] = ()
    backend_contract: str = "NetworkAreaAdapter"
    implementation_status: str = "adapter_required"

    def to_json(self) -> dict[str, JSONValue]:
        """Return a JSON-ready descriptor."""

        return {
            "area_id": self.area_id,
            "name": self.name,
            "kind": self.kind.value,
            "architecture": self.architecture,
            "roles": list(self.roles),
            "input_modalities": list(self.input_modalities),
            "output_modalities": list(self.output_modalities),
            "dedicated_connections": list(self.dedicated_connections),
            "backend_contract": self.backend_contract,
            "implementation_status": self.implementation_status,
        }


@dataclass(frozen=True, slots=True)
class PlasticGatewayConfig:
    """Candidate parameters for opt-in embodiment gateway experiments.

    Defaults are deliberately inert. Enabling learning belongs in an explicit,
    preregistered experiment and must not silently alter canonical core rules.
    """

    weight_min: float = 0.0
    weight_max: float = 1.0
    eta_plus: float = 0.01
    eta_minus: float = 0.012
    tau_plus_ms: float = 10.0
    tau_minus_ms: float = 20.0
    homeostatic_alpha: float = 0.01
    target_rate_hz: float = 5.0
    structural_eta: float = 0.001
    pruning_eta: float = 0.001
    gate_learning_eta: float = 0.001
    synaptic_plasticity_enabled: bool = False
    structural_plasticity_enabled: bool = False
    efferent_gating_enabled: bool = False

    def to_json(self) -> dict[str, JSONValue]:
        """Return the explicit, fail-closed gateway configuration."""

        return {
            "weight_min": self.weight_min,
            "weight_max": self.weight_max,
            "eta_plus": self.eta_plus,
            "eta_minus": self.eta_minus,
            "tau_plus_ms": self.tau_plus_ms,
            "tau_minus_ms": self.tau_minus_ms,
            "homeostatic_alpha": self.homeostatic_alpha,
            "target_rate_hz": self.target_rate_hz,
            "structural_eta": self.structural_eta,
            "pruning_eta": self.pruning_eta,
            "gate_learning_eta": self.gate_learning_eta,
            "synaptic_plasticity_enabled": self.synaptic_plasticity_enabled,
            "structural_plasticity_enabled": self.structural_plasticity_enabled,
            "efferent_gating_enabled": self.efferent_gating_enabled,
            "requires_preregistration": True,
            "requires_experiment_mode": True,
            "core_learning_rules_unchanged": True,
        }


@dataclass(frozen=True, slots=True)
class PipelineTemplate:
    """One possible peripheral pipeline around the core boundary."""

    pipeline_id: str
    name: str
    direction: PipelineDirection
    stages: tuple[str, ...]
    source_connection: str | None = None
    sink_connection: str | None = None
    purpose: str = ""

    def to_json(self, available_connections: set[str]) -> dict[str, JSONValue]:
        """Return pipeline state without enabling or instantiating any stage."""

        source_reachable = self._endpoint_reachable(
            self.source_connection, available_connections
        )
        sink_reachable = self._endpoint_reachable(
            self.sink_connection, available_connections
        )
        return {
            "pipeline_id": self.pipeline_id,
            "name": self.name,
            "direction": self.direction.value,
            "source_connection": self.source_connection,
            "sink_connection": self.sink_connection,
            "stages": list(self.stages),
            "purpose": self.purpose,
            "reachable": source_reachable and sink_reachable,
            "enabled": False,
            "instantiated": False,
            "gateway_learning": "disabled",
        }

    @staticmethod
    def _endpoint_reachable(endpoint: str | None, available: set[str]) -> bool:
        if endpoint is None or endpoint.startswith("virtual."):
            return True
        return any(
            item == endpoint or item.startswith(f"{endpoint}.") for item in available
        )


class NeuralSymbiosisCatalog:
    """Extensible catalog of neural areas and safe pipeline templates."""

    def __init__(self, *, gateway: PlasticGatewayConfig | None = None) -> None:
        self._areas: dict[str, AreaDescriptor] = {
            area.area_id: area for area in default_area_catalog()
        }
        self._pipelines: dict[str, PipelineTemplate] = {
            item.pipeline_id: item for item in default_pipeline_catalog()
        }
        self.gateway = gateway or PlasticGatewayConfig()

    def register_area(self, descriptor: AreaDescriptor) -> None:
        """Register an arbitrary architecture through the embodiment contract."""

        area_id = descriptor.area_id.strip()
        if not area_id:
            raise ValueError("area_id must not be empty")
        if area_id in self._areas:
            raise ValueError(f"area already registered: {area_id}")
        self._areas[area_id] = descriptor

    def register_pipeline(self, pipeline: PipelineTemplate) -> None:
        """Register one additional pipeline template."""

        pipeline_id = pipeline.pipeline_id.strip()
        if not pipeline_id:
            raise ValueError("pipeline_id must not be empty")
        if pipeline_id in self._pipelines:
            raise ValueError(f"pipeline already registered: {pipeline_id}")
        unknown = [stage for stage in pipeline.stages if not self._known_stage(stage)]
        if unknown:
            raise ValueError(f"unknown pipeline stages: {', '.join(unknown)}")
        self._pipelines[pipeline_id] = pipeline

    def to_json(self, connections: Iterable[object]) -> dict[str, JSONValue]:
        """Publish the read-only catalog and endpoint reachability state."""

        available = {
            str(getattr(item, "connection_id"))
            for item in connections
            if bool(getattr(item, "available", False))
            and getattr(item, "connection_id", None)
        }
        pipeline_payloads = [
            self._pipelines[key].to_json(available) for key in sorted(self._pipelines)
        ]
        reachable = sum(bool(item["reachable"]) for item in pipeline_payloads)
        return {
            "name": "Neural Symbiosis",
            "scope": "embodiment",
            "status": "experimental_contract",
            "areas": [self._areas[key].to_json() for key in sorted(self._areas)],
            "pipelines": cast(list[JSONValue], pipeline_payloads),
            "reachable_pipelines": reachable,
            "gateway": self.gateway.to_json(),
            "adapter_contract": {
                "protocol": "NetworkAreaAdapter",
                "architecture_open_set": True,
                "framework_neutral": True,
                "supported_backends": [
                    "pytorch",
                    "tensorflow",
                    "jax",
                    "onnx-runtime",
                    "remote-service",
                    "custom",
                ],
            },
            "scientific_boundary": {
                "embodiment_only": True,
                "read_only_publication": True,
                "core_imports": False,
                "core_mutation": False,
                "canonical_learning_rules_unchanged": True,
                "historical_data_unchanged": True,
                "catalog_presence_is_not_evidence": True,
                "pipeline_reachability_is_not_activation": True,
                "activation_requires_explicit_experiment": True,
            },
        }

    def _known_stage(self, stage: str) -> bool:
        return stage in self._areas or stage in {
            "brain5d.core",
            "gateway.afferent",
            "gateway.efferent",
            "gateway.cognitive",
        }


def _area(
    area_id: str,
    name: str,
    architecture: str,
    roles: tuple[str, ...],
    inputs: tuple[str, ...],
    outputs: tuple[str, ...],
    connections: tuple[str, ...] = (),
    *,
    kind: AreaKind = AreaKind.NEURAL,
    status: str = "adapter_required",
) -> AreaDescriptor:
    return AreaDescriptor(
        area_id=area_id,
        name=name,
        kind=kind,
        architecture=architecture,
        roles=roles,
        input_modalities=inputs,
        output_modalities=outputs,
        dedicated_connections=connections,
        implementation_status=status,
    )


def default_area_catalog() -> tuple[AreaDescriptor, ...]:
    """Return common network families while keeping architecture an open set."""

    return (
        _area(
            "vision.cnn",
            "Vision CNN",
            "CNN",
            ("perception", "feature_extraction"),
            ("image", "video"),
            ("features",),
            ("sensor.camera",),
        ),
        _area(
            "vision.transformer",
            "Vision Transformer",
            "Vision Transformer",
            ("perception", "attention"),
            ("image", "features"),
            ("tokens", "features"),
            ("sensor.camera",),
        ),
        _area(
            "audio.cnn",
            "Audio CNN",
            "CNN",
            ("perception", "spectral_features"),
            ("audio", "spectrogram"),
            ("features",),
            ("sensor.microphone",),
        ),
        _area(
            "audio.transformer",
            "Audio Transformer",
            "Transformer",
            ("perception", "sequence"),
            ("audio", "features"),
            ("tokens", "features"),
            ("sensor.microphone",),
        ),
        _area(
            "speech.transformer",
            "Speech Transformer",
            "Transformer",
            ("speech_recognition", "speech_synthesis"),
            ("audio", "text", "latent"),
            ("text", "audio", "latent"),
            ("sensor.microphone", "actuator.audio"),
        ),
        _area(
            "language.transformer",
            "Language Transformer",
            "Transformer",
            ("language", "translation", "semantic_projection"),
            ("text", "tokens", "latent"),
            ("text", "tokens", "latent"),
        ),
        _area(
            "sequence.lstm",
            "Sequence LSTM",
            "LSTM",
            ("sequence", "temporal_context"),
            ("sequence", "features"),
            ("features", "latent"),
        ),
        _area(
            "sequence.gru",
            "Sequence GRU",
            "GRU",
            ("sequence", "temporal_context"),
            ("sequence", "features"),
            ("features", "latent"),
        ),
        _area(
            "sequence.rnn",
            "Recurrent Network",
            "RNN",
            ("sequence", "recurrence"),
            ("sequence", "features"),
            ("features", "latent"),
        ),
        _area(
            "graph.gnn",
            "Graph Network",
            "GNN",
            ("graph_reasoning", "relational_projection"),
            ("graph", "records"),
            ("features", "latent"),
        ),
        _area(
            "memory.hopfield",
            "Associative Memory",
            "Modern Hopfield Network",
            ("associative_memory", "retrieval"),
            ("latent", "features"),
            ("latent", "features"),
        ),
        _area(
            "reservoir.esn",
            "Reservoir Network",
            "Echo State Network",
            ("reservoir", "temporal_dynamics"),
            ("sequence", "features"),
            ("features", "latent"),
        ),
        _area(
            "control.mlp",
            "Control MLP",
            "MLP",
            ("control", "decoding"),
            ("latent", "features"),
            ("control",),
            ("actuator.robotics",),
        ),
        _area(
            "generative.vae",
            "Variational Autoencoder",
            "VAE",
            ("compression", "generation", "imagination"),
            ("features", "latent"),
            ("features", "latent"),
        ),
        _area(
            "generative.gan",
            "Generative Adversarial Network",
            "GAN",
            ("generation", "imagination"),
            ("latent",),
            ("image", "features"),
        ),
        _area(
            "generative.diffusion",
            "Diffusion Network",
            "Diffusion",
            ("generation", "imagination"),
            ("latent", "text", "features"),
            ("image", "audio", "latent"),
        ),
        _area(
            "autoencoder.generic",
            "Autoencoder",
            "Autoencoder",
            ("compression", "representation"),
            ("features",),
            ("features", "latent"),
        ),
        _area(
            "spiking.peripheral",
            "Peripheral SNN",
            "SNN",
            ("spike_encoding", "event_processing"),
            ("events", "features"),
            ("spikes",),
        ),
        _area(
            "multimodal.transformer",
            "Multimodal Transformer",
            "Multimodal Transformer",
            ("fusion", "cross_modal_attention"),
            ("image", "audio", "text", "features"),
            ("tokens", "latent"),
        ),
        _area(
            "neurosymbolic.mlp",
            "Neuro-symbolic Projector",
            "MLP",
            ("symbol_projection", "encoding", "decoding"),
            ("symbols", "records", "latent"),
            ("features", "latent", "symbols"),
        ),
        _area(
            "virtual.logic",
            "Logic Engine",
            "symbolic",
            ("logic", "constraints"),
            ("symbols", "facts"),
            ("symbols", "facts"),
            kind=AreaKind.VIRTUAL,
            status="virtual_adapter_required",
        ),
        _area(
            "virtual.knowledge",
            "Knowledge Store",
            "database_or_knowledge_graph",
            ("retrieval", "knowledge"),
            ("query", "records"),
            ("records", "graph"),
            ("data.database",),
            kind=AreaKind.VIRTUAL,
            status="virtual_adapter_required",
        ),
        _area(
            "custom.network",
            "Custom Neural Area",
            "open-set",
            ("custom",),
            ("any",),
            ("any",),
            status="registration_contract",
        ),
    )


def default_pipeline_catalog() -> tuple[PipelineTemplate, ...]:
    """Return safe, disabled templates for real and virtual embodiment paths."""

    return (
        PipelineTemplate(
            "camera.vision",
            "Camera → visual cortex → core",
            PipelineDirection.AFFERENT,
            (
                "vision.cnn",
                "vision.transformer",
                "gateway.afferent",
                "brain5d.core",
            ),
            source_connection="sensor.camera",
            purpose="Visual feature and attention pipeline.",
        ),
        PipelineTemplate(
            "microphone.audio",
            "Microphone → auditory pipeline → core",
            PipelineDirection.AFFERENT,
            (
                "audio.cnn",
                "audio.transformer",
                "gateway.afferent",
                "brain5d.core",
            ),
            source_connection="sensor.microphone",
            purpose="Acoustic feature pipeline before the core boundary.",
        ),
        PipelineTemplate(
            "microphone.speech",
            "Microphone → speech/language → core",
            PipelineDirection.AFFERENT,
            (
                "audio.cnn",
                "speech.transformer",
                "language.transformer",
                "gateway.afferent",
                "brain5d.core",
            ),
            source_connection="sensor.microphone",
            purpose="Optional speech and language projection pipeline.",
        ),
        PipelineTemplate(
            "web.language",
            "Web/API → language area → core",
            PipelineDirection.AFFERENT,
            ("language.transformer", "gateway.afferent", "brain5d.core"),
            source_connection="data.web_api",
            purpose="Structured/text external data projection.",
        ),
        PipelineTemplate(
            "database.knowledge",
            "Database → knowledge/graph areas → core",
            PipelineDirection.AFFERENT,
            (
                "virtual.knowledge",
                "graph.gnn",
                "gateway.afferent",
                "brain5d.core",
            ),
            source_connection="data.database",
            purpose="Knowledge retrieval and relational projection.",
        ),
        PipelineTemplate(
            "logic.cognitive",
            "Logic → neuro-symbolic projection → core",
            PipelineDirection.COGNITIVE,
            (
                "virtual.logic",
                "neurosymbolic.mlp",
                "gateway.cognitive",
                "brain5d.core",
            ),
            source_connection="virtual.logic",
            purpose="Virtual symbolic constraint/logic path.",
        ),
        PipelineTemplate(
            "memory.cognitive",
            "Associative memory ↔ core",
            PipelineDirection.COGNITIVE,
            ("memory.hopfield", "gateway.cognitive", "brain5d.core"),
            source_connection="virtual.memory",
            purpose="Optional associative peripheral memory path.",
        ),
        PipelineTemplate(
            "core.audio",
            "Core → language/speech → audio output",
            PipelineDirection.EFFERENT,
            (
                "brain5d.core",
                "gateway.efferent",
                "language.transformer",
                "speech.transformer",
            ),
            sink_connection="actuator.audio",
            purpose="Dedicated neural stages before audible output.",
        ),
        PipelineTemplate(
            "core.display",
            "Core → multimodal decoder → display",
            PipelineDirection.EFFERENT,
            ("brain5d.core", "gateway.efferent", "multimodal.transformer"),
            sink_connection="actuator.display",
            purpose="Visual output preparation before the display endpoint.",
        ),
        PipelineTemplate(
            "core.printer",
            "Core → language/document projection → printer",
            PipelineDirection.EFFERENT,
            ("brain5d.core", "gateway.efferent", "language.transformer"),
            sink_connection="actuator.printer",
            purpose="Document/content projection before printing.",
        ),
        PipelineTemplate(
            "core.robotics",
            "Core → neural control → robotics",
            PipelineDirection.EFFERENT,
            (
                "brain5d.core",
                "gateway.efferent",
                "sequence.gru",
                "control.mlp",
            ),
            sink_connection="actuator.robotics",
            purpose="Temporal control and decoding before a robotics adapter.",
        ),
    )


def pair_stdp_delta(
    weight: float, delta_t_ms: float, config: PlasticGatewayConfig
) -> float:
    """Return one bounded pair-based STDP delta for a candidate gateway weight."""

    bounded_weight = min(config.weight_max, max(config.weight_min, weight))
    if delta_t_ms > 0.0:
        amplitude = config.eta_plus * (config.weight_max - bounded_weight)
        return amplitude * math.exp(-delta_t_ms / config.tau_plus_ms)
    amplitude = config.eta_minus * (bounded_weight - config.weight_min)
    return -amplitude * math.exp(delta_t_ms / config.tau_minus_ms)


def homeostatic_scale(
    weight: float,
    observed_rate_hz: float,
    config: PlasticGatewayConfig,
) -> float:
    """Return a bounded multiplicatively scaled candidate gateway weight."""

    safe_rate = max(observed_rate_hz, 1.0e-9)
    ratio = config.target_rate_hz / safe_rate
    factor = math.pow(ratio, config.homeostatic_alpha)
    scaled = weight * factor
    return float(min(config.weight_max, max(config.weight_min, scaled)))


def gate_signal(drive: float, threshold: float) -> float:
    """Return a numerically stable sigmoid gate value in ``[0, 1]``."""

    x = drive - threshold
    if x >= 0.0:
        inverse = math.exp(-x)
        return 1.0 / (1.0 + inverse)
    exponent = math.exp(x)
    return exponent / (1.0 + exponent)


def reward_modulated_delta(
    stdp_delta: float, reward: float, config: PlasticGatewayConfig
) -> float:
    """Return the candidate third-factor update for an efferent gate weight."""

    return config.gate_learning_eta * reward * stdp_delta


def formation_probability(
    pre_rate_hz: float,
    post_rate_hz: float,
    rho_max_hz: float,
    config: PlasticGatewayConfig,
) -> float:
    """Return a clipped structural-formation probability without RNG sampling."""

    if rho_max_hz <= 0.0:
        raise ValueError("rho_max_hz must be positive")
    coactivity = max(0.0, pre_rate_hz) * max(0.0, post_rate_hz)
    probability = config.structural_eta * coactivity / (rho_max_hz**2)
    return min(1.0, max(0.0, probability))


def pruning_probability(weight: float, config: PlasticGatewayConfig) -> float:
    """Return a clipped weak-weight pruning probability."""

    span = config.weight_max - config.weight_min
    if span <= 0.0:
        raise ValueError("weight range must be positive")
    normalized = (weight - config.weight_min) / span
    normalized = min(1.0, max(0.0, normalized))
    probability = config.pruning_eta * (1.0 - normalized)
    return min(1.0, max(0.0, probability))


__all__ = [
    "AreaDescriptor",
    "AreaKind",
    "NetworkAreaAdapter",
    "NeuralSymbiosisCatalog",
    "PipelineDirection",
    "PipelineTemplate",
    "PlasticGatewayConfig",
    "default_area_catalog",
    "default_pipeline_catalog",
    "formation_probability",
    "gate_signal",
    "homeostatic_scale",
    "pair_stdp_delta",
    "pruning_probability",
    "reward_modulated_delta",
]
