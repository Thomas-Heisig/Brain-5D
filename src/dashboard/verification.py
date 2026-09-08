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
import platform
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

# ============================================================================
# Scientifically relevant source paths
# ============================================================================

# Source code and config changes must mark the baseline as stale.
SCIENTIFIC_PATHS: list[str] = [
    "src/",
    "configs/",
    "research/schemas/",
    "pyproject.toml",
]

# Test logic changes must also mark the baseline as stale — a changed test
# is a changed verification. But the baseline file itself must NOT
# invalidate itself (a file cannot stably contain its own digest).
TEST_PATHS: list[str] = ["tests/"]
_DIGEST_EXCLUDE_FILES: set[str] = {"tests/test_baseline.json"}
_DIGEST_EXCLUDE_SUFFIXES: tuple[str, ...] = (".pyc", ".pyo")
_DIGEST_EXCLUDE_DIRS: tuple[str, ...] = ("__pycache__",)


@dataclass(frozen=True, slots=True)
class SourceTreeInspection:
    """Deterministic source-freeze details used by gates and diagnostics."""

    digest: str | None
    dirty_relevant_paths: tuple[str, ...]
    untracked_relevant_paths: tuple[str, ...]
    missing_relevant_paths: tuple[str, ...]
    mismatching_files: tuple[str, ...]
    platform: str
    line_ending_normalization_mode: str
    git_available: bool


def _is_digest_file(path: Path, repo_root: Path) -> bool:
    """Return whether a filesystem path belongs to the digest scope."""
    if not path.is_file():
        return False
    relative = path.relative_to(repo_root).as_posix()
    if relative in _DIGEST_EXCLUDE_FILES or relative.endswith(_DIGEST_EXCLUDE_SUFFIXES):
        return False
    return not any(
        part in _DIGEST_EXCLUDE_DIRS or part.endswith(".egg-info")
        for part in path.relative_to(repo_root).parts
    )


def _filesystem_digest_paths(repo_root: Path, paths: list[str]) -> list[str]:
    """Return digest paths in the historical, reproducible traversal order."""
    result: list[str] = []
    for relative in paths:
        target = repo_root / relative
        if target.is_file():
            if _is_digest_file(target, repo_root):
                result.append(relative.rstrip("/"))
        elif target.is_dir():
            result.extend(
                path.relative_to(repo_root).as_posix()
                for path in sorted(target.rglob("*"))
                if _is_digest_file(path, repo_root)
            )
    return result


