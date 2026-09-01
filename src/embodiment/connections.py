"""Connection metadata and read-only discovery for an extensible embodiment."""

from __future__ import annotations

import glob
import json
import os
import socket
import subprocess
import threading
import time
from dataclasses import dataclass, replace
from enum import StrEnum
from typing import cast

from .models import JSONValue


class ConnectionKind(StrEnum):
    """Functional role of an external or internal connection."""

    RESOURCE = "resource"
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    DATA = "data"
    SERVICE = "service"


class RelationshipClass(StrEnum):
    """How strongly a connection participates in the current body model."""

    PERCEIVABLE = "perceivable"
    REACHABLE = "reachable"
    USABLE = "usable"
    CONTROLLABLE = "controllable"
    INTEGRATED = "integrated"
    EMBODIED = "embodied"


class ConnectionStatus(StrEnum):
    """Observed connection health without implying authorization."""

    UNAVAILABLE = "unavailable"
    AVAILABLE = "available"
    CONNECTED = "connected"
    DEGRADED = "degraded"
    DENIED = "denied"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class ConnectionDescriptor:
    """One sensor, actuator, service, data source, or vital resource."""

    connection_id: str
    name: str
    kind: ConnectionKind
    relationship: RelationshipClass
    status: ConnectionStatus
    capabilities: tuple[str, ...] = ()
    permissions: tuple[str, ...] = ()
    modalities: tuple[str, ...] = ()
    available: bool = False
    authorized: bool = False
    active: bool = False
    latency_ms: float | None = None
    energy_demand: str = "unknown"
    hazard_level: str = "none"
    source: str = "catalog"
    message: str = ""

    def to_json(self) -> dict[str, JSONValue]:
        """Return the public read-only connection representation."""
        return {
            "connection_id": self.connection_id,
            "name": self.name,
            "kind": self.kind.value,
            "relationship": self.relationship.value,
            "status": self.status.value,
            "capabilities": list(self.capabilities),
            "permissions": list(self.permissions),
            "modalities": list(self.modalities),
            "available": self.available,
            "authorized": self.authorized,
            "active": self.active,
            "latency_ms": self.latency_ms,
            "energy_demand": self.energy_demand,
            "hazard_level": self.hazard_level,
            "source": self.source,
            "message": self.message,
        }


def _descriptor(
    connection_id: str,
    name: str,
    kind: ConnectionKind,
    capabilities: tuple[str, ...],
    *,
    modalities: tuple[str, ...] = (),
    hazard_level: str = "none",
) -> ConnectionDescriptor:
    return ConnectionDescriptor(
        connection_id=connection_id,
        name=name,
        kind=kind,
        relationship=RelationshipClass.PERCEIVABLE,
        status=ConnectionStatus.UNAVAILABLE,
        capabilities=capabilities,
        modalities=modalities,
        hazard_level=hazard_level,
        message="No configured adapter or detected device.",
    )


