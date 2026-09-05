"""Research DATA v2: compact AI packets plus immutable compressed raw runs.

The raw experiment observations remain available for audit, but the default
Research Assistant path is intentionally bounded.  `DATA/runs.json` is a compact
projection for the current experiment, while each complete run is archived as an
immutable gzip member under `DATA/raw/` and indexed by SHA-256.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence, cast

AI_PACKET_MAX_BYTES = 1_000_000
RUN_SUMMARY_MAX_BYTES = 5_000_000
DETAIL_PACKET_MAX_BYTES = 1_000_000
SEQUENCE_PREVIEW_ITEMS = 16


@dataclass(frozen=True, slots=True)
class ResearchDataArtifacts:
    runs_path: Path
    raw_index_path: Path
    current_run_path: Path
    ai_packet_path: Path
    ai_packet_digest_path: Path
    raw_paths: tuple[Path, ...]


def _json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=list,
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_name(value: object) -> str:
    name = re.sub(r"[^A-Za-z0-9_.-]+", "-", str(value)).strip("-")
    return name or "run"


def compact_for_storage(
    value: Any, *, preview_items: int = SEQUENCE_PREVIEW_ITEMS
) -> Any:
    """Return a deterministic bounded projection without inventing statistics."""
    if isinstance(value, dict):
        return {
            str(key): compact_for_storage(item, preview_items=preview_items)
            for key, item in value.items()
        }
    if isinstance(value, list):
        if len(value) <= preview_items * 2:
            return [
                compact_for_storage(item, preview_items=preview_items) for item in value
            ]
        return {
            "_projection": "bounded_sequence",
            "item_count": len(value),
            "head": [
                compact_for_storage(item, preview_items=preview_items)
                for item in value[:preview_items]
            ],
            "tail": [
                compact_for_storage(item, preview_items=preview_items)
                for item in value[-preview_items:]
            ],
        }
    if isinstance(value, tuple):
        return compact_for_storage(list(value), preview_items=preview_items)
    return value


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True, default=list)
        + "\n",
        encoding="utf-8",
    )


def _write_gzip_json(path: Path, value: object) -> tuple[str, int, int]:
    payload = _json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wb", compresslevel=9) as handle:
        handle.write(payload)
    return _sha256_file(path), path.stat().st_size, len(payload)


def _statistics_projection(statistics: Mapping[str, Any]) -> dict[str, Any]:
    allowed = (
        "schema_version",
        "run_count",
        "conditions",
        "two_condition_effects",
        "inter_spike_intervals",
        "temporal_horizons",
        "formulas",
    )
    return {key: statistics[key] for key in allowed if key in statistics}


def prepare_research_data_v2(
    experiment_dir: Path,
    runs: list[dict[str, Any]],
    statistics: Mapping[str, Any],
) -> ResearchDataArtifacts:
    """Archive full runs and replace the mutable in-memory list with compact summaries.

    The function mutates ``runs`` in-place deliberately.  Callers compute deterministic
    statistics before invoking it; subsequent legacy writers therefore persist only the
    bounded projections instead of hundreds of megabytes of traces.
    """
    data_dir = experiment_dir / "DATA"
    raw_dir = data_dir / "raw"
    analysis_dir = experiment_dir / "analysis"
    runs_path = data_dir / "runs.json"
    index_path = data_dir / "runs_index.json"
    current_path = data_dir / "current_run.json"
    ai_packet_path = analysis_dir / "ai_packet.json"
    ai_digest_path = analysis_dir / "ai_packet_digest.json"

    raw_entries: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    raw_paths: list[Path] = []

    for run_index, run in enumerate(tuple(runs)):
        condition = _safe_name(run.get("condition", "unknown"))
        seed = run.get("seed", "unknown")
        raw_path = raw_dir / f"run-{run_index:04d}-{condition}-seed-{seed}.json.gz"
        _write_json(
            current_path,
            {
                "status": "archiving",
                "run_index": run_index,
                "condition": run.get("condition"),
                "seed": seed,
            },
        )
        digest, size_bytes, uncompressed_bytes = _write_gzip_json(raw_path, run)
        raw_paths.append(raw_path)
        raw_ref = {
            "path": raw_path.relative_to(experiment_dir).as_posix(),
            "format": "json.gz",
            "sha256": digest,
            "size_bytes": size_bytes,
            "uncompressed_bytes": uncompressed_bytes,
        }
        summary = cast(dict[str, Any], compact_for_storage(run))
        summary["_raw_artifact"] = raw_ref
        summaries.append(summary)
        raw_entries.append(
            {
                "run_index": run_index,
                "condition": run.get("condition"),
                "seed": seed,
                **raw_ref,
            }
        )
        _write_json(
            current_path,
            {"status": "idle", "last_archived_run": run_index, "raw_artifact": raw_ref},
        )

    index = {
        "schema_version": "2.0",
        "storage_policy": "immutable_raw_runs_plus_compact_current_experiment",
        "run_count": len(raw_entries),
        "runs": raw_entries,
    }
    _write_json(index_path, index)

    compact_bytes = json.dumps(
        summaries, indent=2, ensure_ascii=False, sort_keys=True, default=list
    ).encode("utf-8")
    if len(compact_bytes) > RUN_SUMMARY_MAX_BYTES:
        raise ValueError(
            f"Compact DATA/runs.json would exceed {RUN_SUMMARY_MAX_BYTES} bytes; "
            "increase deterministic aggregation instead of sending it to AI."
        )
    runs[:] = summaries

    ai_packet = {
        "schema_version": "2.0",
        "generated_by": "deterministic_research_data_v2",
        "ai_input_policy": "compact_only_raw_on_explicit_deterministic_extract",
        "run_count": len(summaries),
        "statistics": _statistics_projection(statistics),
        "run_preview": compact_for_storage(summaries, preview_items=8),
        "raw_index": {
            "path": index_path.relative_to(experiment_dir).as_posix(),
            "sha256": _sha256_file(index_path),
            "run_count": len(raw_entries),
        },
        "limits": {
            "ai_packet_max_bytes": AI_PACKET_MAX_BYTES,
            "run_summary_max_bytes": RUN_SUMMARY_MAX_BYTES,
            "sequence_preview_items": SEQUENCE_PREVIEW_ITEMS,
        },
    }
    packet_bytes = json.dumps(
        ai_packet, indent=2, ensure_ascii=False, sort_keys=True, default=list
    ).encode("utf-8")
    if len(packet_bytes) > AI_PACKET_MAX_BYTES:
        raise ValueError(
            f"AI packet exceeds hard limit of {AI_PACKET_MAX_BYTES} bytes; "
            "the deterministic projection must be tightened."
        )
    ai_packet_path.parent.mkdir(parents=True, exist_ok=True)
    ai_packet_path.write_bytes(packet_bytes + b"\n")
    _write_json(
        ai_digest_path,
        {
            "schema_version": "1.0",
            "path": ai_packet_path.relative_to(experiment_dir).as_posix(),
            "sha256": _sha256_file(ai_packet_path),
            "size_bytes": ai_packet_path.stat().st_size,
            "raw_index_sha256": _sha256_file(index_path),
        },
    )
    return ResearchDataArtifacts(
        runs_path=runs_path,
        raw_index_path=index_path,
        current_run_path=current_path,
        ai_packet_path=ai_packet_path,
        ai_packet_digest_path=ai_digest_path,
        raw_paths=tuple(raw_paths),
    )


def _select_metrics(
    run: dict[str, Any], metrics: Sequence[str] | None
) -> dict[str, Any]:
    if not metrics:
        return run
    selected = dict(run)
    raw_metrics = run.get("metrics")
    if isinstance(raw_metrics, dict):
        selected["metrics"] = {
            name: raw_metrics[name] for name in metrics if name in raw_metrics
        }
    return selected


def build_detail_packet(
    experiment_dir: Path,
    *,
    condition: str,
    metrics: Sequence[str] | None = None,
    preview_items: int = 64,
) -> dict[str, Any]:
    """Build a bounded condition-specific packet by reading only indexed raw runs."""
    index_path = experiment_dir / "DATA" / "runs_index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    entries = index.get("runs", []) if isinstance(index, dict) else []
    detail_runs: list[dict[str, Any]] = []
    source_refs: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict) or str(entry.get("condition")) != condition:
            continue
        path = experiment_dir / str(entry["path"])
        if _sha256_file(path) != str(entry.get("sha256")):
            raise ValueError(f"Raw run digest mismatch: {path}")
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            raw = json.load(handle)
        if not isinstance(raw, dict):
            continue
        detail_runs.append(
            cast(
                dict[str, Any],
                compact_for_storage(
                    _select_metrics(raw, metrics), preview_items=preview_items
                ),
            )
        )
        source_refs.append(
            {
                "path": entry["path"],
                "sha256": entry["sha256"],
                "seed": entry.get("seed"),
            }
        )
    packet = {
        "schema_version": "1.0",
        "generated_by": "deterministic_detail_extractor",
        "condition": condition,
        "metrics": list(metrics or ()),
        "run_count": len(detail_runs),
        "runs": detail_runs,
        "sources": source_refs,
    }
    encoded = json.dumps(packet, ensure_ascii=False, sort_keys=True).encode("utf-8")
    if len(encoded) > DETAIL_PACKET_MAX_BYTES:
        raise ValueError(
            f"Detail packet exceeds {DETAIL_PACKET_MAX_BYTES} bytes; request fewer metrics or a smaller preview."
        )
    return packet


def write_detail_packet(
    experiment_dir: Path,
    *,
    condition: str,
    metrics: Sequence[str] | None = None,
    preview_items: int = 64,
) -> Path:
    packet = build_detail_packet(
        experiment_dir,
        condition=condition,
        metrics=metrics,
        preview_items=preview_items,
    )
    path = experiment_dir / "analysis" / "detail" / f"{_safe_name(condition)}.json"
    _write_json(path, packet)
    return path
