"""API contract tests for the Brain-5D dashboard control endpoints.

Tests every runtime command through the full HTTP dispatch path:
- Canonical contract: POST /api/control { "command": "...", ... }
- Legacy contract: POST /api/control { "action": "...", ... }
- Validation: missing fields, invalid types, unsupported commands
- Error responses: structured JSON errors with appropriate HTTP status codes
"""

from __future__ import annotations

import json
from http.client import HTTPConnection
from threading import Thread
from typing import Any, cast

import pytest

from src.dashboard.models import JSONValue
from src.dashboard.operator_bridge import OperatorBridge
from src.dashboard.server import DashboardServer
from src.dashboard.state import DashboardStateStore
from src.dashboard.structural_api import JSONMapping, StructuralCommandResult

# ============================================================================
# Stubs
# ============================================================================


class _StubController:
    """Minimal controller stub for testing the HTTP dispatch layer."""

    def __init__(self) -> None:
        self._tick = 0

    @property
    def telemetry(self) -> object:
        return type(
            "TelemetryStub",
            (),
            {
                "controller_state": "idle",
                "tick": self._tick,
                "neurons": 100,
                "synapses": 500,
                "queue_depth": 0,
                "spikes_this_batch": 0,
                "ticks_per_second": 0.0,
                "batch_duration_ms": 0.0,
                "requested_ticks": 0,
                "completed_ticks": 0,
                "last_error": None,
            },
        )()

    def snapshot(self) -> object:
        tick = self._tick
        return type(
            "SnapshotStub",
            (),
            {
                "to_json": lambda _self=None, tick=tick: {  # type: ignore[assignment]
                    "mode": "idle",
                    "tick": tick,
                    "queued_ticks": 0,
                    "loop_size": 100,
                    "delay_ms": 0.0,
                    "last_batch_ticks": 0,
                    "last_batch_ms": 0.0,
                    "total_runtime_ms": 0.0,
                    "fault": None,
                    "can_snapshot": False,
                }
            },
        )()

    def step(self, ticks: int = 1) -> object:
        self._tick += ticks
        return self.snapshot()

    def run_ticks(self, ticks: int) -> object:
        self._tick += ticks
        return self.snapshot()

    def start(self) -> object:
        return self.snapshot()

    def run(self, *, loop_size: int | None = None) -> object:
        return self.snapshot()

    def pause(self) -> object:
        return self.snapshot()

    def stop(self) -> object:
        return self.snapshot()

    def configure(self, **kwargs: Any) -> object:
        return self.snapshot()

    def request_snapshot(self) -> object:
        return self.snapshot()


class _Bridge:
    """Minimal bridge stub for server startup."""

    def __init__(self) -> None:
        self.controller = _StubController()

    def structural_status(self) -> JSONMapping:
        return {"configured": True}

    def structural_proposals(self) -> list[JSONMapping]:
        return []

    def structural_history(self, _limit: int) -> list[JSONMapping]:
        return []

    def structural_heatmap(self, kind: str) -> JSONMapping:
        return {"kind": kind, "values": []}

    def structural_config(self) -> JSONMapping:
        return {"configured": True}

    def approve_structural(self, _proposal_id: str) -> StructuralCommandResult:
        return StructuralCommandResult(True, "approved")

    def reject_structural(self, _proposal_id: str) -> StructuralCommandResult:
        return StructuralCommandResult(True, "rejected")

    def undo_structural(self) -> StructuralCommandResult:
        return StructuralCommandResult(True, "undone")

    def set_auto_approval(self, enabled: bool) -> StructuralCommandResult:
        return StructuralCommandResult(True, str(enabled))

    def run_ticks(self, count: int) -> StructuralCommandResult:
        return StructuralCommandResult(True, str(count))

    def single_step(self) -> StructuralCommandResult:
        return StructuralCommandResult(True, "one")

    def request_snapshot(self) -> StructuralCommandResult:
        return StructuralCommandResult(True, "snapshot")

    def command(self, command: str, **_kwargs: Any) -> dict[str, JSONValue]:
        return {"ok": True, "status": command}

    def update_structural_config(self, **_body: Any) -> StructuralCommandResult:
        return StructuralCommandResult(True, "updated")


# ============================================================================
# Test helpers
# ============================================================================


