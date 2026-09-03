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


_SIGNAL_METADATA: dict[str, dict[str, JSONValue]] = {
    "cpu_percent": {"unit": "%", "warning_range": [0.0, 85.0], "critical_range": [0.0, 98.0]},
    "memory_percent": {"unit": "%", "warning_range": [0.0, 85.0], "critical_range": [0.0, 98.0]},
    "temperature_c": {"unit": "degC", "warning_range": [-20.0, 80.0], "critical_range": [-30.0, 95.0]},
    "network_up": {"unit": "bool", "causal_criticality": "continuity"},
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


def _range(value: JSONValue) -> tuple[float, float] | None:
    if not isinstance(value, list) or len(value) != 2:
        return None
    if not all(isinstance(item, (int, float)) for item in value):
        return None
    return float(value[0]), float(value[1])


__all__ = ["InteroceptionFrame", "VitalSignal", "normalize_vital_signals"]
