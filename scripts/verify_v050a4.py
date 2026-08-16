"""Quality gate for v0.5.0-alpha.4."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> int:
    run(sys.executable, "-m", "pytest", "-v", "-m", "not slow")
    if shutil.which("black"):
        run("black", "--check", "src", "tests", "scripts")
    if shutil.which("mypy"):
        run("mypy", "src")
    if shutil.which("pyright"):
        run("pyright", "src", "scripts", "tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
