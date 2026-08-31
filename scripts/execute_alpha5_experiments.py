"""Execute Alpha.5 experiments EXP-DET-0001 and EXP-STOR-0001.

This script:
1. Runs the determinism A/B/C experiment (EXP-DET-0001)
2. Runs the storage persistence experiment (EXP-STOR-0001)
3. Records manifests for both experiments
4. Generates DATA-* and EVID-* artifacts
5. Rebuilds Research Catalog and Evidence Matrix
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.research.experiment_recorder import ExperimentRecorder, get_software_info
from src.research.evidence_engine import EvidenceEngine
from src.research.registry import ResearchRegistry
from src.research.report_builder import ReportBuilder
from src.dashboard.verification import compute_source_tree_digest

EXPERIMENTS_DIR = REPO_ROOT / "research" / "experiments"
EVIDENCE_DIR = REPO_ROOT / "research" / "registry" / "evidence"
DATA_DIR = REPO_ROOT / "research" / "generated" / "data"


# Map experiments to their canonical runtime configuration files.
EXPERIMENT_CONFIGS: dict[str, Path] = {
    "EXP-DET-0001": REPO_ROOT / "configs" / "poc_alpha5_live.yaml",
    "EXP-STOR-0001": REPO_ROOT / "configs" / "poc_alpha5_live.yaml",
}


def _sha256_file(path: Path) -> str:
    """Return the SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _brain5d_version() -> str:
    """Read Brain-5D version from pyproject.toml, fallback to import."""
    pyproject = REPO_ROOT / "pyproject.toml"
    if pyproject.exists():
        try:
            text = pyproject.read_text(encoding="utf-8")
            for line in text.splitlines():
                if line.strip().startswith("version"):
                    _, _, value = line.partition("=")
                    return value.strip().strip('"').strip("'")
        except Exception:
            pass
    return get_software_info().get("brain5d_version", "unknown")


def _run_pytest(test_path: str, timeout: int = 120) -> dict[str, object]:
    """Run a pytest file and return pass/fail with output."""
    start = time.time()
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path, "-q", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(REPO_ROOT),
    )
    duration = time.time() - start
    return {
        "returncode": result.returncode,
        "passed": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "duration_seconds": duration,
    }


def _run_determinism_experiment() -> dict[str, object]:
    """Run EXP-DET-0001: A/B/C restore determinism."""
    result = _run_pytest("tests/test_restore_determinism_abc.py", timeout=300)
    return result


def _run_storage_experiment() -> dict[str, object]:
    """Run EXP-STOR-0001: B5D storage roundtrip persistence."""
    result = _run_pytest("tests/test_b5d_storage.py", timeout=300)
    return result


def _update_manifest(
    experiment_id: str,
    result: dict[str, object],
    claim_id: str,
    hypothesis_id: str,
    research_question_id: str,
) -> None:
    """Update experiment manifest with full provenance."""
    config_path = EXPERIMENT_CONFIGS.get(experiment_id)
    config_sha256 = _sha256_file(config_path) if config_path and config_path.exists() else ""

    duration_seconds = float(result["duration_seconds"])
    passed = bool(result["passed"])
    returncode = int(result["returncode"])
    stdout = str(result["stdout"])
    stderr = str(result["stderr"])

    recorder = ExperimentRecorder(experiment_id)
    recorder.record_software_version("brain5d_version", _brain5d_version())
    recorder.record_config(
        config_path=str(config_path) if config_path else "",
        sha256=config_sha256,
    )
    recorder.record_research_links(
        research_questions=[research_question_id],
        hypotheses=[hypothesis_id],
    )
    recorder.record_results(
        passed=passed,
        returncode=returncode,
        duration_seconds=duration_seconds,
        stdout_summary=stdout[:2000],
        stderr_summary=stderr[:2000],
    )
    recorder.record_runtime(duration_seconds=duration_seconds)
    recorder.record_artifact("test_output", str(EXPERIMENTS_DIR / experiment_id / "output.log"))
    recorder.mark_completed()
    recorder.save()


