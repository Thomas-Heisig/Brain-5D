"""Fail fast unless the real science-suite network shows observable activity."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

from src.research.experiment_suite import run_ping  # noqa: E402


def main() -> int:
    config = yaml.safe_load(
        (ROOT / "configs/learning_experiment.yaml").read_text(encoding="utf-8")
    )
    runs = run_ping(config, seeds=(42,), ticks=12)
    if len(runs) != 2:
        raise RuntimeError(f"Expected two ping conditions, got {len(runs)}")

    metrics = [run.metrics for run in runs]
    for run in runs:
        print(run.condition, run.metrics)

    if not all(int(item.get("ticks_executed", 0)) > 0 for item in metrics):
        raise RuntimeError(f"No executed ticks observed: {metrics}")
    if not all(int(item.get("total_synapses", 0)) > 0 for item in metrics):
        raise RuntimeError(f"No synapses observed: {metrics}")
    if not any(int(item.get("total_spikes", 0)) > 0 for item in metrics):
        raise RuntimeError(f"No neuronal spikes observed: {metrics}")
    if not any(int(item.get("delivered_synaptic_events", 0)) > 0 for item in metrics):
        raise RuntimeError(f"No delivered synaptic events observed: {metrics}")

    print("Real network activity verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
