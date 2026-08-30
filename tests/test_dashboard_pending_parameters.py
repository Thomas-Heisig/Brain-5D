"""Tests for the dashboard pending-parameters workflow."""

from __future__ import annotations

import json
import threading
import time
from http import HTTPStatus
from http.client import HTTPConnection

import pytest

from src.dashboard.models import (
    ComponentStatus,
    DashboardSnapshot,
    HealthSnapshot,
    ParameterSchema,
    PendingParameterChange,
)
from src.dashboard.server import DashboardServer
from src.dashboard.state import DashboardStateStore


@pytest.fixture
def state() -> DashboardStateStore:
    """Create a state store with a few parameters."""
    parameters = {
        "simulation.dt_ms": ParameterSchema(
            name="simulation.dt_ms",
            value=1.0,
            default=1.0,
            min=0.0,
            max=1000.0,
            unit="ms",
            description="Simulation time step.",
            source="config",
            runtime_mutable=False,
            requires_restart=True,
            scientific_sensitive=True,
        ),
        "stdp.enabled": ParameterSchema(
            name="stdp.enabled",
            value=False,
            default=False,
            description="STDP toggle.",
            source="config",
            runtime_mutable=False,
            requires_restart=True,
            scientific_sensitive=True,
        ),
        "homeostasis.target_rate_hz": ParameterSchema(
            name="homeostasis.target_rate_hz",
            value=5.0,
            default=5.0,
            min=0.0,
            max=1000.0,
            unit="Hz",
            description="Target firing rate.",
            source="config",
            runtime_mutable=True,
            requires_restart=False,
            scientific_sensitive=True,
        ),
    }
    snapshot = DashboardSnapshot(parameters=parameters)
    return DashboardStateStore(initial=snapshot)


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


class TestPendingParameters:
    def test_list_parameters(self, server: DashboardServer) -> None:
        status, payload = _request(server, "GET", "/api/parameters")
        assert status == HTTPStatus.OK
        assert payload["count"] == 3
        assert "simulation.dt_ms" in payload["parameters"]

    def test_set_pending_change(self, server: DashboardServer) -> None:
        status, payload = _request(
            server,
            "POST",
            "/api/parameters/homeostasis.target_rate_hz/pending",
            {"value": 10.0},
        )
        assert status == HTTPStatus.OK
        assert payload["ok"] is True
        assert payload["pending"]["proposed_value"] == 10.0

        status, payload = _request(server, "GET", "/api/parameters/pending")
        assert status == HTTPStatus.OK
        assert payload["count"] == 1
        pending = payload["pending"]["homeostasis.target_rate_hz"]
        assert pending["current_value"] == 5.0
        assert pending["proposed_value"] == 10.0

    def test_apply_pending_change(self, server: DashboardServer) -> None:
        _request(
            server,
            "POST",
            "/api/parameters/homeostasis.target_rate_hz/pending",
            {"value": 12.0},
        )

        status, payload = _request(server, "POST", "/api/parameters/pending/apply", {})
        assert status == HTTPStatus.OK
        assert payload["ok"] is True
        assert payload["applied"] == ["homeostasis.target_rate_hz"]

        status, payload = _request(
            server, "GET", "/api/parameters/homeostasis.target_rate_hz"
        )
        assert status == HTTPStatus.OK
        assert payload["value"] == 12.0
        assert payload["source"] == "operator"

        status, payload = _request(server, "GET", "/api/parameters/pending")
        assert status == HTTPStatus.OK
        assert payload["count"] == 0
        assert len(payload["history"]) == 1
        assert payload["history"][0]["action"] == "applied"
        assert payload["history"][0]["saved_profile"] is False

    def test_apply_and_save_profile(self, server: DashboardServer) -> None:
        _request(
            server,
            "POST",
            "/api/parameters/homeostasis.target_rate_hz/pending",
            {"value": 7.0},
        )

        status, payload = _request(
            server, "POST", "/api/parameters/pending/save-profile", {}
        )
        assert status == HTTPStatus.OK
        assert payload["saved_profile"] is True

        status, payload = _request(
            server, "GET", "/api/parameters/homeostasis.target_rate_hz"
        )
        assert status == HTTPStatus.OK
        assert payload["source"] == "profile"

    def test_cancel_pending_change(self, server: DashboardServer) -> None:
        _request(
            server,
            "POST",
            "/api/parameters/homeostasis.target_rate_hz/pending",
            {"value": 20.0},
        )

        status, payload = _request(
            server,
            "POST",
            "/api/parameters/pending/cancel",
            {"names": ["homeostasis.target_rate_hz"]},
        )
        assert status == HTTPStatus.OK
        assert payload["cancelled"] == ["homeostasis.target_rate_hz"]

        status, payload = _request(server, "GET", "/api/parameters/pending")
        assert status == HTTPStatus.OK
        assert payload["count"] == 0
        assert len(payload["history"]) == 1
        assert payload["history"][0]["action"] == "cancelled"

    def test_coerce_boolean_string(self, server: DashboardServer) -> None:
        status, payload = _request(
            server,
            "POST",
            "/api/parameters/stdp.enabled/pending",
            {"value": "true"},
        )
        assert status == HTTPStatus.OK
        assert payload["pending"]["proposed_value"] is True

    def test_missing_parameter_returns_404(self, server: DashboardServer) -> None:
        status, payload = _request(
            server,
            "POST",
            "/api/parameters/does.not.exist/pending",
            {"value": 1.0},
        )
        assert status == HTTPStatus.NOT_FOUND
        assert "not found" in payload["error"].lower()

    def test_missing_value_returns_400(self, server: DashboardServer) -> None:
        status, payload = _request(
            server,
            "POST",
            "/api/parameters/homeostasis.target_rate_hz/pending",
            {},
        )
        assert status == HTTPStatus.BAD_REQUEST
        assert "value" in payload["error"].lower()
