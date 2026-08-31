"""Test that exactly one TCP listener owns the dashboard port.

This test launches Brain-5D, inspects TCP listeners for the dashboard port,
and asserts exactly one LISTEN socket owned by the Brain-5D PID.

Uses a dynamically allocated free port so the test never conflicts with
pre-existing processes on port 8765.
"""

from __future__ import annotations

import os
import socket
import subprocess
import time
from pathlib import Path


def _find_free_port() -> int:
    """Find a free TCP port on 127.0.0.1."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]
    finally:
        sock.close()


def _get_listener_pids(port: int) -> dict[int, list[int]]:
    """Return {pid: [socket_inodes]} for processes listening on the given port.

    Platform-specific implementation:
    - **Windows**: Uses ``netstat -ano`` and parses the output.
    - **Linux**: Parses ``/proc/net/tcp`` and ``/proc/net/tcp6``, then
      resolves socket inodes to PIDs via ``/proc/<pid>/fd``.
    - **Other platforms**: Returns an empty dict (unavailable).

    Returns an empty dict if the platform is unsupported or the required
    infrastructure is unavailable.
    """
    import platform as _platform

    system = _platform.system()
    if system == "Windows":
        return _get_listener_pids_windows(port)
    if system == "Linux":
        return _get_listener_pids_linux(port)
    return {}


# ---------------------------------------------------------------------------
# Windows implementation (netstat -ano)
# ---------------------------------------------------------------------------


def _get_listener_pids_windows(port: int) -> dict[int, list[int]]:
    """Windows: parse ``netstat -ano`` for listening sockets on ``port``."""
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return {}

    listeners: dict[int, list[int]] = {}
    for line in result.stdout.splitlines():
        if f"127.0.0.1:{port}" not in line and f"[::1]:{port}" not in line:
            continue
        parts = line.strip().split()
        if len(parts) < 5:
            continue
        state_candidate = parts[-2].upper()
        pid_raw = parts[-1]
        try:
            int(state_candidate)
            state_candidate = pid_raw.upper()
            pid_raw = parts[-2]
        except ValueError:
            pass
        if state_candidate in (
            "ESTABLISHED",
            "TIME_WAIT",
            "CLOSE_WAIT",
            "FIN_WAIT_1",
            "FIN_WAIT_2",
            "CLOSING",
            "SYN_SENT",
            "SYN_RECEIVED",
            "LAST_ACK",
            "BOUND",
            "CLOSED",
            "DELETE_TCB",
        ):
            continue
        try:
            pid = int(pid_raw)
        except ValueError:
            pid_str = pid_raw.split("/")[0] if "/" in pid_raw else ""
            try:
                pid = int(pid_str) if pid_str else 0
            except ValueError:
                continue
        if pid > 0:
            listeners.setdefault(pid, []).append(id(line))
    return listeners


# ---------------------------------------------------------------------------
# Linux implementation (/proc/net/tcp + /proc/<pid>/fd)
# ---------------------------------------------------------------------------

_TCP_STATE_LISTEN = "0A"


def _parse_proc_net_tcp(
    port: int,
    tcp_text: str | None = None,
    tcp6_text: str | None = None,
) -> dict[int, list[str]]:
    """Parse ``/proc/net/tcp`` and ``/proc/net/tcp6`` for listening sockets.

    Returns ``{inode: [local_addresses]}`` for sockets in LISTEN state
    on the requested ``port``.

    For testing, pass ``tcp_text`` and/or ``tcp6_text`` directly instead of
    reading from ``/proc``.
    """
    import pathlib

    sources: list[tuple[str | None, str]] = [
        (tcp_text, str(pathlib.Path("/proc/net/tcp"))),
        (tcp6_text, str(pathlib.Path("/proc/net/tcp6"))),
    ]
    result: dict[int, list[str]] = {}
    for content_override, proc_path_str in sources:
        proc_path = pathlib.Path(proc_path_str)
        if content_override is not None:
            text = content_override
        elif proc_path.exists():
            text = proc_path.read_text(encoding="ascii", errors="replace")
        else:
            continue
        for line in text.splitlines()[1:]:  # skip header
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) < 10:
                continue
            # parts[1] = local_address in hex format "XXXXXX:PORT"
            local_addr = parts[1]
            # parts[3] = state (hex)
            state = parts[3]
            # parts[9] = inode
            inode_str = parts[9]
            if state != _TCP_STATE_LISTEN:
                continue
            try:
                inode = int(inode_str)
            except ValueError:
                continue
            # local port is after the colon in hex
            if ":" not in local_addr:
                continue
            hex_port = local_addr.split(":")[1]
            try:
                line_port = int(hex_port, 16)
            except ValueError:
                continue
            if line_port == port:
                result.setdefault(inode, []).append(local_addr)
    return result


def _resolve_inode_to_pid(inode: int, brain_pid: int | None = None) -> int | None:
    """Resolve a socket inode to a PID by scanning ``/proc/<pid>/fd``.

    If ``brain_pid`` is provided, it is checked first (fast path).
    Returns the matching PID, or ``None`` if no process owns the inode.
    """
    import pathlib

    proc = pathlib.Path("/proc")
    candidates: list[int] = []
    if brain_pid is not None:
        candidates.append(brain_pid)
    # Only scan other PIDs if brain_pid didn't match
    for entry in proc.iterdir():
        if not entry.name.isdigit():
            continue
        pid_candidate = int(entry.name)
        if pid_candidate == brain_pid:
            continue
        if pid_candidate not in candidates:
            candidates.append(pid_candidate)
    for pid in candidates:
        fd_dir = proc / str(pid) / "fd"
        if not fd_dir.is_dir():
            continue
        try:
            for fd_entry in fd_dir.iterdir():
                try:
                    link: str = fd_entry.readlink()  # type: ignore[assignment]
                except OSError:
                    continue
                # socket:[INODE]
                if link == f"socket:[{inode}]":
                    return pid
        except PermissionError:
            continue
    return None


def _get_listener_pids_linux(port: int) -> dict[int, list[int]]:
    """Linux: parse ``/proc/net/tcp`` and resolve inodes to PIDs.

    Returns ``{pid: [inode]}`` for all processes listening on ``port``.
    """
    inode_map = _parse_proc_net_tcp(port)
    if not inode_map:
        return {}
    result: dict[int, list[int]] = {}
    for inode in inode_map:
        pid = _resolve_inode_to_pid(inode)
        if pid is not None:
            result.setdefault(pid, []).append(inode)
    return result


def test_exactly_one_listener_owns_port() -> None:
    """Launch Brain-5D and verify exactly one TCP listener on the dashboard port.

    Uses a dynamically allocated port to avoid conflicts. Verifies:
    - exactly one LISTEN socket
    - listener PID == launched Brain-5D PID
    - process remains alive
    - no other PID listens on the same port
    - /healthz answers from the launched runtime
    """
    test_port = _find_free_port()

    repo_root = Path(__file__).resolve().parents[1]
    config_path = repo_root / "configs" / "poc_config.yaml"

    # ---- Phase 1: Launch Brain-5D in background with test port -----------
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.Popen(
        [
            "python",
            "-m",
            "src.main",
            "--config",
            str(config_path),
            "--dashboard-port",
            str(test_port),
        ],
        cwd=str(repo_root),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env,
    )
    brain_pid = proc.pid

    try:
        # ---- Phase 2: Wait for dashboard to start ------------------------
        deadline = time.monotonic() + 15.0
        dashboard_ready = False
        while time.monotonic() < deadline:
            exit_code = proc.poll()
            if exit_code is not None:
                raise AssertionError(
                    f"Brain-5D process (PID {brain_pid}) exited prematurely "
                    f"with code {exit_code}"
                )
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.settimeout(1)
                if sock.connect_ex(("127.0.0.1", test_port)) == 0:
                    dashboard_ready = True
                    break
            finally:
                sock.close()
            time.sleep(0.5)

        assert dashboard_ready, (
            f"Port {test_port} did not become listening within 15 seconds "
            f"(Brain-5D PID {brain_pid})"
        )

        # ---- Phase 3: Verify exactly one LISTEN socket owned by our PID ---
        listeners = _get_listener_pids(test_port)
        assert (
            len(listeners) > 0
        ), f"No LISTEN socket found on port {test_port} after connection succeeded"

        assert brain_pid in listeners, (
            f"Listener PID(s) {list(set(listeners.keys()))} does not include "
            f"Brain-5D PID {brain_pid}"
        )

        our_sockets = listeners[brain_pid]
        assert len(our_sockets) == 1, (
            f"Expected exactly 1 LISTEN socket on port {test_port} from PID {brain_pid}, "
            f"found {len(our_sockets)}"
        )

        other_pids = {pid for pid in listeners if pid != brain_pid}
        assert (
            len(other_pids) == 0
        ), f"Other PIDs also listening on port {test_port}: {other_pids}"

        # ---- Phase 4: Verify process is still alive -----------------------
        assert (
            proc.poll() is None
        ), f"Brain-5D process (PID {brain_pid}) died after port check"

        # ---- Phase 5: Verify /healthz belongs to this process -------------
        import urllib.request

        try:
            req = urllib.request.Request(f"http://127.0.0.1:{test_port}/healthz")
            resp = urllib.request.urlopen(req, timeout=5)
            assert resp.status == 200, f"Health check returned HTTP {resp.status}"
            data = resp.read().decode("utf-8")
            assert (
                "bridge_configured" in data
            ), f"Health response missing 'bridge_configured': {data[:200]}"
        except Exception as e:
            raise AssertionError(f"Dashboard health check failed: {e}")

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=3)


# =========================================================================
# Verification artifact writer for single listener
# =========================================================================


def test_write_single_listener_verification_artifact() -> None:
    """Write a machine-readable single listener verification artifact.

    The artifact is written to
    ``research/generated/verification/single_listener.json``
    (persistent, not gitignored) so GateStatusBuilder can verify the
    single listener ownership proof independently from the structural
    live loop.

    Proof IDs match REQUIRED_SINGLE_LISTENER_PROOFS in gate_status.py.
    """
    import json
    import platform
    import sys
    from datetime import datetime

    repo_root = Path(__file__).resolve().parents[1]

    # Run the single listener test via pytest subprocess
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_single_listener.py::test_exactly_one_listener_owns_port",
            "-q",
            "--tb=line",
            "--no-header",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(repo_root),
    )
    listener_passed = result.returncode == 0

    from src.dashboard.verification import compute_source_tree_digest, current_git_head

    tree_digest = compute_source_tree_digest(repo_root)
    commit = current_git_head(repo_root)

    proofs = {
        "port_initially_free_or_explicitly_rejected": listener_passed,
        "brain5d_process_started": listener_passed,
        "listener_pid_matches_process_pid": listener_passed,
        "exactly_one_listener_socket": listener_passed,
        "no_other_listener_pid": listener_passed,
        "healthz_reachable": listener_passed,
        "process_alive_during_verification": listener_passed,
    }

    all_passed = all(proofs.values())

    artifact = {
        "schema_version": 1,
        "suite": "single_listener",
        "status": "verified" if all_passed else "failed",
        "timestamp": datetime.now().isoformat(),
        "python_version": platform.python_version(),
        "test_run_head": commit,
        "tested_tree_digest": tree_digest,
        "test_command": "python -m pytest tests/test_single_listener.py -q",
        "proofs": proofs,
    }

    verification_dir = repo_root / "research" / "generated" / "verification"
    verification_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = verification_dir / "single_listener.json"
    artifact_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")

    assert (
        all_passed
    ), f"Single listener verification failed: listener={listener_passed}"
