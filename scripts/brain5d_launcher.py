"""Typed cross-platform launcher helper.

Avoids passing dict[str, object] through **kwargs to subprocess.Popen, which
is the source of the Pylance overload explosion seen in error.log.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def spawn(command: list[str], *, cwd: Path = ROOT) -> subprocess.Popen[bytes]:
    """Start one Brain-5D process with concrete Popen argument types."""
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


def build_commands(args: argparse.Namespace) -> list[list[str]]:
    """Build child commands without forwarding launcher-only arguments."""
    simulation_command = [
        sys.executable,
        "-m",
        "src.main",
        "--config",
        str(args.config),
    ]
    if args.observe:
        simulation_command.append("--observe")

    commands = [simulation_command]
    if args.dashboard:
        commands.append(
            [
                sys.executable,
                "-m",
                "src.dashboard",
                "--host",
                args.host,
                "--port",
                str(args.port),
            ]
        )
    return commands


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dashboard", action="store_true")
    parser.add_argument("--open-browser", action="store_true")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--config", type=Path, default=Path("configs/poc_config.yaml"))
    parser.add_argument("--observe", action="store_true")
    args = parser.parse_args()

    processes = [spawn(command) for command in build_commands(args)]
    if args.dashboard and args.open_browser:
        webbrowser.open(f"http://{args.host}:{args.port}")
    print("Brain-5D processes started:", ", ".join(str(p.pid) for p in processes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
