"""Engineering-only v0.6 performance and pacing acceptance contract.

The contract deliberately separates reproducible software budgets from
scientific evidence.  It validates benchmark/telemetry payloads and never
promotes experimental results.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, cast


class PerformanceContractError(ValueError):
    """Raised when a performance payload violates the v0.6 contract."""


def load_performance_budgets(path: Path) -> dict[str, Any]:
    payload: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise PerformanceContractError("performance budget must be a JSON object")
    data = cast(dict[str, Any], payload)
    if int(data.get("schema_version", 0)) != 1:
        raise PerformanceContractError("unsupported performance budget schema")
    return data


def evaluate_scaling_tier(
    tier: Mapping[str, Any], budgets: Mapping[str, Any]
) -> tuple[str, ...]:
    """Return deterministic budget violations for one scaling tier."""
    scaling = budgets.get("scaling", {})
    if not isinstance(scaling, Mapping):
        raise PerformanceContractError("scaling budget must be an object")
    violations: list[str] = []
    tick_cost = float(tier.get("mean_tick_cost_ms") or 0.0)
    peak_per_neuron = float(tier.get("python_peak_bytes_per_neuron") or 0.0)
    max_tick = float(scaling.get("max_mean_tick_cost_ms", float("inf")))
    max_peak = float(scaling.get("max_python_peak_bytes_per_neuron", float("inf")))
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
    budgets: Mapping[str, Any],
) -> tuple[str, ...]:
    """Validate RuntimeController and named subsystem phase thresholds."""
    runtime = budgets.get("runtime", {})
    phase_budget = budgets.get("phases_ms_per_tick", {})
    if not isinstance(runtime, Mapping) or not isinstance(phase_budget, Mapping):
        raise PerformanceContractError("runtime and phase budgets must be objects")
    violations: list[str] = []
    max_latency = float(runtime.get("max_tick_latency_ms", float("inf")))
    if float(tick_latency_ms) > max_latency:
        violations.append(
            f"tick_latency_ms {float(tick_latency_ms):.6f} > {max_latency:.6f}"
        )
    required = {
        "learning",
        "homeostasis",
        "structural",
        "embodiment",
        "neural_symbiosis_msba",
        "dashboard_telemetry",
        "storage",
    }
    missing = sorted(required - set(phase_budget))
    if missing:
        raise PerformanceContractError(
            "missing subsystem phase budgets: " + ", ".join(missing)
        )
    for phase in sorted(required):
        elapsed = float(phases_ms.get(phase, 0.0))
        maximum = float(phase_budget[phase])
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
    budgets: Mapping[str, Any],
) -> tuple[str, ...]:
    """Apply explicit acceptance criteria to TARGETED and MAX runtime modes."""
    pacing = budgets.get("pacing", {})
    if not isinstance(pacing, Mapping):
        raise PerformanceContractError("pacing budget must be an object")
    violations: list[str] = []
    if achieved_hz < 0.0 or realtime_ratio < 0.0 or dt_seconds <= 0.0:
        return ("pacing telemetry contains invalid values",)
    expected_ratio = achieved_hz * dt_seconds
    tolerance = float(pacing.get("realtime_ratio_absolute_tolerance", 1e-9))
    if abs(realtime_ratio - expected_ratio) > tolerance:
        violations.append("realtime_ratio is inconsistent with achieved_hz * dt")
    if target_hz is None:
        if runtime_mode != "MAX":
            violations.append("unlimited target requires runtime_mode=MAX")
        return tuple(violations)
    if target_hz <= 0.0:
        return (*violations, "target_hz must be positive or null")
    minimum_fraction = float(pacing.get("minimum_target_fraction", 0.75))
    if achieved_hz < target_hz * minimum_fraction:
        violations.append(
            f"achieved_hz {achieved_hz:.6f} below {minimum_fraction:.3f} of target {target_hz:.6f}"
        )
    if runtime_mode not in {"TARGETED", "COMPUTE LIMITED"}:
        violations.append("finite target requires TARGETED or COMPUTE LIMITED mode")
    return tuple(violations)
