"""Embodiment interfaces for Brain-5D perception-action experiments."""

from .actuator import ActuatorAdapter
from .agent import EmbodimentAgent
from .connections import (
    ConnectionDescriptor,
    ConnectionKind,
    ConnectionManager,
    ConnectionStatus,
    RelationshipClass,
)
from .environment import EnvironmentAdapter
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
    "ConnectionDescriptor",
    "ConnectionKind",
    "ConnectionManager",
    "ConnectionStatus",
    "EmbodimentAgent",
    "EmbodimentMetrics",
    "EmbodimentRegistry",
    "EnvironmentAdapter",
    "EnvironmentKind",
    "EnvironmentObservation",
    "RelationshipClass",
    "SensorAdapter",
    "SensorFrame",
]
