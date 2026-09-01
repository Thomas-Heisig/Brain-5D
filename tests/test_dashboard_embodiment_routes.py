"""HTTP tests for read-only embodiment dashboard endpoints."""

from __future__ import annotations

import json
from http.client import HTTPConnection
from threading import Thread
from typing import Any, cast

from src.dashboard.models import DashboardSnapshot, SystemMetrics
from src.dashboard.server import DashboardServer
from src.dashboard.state import DashboardStateStore
from src.embodiment import (
    ConnectionDescriptor,
    ConnectionKind,
    ConnectionManager,
    ConnectionStatus,
    RelationshipClass,
)
from src.embodiment.models import EmbodimentMetrics


def _start(state: DashboardStateStore) -> tuple[DashboardServer, Thread, str, int]:
    server = DashboardServer(("127.0.0.1", 0), state, heatmaps=None)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    assert isinstance(host, str)
    return server, thread, host, port


def _get(host: str, port: int, path: str) -> dict[str, Any]:
    connection = HTTPConnection(host, port, timeout=5)
    try:
        connection.request("GET", path)
        response = connection.getresponse()
        assert response.status == 200
        return cast(dict[str, Any], json.loads(response.read()))
    finally:
        connection.close()


def _stop(server: DashboardServer, thread: Thread) -> None:
    server.shutdown()
    server.server_close()
    thread.join(timeout=1)


def test_embodiment_state_is_honest_when_unconfigured() -> None:
    state = DashboardStateStore()
    server, thread, host, port = _start(state)
    try:
        payload = _get(host, port, "/api/embodiment/state")
        assert payload["available"] is False
        assert payload["loop_status"] == "unconfigured"
        assert payload["details"]["sensor_values"] is None
        assert len(payload["loop"]) == 6
    finally:
        _stop(server, thread)


def test_embodiment_metrics_expose_published_values() -> None:
    state = DashboardStateStore(
        initial=DashboardSnapshot(
            system=SystemMetrics(tick=12),
            embodiment=EmbodimentMetrics(
                environment_kind="simulated",
                active_sensors=2,
                active_actuators=1,
                episode=3,
                episode_reward=1.25,
                last_reward=0.5,
                last_action="advance",
            ),
        )
    )
    server, thread, host, port = _start(state)
    try:
        payload = _get(host, port, "/api/embodiment/metrics")
        assert payload["available"] is True
        assert payload["tick"] == 12
        assert payload["metrics"]["episode_reward"] == 1.25
        assert payload["metrics"]["last_action"] == "advance"
    finally:
        _stop(server, thread)


def test_embodiment_history_contains_only_published_snapshots() -> None:
    state = DashboardStateStore(max_history=5)
    state.publish(
        DashboardSnapshot(
            system=SystemMetrics(tick=1),
            embodiment=EmbodimentMetrics(environment_kind="simulated", episode=1),
        )
    )
    state.publish(
        DashboardSnapshot(
            system=SystemMetrics(tick=2),
            embodiment=EmbodimentMetrics(
                environment_kind="simulated",
                episode=1,
                episode_reward=0.75,
                last_action="move",
            ),
        )
    )
    server, thread, host, port = _start(state)
    try:
        payload = _get(host, port, "/api/embodiment/history?limit=2")
        assert payload["available"] is True
        assert payload["count"] == 2
        assert payload["history"][0]["tick"] == 2
        assert payload["history"][0]["metrics"]["last_action"] == "move"
    finally:
        _stop(server, thread)


def test_embodiment_connections_are_read_only_and_explicitly_authorized() -> None:
    state = DashboardStateStore()
    manager = ConnectionManager(cache_seconds=60)
    manager.register(
        ConnectionDescriptor(
            connection_id="sensor.test-camera",
            name="Test camera",
            kind=ConnectionKind.SENSOR,
            relationship=RelationshipClass.USABLE,
            status=ConnectionStatus.CONNECTED,
            capabilities=("frames",),
            permissions=("capture",),
            available=True,
            authorized=True,
            active=True,
            source="test_adapter",
        )
    )
    server = DashboardServer(
        ("127.0.0.1", 0),
        state,
        heatmaps=None,
        connection_manager=manager,
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    assert isinstance(host, str)
    try:
        payload = _get(host, port, "/api/embodiment/connections")
        camera = next(
            item
            for item in payload["connections"]
            if item["connection_id"] == "sensor.test-camera"
        )
        assert camera["available"] is True
        assert camera["authorized"] is True
        assert camera["permissions"] == ["capture"]
    finally:
        _stop(server, thread)
