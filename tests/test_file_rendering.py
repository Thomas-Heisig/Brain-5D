"""Real file service contracts shared by File Viewer and chat."""

from __future__ import annotations

import json
import zipfile
from collections.abc import Iterator
from http.client import HTTPConnection
from pathlib import Path
from threading import Thread
from typing import Any

import pytest

from src.dashboard.docs_source import create_docs_source
from src.dashboard.file_rendering import (
    PREVIEW_BYTES,
    FileContractError,
    FilePreviewService,
)
from src.dashboard.research_source import ResearchSource
from src.dashboard.server import DashboardServer
from src.dashboard.state import DashboardStateStore


@pytest.fixture
def service(tmp_path: Path) -> FilePreviewService:
    for source in ("docs", "research"):
        (tmp_path / source).mkdir()
    return FilePreviewService(
        {"docs": tmp_path / "docs", "research": tmp_path / "research"}
    )


def test_create_write_rename_and_recoverable_trash(service: FilePreviewService) -> None:
    first = service.mutate(
        "docs", "notes/a.md", {"action": "create", "content": "# Exact\n"}
    )["file"]
    assert first["kind"] == "markdown"
    assert first["editable"] is True
    assert first["digest_status"] == "COMPLETE"
    changed = service.mutate(
        "docs",
        "notes/a.md",
        {"content": "# Updated\n", "expected_sha256": first["sha256"]},
    )["file"]
    assert changed["sha256"] != first["sha256"]
    assert (service.roots["docs"] / "notes/a.md.bak").read_text() == "# Exact\n"
    with pytest.raises(FileContractError, match="version changed"):
        service.mutate(
            "docs",
            "notes/a.md",
            {"content": "obsolete", "expected_sha256": first["sha256"]},
        )
    renamed = service.mutate(
        "docs",
        "notes/a.md",
        {
            "action": "rename",
            "destination": "notes/b.md",
            "expected_sha256": changed["sha256"],
        },
    )["file"]
    assert renamed["path"] == "notes/b.md"
    assert renamed["sha256"] == changed["sha256"]
    trashed = service.mutate(
        "docs", "notes/b.md", {"action": "trash", "expected_sha256": renamed["sha256"]}
    )
    assert trashed["recoverable"] is True
    assert not (service.roots["docs"] / "notes/b.md").exists()
    assert (
        next((service.roots["docs"] / ".trash").iterdir()).read_text() == "# Updated\n"
    )


@pytest.mark.parametrize(
    "path",
    [
        "../secret",
        "/etc/passwd",
        "a/../../secret",
        "C:/secret",
        ".git/config",
        "a/.secret",
        "a\\secret",
        "a\x00b",
    ],
)
def test_path_traversal_rejected(service: FilePreviewService, path: str) -> None:
    with pytest.raises(FileContractError) as raised:
        service.resolve("docs", path, must_exist=False)
    assert raised.value.status == 403


@pytest.mark.parametrize(
    "directory",
    [
        "experiments",
        "archive",
        "registry",
        "preregistrations",
        "protocols",
        "schemas",
        "workflows",
        "generated",
    ],
)
def test_scientific_files_cannot_be_mutated(
    service: FilePreviewService, directory: str
) -> None:
    path = f"{directory}/result.json"
    target = service.roots["research"] / path
    target.parent.mkdir()
    target.write_text('{"original": true}')
    before = target.read_bytes()
    preview = service.preview("research", path)
    assert preview["read_only"] is True
    for action in ("write", "rename", "trash"):
        with pytest.raises(FileContractError) as raised:
            service.mutate(
                "research",
                path,
                {
                    "action": action,
                    "content": "changed",
                    "expected_sha256": preview["sha256"],
                    "destination": "notes/moved.json",
                },
            )
        assert raised.value.status == 403
        assert target.read_bytes() == before


