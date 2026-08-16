"""Embodiment interfaces for Brain-5D perception-action experiments."""

from .actuator import ActuatorAdapter
from .agent import EmbodimentAgent
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
    "EmbodimentAgent",
    "EmbodimentMetrics",
    "EmbodimentRegistry",
    "EnvironmentAdapter",
    "EnvironmentKind",
    "EnvironmentObservation",
    "SensorAdapter",
    "SensorFrame",
]
