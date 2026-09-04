"""Real-host body inventory for the Brain-5D embodiment dashboard.

This module deliberately extends connection discovery without changing its
fail-closed authorization semantics.  Availability is observation; it is not
permission to capture, transmit, print, play audio, or move hardware.
"""

from __future__ import annotations

import time
from typing import cast

from .connections import ConnectionManager as BaseConnectionManager
from .models import JSONValue
from .system_sensor import host_system_readings


class ConnectionManager(BaseConnectionManager):
    """Connection manager that adds a read-only, real host telemetry snapshot."""

    def to_json(self, *, refresh: bool = False) -> dict[str, JSONValue]:
        payload = super().to_json(refresh=refresh)
        sample_tick = int(time.monotonic() * 1000)
        payload["host"] = cast(
            dict[str, JSONValue], dict(host_system_readings(sample_tick))
        )
        payload["body_contract"] = {
            "observed_only": True,
            "missing_values_are_unknown": True,
            "availability_is_not_authorization": True,
            "sample_clock": "host_monotonic_ms",
        }
        return payload


__all__ = ["ConnectionManager"]
