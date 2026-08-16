"""Quality verification for the Brain-5D operator dashboard and embodiment bridge."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run(*command: str) -> None:
    """Run one command and fail immediately if it fails."""
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    """Verify dashboard and embodiment quality surfaces."""
    python = sys.executable
    run(
        python,
        "-m",
        "pytest",
        "tests/test_dashboard.py",
        "tests/test_dashboard_alpha6.py",
        "tests/test_dashboard_alpha7.py",
        "tests/test_embodiment.py",
        "-v",
    )
    run(
        "black",
        "--check",
        "src/dashboard",
        "src/embodiment",
        "tests/test_dashboard.py",
        "tests/test_dashboard_alpha6.py",
        "tests/test_dashboard_alpha7.py",
        "tests/test_embodiment.py",
    )
    run("mypy", "--strict", "src/dashboard", "src/embodiment")
    run("pylint", "src/dashboard", "src/embodiment")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
