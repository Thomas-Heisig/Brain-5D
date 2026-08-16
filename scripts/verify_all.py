"""Fail-fast quality gate for Brain-5D v0.4.0-alpha.7."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run(*command: str) -> None:
    """Run one quality command and fail immediately on errors."""
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    """Run functional, formatting, typing, lint and compile checks."""
    python = sys.executable
    run(python, "-m", "pytest", "-v")
    run("black", "--check", "src", "tests")
    run("mypy", "src")
    run("pylint", "src")
    run(python, "-m", "compileall", "-q", "src", "tests")
    print("Brain-5D alpha.7 quality gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