def default_connection_catalog() -> tuple[ConnectionDescriptor, ...]:
    """Return the stable open-ended catalog; entries are inactive by default."""
    return (
        _descriptor(
            "resource.compute",
            "Compute",
            ConnectionKind.RESOURCE,
            ("cpu", "memory", "runtime"),
        ),
        _descriptor(
            "resource.storage",
            "Storage",
            ConnectionKind.RESOURCE,
            ("files", "snapshots", "journals"),
        ),
        _descriptor(
            "network.local",
            "Local network",
            ConnectionKind.DATA,
            ("tcp", "local_services"),
            modalities=("network",),
        ),
        _descriptor(
            "network.internet",
            "Internet",
            ConnectionKind.DATA,
            ("web", "api", "feeds"),
            modalities=("network",),
            hazard_level="medium",
        ),
        _descriptor(
            "sensor.camera",
            "Camera",
            ConnectionKind.SENSOR,
            ("frames", "video"),
            modalities=("vision",),
            hazard_level="medium",
        ),
        _descriptor(
            "sensor.microphone",
            "Microphone",
            ConnectionKind.SENSOR,
            ("samples", "audio_stream"),
            modalities=("audio",),
            hazard_level="medium",
        ),
        _descriptor(
            "sensor.location",
            "Location",
            ConnectionKind.SENSOR,
            ("position", "time"),
            modalities=("location",),
        ),
        _descriptor(
            "sensor.environment",
            "Environment sensors",
            ConnectionKind.SENSOR,
            ("temperature", "humidity", "motion", "force"),
            modalities=("environment",),
        ),
        _descriptor(
            "data.web_api",
            "Web and APIs",
            ConnectionKind.DATA,
            ("http_read", "structured_data"),
            modalities=("text", "data"),
            hazard_level="medium",
        ),
        _descriptor(
            "data.database",
            "Databases",
            ConnectionKind.DATA,
            ("query", "records"),
            modalities=("data",),
            hazard_level="medium",
        ),
        _descriptor(
            "service.messaging",
            "Communication services",
            ConnectionKind.SERVICE,
            ("receive", "send"),
            modalities=("text", "audio"),
            hazard_level="high",
        ),
        _descriptor(
            "actuator.display",
            "Display",
            ConnectionKind.ACTUATOR,
            ("visual_output",),
            hazard_level="low",
        ),
        _descriptor(
            "actuator.audio",
            "Audio output",
            ConnectionKind.ACTUATOR,
            ("play_audio", "speech"),
            hazard_level="low",
        ),
        _descriptor(
            "actuator.printer",
            "Printer",
            ConnectionKind.ACTUATOR,
            ("print_document", "fabricate"),
            hazard_level="medium",
        ),
        _descriptor(
            "actuator.robotics",
            "Robotics",
            ConnectionKind.ACTUATOR,
            ("move", "grip", "stop"),
            modalities=("proprioception",),
            hazard_level="critical",
        ),
    )


