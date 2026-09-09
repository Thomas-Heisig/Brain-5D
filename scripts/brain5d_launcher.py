"""Typed cross-platform launcher for MHRN.

Usage:
    python scripts/brain5d_launcher.py start [options]   # Start simulation
    python scripts/brain5d_launcher.py stop               # Stop all processes
    python scripts/brain5d_launcher.py --help             # Show help

The launcher starts exactly one MHRN application process (src.main),
which owns the simulation, runtime controller, OperatorBridge and dashboard.

Important architecture rule:
    src.main owns the dashboard server. The launcher must therefore NOT start
    ``python -m src.dashboard`` as a second process. Starting a separate
    dashboard process would create a second Python memory space without
    access to the OperatorBridge.
"""

from __future__ import annotations

import argparse
import csv
import os
import signal
import socket
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


def pid_is_running(pid: int) -> bool:
    """Return whether a process with *pid* is currently alive."""
    if os.name == "nt":
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
            capture_output=True,
            timeout=10,
        )
        if result.returncode != 0:
            return False
        output = result.stdout.decode(errors="replace")
        return any(
            len(row) > 1 and row[1].strip() == str(pid)
            for row in csv.reader(output.splitlines())
        )
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def port_is_available(host: str, port: int) -> bool:
    """Return whether a TCP listener can bind to the requested address."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        try:
            probe.bind((host, port))
        except OSError:
            return False
    return True


def spawn(
    command: list[str],
    *,
    cwd: Path = ROOT,
) -> subprocess.Popen[bytes]:
    """Start one MHRN child process with concrete Popen argument types."""
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
    """Build the single MHRN application command.

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
    else:
        command.extend(["--dashboard-host", str(args.host)])
        command.extend(["--dashboard-port", str(args.port)])

    return command


def dashboard_url(args: argparse.Namespace) -> str:
    """Return the dashboard URL used for browser launch."""
    return f"http://{args.host}:{args.port}"


def _lan_address() -> str | None:
    """Return the preferred local IPv4 address without sending network data."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.connect(("8.8.8.8", 80))
            address = str(probe.getsockname()[0])
            if address and not address.startswith("127."):
                return address
    except OSError:
        pass
    try:
        candidates = socket.gethostbyname_ex(socket.gethostname())[2]
    except OSError:
        return None
    return next((item for item in candidates if not item.startswith("127.")), None)


def dashboard_access_urls(host: str, port: int) -> dict[str, str | None]:
    """Build clear local/LAN access URLs for the launcher summary."""
    if host in {"0.0.0.0", "::"}:
        lan_address = _lan_address()
        return {
            "bind": f"{host}:{port}",
            "local": f"http://127.0.0.1:{port}",
            "lan": f"http://{lan_address}:{port}" if lan_address else None,
        }
    return {
        "bind": f"{host}:{port}",
        "local": f"http://{host}:{port}",
        "lan": None,
    }


# ============================================================================
# Subcommand: start
# ============================================================================


def add_start_parser(subparsers: Any) -> None:
    """Add the ``start`` subcommand parser."""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "start",
        help="Start the MHRN simulation",
        description="Start the MHRN simulation with optional dashboard.",
    )
    parser.set_defaults(func=_cmd_start)

    parser.add_argument(
        "--dashboard",
        action="store_true",
        help="Start MHRN with the integrated operator dashboard.",
    )
    parser.add_argument(
        "--open-browser",
        action="store_true",
        help="Open the dashboard in the default browser after startup.",
    )
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"Dashboard bind host (default: {DEFAULT_HOST}; use 0.0.0.0 for LAN).",
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
        help="MHRN configuration file.",
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
        if not args.host.strip():
            print("Error: --host must not be empty", file=sys.stderr)
            return 1

    # Check if already running
    existing_pid = _read_pid()
    if existing_pid is not None:
        if pid_is_running(existing_pid):
            print(
                f"Error: MHRN is already running (PID {existing_pid}).",
                file=sys.stderr,
            )
            return 1
        _remove_pid()

    if args.dashboard and not port_is_available(args.host, args.port):
        print(
            f"Error: dashboard address {args.host}:{args.port} is already in use.",
            file=sys.stderr,
        )
        return 1

    command = build_command(args)
    access = dashboard_access_urls(args.host, args.port) if args.dashboard else None

    print("[MHRN] Launching integrated application")
    print(f"  Config: {args.config}")
    print(f"  Mode: {'dashboard / idle' if args.dashboard else 'headless / automatic'}")
    if access is not None:
        print(
            f"  Dashboard bind: {access['bind']} (all interfaces)"
            if args.host in {"0.0.0.0", "::"}
            else f"  Dashboard bind: {access['bind']}"
        )
        print(f"  Dashboard local: {access['local']}")
        if access["lan"] is not None:
            print(f"  Dashboard LAN: {access['lan']}")
        else:
            print("  Dashboard LAN: unavailable (no non-loopback IPv4 detected)")
        print(f"  Browser: {access['local'] if args.open_browser else 'disabled'}")

    try:
        process = spawn(command)
    except OSError as exc:
        print(
            f"Failed to start MHRN: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 1

    _write_pid(process.pid)
    print(f"MHRN started (PID {process.pid})")
    print(f"  Command: {' '.join(command)}")
    if args.dashboard and args.open_browser:
        browser_url = (
            str(access["local"]) if access is not None else dashboard_url(args)
        )
        try:
            webbrowser.open(browser_url)
        except webbrowser.Error as exc:
            print(f"  Warning: could not open browser: {exc}", file=sys.stderr)

    return 0


# ============================================================================
# Subcommand: stop
# ============================================================================


def add_stop_parser(subparsers: Any) -> None:
    """Add the ``stop`` subcommand parser."""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "stop",
        help="Stop the MHRN simulation",
        description="Stop the running MHRN simulation process.",
    )
    parser.set_defaults(func=_cmd_stop)


def _cmd_stop(_args: argparse.Namespace) -> int:
    """Execute the ``stop`` subcommand."""
    pid = _read_pid()
    if pid is None:
        print("No MHRN process found (no PID file).", file=sys.stderr)
        return 1

    if not pid_is_running(pid):
        print(f"MHRN process {pid} not found (already exited).")
        _remove_pid()
        return 0

    try:
        if os.name == "nt":
            result = subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                timeout=15,
            )
            if result.returncode != 0:
                message = result.stderr.decode(errors="replace").strip()
                raise OSError(message or f"taskkill exited with {result.returncode}")
        else:
            os.kill(pid, signal.SIGTERM)

        print(f"MHRN process {pid} stopped.")
        _remove_pid()
        return 0
    except ProcessLookupError:
        print(f"MHRN process {pid} not found (already exited).")
        _remove_pid()
        return 0
    except OSError as exc:
        print(f"Failed to stop MHRN process {pid}: {exc}", file=sys.stderr)
        return 1


# ============================================================================
# Entry point
# ============================================================================


def main() -> int:
    """Parse arguments and dispatch to the appropriate subcommand."""
    parser = argparse.ArgumentParser(
        description="MHRN application launcher",
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
