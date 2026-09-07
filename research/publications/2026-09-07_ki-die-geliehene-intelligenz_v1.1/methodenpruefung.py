"""Check finite methodological witnesses, not Brain-5D runtime capabilities."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def addresses(n: int, dimensions: int) -> list[tuple[int, ...]]:
    """Injectively label a fixed population without changing its size."""
    if n < 1 or dimensions < 1:
        raise ValueError("Positive population and dimensionality required")
    base = 1
    while base**dimensions < n:
        base += 1
    result = []
    for index in range(n):
        digits = []
        for _ in range(dimensions):
            digits.append(index % base)
            index //= base
        result.append(tuple(digits))
    return result


def trajectory(
    dimensions: int, *, permute: bool = False, break_edge: bool = False
) -> list[list[int]]:
    """Simulate a binary ring, explicitly not the Brain-5D neuron model."""
    n, ticks = 12, 64
    labels = addresses(n, dimensions)
    if permute:
        labels = labels[5:] + labels[:5]
    state = {label: int(i == 0) for i, label in enumerate(labels)}
    edges = [(labels[i], labels[(i + 1) % n]) for i in range(n)]
    if break_edge:
        edges = edges[1:]
    output = [[state[label] for label in labels]]
    for tick in range(ticks):
        incoming = dict.fromkeys(labels, 0)
        for source, target in edges:
            incoming[target] += state[source]
        state = {
            label: int(incoming[label] > 0 or (i == 0 and tick % 7 == 0))
            for i, label in enumerate(labels)
        }
        output.append([state[label] for label in labels])
    return output


def memory_witness(informative: bool, bit: int) -> list[list[int]]:
    """Construct persistent codes with identical population summaries."""
    channel = bit if informative else 0
    return [[int(channel == 0), int(channel == 1)] for _ in range(4)]


def summarize(trace: list[list[int]]) -> tuple[int, int]:
    """Return total activity and number of ever-active channels."""
    return sum(map(sum, trace)), sum(any(row[i] for row in trace) for i in range(2))


def run_checks() -> dict[str, Any]:
    """Execute witnesses and fail rather than accepting a false assertion."""
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool) -> None:
        if not condition:
            raise AssertionError(name)
        checks.append({"name": name, "passed": True})

    dimensions = list(range(2, 7))
    reference = trajectory(2)
    for dim in dimensions:
        labels = addresses(12, dim)
        check(f"addresses_{dim}d_injective", len(set(labels)) == 12)
        check(f"addresses_{dim}d_shape", all(len(label) == dim for label in labels))
        check(f"trajectory_{dim}d_equal", trajectory(dim) == reference)
        check(f"permutation_{dim}d_equal", trajectory(dim, permute=True) == reference)
    check("nonzero_activity", sum(map(sum, reference)) > 0)
    check("nonconstant_trajectory", len({tuple(row) for row in reference}) > 1)
    check(
        "negative_control_changes_trajectory", trajectory(5, break_edge=True) != reference
    )
    records = []
    for bit in (0, 1):
        informative = memory_witness(True, bit)
        uninformative = memory_witness(False, bit)
        check(
            f"same_counts_bit_{bit}", summarize(informative) == summarize(uninformative)
        )
        records.append(
            {
                "input_bit": bit,
                "informative_trace": informative,
                "uninformative_trace": uninformative,
                "aggregate_total_spikes": summarize(informative)[0],
                "aggregate_activated_channels": summarize(informative)[1],
            }
        )
    acc_info = sum(memory_witness(True, b)[-1][1] == b for b in (0, 1)) / 2
    acc_none = sum(memory_witness(False, b)[-1][1] == b for b in (0, 1)) / 2
    check("different_decodability", acc_info == 1.0 and acc_none == 0.5)
    observed = [{"input": b, "core": b, "external": b} for b in (0, 1)]
    check(
        "observational_equivalence",
        all(row["core"] == row["external"] for row in observed),
    )
    check(
        "intervention_separates_models",
        all((1 - row["core"]) != row["external"] for row in observed),
    )
    return {
        "schema_version": "1.0",
        "kind": "methodological_witness_checks",
        "brain5d_runtime_executed": False,
        "scientific_evidence_promotion": False,
        "preregistered": False,
        "limitations": "Constructed finite witnesses, not learned capabilities or a topology benchmark.",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "fixture": {
            "nodes": 12,
            "updates": 64,
            "recorded_states": 65,
            "dimensions": dimensions,
        },
        "memory_records": records,
        "decoding_accuracy": {"informative": acc_info, "uninformative": acc_none},
        "checks_passed": len(checks),
        "checks": checks,
    }


def main() -> None:
    """Write a report, or compare it without changing any repository file."""
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--output", type=Path)
    group.add_argument("--check", type=Path)
    args = parser.parse_args()
    report = run_checks()
    payload = (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if args.check and args.check.read_bytes() != payload:
        raise SystemExit("Stored report differs from this script's actual output")
    if args.output:
        args.output.write_bytes(payload)
    print(
        f"PASS: {report['checks_passed']} methodological checks; Brain-5D runtime NOT executed"
    )


if __name__ == "__main__":
    main()
