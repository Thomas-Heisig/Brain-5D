"""Generate tests/test_baseline.json from a completed full-suite run.

Usage:
    python -m pytest tests/ -q
    python scripts/generate_baseline.py

The script reads the pytest output from the last run (or you can pipe it),
computes the canonical source digest, and writes tests/test_baseline.json.

This is the ONLY canonical baseline writer. Never manually patch the digest.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = REPO_ROOT / "tests" / "test_baseline.json"

# Ensure src/ is importable
sys.path.insert(0, str(REPO_ROOT))


def current_git_head() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10,
            cwd=str(REPO_ROOT),
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception:
        return None


def main() -> int:
    from src.dashboard.verification import compute_source_tree_digest

    # Compute canonical digest
    digest = compute_source_tree_digest(REPO_ROOT)
    if digest is None:
        print("ERROR: Failed to compute source tree digest")
        return 1

    head = current_git_head()

    print(f"Canonical digest: {digest}")
    print(f"HEAD: {head}")
    print()

    # Run the full suite
    print("Running full test suite...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q"],
        capture_output=True, text=True, timeout=600,
        cwd=str(REPO_ROOT),
    )
    output = result.stdout + result.stderr

    # Parse results
    passed = 0
    failed = 0
    skipped = 0
    xfailed = 0
    xpassed = 0
    collection_errors = 0

    match = re.search(r"(\d+) passed", output)
    if match:
        passed = int(match.group(1))
    match = re.search(r"(\d+) failed", output)
    if match:
        failed = int(match.group(1))
    match = re.search(r"(\d+) skipped", output)
    if match:
        skipped = int(match.group(1))
    match = re.search(r"(\d+) xfailed", output)
    if match:
        xfailed = int(match.group(1))
    match = re.search(r"(\d+) xpassed", output)
    if match:
        xpassed = int(match.group(1))

    # Detect collection errors
    if "errors" in output and "collection" in output.lower():
        match = re.search(r"(\d+) error", output)
        if match:
            collection_errors = int(match.group(1))

    print(f"  {passed} passed, {failed} failed, {skipped} skipped, {xfailed} xfailed, {xpassed} xpassed, {collection_errors} collection errors")
    print()

    # Build baseline
    baseline: dict[str, object] = {
        "tested_commit": head,
        "tested_tree_digest": digest,
        "tree_digest_paths": ["src/", "configs/", "research/schemas/", "pyproject.toml", "tests/"],
        "tree_digest_excludes": ["tests/test_baseline.json"],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "full_collection": {
            "status": "passed" if collection_errors == 0 else "failed",
            "collection_errors": collection_errors,
        },
        "full_suite": {
            "command": "python -m pytest tests/ -q",
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "xfailed": xfailed,
            "xpassed": xpassed,
        },
    }

    # Add skipped reasons if any
    if skipped > 0:
        reasons: list[str] = []
        for line in output.split("\n"):
            if "SKIPPED" in line:
                reasons.append(line.split("SKIPPED")[-1].strip().lstrip("[").rstrip("]"))
        if reasons:
            baseline["full_suite"]["skipped_reasons"] = reasons  # type: ignore[typeddict-item]

    # Write baseline
    BASELINE_PATH.write_text(
        json.dumps(baseline, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Baseline written to: {BASELINE_PATH}")
    print(f"  tested_tree_digest = {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
