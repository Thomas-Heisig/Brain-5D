"""Verify the Brain-5D operator dashboard and its static assets."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*command: str) -> None:
    """Execute one command from the repository root and fail fast."""
    print("+", " ".join(command))
    result = subprocess.run(command, cwd=ROOT, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> None:
    """Run dashboard unit, format, type, and lint checks."""
    run(sys.executable, "-m", "pytest", "tests/test_dashboard.py", "-v")
    run("black", "--check", "src/dashboard", "tests/test_dashboard.py")
    run("mypy", "--strict", "src/dashboard")
    run("pylint", "src/dashboard")


if __name__ == "__main__":
    main()
