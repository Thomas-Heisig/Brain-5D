"""Shared verification utilities for dashboard status builders.

Both ``IntegrationStatusBuilder`` and ``GateStatusBuilder`` use these
functions so that ``/api/integration/status`` and ``/api/gate/status``
can never disagree about the same source tree.

Scientifically relevant paths (tree digest)::

    src/
    configs/
    research/schemas/
    pyproject.toml

A test-baseline change (docs, CHANGELOG, test_baseline.json itself) must
NOT invalidate the test status. Only changes to the scientifically
relevant source tree mark the baseline as stale.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

# ============================================================================
# Scientifically relevant source paths
# ============================================================================

# Source code and config changes must mark the baseline as stale.
SCIENTIFIC_PATHS: list[str] = ["src/", "configs/", "research/schemas/", "pyproject.toml"]

# Test logic changes must also mark the baseline as stale — a changed test
# is a changed verification. But the baseline file itself must NOT
# invalidate itself (a file cannot stably contain its own digest).
TEST_PATHS: list[str] = ["tests/"]
_DIGEST_EXCLUDE_FILES: set[str] = {"tests/test_baseline.json"}

# ============================================================================
# Test baseline evaluation
# ============================================================================


def read_test_baseline(repo_root: Path) -> dict[str, Any] | None:
    """Read ``tests/test_baseline.json``.

    Returns ``None`` if the file is missing or unparseable.
    """
    baseline_path = repo_root / "tests" / "test_baseline.json"
    if not baseline_path.exists():
        return None
    try:
        return json.loads(baseline_path.read_text(encoding="utf-8"))
    except Exception:
        return None


def compute_source_tree_digest(repo_root: Path) -> str | None:
    """Return a SHA-256 digest of the scientifically relevant source tree.

    The digest covers ``src/``, ``configs/``, ``research/schemas/``,
    ``pyproject.toml`` and ``tests/`` (excluding ``test_baseline.json``
    so the baseline file cannot invalidate itself).

    The digest is computed from file contents (not git blobs) so it works
    in a dirty working tree and does not require a clean git state.
    Returns ``None`` if no files were found.
    """
    all_paths = SCIENTIFIC_PATHS + TEST_PATHS
    try:
        hasher = hashlib.sha256()
        found_any = False
        for rel in all_paths:
            target = repo_root / rel
            if target.is_file():
                rel_posix = rel.rstrip("/")
                if rel_posix in _DIGEST_EXCLUDE_FILES:
                    continue
                hasher.update(rel_posix.encode("utf-8"))
                hasher.update(b"\0")
                hasher.update(target.read_bytes())
                hasher.update(b"\0")
                found_any = True
            elif target.is_dir():
                for path in sorted(target.rglob("*")):
                    if not path.is_file():
                        continue
                    rel_path = path.relative_to(repo_root).as_posix()
                    if rel_path in _DIGEST_EXCLUDE_FILES:
                        continue
                    hasher.update(rel_path.encode("utf-8"))
                    hasher.update(b"\0")
                    hasher.update(path.read_bytes())
                    hasher.update(b"\0")
                    found_any = True
        if not found_any:
            return None
        return hasher.hexdigest()
    except Exception:
        return None


def current_git_head(repo_root: Path) -> str | None:
    """Return the current git HEAD SHA, or None if unavailable."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(repo_root),
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


class BaselineEvaluation:
    """Result of evaluating the test baseline against the current tree."""

    def __init__(
        self,
        *,
        stale: bool,
        available: bool,
        passed: int,
        failed: int,
        skipped: int,
        collection_errors: int,
        tested_commit: str | None,
        current_commit: str | None,
        tested_tree_digest: str | None,
        current_tree_digest: str | None,
    ) -> None:
        self.stale = stale
        self.available = available
        self.passed = passed
        self.failed = failed
        self.skipped = skipped
        self.collection_errors = collection_errors
        self.tested_commit = tested_commit
        self.current_commit = current_commit
        self.tested_tree_digest = tested_tree_digest
        self.current_tree_digest = current_tree_digest


def evaluate_test_baseline(repo_root: Path) -> BaselineEvaluation:
    """Evaluate ``tests/test_baseline.json`` against the current source tree.

    Handles both the new format (``full_suite`` + ``full_collection``) and
    the legacy format (``verified_subset``) so that old baselines do not
    silently report zero counts.

    Returns a :class:`BaselineEvaluation` with ``stale=True`` when the
    scientifically relevant source tree changed since the baseline.
    """
    baseline = read_test_baseline(repo_root)
    current_commit = current_git_head(repo_root)
    current_tree_digest = compute_source_tree_digest(repo_root)

    if baseline is None:
        return BaselineEvaluation(
            stale=True,
            available=False,
            passed=0,
            failed=0,
            skipped=0,
            collection_errors=1,
            tested_commit=None,
            current_commit=current_commit,
            tested_tree_digest=None,
            current_tree_digest=current_tree_digest,
        )

    # --- Counts: support both new (full_suite) and legacy (verified_subset) ---
    full_suite = baseline.get("full_suite", {})
    full_collection = baseline.get("full_collection", {})
    legacy_subset = baseline.get("verified_subset", {})

    if full_suite:
        passed = int(full_suite.get("passed", 0))
        failed = int(full_suite.get("failed", 0))
        skipped = int(full_suite.get("skipped", 0))
    elif legacy_subset:
        passed = int(legacy_subset.get("passed", 0))
        failed = int(legacy_subset.get("failed", 0))
        skipped = int(legacy_subset.get("skipped", 0))
    else:
        passed = 0
        failed = 0
        skipped = 0

    if full_collection:
        collection_errors = int(full_collection.get("collection_errors", 1))
    else:
        collection_errors = 0 if passed > 0 else 1

    tested_commit = baseline.get("tested_commit")
    tested_tree_digest = baseline.get("tested_tree_digest")

    stale = True
    if tested_tree_digest is not None and current_tree_digest is not None:
        stale = tested_tree_digest != current_tree_digest

    return BaselineEvaluation(
        stale=stale,
        available=True,
        passed=passed,
        failed=failed,
        skipped=skipped,
        collection_errors=collection_errors,
        tested_commit=tested_commit,
        current_commit=current_commit,
        tested_tree_digest=tested_tree_digest,
        current_tree_digest=current_tree_digest,
    )