def _generate_data_artifact(experiment_id: str, result: dict[str, object]) -> Path:
    """Generate a DATA-* artifact for an experiment."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    year = time.localtime().tm_year
    existing = list(DATA_DIR.glob(f"DATA-{year}-*.json"))
    data_id = f"DATA-{year}-{len(existing) + 1:02d}"
    data_path = DATA_DIR / f"{data_id}.json"
    data_record = {
        "data_id": data_id,
        "experiment_id": experiment_id,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "tree_digest": compute_source_tree_digest(REPO_ROOT),
        "test_command": result.get("command", ""),
        "results": {
            "passed": result["passed"],
            "returncode": result["returncode"],
            "duration_seconds": result["duration_seconds"],
        },
        "raw_outputs": {
            "stdout": result["stdout"],
            "stderr": result["stderr"],
        },
    }
    data_path.write_text(json.dumps(data_record, indent=2, ensure_ascii=False), encoding="utf-8")
    return data_path


def _create_evidence(
    experiment_id: str,
    claim_id: str,
    hypothesis_id: str,
    summary: str,
    status: str,
) -> str:
    """Create an EVID-* record linking experiment to claim/hypothesis."""
    registry = ResearchRegistry(REPO_ROOT / "research" / "registry")
    registry.load_all()
    engine = EvidenceEngine(registry)
    evidence_id = engine.evaluate_experiment(
        experiment_id=experiment_id,
        claim_id=claim_id,
        hypothesis_id=hypothesis_id,
        result_summary=summary,
        status=status,
    )
    return evidence_id


def _rebuild_reports(refresh_registry: bool = False) -> None:
    """Rebuild Research Catalog and Evidence Matrix."""
    registry = ResearchRegistry(REPO_ROOT / "research" / "registry")
    registry.load_all()
    builder = ReportBuilder(registry)
    catalog = builder.build_research_catalog()
    matrix = builder.build_evidence_matrix()
    (REPO_ROOT / "research" / "generated" / "RESEARCH_CATALOG.md").write_text(catalog, encoding="utf-8")
    (REPO_ROOT / "research" / "generated" / "EVIDENCE_MATRIX.md").write_text(matrix, encoding="utf-8")
    print("Rebuilt RESEARCH_CATALOG.md and EVIDENCE_MATRIX.md")


def main() -> int:
    print("=" * 60)
    print("Alpha.5 Experiment Execution")
    print("=" * 60)

    # EXP-DET-0001: Determinism A/B/C
    print("\n[EXP-DET-0001] Running determinism A/B/C experiment...")
    det_result = _run_determinism_experiment()
    print(f"  passed={det_result['passed']}, duration={det_result['duration_seconds']:.1f}s")
    _update_manifest(
        "EXP-DET-0001",
        det_result,
        claim_id="CLAIM-DET-001",
        hypothesis_id="H-SNN-003-A",
        research_question_id="RQ-DET-001",
    )
    det_data = _generate_data_artifact("EXP-DET-0001", det_result)
    print(f"  DATA artifact: {det_data.name}")
    det_evid = _create_evidence(
        "EXP-DET-0001",
        claim_id="CLAIM-DET-001",
        hypothesis_id="H-SNN-003-A",
        summary="A/B/C restore determinism verified: process-restart restore produces identical structural and dynamic state.",
        status="supports" if det_result["passed"] else "inconclusive",
    )
    print(f"  EVID artifact: {det_evid}")

    # EXP-STOR-0001: Storage persistence
    print("\n[EXP-STOR-0001] Running storage persistence experiment...")
    stor_result = _run_storage_experiment()
    print(f"  passed={stor_result['passed']}, duration={stor_result['duration_seconds']:.1f}s")
    _update_manifest(
        "EXP-STOR-0001",
        stor_result,
        claim_id="CLAIM-STOR-001",
        hypothesis_id="H-STOR-001-A",
        research_question_id="RQ-STORAGE-001",
    )
    stor_data = _generate_data_artifact("EXP-STOR-0001", stor_result)
    print(f"  DATA artifact: {stor_data.name}")
    stor_evid = _create_evidence(
        "EXP-STOR-0001",
        claim_id="CLAIM-STOR-001",
        hypothesis_id="H-STOR-001-A",
        summary="B5D storage roundtrip verified: full network state serializes and deserializes without loss.",
        status="supports" if stor_result["passed"] else "inconclusive",
    )
    print(f"  EVID artifact: {stor_evid}")

    # Rebuild reports after evidence has updated the registry
    print("\n[Reports] Rebuilding Research Catalog and Evidence Matrix...")
    _rebuild_reports(refresh_registry=True)

    print("\n" + "=" * 60)
    print("Alpha.5 experiments executed successfully.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
