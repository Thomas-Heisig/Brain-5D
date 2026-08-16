"""Prepare an alpha.4 working tree for strict quality verification."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    """Run one repository preparation command and fail fast."""
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> int:
    """Apply narrow typing patches and normalize Python formatting."""
    run(sys.executable, "scripts/apply_alpha4_quality_fixes.py")
    run(sys.executable, "-m", "black", "src", "tests")
    print("alpha.4 preparation complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
