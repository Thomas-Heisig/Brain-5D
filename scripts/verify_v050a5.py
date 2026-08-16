"""Quality gate for Brain-5D v0.5.0-alpha.5."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(list(args), cwd=ROOT, check=True)


def run_module(module: str, *args: str) -> None:
    run(sys.executable, "-m", module, *args)


def main() -> int:
    run_module("pytest", "-v", "-m", "not slow")
    run_module(
        "pytest",
        "-v",
        "tests/test_structural_journal.py",
        "tests/test_structural_recovery.py",
        "tests/test_structural_undo.py",
        "tests/test_structural_heatmap.py",
        "tests/test_auto_approval.py",
    )
    run_module("mypy", "src")
    run_module("black", "--check", "src", "tests", "scripts")
    try:
        run_module("pyright", "src", "scripts", "tests")
    except subprocess.CalledProcessError:
        executable = shutil.which("pyright")
        if executable is None:
            raise RuntimeError(
                "Pyright is a required quality gate but is not installed"
            )
        run(executable, "src", "scripts", "tests")
    pylint = shutil.which("pylint")
    if pylint is None:
        raise RuntimeError("Pylint is a required quality gate but is not installed")
    run(pylint, "src")
    git = shutil.which("git")
    if git is None:
        raise RuntimeError("git is required for diff validation")
    run(git, "diff", "--check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