def test_create_and_rename_never_overwrite(service: FilePreviewService) -> None:
    first = service.mutate("docs", "a.txt", {"action": "create", "content": "a"})[
        "file"
    ]
    service.mutate("docs", "b.txt", {"action": "create", "content": "b"})
    for path, body in [
        ("a.txt", {"action": "create", "content": "c"}),
        (
            "a.txt",
            {
                "action": "rename",
                "destination": "b.txt",
                "expected_sha256": first["sha256"],
            },
        ),
    ]:
        with pytest.raises(FileContractError) as raised:
            service.mutate("docs", path, body)
        assert raised.value.status == 409
    assert (service.roots["docs"] / "b.txt").read_text() == "b"


def test_symlink_escape_and_backup_symlink_rejected(
    service: FilePreviewService, tmp_path: Path
) -> None:
    secret = tmp_path / "secret.txt"
    secret.write_text("private")
    link = service.roots["docs"] / "escape.txt"
    try:
        link.symlink_to(secret)
    except OSError:
        pytest.skip("Host does not permit creating test symlinks")
    with pytest.raises(FileContractError):
        service.preview("docs", "escape.txt")
    first = service.mutate(
        "docs", "normal.txt", {"action": "create", "content": "safe"}
    )["file"]
    (service.roots["docs"] / "normal.txt.bak").symlink_to(secret)
    with pytest.raises(FileContractError):
        service.mutate(
            "docs", "normal.txt", {"content": "new", "expected_sha256": first["sha256"]}
        )
    assert secret.read_text() == "private"


def test_bounded_preview_retains_complete_original(
    service: FilePreviewService, monkeypatch: pytest.MonkeyPatch
) -> None:
    from src.dashboard import file_rendering

    monkeypatch.setattr(file_rendering, "DIGEST_BYTES", 128)
    target = service.roots["docs"] / "large.jsonl"
    target.write_bytes(b'{"value": 123}\n' * PREVIEW_BYTES)
    size = target.stat().st_size
    preview = service.preview("docs", target.name)
    assert len(preview["content"].encode()) <= PREVIEW_BYTES
    assert preview["truncated"] is True
    assert preview["editable"] is False
    assert preview["sha256"] is None
    assert preview["digest_status"] == "NOT_COMPUTED_SIZE_LIMIT"
    assert target.stat().st_size == size


def test_json_pretty_preview_keeps_exact_editor_source(
    service: FilePreviewService,
) -> None:
    target = service.roots["docs"] / "data.json"
    original = '{"value":1, "ordered":[1,2]}\n'
    target.write_text(original)
    preview = service.preview("docs", target.name)
    assert preview["raw_content"] == original
    assert json.loads(preview["content"])["value"] == 1


def test_csv_quoted_cells_and_binary_fallback(service: FilePreviewService) -> None:
    (service.roots["docs"] / "data.csv").write_text('name,value\n"a,b",3\n')
    preview = service.preview("docs", "data.csv")
    assert preview["kind"] == "table"
    assert preview["rows"][1] == ["a,b", "3"]
    (service.roots["docs"] / "state.b5d").write_bytes(b"B5D\x00\xff")
    binary = service.preview("docs", "state.b5d")
    assert binary["kind"] == "binary"
    assert binary["editable"] is False
    assert binary["download_url"]


def test_unsafe_document_xml_never_expands_entities(
    service: FilePreviewService,
) -> None:
    target = service.roots["docs"] / "unsafe.docx"
    with zipfile.ZipFile(target, "w") as archive:
        archive.writestr(
            "word/document.xml",
            '<!DOCTYPE x [<!ENTITY e SYSTEM "file:///etc/passwd">]><x>&e;</x>',
        )
    result = service.preview("docs", target.name)
    assert result["kind"] == "binary"
    assert "Unsafe" in result["notice"]
    assert result["content"] == ""


@pytest.fixture
def server(service: FilePreviewService) -> Iterator[DashboardServer]:
    instance = DashboardServer(
        ("127.0.0.1", 0),
        DashboardStateStore(),
        None,
        None,
        docs_source=create_docs_source(service.roots["docs"]),
        research_source=ResearchSource(service.roots["research"]),
    )
    thread = Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    try:
        yield instance
    finally:
        instance.shutdown()
        instance.server_close()
        thread.join(timeout=3)


