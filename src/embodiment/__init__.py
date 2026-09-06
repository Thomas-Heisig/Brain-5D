"""Embodiment interfaces for Brain-5D perception-action experiments."""

from .actuator import ActuatorAdapter
from .actuator_hub import ActionRouter, ActuatorHub
from .agent import EmbodimentAgent
from .audit import ActionAuditRecord, ActionAuditTrail
from .connections import (
    ConnectionDescriptor,
    ConnectionKind,
    ConnectionStatus,
    RelationshipClass,
)
from .controlled import ControlledEmbodimentAgent, ControlledSensorAdapter
from .deterministic import DeterministicTargetEnvironment
from .environment import EnvironmentAdapter
from .interoception import (
    DriveState,
    FunctionalState,
    InteroceptionFrame,
    RegulatoryState,
    VitalSignal,
    derive_drives,
    derive_functional_state,
    derive_regulatory_state,
    normalize_vital_signals,
)
from .models import (
    ActionCommand,
    ActionReceipt,
    ActuatorResult,
    EmbodimentMetrics,
    EnvironmentKind,
    EnvironmentObservation,
    SensorFrame,
)
from .neural_symbiosis import (
    AreaDescriptor,
    AreaKind,
    NetworkAreaAdapter,
    NeuralSymbiosisCatalog,
    PipelineDirection,
    PipelineTemplate,
    PlasticGatewayConfig,
    formation_probability,
    gate_signal,
    homeostatic_scale,
    pair_stdp_delta,
    pruning_probability,
    reward_modulated_delta,
)
from .pipeline import EmbodimentPipeline
from .real_body import ConnectionManager
from .registry import EmbodimentRegistry
from .sensor import SensorAdapter
from .system_sensor import (
    SystemSensorAdapter,
    host_system_readings,
    wall_clock_readings,
)
from .task_outcome import TaskOutcome, TaskOutcomeVerifier

__all__ = [
    "ActionCommand",
    "ActionReceipt",
    "ActuatorAdapter",
    "ActuatorHub",
    "ActionRouter",
    "ActuatorResult",
    "ActionAuditRecord",
    "ActionAuditTrail",
    "AreaDescriptor",
    "AreaKind",
    "ConnectionDescriptor",
    "ConnectionKind",
    "ConnectionManager",
    "ConnectionStatus",
    "EmbodimentAgent",
    "ControlledEmbodimentAgent",
    "ControlledSensorAdapter",
    "DeterministicTargetEnvironment",
    "EmbodimentMetrics",
    "EmbodimentRegistry",
    "EnvironmentAdapter",
    "EnvironmentKind",
    "EnvironmentObservation",
    "DriveState",
    "FunctionalState",
    "InteroceptionFrame",
    "NetworkAreaAdapter",
    "NeuralSymbiosisCatalog",
    "PipelineDirection",
    "PipelineTemplate",
    "PlasticGatewayConfig",
    "RegulatoryState",
    "EmbodimentPipeline",
    "RelationshipClass",
    "SensorAdapter",
    "SensorFrame",
    "TaskOutcome",
    "TaskOutcomeVerifier",
    "SystemSensorAdapter",
    "VitalSignal",
    "derive_drives",
    "derive_functional_state",
    "derive_regulatory_state",
    "formation_probability",
    "gate_signal",
    "homeostatic_scale",
    "host_system_readings",
    "normalize_vital_signals",
    "pair_stdp_delta",
    "pruning_probability",
    "reward_modulated_delta",
    "wall_clock_readings",
]
