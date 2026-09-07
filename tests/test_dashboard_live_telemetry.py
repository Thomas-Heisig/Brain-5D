from __future__ import annotations

import json
from http.client import HTTPConnection
from threading import Thread
from typing import Any

from src.controller.runtime import RuntimeController
from src.core.network import Brain5DConfig, NeuralNetwork
from src.dashboard.live_projection import TelemetryFrameStore
from src.dashboard.operator_bridge import OperatorBridge
from src.dashboard.server import DashboardServer
from src.dashboard.state import DashboardStateStore


def make_network() -> NeuralNetwork:
    network = NeuralNetwork(Brain5DConfig(dimensions=(2, 2, 1, 1, 1)))
    network.add_neuron((0, 0, 0, 0, 0))
    return network


def _request(server: DashboardServer) -> tuple[int, dict[str, Any]]:
    host, port = server.server_address[:2]
    connection = HTTPConnection(str(host), int(port), timeout=5)
    try:
        connection.request("GET", "/api/live/projection?kind=energy&resolution=2")
        response = connection.getresponse()
        return response.status, json.loads(response.read().decode("utf-8"))
    finally:
        connection.close()


def _start_server(
    network: NeuralNetwork, store: TelemetryFrameStore
) -> DashboardServer:
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
    network = make_network()
    server = _start_server(network, TelemetryFrameStore(capture_interval_ticks=2))
    try:
        status, payload = _request(server)

        assert status == 503
        assert "error" in payload
    finally:
        server.shutdown()
        server.server_close()


def test_live_projection_route_propagates_stale_store_status() -> None:
    network = make_network()
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
