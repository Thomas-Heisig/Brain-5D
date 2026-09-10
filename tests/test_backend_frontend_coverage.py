from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_backend_frontend_coverage_contract_has_consumers_or_reasons() -> None:
    contract = json.loads(
        (ROOT / "docs/03-dashboard/BACKEND_FRONTEND_COVERAGE.json").read_text(
            encoding="utf-8"
        )
    )
    entries = contract["entries"]
    assert entries
    for entry in entries:
        assert {
            "method",
            "path",
            "backend_owner",
            "frontend_consumer",
            "surface",
            "read_write",
            "experiment_only",
            "safety_class",
            "coverage_status",
        } <= set(entry)
        if entry["coverage_status"] == "BACKEND_ONLY":
            assert entry.get("backend_only_reason")
        else:
            for consumer in entry["frontend_consumer"].split(", "):
                assert (ROOT / "src/dashboard/static" / consumer).is_file()


def test_coverage_contract_preserves_sensor_cognition_and_gateway_boundaries() -> None:
    server_source = (ROOT / "src/dashboard/server.py").read_text(encoding="utf-8")
    gateway_source = (
        ROOT / "src/dashboard/static/wesen-neural-symbiosis.js"
    ).read_text(encoding="utf-8")
    assert "/api/embodiment/sensors/" in server_source
    assert "/api/cognition/memory/controls" in server_source
    assert "/api/experiments/" in server_source
    assert "Productive Gateway" in gateway_source
    assert "/api/gateway/activate" not in server_source
