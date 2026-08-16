"""Run the v0.5.0-alpha.1 release verification commands."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    """Run one verification command and stop on failure."""
    print("+", " ".join(args))
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> int:
    """Execute the focused and repository-wide quality gates."""
    python = sys.executable
    run(python, "-m", "pytest", "tests/test_restore_continue.py", "-v")
    run(python, "-m", "pytest", "tests/test_homeostasis_engine.py", "-v")
    run(python, "-m", "pytest", "tests/test_dashboard_homeostasis.py", "-v")
    run(python, "-m", "pytest", "-v")
    run("black", "--check", "src", "tests")
    run("mypy", "src")
    run("pylint", "src/homeostasis", "src/dashboard", "src/storage/checkpoint.py")
    run("git", "diff", "--check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
