"""Regression tests for the cross-platform scientific source freeze."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, cast

from src.dashboard.gate_status import GateStatusBuilder
from src.dashboard.verification import (
    artifact_digest_matches,
    compute_scope_digest,
    compute_source_tree_digest,
    inspect_source_tree,
)


def _git_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True
    )
    subprocess.run(["git", "config", "user.name", "Digest Test"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "initial"], cwd=root, check=True)


def test_lf_and_crlf_text_have_identical_scientific_digest(tmp_path: Path) -> None:
    source = tmp_path / "src" / "module.py"
    source.parent.mkdir()
    source.write_bytes(b"one\ntwo\n")
    lf_digest = compute_source_tree_digest(tmp_path, ["src/"])
    source.write_bytes(b"one\r\ntwo\r\n")
    assert compute_source_tree_digest(tmp_path, ["src/"]) == lf_digest


def test_real_text_change_changes_digest(tmp_path: Path) -> None:
    source = tmp_path / "src" / "module.py"
    source.parent.mkdir()
    source.write_text("value = 1\n", encoding="utf-8")
    first = compute_source_tree_digest(tmp_path, ["src/"])
    source.write_text("value = 2\n", encoding="utf-8")
    assert compute_source_tree_digest(tmp_path, ["src/"]) != first


def test_binary_bytes_remain_exact(tmp_path: Path) -> None:
    binary = tmp_path / "src" / "payload.bin"
    binary.parent.mkdir()
    binary.write_bytes(b"header\x00one\r\ntwo")
    first = compute_source_tree_digest(tmp_path, ["src/"])
    binary.write_bytes(b"header\x00one\ntwo")
    assert compute_source_tree_digest(tmp_path, ["src/"]) != first


def test_ignored_cache_does_not_change_digest(tmp_path: Path) -> None:
    source = tmp_path / "src" / "module.py"
    source.parent.mkdir()
    source.write_text("value = 1\n", encoding="utf-8")
    first = compute_source_tree_digest(tmp_path, ["src/"])
    (source.parent / "module.pyc").write_bytes(b"cache")
    metadata = source.parent / "mhrn_core.egg-info"
    metadata.mkdir()
    (metadata / "PKG-INFO").write_text("generated", encoding="utf-8")
    assert compute_source_tree_digest(tmp_path, ["src/"]) == first


def test_relevant_untracked_file_is_reported(tmp_path: Path) -> None:
    source = tmp_path / "src" / "module.py"
    source.parent.mkdir()
    source.write_text("value = 1\n", encoding="utf-8")
    _git_repo(tmp_path)
    extra = tmp_path / "src" / "untracked.py"
    extra.write_text("value = 2\n", encoding="utf-8")
    inspection = inspect_source_tree(tmp_path, ["src/"])
    assert inspection.untracked_relevant_paths == ("src/untracked.py",)
    assert "src/untracked.py" in inspection.mismatching_files


def test_relevant_dirty_file_is_reported(tmp_path: Path) -> None:
    source = tmp_path / "src" / "module.py"
    source.parent.mkdir()
    source.write_text("value = 1\n", encoding="utf-8")
    _git_repo(tmp_path)
    source.write_text("value = 2\n", encoding="utf-8")
    inspection = inspect_source_tree(tmp_path, ["src/"])
    assert inspection.dirty_relevant_paths == ("src/module.py",)
    assert inspection.mismatching_files == ("src/module.py",)


def test_scoped_artifact_accepts_crlf_working_tree(tmp_path: Path) -> None:
    source = tmp_path / "src" / "self_organization" / "engine.py"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"return True\n")
    digest = compute_scope_digest(tmp_path, "structural_e2e")
    source.write_bytes(b"return True\r\n")
    assert artifact_digest_matches(
        tmp_path, {"scope": "structural_e2e", "scope_digest": digest}
    )


def test_ci_provenance_loads_when_source_digest_matches(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "module.py").write_text("value = 1\n", encoding="utf-8")
    digest = compute_source_tree_digest(tmp_path)
    baseline = {
        "tested_commit": "verified-head",
        "tested_tree_digest": digest,
        "full_collection": {"collection_errors": 0},
        "full_suite": {"passed": 1, "failed": 0, "skipped": 0},
    }
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_baseline.json").write_text(
        json.dumps(baseline), encoding="utf-8"
    )
    artifact_dir = tmp_path / "research" / "generated" / "verification"
    artifact_dir.mkdir(parents=True)
    (artifact_dir / "phase_b_gate_status.json").write_text(
        json.dumps(
            {
                "source_freeze": {
                    "commit": "verified-head",
                    "tested_tree_digest": digest,
                },
                "continuous_integration": {
                    "workflow": "CI",
                    "run_id": 1,
                    "head_sha": "verified-head",
                    "conclusion": "success",
                },
            }
        ),
        encoding="utf-8",
    )
    status = cast(
        dict[str, Any], GateStatusBuilder(repo_root=tmp_path).build()["ci_status"]
    )
    assert status["status"] == "passed"
