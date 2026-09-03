"""Small deterministic statistics writer for experiment DATA boundaries."""

from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import fmean, median, pstdev
from typing import Any, Iterable


def summarize(values: Iterable[float]) -> dict[str, Any]:
    """Return reproducible descriptive statistics without any model call."""
    samples = [float(value) for value in values if math.isfinite(float(value))]
    if not samples:
        return {"n": 0, "missing_values": 0, "status": "NO_FINITE_VALUES"}
    return {
        "n": len(samples),
        "missing_values": 0,
        "mean": fmean(samples),
        "median": median(samples),
        "std": pstdev(samples),
        "min": min(samples),
        "max": max(samples),
        "method": "population_descriptive_statistics",
    }


def write_statistics(experiment_root: Path, values: Iterable[float]) -> Path:
    """Write the canonical deterministic statistics artifact for one run."""
    path = experiment_root / "analysis" / "statistics.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summarize(values), indent=2) + "\n", encoding="utf-8")
    return path
