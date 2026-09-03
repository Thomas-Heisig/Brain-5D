from __future__ import annotations

import pytest

from src.embodiment import (
    InteroceptionFrame,
    SystemSensorAdapter,
    VitalSignal,
    derive_drives,
    derive_regulatory_state,
    normalize_vital_signals,
)
from src.embodiment.system_sensor import host_system_readings


def test_missing_signal_is_unknown_and_not_nominal() -> None:
    signals = normalize_vital_signals({"cpu_percent": 42.0})

    temperature = next(signal for signal in signals if signal.name == "temperature_c")
    assert temperature.value is None
    assert temperature.status == "unknown"


def test_signal_quality_and_critical_range_are_explicit() -> None:
    signal = VitalSignal(
        name="thermal_margin",
        value=105.0,
        unit="degC",
        critical_range=(0.0, 95.0),
        confidence=0.8,
    )

    assert signal.status == "critical"
    assert signal.to_json()["confidence"] == 0.8


def test_system_sensor_exposes_typed_interoception_without_changing_sample() -> None:
    sensor = SystemSensorAdapter(lambda tick: {"cpu_percent": float(tick)})

    frame = sensor.sample_interoception(7)

    assert frame.tick == 7
    assert frame.to_json()["signals"]


def test_confidence_must_be_bounded() -> None:
    with pytest.raises(ValueError, match="confidence"):
        VitalSignal(name="test", value=1.0, unit="x", confidence=1.1)


def test_drives_are_bounded_and_derive_resource_and_continuity_pressure() -> None:
    signals = normalize_vital_signals(
        {"cpu_percent": 92.0, "memory_percent": 40.0, "temperature_c": 90.0, "network_up": False}
    )

    drives = derive_drives(InteroceptionFrame(3, signals))

    assert drives.drives["resource_pressure"] == pytest.approx(7 / 15)
    assert drives.drives["thermal_threat"] == pytest.approx(10 / 15)
    assert drives.drives["continuity_risk"] == 1.0
    assert all(value is None or 0.0 <= value <= 1.0 for value in drives.drives.values())


def test_unavailable_drive_is_explicitly_uncertain() -> None:
    frame = SystemSensorAdapter(lambda tick: {}).sample_interoception(4)

    drives = derive_drives(frame)

    assert drives.drives["task_progress"] is None
    assert drives.uncertainty["task_progress"] == 1.0


def test_normalizer_includes_optional_resource_and_continuity_signals() -> None:
    names = {signal.name for signal in normalize_vital_signals({})}

    assert {
        "memory_available_bytes",
        "disk_free_bytes",
        "disk_read_bytes",
        "disk_write_bytes",
        "network_bytes_sent",
        "network_bytes_received",
        "battery_percent",
        "battery_plugged",
        "fan_rpm",
    } <= names


def test_host_readings_expose_optional_metrics_without_external_services() -> None:
    readings = host_system_readings(2)

    assert readings["tick"] == 2
    assert isinstance(readings["memory_available_bytes"], int)
    assert isinstance(readings["disk_free_bytes"], int)


def test_regulatory_state_is_bounded_and_fail_closed() -> None:
    frame = InteroceptionFrame(
        12,
        normalize_vital_signals(
            {
                "cpu_percent": 90.0,
                "memory_percent": 40.0,
                "temperature_c": 85.0,
                "network_up": False,
                "task_progress": 1.4,
            }
        ),
    )

    state = derive_regulatory_state(frame)

    assert state.values["thermal_margin"] == pytest.approx(2 / 3)
    assert state.values["energy_reserve"] == pytest.approx(2 / 3)
    assert state.values["continuity_risk"] == 1.0
    assert state.values["sensory_integrity"] == 1.0
    assert state.values["resource_pressure"] == pytest.approx(1 / 3)
    assert state.values["task_progress"] == 1.0
    assert all(0.0 <= value <= 1.0 for value in state.values.values() if value is not None)


def test_regulatory_state_keeps_unknown_sources_unknown() -> None:
    state = derive_regulatory_state(
        InteroceptionFrame(1, normalize_vital_signals({}))
    )

    assert state.values["thermal_margin"] is None
    assert state.values["energy_reserve"] is None
    assert state.uncertainty["thermal_margin"] == 1.0
