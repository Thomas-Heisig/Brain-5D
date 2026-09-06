from __future__ import annotations

import gzip
import json
from pathlib import Path

from src.research.data_v2 import (
    AI_PACKET_MAX_BYTES,
    build_detail_packet,
    prepare_research_data_v2,
)
from src.research.experiment_summary import build_descriptive_statistics


def _large_runs() -> list[dict[str, object]]:
    comparisons = [
        {"tick": tick, "horizon": "fast", "discrepancy": float(tick % 7) / 10.0}
        for tick in range(20_000)
    ]
    return [
        {
            "experiment_id": "EXP-TEST-DATA-V2",
            "condition": "temporal:fast_medium_slow",
            "seed": 42,
            "metrics": {
                "ticks_executed": 20_000,
                "total_spikes": 3,
                "comparisons": comparisons,
            },
            "state_digest_before": "before",
            "state_digest_after": "after",
            "runtime_error": None,
        },
        {
            "experiment_id": "EXP-TEST-DATA-V2",
            "condition": "ping:recurrence_on",
            "seed": 43,
            "metrics": {
                "ticks_executed": 256,
                "total_spikes": 33,
                "spike_sequence": [
                    {"tick": tick, "neuron_id": tick % 3} for tick in range(2_000)
                ],
            },
            "state_digest_before": "before-2",
            "state_digest_after": "after-2",
            "runtime_error": None,
        },
    ]


def test_data_v2_archives_full_runs_and_bounds_ai_input(tmp_path: Path) -> None:
    experiment = tmp_path / "EXP-TEST-DATA-V2"
    runs = _large_runs()
    statistics = build_descriptive_statistics(runs)

    artifacts = prepare_research_data_v2(experiment, runs, statistics)
    artifacts.runs_path.write_text(
        json.dumps(runs, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    index = json.loads(artifacts.raw_index_path.read_text(encoding="utf-8"))
    current = json.loads(artifacts.current_run_path.read_text(encoding="utf-8"))
    packet = json.loads(artifacts.ai_packet_path.read_text(encoding="utf-8"))

    assert index["run_count"] == 2
    assert current["status"] == "idle"
    assert artifacts.ai_packet_path.stat().st_size <= AI_PACKET_MAX_BYTES
    assert (
        packet["ai_input_policy"]
        == "compact_only_raw_on_explicit_deterministic_extract"
    )
    assert isinstance(runs[0]["metrics"]["comparisons"], dict)  # type: ignore[index]
    assert runs[0]["metrics"]["comparisons"]["item_count"] == 20_000  # type: ignore[index]

    first_raw = experiment / index["runs"][0]["path"]
    with gzip.open(first_raw, "rt", encoding="utf-8") as handle:
        raw = json.load(handle)
    assert len(raw["metrics"]["comparisons"]) == 20_000


def test_detail_packet_reads_only_indexed_condition(tmp_path: Path) -> None:
    experiment = tmp_path / "EXP-TEST-DATA-V2"
    runs = _large_runs()
    statistics = build_descriptive_statistics(runs)
    prepare_research_data_v2(experiment, runs, statistics)

    detail = build_detail_packet(
        experiment,
        condition="ping:recurrence_on",
        metrics=("spike_sequence", "total_spikes"),
        preview_items=4,
    )

    assert detail["run_count"] == 1
    assert detail["condition"] == "ping:recurrence_on"
    metrics = detail["runs"][0]["metrics"]
    assert metrics["total_spikes"] == 33
    assert metrics["spike_sequence"]["item_count"] == 2_000
    assert len(metrics["spike_sequence"]["head"]) == 4
