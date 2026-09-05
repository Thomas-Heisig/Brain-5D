"""Contracts for clean-process productive-learning publication."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from src.research.productive_learning import run_clean_process_repeats


def test_clean_process_repeats_publish_digest_bound_data(tmp_path: Path) -> None:
    artifact = run_clean_process_repeats(
        Path("configs/learning_experiment.yaml"),
        tmp_path / "EXP-STDP-0002",
        seeds=(42,),
    )

    assert artifact.run_count == 3
    assert (
        artifact.data_digest
        == hashlib.sha256(artifact.data_path.read_bytes()).hexdigest()
    )
    records = [
        json.loads(line)
        for line in artifact.data_path.read_text(encoding="utf-8").splitlines()
    ]
    assert {record["condition"] for record in records} == {
        "learning_on",
        "learning_off",
        "sham_replay",
    }
    assert all(record["clean_process"] is True for record in records)
    assert all(isinstance(record["process_id"], int) for record in records)

    manifest = json.loads(artifact.manifest_path.read_text(encoding="utf-8"))
    assert manifest["provenance_digests"]["data"] == artifact.data_digest
    assert manifest["source_freeze_sha"] == artifact.source_freeze_sha
    assert manifest["simulation"]["clean_process"] is True
    assert manifest["data_partitions"] == [
        "DEVELOPMENT",
        "VALIDATION",
        "SCIENTIFIC_HOLDOUT",
    ]
