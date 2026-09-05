"""Clean-process productive-learning orchestration and DATA binding."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .experiment_recorder import ExperimentRecorder

REPO_ROOT = Path(__file__).resolve().parents[2]
CONDITIONS = ("learning_on", "learning_off", "sham_replay")
CODE_FILES = (
    "src/experiments/learning_lab.py",
    "src/research/experiment_suite.py",
    "src/research/productive_learning.py",
    "src/research/productive_learning_worker.py",
)


@dataclass(frozen=True, slots=True)
class ProductiveLearningArtifact:
    """Paths and digests for one clean-process DATA publication."""

    experiment_id: str
    output_dir: Path
    data_path: Path
    manifest_path: Path
    run_count: int
    code_digest: str
    config_digest: str
    prompt_digest: str
    data_digest: str
    source_freeze_sha: str


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _json_digest(value: object) -> str:
    return _sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )


def _code_digest() -> str:
    files = [
        (relative, _sha256((REPO_ROOT / relative).read_bytes()))
        for relative in CODE_FILES
    ]
    return _json_digest(files)


def _run_worker(config_path: Path, seed: int, condition: str) -> dict[str, Any]:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.research.productive_learning_worker",
            "--config",
            str(config_path),
            "--seed",
            str(seed),
            "--condition",
            condition,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"clean productive-learning worker failed for seed={seed}, "
            f"condition={condition}: {completed.stderr.strip()}"
        )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("clean worker returned invalid JSON") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("result"), dict):
        raise RuntimeError("clean worker returned an invalid result envelope")
    return payload


def run_clean_process_repeats(
    config_path: Path,
    output_dir: Path,
    *,
    seeds: tuple[int, ...] = (42, 43, 44),
) -> ProductiveLearningArtifact:
    """Run each seed/condition in a fresh process and publish DATA + manifest."""
    if not seeds or len(set(seeds)) != len(seeds):
        raise ValueError("seeds must be non-empty and unique")
    config_path = config_path.resolve()
    if not config_path.is_file():
        raise FileNotFoundError(config_path)

    records: list[dict[str, Any]] = []
    for seed in seeds:
        for condition in CONDITIONS:
            payload = _run_worker(config_path, seed, condition)
            records.append(
                {
                    "experiment_id": "EXP-STDP-0002",
                    "condition": condition,
                    "seed": seed,
                    "clean_process": True,
                    "process_id": payload["process_id"],
                    "metrics": payload["result"],
                }
            )

    output_dir.mkdir(parents=True, exist_ok=True)
    data_dir = output_dir / "DATA"
    data_dir.mkdir(parents=True, exist_ok=True)
    data_path = data_dir / "runs.jsonl"
    with data_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    code_digest = _code_digest()
    config_digest = _sha256(config_path.read_bytes())
    prompt_digest = _sha256(b"NO_PROMPT")
    data_digest = _sha256(data_path.read_bytes())
    provenance = {
        "code": code_digest,
        "config": config_digest,
        "prompt": prompt_digest,
        "data": data_digest,
    }
    source_freeze_sha = _json_digest(provenance)

    recorder = ExperimentRecorder("EXP-STDP-0002", output_dir=output_dir)
    recorder.record_config(str(config_path), config_digest)
    recorder.record_research_links(
        research_questions=["RQ-STDP-001"], hypotheses=["H-STDP-001-A"]
    )
    recorder.record_simulation_params(
        protocol_id="PROTOCOL-STDP-0002",
        protocol_version=1,
        seeds=list(seeds),
        conditions=list(CONDITIONS),
        clean_process=True,
    )
    for partition in ("DEVELOPMENT", "VALIDATION", "SCIENTIFIC_HOLDOUT"):
        recorder.record_data_partition(partition)
    recorder.record_artifact("data", str(data_path.relative_to(output_dir)))
    recorder.record_results(
        run_count=len(records),
        clean_process=True,
        source_freeze_sha=source_freeze_sha,
    )
    recorder.record_provenance_digests(
        code_digest=code_digest,
        config_digest=config_digest,
        prompt_digest=prompt_digest,
        data_digest=data_digest,
    )
    manifest_path = recorder.mark_completed().save()

    return ProductiveLearningArtifact(
        experiment_id="EXP-STDP-0002",
        output_dir=output_dir,
        data_path=data_path,
        manifest_path=manifest_path,
        run_count=len(records),
        code_digest=code_digest,
        config_digest=config_digest,
        prompt_digest=prompt_digest,
        data_digest=data_digest,
        source_freeze_sha=source_freeze_sha,
    )