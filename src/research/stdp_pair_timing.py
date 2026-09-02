"""Deterministic laboratory protocol for pair-based STDP timing curves."""

from __future__ import annotations

from statistics import fmean
from typing import Any

from src.learning.stdp_plugin import STDPParameters, STDPSynapse

PROTOCOL_ID = "stdp_pair_timing_v1"
DELTA_T_MS = (-50, -20, -10, -5, -1, 0, 1, 5, 10, 20, 50)
REPLICATIONS = 10
INITIAL_WEIGHT = 0.5
PARAMETERS = STDPParameters(
    a_plus=0.1,
    a_minus=0.12,
    tau_plus=20.0,
    tau_minus=20.0,
)


def run_pair_timing_protocol() -> dict[str, Any]:
    """Measure the STDP timing curve with fixed, isolated conditions.

    The protocol does not access the Brain-5D runtime, filesystem, network,
    or any language model. Each replication receives a new synapse and the
    same pre/post timing, making the measurement deterministic and auditable.
    """
    rows: list[dict[str, float | int]] = []
    for delta_t in DELTA_T_MS:
        changes = [_measure_delta_weight(delta_t) for _ in range(REPLICATIONS)]
        rows.append(
            {
                "delta_t_ms": delta_t,
                "replications": REPLICATIONS,
                "mean_delta_weight": fmean(changes),
                "min_delta_weight": min(changes),
                "max_delta_weight": max(changes),
            }
        )

    positive = [row["mean_delta_weight"] for row in rows if row["delta_t_ms"] > 0]
    negative = [row["mean_delta_weight"] for row in rows if row["delta_t_ms"] < 0]
    zero = next(row["mean_delta_weight"] for row in rows if row["delta_t_ms"] == 0)
    supported = all(change > 0 for change in positive) and all(
        change < 0 for change in negative
    ) and zero == 0.0
    return {
        "protocol": PROTOCOL_ID,
        "seed": 42,
        "conditions": {
            "initial_weight": INITIAL_WEIGHT,
            "parameters": PARAMETERS.to_dict(),
            "replications_per_delta_t": REPLICATIONS,
        },
        "measurements": rows,
        "summary": {
            "total_replications": len(DELTA_T_MS) * REPLICATIONS,
            "mean_ltp": fmean(positive),
            "mean_ltd": fmean(negative),
            "zero_delta_weight": zero,
            "hypothesis_supported": supported,
        },
    }


def _measure_delta_weight(delta_t_ms: int) -> float:
    synapse = STDPSynapse.from_parameters(INITIAL_WEIGHT, PARAMETERS)
    reference_tick = 100
    if delta_t_ms < 0:
        synapse.post_spike(reference_tick + delta_t_ms)
        return synapse.pre_spike(reference_tick)
    synapse.pre_spike(reference_tick)
    return synapse.post_spike(reference_tick + delta_t_ms)