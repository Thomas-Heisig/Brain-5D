"""Typed cross-platform launcher for Brain-5D.

The launcher starts exactly one Brain-5D application process.

Important architecture rule:
    src.main owns the simulation, runtime controller, OperatorBridge and
    dashboard server. The launcher must therefore NOT start
    ``python -m src.dashboard`` as a second process.

Starting a separate dashboard process would create a second Python memory
space without access to the OperatorBridge created by src.main. This caused
the runtime error:

    Structural operator bridge is not configured.

The launcher is intentionally type-safe and avoids passing loosely typed
``dict[str, object]`` values through ``subprocess.Popen``.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


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


def parse_args() -> argparse.Namespace:
    """Parse launcher command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Brain-5D application launcher",
    )

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

    args = parser.parse_args()

    if args.port < 1 or args.port > 65535:
        parser.error("--port must be in the range 1..65535")

    if args.ticks is not None and args.ticks < 1:
        parser.error("--ticks must be greater than zero")

    if args.open_browser and not args.dashboard:
        parser.error("--open-browser requires --dashboard")

    # src.main currently owns the dashboard binding and uses
    # 127.0.0.1:8765 internally. Prevent misleading launcher arguments
    # until host/port have been moved into the application composition root.
    if args.dashboard:
        if args.host != DEFAULT_HOST:
            parser.error(
                f"Integrated dashboard currently requires --host {DEFAULT_HOST}"
            )
        if args.port != DEFAULT_PORT:
            parser.error(
                f"Integrated dashboard currently requires --port {DEFAULT_PORT}"
            )

    return args


def main() -> int:
    """Start Brain-5D and return immediately after successful process creation."""
    args = parse_args()

    command = build_command(args)

    try:
        process = spawn(command)
    except OSError as exc:
        print(
            f"Failed to start Brain-5D: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 1

    print(f"Brain-5D process started: {process.pid}")
    print(f"Command: {' '.join(command)}")

    if args.dashboard:
        print(f"Dashboard: {dashboard_url(args)}")

    if args.dashboard and args.open_browser:
        try:
            webbrowser.open(dashboard_url(args))
        except webbrowser.Error as exc:
            print(
                f"Warning: dashboard started, but browser could not be opened: {exc}",
                file=sys.stderr,
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
