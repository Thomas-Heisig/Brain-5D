"""End-to-end publication for the registered pair-timing STDP experiment."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

from .experiment_recorder import ExperimentRecorder
from .registry import REPO_ROOT, ResearchRegistry
from .stdp_pair_timing import PROTOCOL_ID, run_pair_timing_protocol

EXPERIMENT_ID = "EXP-STDP-0001"
QUESTION_ID = "RQ-STDP-001"
HYPOTHESIS_ID = "H-STDP-001-A"


def execute_stdp_pair_experiment(
    experiment_id: str = EXPERIMENT_ID,
    research_root: Path | None = None,
) -> dict[str, str]:
    """Publish the pre-registered isolated STDP timing experiment once."""
    research_root = research_root or REPO_ROOT / "research"
    experiment_dir = research_root / "experiments" / experiment_id
    if (experiment_dir / "manifest.json").exists():
        raise FileExistsError(f"{experiment_id} has already been published.")
    experiment_dir.mkdir(parents=True, exist_ok=False)

    started = perf_counter()
    data = run_pair_timing_protocol()
    duration = perf_counter() - started
    protocol_path = experiment_dir / "protocol.json"
    protocol_path.write_text(
        json.dumps(data["conditions"], indent=2) + "\n", encoding="utf-8"
    )
    data_path = _write_data(research_root, data, experiment_id)

    recorder = ExperimentRecorder(experiment_id, output_dir=experiment_dir)
    recorder.record_software_version("brain5d_version", _brain5d_version())
    recorder.record_config(
        _artifact_reference(protocol_path, research_root), _sha256(protocol_path)
    ).record_research_links([QUESTION_ID], [HYPOTHESIS_ID]).record_simulation_params(
        seed=data["seed"],
        ticks=len(data["measurements"]),
        learning=True,
        input_pattern="isolated pre/post spike pair timing sweep",
        protocol=PROTOCOL_ID,
    ).record_artifact(
        "data", _artifact_reference(data_path, research_root)
    ).record_artifact(
        "protocol", _artifact_reference(protocol_path, research_root)
    ).record_results(
        metrics_summary=data["summary"],
        hypothesis_supported=data["summary"]["hypothesis_supported"],
    ).record_runtime(
        duration
    ).mark_completed()
    recorder.manifest["data_ids"] = [data_path.stem]
    recorder.save()

    report_path = experiment_dir / "report.md"
    report_path.write_text(
        _render_report(data, duration, experiment_id), encoding="utf-8"
    )
    _rebuild_reports(research_root)
    return {
        "experiment_id": experiment_id,
        "data_id": data_path.stem,
        "evidence_id": "",
        "report": _artifact_reference(report_path, research_root),
    }


def _artifact_reference(path: Path, research_root: Path) -> str:
    """Return a stable repository-relative reference for local or test roots."""
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.relative_to(research_root).as_posix()


def _write_data(research_root: Path, data: dict[str, Any], experiment_id: str) -> Path:
    directory = research_root / "generated" / "data"
    directory.mkdir(parents=True, exist_ok=True)
    year = datetime.now(timezone.utc).year
    index = 1
    while (directory / f"DATA-{year}-{index:02d}.json").exists():
        index += 1
    path = directory / f"DATA-{year}-{index:02d}.json"
    record = {
        "data_id": path.stem,
        "experiment_id": experiment_id,
        "generated": datetime.now(timezone.utc).isoformat(),
        **data,
    }
    path.write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return path


def _rebuild_reports(research_root: Path) -> None:
    from .report_builder import ReportBuilder

    registry = ResearchRegistry(research_root / "registry").load_all()
    builder = ReportBuilder(registry)
    generated = research_root / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    (generated / "RESEARCH_CATALOG.md").write_text(
        builder.build_research_catalog(), encoding="utf-8"
    )
    (generated / "EVIDENCE_MATRIX.md").write_text(
        builder.build_evidence_matrix(), encoding="utf-8"
    )
    (generated / "OPEN_QUESTIONS.md").write_text(
        builder.build_open_questions(), encoding="utf-8"
    )
    (generated / "CLAIM_REGISTER.md").write_text(
        builder.build_claim_register(), encoding="utf-8"
    )


def _brain5d_version() -> str:
    from src.version import BRAIN5D_VERSION_DISPLAY

    return BRAIN5D_VERSION_DISPLAY


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _render_report(
    data: dict[str, Any], duration: float, experiment_id: str = EXPERIMENT_ID
) -> str:
    summary = data["summary"]
    return "\n".join(
        [
            f"# {experiment_id}: Pair-Timing STDP",
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
            "Zehn identische Wiederholungspruefungen pro Delta t; feste STDP-Parameter.",
            "Es gibt keine unabhaengigen stochastischen Runs und keinen statistischen Test.",
            "",
            "## Ergebnis",
            f"LTP-Mittelwert: {summary['mean_ltp']:.8f}; LTD-Mittelwert: {summary['mean_ltd']:.8f}; Delta t = 0: {summary['zero_delta_weight']:.8f}.",
            f"Bedingungen: {summary['conditions']}; wiederholte Auswertungen: {summary['repeated_evaluations']}; unabhaengige Runs: 0; Dauer: {duration:.6f} s.",
            "",
            "## Wissenschaftliche Einordnung",
            "Pilot- und Methodenvalidierung. Der Lauf bestaetigt die deterministische Implementierung der isolierten Pair-STDP-Regel: negatives Delta t fuehrt zu LTD, positives Delta t zu LTP und Delta t = 0 zu keiner Aenderung.",
            "Er erzeugt absichtlich keine wissenschaftliche EVID und zaehlt nicht fuer Claim oder Forschungsfrage, weil ein produktiver Brain-5D-Lernpfad hier nicht gemessen wird.",
            "",
            "## Reproduzierbarkeit und Grenzen",
            "Der Protokoll-Snapshot, Startgewicht und STDP-Parameter sind im Manifest und in `protocol.json` hinterlegt. Der angegebene Seed ist fuer dieses deterministische Laborprotokoll nicht Teil des Messpfads.",
            "Fuer evidenzfaehige Folgerungen sind ein sauberer Source-Freeze sowie unabhaengige Runs ueber NeuralNetwork, LearningEngine und reale Network-Synapsen erforderlich.",
            "",
        ]
    )
