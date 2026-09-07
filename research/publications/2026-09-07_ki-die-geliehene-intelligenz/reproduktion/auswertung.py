#!/usr/bin/env python3
"""Recalculate descriptive report aggregates, not Brain-5D experiments.

Standard library only. The source values are explicitly transcribed summaries.
No p-values, confidence intervals, independence claims, or evidence promotion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path
from typing import Any


def number(value: Any, field: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{field}: Boolean is not a numeric observation")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field}: invalid numeric value") from exc
    if not result.is_finite():
        raise ValueError(f"{field}: non-finite numeric value")
    return result


def compare(a: Any, b: Any, field: str) -> dict[str, Any]:
    x, y = number(a, field), number(b, field)
    return {
        "reference": float(x),
        "comparison": float(y),
        "absolute_difference": float(y - x),
        "ratio": None if x == 0 else float(y / x),
        "relative_change_percent": None if x == 0 else float((y - x) / x * 100),
        "ratio_note": "undefined for zero reference" if x == 0 else "descriptive only",
    }


def analyse(source: dict[str, Any], input_digest: str) -> dict[str, Any]:
    if source.get("input_kind") != "transcribed_report_aggregates_not_raw_observations":
        raise ValueError("Unexpected input kind: this program handles report aggregates only")
    rec = source["recurrence"]
    off, on = rec["recurrence_off"], rec["recurrence_on"]
    fields = ("total_spikes", "delivered_synaptic_events", "activated_neurons",
              "recurrent_events", "propagation_depth")
    with localcontext() as ctx:
        ctx.prec = 40
        recurrence = {key: compare(off[key], on[key], key) for key in fields}
        learning = compare(source["learning"]["initial_weight"],
                           source["learning"]["final_weight"], "weight")
        raw = source["compression_pointer"]
        compressed = number(raw["compressed_bytes"], "compressed_bytes")
        uncompressed = number(raw["uncompressed_bytes"], "uncompressed_bytes")
        if compressed <= 0 or uncompressed <= 0:
            raise ValueError("Byte counts must be positive")
        compression = {
            "uncompressed_to_compressed_ratio": float(uncompressed / compressed),
            "size_reduction_percent": float((1 - compressed / uncompressed) * 100),
            "scope": "one reported raw-artifact pointer; no general compression claim",
            "raw_digest_verified": False,
        }
    return {
        "input_sha256": input_digest,
        "calculation_status": "descriptive_secondary_calculation",
        "new_experiment": False,
        "raw_event_reanalysis": False,
        "independent_replication": False,
        "evidence_promotion": False,
        "recurrence_report_comparisons": recurrence,
        "learning_weight_report_comparison": learning,
        "compression_pointer_comparison": compression,
        "excluded_inferences": [
            "No significance tests without raw data and a valid sampling design",
            "Seed labels alone do not establish independent initialization",
            "Propagation depth is not the number of distinct anatomical layers",
            "Persistence and technical restore are not functional memory evidence",
        ],
    }


def main() -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=here / "berichtsdaten.json")
    parser.add_argument("--output", type=Path, default=here / "auswertung.json")
    args = parser.parse_args()
    try:
        content = args.input.read_bytes()
        source = json.loads(content.decode("utf-8"))
        result = analyse(source, hashlib.sha256(content).hexdigest())
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                               encoding="utf-8")
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
        parser.exit(2, f"Input or calculation error: {exc}\n")
    print(f"Descriptive report calculation written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
