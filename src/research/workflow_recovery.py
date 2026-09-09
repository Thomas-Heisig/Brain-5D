"""Recovery helpers for failed experiment-workflow children.

Historical workflow reports remain immutable audit records. This module builds a
new batch request containing only children that previously failed, preserving the
recorded tick and seed settings. Executing a recovery never rewrites the source
workflow and never promotes results to scientific evidence automatically.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Sequence, cast


class WorkflowRecoveryError(ValueError):
    """Raised when a historical workflow cannot be converted into a retry plan."""


def _validate_workflow_id(workflow_id: str) -> str:
    value = workflow_id.strip()
    if not value.startswith("EXP-"):
        raise WorkflowRecoveryError("workflow_id must use the EXP-* convention")
    if any(part in value for part in ("/", "\\", "..")):
        raise WorkflowRecoveryError("workflow_id must not contain path components")
    return value


def load_workflow_report(research_root: Path, workflow_id: str) -> dict[str, object]:
    """Load one aggregate workflow report from ``research/workflows``."""
    safe_id = _validate_workflow_id(workflow_id)
    path = research_root / "workflows" / f"{safe_id}.json"
    if not path.is_file():
        raise WorkflowRecoveryError(f"Workflow report not found: {path}")
    try:
        raw: object = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise WorkflowRecoveryError(f"Workflow report is invalid JSON: {path}") from exc
    if not isinstance(raw, dict):
        raise WorkflowRecoveryError("Workflow report root must be an object")
    return cast(dict[str, object], raw)


def failed_protocol_results(report: Mapping[str, object]) -> list[dict[str, object]]:
    """Return failed child records in their original workflow order."""
    raw_results = report.get("results")
    if not isinstance(raw_results, list):
        raise WorkflowRecoveryError("Workflow report does not contain a results list")

    failed: list[dict[str, object]] = []
    for item in cast(list[object], raw_results):
        if not isinstance(item, dict):
            continue
        record = cast(dict[str, object], item)
        if record.get("status") != "failed":
            continue
        protocol = record.get("protocol")
        if not isinstance(protocol, str) or not protocol.strip():
            raise WorkflowRecoveryError("Failed workflow child has no protocol id")
        failed.append(record)
    return failed


def _default_retry_id(source_workflow_id: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    source_suffix = source_workflow_id.removeprefix("EXP-BATCH-")
    compact_source = "".join(ch for ch in source_suffix if ch.isalnum())[-12:]
    suffix = f"-{compact_source}" if compact_source else ""
    return f"EXP-RETRY-{stamp}{suffix}"


def build_retry_request(
    research_root: Path,
    workflow_id: str,
    *,
    batch_id: str | None = None,
    title_prefix: str = "Recovered experiment workflow",
    notes: str | None = None,
) -> dict[str, object]:
    """Build a ``run_batch`` request for failed children only.

    Per-child ``ticks`` and ``seeds`` are copied from the historical result when
    available. The original aggregate defaults are retained as fallbacks.
    """
    safe_id = _validate_workflow_id(workflow_id)
    report = load_workflow_report(research_root, safe_id)
    failed = failed_protocol_results(report)
    if not failed:
        raise WorkflowRecoveryError(f"Workflow {safe_id} contains no failed children")

    requested_ticks = report.get("requested_ticks", 1000)
    if (
        isinstance(requested_ticks, bool)
        or not isinstance(requested_ticks, int)
        or requested_ticks < 1
    ):
        requested_ticks = 1000
    default_seeds = report.get("seeds", "42-44")

    protocols: list[str] = []
    protocol_options: dict[str, object] = {}
    for record in failed:
        protocol = cast(str, record["protocol"])
        if protocol in protocols:
            raise WorkflowRecoveryError(
                f"Workflow {safe_id} contains duplicate failed protocol {protocol!r}; "
                "automatic recovery would make per-child options ambiguous"
            )
        protocols.append(protocol)

        ticks_value = record.get("ticks", requested_ticks)
        ticks = (
            ticks_value
            if isinstance(ticks_value, int)
            and not isinstance(ticks_value, bool)
            and ticks_value > 0
            else requested_ticks
        )
        seeds = record.get("seeds", default_seeds)
        protocol_options[protocol] = {"ticks": ticks, "seeds": seeds}

    retry_id = (
        _validate_workflow_id(batch_id) if batch_id else _default_retry_id(safe_id)
    )
    recovery_note = (
        notes.strip()
        if isinstance(notes, str) and notes.strip()
        else (
            f"Recovery batch for failed children of {safe_id}. The historical "
            "workflow remains unchanged; this retry is a new execution lineage."
        )
    )
    return {
        "batch_id": retry_id,
        "protocols": protocols,
        "ticks": requested_ticks,
        "seeds": default_seeds,
        "protocol_options": protocol_options,
        "title_prefix": title_prefix,
        "conditions": "Recovered registered protocol conditions",
        "notes": recovery_note,
        "recovery_of": safe_id,
    }


def execute_failed_protocol_retry(
    research_root: Path,
    workflow_id: str,
    *,
    batch_id: str | None = None,
) -> dict[str, object]:
    """Execute a recovery batch for failed operational protocols.

    Exploratory runtime children require a live runtime controller and therefore
    are deliberately rejected by this standalone path.
    """
    request = build_retry_request(research_root, workflow_id, batch_id=batch_id)
    protocols_value = request["protocols"]
    if not isinstance(protocols_value, list):
        raise WorkflowRecoveryError("Internal recovery request lost protocol list")
    protocols = cast(list[object], protocols_value)
    exploratory = [
        item
        for item in protocols
        if isinstance(item, str) and item.startswith("exploratory:")
    ]
    if exploratory:
        raise WorkflowRecoveryError(
            "Standalone recovery cannot execute exploratory runtime children: "
            + ", ".join(exploratory)
        )

    from src.dashboard.experiment_workflow import ExperimentWorkflowService

    service = ExperimentWorkflowService(research_root)
    return service.run_batch(request)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Retry only failed children from an immutable experiment workflow report."
    )
    parser.add_argument(
        "workflow_id",
        help="Historical workflow id, for example EXP-BATCH-20260906200118",
    )
    parser.add_argument(
        "--research-root",
        default="research",
        help="Research root containing workflows/ and experiments/ (default: research)",
    )
    parser.add_argument(
        "--batch-id",
        default=None,
        help="Explicit EXP-* id for the new recovery batch",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the recovery request without executing experiments",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point for ``python -m src.research.workflow_recovery``."""
    args = _parser().parse_args(list(argv) if argv is not None else None)
    research_root = Path(str(args.research_root)).resolve()
    workflow_id = str(args.workflow_id)
    batch_id = str(args.batch_id) if args.batch_id else None

    if bool(args.dry_run):
        result = build_retry_request(research_root, workflow_id, batch_id=batch_id)
    else:
        result = execute_failed_protocol_retry(
            research_root, workflow_id, batch_id=batch_id
        )
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
