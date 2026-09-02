"""System-state sensor with an injectable provider for reproducible studies."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from time import time
from typing import Any, cast

import psutil

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


def host_system_readings(tick: int) -> Mapping[str, JSONValue]:
    """Read opt-in host state without contacting external services."""

    temperature_reader = getattr(psutil, "sensors_temperatures", None)
    temperatures = cast(
        dict[str, list[Any]],
        temperature_reader() if callable(temperature_reader) else {},
    )
    temperature: float | None = None
    for entries in temperatures.values():
        if entries:
            temperature = entries[0].current
            break

    network_up = any(bool(status.isup) for status in psutil.net_if_stats().values())
    return {
        "tick": tick,
        "cpu_percent": psutil.cpu_percent(interval=None),
        "memory_percent": psutil.virtual_memory().percent,
        "temperature_c": temperature,
        "network_up": network_up,
        "process_count": len(psutil.pids()),
        "unix_time": time(),
    }


__all__ = [
    "SystemReadings",
    "SystemSensorAdapter",
    "host_system_readings",
    "wall_clock_readings",
]
