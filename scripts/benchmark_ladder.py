"""Run a bounded, reproducible Brain-5D scaling benchmark ladder.

Examples:
    python scripts/benchmark_ladder.py --tiers 100,500,5000 --ticks 20
    python scripts/benchmark_ladder.py --tiers 5000,50000,1000000 --ticks 10 --allow-large

The benchmark reports construction and step throughput. It does not claim
scientific performance evidence; hardware, Python version and configuration
are recorded in the JSON output.
"""

from __future__ import annotations

import argparse
import json
import platform
import random
import sys
import time
from pathlib import Path
from typing import Any

# Make direct ``python scripts/benchmark_ladder.py`` invocation equivalent to
# running the module from the repository root.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_TIERS = (5_000, 25_000, 100_000, 1_000_000)
LARGE_TIER_LIMIT = 100_000


def build_network(neuron_count: int, seed: int) -> Any:
    from src.core.network import Brain5DConfig, NeuralNetwork
    from src.core.spatial_index import linear_to_5d

    side = max(1, neuron_count)
    config = Brain5DConfig.from_dict(
        {
            "dimensions": [side, 1, 1, 1, 1],
            "network": {
                "initial_connections_per_neuron": 0,
                "neighbour_radius": 1.0,
            },
        }
    )
    network = NeuralNetwork(config, random.Random(seed))
    for index in range(neuron_count):
        network.add_neuron(linear_to_5d(index, config.dimensions))
    return network


def run_tier(neuron_count: int, ticks: int, seed: int) -> dict[str, Any]:
    started = time.perf_counter()
    network = build_network(neuron_count, seed)
    construction_seconds = time.perf_counter() - started

    step_started = time.perf_counter()
    for _ in range(ticks):
        network.step()
    step_seconds = time.perf_counter() - step_started

    return {
        "neurons": neuron_count,
        "synapses": network.get_state_summary().get("synapses", 0),
        "ticks": ticks,
        "construction_seconds": round(construction_seconds, 6),
        "step_seconds": round(step_seconds, 6),
        "ticks_per_second": round(ticks / step_seconds, 3) if step_seconds else None,
        "neurons_per_second": (
            round(neuron_count * ticks / step_seconds, 3) if step_seconds else None
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tiers",
        default=",".join(str(value) for value in DEFAULT_TIERS),
        help="Comma-separated neuron counts (default: 5000,25000,100000,1000000)",
    )
    parser.add_argument("--ticks", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--allow-large",
        action="store_true",
        help="Allow tiers above the 100k safety limit.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.ticks <= 0:
        raise SystemExit("--ticks must be positive")
    tiers = tuple(sorted({int(value) for value in args.tiers.split(",") if value}))
    if not tiers or any(value <= 0 for value in tiers):
        raise SystemExit("--tiers must contain positive integers")
    if not args.allow_large and any(value > LARGE_TIER_LIMIT for value in tiers):
        raise SystemExit(
            "tiers above 100000 require --allow-large; this prevents accidental 1M runs"
        )

    report = {
        "schema_version": 1,
        "benchmark": "brain5d_scaling_ladder",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "seed": args.seed,
        "requested_ticks": args.ticks,
        "tiers": [run_tier(value, args.ticks, args.seed) for value in tiers],
        "scientific_claim": False,
    }
    payload = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
