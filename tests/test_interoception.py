from __future__ import annotations

import pytest

from src.embodiment import SystemSensorAdapter, VitalSignal, normalize_vital_signals


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
