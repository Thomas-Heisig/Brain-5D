from __future__ import annotations

import json
from dataclasses import dataclass
from http.client import HTTPConnection
from threading import Thread
from typing import Any

from src.controller.runtime import RuntimeController
from src.dashboard.live_projection import TelemetryFrameStore
from src.dashboard.operator_bridge import OperatorBridge
from src.dashboard.server import DashboardServer
from src.dashboard.state import DashboardStateStore


@dataclass
class _Neuron:
    v: float = -65.0
    energy: float = 1.0
    u: float = -13.0
    spike_counter: int = 0
    last_spike_tick: int = -1


class _Network:
    dimensions = (2, 2, 1, 1, 1)
    neurons = {0: _Neuron()}
    synapses: dict[int, list[Any]] = {}
    neuron_count = 1
    synapse_count = 0
    queued_event_count = 0

    def __init__(self) -> None:
        self.current_tick = 0


def _request(server: DashboardServer) -> tuple[int, dict[str, Any]]:
    host, port = server.server_address[:2]
    connection = HTTPConnection(str(host), int(port), timeout=5)
    try:
        connection.request("GET", "/api/live/projection?kind=energy&resolution=2")
        response = connection.getresponse()
        return response.status, json.loads(response.read().decode("utf-8"))
    finally:
        connection.close()


def _start_server(network: _Network, store: TelemetryFrameStore) -> DashboardServer:
    bridge = OperatorBridge(
        RuntimeController(network),
        telemetry_store=store,
    )
    server = DashboardServer(
        ("127.0.0.1", 0),
        DashboardStateStore(),
        None,
        bridge,
    )
    Thread(target=server.serve_forever, daemon=True).start()
    return server


def test_live_projection_route_propagates_unavailable_telemetry() -> None:
    network = _Network()
    server = _start_server(network, TelemetryFrameStore(capture_interval_ticks=2))
    try:
        status, payload = _request(server)

        assert status == 503
        assert "error" in payload
    finally:
        server.shutdown()
        server.server_close()


def test_live_projection_route_propagates_stale_store_status() -> None:
    network = _Network()
    store = TelemetryFrameStore(capture_interval_ticks=2)
    store.prime(network)
    network.current_tick = 10
    server = _start_server(network, store)
    try:
        status, payload = _request(server)

        assert status == 200
        telemetry = payload["telemetry"]
        assert telemetry["status"] == "stale"
        assert telemetry["frame_age_ticks"] == 10
    finally:
        server.shutdown()
        server.server_close()