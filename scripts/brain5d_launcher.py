"""Typed cross-platform launcher for Brain-5D.

Usage:
    python scripts/brain5d_launcher.py start [options]   # Start simulation
    python scripts/brain5d_launcher.py stop               # Stop all processes
    python scripts/brain5d_launcher.py --help             # Show help

The launcher starts exactly one Brain-5D application process (src.main),
which owns the simulation, runtime controller, OperatorBridge and dashboard.

Important architecture rule:
    src.main owns the dashboard server. The launcher must therefore NOT start
    ``python -m src.dashboard`` as a second process. Starting a separate
    dashboard process would create a second Python memory space without
    access to the OperatorBridge.
"""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import webbrowser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
PID_FILE = ROOT / "artifacts" / "brain5d.pid"


# ============================================================================
# Helpers
# ============================================================================


def _ensure_artifacts_dir() -> None:
    """Ensure the artifacts directory exists for PID file."""
    (ROOT / "artifacts").mkdir(parents=True, exist_ok=True)


def _read_pid() -> int | None:
    """Read the stored PID, or return None if no PID file exists."""
    pid_path = PID_FILE
    if not pid_path.exists():
        return None
    try:
        return int(pid_path.read_text(encoding="utf-8").strip())
    except (ValueError, OSError):
        return None


def _write_pid(pid: int) -> None:
    """Write the PID file."""
    _ensure_artifacts_dir()
    PID_FILE.write_text(str(pid), encoding="utf-8")


def _remove_pid() -> None:
    """Remove the PID file."""
    try:
        PID_FILE.unlink(missing_ok=True)
    except OSError:
        pass


def spawn(
    command: list[str],
    *,
    cwd: Path = ROOT,
) -> subprocess.Popen[bytes]:
    """Start one Brain-5D child process with concrete Popen argument types."""
    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

    return subprocess.Popen(
        command,
        cwd=str(cwd),
        stdin=subprocess.DEVNULL,
        stdout=None,
        stderr=None,
        shell=False,
        creationflags=creationflags,
    )


def build_command(args: argparse.Namespace) -> list[str]:
    """Build the single Brain-5D application command.

    ``src.main`` is the application composition root. It owns:

    - NeuralNetwork
    - learning engine
    - homeostasis engine
    - runtime/controller integration
    - OperatorBridge
    - dashboard state
    - dashboard HTTP server

    Therefore no independent dashboard process is started here.
    """
    command = [
        sys.executable,
        "-m",
        "src.main",
        "--config",
        str(args.config),
    ]

    if args.observe:
        command.append("--observe")

    if args.benchmark:
        command.append("--benchmark")

    if args.no_learning:
        command.append("--no-learning")

    if args.no_homeostasis:
        command.append("--no-homeostasis")

    if args.ticks is not None:
        command.extend(["--ticks", str(args.ticks)])

    # src.main starts its integrated dashboard by default.
    # Only explicitly disable it when --dashboard was not requested.
    if not args.dashboard:
        command.append("--no-dashboard")

    return command


def dashboard_url(args: argparse.Namespace) -> str:
    """Return the dashboard URL used for browser launch."""
    return f"http://{args.host}:{args.port}"


# ============================================================================
# Subcommand: start
# ============================================================================


def add_start_parser(subparsers: Any) -> None:
    """Add the ``start`` subcommand parser."""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "start",
        help="Start the Brain-5D simulation",
        description="Start the Brain-5D simulation with optional dashboard.",
    )
    parser.set_defaults(func=_cmd_start)

    parser.add_argument(
        "--dashboard",
        action="store_true",
        help="Start Brain-5D with the integrated operator dashboard.",
    )
    parser.add_argument(
        "--open-browser",
        action="store_true",
        help="Open the dashboard in the default browser after startup.",
    )
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"Dashboard host for browser URL (default: {DEFAULT_HOST}).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Dashboard port for browser URL (default: {DEFAULT_PORT}).",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/poc_config.yaml"),
        help="Brain-5D configuration file.",
    )
    parser.add_argument(
        "--observe",
        action="store_true",
        help="Enable the observatory.",
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Enable runtime benchmarking.",
    )
    parser.add_argument(
        "--no-learning",
        action="store_true",
        help="Disable the learning engine.",
    )
    parser.add_argument(
        "--no-homeostasis",
        action="store_true",
        help="Disable the homeostasis engine.",
    )
    parser.add_argument(
        "--ticks",
        type=int,
        default=None,
        help="Override the configured simulation tick count.",
    )


