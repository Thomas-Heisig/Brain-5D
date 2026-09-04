"""Tests for the real-host embodiment self-model contract."""

from __future__ import annotations

from pathlib import Path

from src.embodiment import ConnectionManager
from src.embodiment.system_sensor import host_system_readings

STATIC = Path("src/dashboard/static")


def test_real_body_manager_adds_measured_host_snapshot() -> None:
    payload = ConnectionManager(cache_seconds=60).to_json()

    host = payload["host"]
    contract = payload["body_contract"]
    assert isinstance(host, dict)
    assert isinstance(host["cpu_percent"], float)
    assert isinstance(host["memory_total_bytes"], int)
    assert isinstance(host["network_interfaces"], dict)
    assert host["unix_time"] is not None
    assert isinstance(contract, dict)
    assert contract["observed_only"] is True
    assert contract["missing_values_are_unknown"] is True
    assert contract["availability_is_not_authorization"] is True
    assert contract["per_device_identity"] is True


def test_host_snapshot_exposes_real_pc_resources_without_fallback_values() -> None:
    readings = host_system_readings(7)

    assert readings["tick"] == 7
    assert isinstance(readings["cpu_percent_per_core"], list)
    assert isinstance(readings["memory_available_bytes"], int)
    assert isinstance(readings["disk_free_bytes"], int)
    assert isinstance(readings["network_interfaces"], dict)
    assert isinstance(readings["temperatures"], dict)
    assert isinstance(readings["fans"], dict)
    assert readings["temperature_c"] is None or isinstance(
        readings["temperature_c"], float
    )
    assert readings["fan_rpm"] is None or isinstance(readings["fan_rpm"], float)


def test_dynamic_self_model_is_real_data_driven_and_theme_safe() -> None:
    module = (STATIC / "embodiment-self-model.js").read_text(encoding="utf-8")
    styles = (STATIC / "embodiment-self-model.css").read_text(encoding="utf-8")
    console = (STATIC / "console-log.js").read_text(encoding="utf-8")

    assert 'readJson("/api/embodiment/connections")' in module
    assert 'readJson("/api/status")' in module
    assert "connections.filter((item) => item.available)" in module
    assert "host.temperature_c == null" in module
    assert "Nicht erkannte Hardware wird nicht als Organ dargestellt" in module
    assert 'body[data-theme="light"]' in styles
    assert "prefers-reduced-motion" in styles
    assert 'import "./embodiment-self-model.js"' in console
