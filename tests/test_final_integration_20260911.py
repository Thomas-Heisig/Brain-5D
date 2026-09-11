"""Regression coverage for the 2026-09-11 final integration."""

from __future__ import annotations

import json
import threading
import time
from http import HTTPStatus
from http.client import HTTPConnection
from pathlib import Path
from typing import Any, cast

from src.controller.runtime import RuntimeController
from src.core.network import Brain5DConfig, NeuralNetwork
from src.core.neuron import NeuronConfig, create_neuron
from src.dashboard.models import DashboardSnapshot
from src.dashboard.operator_bridge import OperatorBridge
from src.dashboard.server import DashboardServer
from src.dashboard.state import DashboardStateStore
from src.research.protocol_registry import (
    OPERATIONAL_RUNNERS,
    load_operational_protocols,
)

ROOT = Path(__file__).parents[1]


def _request(
    server: DashboardServer,
    method: str,
    path: str,
    body: dict[str, Any] | None = None,
) -> tuple[int, dict[str, Any] | str]:
    host, port = cast(tuple[str, int], server.server_address)
    connection = HTTPConnection(host, port, timeout=5)
    try:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {"Content-Type": "application/json"} if body is not None else {}
        connection.request(method, path, body=data, headers=headers)
        response = connection.getresponse()
        raw = response.read().decode("utf-8")
        try:
            return response.status, json.loads(raw)
        except json.JSONDecodeError:
            return response.status, raw
    finally:
        connection.close()


def _live_server() -> tuple[DashboardServer, DashboardStateStore, int, int]:
    config = Brain5DConfig(
        dimensions=(2, 1, 1, 1, 1),
        neuron=NeuronConfig(initial_v=-64.0, initial_u=-11.5),
    )
    network = NeuralNetwork(config)
    input_id = network.add_neuron((0, 0, 0, 0, 0))
    output_id = network.add_neuron((1, 0, 0, 0, 0))
    network.input_cells.add(input_id)
    network.output_cells.add(output_id)
    network.connect(input_id, output_id, weight=0.5, delay=1)
    controller = RuntimeController(network)
    state = DashboardStateStore(initial=DashboardSnapshot())
    server = DashboardServer(
        ("127.0.0.1", 0),
        state,
        heatmaps=None,
        structural_bridge=OperatorBridge(controller),
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.03)
    return server, state, input_id, output_id


def test_neuron_config_controls_initial_construction_without_live_u_override() -> None:
    config = NeuronConfig(
        a=0.03, b=0.25, c=-62.0, d=6.0, initial_v=-61.5, initial_u=-9.25
    )
    neuron = create_neuron(7, config=config)
    assert (neuron.a, neuron.b, neuron.c, neuron.d) == (0.03, 0.25, -62.0, 6.0)
    assert (neuron.v, neuron.u) == (-61.5, -9.25)
    neuron.u = 123.0
    neuron.set_config(config)
    assert neuron.u == 123.0


def test_network_uses_neuron_construction_config() -> None:
    config = Brain5DConfig(
        dimensions=(1, 1, 1, 1, 1),
        neuron=NeuronConfig(
            a=0.04, b=0.3, c=-60.0, d=4.0, initial_v=-58.0, initial_u=-8.0
        ),
    )
    network = NeuralNetwork(config)
    neuron_id = network.add_neuron((0, 0, 0, 0, 0))
    neuron = network.get_neuron(neuron_id)
    assert neuron is not None
    assert (neuron.a, neuron.b, neuron.c, neuron.d, neuron.v, neuron.u) == (
        0.04,
        0.3,
        -60.0,
        4.0,
        -58.0,
        -8.0,
    )


def test_runtime_io_get_and_operator_injection_are_observable_and_non_evidentiary() -> (
    None
):
    server, _state, input_id, output_id = _live_server()
    try:
        status, payload = _request(server, "GET", "/api/runtime/io")
        assert status == HTTPStatus.OK
        assert isinstance(payload, dict)
        assert payload["manual_injection_allowed"] is True
        assert payload["scientific_evidence"] is False
        assert payload["input_neurons"][0]["neuron_id"] == input_id
        assert payload["output_neurons"][0]["neuron_id"] == output_id

        status, payload = _request(
            server,
            "POST",
            "/api/runtime/io/inject",
            {"neuron_id": input_id, "current": 25.0, "ticks": 2},
        )
        assert status == HTTPStatus.OK
        assert isinstance(payload, dict)
        assert payload["ok"] is True
        assert payload["operator_intervention"] is True
        assert payload["scientific_evidence"] is False
        assert payload["delta"]["ticks"] == 2
        assert str(output_id) in payload["after"]["outputs"]
    finally:
        server.shutdown()


