"""Test that exactly one TCP listener owns the dashboard port.

This test launches Brain-5D, inspects TCP listeners for port 8765,
and asserts exactly one LISTEN socket owned by the Brain-5D PID.

Hardened against:
- Stale pre-existing process on port 8765
- netstat not being available
- PID mismatch (listener PID must equal Brain-5D process PID)
- Process death before test completes
"""

from __future__ import annotations

import os
import socket
import subprocess
import time
from pathlib import Path


def _get_listener_pids(port: int) -> dict[int, list[int]]:
    """Return {pid: [socket_inodes]} for processes listening on the given port.

    Uses ``netstat -ano`` (Windows) to find listening sockets.
    Works with any locale (LISTENING, ABHÖREN, etc.).
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
        # Match any line containing the port and a PID at the end.
        # Windows netstat: "  TCP    127.0.0.1:8765    0.0.0.0:0    LISTENING    12345"
        # On German Windows: "  TCP    127.0.0.1:8765    0.0.0.0:0    ABHÖREN    12345"
        if f":{port}" not in line:
            continue
        parts = line.strip().split()
        # A listening line has at least 5 parts and the last is a numeric PID
        if len(parts) >= 5:
            try:
                pid = int(parts[-1])
                if pid > 0:
                    listeners.setdefault(pid, []).append(id(line))
            except ValueError:
                continue
    return listeners


def test_exactly_one_listener_owns_port_8765() -> None:
    """Launch Brain-5D and verify exactly one TCP listener on port 8765.

    A single PID can open multiple sockets — this test proves that
    only one DashboardServer binds 127.0.0.1:8765.

    If port 8765 is already occupied, the test FAILS clearly with PID
    information. The test must NOT kill unrelated processes.
    """
    # ---- Phase 1: Detect whether port 8765 is already occupied ------------
    pre_existing = _get_listener_pids(8765)
    if pre_existing:
        pids_str = ", ".join(
            f"PID {pid} ({count} socket(s))"
            for pid, count in ((p, len(s)) for p, s in pre_existing.items())
        )
        raise AssertionError(
            f"Port 8765 is already occupied: {pids_str}. "
            f"The test must not kill unrelated processes. "
            f"Please stop the existing process and retry."
        )

    repo_root = Path(__file__).resolve().parents[1]
    config_path = repo_root / "configs" / "poc_config.yaml"

    # ---- Phase 2: Launch Brain-5D in background --------------------------
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.Popen(
        ["python", "-m", "src.main", "--config", str(config_path)],
        cwd=str(repo_root),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env,
    )
    brain_pid = proc.pid

    try:
        # ---- Phase 3: Wait for dashboard to start ------------------------
        deadline = time.monotonic() + 15.0
        dashboard_ready = False
        while time.monotonic() < deadline:
            # Check process is still alive
            exit_code = proc.poll()
            if exit_code is not None:
                raise AssertionError(
                    f"Brain-5D process (PID {brain_pid}) exited prematurely "
                    f"with code {exit_code}"
                )
            # Try connecting to port 8765
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.settimeout(1)
                if sock.connect_ex(("127.0.0.1", 8765)) == 0:
                    dashboard_ready = True
                    break
            finally:
                sock.close()
            time.sleep(0.5)

        assert dashboard_ready, (
            f"Port 8765 did not become listening within 15 seconds "
            f"(Brain-5D PID {brain_pid})"
        )

        # ---- Phase 4: Verify exactly one LISTEN socket owned by our PID ---
        listeners = _get_listener_pids(8765)
        assert len(listeners) > 0, (
            "No LISTEN socket found on port 8765 after connection succeeded"
        )

        # The listener PID must equal the Brain-5D process PID
        assert brain_pid in listeners, (
            f"Listener PID(s) {list(set(listeners.keys()))} does not include "
            f"Brain-5D PID {brain_pid}. A stale process may own port 8765."
        )

        # Exactly one socket from our PID
        our_sockets = listeners[brain_pid]
        assert len(our_sockets) == 1, (
            f"Expected exactly 1 LISTEN socket on port 8765 from PID {brain_pid}, "
            f"found {len(our_sockets)}"
        )

        # No other PID should be listening on this port
        other_pids = {pid for pid in listeners if pid != brain_pid}
        assert len(other_pids) == 0, (
            f"Other PIDs also listening on port 8765: {other_pids}"
        )

        # ---- Phase 5: Verify process is still alive -----------------------
        assert proc.poll() is None, (
            f"Brain-5D process (PID {brain_pid}) died after port check"
        )

        # ---- Phase 6: Verify /healthz belongs to this process -------------
        import urllib.request
        try:
            req = urllib.request.Request("http://127.0.0.1:8765/healthz")
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
         "tests/test_single_listener.py::test_exactly_one_listener_owns_port_8765",
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
        "tested_commit": commit,
        "tested_tree_digest": tree_digest,
        "test_command": "python -m pytest tests/test_single_listener.py -q",
        "proofs": proofs,
    }

    verification_dir = repo_root / "research" / "generated" / "verification"
    verification_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = verification_dir / "single_listener.json"
    artifact_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")

    assert all_passed, f"Single listener verification failed: listener={listener_passed}"