class ConnectionManager:
    """Own connection identity and health without opening sensors or actuators."""

    def __init__(self, *, cache_seconds: float = 15.0) -> None:
        self._lock = threading.RLock()
        self._connections = {
            item.connection_id: item for item in default_connection_catalog()
        }
        self._cache_seconds = cache_seconds
        self._last_discovery = 0.0

    def register(self, descriptor: ConnectionDescriptor) -> None:
        """Register or replace an explicitly configured adapter descriptor."""
        if not descriptor.connection_id.strip():
            raise ValueError("connection_id must not be empty")
        with self._lock:
            self._connections[descriptor.connection_id] = descriptor

    def snapshot(self, *, refresh: bool = False) -> tuple[ConnectionDescriptor, ...]:
        """Return a stable snapshot after optional cached read-only discovery."""
        now = time.monotonic()
        with self._lock:
            if refresh or now - self._last_discovery >= self._cache_seconds:
                self._discover_local_resources()
                self._last_discovery = now
            return tuple(self._connections[key] for key in sorted(self._connections))

    def to_json(self, *, refresh: bool = False) -> dict[str, JSONValue]:
        """Return catalog entries and summary counts for the dashboard."""
        connections = self.snapshot(refresh=refresh)
        return {
            "count": len(connections),
            "available": sum(item.available for item in connections),
            "authorized": sum(item.authorized for item in connections),
            "active": sum(item.active for item in connections),
            "connections": [item.to_json() for item in connections],
        }

    def _update_detected(
        self, connection_id: str, detected: bool, message: str
    ) -> None:
        current = self._connections[connection_id]
        self._connections[connection_id] = replace(
            current,
            relationship=(
                RelationshipClass.REACHABLE
                if detected
                else RelationshipClass.PERCEIVABLE
            ),
            status=(
                ConnectionStatus.AVAILABLE if detected else ConnectionStatus.UNAVAILABLE
            ),
            available=detected,
            authorized=False,
            active=False,
            source="system_discovery",
            message=message,
        )

    def _discover_local_resources(self) -> None:
        self._update_detected(
            "resource.compute", True, "Runtime compute resource detected."
        )
        self._update_detected("resource.storage", True, "Local filesystem detected.")

        addresses = self._local_addresses()
        local_network = bool(addresses)
        self._update_detected(
            "network.local",
            local_network,
            (
                f"Local addresses: {', '.join(addresses)}"
                if addresses
                else "No non-loopback address detected."
            ),
        )
        internet_route = self._has_internet_route()
        self._update_detected(
            "network.internet",
            internet_route,
            (
                "Outbound IP route detected; external reachability is not asserted."
                if internet_route
                else "No outbound IP route detected."
            ),
        )

        camera, microphone, audio_output, printer, display = self._discover_devices()
        self._update_detected(
            "sensor.camera",
            camera,
            "Camera device detected." if camera else "No camera device detected.",
        )
        self._update_detected(
            "sensor.microphone",
            microphone,
            (
                "Microphone endpoint detected."
                if microphone
                else "No microphone endpoint detected."
            ),
        )
        self._update_detected(
            "actuator.audio",
            audio_output,
            (
                "Audio output endpoint detected."
                if audio_output
                else "No audio output endpoint detected."
            ),
        )
        self._update_detected(
            "actuator.printer",
            printer,
            (
                "Print queue detected; it may represent a physical or virtual printer."
                if printer
                else "No print queue detected."
            ),
        )
        self._update_detected(
            "actuator.display",
            display,
            (
                "Display endpoint detected."
                if display
                else "No display endpoint detected."
            ),
        )

    @staticmethod
    def _local_addresses() -> tuple[str, ...]:
        try:
            addresses = {
                str(address[4][0])
                for address in socket.getaddrinfo(socket.gethostname(), None)
                if address[0] in {socket.AF_INET, socket.AF_INET6}
                and not str(address[4][0]).startswith(("127.", "169.254.", "::1"))
            }
        except OSError:
            return ()
        return tuple(sorted(addresses))

    @staticmethod
    def _has_internet_route() -> bool:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
                probe.connect(("1.1.1.1", 53))
                return not probe.getsockname()[0].startswith("127.")
        except OSError:
            return False

    @staticmethod
    def _discover_devices() -> tuple[bool, bool, bool, bool, bool]:
        if os.name == "nt":
            return ConnectionManager._discover_windows_devices()
        camera = bool(glob.glob("/dev/video*"))
        audio = bool(glob.glob("/dev/snd/*"))
        printer = bool(glob.glob("/dev/usb/lp*"))
        display = any(
            path.endswith("/status")
            and ConnectionManager._read_text(path).strip().lower() == "connected"
            for path in glob.glob("/sys/class/drm/*/status")
        )
        return camera, audio, audio, printer, display

    @staticmethod
    def _read_text(path: str) -> str:
        try:
            with open(path, encoding="utf-8") as stream:
                return stream.read()
        except OSError:
            return ""

    @staticmethod
    def _discover_windows_devices() -> tuple[bool, bool, bool, bool, bool]:
        script = (
            "$ErrorActionPreference='SilentlyContinue';"
            "$d=Get-PnpDevice -PresentOnly | Select-Object Class,FriendlyName,Status;"
            "$p=Get-CimInstance Win32_Printer | Select-Object Name,PrinterStatus;"
            "@{devices=$d;printers=$p}|ConvertTo-Json -Compress -Depth 3"
        )
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
                capture_output=True,
                timeout=8,
                check=False,
            )
            if result.returncode != 0:
                return False, False, False, False, False
            payload = cast(
                dict[str, object],
                json.loads(result.stdout.decode(errors="replace")),
            )
            devices = ConnectionManager._object_list(payload.get("devices"))
            printers = ConnectionManager._object_list(payload.get("printers"))
            names = [
                f"{item.get('Class', '')} {item.get('FriendlyName', '')}".lower()
                for item in devices
                if item.get("Status") == "OK"
            ]
            camera = any("camera" in name or "image" in name for name in names)
            microphone = any(
                "microphone" in name or "mikrofon" in name for name in names
            )
            audio_output = any(
                "audioendpoint" in name
                and "microphone" not in name
                and "mikrofon" not in name
                for name in names
            )
            display = any("monitor" in name or "display" in name for name in names)
            return camera, microphone, audio_output, bool(printers), display
        except (OSError, subprocess.SubprocessError, json.JSONDecodeError, TypeError):
            return False, False, False, False, False

    @staticmethod
    def _object_list(value: object) -> list[dict[str, object]]:
        if isinstance(value, dict):
            return [cast(dict[str, object], value)]
        if isinstance(value, list):
            return [
                cast(dict[str, object], item)
                for item in cast(list[object], value)
                if isinstance(item, dict)
            ]
        return []
