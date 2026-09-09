from __future__ import annotations

import base64
import json
from http.client import HTTPConnection
from pathlib import Path
from threading import Thread
from typing import Any, cast

from src.dashboard.server import DashboardServer
from src.dashboard.state import DashboardStateStore


def _server(tmp_path: Path) -> tuple[DashboardServer, Thread, str, int]:
    server = DashboardServer(
        ("127.0.0.1", 0),
        DashboardStateStore(),
        None,
        profiles_root=tmp_path / "profiles",
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    assert isinstance(host, str)
    return server, thread, host, int(port)


def _request(
    host: str,
    port: int,
    method: str,
    path: str,
    body: dict[str, Any] | None = None,
) -> tuple[int, dict[str, Any], bytes]:
    connection = HTTPConnection(host, port, timeout=5)
    try:
        raw = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {"Content-Type": "application/json"} if body is not None else {}
        connection.request(method, path, body=raw, headers=headers)
        response = connection.getresponse()
        content = response.read()
        try:
            parsed = cast(dict[str, Any], json.loads(content))
        except (json.JSONDecodeError, UnicodeDecodeError):
            parsed = {}
        return response.status, parsed, content
    finally:
        connection.close()


def test_profile_api_crud_load_snapshot_and_export_import(tmp_path: Path) -> None:
    server, thread, host, port = _server(tmp_path)
    try:
        status, created, _ = _request(
            host, port, "POST", "/api/profiles", {"name": "API Wesen"}
        )
        assert status == 201
        assert created["profile"]["profile_id"] == "WESEN-0001"

        status, listed, _ = _request(host, port, "GET", "/api/profiles")
        assert status == 200
        assert listed["count"] == 1

        status, updated, _ = _request(
            host,
            port,
            "PUT",
            "/api/profiles/WESEN-0001",
            {"name": "API Wesen Updated", "reason": "test"},
        )
        assert status == 200
        assert updated["profile"]["revision"] == 2

        status, _, _ = _request(
            host, port, "POST", "/api/profiles/WESEN-0001/load", {"with_state": False}
        )
        assert status == 200
        status, current, _ = _request(host, port, "GET", "/api/profiles/current")
        assert status == 200
        assert current["active"] is True

        snapshot = tmp_path / "state.b5d"
        snapshot.write_bytes(b"api snapshot")
        status, saved, _ = _request(
            host,
            port,
            "POST",
            "/api/profiles/WESEN-0001/save-state",
            {"snapshot_path": str(snapshot)},
        )
        assert status == 200
        assert saved["profile"]["snapshot_binding"]["digest"]

        status, _, exported = _request(
            host, port, "GET", "/api/profiles/WESEN-0001/export"
        )
        assert status == 200
        assert exported[:2] == b"PK"
        encoded = base64.b64encode(exported).decode("ascii")

        status, imported, _ = _request(
            host,
            port,
            "POST",
            "/api/profiles/import",
            {"archive_base64": encoded, "profile_id": "WESEN-0007"},
        )
        assert status == 200
        assert imported["profile"]["profile_id"] == "WESEN-0007"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=1)


def test_profile_api_save_current_runtime(tmp_path: Path) -> None:
    server, thread, host, port = _server(tmp_path)
    try:
        status, payload, _ = _request(
            host,
            port,
            "POST",
            "/api/profiles",
            {"name": "Runtime Identity", "source": "current_runtime"},
        )
        assert status == 201
        assert payload["profile"]["provenance"]["source"] == "current_runtime"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=1)


def test_profile_api_archive_clears_active_assignment(tmp_path: Path) -> None:
    server, thread, host, port = _server(tmp_path)
    try:
        _request(host, port, "POST", "/api/profiles", {"name": "Archive me"})
        _request(host, port, "POST", "/api/profiles/WESEN-0001/load", {})
        status, payload, _ = _request(
            host, port, "POST", "/api/profiles/WESEN-0001/archive", {}
        )
        assert status == 200
        assert payload["profile"]["status"] == "archived"
        _, current, _ = _request(host, port, "GET", "/api/profiles/current")
        assert current["active"] is False
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=1)


def test_profile_api_delete_is_blocked_for_active_or_bound_identity(
    tmp_path: Path,
) -> None:
    server, thread, host, port = _server(tmp_path)
    try:
        _request(host, port, "POST", "/api/profiles", {"name": "Protected"})
        _request(host, port, "POST", "/api/profiles/WESEN-0001/load", {})
        status, payload, _ = _request(host, port, "DELETE", "/api/profiles/WESEN-0001")
        assert status == 400
        assert "active" in payload["error"]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=1)
