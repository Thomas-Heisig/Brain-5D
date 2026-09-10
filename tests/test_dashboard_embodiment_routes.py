"""HTTP tests for read-only embodiment dashboard endpoints."""

from __future__ import annotations

import json
from http.client import HTTPConnection
from threading import Thread
from types import SimpleNamespace
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
from src.memory import MemoryStore, MemoryWorldModel, TransitionWorldModel
from src.profiles import BehaviorProfile


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


def _post(
    host: str, port: int, path: str, body: dict[str, Any]
) -> tuple[int, dict[str, Any]]:
    connection = HTTPConnection(host, port, timeout=5)
    try:
        raw = json.dumps(body).encode("utf-8")
        connection.request(
            "POST", path, body=raw, headers={"Content-Type": "application/json"}
        )
        response = connection.getresponse()
        return response.status, cast(dict[str, Any], json.loads(response.read()))
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


def test_cognition_state_exposes_bounded_read_only_status() -> None:
    store = MemoryStore(run_id="run-dashboard")
    profile = BehaviorProfile("WESEN-0001")
    cognition = MemoryWorldModel(store, TransitionWorldModel(), "run-dashboard")
    experience = SimpleNamespace(memory=cognition, behavior_profile=profile)
    server = DashboardServer(
        ("127.0.0.1", 0), DashboardStateStore(), heatmaps=None, experience=experience
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    assert isinstance(host, str)
    try:
        payload = _get(host, port, "/api/cognition/state")
        assert payload["available"] is True
        assert payload["memory"]["controls"] == {
            "read_enabled": True,
            "write_enabled": True,
        }
        assert payload["behavior_profile"]["owner"] == "profiles.behavior"
        assert payload["world_model_influences_actions"] is False
    finally:
        _stop(server, thread)


def test_cognition_routes_expose_telemetry_and_confirm_memory_controls() -> None:
    store = MemoryStore(run_id="run-granular")
    profile = BehaviorProfile("WESEN-0001")
    cognition = MemoryWorldModel(store, TransitionWorldModel(), "run-granular")
    experience = SimpleNamespace(memory=cognition, behavior_profile=profile)
    server = DashboardServer(
        ("127.0.0.1", 0), DashboardStateStore(), heatmaps=None, experience=experience
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    assert isinstance(host, str)
    try:
        status = _get(host, port, "/api/cognition/status")
        assert status["memory"]["run_id"] == "run-granular"
        assert status["memory"]["retention_ticks"] == 1024

        memory = _get(host, port, "/api/cognition/memory")
        assert memory["integrity_digest"]
        assert memory["controls"] == {"read_enabled": True, "write_enabled": True}
        assert _get(host, port, "/api/cognition/memory/episodes")["available"] is True

        assert _get(host, port, "/api/cognition/world-model")["causal_understanding_claim"] is False
        assert _get(host, port, "/api/cognition/behavior-profile")["profile"]["profile_id"] == "WESEN-0001"

        status_code, changed = _post(
            host,
            port,
            "/api/cognition/memory/controls",
            {"read_enabled": False, "write_enabled": True},
        )
        assert status_code == 200
        assert changed["memory"]["controls"] == {
            "read_enabled": False,
            "write_enabled": True,
        }
        assert _get(host, port, "/api/cognition/memory/episodes")["episodes"] == []
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


def test_embodiment_pipeline_switches_are_validated_and_persisted() -> None:
    server, thread, host, port = _start(DashboardStateStore())
    try:
        status, result = _post(
            host, port, "/api/embodiment/pipeline", {"stage": "sensor", "enabled": True}
        )
        assert status == 200
        assert result == {"ok": True, "stage": "sensor", "enabled": True}
        pipeline = _get(host, port, "/api/embodiment/pipeline")
        assert pipeline["stages"]["sensor"]["enabled"] is True

        status, result = _post(
            host,
            port,
            "/api/embodiment/pipeline",
            {"stage": "unknown", "enabled": True},
        )
        assert status == 400
        assert "error" in result
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


def test_sensor_lifecycle_requires_adapter_and_audits_transitions() -> None:
    manager = ConnectionManager(cache_seconds=60)
    manager.register(
        ConnectionDescriptor(
            connection_id="sensor.lifecycle",
            name="Lifecycle sensor",
            kind=ConnectionKind.SENSOR,
            relationship=RelationshipClass.USABLE,
            status=ConnectionStatus.AVAILABLE,
            capabilities=("sample",),
            available=True,
            authorized=True,
            source="test_adapter",
        )
    )
    manager.register(
        ConnectionDescriptor(
            connection_id="sensor.adapter",
            name="Configured test sensor",
            kind=ConnectionKind.SENSOR,
            relationship=RelationshipClass.USABLE,
            status=ConnectionStatus.CONNECTED,
            capabilities=("sample",),
            available=True,
            authorized=True,
            adapter_id="test.adapter",
            configured=True,
            source="test_adapter",
        )
    )
    server, thread, host, port = _start(DashboardStateStore())
    server.connection_manager = manager
    from src.embodiment import SensorActivationService

    server.sensor_activation = SensorActivationService(manager)
    try:
        status, rejected = _post(
            host, port, "/api/embodiment/sensors/sensor.lifecycle/enable", {"tick": 7}
        )
        assert status == 409
        assert rejected["audit"]["result"] == "rejected"
        assert "adapter unavailable" in rejected["audit"]["error"]

        status, enabled = _post(
            host, port, "/api/embodiment/sensors/sensor.adapter/enable", {"tick": 8}
        )
        assert status == 200
        assert enabled["sensor"]["active"] is True
        assert enabled["sensor"]["health"] == "ACTIVE"

        status, disabled = _post(
            host, port, "/api/embodiment/sensors/sensor.adapter/disable", {"tick": 9}
        )
        assert status == 200
        assert disabled["sensor"]["active"] is False
        assert disabled["audit"]["previous_state"] == "ACTIVE"
        collection = _get(host, port, "/api/embodiment/sensors")
        assert len(collection["audit"]) == 3
    finally:
        _stop(server, thread)


def test_embodiment_connections_reflect_runtime_appearance_change() -> None:
    state = DashboardStateStore()
    manager = ConnectionManager(cache_seconds=60)
    available = ConnectionDescriptor(
        connection_id="sensor.dynamic-test",
        name="Dynamic test sensor",
        kind=ConnectionKind.SENSOR,
        relationship=RelationshipClass.USABLE,
        status=ConnectionStatus.CONNECTED,
        capabilities=("sample",),
        available=True,
        authorized=True,
        active=True,
        source="test_adapter",
    )
    manager.register(available)
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
        first = _get(host, port, "/api/embodiment/connections")
        dynamic = next(
            item
            for item in first["connections"]
            if item["connection_id"] == "sensor.dynamic-test"
        )
        assert dynamic["available"] is True
        assert dynamic["active"] is True

        manager.register(
            ConnectionDescriptor(
                connection_id=available.connection_id,
                name=available.name,
                kind=available.kind,
                relationship=RelationshipClass.PERCEIVABLE,
                status=ConnectionStatus.UNAVAILABLE,
                capabilities=available.capabilities,
                available=False,
                authorized=False,
                active=False,
                source="system_discovery",
                message="Device disappeared during discovery.",
            )
        )

        second = _get(host, port, "/api/embodiment/connections")
        dynamic = next(
            item
            for item in second["connections"]
            if item["connection_id"] == "sensor.dynamic-test"
        )
        assert dynamic["available"] is False
        assert dynamic["authorized"] is False
        assert dynamic["active"] is False
        assert dynamic["message"] == "Device disappeared during discovery."
    finally:
        _stop(server, thread)


def test_neural_symbiosis_gateway_status_and_experiment_guard() -> None:
    server, thread, host, port = _start(DashboardStateStore())
    try:
        status = _get(host, port, "/api/embodiment/neural-symbiosis")
        assert status["status"] == "implemented_experimental"
        assert status["gateway"]["state"] == "disabled"
        assert status["productive_gateway"]["available"] is False

        gateway_id = status["gateway"]["gateway_id"]
        collection = _get(host, port, "/api/embodiment/gateways")
        assert collection["count"] == 1
        detail = _get(host, port, f"/api/embodiment/gateways/{gateway_id}")
        assert detail["gateway_id"] == gateway_id

        rejected_status, rejected = _post(
            host,
            port,
            "/api/experiments/EXP-GW-HTTP/gateway/activate",
            {"condition": "plastic", "seed": 101, "experiment_mode": True},
        )
        assert rejected_status == 400
        assert "preregistration" in rejected["error"]

        accepted_status, accepted = _post(
            host,
            port,
            "/api/experiments/EXP-GW-HTTP/gateway/activate",
            {"condition": "frozen", "seed": 101, "experiment_mode": True},
        )
        assert accepted_status == 200
        assert accepted["gateway"]["state"] == "active_frozen"
        assert accepted["gateway"]["productive_gateway"]["available"] is False
    finally:
        _stop(server, thread)
