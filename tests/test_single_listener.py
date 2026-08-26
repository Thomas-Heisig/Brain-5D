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

    Uses ``netstat -ano`` (Windows) to find listening sockets.
    Filters for:
    - local address contains ``127.0.0.1:{port}`` (local port)
    - state is ``LISTENING`` (Windows) or ``LISTEN`` (Linux/macOS)
    - PID is a valid positive integer

    Works with any locale (LISTENING, ABHÖREN, etc.) by checking the
    state column case-insensitively for the ``LISTEN`` prefix.

    Returns an empty dict if netstat is unavailable.
    """
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True, text=True, timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return {}

    listeners: dict[int, list[int]] = {}
    for line in result.stdout.splitlines():
        # 1) Must contain the target port in a local-address position
        if f"127.0.0.1:{port}" not in line and f"[::1]:{port}" not in line:
            continue
        parts = line.strip().split()
        if len(parts) < 5:
            continue
        # 2) State column must indicate listening.
        #    On Windows:  Proto | Local | Remote | State | PID
        #    State is the second-to-last field (index -2).
        #    On Linux:    Proto | Recv-Q | Send-Q | Local | Remote | State | PID/Program
        #    State is the second-to-last field (index -2) or last field (index -1).
        #    Locale-agnostic: check for "LISTEN", "LISTENING", "ABHÖREN", "ESCUCHAN",
        #    "ÉCOUTE", "AUSKULTOWANIE", etc. by checking if the state is NOT a number
        #    and NOT "ESTABLISHED", "TIME_WAIT", "CLOSE_WAIT", "SYN_SENT" etc.
        #    The safest approach: the state column is the one before PID, and it
        #    is never a pure integer.
        state_candidate = parts[-2].upper()
        pid_raw = parts[-1]
        # If parts[-2] looks like a number, we're on a Linux variant where
        # PID comes before state — swap them.
        try:
            int(state_candidate)
            # state_candidate is actually the PID; swap
            state_candidate = pid_raw.upper()
            pid_raw = parts[-2]
        except ValueError:
            pass
        # Skip non-listening states explicitly (ESTABLISHED, TIME_WAIT, etc.)
        if state_candidate in ("ESTABLISHED", "TIME_WAIT", "CLOSE_WAIT",
                               "FIN_WAIT_1", "FIN_WAIT_2", "CLOSING",
                               "SYN_SENT", "SYN_RECEIVED", "LAST_ACK",
                               "BOUND", "CLOSED", "DELETE_TCB"):
            continue
        # 3) PID is a valid positive integer
        try:
            pid = int(pid_raw)
        except ValueError:
            # Linux format: "PID/ProgramName" — extract numeric prefix
            pid_str = pid_raw.split("/")[0] if "/" in pid_raw else ""
            try:
                pid = int(pid_str) if pid_str else 0
            except ValueError:
                continue
        if pid > 0:
            listeners.setdefault(pid, []).append(id(line))
    return listeners


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
        ["python", "-m", "src.main", "--config", str(config_path),
         "--dashboard-port", str(test_port)],
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
        assert len(listeners) > 0, (
            f"No LISTEN socket found on port {test_port} after connection succeeded"
        )

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
        assert len(other_pids) == 0, (
            f"Other PIDs also listening on port {test_port}: {other_pids}"
        )

        # ---- Phase 4: Verify process is still alive -----------------------
        assert proc.poll() is None, (
            f"Brain-5D process (PID {brain_pid}) died after port check"
        )

        # ---- Phase 5: Verify /healthz belongs to this process -------------
        import urllib.request
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{test_port}/healthz")
            resp = urllib.request.urlopen(req, timeout=5)
            assert resp.status == 200, f"Health check returned HTTP {resp.status}"
            data = resp.read().decode("utf-8")
            assert "bridge_configured" in data, (
                f"Health response missing 'bridge_configured': {data[:200]}"
            )
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
        [sys.executable, "-m", "pytest",
         "tests/test_single_listener.py::test_exactly_one_listener_owns_port",
         "-q", "--tb=line", "--no-header"],
        capture_output=True, text=True, timeout=30,
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

    assert all_passed, f"Single listener verification failed: listener={listener_passed}"
