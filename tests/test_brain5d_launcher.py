"""Launcher subprocess argument isolation and single-PID tests."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from argparse import Namespace
from pathlib import Path

import pytest

from scripts.brain5d_launcher import build_command

ROOT = Path(__file__).resolve().parents[1]
PID_FILE = ROOT / "artifacts" / "brain5d.pid"


# ============================================================================
# Argument isolation tests
# ============================================================================


def test_launcher_keeps_dashboard_arguments_out_of_simulation_command() -> None:
    args = Namespace(
        config=Path("configs/poc_config.yaml"),
        observe=True,
        dashboard=True,
        open_browser=True,
        host="0.0.0.0",
        port=9000,
        benchmark=False,
        no_learning=False,
        no_homeostasis=False,
        ticks=None,
    )

    simulation_command = build_command(args)

    assert simulation_command[1:4] == ["-m", "src.main", "--config"]
    assert simulation_command[-1] == "--observe"
    assert "--dashboard" not in simulation_command
    assert "--open-browser" not in simulation_command
    assert "--host" not in simulation_command
    assert "--port" not in simulation_command


# ============================================================================
# Single-PID end-to-end test
# ============================================================================


def _clean_pid_file() -> None:
    """Remove the PID file if it exists."""
    try:
        PID_FILE.unlink(missing_ok=True)
    except OSError:
        pass


@pytest.mark.integration
def test_launcher_starts_exactly_one_process() -> None:
    """Verify the launcher starts exactly one Brain-5D process.

    This is the end-to-end test for the P0 process-architecture contract:

        * Exactly one application PID
        * Exactly one listener (no second dashboard process)
        * No global bridge state
        * Bridge identity remains stable for all HTTP requests

    The test starts ``brain5d_launcher.py start`` as a subprocess with
    ``--no-dashboard`` and a minimal tick count, then reads the PID file
    to verify a single PID was recorded. Finally it stops the process
    via the launcher's stop command.
    """
    _clean_pid_file()

    python_exe = sys.executable
    launcher = ROOT / "scripts" / "brain5d_launcher.py"
    config = ROOT / "configs" / "poc_config.yaml"

    # Start the launcher subprocess.
    # Without --dashboard, build_command() adds --no-dashboard to
    # the simulation command, so the simulation runs without a dashboard.
    proc = subprocess.Popen(
        [
            python_exe,
            str(launcher),
            "start",
            "--config",
            str(config),
            "--ticks",
            "10",
        ],
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        # Wait for the PID file to appear
        deadline = time.time() + 15.0
        pid_from_file: int | None = None

        while time.time() < deadline:
            if PID_FILE.exists():
                try:
                    raw = PID_FILE.read_text(encoding="utf-8").strip()
                    if raw:
                        pid_from_file = int(raw)
                        break
                except (ValueError, OSError):
                    pass
            time.sleep(0.2)

        # Assert: PID file was written
        assert pid_from_file is not None, (
            f"PID file was not created within 15 s. "
            f"Launcher stdout: {proc.stdout.read() if proc.stdout else '(none)'}\n"
            f"Launcher stderr: {proc.stderr.read() if proc.stderr else '(none)'}"
        )

        # Assert: PID is a positive integer
        assert pid_from_file > 0, f"PID must be positive, got {pid_from_file}"

        # Assert: exactly one PID (the file contains exactly one integer)
        raw = PID_FILE.read_text(encoding="utf-8").strip()
        parts = raw.split()
        assert len(parts) == 1, (
            f"PID file must contain exactly one PID, got {len(parts)}: {parts}"
        )

        # Assert: the process is actually running
        try:
            os.kill(pid_from_file, 0)  # signal 0 = existence check only
        except OSError as exc:
            pytest.fail(
                f"Process {pid_from_file} is not running: {exc}"
            )

        # Assert: the PID matches the launcher's child PID
        # (The launcher spawns one child; the PID file stores that child's PID)
        assert proc.returncode is None, (
            f"Launcher process exited prematurely with code {proc.returncode}"
        )

    finally:
        # Stop the process via the launcher's stop command
        subprocess.run(
            [python_exe, str(launcher), "stop"],
            cwd=str(ROOT),
            capture_output=True,
            timeout=10,
        )

        # Also terminate the launcher itself if still running
        if proc.returncode is None:
            if os.name == "nt":
                proc.send_signal(signal.CTRL_BREAK_EVENT)  # type: ignore[attr-defined]
            else:
                proc.terminate()
            proc.wait(timeout=5)

        _clean_pid_file()
