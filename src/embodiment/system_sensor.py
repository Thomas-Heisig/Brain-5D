"""System-state sensor with an injectable provider for reproducible studies."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from time import time

from .models import JSONValue, SensorFrame

SystemReadings = Callable[[int], Mapping[str, JSONValue]]


@dataclass(slots=True)
class SystemSensorAdapter:
    """Publish host measurements as a typed sensor frame.

    The provider is deliberately injected: production may read host metrics,
    while experiments can supply a deterministic trace without hidden inputs.
    """

    provider: SystemReadings
    _active: bool = True
    sensor_id: str = "system-state-v1"
    modality: str = "system"

    @property
    def active(self) -> bool:
        return self._active

    def sample(self, tick: int) -> SensorFrame:
        if tick < 0:
            raise ValueError("tick must be >= 0")
        payload = dict(self.provider(tick))
        return SensorFrame(
            sensor_id=self.sensor_id,
            tick=tick,
            modality=self.modality,
            payload=payload,
        )


def wall_clock_readings(tick: int) -> Mapping[str, JSONValue]:
    """Return the minimal live provider; richer metrics remain opt-in."""

    return {"tick": tick, "unix_time": time()}


__all__ = ["SystemReadings", "SystemSensorAdapter", "wall_clock_readings"]
