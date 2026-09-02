"""Embodiment interfaces for Brain-5D perception-action experiments."""

from .actuator import ActuatorAdapter
from .agent import EmbodimentAgent
from .audit import ActionAuditRecord, ActionAuditTrail
from .controlled import ControlledEmbodimentAgent, ControlledSensorAdapter
from .connections import (
    ConnectionDescriptor,
    ConnectionKind,
    ConnectionManager,
    ConnectionStatus,
    RelationshipClass,
)
from .environment import EnvironmentAdapter
from .deterministic import DeterministicTargetEnvironment
from .models import (
    ActionCommand,
    ActuatorResult,
    EmbodimentMetrics,
    EnvironmentKind,
    EnvironmentObservation,
    SensorFrame,
)
from .registry import EmbodimentRegistry
from .sensor import SensorAdapter

__all__ = [
    "ActionCommand",
    "ActuatorAdapter",
    "ActuatorResult",
    "ActionAuditRecord",
    "ActionAuditTrail",
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
    "RelationshipClass",
    "SensorAdapter",
    "SensorFrame",
]
