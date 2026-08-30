"""Tests for the dashboard experiment-mode workflow."""

from __future__ import annotations

import json
import threading
import time
from http import HTTPStatus
from http.client import HTTPConnection

import pytest

from src.dashboard.models import DashboardSnapshot
from src.dashboard.server import DashboardServer
from src.dashboard.state import DashboardStateStore


@pytest.fixture
def state() -> DashboardStateStore:
    """Create an empty dashboard state store."""
    return DashboardStateStore(initial=DashboardSnapshot())


@pytest.fixture
def server(state: DashboardStateStore) -> DashboardServer:
    """Create a dashboard server on a free port."""
    srv = DashboardServer(("127.0.0.1", 0), state, heatmaps=None)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.05)
    yield srv
    srv.shutdown()


def _request(
    server: DashboardServer,
    method: str,
    path: str,
    body: dict | None = None,
) -> tuple[int, dict]:
    """Send a JSON request and return (status, parsed body)."""
    host, port = server.server_address
    conn = HTTPConnection(host, port, timeout=5)
    try:
        headers = {"Content-Type": "application/json"} if body is not None else {}
        data = json.dumps(body).encode() if body is not None else None
        conn.request(method, path, body=data, headers=headers)
        response = conn.getresponse()
        status = response.status
        raw = response.read()
        try:
            payload = json.loads(raw.decode())
        except json.JSONDecodeError:
            payload = {"raw": raw.decode(errors="replace")}
        return status, payload
    finally:
        conn.close()


class TestExperimentMode:
    def test_get_default_mode(self, server: DashboardServer) -> None:
        status, payload = _request(server, "GET", "/api/experiment/mode")
        assert status == HTTPStatus.OK
        assert payload["current_mode"] == "operator"
        assert payload["active_session"] is None
        assert payload["sessions"] == []

    def test_set_mode(self, server: DashboardServer) -> None:
        status, payload = _request(
            server, "POST", "/api/experiment/mode", {"mode": "experiment"}
        )
        assert status == HTTPStatus.OK
        assert payload["ok"] is True
        assert payload["mode"] == "experiment"

        status, payload = _request(server, "GET", "/api/experiment/mode")
        assert status == HTTPStatus.OK
        assert payload["current_mode"] == "experiment"

    def test_invalid_mode_rejected(self, server: DashboardServer) -> None:
        status, payload = _request(
            server, "POST", "/api/experiment/mode", {"mode": "invalid"}
        )
        assert status == HTTPStatus.BAD_REQUEST
        assert "invalid" in payload["error"].lower()

    def test_start_session(self, server: DashboardStateStore) -> None:
        status, payload = _request(
            server,
            "POST",
            "/api/experiment/session/start",
            {
                "session_id": "exp-001",
                "mode": "experiment",
                "hypothesis": "Test STDP pair protocol",
                "note": "Baseline recorded",
            },
        )
        assert status == HTTPStatus.OK
        assert payload["ok"] is True
        assert payload["session"]["session_id"] == "exp-001"
        assert payload["session"]["mode"] == "experiment"
        assert payload["session"]["hypothesis"] == "Test STDP pair protocol"
        assert len(payload["session"]["notes"]) == 1

        status, payload = _request(server, "GET", "/api/experiment/mode")
        assert payload["current_mode"] == "experiment"
        assert payload["active_session"]["session_id"] == "exp-001"

    def test_add_note(self, server: DashboardServer) -> None:
        _request(
            server,
            "POST",
            "/api/experiment/session/start",
            {"session_id": "exp-002", "mode": "debug"},
        )

        status, payload = _request(
            server, "POST", "/api/experiment/note", {"note": "Observation 1"}
        )
        assert status == HTTPStatus.OK
        assert payload["ok"] is True

        status, payload = _request(server, "GET", "/api/experiment/mode")
        assert len(payload["active_session"]["notes"]) == 1
        assert "Observation 1" in payload["active_session"]["notes"][0]

    def test_stop_session(self, server: DashboardServer) -> None:
        _request(
            server,
            "POST",
            "/api/experiment/session/start",
            {"session_id": "exp-003", "mode": "experiment"},
        )

        status, payload = _request(
            server, "POST", "/api/experiment/session/stop", {"end_tick": 42}
        )
        assert status == HTTPStatus.OK
        assert payload["ok"] is True
        assert payload["end_tick"] == 42

        status, payload = _request(server, "GET", "/api/experiment/mode")
        assert payload["active_session"] is None
        assert len(payload["sessions"]) == 1
        assert payload["sessions"][0]["end_tick"] == 42
        assert payload["sessions"][0]["active"] is False

    def test_session_history(self, server: DashboardServer) -> None:
        _request(
            server,
            "POST",
            "/api/experiment/session/start",
            {"session_id": "exp-004", "mode": "experiment"},
        )
        _request(server, "POST", "/api/experiment/session/stop", {})

        status, payload = _request(server, "GET", "/api/experiment/sessions")
        assert status == HTTPStatus.OK
        assert payload["count"] == 1
        assert payload["sessions"][0]["session_id"] == "exp-004"
