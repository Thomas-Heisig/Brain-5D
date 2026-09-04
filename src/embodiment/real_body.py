"""Real-host body inventory for the Brain-5D embodiment dashboard.

This module deliberately extends connection discovery without changing its
fail-closed authorization semantics. Availability is observation; it is not
permission to capture, transmit, print, play audio, or move hardware.
"""

from __future__ import annotations

import glob
import hashlib
import json
import os
import subprocess
import time
from dataclasses import replace
from pathlib import Path
from typing import cast

from .connections import (
    ConnectionDescriptor,
    ConnectionKind,
    ConnectionManager as BaseConnectionManager,
    ConnectionStatus,
    RelationshipClass,
)
from .models import JSONValue
from .system_sensor import host_system_readings

_GENERIC_DEVICE_FAMILIES = (
    "sensor.camera",
    "sensor.microphone",
    "actuator.display",
    "actuator.audio",
    "actuator.printer",
)


class ConnectionManager(BaseConnectionManager):
    """Connection manager with real host telemetry and per-device endpoints."""

    def __init__(self, *, cache_seconds: float = 15.0) -> None:
        super().__init__(cache_seconds=cache_seconds)
        self._dynamic_device_ids: set[str] = set()

    def _discover_local_resources(self) -> None:
        """Run the base discovery and then enumerate individual real devices."""
        super()._discover_local_resources()
        self._refresh_dynamic_devices()

    def _refresh_dynamic_devices(self) -> None:
        for connection_id in self._dynamic_device_ids:
            self._connections.pop(connection_id, None)
        self._dynamic_device_ids.clear()

        if os.name == "nt":
            devices = self._windows_devices()
        else:
            devices = self._posix_devices()

        for descriptor in devices:
            self._connections[descriptor.connection_id] = descriptor
            self._dynamic_device_ids.add(descriptor.connection_id)

    def _device_descriptor(
        self,
        family: str,
        name: str,
        kind: ConnectionKind,
        capabilities: tuple[str, ...],
        *,
        modalities: tuple[str, ...] = (),
        hazard_level: str = "none",
        source_detail: str = "",
        index: int = 0,
    ) -> ConnectionDescriptor:
        stable = hashlib.sha1(
            f"{family}|{name}|{source_detail}|{index}".encode("utf-8"),
            usedforsecurity=False,
        ).hexdigest()[:12]
        return ConnectionDescriptor(
            connection_id=f"{family}.{stable}",
            name=name,
            kind=kind,
            relationship=RelationshipClass.REACHABLE,
            status=ConnectionStatus.AVAILABLE,
            capabilities=capabilities,
            modalities=modalities,
            available=True,
            authorized=False,
            active=False,
            hazard_level=hazard_level,
            source="system_device_inventory",
            message=(
                f"Real device endpoint detected: {source_detail}"
                if source_detail
                else "Real device endpoint detected."
            ),
        )

    def _windows_devices(self) -> tuple[ConnectionDescriptor, ...]:
        script = (
            "$ErrorActionPreference='SilentlyContinue';"
            "$d=Get-PnpDevice -PresentOnly | Select-Object Class,FriendlyName,InstanceId,Status;"
            "$p=Get-CimInstance Win32_Printer | Select-Object Name,DeviceID,PrinterStatus;"
            "@{devices=$d;printers=$p}|ConvertTo-Json -Compress -Depth 4"
        )
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
                capture_output=True,
                timeout=8,
                check=False,
            )
            if result.returncode != 0:
                return ()
            payload = cast(
                dict[str, object], json.loads(result.stdout.decode(errors="replace"))
            )
        except (OSError, subprocess.SubprocessError, json.JSONDecodeError, TypeError):
            return ()

        descriptors: list[ConnectionDescriptor] = []
        devices = self._object_list(payload.get("devices"))
        for index, item in enumerate(devices):
            if str(item.get("Status", "")).upper() != "OK":
                continue
            device_class = str(item.get("Class", "") or "")
            name = str(item.get("FriendlyName", "") or device_class or "Device")
            instance = str(item.get("InstanceId", "") or "")
            searchable = f"{device_class} {name}".lower()

            if "camera" in searchable or "image" in searchable:
                descriptors.append(
                    self._device_descriptor(
                        "sensor.camera",
                        name,
                        ConnectionKind.SENSOR,
                        ("frames", "video"),
                        modalities=("vision",),
                        hazard_level="medium",
                        source_detail=instance,
                        index=index,
                    )
                )
            if "microphone" in searchable or "mikrofon" in searchable:
                descriptors.append(
                    self._device_descriptor(
                        "sensor.microphone",
                        name,
                        ConnectionKind.SENSOR,
                        ("samples", "audio_stream"),
                        modalities=("audio",),
                        hazard_level="medium",
                        source_detail=instance,
                        index=index,
                    )
                )
            if "monitor" in searchable or "display" in searchable:
                descriptors.append(
                    self._device_descriptor(
                        "actuator.display",
                        name,
                        ConnectionKind.ACTUATOR,
                        ("visual_output",),
                        modalities=("visual",),
                        hazard_level="low",
                        source_detail=instance,
                        index=index,
                    )
                )
            if (
                "audioendpoint" in searchable
                and "microphone" not in searchable
                and "mikrofon" not in searchable
            ):
                descriptors.append(
                    self._device_descriptor(
                        "actuator.audio",
                        name,
                        ConnectionKind.ACTUATOR,
                        ("play_audio", "speech"),
                        modalities=("audio",),
                        hazard_level="low",
                        source_detail=instance,
                        index=index,
                    )
                )

        for index, item in enumerate(self._object_list(payload.get("printers"))):
            name = str(item.get("Name", "") or "Printer")
            device_id = str(item.get("DeviceID", "") or name)
            descriptors.append(
                self._device_descriptor(
                    "actuator.printer",
                    name,
                    ConnectionKind.ACTUATOR,
                    ("print_document",),
                    hazard_level="medium",
                    source_detail=device_id,
                    index=index,
                )
            )
        return tuple(descriptors)

    def _posix_devices(self) -> tuple[ConnectionDescriptor, ...]:
        descriptors: list[ConnectionDescriptor] = []

        for index, path in enumerate(sorted(glob.glob("/dev/video*"))):
            descriptors.append(
                self._device_descriptor(
                    "sensor.camera",
                    Path(path).name,
                    ConnectionKind.SENSOR,
                    ("frames", "video"),
                    modalities=("vision",),
                    hazard_level="medium",
                    source_detail=path,
                    index=index,
                )
            )

        for index, connector in enumerate(sorted(glob.glob("/sys/class/drm/*/status"))):
            if self._read_text(connector).strip().lower() != "connected":
                continue
            connector_name = Path(connector).parent.name
            descriptors.append(
                self._device_descriptor(
                    "actuator.display",
                    connector_name,
                    ConnectionKind.ACTUATOR,
                    ("visual_output",),
                    modalities=("visual",),
                    hazard_level="low",
                    source_detail=connector,
                    index=index,
                )
            )

        descriptors.extend(self._pulse_audio_devices("sources", sensor=True))
        descriptors.extend(self._pulse_audio_devices("sinks", sensor=False))

        for index, printer in enumerate(self._command_lines(["lpstat", "-p"])):
            name = printer.split()[1] if printer.startswith("printer ") else printer
            descriptors.append(
                self._device_descriptor(
                    "actuator.printer",
                    name,
                    ConnectionKind.ACTUATOR,
                    ("print_document",),
                    hazard_level="medium",
                    source_detail=printer,
                    index=index,
                )
            )
        return tuple(descriptors)

    def _pulse_audio_devices(
        self, category: str, *, sensor: bool
    ) -> tuple[ConnectionDescriptor, ...]:
        lines = self._command_lines(["pactl", "list", "short", category])
        descriptors: list[ConnectionDescriptor] = []
        for index, line in enumerate(lines):
            columns = line.split("\t")
            endpoint_name = columns[1] if len(columns) > 1 else line
            if sensor:
                descriptors.append(
                    self._device_descriptor(
                        "sensor.microphone",
                        endpoint_name,
                        ConnectionKind.SENSOR,
                        ("samples", "audio_stream"),
                        modalities=("audio",),
                        hazard_level="medium",
                        source_detail=line,
                        index=index,
                    )
                )
            else:
                descriptors.append(
                    self._device_descriptor(
                        "actuator.audio",
                        endpoint_name,
                        ConnectionKind.ACTUATOR,
                        ("play_audio", "speech"),
                        modalities=("audio",),
                        hazard_level="low",
                        source_detail=line,
                        index=index,
                    )
                )
        return tuple(descriptors)

    @staticmethod
    def _command_lines(command: list[str]) -> tuple[str, ...]:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                timeout=4,
                check=False,
                text=True,
            )
        except (OSError, subprocess.SubprocessError):
            return ()
        if result.returncode != 0:
            return ()
        return tuple(line.strip() for line in result.stdout.splitlines() if line.strip())

    def to_json(self, *, refresh: bool = False) -> dict[str, JSONValue]:
        connections = self.snapshot(refresh=refresh)
        dynamic_families = {
            family
            for family in _GENERIC_DEVICE_FAMILIES
            if any(item.connection_id.startswith(f"{family}.") for item in connections)
        }
        visible = tuple(
            item
            for item in connections
            if not (item.connection_id in dynamic_families and item.connection_id in _GENERIC_DEVICE_FAMILIES)
        )
        sample_tick = int(time.monotonic() * 1000)
        return {
            "count": len(visible),
            "available": sum(item.available for item in visible),
            "authorized": sum(item.authorized for item in visible),
            "active": sum(item.active for item in visible),
            "connections": [item.to_json() for item in visible],
            "host": cast(dict[str, JSONValue], dict(host_system_readings(sample_tick))),
            "body_contract": {
                "observed_only": True,
                "missing_values_are_unknown": True,
                "availability_is_not_authorization": True,
                "per_device_identity": True,
                "sample_clock": "host_monotonic_ms",
            },
        }


__all__ = ["ConnectionManager"]
