"""Verification gate for Brain-5D v0.5.0-alpha.3."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    """Run one quality-gate command in the repository root."""
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> int:
    """Run deterministic, type and dashboard checks for alpha.3."""
    python = sys.executable
    run(python, "-m", "pytest", "tests/test_runtime_control.py", "-v")
    run(python, "-m", "pytest", "tests/test_self_organization_policy_alpha3.py", "-v")
    run(python, "-m", "pytest", "tests/test_dashboard_control_service.py", "-v")
    run(python, "-m", "pytest", "tests/test_restore_continue.py", "-v")
    run(python, "-m", "pytest", "-m", "not slow", "-v")
    run(python, "-m", "mypy", "src")
    run("pyright", "src", "scripts", "tests")
    run("black", "--check", "src", "tests", "scripts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