def test_runtime_io_is_fail_closed_in_experiment_mode_and_rejects_non_input() -> None:
    server, state, input_id, output_id = _live_server()
    try:
        status, payload = _request(
            server,
            "POST",
            "/api/runtime/io/inject",
            {"neuron_id": output_id, "current": 10.0, "ticks": 1},
        )
        assert status == HTTPStatus.BAD_REQUEST
        assert (
            isinstance(payload, dict) and "not a registered input" in payload["error"]
        )

        state.set_experiment_mode("experiment")
        status, payload = _request(
            server,
            "POST",
            "/api/runtime/io/inject",
            {"neuron_id": input_id, "current": 10.0, "ticks": 1},
        )
        assert status == HTTPStatus.CONFLICT
        assert isinstance(payload, dict)
        assert payload["scientific_evidence"] is False
        assert "locked" in payload["error"].lower()
    finally:
        server.shutdown()


def test_review_route_is_directly_addressable() -> None:
    state = DashboardStateStore(initial=DashboardSnapshot())
    server = DashboardServer(("127.0.0.1", 0), state, heatmaps=None)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.03)
    try:
        status, payload = _request(server, "GET", "/review")
        assert status == HTTPStatus.OK
        assert isinstance(payload, str)
        assert "review" in payload.lower() or "fragen" in payload.lower()
    finally:
        server.shutdown()


def test_operational_registry_covers_every_registered_question_once() -> None:
    import yaml

    questions: list[dict[str, Any]] = []
    for path in sorted((ROOT / "research" / "registry").glob("questions*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if isinstance(data, dict):
            questions.extend(data.get("questions", []))
        elif isinstance(data, list):
            questions.extend(data)
    question_ids = {item["id"] for item in questions}
    protocols = load_operational_protocols(ROOT / "research")
    protocol_questions = [item["research_question"] for item in protocols]
    assert len(question_ids) == 94
    assert len(protocols) == 94
    assert set(protocol_questions) == question_ids
    assert len(protocol_questions) == len(set(protocol_questions))
    assert all(item["id"] in OPERATIONAL_RUNNERS for item in protocols)
    assert all(item.get("scientific_evidence", False) is False for item in protocols)
    assert all(
        item.get("automatic_evidence_promotion", False) is False for item in protocols
    )


def test_frontend_final_integration_contract_is_present() -> None:
    static = ROOT / "src" / "dashboard" / "static"
    required = [
        "frontend/index.js",
        "frontend/core/api.js",
        "frontend/components/status-bar.js",
        "frontend/components/notification-center.js",
        "frontend/components/help.js",
        "frontend/modules/runtime-io.js",
        "frontend/modules/science-transparency.js",
        "frontend/modules/review-link.js",
        "frontend/styles/tokens.css",
        "frontend/styles/reset.css",
        "frontend/styles/base.css",
        "frontend/styles/layout.css",
        "frontend/styles/components.css",
        "frontend/styles/modules.css",
        "frontend/styles/utilities.css",
        "frontend/styles/print.css",
    ]
    assert all((static / path).is_file() for path in required)
    html = (static / "index.html").read_text(encoding="utf-8")
    viewer = (static / "neuron-model-viewer.js").read_text(encoding="utf-8")
    wesen = (static / "wesen.js").read_text(encoding="utf-8")
    console = (static / "console-log.js").read_text(encoding="utf-8")
    assert "/frontend/styles/index.css" in html
    assert 'import "./frontend/index.js";' in console
    assert '<option value="tsne">' in viewer
    assert '<option value="umap">' in viewer
    assert '<option value="cluster_export">' in viewer
    assert "t-SNE · Not implemented yet" not in viewer
    assert "appendChild(embodiment)" not in wesen
    for route in ("overview", "research", "wesen", "gate", "settings"):
        assert f'data-footer-tab="{route}"' in wesen
    assert "BRAIN-5D" not in html
