from __future__ import annotations

import json
from datetime import datetime, timezone
from http.client import HTTPConnection
from pathlib import Path
from threading import Thread
from typing import Any

from src.dashboard.development_timeline import build_development_timeline
from src.dashboard.server import DashboardServer
from src.dashboard.state import DashboardStateStore

ROOT = Path(__file__).resolve().parents[1]


def test_development_timeline_separates_engineering_verification_and_evidence() -> None:
    payload = build_development_timeline(
        ROOT,
        now=datetime(2026, 9, 9, tzinfo=timezone.utc),
    )

    assert len(payload["stages"]) == 11
    assert payload["stage_floor"] == 3
    assert payload["stage_next"] == 4
    assert payload["current_stage"] == 3.75
    assert payload["scientific_stage"] < payload["current_stage"]
    assert payload["engineering_score"] != payload["verification_score"]
    assert payload["verification_score"] != payload["scientific_evidence_score"]
    assert payload["consciousness_claim"] == "unsupported"
    assert "consciousness" in payload["scientific_note"].lower()


def test_planned_features_do_not_count_as_implemented() -> None:
    payload = build_development_timeline(ROOT)
    stage_eight = next(stage for stage in payload["stages"] if stage["stage"] == 8)
    assert stage_eight["status"] == "planned"
    assert all(item["status"] == "planned" for item in stage_eight["criteria"])
    assert payload["scientific_evidence_score"] <= 1.0


def test_runtime_override_and_snapshot_fallback_are_distinct() -> None:
    runtime_payload = build_development_timeline(
        ROOT,
        runtime={"neurons": 12, "synapses": 34},
    )
    assert runtime_payload["current_runtime"]["source"] == "runtime"
    assert runtime_payload["current_runtime"]["status"] == "active"
    assert runtime_payload["current_runtime"]["neurons"] == 12

    snapshot_payload = build_development_timeline(ROOT)
    assert snapshot_payload["current_runtime"]["source"] in {
        "last_observed",
        "unavailable",
    }
    if snapshot_payload["last_observed_runtime"] is not None:
        assert snapshot_payload["last_observed_runtime"]["status"] == "unavailable"


def _request(server: DashboardServer, path: str) -> tuple[int, dict[str, Any]]:
    host, port = server.server_address[:2]
    connection = HTTPConnection(str(host), int(port), timeout=5)
    try:
        connection.request("GET", path)
        response = connection.getresponse()
        return response.status, json.loads(response.read().decode("utf-8"))
    finally:
        connection.close()


def test_development_timeline_api_is_read_only_and_reachable() -> None:
    server = DashboardServer(("127.0.0.1", 0), DashboardStateStore(), None)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, payload = _request(server, "/api/release/development-timeline")
        assert status == 200
        assert payload["schema_version"] == 1
        assert payload["consciousness_claim"] == "unsupported"
        assert len(payload["stages"]) == 11
    finally:
        server.shutdown()
        server.server_close()