def request(
    server: DashboardServer,
    method: str,
    path: str,
    body: object = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, bytes, dict[str, str]]:
    host, port = server.server_address[:2]
    assert isinstance(host, str) and isinstance(port, int)
    connection = HTTPConnection(host, port, timeout=5)
    try:
        connection.request(
            method,
            path,
            body=json.dumps(body) if body is not None else None,
            headers=headers or {},
        )
        response = connection.getresponse()
        return response.status, response.read(), dict(response.getheaders())
    finally:
        connection.close()


def test_actual_http_preview_range_and_origin_contract(
    server: DashboardServer, service: FilePreviewService
) -> None:
    (service.roots["docs"] / "notes.md").write_text("# Original\n")
    status, data, _ = request(server, "GET", "/api/files/preview/notes.md?source=docs")
    assert status == 200
    preview: dict[str, Any] = json.loads(data)
    assert preview["kind"] == "markdown"
    status, data, headers = request(
        server,
        "GET",
        "/api/files/raw/notes.md?source=docs",
        headers={"Range": "bytes=0-4"},
    )
    assert (status, data) == (206, b"# Ori")
    assert headers["Content-Range"] == "bytes 0-4/11"
    status, _, _ = request(
        server,
        "PUT",
        "/api/files/document/notes.md?source=docs",
        {"content": "changed", "expected_sha256": preview["sha256"]},
        {"Origin": "https://untrusted.example"},
    )
    assert status == 403
    assert (service.roots["docs"] / "notes.md").read_text() == "# Original\n"
    status, _, _ = request(
        server, "PUT", "/api/files/document/notes.md?source=docs", {"action": []}
    )
    assert status == 400
    status, _, _ = request(
        server,
        "GET",
        "/api/files/raw/notes.md?source=docs",
        headers={"Range": "bytes=900-901"},
    )
    assert status == 416


def test_active_content_download_is_sandboxed(
    server: DashboardServer, service: FilePreviewService
) -> None:
    (service.roots["docs"] / "unsafe.html").write_text(
        '<script>alert("not executed")</script>'
    )
    status, _, headers = request(
        server, "GET", "/api/files/raw/unsafe.html?source=docs"
    )
    assert status == 200
    assert "attachment" in headers["Content-Disposition"]
    assert "sandbox" in headers["Content-Security-Policy"]
    assert headers["X-Content-Type-Options"] == "nosniff"


def test_internal_symlink_cannot_bypass_research_protection(
    service: FilePreviewService,
) -> None:
    original = service.roots["research"] / "experiments" / "result.json"
    original.parent.mkdir()
    original.write_text("{}")
    alias = service.roots["research"] / "alias.json"
    try:
        alias.symlink_to(original)
    except OSError:
        pytest.skip("Host cannot create symlinks")
    with pytest.raises(FileContractError):
        service.preview("research", "alias.json")
    with pytest.raises(FileContractError):
        service.mutate(
            "research", "alias.json", {"content": "changed", "action": "write"}
        )
    assert original.read_text() == "{}"


def test_remote_file_writes_require_explicit_authorization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from types import SimpleNamespace

    from src.dashboard.file_rendering import validate_file_write_access

    request = SimpleNamespace(
        client_address=("192.0.2.1", 1234), headers={"Host": "example.test"}
    )
    monkeypatch.delenv("BRAIN5D_FILE_WRITE_TOKEN", raising=False)
    with pytest.raises(FileContractError):
        validate_file_write_access(request)
    monkeypatch.setenv("BRAIN5D_FILE_WRITE_TOKEN", "explicit-test-credential")
    with pytest.raises(FileContractError):
        validate_file_write_access(request)
    request.headers["Authorization"] = "Bearer explicit-test-credential"
    validate_file_write_access(request)
