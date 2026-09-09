"""Engineering-only v0.6 performance and pacing acceptance contract.

The contract deliberately separates reproducible software budgets from
scientific evidence. It validates benchmark/telemetry payloads and never
promotes experimental results.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping, cast


class PerformanceContractError(ValueError):
    """Raised when a performance payload violates the v0.6 contract."""


def _number(value: object, *, default: float) -> float:
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise PerformanceContractError(
            f"expected numeric performance value, got {value!r}"
        )
    return float(value)


def _string_mapping(value: object, *, label: str) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise PerformanceContractError(f"{label} must be an object")
    mapping = cast(dict[object, object], value)
    if any(not isinstance(key, str) for key in mapping):
        raise PerformanceContractError(f"{label} keys must be strings")
    return cast(Mapping[str, object], mapping)


def load_performance_budgets(path: Path) -> dict[str, object]:
    payload: object = json.loads(path.read_text(encoding="utf-8"))
    data = dict(_string_mapping(payload, label="performance budget"))
    schema_version = data.get("schema_version", 0)
    if isinstance(schema_version, bool) or not isinstance(schema_version, int):
        raise PerformanceContractError(
            "performance budget schema_version must be an integer"
        )
    if schema_version != 1:
        raise PerformanceContractError("unsupported performance budget schema")
    return data


def evaluate_scaling_tier(
    tier: Mapping[str, object], budgets: Mapping[str, object]
) -> tuple[str, ...]:
    """Return deterministic budget violations for one scaling tier."""
    scaling = _string_mapping(budgets.get("scaling", {}), label="scaling budget")
    violations: list[str] = []
    tick_cost = _number(tier.get("mean_tick_cost_ms"), default=0.0)
    peak_per_neuron = _number(tier.get("python_peak_bytes_per_neuron"), default=0.0)
    max_tick = _number(scaling.get("max_mean_tick_cost_ms"), default=float("inf"))
    max_peak = _number(
        scaling.get("max_python_peak_bytes_per_neuron"), default=float("inf")
    )
    if tick_cost > max_tick:
        violations.append(f"mean_tick_cost_ms {tick_cost:.6f} > {max_tick:.6f}")
    if peak_per_neuron > max_peak:
        violations.append(
            f"python_peak_bytes_per_neuron {peak_per_neuron:.3f} > {max_peak:.3f}"
        )
    return tuple(violations)


def evaluate_runtime_profile(
    *,
    tick_latency_ms: float,
    phases_ms: Mapping[str, float],
    budgets: Mapping[str, object],
) -> tuple[str, ...]:
    """Validate RuntimeController and named subsystem phase thresholds."""
    runtime = _string_mapping(budgets.get("runtime", {}), label="runtime budget")
    phase_budget = _string_mapping(
        budgets.get("phases_ms_per_tick", {}), label="phase budget"
    )
    violations: list[str] = []
    max_latency = _number(runtime.get("max_tick_latency_ms"), default=float("inf"))
    if tick_latency_ms > max_latency:
        violations.append(f"tick_latency_ms {tick_latency_ms:.6f} > {max_latency:.6f}")
    required = {
        "learning",
        "homeostasis",
        "structural",
        "embodiment",
        "neural_symbiosis_msba",
        "dashboard_telemetry",
        "storage",
    }
    missing = sorted(required - set(phase_budget.keys()))
    if missing:
        raise PerformanceContractError(
            "missing subsystem phase budgets: " + ", ".join(missing)
        )
    for phase in sorted(required):
        elapsed = phases_ms.get(phase, 0.0)
        maximum = _number(phase_budget[phase], default=float("inf"))
        if elapsed > maximum:
            violations.append(f"{phase} {elapsed:.6f}ms > {maximum:.6f}ms")
    return tuple(violations)


def evaluate_pacing(
    *,
    target_hz: float | None,
    achieved_hz: float,
    realtime_ratio: float,
    dt_seconds: float,
    runtime_mode: str,
    budgets: Mapping[str, object],
) -> tuple[str, ...]:
    """Apply explicit acceptance criteria to TARGETED and MAX runtime modes."""
    pacing = _string_mapping(budgets.get("pacing", {}), label="pacing budget")
    violations: list[str] = []
    if achieved_hz < 0.0 or realtime_ratio < 0.0 or dt_seconds <= 0.0:
        return ("pacing telemetry contains invalid values",)
    expected_ratio = achieved_hz * dt_seconds
    tolerance = _number(pacing.get("realtime_ratio_absolute_tolerance"), default=1e-9)
    if abs(realtime_ratio - expected_ratio) > tolerance:
        violations.append("realtime_ratio is inconsistent with achieved_hz * dt")
    if target_hz is None:
        if runtime_mode != "MAX":
            violations.append("unlimited target requires runtime_mode=MAX")
        return tuple(violations)
    if target_hz <= 0.0:
        return (*violations, "target_hz must be positive or null")
    minimum_fraction = _number(pacing.get("minimum_target_fraction"), default=0.75)
    if achieved_hz < target_hz * minimum_fraction:
        violations.append(
            f"achieved_hz {achieved_hz:.6f} below "
            f"{minimum_fraction:.3f} of target {target_hz:.6f}"
        )
    if runtime_mode not in {"TARGETED", "COMPUTE LIMITED"}:
        violations.append("finite target requires TARGETED or COMPUTE LIMITED mode")
    return tuple(violations)
