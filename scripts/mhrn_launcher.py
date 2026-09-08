"""MHRN launcher; keep the legacy process/PID contract to avoid orphan processes."""

from __future__ import annotations

import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(
        str(Path(__file__).with_name("brain5d_launcher.py")), run_name="__main__"
    )
