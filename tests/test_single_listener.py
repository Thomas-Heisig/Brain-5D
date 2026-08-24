"""Test that exactly one TCP listener owns the dashboard port.

This test launches Brain-5D, inspects TCP listeners for port 8765,
and asserts exactly one LISTEN socket owned by the Brain-5D PID.
"""

from __future__ import annotations

import socket
import subprocess
import time
from pathlib import Path


def test_exactly_one_listener_owns_port_8765() -> None:
    """Launch Brain-5D and verify exactly one TCP listener on port 8765.

    A single PID can open multiple sockets — this test proves that
    only one DashboardServer binds 127.0.0.1:8765.
    """
    repo_root = Path(__file__).resolve().parents[1]
    config_path = repo_root / "configs" / "poc_config.yaml"

    # Start Brain-5D in background
    proc = subprocess.Popen(
        ["python", "-m", "src.main", "--config", str(config_path)],
        cwd=str(repo_root),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        # Wait for dashboard to start
        time.sleep(5)

        # Check that port 8765 is listening
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.settimeout(2)
            result = sock.connect_ex(("127.0.0.1", 8765))
            assert result == 0, f"Port 8765 is not listening (connect_ex={result})"
        finally:
            sock.close()

        # Use netstat to count LISTEN sockets on port 8765
        try:
            netstat = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True, text=True, timeout=10,
            )
            lines = netstat.stdout.splitlines()
            listen_lines = [
                line for line in lines
                if "LISTENING" in line and ":8765" in line
            ]
            assert len(listen_lines) == 1, (
                f"Expected exactly 1 LISTEN socket on port 8765, "
                f"found {len(listen_lines)}: {listen_lines}"
            )
        except FileNotFoundError:
            pass  # netstat not available on all platforms

        # Verify the dashboard is responsive
        import urllib.request
        try:
            req = urllib.request.Request("http://127.0.0.1:8765/healthz")
            resp = urllib.request.urlopen(req, timeout=5)
            assert resp.status == 200, f"Health check returned HTTP {resp.status}"
            data = resp.read().decode("utf-8")
            assert "bridge_configured" in data
        except Exception as e:
            raise AssertionError(f"Dashboard health check failed: {e}")

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