def _cmd_start(args: argparse.Namespace) -> int:
    """Execute the ``start`` subcommand."""
    # Validate
    if args.port < 1 or args.port > 65535:
        print("Error: --port must be in the range 1..65535", file=sys.stderr)
        return 1

    if args.ticks is not None and args.ticks < 1:
        print("Error: --ticks must be greater than zero", file=sys.stderr)
        return 1

    if args.open_browser and not args.dashboard:
        print("Error: --open-browser requires --dashboard", file=sys.stderr)
        return 1

    if args.dashboard:
        if args.host != DEFAULT_HOST:
            print(
                f"Error: Integrated dashboard currently requires --host {DEFAULT_HOST}",
                file=sys.stderr,
            )
            return 1
        if args.port != DEFAULT_PORT:
            print(
                f"Error: Integrated dashboard currently requires --port {DEFAULT_PORT}",
                file=sys.stderr,
            )
            return 1

    # Check if already running
    existing_pid = _read_pid()
    if existing_pid is not None:
        print(
            f"Warning: Brain-5D may already be running (PID {existing_pid}).",
            file=sys.stderr,
        )
        print("Use 'stop' first or remove the PID file.", file=sys.stderr)

    command = build_command(args)

    try:
        process = spawn(command)
    except OSError as exc:
        print(
            f"Failed to start Brain-5D: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 1

    _write_pid(process.pid)
    print(f"Brain-5D started (PID {process.pid})")
    print(f"  Command: {' '.join(command)}")

    if args.dashboard:
        url = dashboard_url(args)
        print(f"  Dashboard: {url}")
        if args.open_browser:
            try:
                webbrowser.open(url)
            except webbrowser.Error as exc:
                print(
                    f"  Warning: could not open browser: {exc}",
                    file=sys.stderr,
                )

    return 0


# ============================================================================
# Subcommand: stop
# ============================================================================


def add_stop_parser(subparsers: Any) -> None:
    """Add the ``stop`` subcommand parser."""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "stop",
        help="Stop the Brain-5D simulation",
        description="Stop the running Brain-5D simulation process.",
    )
    parser.set_defaults(func=_cmd_stop)


def _cmd_stop(_args: argparse.Namespace) -> int:
    """Execute the ``stop`` subcommand."""
    pid = _read_pid()
    if pid is None:
        print("No Brain-5D process found (no PID file).", file=sys.stderr)
        return 1

    try:
        if os.name == "nt":
            os.kill(pid, signal.CTRL_BREAK_EVENT)  # type: ignore[attr-defined]
        else:
            os.kill(pid, signal.SIGTERM)

        print(f"Brain-5D process {pid} stopped.")
        _remove_pid()
        return 0
    except ProcessLookupError:
        print(f"Brain-5D process {pid} not found (already exited).")
        _remove_pid()
        return 0
    except OSError as exc:
        print(f"Failed to stop Brain-5D process {pid}: {exc}", file=sys.stderr)
        return 1


# ============================================================================
# Entry point
# ============================================================================


def main() -> int:
    """Parse arguments and dispatch to the appropriate subcommand."""
    parser = argparse.ArgumentParser(
        description="Brain-5D application launcher",
    )
    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
        description="Available commands. Use 'start' to run, 'stop' to terminate.",
    )

    add_start_parser(subparsers)
    add_stop_parser(subparsers)

    # Default: if no subcommand given, show help
    if len(sys.argv) < 2:
        parser.print_help()
        return 0

    args = parser.parse_args()

    if hasattr(args, "func"):
        return args.func(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
