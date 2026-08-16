"""Cross-platform process launcher for Brain-5D simulation and dashboard."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import webbrowser

_STATE_FILE = Path("artifacts/run/brain5d_processes.json")
_LOG_DIR = Path("artifacts/logs")


def _spawn(command: list[str], log_name: str) -> int:
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = _LOG_DIR / log_name
    with log_path.open("ab") as log_handle:
        kwargs: dict[str, object] = {
            "stdin": subprocess.DEVNULL,
            "stdout": log_handle,
            "stderr": subprocess.STDOUT,
            "cwd": Path.cwd(),
        }
        if os.name == "nt":
            kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            kwargs["start_new_session"] = True
        process = subprocess.Popen(command, **kwargs)  # noqa: S603
    return int(process.pid)


def _write_state(processes: dict[str, int]) -> None:
    _STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    _STATE_FILE.write_text(
        json.dumps(processes, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _read_state() -> dict[str, int]:
    if not _STATE_FILE.is_file():
        return {}
    raw: object = json.loads(_STATE_FILE.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return {}
    result: dict[str, int] = {}
    for name, value in raw.items():
        if isinstance(name, str) and isinstance(value, int):
            result[name] = value
    return result


def _stop_pid(pid: int) -> None:
    try:
        os.kill(pid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError, OSError):
        return


def start(args: argparse.Namespace) -> int:
    """Start requested Brain-5D processes and persist their PIDs."""
    existing = _read_state()
    if existing:
        print("Brain-5D appears to be running. Stop it first.")
        return 2

    processes: dict[str, int] = {}
    python = sys.executable
    if not args.no_simulation:
        processes["simulation"] = _spawn(
            [python, "-m", "src.main", "--config", args.config],
            "simulation.log",
        )
    if not args.no_dashboard:
        command = [
            python,
            "-m",
            "src.dashboard",
            "--host",
            args.host,
            "--port",
            str(args.port),
        ]
        if args.snapshot:
            command.extend(["--snapshot", args.snapshot])
        processes["dashboard"] = _spawn(command, "dashboard.log")

    _write_state(processes)
    dashboard_url = f"http://{args.host}:{args.port}"
    print("Brain-5D started:", processes)
    if "dashboard" in processes:
        print("Dashboard:", dashboard_url)
        if args.open_browser:
            time.sleep(0.5)
            webbrowser.open(dashboard_url)
    return 0


def stop() -> int:
    """Stop only PIDs previously started by this launcher."""
    processes = _read_state()
    if not processes:
        print("No Brain-5D launcher state found.")
        return 0
    for name, pid in processes.items():
        _stop_pid(pid)
        print(f"Stopped {name}: PID {pid}")
    _STATE_FILE.unlink(missing_ok=True)
    return 0


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Brain-5D process launcher")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start")
    start_parser.add_argument("--config", default="configs/poc_config.yaml")
    start_parser.add_argument("--snapshot", default="artifacts/brain5d_snapshot.b5d")
    start_parser.add_argument("--host", default="127.0.0.1")
    start_parser.add_argument("--port", type=int, default=8765)
    start_parser.add_argument("--no-dashboard", action="store_true")
    start_parser.add_argument("--no-simulation", action="store_true")
    start_parser.add_argument("--open-browser", action="store_true")
    subparsers.add_parser("stop")

    args = parser.parse_args()
    if args.command == "start":
        return start(args)
    return stop()


if __name__ == "__main__":
    raise SystemExit(main())