@pytest.fixture(scope="module")
def server_and_client() -> tuple[DashboardServer, Thread, str, int]:
    """Start a dashboard server with a stub bridge for testing."""
    bridge = _Bridge()
    server = DashboardServer(
        ("127.0.0.1", 0),
        DashboardStateStore(),
        None,
        cast(OperatorBridge | None, bridge),
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    if not isinstance(host, str):
        raise AssertionError("server address is not a string")
    return server, thread, host, port


def _post(
    host: str, port: int, path: str, body: object
) -> tuple[int, dict[str, JSONValue] | str]:
    """Send a POST request and return (status, parsed_body)."""
    conn = HTTPConnection(host, port)
    try:
        conn.request(
            "POST",
            path,
            json.dumps(body),
            {"Content-Type": "application/json"},
        )
        resp = conn.getresponse()
        data = resp.read()
        ct = resp.getheader("Content-Type", "")
        if "application/json" in ct:
            return resp.status, json.loads(data)
        return resp.status, data.decode("utf-8", errors="replace")
    finally:
        conn.close()


def _get(host: str, port: int, path: str) -> tuple[int, dict[str, JSONValue] | str]:
    """Send a GET request and return (status, parsed_body)."""
    conn = HTTPConnection(host, port)
    try:
        conn.request("GET", path)
        resp = conn.getresponse()
        data = resp.read()
        ct = resp.getheader("Content-Type", "")
        if "application/json" in ct:
            return resp.status, json.loads(data)
        return resp.status, data.decode("utf-8", errors="replace")
    finally:
        conn.close()


# ============================================================================
# Canonical Contract Tests
# ============================================================================


@pytest.mark.smoke
class TestCanonicalContract:
    """Test the canonical { "command": "...", ... } contract."""

    def test_run_ticks_command(
        self, server_and_client: tuple[DashboardServer, Thread, str, int]
    ) -> None:
        _, _, host, port = server_and_client
        status, body = _post(
            host, port, "/api/control", {"command": "run_ticks", "ticks": 10}
        )
        assert status == 200
        assert isinstance(body, dict)
        assert body.get("ok") is True

    def test_step_command(
        self, server_and_client: tuple[DashboardServer, Thread, str, int]
    ) -> None:
        _, _, host, port = server_and_client
        status, body = _post(
            host, port, "/api/control", {"command": "step", "ticks": 1}
        )
        assert status == 200
        assert isinstance(body, dict)
        assert body.get("ok") is True

    def test_pause_command(
        self, server_and_client: tuple[DashboardServer, Thread, str, int]
    ) -> None:
        _, _, host, port = server_and_client
        status, body = _post(host, port, "/api/control", {"command": "pause"})
        assert status == 200
        assert isinstance(body, dict)
        assert body.get("ok") is True

    def test_stop_command(
        self, server_and_client: tuple[DashboardServer, Thread, str, int]
    ) -> None:
        _, _, host, port = server_and_client
        status, body = _post(host, port, "/api/control", {"command": "stop"})
        assert status == 200
        assert isinstance(body, dict)
        assert body.get("ok") is True

    def test_snapshot_command(
        self, server_and_client: tuple[DashboardServer, Thread, str, int]
    ) -> None:
        _, _, host, port = server_and_client
        status, body = _post(host, port, "/api/control", {"command": "snapshot"})
        assert status == 200
        assert isinstance(body, dict)
        assert body.get("ok") is True

    def test_start_command(
        self, server_and_client: tuple[DashboardServer, Thread, str, int]
    ) -> None:
        _, _, host, port = server_and_client
        status, body = _post(host, port, "/api/control", {"command": "start"})
        assert status == 200
        assert isinstance(body, dict)
        assert body.get("ok") is True

    def test_resume_command(
        self, server_and_client: tuple[DashboardServer, Thread, str, int]
    ) -> None:
        _, _, host, port = server_and_client
        status, body = _post(host, port, "/api/control", {"command": "resume"})
        assert status == 200
        assert isinstance(body, dict)
        assert body.get("ok") is True

    def test_configure_command(
        self, server_and_client: tuple[DashboardServer, Thread, str, int]
    ) -> None:
        _, _, host, port = server_and_client
        status, body = _post(
            host,
            port,
            "/api/control",
            {"command": "configure", "loop_size": 50, "delay_ms": 1.0},
        )
        assert status == 200
        assert isinstance(body, dict)
        assert body.get("ok") is True

    def test_single_step_command(
        self, server_and_client: tuple[DashboardServer, Thread, str, int]
    ) -> None:
        _, _, host, port = server_and_client
        status, body = _post(host, port, "/api/control", {"command": "single_step"})
        assert status == 200
        assert isinstance(body, dict)
        assert body.get("ok") is True


# ============================================================================
# Legacy Contract Tests
# ============================================================================


@pytest.mark.smoke
class TestLegacyContract:
    """Test the legacy { "action": "...", ... } contract still works."""

    def test_legacy_step_action(
        self, server_and_client: tuple[DashboardServer, Thread, str, int]
    ) -> None:
        _, _, host, port = server_and_client
        status, body = _post(host, port, "/api/control", {"action": "step", "ticks": 1})
        assert status == 200
        assert isinstance(body, dict)
        assert body.get("ok") is True

    def test_legacy_run_ticks_action(
        self, server_and_client: tuple[DashboardServer, Thread, str, int]
    ) -> None:
        _, _, host, port = server_and_client
        status, body = _post(
            host, port, "/api/control", {"action": "run_ticks", "ticks": 10}
        )
        assert status == 200
        assert isinstance(body, dict)
        assert body.get("ok") is True

    def test_legacy_pause_action(
        self, server_and_client: tuple[DashboardServer, Thread, str, int]
    ) -> None:
        _, _, host, port = server_and_client
        status, body = _post(host, port, "/api/control", {"action": "pause"})
        assert status == 200
        assert isinstance(body, dict)
        assert body.get("ok") is True

    def test_legacy_stop_action(
        self, server_and_client: tuple[DashboardServer, Thread, str, int]
    ) -> None:
        _, _, host, port = server_and_client
        status, body = _post(host, port, "/api/control", {"action": "stop"})
        assert status == 200
        assert isinstance(body, dict)
        assert body.get("ok") is True


# ============================================================================
# Validation Tests
# ============================================================================


@pytest.mark.smoke
class TestValidation:
    """Test input validation and error responses."""

    def test_missing_command_returns_400(
        self, server_and_client: tuple[DashboardServer, Thread, str, int]
    ) -> None:
        _, _, host, port = server_and_client
        status, body = _post(host, port, "/api/control", {})
        assert status == 400
        assert isinstance(body, dict)
        assert "error" in body

    def test_unknown_command_returns_400(
        self, server_and_client: tuple[DashboardServer, Thread, str, int]
    ) -> None:
        _, _, host, port = server_and_client
        status, body = _post(host, port, "/api/control", {"command": "warp-core"})
        assert status == 400
        assert isinstance(body, dict)
        assert "error" in body

    def test_non_dict_body_returns_400(
        self, server_and_client: tuple[DashboardServer, Thread, str, int]
    ) -> None:
        _, _, host, port = server_and_client
        status, body = _post(host, port, "/api/control", ["not", "a", "dict"])
        assert status == 400
        assert isinstance(body, dict)
        assert "error" in body

    def test_invalid_ticks_type_returns_400(
        self, server_and_client: tuple[DashboardServer, Thread, str, int]
    ) -> None:
        _, _, host, port = server_and_client
        status, body = _post(
            host,
            port,
            "/api/control",
            {"command": "run_ticks", "ticks": "not-a-number"},
        )
        assert status == 400
        assert isinstance(body, dict)
        assert "error" in body

    def test_unsupported_content_type_returns_415(
        self, server_and_client: tuple[DashboardServer, Thread, str, int]
    ) -> None:
        _, _, host, port = server_and_client
        conn = HTTPConnection(host, port)
        try:
            conn.request(
                "POST",
                "/api/control",
                '{"command": "pause"}',
                {"Content-Type": "text/plain"},
            )
            resp = conn.getresponse()
            _data = resp.read()
            assert resp.status in (400, 415)
        finally:
            conn.close()


# ============================================================================
# GET /api/control (status) Tests
# ============================================================================


@pytest.mark.smoke
class TestControlStatus:
    """Test the GET /api/control status endpoint."""

    def test_get_control_status_returns_200(
        self, server_and_client: tuple[DashboardServer, Thread, str, int]
    ) -> None:
        _, _, host, port = server_and_client
        conn = HTTPConnection(host, port)
        try:
            conn.request("GET", "/api/control")
            resp = conn.getresponse()
            data = resp.read()
            assert resp.status == 200
            ct = resp.getheader("Content-Type", "")
            assert "application/json" in ct
            body = json.loads(data)
            assert isinstance(body, dict)
            assert "state" in body
        finally:
            conn.close()


class TestUnknownApiRoutes:
    """Unknown API routes remain JSON errors instead of SPA fallbacks."""

    def test_unknown_get_route_returns_json_404(
        self, server_and_client: tuple[DashboardServer, Thread, str, int]
    ) -> None:
        _, _, host, port = server_and_client
        status, body = _get(host, port, "/api/does-not-exist")
        assert status == 404
        assert isinstance(body, dict)
        assert body["error"] == "Unknown API endpoint: /api/does-not-exist"

    def test_unknown_post_route_returns_json_404(
        self, server_and_client: tuple[DashboardServer, Thread, str, int]
    ) -> None:
        _, _, host, port = server_and_client
        status, body = _post(host, port, "/api/does-not-exist", {})
        assert status == 404
        assert isinstance(body, dict)
        assert body["error"] == "Unknown API endpoint: /api/does-not-exist"
