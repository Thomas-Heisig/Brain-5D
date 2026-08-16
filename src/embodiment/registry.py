"""Typed adapter registry for the Brain-5D embodiment layer."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from .actuator import ActuatorAdapter
from .environment import EnvironmentAdapter
from .sensor import SensorAdapter

SensorFactory = Callable[[], SensorAdapter]
ActuatorFactory = Callable[[], ActuatorAdapter]
EnvironmentFactory = Callable[[], EnvironmentAdapter]
T = TypeVar("T")


class EmbodimentRegistry:
    """Register adapter factories without coupling them to the neural core."""

    def __init__(self) -> None:
        self._sensors: dict[str, SensorFactory] = {}
        self._actuators: dict[str, ActuatorFactory] = {}
        self._environments: dict[str, EnvironmentFactory] = {}

    def register_sensor(self, name: str, factory: SensorFactory) -> None:
        """Register one sensor factory."""
        self._register_unique(self._sensors, name, factory)

    def register_actuator(self, name: str, factory: ActuatorFactory) -> None:
        """Register one actuator factory."""
        self._register_unique(self._actuators, name, factory)

    def register_environment(self, name: str, factory: EnvironmentFactory) -> None:
        """Register one environment factory."""
        self._register_unique(self._environments, name, factory)

    def create_sensor(self, name: str) -> SensorAdapter:
        """Create a registered sensor."""
        return self._sensors[name]()

    def create_actuator(self, name: str) -> ActuatorAdapter:
        """Create a registered actuator."""
        return self._actuators[name]()

    def create_environment(self, name: str) -> EnvironmentAdapter:
        """Create a registered environment."""
        return self._environments[name]()

    def names(self) -> dict[str, tuple[str, ...]]:
        """Return registered adapter names by category."""
        return {
            "sensors": tuple(sorted(self._sensors)),
            "actuators": tuple(sorted(self._actuators)),
            "environments": tuple(sorted(self._environments)),
        }

    @staticmethod
    def _register_unique(
        registry: dict[str, Callable[[], T]],
        name: str,
        factory: Callable[[], T],
    ) -> None:
        key = name.strip()
        if not key:
            raise ValueError("adapter name must not be empty")
        if key in registry:
            raise ValueError(f"adapter already registered: {key}")
        registry[key] = factory
