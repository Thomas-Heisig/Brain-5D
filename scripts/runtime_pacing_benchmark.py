"""Measure RuntimeController pacing without changing simulation ``dt`` semantics."""

from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.controller.runtime import RuntimeController


@dataclass(slots=True)
class _StepResult:
    spikes_this_tick: int = 0


class _BenchmarkNetwork:
    """Minimal deterministic network used only to measure controller pacing."""

    def __init__(self) -> None:
        self.current_tick = 0
        self.neuron_count = 1
        self.synapse_count = 0
        self.queued_event_count = 0

    def step(self) -> _StepResult:
        self.current_tick += 1
        return _StepResult()


def run_pacing_case(
    target_hz: float | None,
    *,
    duration_seconds: float = 0.2,
    batch_size: int = 1,
    dt_ms: float = 1.0,
) -> dict[str, Any]:
    """Run one bounded pacing case and return a machine-readable measurement."""
    if duration_seconds <= 0.0:
        raise ValueError("duration_seconds must be positive")
    if target_hz is not None and target_hz <= 0.0:
        raise ValueError("target_hz must be positive or None")
    network = _BenchmarkNetwork()
    controller = RuntimeController(
        network,
        batch_size=batch_size,
        target_hz=target_hz,
        telemetry_interval_ticks=1,
    )
    controller.start()
    warmup_deadline = time.perf_counter() + max(0.1, duration_seconds)
    while controller.telemetry.completed_ticks == 0:
        if time.perf_counter() >= warmup_deadline:
            raise RuntimeError("RuntimeController did not complete a warmup tick")
        time.sleep(0.001)
    warmup_ticks = controller.telemetry.completed_ticks
    measurement_duration = duration_seconds
    if target_hz is not None:
        measurement_duration = max(
            measurement_duration, (3.0 * batch_size) / target_hz
        )
    started = time.perf_counter()
    time.sleep(measurement_duration)
    controller.stop()
    elapsed = max(time.perf_counter() - started, 1e-9)
    telemetry = controller.telemetry
    completed_ticks = max(0, telemetry.completed_ticks - warmup_ticks)
    achieved_hz = completed_ticks / elapsed
    return {
        "target_hz": target_hz,
        "achieved_hz": achieved_hz,
        "realtime_ratio": (
            None if target_hz is None else achieved_hz / target_hz
        ),
        "duration_seconds": elapsed,
        "measurement_duration_seconds": measurement_duration,
        "warmup_ticks": warmup_ticks,
        "ticks": completed_ticks,
        "dt_ms": dt_ms,
        "tick_cost_ms": telemetry.tick_latency_ms,
        "tick_profile_ms": dict(telemetry.tick_profile),
        "controller_runtime_mode": telemetry.runtime_mode,
        "simulation_tick": network.current_tick,
    }


def build_report(
    *,
    duration_seconds: float = 0.2,
    targets: tuple[float | None, ...] = (1.0, 10.0, None),
    dt_ms: float = 1.0,
) -> dict[str, Any]:
    """Build a bounded pacing report for low-rate, targeted and unlimited modes."""
    return {
        "schema_version": 1,
        "benchmark": "runtime_pacing",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "duration_seconds_requested": duration_seconds,
        "dt_ms": dt_ms,
        "cases": [
            run_pacing_case(target, duration_seconds=duration_seconds, dt_ms=dt_ms)
            for target in targets
        ],
        "scientific_claim": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--duration", type=float, default=0.2)
    parser.add_argument("--dt-ms", type=float, default=1.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = build_report(duration_seconds=args.duration, dt_ms=args.dt_ms)
    payload = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())