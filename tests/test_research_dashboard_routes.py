"""HTTP route tests for the B5D-SEF research dashboard API."""

import json
from http.client import HTTPConnection
from pathlib import Path
from threading import Thread
from typing import Any, cast

from src.dashboard.research_source import ResearchSource  # type: ignore
from src.dashboard.server import DashboardServer
from src.dashboard.state import DashboardStateStore


def _start_server(
    research_root: Path | None,
) -> tuple[DashboardServer, Thread, str, int]:
    research_source: ResearchSource | None = (  # type: ignore
        ResearchSource(research_root) if research_root is not None else None
    )
    server = DashboardServer(
        ("127.0.0.1", 0),
        DashboardStateStore(),
        None,
        None,
        None,
        research_source,
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    if not isinstance(host, str):
        raise AssertionError("dashboard server did not expose an IP address")
    return server, thread, host, port


def _stop(server: DashboardServer, thread: Thread) -> None:
    server.shutdown()
    server.server_close()
    thread.join(timeout=1.0)


def _get(host: str, port: int, path: str) -> tuple[int, dict[str, Any]]:
    conn = HTTPConnection(host, port)
    try:
        conn.request("GET", path)
        resp = conn.getresponse()
        body = resp.read()
        return resp.status, cast(dict[str, Any], json.loads(body))
    finally:
        conn.close()


def test_research_summary_reports_available(tmp_path: Path) -> None:
    root = tmp_path / "research"
    (root / "generated").mkdir(parents=True)
    (root / "generated" / "RESEARCH_CATALOG.md").write_text(
        "# catalog", encoding="utf-8"
    )
    (root / "registry").mkdir()
    (root / "registry" / "questions.yaml").write_text("questions: []", encoding="utf-8")

    server, thread, host, port = _start_server(root)
    try:
        status, payload = _get(host, port, "/api/research")
        assert status == 200
        assert payload["available"] is True
        assert payload["categories"]["generated"] == 1
        assert payload["categories"]["registry"] == 1
    finally:
        _stop(server, thread)


def test_research_summary_reports_unavailable_without_source() -> None:
    server, thread, host, port = _start_server(None)
    try:
        status, payload = _get(host, port, "/api/research")
        assert status == 200
        assert payload["available"] is False
    finally:
        _stop(server, thread)


def test_research_reports_list(tmp_path: Path) -> None:
    root = tmp_path / "research"
    (root / "generated").mkdir(parents=True)
    (root / "generated" / "RESEARCH_CATALOG.md").write_text(
        "# catalog", encoding="utf-8"
    )
    (root / "generated" / "EVIDENCE_MATRIX.md").write_text("# matrix", encoding="utf-8")

    server, thread, host, port = _start_server(root)
    try:
        status, payload = _get(host, port, "/api/research/reports")
        assert status == 200
        names = [r["name"] for r in payload["reports"]]
        assert "RESEARCH_CATALOG" in names
        assert "EVIDENCE_MATRIX" in names
    finally:
        _stop(server, thread)


def test_research_file_content(tmp_path: Path) -> None:
    root = tmp_path / "research"
    (root / "generated").mkdir(parents=True)
    (root / "generated" / "REPORT.md").write_text("# test content", encoding="utf-8")

    server, thread, host, port = _start_server(root)
    try:
        status, payload = _get(host, port, "/api/research-files/generated/REPORT.md")
        assert status == 200
        assert payload["content"] == "# test content"
    finally:
        _stop(server, thread)


def test_research_file_path_traversal_rejected(tmp_path: Path) -> None:
    root = tmp_path / "research"
    (root / "generated").mkdir(parents=True)
    (root / "generated" / "REPORT.md").write_text("secret", encoding="utf-8")

    server, thread, host, port = _start_server(root)
    try:
        status, _payload = _get(host, port, "/api/research-files/../secret.md")
        assert status in (400, 404)
    finally:
        _stop(server, thread)


def test_unknown_research_subpath_returns_json_404(tmp_path: Path) -> None:
    root = tmp_path / "research"
    (root / "generated").mkdir(parents=True)

    server, thread, host, port = _start_server(root)
    try:
        status, payload = _get(
            host, port, "/api/research-files/generated/nonexistent.md"
        )
        assert status == 404
        assert "error" in payload
    finally:
        _stop(server, thread)
