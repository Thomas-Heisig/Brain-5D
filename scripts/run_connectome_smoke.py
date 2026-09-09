"""Run six real registered screens through the existing workflow in a NEW output root.

No AI backend, network, production devices or evidence promotion. Full original
DATA sidecars, workflow manifests and bounded AI packets are produced normally.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.dashboard.experiment_workflow import ExperimentWorkflowService  # noqa: E402
from src.research.connectome_embodiment import RUNNERS  # noqa: E402
from src.research.connectome_governance import connectome_catalog  # noqa: E402


def run_smoke(destination: Path, ticks: int = 120) -> dict[str, Any]:
    destination = destination.resolve()
    if destination.exists():
        raise ValueError(
            "Use a new smoke-output directory; previous runs are never overwritten"
        )
    destination.mkdir(parents=True)
    research = destination / "research"
    for directory in (
        "registry",
        "protocols",
        "preregistrations",
        "literature",
        "ethics",
    ):
        shutil.copytree(ROOT / "research" / directory, research / directory)
    (destination / "configs").mkdir()
    shutil.copy2(
        ROOT / "configs/learning_experiment.yaml",
        destination / "configs/learning_experiment.yaml",
    )
    service = ExperimentWorkflowService(research)
    results: list[dict[str, Any]] = []
    for number, record in enumerate(connectome_catalog(research), start=1):
        if record["id"] not in RUNNERS:
            continue
        exp = f"EXP-CONN-SMOKE-{number:03d}"
        service.run_science(
            {
                "experiment_id": exp,
                "question_id": record["research_question"],
                "hypothesis_id": record["hypothesis"],
                "protocol": record["id"],
                "title": "Development smoke: " + record["id"],
                "conditions": ", ".join(record["conditions"]),
                "ticks": ticks,
                "seeds": "101,102,103",
                "notes": "AI-assisted engineering validation. SYNTHETIC data; no confirmation, learning or biological replication claim.",
            }
        )
        folder = research / "experiments" / exp
        runs = json.loads((folder / "DATA/runs.json").read_text(encoding="utf-8"))
        manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
        if len(runs) != 3 * len(record["conditions"]) or any(
            row.get("runtime_error") for row in runs
        ):
            raise ValueError("Incomplete or failed native run: " + exp)
        if not (folder / "DATA/gateway_state.json").is_file():
            raise ValueError("Body/gateway sidecar missing")
        if (
            manifest.get("execution_contract", {}).get("source_runtime_consistency")
            != "MATCH"
        ):
            raise ValueError("Loaded runner differs from its recorded source")
        results.append(
            {
                "experiment_id": exp,
                "protocol": record["id"],
                "runs": len(runs),
                "ticks_per_run": ticks,
                "observed_spikes": sum(row["metrics"]["total_spikes"] for row in runs),
                "observed_synaptic_events": sum(
                    row["metrics"]["synaptic_events_delivered"] for row in runs
                ),
                "all_runtime_errors": None,
                "evidence_promoted": False,
            }
        )
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    report = {
        "stage": "DEVELOPMENT_SMOKE",
        "source_commit": commit,
        "source_tree_note": "Commit plus checked-out working tree; CI must identify the clean tested commit.",
        "data_kind": "SYNTHETIC",
        "scientific_confirmation": False,
        "protocol_count": len(results),
        "run_count": sum(r["runs"] for r in results),
        "results": results,
    }
    (destination / "smoke-summary.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ticks", type=int, default=120)
    arguments = parser.parse_args()
    print(json.dumps(run_smoke(arguments.output, arguments.ticks), indent=2))
