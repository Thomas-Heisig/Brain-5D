"""HTTP route tests for the alpha.5 structural dashboard API."""

import json
from http.client import HTTPConnection
from threading import Thread

from src.dashboard.models import JSONValue
from src.dashboard.server import DashboardServer
from src.dashboard.state import DashboardStateStore
from src.dashboard.structural_api import JSONMapping, StructuralCommandResult


class Bridge:
    def structural_status(self) -> JSONMapping:
        return {"configured": True}

    def structural_proposals(self) -> list[JSONMapping]:
        return [{"proposal_id": "p1"}]

    def structural_history(self, limit: int) -> list[JSONMapping]:
        return [{"sequence": limit}]

    def structural_heatmap(self, kind: str) -> JSONMapping:
        values: list[JSONValue] = []
        return {"kind": kind, "values": values}

    def structural_config(self) -> JSONMapping:
        return {"enabled": False}

    def approve_structural(self, proposal_id: str) -> StructuralCommandResult:
        return StructuralCommandResult(proposal_id == "p1", "approved")

    def reject_structural(self, proposal_id: str) -> StructuralCommandResult:
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


def test_structural_get_and_post_routes() -> None:
    server = DashboardServer(("127.0.0.1", 0), DashboardStateStore(), None, Bridge())
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    if not isinstance(host, str):
        raise AssertionError("dashboard server did not expose an IP address")
    connection = HTTPConnection(host, port)
    try:
        connection.request("GET", "/api/structural/proposals")
        response = connection.getresponse()
        assert response.status == 200
        assert json.loads(response.read())["proposals"][0]["proposal_id"] == "p1"

        body = json.dumps({"proposal_id": "p1"})
        connection.request(
            "POST",
            "/api/structural/approve",
            body=body,
            headers={"Content-Type": "application/json"},
        )
        response = connection.getresponse()
        assert response.status == 200
        assert json.loads(response.read())["ok"] is True
    finally:
        connection.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=1.0)
