"""Sensor adapter contracts for simulated, digital, and physical inputs."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .models import SensorFrame


@runtime_checkable
class SensorAdapter(Protocol):
    """Minimal sensor interface consumed by the embodiment layer."""

    @property
    def sensor_id(self) -> str:
        """Return the stable adapter identifier."""
        raise NotImplementedError

    @property
    def modality(self) -> str:
        """Return the sensor modality name."""
        raise NotImplementedError

    @property
    def active(self) -> bool:
        """Return whether the sensor is currently available."""
        raise NotImplementedError

    def sample(self, tick: int) -> SensorFrame:
        """Capture one sensor frame for *tick*."""
        raise NotImplementedError
