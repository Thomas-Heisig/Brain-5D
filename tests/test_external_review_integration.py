"""Public questionnaire integration must not become private-data or EVID authority."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from threading import Thread

import pytest

from src.dashboard.external_review import build_external_review_status
from src.dashboard.research_source import ResearchSource
from src.dashboard.server import DashboardServer
from src.dashboard.state import DashboardStateStore
from tests.dashboard_http import request_json

ROOT = Path(__file__).resolve().parents[1]


def _copy_public(root: Path) -> Path:
    for relative in (
        "research/external_review/integration.json",
        "review_portal/catalogue.py",
        "src/dashboard/static/review/instrument.js",
    ):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    return root / "research/external_review/integration.json"


def test_public_status_binds_instrument_without_claiming_completed_reviews() -> None:
    status = build_external_review_status(ROOT)
    assert status["available"] is True
    assert status["base_questions"] + status["specialist_questions"] == 135
    assert status["human_review_status"] == "not_recorded"
    assert status["external_ethics_approval"] == "not_claimed"
    assert status["response_count"] is None
    assert status["automatic_evidence_promotion"] is False
    assert status["scientific_evidence"] is False


@pytest.mark.parametrize(
    "field,value",
    [
        ("automatic_evidence_promotion", True),
        ("external_ethics_approval", "approved"),
        ("human_review_status", "completed"),
        ("schema_version", 99),
    ],
)
def test_public_metadata_cannot_grant_review_or_ethics_authority(
    tmp_path: Path,
    field: str,
    value: object,
) -> None:
    path = _copy_public(tmp_path)
    data = json.loads(path.read_text())
    data[field] = value
    path.write_text(json.dumps(data))
    status = build_external_review_status(tmp_path)
    assert status["available"] is False
    assert status["scientific_evidence"] is False


def test_instrument_drift_fails_closed(tmp_path: Path) -> None:
    _copy_public(tmp_path)
    (tmp_path / "review_portal/catalogue.py").write_text("changed")
    status = build_external_review_status(tmp_path)
    assert status["available"] is False
    assert "drift" in status["reason"]
    assert build_external_review_status(tmp_path / "missing")["available"] is False


def test_review_readiness_api_is_read_only() -> None:
    server = DashboardServer(
        ("127.0.0.1", 0),
        DashboardStateStore(),
        None,
        research_source=ResearchSource(ROOT / "research"),
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        code, data = request_json(server, "GET", "/api/research/external-review")
        assert code == 200 and data["available"] is True
        code, _ = request_json(
            server, "POST", "/api/research/external-review", {"approved": True}
        )
        assert code >= 400
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
