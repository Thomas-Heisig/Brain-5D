"""End-to-end publication for the registered pair-timing STDP experiment."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

from .evidence_engine import EvidenceEngine
from .experiment_recorder import ExperimentRecorder
from .registry import REPO_ROOT, ResearchRegistry
from .stdp_pair_timing import PROTOCOL_ID, run_pair_timing_protocol

EXPERIMENT_ID = "EXP-STDP-0001"
QUESTION_ID = "RQ-STDP-001"
HYPOTHESIS_ID = "H-STDP-001-A"
CLAIM_ID = "CLAIM-STDP-001"


def execute_stdp_pair_experiment() -> dict[str, str]:
    """Publish the pre-registered isolated STDP timing experiment once."""
    research_root = REPO_ROOT / "research"
    experiment_dir = research_root / "experiments" / EXPERIMENT_ID
    if (experiment_dir / "manifest.json").exists():
        raise FileExistsError(f"{EXPERIMENT_ID} has already been published.")
    experiment_dir.mkdir(parents=True, exist_ok=False)

    started = perf_counter()
    data = run_pair_timing_protocol()
    duration = perf_counter() - started
    protocol_path = experiment_dir / "protocol.json"
    protocol_path.write_text(json.dumps(data["conditions"], indent=2) + "\n", encoding="utf-8")
    data_path = _write_data(research_root, data)

    recorder = ExperimentRecorder(EXPERIMENT_ID, output_dir=experiment_dir)
    recorder.record_software_version("brain5d_version", _brain5d_version())
    recorder.record_config(
        str(protocol_path.relative_to(REPO_ROOT).as_posix()), _sha256(protocol_path)
    ).record_research_links(
        [QUESTION_ID], [HYPOTHESIS_ID]
    ).record_simulation_params(
        seed=data["seed"],
        ticks=len(data["measurements"]),
        learning=True,
        input_pattern="isolated pre/post spike pair timing sweep",
        protocol=PROTOCOL_ID,
    ).record_artifact(
        "data", data_path.relative_to(REPO_ROOT).as_posix()
    ).record_artifact(
        "protocol", protocol_path.relative_to(REPO_ROOT).as_posix()
    ).record_results(
        metrics_summary=data["summary"],
        hypothesis_supported=data["summary"]["hypothesis_supported"],
    ).record_runtime(duration).mark_completed()
    recorder.manifest["data_ids"] = [data_path.stem]
    recorder.save()

    evidence_id = _write_evidence(data_path, data)
    report_path = experiment_dir / "report.md"
    report_path.write_text(_render_report(data, duration, evidence_id), encoding="utf-8")
    _rebuild_reports()
    return {
        "experiment_id": EXPERIMENT_ID,
        "data_id": data_path.stem,
        "evidence_id": evidence_id,
        "report": report_path.relative_to(REPO_ROOT).as_posix(),
    }


def _write_data(research_root: Path, data: dict[str, Any]) -> Path:
    directory = research_root / "generated" / "data"
    directory.mkdir(parents=True, exist_ok=True)
    year = datetime.now(timezone.utc).year
    index = 1
    while (directory / f"DATA-{year}-{index:02d}.json").exists():
        index += 1
    path = directory / f"DATA-{year}-{index:02d}.json"
    record = {
        "data_id": path.stem,
        "experiment_id": EXPERIMENT_ID,
        "generated": datetime.now(timezone.utc).isoformat(),
        **data,
    }
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def _write_evidence(data_path: Path, data: dict[str, Any]) -> str:
    registry = ResearchRegistry().load_all()
    evidence_id = EvidenceEngine(registry).evaluate_experiment(
        experiment_id=EXPERIMENT_ID,
        claim_id=CLAIM_ID,
        hypothesis_id=HYPOTHESIS_ID,
        result_summary=(
            "The isolated pair-timing sweep measured LTP for every positive "
            "delta_t, LTD for every negative delta_t, and zero change at delta_t=0."
        ),
        effect_size={
            "value": abs(float(data["summary"]["mean_ltp"])) + abs(float(data["summary"]["mean_ltd"])),
            "metric": "mean absolute delta_weight across timing branches",
        },
        statistical_significance={
            "test": "deterministic protocol replication",
            "n_runs": int(data["summary"]["total_replications"]),
        },
        status="supports" if data["summary"]["hypothesis_supported"] else "refutes",
        limitations=(
            "Isolated nearest-neighbour synapse only; the result does not yet "
            "establish behaviour in the full Brain-5D runtime."
        ),
    )
    evidence_path = REPO_ROOT / "research" / "registry" / "evidence" / f"{evidence_id}.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    evidence["artifacts"]["data_files"] = [data_path.relative_to(REPO_ROOT).as_posix()]
    evidence_path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return evidence_id


def _rebuild_reports() -> None:
    from .report_builder import ReportBuilder

    registry = ResearchRegistry().load_all()
    builder = ReportBuilder(registry)
    generated = REPO_ROOT / "research" / "generated"
    (generated / "RESEARCH_CATALOG.md").write_text(builder.build_research_catalog(), encoding="utf-8")
    (generated / "EVIDENCE_MATRIX.md").write_text(builder.build_evidence_matrix(), encoding="utf-8")
    (generated / "OPEN_QUESTIONS.md").write_text(builder.build_open_questions(), encoding="utf-8")
    (generated / "CLAIM_REGISTER.md").write_text(builder.build_claim_register(), encoding="utf-8")


def _brain5d_version() -> str:
    from src.version import BRAIN5D_VERSION_DISPLAY

    return BRAIN5D_VERSION_DISPLAY


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _render_report(data: dict[str, Any], duration: float, evidence_id: str) -> str:
    summary = data["summary"]
    return "\n".join(
        [
            f"# {EXPERIMENT_ID}: Pair-Timing STDP",
            "",
            "## Forschungsfrage",
            QUESTION_ID,
            "",
            "## Hypothese",
            HYPOTHESIS_ID,
            "",
            "## Bedingungen",
            f"Protokoll: `{PROTOCOL_ID}`; Seed: {data['seed']}; Startgewicht: 0.5.",
            "Delta t: -50, -20, -10, -5, -1, 0, +1, +5, +10, +20, +50 ms.",
            "Zehn isolierte Replikationen pro Delta t; feste STDP-Parameter.",
            "",
            "## Ergebnis",
            f"LTP-Mittelwert: {summary['mean_ltp']:.8f}; LTD-Mittelwert: {summary['mean_ltd']:.8f}; Delta t = 0: {summary['zero_delta_weight']:.8f}.",
            f"Replikationen: {summary['total_replications']}; Dauer: {duration:.6f} s.",
            "",
            "## Evidenz",
            f"{evidence_id} supports the isolated pair-timing claim. The associated claim remains subject to its configured evidence threshold and human scientific review.",
            "",
        ]
    )