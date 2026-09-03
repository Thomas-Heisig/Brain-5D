"""Typed digital interoception contracts for system-state observations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from .models import JSONValue


@dataclass(frozen=True, slots=True)
class VitalSignal:
    """One body-relevant signal with explicit quality and safety metadata."""

    name: str
    value: JSONValue
    unit: str
    safe_range: tuple[float, float] | None = None
    warning_range: tuple[float, float] | None = None
    critical_range: tuple[float, float] | None = None
    confidence: float = 1.0
    freshness: str = "current"
    source: str = "system_sensor"
    causal_criticality: str = "informational"
    recoverability: str = "unknown"

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("signal name must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")

    @property
    def status(self) -> str:
        """Classify missing or numeric values without treating missing as safe."""
        if self.value is None:
            return "unknown"
        if self.critical_range is not None and self._outside(self.critical_range):
            return "critical"
        if self.warning_range is not None and self._outside(self.warning_range):
            return "warning"
        return "nominal"

    def _outside(self, bounds: tuple[float, float]) -> bool:
        if not isinstance(self.value, (int, float)) or isinstance(self.value, bool):
            return False
        return not bounds[0] <= self.value <= bounds[1]

    def to_json(self) -> dict[str, JSONValue]:
        """Return a stable JSON representation for telemetry and audit."""
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "safe_range": list(self.safe_range) if self.safe_range else None,
            "warning_range": list(self.warning_range) if self.warning_range else None,
            "critical_range": list(self.critical_range) if self.critical_range else None,
            "confidence": self.confidence,
            "freshness": self.freshness,
            "source": self.source,
            "causal_criticality": self.causal_criticality,
            "recoverability": self.recoverability,
            "status": self.status,
        }


@dataclass(frozen=True, slots=True)
class InteroceptionFrame:
    """A tick-bound collection of vital signals."""

    tick: int
    signals: tuple[VitalSignal, ...]

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "tick": self.tick,
            "signals": [signal.to_json() for signal in self.signals],
        }


@dataclass(frozen=True, slots=True)
class DriveState:
    """Deterministic regulatory drives derived from one interoception frame."""

    tick: int
    drives: dict[str, float | None]
    uncertainty: dict[str, float]

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "tick": self.tick,
            "drives": cast(dict[str, JSONValue], self.drives),
            "uncertainty": cast(dict[str, JSONValue], self.uncertainty),
        }


@dataclass(frozen=True, slots=True)
class RegulatoryState:
    """Bounded internal regulation variables, distinct from interpretation."""

    tick: int
    values: dict[str, float | None]
    uncertainty: dict[str, float]

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "tick": self.tick,
            "values": cast(dict[str, JSONValue], self.values),
            "uncertainty": cast(dict[str, JSONValue], self.uncertainty),
        }


@dataclass(frozen=True, slots=True)
class FunctionalState:
    """Bounded functional qualities; these are not human emotion claims."""

    tick: int
    valence: float | None
    activation: float | None
    safety: float | None
    uncertainty: float

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "tick": self.tick,
            "valence": self.valence,
            "activation": self.activation,
            "safety": self.safety,
            "uncertainty": self.uncertainty,
        }


_SIGNAL_METADATA: dict[str, dict[str, JSONValue]] = {
    "cpu_percent": {"unit": "%", "warning_range": [0.0, 85.0], "critical_range": [0.0, 98.0]},
    "memory_percent": {"unit": "%", "warning_range": [0.0, 85.0], "critical_range": [0.0, 98.0]},
    "memory_available_bytes": {"unit": "bytes", "causal_criticality": "continuity"},
    "temperature_c": {"unit": "degC", "warning_range": [-20.0, 80.0], "critical_range": [-30.0, 95.0]},
    "disk_free_bytes": {"unit": "bytes", "causal_criticality": "continuity"},
    "disk_read_bytes": {"unit": "bytes", "causal_criticality": "resource"},
    "disk_write_bytes": {"unit": "bytes", "causal_criticality": "resource"},
    "network_up": {"unit": "bool", "causal_criticality": "continuity"},
    "network_bytes_sent": {"unit": "bytes", "causal_criticality": "continuity"},
    "network_bytes_received": {"unit": "bytes", "causal_criticality": "continuity"},
    "battery_percent": {"unit": "%", "warning_range": [20.0, 100.0], "critical_range": [5.0, 100.0], "causal_criticality": "continuity"},
    "battery_plugged": {"unit": "bool", "causal_criticality": "continuity"},
    "fan_rpm": {"unit": "rpm", "causal_criticality": "thermal"},
    "task_progress": {"unit": "ratio", "causal_criticality": "task"},
    "novelty": {"unit": "ratio", "causal_criticality": "informational"},
    "actuator_confidence": {"unit": "ratio", "causal_criticality": "continuity"},
}


def normalize_vital_signals(readings: dict[str, JSONValue]) -> tuple[VitalSignal, ...]:
    """Convert raw readings into typed signals without inferring missing safety."""
    signals: list[VitalSignal] = []
    for name in sorted(_SIGNAL_METADATA):
        metadata = _SIGNAL_METADATA[name]
        signals.append(
            VitalSignal(
                name=name,
                value=readings.get(name),
                unit=cast(str, metadata.get("unit", "unknown")),
                warning_range=_range(metadata.get("warning_range")),
                critical_range=_range(metadata.get("critical_range")),
                causal_criticality=cast(
                    str, metadata.get("causal_criticality", "informational")
                ),
            )
        )
    return tuple(signals)


def derive_drives(frame: InteroceptionFrame) -> DriveState:
    """Derive bounded regulatory drives without claiming psychological states."""
    signals = {signal.name: signal for signal in frame.signals}
    cpu = _numeric_signal(signals.get("cpu_percent"))
    memory = _numeric_signal(signals.get("memory_percent"))
    temperature = _numeric_signal(signals.get("temperature_c"))
    network = signals.get("network_up")

    known_pressures = [
        pressure
        for pressure in (_pressure(cpu, 85.0), _pressure(memory, 85.0))
        if pressure is not None
    ]
    resource_pressure = max(known_pressures) if known_pressures else None
    thermal_threat = _pressure(temperature, 80.0, 95.0)
    continuity_risk = _continuity_risk(network)
    known_count = sum(value is not None for value in (cpu, memory, temperature, network))
    sensory_integrity = known_count / 4.0
    task_progress = _bounded_signal(signals.get("task_progress"))
    novelty = _bounded_signal(signals.get("novelty"))
    actuator_confidence = _bounded_signal(signals.get("actuator_confidence"))

    drives: dict[str, float | None] = {
        "thermal_threat": thermal_threat,
        "resource_pressure": resource_pressure,
        "sensory_integrity": sensory_integrity,
        "continuity_risk": continuity_risk,
        "task_progress": task_progress,
        "novelty": novelty,
        "actuator_confidence": actuator_confidence,
    }
    uncertainty = {
        "thermal_threat": _uncertainty(temperature),
        "resource_pressure": 1.0 if not known_pressures else 0.0,
        "sensory_integrity": 1.0 - sensory_integrity,
        "continuity_risk": _uncertainty(network),
        "task_progress": _uncertainty(task_progress),
        "novelty": _uncertainty(novelty),
        "actuator_confidence": _uncertainty(actuator_confidence),
    }
    return DriveState(tick=frame.tick, drives=drives, uncertainty=uncertainty)


def derive_regulatory_state(frame: InteroceptionFrame) -> RegulatoryState:
    """Derive bounded control variables without inventing unavailable telemetry."""
    drives = derive_drives(frame)
    resource_pressure = drives.drives["resource_pressure"]
    thermal_threat = drives.drives["thermal_threat"]
    values = {
        "thermal_margin": None if thermal_threat is None else 1.0 - thermal_threat,
        "energy_reserve": None if resource_pressure is None else 1.0 - resource_pressure,
        "continuity_risk": drives.drives["continuity_risk"],
        "sensory_integrity": drives.drives["sensory_integrity"],
        "resource_pressure": resource_pressure,
        "task_progress": drives.drives["task_progress"],
    }
    uncertainty = {
        "thermal_margin": drives.uncertainty["thermal_threat"],
        "energy_reserve": drives.uncertainty["resource_pressure"],
        "continuity_risk": drives.uncertainty["continuity_risk"],
        "sensory_integrity": drives.uncertainty["sensory_integrity"],
        "resource_pressure": drives.uncertainty["resource_pressure"],
        "task_progress": drives.uncertainty["task_progress"],
    }
    return RegulatoryState(tick=frame.tick, values=values, uncertainty=uncertainty)


def derive_functional_state(frame: InteroceptionFrame) -> FunctionalState:
    """Derive bounded technical qualities from regulatory state variables."""
    drives = derive_drives(frame)
    known_risks = [
        value
        for value in (
            drives.drives["thermal_threat"],
            drives.drives["resource_pressure"],
            drives.drives["continuity_risk"],
        )
        if value is not None
    ]
    safety = None if not known_risks else 1.0 - max(known_risks)
    activity_inputs = [
        value
        for value in (drives.drives["novelty"], drives.drives["resource_pressure"])
        if value is not None
    ]
    activation = None if not activity_inputs else sum(activity_inputs) / len(activity_inputs)
    valence = None if safety is None else (2.0 * safety) - 1.0
    uncertainty = sum(drives.uncertainty.values()) / len(drives.uncertainty)
    return FunctionalState(
        tick=frame.tick,
        valence=valence,
        activation=activation,
        safety=safety,
        uncertainty=uncertainty,
    )


def _numeric_signal(signal: VitalSignal | None) -> float | None:
    if signal is None or signal.value is None:
        return None
    if isinstance(signal.value, bool) or not isinstance(signal.value, (int, float)):
        return None
    return float(signal.value)


def _bounded_signal(signal: VitalSignal | None) -> float | None:
    value = _numeric_signal(signal)
    return None if value is None else max(0.0, min(1.0, value))


def _pressure(value: float | None, warning: float, critical: float = 100.0) -> float | None:
    if value is None:
        return None
    return max(0.0, min(1.0, (value - warning) / (critical - warning)))


def _continuity_risk(signal: VitalSignal | None) -> float | None:
    if signal is None or not isinstance(signal.value, bool):
        return None
    return 0.0 if signal.value else 1.0


def _uncertainty(value: object) -> float:
    return 1.0 if value is None else 0.0


def _range(value: JSONValue) -> tuple[float, float] | None:
    if not isinstance(value, list) or len(value) != 2:
        return None
    lower, upper = value
    if not isinstance(lower, (int, float)) or isinstance(lower, bool):
        return None
    if not isinstance(upper, (int, float)) or isinstance(upper, bool):
        return None
    return float(lower), float(upper)


__all__ = [
    "DriveState",
    "FunctionalState",
    "InteroceptionFrame",
    "RegulatoryState",
    "VitalSignal",
    "derive_drives",
    "derive_functional_state",
    "derive_regulatory_state",
    "normalize_vital_signals",
]
