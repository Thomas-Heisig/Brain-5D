"""Descriptive diagnostics only; no automated scientific/evidence promotion."""
from __future__ import annotations

import statistics
from typing import Any

from .catalogue import ITEMS, NA, SECTIONS, SKIP


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    responses = [row["response"] for row in records]
    items: dict[str, Any] = {}
    for code, question in ITEMS.items():
        if question["kind"] != "scale":
            continue
        values = [r["answers"].get(code) for r in responses]
        numeric = [v for v in values if type(v) is int and 1 <= v <= 5]
        items[code] = {
            "n": len(numeric), "missing": sum(v is None or v == "" for v in values),
            "not_assessable": values.count(NA), "declined": values.count(SKIP),
            "frequencies": {str(i): numeric.count(i) for i in range(1, 6)},
            "mean": statistics.mean(numeric) if numeric else None,
            "median": statistics.median(numeric) if numeric else None,
            "sd_sample": statistics.stdev(numeric) if len(numeric) > 1 else None,
        }
    reliability: dict[str, Any] = {}
    for section in SECTIONS:
        if section["id"] not in ("B", "C", "D", "E"):
            continue
        ids = [q["id"] for q in section["items"]]
        rows = [[r["answers"].get(code) for code in ids] for r in responses]
        complete = [row for row in rows if all(type(v) is int and 1 <= v <= 5 for v in row)]
        result: dict[str, Any] = {"n_complete": len(complete), "alpha": None, "status": "not_reported_small_pilot", "interpretation": "Unvalidated heterogeneous items; alpha is not proof of validity."}
        if len(complete) >= 20:
            total_variance = statistics.variance(sum(row) for row in complete)
            if total_variance > 0:
                k = len(ids)
                result["alpha"] = k / (k - 1) * (1 - sum(statistics.variance(column) for column in zip(*complete)) / total_variance)
                result["status"] = "exploratory_diagnostic_only"
            else:
                result["status"] = "zero_total_variance"
        reliability[section["id"]] = result
    return {
        "classification": "PRIVATE_HUMAN_REVIEW_DESCRIPTIVES_NOT_EVIDENCE", "n": len(responses),
        "items": items, "reliability": reliability, "automatic_exclusions": 0,
        "group_tests": "Not run: preregister design, sample size, assumptions and multiplicity handling first.",
        "factor_analysis": "Not run: no automatic EFA/CFA for a small convenience sample.",
        "publication": "No automatic raw-data or aggregate publication. Disclosure review required.",
    }
