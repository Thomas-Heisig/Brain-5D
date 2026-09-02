"""Embodiment interfaces for Brain-5D perception-action experiments."""

from .actuator import ActuatorAdapter
from .agent import EmbodimentAgent
from .audit import ActionAuditRecord, ActionAuditTrail
from .connections import (
    ConnectionDescriptor,
    ConnectionKind,
    ConnectionManager,
    ConnectionStatus,
    RelationshipClass,
)
from .controlled import ControlledEmbodimentAgent, ControlledSensorAdapter
from .deterministic import DeterministicTargetEnvironment
from .environment import EnvironmentAdapter
from .models import (
    ActionCommand,
    ActuatorResult,
    EmbodimentMetrics,
    EnvironmentKind,
    EnvironmentObservation,
    SensorFrame,
)
from .pipeline import EmbodimentPipeline
from .registry import EmbodimentRegistry
from .sensor import SensorAdapter
from .system_sensor import (
    SystemSensorAdapter,
    host_system_readings,
    wall_clock_readings,
)

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
    "EmbodimentPipeline",
    "RelationshipClass",
    "SensorAdapter",
    "SensorFrame",
    "SystemSensorAdapter",
    "host_system_readings",
    "wall_clock_readings",
]
