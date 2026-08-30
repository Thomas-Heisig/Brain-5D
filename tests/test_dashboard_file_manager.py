"""Tests for the Brain-5D dashboard file manager save endpoints."""

import json
import tempfile
from http.client import HTTPConnection
from pathlib import Path
from threading import Thread
from typing import cast

from src.dashboard.docs_source import create_docs_source
from src.dashboard.server import DashboardServer
from src.dashboard.state import DashboardStateStore


class DummyBridge:
    pass


def _start_server(tmp_path: Path):
    store = DashboardStateStore()
    docs_root = tmp_path / "docs"
    docs_root.mkdir(parents=True, exist_ok=True)
    docs_source = create_docs_source(docs_root)
    server = DashboardServer(
        ("127.0.0.1", 0),
        store,
        None,
        DummyBridge(),  # type: ignore[arg-type]
        docs_source=docs_source,
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _request(conn: HTTPConnection, method: str, url: str, body: str | None = None):
    headers = {"Content-Type": "application/json"} if body else {}
    conn.request(method, url, body=body, headers=headers)
    return conn.getresponse()


def test_save_content_updates_text_file() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        file_path = docs_root / "notes.md"
        file_path.write_text("original", encoding="utf-8")

        server, thread = _start_server(tmp_path)
        address = cast(tuple[str, int], server.server_address)
        host, port = address
        try:
            conn = HTTPConnection(host, port)
            try:
                body = json.dumps({"content": "updated", "backup": True})
                response = _request(
                    conn,
                    "PUT",
                    "/api/files/save/notes.md?source=docs",
                    body=body,
                )
                data = json.loads(response.read())
                assert response.status == 200
                assert data["success"] is True
                assert file_path.read_text(encoding="utf-8") == "updated"
                assert (docs_root / "notes.md.bak").read_text(encoding="utf-8") == "original"
            finally:
                conn.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=1.0)


def test_save_content_rejects_traversal() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        (docs_root / "notes.md").write_text("original", encoding="utf-8")

        server, thread = _start_server(tmp_path)
        address = cast(tuple[str, int], server.server_address)
        host, port = address
        try:
            conn = HTTPConnection(host, port)
            try:
                body = json.dumps({"content": "evil", "backup": True})
                response = _request(
                    conn,
                    "PUT",
                    "/api/files/save/../notes.md?source=docs",
                    body=body,
                )
                assert response.status == 403
            finally:
                conn.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=1.0)


def test_save_content_rejects_missing_content() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        (docs_root / "notes.md").write_text("original", encoding="utf-8")

        server, thread = _start_server(tmp_path)
        address = cast(tuple[str, int], server.server_address)
        host, port = address
        try:
            conn = HTTPConnection(host, port)
            try:
                body = json.dumps({"backup": True})
                response = _request(
                    conn,
                    "PUT",
                    "/api/files/save/notes.md?source=docs",
                    body=body,
                )
                assert response.status == 400
            finally:
                conn.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=1.0)


def test_save_content_rejects_binary_extension() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        (docs_root / "image.png").write_bytes(b"\x89PNG")

        server, thread = _start_server(tmp_path)
        address = cast(tuple[str, int], server.server_address)
        host, port = address
        try:
            conn = HTTPConnection(host, port)
            try:
                body = json.dumps({"content": "not allowed", "backup": True})
                response = _request(
                    conn,
                    "PUT",
                    "/api/files/save/image.png?source=docs",
                    body=body,
                )
                assert response.status == 400
            finally:
                conn.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=1.0)


def test_save_content_creates_backup() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        file_path = docs_root / "notes.md"
        file_path.write_text("original", encoding="utf-8")

        server, thread = _start_server(tmp_path)
        address = cast(tuple[str, int], server.server_address)
        host, port = address
        try:
            conn = HTTPConnection(host, port)
            try:
                body = json.dumps({"content": "updated", "backup": True})
                response = _request(
                    conn,
                    "PUT",
                    "/api/files/save/notes.md?source=docs",
                    body=body,
                )
                assert response.status == 200
                assert (docs_root / "notes.md.bak").read_text(encoding="utf-8") == "original"
                assert file_path.read_text(encoding="utf-8") == "updated"
            finally:
                conn.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=1.0)


def test_meta_save_and_load() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        file_path = docs_root / "notes.md"
        file_path.write_text("content", encoding="utf-8")

        server, thread = _start_server(tmp_path)
        address = cast(tuple[str, int], server.server_address)
        host, port = address
        try:
            conn = HTTPConnection(host, port)
            try:
                body = json.dumps({"content": "status: reviewed\ntags: [dashboard]\n", "backup": True})
                response = _request(
                    conn,
                    "PUT",
                    "/api/files/meta/notes.md?source=docs",
                    body=body,
                )
                data = json.loads(response.read())
                assert response.status == 200
                assert data["success"] is True
                assert (docs_root / "notes.md.meta.yaml").read_text(encoding="utf-8") == "status: reviewed\ntags: [dashboard]\n"

                response = _request(conn, "GET", "/api/files/meta/notes.md?source=docs")
                data = json.loads(response.read())
                assert response.status == 200
                assert data["exists"] is True
                assert "reviewed" in data["content"]
            finally:
                conn.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=1.0)


def test_meta_rejects_missing_file() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        docs_root = tmp_path / "docs"
        docs_root.mkdir()

        server, thread = _start_server(tmp_path)
        address = cast(tuple[str, int], server.server_address)
        host, port = address
        try:
            conn = HTTPConnection(host, port)
            try:
                response = _request(conn, "GET", "/api/files/meta/missing.md?source=docs")
                assert response.status == 404
            finally:
                conn.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=1.0)


def test_analyze_returns_document_stats() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        file_path = docs_root / "report.md"
        file_path.write_text(
            "The quick brown fox jumps over the lazy dog. "
            "This is a great document with positive energy and excellent ideas.",
            encoding="utf-8",
        )

        server, thread = _start_server(tmp_path)
        address = cast(tuple[str, int], server.server_address)
        host, port = address
        try:
            conn = HTTPConnection(host, port)
            try:
                response = _request(conn, "GET", "/api/files/analyze/report.md?source=docs")
                data = json.loads(response.read())
                assert response.status == 200
                assert data["language"] == "en"
                assert data["stats"]["words"] > 0
                assert data["stats"]["sentences"] == 2
                assert data["sentiment"]["label"] == "positive"
                assert any(k["word"] == "document" for k in data["keywords"])
            finally:
                conn.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=1.0)


def test_analyze_rejects_binary_file() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        (docs_root / "image.png").write_bytes(b"\x89PNG")

        server, thread = _start_server(tmp_path)
        address = cast(tuple[str, int], server.server_address)
        host, port = address
        try:
            conn = HTTPConnection(host, port)
            try:
                response = _request(conn, "GET", "/api/files/analyze/image.png?source=docs")
                assert response.status == 400
            finally:
                conn.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=1.0)
