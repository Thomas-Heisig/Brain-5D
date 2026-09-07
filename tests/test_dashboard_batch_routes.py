from __future__ import annotations

from http.client import HTTPConnection
from pathlib import Path
from threading import Thread
from typing import Any

import src.dashboard.server as server_module
from src.dashboard.server import DashboardServer
from src.dashboard.state import DashboardStateStore
from src.dashboard.research_source import ResearchSource


class _FakeBatchService:
    def __init__(self, *_args: Any, **_kwargs: Any) -> None:
        pass

    def run_batch(self, body: dict[str, object], **_kwargs: Any) -> dict[str, object]:
        return {
            "workflow_id": str(body.get("batch_id")),
            "report": "workflows/test.json",
            "report_markdown": "workflows/test.md",
            "completed": 1,
            "failed": 0,
            "results": [],
        }

    def catalog(self) -> dict[str, object]:
        return {"questions": [{"id": "RQ-TEST-001"}], "protocols": []}


class _RejectingBatchService(_FakeBatchService):
    def run_batch(self, body: dict[str, object], **_kwargs: Any) -> dict[str, object]:
        raise ValueError("Unknown experiment protocol: missing_protocol")


def _request(server: DashboardServer, method: str, path: str, body: dict[str, object] | None = None) -> tuple[int, str]:
    host, port = server.server_address[:2]
    connection = HTTPConnection(str(host), int(port), timeout=5)
    try:
        payload = None
        headers: dict[str, str] = {}
        if body is not None:
            import json

            payload = json.dumps(body)
            headers["Content-Type"] = "application/json"
        connection.request(method, path, payload, headers)
        response = connection.getresponse()
        return response.status, response.read().decode("utf-8")
    finally:
        connection.close()


def test_workflow_catalog_and_batch_routes_are_reachable(monkeypatch: Any) -> None:
    original = server_module.ExperimentWorkflowService
    monkeypatch.setattr(server_module, "ExperimentWorkflowService", _FakeBatchService)
    server = DashboardServer(
        ("127.0.0.1", 0),
        DashboardStateStore(),
        None,
        research_source=ResearchSource(Path("research")),
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        catalog_status, catalog_body = _request(server, "GET", "/api/experiment/workflow/catalog")
        assert catalog_status == 200
        assert '"questions"' in catalog_body

        batch_status, batch_body = _request(
            server,
            "POST",
            "/api/experiment/workflow/batch",
            {"batch_id": "EXP-ROUTE-0001", "protocols": ["protocol_a"]},
        )
        assert batch_status == 200, batch_body
        assert '"workflow_id":"EXP-ROUTE-0001"' in batch_body
    finally:
        server.shutdown()
        server.server_close()
        assert server_module.ExperimentWorkflowService is _FakeBatchService
        monkeypatch.setattr(server_module, "ExperimentWorkflowService", original)


def test_batch_route_returns_structured_bad_request_for_invalid_protocol(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(server_module, "ExperimentWorkflowService", _RejectingBatchService)
    server = DashboardServer(
        ("127.0.0.1", 0),
        DashboardStateStore(),
        None,
        research_source=ResearchSource(Path("research")),
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, response_body = _request(
            server,
            "POST",
            "/api/experiment/workflow/batch",
            {"batch_id": "EXP-ROUTE-INVALID", "protocols": ["missing_protocol"]},
        )

        assert status == 400
        assert response_body == '{"error":"Unknown experiment protocol: missing_protocol"}'
    finally:
        server.shutdown()
        server.server_close()
