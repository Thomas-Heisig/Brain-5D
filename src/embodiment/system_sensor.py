"""System-state sensor with an injectable provider for reproducible studies."""

from __future__ import annotations

import os
import platform
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


def _temperature_readings() -> tuple[float | None, dict[str, JSONValue]]:
    reader = getattr(psutil, "sensors_temperatures", None)
    raw = cast(dict[str, list[Any]], reader() if callable(reader) else {})
    groups: dict[str, JSONValue] = {}
    first: float | None = None
    for group, entries in raw.items():
        values: list[JSONValue] = []
        for entry in entries:
            current = getattr(entry, "current", None)
            if first is None and isinstance(current, (int, float)):
                first = float(current)
            values.append(
                {
                    "label": str(getattr(entry, "label", "") or ""),
                    "current_c": (
                        float(current) if isinstance(current, (int, float)) else None
                    ),
                    "high_c": (
                        float(getattr(entry, "high"))
                        if isinstance(getattr(entry, "high", None), (int, float))
                        else None
                    ),
                    "critical_c": (
                        float(getattr(entry, "critical"))
                        if isinstance(getattr(entry, "critical", None), (int, float))
                        else None
                    ),
                }
            )
        groups[str(group)] = values
    return first, groups


def _fan_readings() -> tuple[float | None, dict[str, JSONValue]]:
    reader = getattr(psutil, "sensors_fans", None)
    raw = cast(Mapping[str, list[Any]], reader() if callable(reader) else {})
    groups: dict[str, JSONValue] = {}
    first: float | None = None
    for group, entries in raw.items():
        values: list[JSONValue] = []
        for entry in entries:
            current = getattr(entry, "current", None)
            if first is None and isinstance(current, (int, float)):
                first = float(current)
            values.append(
                {
                    "label": str(getattr(entry, "label", "") or ""),
                    "rpm": (
                        float(current) if isinstance(current, (int, float)) else None
                    ),
                }
            )
        groups[str(group)] = values
    return first, groups


def _network_interfaces() -> dict[str, JSONValue]:
    stats = psutil.net_if_stats()
    addresses = psutil.net_if_addrs()
    result: dict[str, JSONValue] = {}
    for name in sorted(set(stats) | set(addresses)):
        status = stats.get(name)
        result[name] = {
            "is_up": bool(status.isup) if status is not None else None,
            "speed_mbps": int(status.speed) if status is not None else None,
            "mtu": int(status.mtu) if status is not None else None,
            "addresses": [
                {
                    "family": str(address.family),
                    "address": str(address.address),
                    "netmask": str(address.netmask) if address.netmask else None,
                }
                for address in addresses.get(name, [])
            ],
        }
    return result


def host_system_readings(tick: int) -> Mapping[str, JSONValue]:
    """Read real host state without contacting external services.

    Unsupported operating-system sensors remain ``None`` or empty mappings;
    this function never manufactures substitute values for missing hardware.
    """

    temperature, temperatures = _temperature_readings()
    fan_rpm, fans = _fan_readings()
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disk = psutil.disk_usage(os.path.abspath(os.sep))
    disk_io = psutil.disk_io_counters()
    network_io = psutil.net_io_counters()
    interfaces = _network_interfaces()
    network_up = any(
        bool(value.get("is_up"))
        for value in interfaces.values()
        if isinstance(value, dict)
    )
    battery_reader = getattr(psutil, "sensors_battery", None)
    battery = cast(Any, battery_reader() if callable(battery_reader) else None)
    frequency = cast(Any, psutil.cpu_freq())
    per_cpu = psutil.cpu_percent(interval=None, percpu=True)

    load_average_reader = cast(
        Callable[[], tuple[float, float, float]] | None,
        getattr(os, "getloadavg", None),
    )
    try:
        load_average: JSONValue = (
            [float(value) for value in load_average_reader()]
            if callable(load_average_reader)
            else None
        )
    except OSError:
        load_average = None

    return {
        "tick": tick,
        "unix_time": time(),
        "platform": platform.system(),
        "platform_release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor() or None,
        "hostname": platform.node() or None,
        "boot_time": psutil.boot_time(),
        "cpu_percent": psutil.cpu_percent(interval=None),
        "cpu_percent_per_core": [float(value) for value in per_cpu],
        "cpu_logical_count": psutil.cpu_count(logical=True),
        "cpu_physical_count": psutil.cpu_count(logical=False),
        "cpu_frequency_mhz": (
            float(frequency.current) if frequency is not None else None
        ),
        "cpu_frequency_min_mhz": (
            float(frequency.min) if frequency is not None else None
        ),
        "cpu_frequency_max_mhz": (
            float(frequency.max) if frequency is not None else None
        ),
        "load_average": load_average,
        "memory_percent": memory.percent,
        "memory_total_bytes": memory.total,
        "memory_available_bytes": memory.available,
        "memory_used_bytes": memory.used,
        "swap_percent": swap.percent,
        "swap_total_bytes": swap.total,
        "swap_used_bytes": swap.used,
        "temperature_c": temperature,
        "temperatures": temperatures,
        "disk_total_bytes": disk.total,
        "disk_used_bytes": disk.used,
        "disk_free_bytes": disk.free,
        "disk_percent": disk.percent,
        "disk_read_bytes": disk_io.read_bytes if disk_io is not None else None,
        "disk_write_bytes": disk_io.write_bytes if disk_io is not None else None,
        "disk_read_count": disk_io.read_count if disk_io is not None else None,
        "disk_write_count": disk_io.write_count if disk_io is not None else None,
        "network_up": network_up,
        "network_interfaces": interfaces,
        "network_bytes_sent": network_io.bytes_sent,
        "network_bytes_received": network_io.bytes_recv,
        "network_packets_sent": network_io.packets_sent,
        "network_packets_received": network_io.packets_recv,
        "network_errors_in": network_io.errin,
        "network_errors_out": network_io.errout,
        "battery_percent": battery.percent if battery is not None else None,
        "battery_plugged": battery.power_plugged if battery is not None else None,
        "battery_seconds_left": battery.secsleft if battery is not None else None,
        "fan_rpm": fan_rpm,
        "fans": fans,
        "process_count": len(psutil.pids()),
    }


__all__ = [
    "InteroceptionFrame",
    "SystemReadings",
    "SystemSensorAdapter",
    "host_system_readings",
    "wall_clock_readings",
]
