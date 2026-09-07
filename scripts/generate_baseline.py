"""Run the complete suite and publish an honest, source-bound test baseline.

Ordinary pytest invocations never update tracked verification artifacts. This
explicit command enables their publication and rejects failed/interrupted runs
or a source tree that changes while verification is running.
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

REPO_ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = REPO_ROOT / "tests" / "test_baseline.json"
sys.path.insert(0, str(REPO_ROOT))


def main() -> int:
    from src.dashboard.verification import compute_source_tree_digest, current_git_head

    digest = compute_source_tree_digest(REPO_ROOT)
    if digest is None:
        print("ERROR: Cannot compute source digest")
        return 1
    with tempfile.TemporaryDirectory(prefix="brain5d-baseline-") as directory:
        report = Path(directory) / "pytest.xml"
        command = [
            sys.executable,
            "-m",
            "pytest",
            "tests/",
            "-q",
            "-ra",
            f"--junitxml={report}",
        ]
        environment = {**os.environ, "BRAIN5D_WRITE_VERIFICATION_ARTIFACTS": "1"}
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
            timeout=900,
        )
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        if not report.is_file():
            print("ERROR: pytest produced no machine-readable results")
            return 1
        suites = ElementTree.parse(report).getroot().findall(".//testsuite")
        tests = sum(int(suite.get("tests", "0")) for suite in suites)
        failed = sum(int(suite.get("failures", "0")) for suite in suites)
        errors = sum(int(suite.get("errors", "0")) for suite in suites)
        skipped = sum(int(suite.get("skipped", "0")) for suite in suites)
        passed = tests - failed - errors - skipped
        unchanged = compute_source_tree_digest(REPO_ROOT) == digest
        success = (
            result.returncode == 0
            and passed > 0
            and errors == 0
            and failed == 0
            and unchanged
        )
        baseline: dict[str, Any] = {
            "schema_version": 2,
            "tested_commit": current_git_head(REPO_ROOT),
            "tested_tree_digest": digest,
            "tree_digest_paths": [
                "src/",
                "configs/",
                "research/schemas/",
                "pyproject.toml",
                "tests/",
            ],
            "tree_digest_excludes": ["tests/test_baseline.json"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(),
            "platform": platform.platform(),
            "source_unchanged_during_run": unchanged,
            "full_collection": {
                "status": "passed" if success else "failed",
                "collected": tests,
                "collection_errors": errors,
            },
            "full_suite": {
                "command": "python -m pytest tests/ -q -ra --junitxml=<temporary-report>",
                "status": "passed" if success else "failed",
                "exit_code": result.returncode,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "skipped": skipped,
                "xfailed": 0,
                "xpassed": 0,
                "skipped_reasons": [
                    element.text or ""
                    for element in ElementTree.parse(report).getroot().iter("skipped")
                ],
            },
        }
    BASELINE_PATH.write_text(
        json.dumps(baseline, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        f"Baseline: {passed} passed, {failed} failed, {errors} errors, {skipped} skipped; unchanged={unchanged}"
    )
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