def _git_output(
    repo_root: Path, arguments: list[str], input_data: bytes = b""
) -> bytes | None:
    """Run a bounded, read-only Git command."""
    try:
        result = subprocess.run(
            ["git", *arguments],
            cwd=str(repo_root),
            input=input_data,
            capture_output=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout


def _git_scope_paths(
    repo_root: Path, paths: list[str], *, untracked: bool
) -> list[str]:
    arguments = ["ls-files", "-z"]
    if untracked:
        arguments.extend(["--others", "--exclude-standard"])
    arguments.extend(["--", *paths])
    output = _git_output(repo_root, arguments)
    if output is None:
        return []
    return [
        item.decode("utf-8", "surrogateescape") for item in output.split(b"\0") if item
    ]


def _git_changed_paths(repo_root: Path, paths: list[str]) -> set[str]:
    output = _git_output(repo_root, ["diff", "HEAD", "--name-only", "-z", "--", *paths])
    if output is None:
        return set()
    return {
        item.decode("utf-8", "surrogateescape") for item in output.split(b"\0") if item
    }


def _git_index_blobs(repo_root: Path) -> dict[str, bytes]:
    """Read stage-zero index blobs in one Git batch operation."""
    listing = _git_output(repo_root, ["ls-files", "-s", "-z"])
    if listing is None:
        return {}
    entries: list[tuple[str, str]] = []
    for raw_entry in listing.split(b"\0"):
        if not raw_entry:
            continue
        header, separator, raw_path = raw_entry.partition(b"\t")
        fields = header.split()
        if not separator or len(fields) != 3 or fields[2] != b"0":
            continue
        entries.append(
            (
                raw_path.decode("utf-8", "surrogateescape"),
                fields[1].decode("ascii"),
            )
        )
    if not entries:
        return {}

    request = b"".join(f"{object_id}\n".encode("ascii") for _, object_id in entries)
    output = _git_output(repo_root, ["cat-file", "--batch"], request)
    if output is None:
        return {}
    blobs: dict[str, bytes] = {}
    offset = 0
    for relative, object_id in entries:
        header_end = output.find(b"\n", offset)
        if header_end < 0:
            break
        fields = output[offset:header_end].split()
        offset = header_end + 1
        if len(fields) != 3 or fields[0].decode("ascii", "ignore") != object_id:
            break
        size = int(fields[2])
        blobs[relative] = output[offset : offset + size]
        offset += size + 1
    return blobs


def _git_text_paths(repo_root: Path, paths: list[str]) -> set[str]:
    """Resolve Git's text attribute for paths using one batch query."""
    if not paths:
        return set()
    input_data = ("\n".join(paths) + "\n").encode("utf-8", "surrogateescape")
    output = _git_output(repo_root, ["check-attr", "--stdin", "text"], input_data)
    if output is None:
        return set()
    text_paths: set[str] = set()
    for raw_line in output.splitlines():
        try:
            relative, _attribute, value = raw_line.decode(
                "utf-8", "surrogateescape"
            ).rsplit(": ", 2)
        except ValueError:
            continue
        if value in {"set", "auto"}:
            text_paths.add(relative)
    return text_paths


def _canonical_text_bytes(data: bytes) -> bytes:
    """Apply Git's portable text line-ending representation without decoding."""
    return data.replace(b"\r\n", b"\n")


def _digest_bytes(path: Path, relative: str, text_paths: set[str]) -> bytes:
    data = path.read_bytes()
    if relative in text_paths or (relative not in text_paths and b"\0" not in data):
        return _canonical_text_bytes(data)
    return data


def inspect_source_tree(
    repo_root: Path,
    paths: list[str] | None = None,
) -> SourceTreeInspection:
    """Inspect and hash the source freeze with Git-aware text canonicalization."""
    all_paths = paths if paths is not None else SCIENTIFIC_PATHS + TEST_PATHS
    filesystem_paths = _filesystem_digest_paths(repo_root, all_paths)
    tracked_paths = _git_scope_paths(repo_root, all_paths, untracked=False)
    untracked_paths = _git_scope_paths(repo_root, all_paths, untracked=True)
    git_available = bool(
        tracked_paths or _git_output(repo_root, ["rev-parse", "--git-dir"])
    )
    changed_paths: set[str] = (
        _git_changed_paths(repo_root, all_paths) if git_available else set()
    )
    relevant_untracked = sorted(
        path for path in untracked_paths if _is_digest_file(repo_root / path, repo_root)
    )
    tracked_set = {
        path for path in tracked_paths if _is_digest_file(repo_root / path, repo_root)
    }
    filesystem_set = set(filesystem_paths)
    missing_paths = sorted(tracked_set - filesystem_set)
    dirty_paths = sorted(path for path in changed_paths if path in tracked_set)
    mismatching = tuple(
        sorted(set(dirty_paths) | set(relevant_untracked) | set(missing_paths))
    )

    text_paths: set[str] = (
        _git_text_paths(
            repo_root, sorted(set(filesystem_paths) | set(relevant_untracked))
        )
        if git_available
        else set()
    )
    index_blobs = _git_index_blobs(repo_root) if git_available else {}
    hasher = hashlib.sha256()
    found_any = False
    ordered_paths = list(filesystem_paths)
    ordered_paths.extend(path for path in missing_paths if path not in filesystem_set)
    for relative in ordered_paths:
        path = repo_root / relative
        if (
            relative in index_blobs
            and relative not in dirty_paths
            and relative not in missing_paths
        ):
            data = index_blobs[relative]
        elif path.is_file():
            data = _digest_bytes(path, relative, text_paths)
        else:
            data = b"<missing>"
        hasher.update(relative.encode("utf-8", "surrogateescape"))
        hasher.update(b"\0")
        hasher.update(data)
        hasher.update(b"\0")
        found_any = True

    return SourceTreeInspection(
        digest=hasher.hexdigest() if found_any else None,
        dirty_relevant_paths=tuple(dirty_paths),
        untracked_relevant_paths=tuple(relevant_untracked),
        missing_relevant_paths=tuple(missing_paths),
        mismatching_files=mismatching,
        platform=platform.platform(),
        line_ending_normalization_mode="git-text-crlf-to-lf;binary-byte-exact",
        git_available=git_available,
    )


def canonical_source_file_bytes(repo_root: Path, relative: str) -> bytes:
    """Return one working-tree file in the source-freeze representation."""
    path = repo_root / relative
    if not path.is_file():
        raise FileNotFoundError(relative)
    text_paths = _git_text_paths(repo_root, [relative])
    return _digest_bytes(path, relative, text_paths)


def source_digest_paths(repo_root: Path, paths: list[str] | None = None) -> list[str]:
    """Return the included repository-relative paths in digest order."""
    return _filesystem_digest_paths(
        repo_root, paths if paths is not None else SCIENTIFIC_PATHS + TEST_PATHS
    )


def git_source_blob(repo_root: Path, relative: str) -> bytes | None:
    """Read one HEAD blob for human-readable source-digest diagnostics."""
    return _git_output(repo_root, ["show", f"HEAD:{relative}"])


# Stable evidence boundaries.  Paths are repository-relative and deliberately
# explicit so a dashboard-only change does not stale storage evidence.
EVIDENCE_SCOPES: dict[str, tuple[str, ...]] = {
    "restore_determinism": (
        "src/core/",
        "src/storage/",
        "src/learning/",
        "src/homeostasis/",
        "configs/",
        "tests/test_restore_determinism_abc.py",
        "tests/test_production_restore.py",
    ),
    "structural_e2e": (
        "src/self_organization/",
        "src/manipulation/",
        "src/storage/",
        "tests/test_structural_e2e.py",
    ),
    "structural_live_loop": (
        "src/self_organization/",
        "src/manipulation/",
        "src/storage/",
        "src/controller/",
        "tests/test_structural_live_loop.py",
    ),
    "runtime_integration": (
        "src/controller/",
        "src/dashboard/operator_bridge.py",
        "src/main.py",
        "tests/test_single_listener.py",
    ),
    "dashboard": (
        "src/dashboard/",
        "tests/test_dashboard.py",
        "tests/test_dashboard_completion.py",
    ),
    "research": (
        "src/research/",
        "research/schemas/",
        "tests/test_research_registry.py",
        "tests/test_experiment_validity.py",
    ),
    "release": ("src/", "configs/", "research/schemas/", "tests/"),
}

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
        return cast(
            "dict[str, Any]", json.loads(baseline_path.read_text(encoding="utf-8"))
        )
    except Exception:
        return None


def compute_source_tree_digest(
    repo_root: Path,
    paths: list[str] | None = None,
) -> str | None:
    """Return a SHA-256 digest of the scientifically relevant source tree.

    The digest covers ``src/``, ``configs/``, ``research/schemas/``,
    ``pyproject.toml`` and ``tests/`` (excluding ``test_baseline.json``
    so the baseline file cannot invalidate itself).

    Tracked clean files use their canonical Git index blobs. Working-tree
    changes and relevant untracked files are included after Git-compatible
    text line-ending normalization; binary bytes remain exact. Returns
    ``None`` if no files were found.
    """
    try:
        return inspect_source_tree(repo_root, paths).digest
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def compute_legacy_raw_source_tree_digest(
    repo_root: Path,
    paths: list[str] | None = None,
) -> str | None:
    """Compute the pre-fix raw-byte digest for migration diagnostics only."""
    all_paths = paths if paths is not None else SCIENTIFIC_PATHS + TEST_PATHS
    try:
        hasher = hashlib.sha256()
        found_any = False
        for relative in _filesystem_digest_paths(repo_root, all_paths):
            hasher.update(relative.encode("utf-8", "surrogateescape"))
            hasher.update(b"\0")
            hasher.update((repo_root / relative).read_bytes())
            hasher.update(b"\0")
            found_any = True
        return hasher.hexdigest() if found_any else None
    except OSError:
        return None


def compute_scope_digest(repo_root: Path, scope: str) -> str | None:
    """Return the content digest for one named evidence scope."""
    paths = EVIDENCE_SCOPES.get(scope)
    if paths is None:
        raise ValueError(f"unknown evidence scope: {scope}")
    return compute_source_tree_digest(repo_root, list(paths))


def artifact_digest_matches(repo_root: Path, artifact: dict[str, Any]) -> bool:
    """Validate scoped artifact digests, falling back to legacy digests."""
    scope = artifact.get("scope")
    scope_digest = artifact.get("scope_digest")
    if isinstance(scope, str) and isinstance(scope_digest, str):
        try:
            return scope_digest == compute_scope_digest(repo_root, scope)
        except ValueError:
            return False
    legacy_digest = artifact.get("tested_tree_digest")
    return isinstance(
        legacy_digest, str
    ) and legacy_digest == compute_source_tree_digest(repo_root)


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
        dirty_relevant_paths: tuple[str, ...] = (),
        untracked_relevant_paths: tuple[str, ...] = (),
        mismatching_files: tuple[str, ...] = (),
        stale_reason: str | None = None,
        platform_name: str | None = None,
        line_ending_normalization_mode: str = "git-text-crlf-to-lf;binary-byte-exact",
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
        self.dirty_relevant_paths = dirty_relevant_paths
        self.untracked_relevant_paths = untracked_relevant_paths
        self.mismatching_files = mismatching_files
        self.stale_reason = stale_reason
        self.platform = platform_name or platform.platform()
        self.line_ending_normalization_mode = line_ending_normalization_mode


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
    inspection = inspect_source_tree(repo_root)
    current_tree_digest = inspection.digest

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
            dirty_relevant_paths=inspection.dirty_relevant_paths,
            untracked_relevant_paths=inspection.untracked_relevant_paths,
            mismatching_files=inspection.mismatching_files,
            platform_name=inspection.platform,
            line_ending_normalization_mode=inspection.line_ending_normalization_mode,
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
    stale_reason: str | None = "missing_tree_digest"
    if tested_tree_digest is not None and current_tree_digest is not None:
        local_tree_changed = bool(inspection.mismatching_files)
        stale = tested_tree_digest != current_tree_digest or local_tree_changed
        if not stale:
            stale_reason = None
        elif inspection.dirty_relevant_paths or inspection.missing_relevant_paths:
            stale_reason = "working_tree_content_diff"
        elif inspection.untracked_relevant_paths:
            stale_reason = "untracked_relevant_path"
        elif tested_tree_digest == compute_legacy_raw_source_tree_digest(repo_root):
            stale_reason = "legacy_platform_digest_mismatch"
        else:
            stale_reason = "verification_artifact_scope_mismatch"

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
        dirty_relevant_paths=inspection.dirty_relevant_paths,
        untracked_relevant_paths=inspection.untracked_relevant_paths,
        mismatching_files=inspection.mismatching_files,
        stale_reason=stale_reason,
        platform_name=inspection.platform,
        line_ending_normalization_mode=inspection.line_ending_normalization_mode,
    )
