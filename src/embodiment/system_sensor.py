"""System-state sensor with an injectable provider for reproducible studies."""

from __future__ import annotations

import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from time import time
from typing import Any, cast

import psutil

from .interoception import InteroceptionFrame, normalize_vital_signals
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

    def sample_interoception(self, tick: int) -> InteroceptionFrame:
        """Return typed body-relevant signals for the same deterministic sample."""
        frame = self.sample(tick)
        if not isinstance(frame.payload, dict):
            raise TypeError("system sensor provider must return a mapping")
        return InteroceptionFrame(
            tick=tick, signals=normalize_vital_signals(frame.payload)
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
            temperature = float(entries[0].current)
            break

    network_up = any(bool(status.isup) for status in psutil.net_if_stats().values())
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage(os.path.abspath(os.sep))
    disk_io = psutil.disk_io_counters()
    network_io = psutil.net_io_counters()
    battery_reader = getattr(psutil, "sensors_battery", None)
    battery = cast(Any, battery_reader() if callable(battery_reader) else None)
    fan_reader = getattr(psutil, "sensors_fans", None)
    fans = cast(
        Mapping[str, list[Any]],
        fan_reader() if callable(fan_reader) else {},
    )
    fan_rpm: float | None = None
    for entries in fans.values():
        if entries:
            fan_rpm = float(entries[0].current)
            break
    return {
        "tick": tick,
        "cpu_percent": psutil.cpu_percent(interval=None),
        "memory_percent": memory.percent,
        "memory_available_bytes": memory.available,
        "temperature_c": temperature,
        "disk_free_bytes": disk.free,
        "disk_read_bytes": disk_io.read_bytes if disk_io is not None else None,
        "disk_write_bytes": disk_io.write_bytes if disk_io is not None else None,
        "network_up": network_up,
        "network_bytes_sent": network_io.bytes_sent,
        "network_bytes_received": network_io.bytes_recv,
        "battery_percent": battery.percent if battery is not None else None,
        "battery_plugged": battery.power_plugged if battery is not None else None,
        "fan_rpm": fan_rpm,
        "process_count": len(psutil.pids()),
        "unix_time": time(),
    }


__all__ = [
    "InteroceptionFrame",
    "SystemReadings",
    "SystemSensorAdapter",
    "host_system_readings",
    "wall_clock_readings",
]
