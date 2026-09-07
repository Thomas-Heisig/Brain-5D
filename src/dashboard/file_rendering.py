"""Bounded, provenance-bearing file previews shared by the viewer and chat.

Preview conversion never changes the original. Active HTML, SVG and notebook
outputs are not executed. Scientific records are immutable through this API.
"""

from __future__ import annotations

import csv
import hashlib
import io
import ipaddress
import json
import mimetypes
import os
import re
import secrets
import shutil
import tempfile
import threading
import time
import zipfile
from collections.abc import Mapping
from http import HTTPStatus
from pathlib import Path, PurePosixPath
from typing import Any, cast
from urllib.parse import quote, unquote, urlparse
from xml.etree import ElementTree

PREVIEW_BYTES = 256 * 1024
EDIT_BYTES = 1024 * 1024
DIGEST_BYTES = 64 * 1024 * 1024
ARCHIVE_BYTES = 32 * 1024 * 1024
TEXT_EXTENSIONS = frozenset(
    ".md .markdown .txt .text .json .jsonl .ndjson .yaml .yml .toml .csv .tsv "
    ".py .js .mjs .ts .tsx .jsx .css .html .xml .svg .bib .tex .rst .log .ini "
    ".cfg .conf .sh .bat .cmd .ps1 .sql .ipynb .dot .puml .plantuml .diff .patch "
    ".c .h .cpp .hpp .rs .go .java .kt .r .properties".split()
)
_PROTECTED_RESEARCH = frozenset(
    {
        "experiments",
        "archive",
        "registry",
        "preregistrations",
        "protocols",
        "schemas",
        "workflows",
        "generated",
    }
)
_MUTATION_LOCK = threading.RLock()


class FileContractError(ValueError):
    """A file request violates the renderer's public contract."""

    def __init__(self, message: str, status: HTTPStatus = HTTPStatus.BAD_REQUEST):
        super().__init__(message)
        self.status = status


def _sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def file_is_read_only(source: str, path: str) -> bool:
    """Preserve scientific provenance even when a file is otherwise editable."""
    parts = PurePosixPath(path.replace("\\", "/")).parts
    return source == "research" and bool(parts and parts[0] in _PROTECTED_RESEARCH)


def validate_file_write_access(handler: Any) -> None:
    """Remote deployments are read-only unless an explicit bearer token is used."""
    origin = handler.headers.get("Origin")
    if origin and urlparse(str(origin)).netloc != handler.headers.get("Host"):
        raise FileContractError(
            "Cross-origin file changes are forbidden", HTTPStatus.FORBIDDEN
        )
    peer = str(handler.client_address[0])
    local = ipaddress.ip_address(peer).is_loopback
    proxied = any(
        handler.headers.get(name)
        for name in ("Forwarded", "X-Forwarded-For", "X-Real-IP")
    )
    if local and not proxied:
        return
    token = os.environ.get("BRAIN5D_FILE_WRITE_TOKEN", "")
    supplied = str(handler.headers.get("Authorization", ""))
    if not token or not secrets.compare_digest(supplied, "Bearer " + token):
        raise FileContractError(
            "Remote file management requires explicit authorization",
            HTTPStatus.FORBIDDEN,
        )


def atomic_write(path: Path, data: bytes) -> None:
    """Replace a file on its own filesystem without a missing-file window."""
    mode = path.stat().st_mode & 0o777 if path.is_file() else None
    fd, temporary = tempfile.mkstemp(prefix=".brain5d-write-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            if mode is not None:
                os.chmod(temporary, mode)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class FilePreviewService:
    """One source/path contract for every frontend file-rendering context."""

    def __init__(self, roots: Mapping[str, Path]):
        self.roots = {name: root.resolve() for name, root in roots.items()}

    def resolve(self, source: str, path: str, *, must_exist: bool = True) -> Path:
        """Reject absolute paths, symlink escapes and hidden management files."""
        if source not in self.roots:
            raise FileContractError("Unknown file source", HTTPStatus.NOT_FOUND)
        parts = PurePosixPath(path).parts
        if (
            not parts
            or path.startswith("/")
            or "\\" in path
            or ":" in path
            or "\x00" in path
            or any(part in {"..", ".git"} or part.startswith(".") for part in parts)
        ):
            raise FileContractError(
                "Path traversal is not allowed", HTTPStatus.FORBIDDEN
            )
        root = self.roots[source]
        candidate = (root / path).resolve()
        if not candidate.is_relative_to(root):
            raise FileContractError("Path escapes file source", HTTPStatus.FORBIDDEN)
        if candidate != root.joinpath(*parts):
            raise FileContractError(
                "Symbolic file references are not allowed", HTTPStatus.FORBIDDEN
            )
        if must_exist and not candidate.is_file():
            raise FileContractError("File not found", HTTPStatus.NOT_FOUND)
        return candidate

    @staticmethod
    def _office_text(path: Path) -> str:
        """Extract bounded OOXML text, without macros, formulas or remote links."""
        with zipfile.ZipFile(path) as archive:
            members = archive.infolist()
            if (
                len(members) > 2048
                or sum(item.file_size for item in members) > ARCHIVE_BYTES
            ):
                raise FileContractError("Archive exceeds preview expansion limit")
            names = archive.namelist()
            if path.suffix.lower() in {".xlsx", ".xlsm"}:
                selected = [
                    name
                    for name in names
                    if name == "xl/sharedStrings.xml"
                    or re.fullmatch(r"xl/worksheets/sheet\d+\.xml", name)
                ]
            elif path.suffix.lower() == ".pptx":
                selected = sorted(
                    name
                    for name in names
                    if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
                )
            else:
                selected = ["word/document.xml"]
            lines: list[str] = []
            total = 0
            for name in selected[:32]:
                if name not in names:
                    continue
                raw = archive.read(name)
                if (
                    len(raw) > 8 * PREVIEW_BYTES
                    or b"<!DOCTYPE" in raw.upper()
                    or b"<!ENTITY" in raw.upper()
                ):
                    raise FileContractError("Unsafe or oversized document XML")
                tree = ElementTree.fromstring(raw)
                lines.append(name)
                for node in tree.iter():
                    if node.tag.rsplit("}", 1)[-1] in {"t", "v", "f"} and node.text:
                        value = node.text[:2000]
                        total += len(value)
                        lines.append(value)
                        if total >= PREVIEW_BYTES:
                            return "\n".join(lines)[:PREVIEW_BYTES]
            return "\n".join(lines)[:PREVIEW_BYTES]

    def preview(self, source: str, path: str) -> dict[str, Any]:
        """Produce a bounded rendering descriptor; never load a whole large file."""
        candidate = self.resolve(source, path)
        stat = candidate.stat()
        ext = candidate.suffix.lower()
        mime = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
        url = f"/api/files/raw/{quote(path, safe='')}?source={quote(source)}"
        digest = _sha256(candidate) if stat.st_size <= DIGEST_BYTES else None
        result: dict[str, Any] = {
            "schema_version": "1.0",
            "renderer_version": "1.0",
            "source": source,
            "path": path,
            "name": candidate.name,
            "mime_type": mime,
            "ext": ext,
            "size_bytes": stat.st_size,
            "modified_ns": stat.st_mtime_ns,
            "sha256": digest,
            "digest_status": "COMPLETE" if digest else "NOT_COMPUTED_SIZE_LIMIT",
            "preview_limit_bytes": PREVIEW_BYTES,
            "truncated": False,
            "raw_url": url,
            "download_url": url + "&download=1",
            "read_only": file_is_read_only(source, path),
            "editable": False,
            "kind": "binary",
            "content": "",
            "notice": "",
        }
        if mime.startswith(("image/", "audio/", "video/")) and ext not in {
            ".svg",
            ".html",
        }:
            result["kind"] = mime.split("/", 1)[0]
        elif ext == ".pdf":
            result["kind"] = "pdf"
        elif ext in {".docx", ".pptx", ".xlsx", ".xlsm"}:
            try:
                result["content"] = self._office_text(candidate)
                result["kind"] = "text"
                result["truncated"] = len(result["content"]) >= PREVIEW_BYTES
                result["notice"] = (
                    "Extracted document text; layout and spreadsheet cell relationships are available in the original download. Formulas are never executed."
                )
            except (
                FileContractError,
                OSError,
                ValueError,
                KeyError,
                zipfile.BadZipFile,
                ElementTree.ParseError,
            ) as exc:
                result["notice"] = (
                    f"Document preview unavailable: {exc}. Original download remains available."
                )
        else:
            with candidate.open("rb") as stream:
                raw = stream.read(PREVIEW_BYTES + 1)
            if b"\x00" not in raw[:8192]:
                try:
                    content = raw[:PREVIEW_BYTES].decode("utf-8", errors="strict")
                except UnicodeDecodeError:
                    # A preview can split the final UTF-8 character, never silently
                    # replace arbitrary binary data with apparent scientific text.
                    content = ""
                    if stat.st_size > PREVIEW_BYTES:
                        for trim in range(1, 4):
                            try:
                                content = raw[: PREVIEW_BYTES - trim].decode("utf-8")
                                break
                            except UnicodeDecodeError:
                                continue
                else:
                    result["kind"] = "text"
                if content:
                    result["kind"] = "text"
                if result["kind"] == "text":
                    result["content"] = content
                    result["raw_content"] = content
                    result["truncated"] = len(raw) > PREVIEW_BYTES
                    result["editable"] = (
                        not result["read_only"]
                        and not result["truncated"]
                        and stat.st_size <= EDIT_BYTES
                        and (ext in TEXT_EXTENSIONS or not ext)
                    )
                    result["kind"] = (
                        "markdown" if ext in {".md", ".markdown"} else "text"
                    )
                    if ext == ".json" and not result["truncated"]:
                        try:
                            result["content"] = json.dumps(
                                json.loads(content), ensure_ascii=False, indent=2
                            )
                            result["kind"] = "json"
                        except (ValueError, RecursionError):
                            result["notice"] = (
                                "Invalid JSON; showing exact source text."
                            )
                    if ext in {".csv", ".tsv"}:
                        rows: list[list[str]] = []
                        for index, row in enumerate(
                            csv.reader(
                                io.StringIO(content),
                                delimiter="\t" if ext == ".tsv" else ",",
                            )
                        ):
                            if index >= 500:
                                result["truncated"] = True
                                break
                            rows.append([cell[:2000] for cell in row[:64]])
                            if len(row) > 64 or any(len(cell) > 2000 for cell in row):
                                result["truncated"] = True
                        result["rows"] = rows
                        result["kind"] = "table"
        if candidate.stat().st_mtime_ns != stat.st_mtime_ns:
            raise FileContractError(
                "File changed while reading; retry", HTTPStatus.CONFLICT
            )
        return result

    def mutate(
        self, source: str, path: str, body: Mapping[str, object]
    ) -> dict[str, Any]:
        """Explicit create/write/rename/trash operations with optimistic locking."""
        with _MUTATION_LOCK:
            return self._mutate_locked(source, path, body)

    def _mutate_locked(
        self, source: str, path: str, body: Mapping[str, object]
    ) -> dict[str, Any]:
        action = body.get("action", "write")
        if not isinstance(action, str) or action not in {
            "create",
            "write",
            "rename",
            "trash",
        }:
            raise FileContractError("Unknown file action")
        candidate = self.resolve(source, path, must_exist=action != "create")
        if file_is_read_only(source, path):
            raise FileContractError(
                "Scientific artifacts are immutable; use the registered review/archive workflow",
                HTTPStatus.FORBIDDEN,
            )
        if action == "create" and candidate.exists():
            raise FileContractError("File already exists", HTTPStatus.CONFLICT)
        if action != "create":
            if candidate.stat().st_size > DIGEST_BYTES:
                raise FileContractError(
                    "Large files require an external managed file workflow"
                )
            if body.get("expected_sha256") != _sha256(candidate):
                raise FileContractError(
                    "File version changed; reload before saving", HTTPStatus.CONFLICT
                )
        if action in {"create", "write"}:
            content = body.get("content")
            if (
                not isinstance(content, str)
                or len(content.encode("utf-8")) > EDIT_BYTES
            ):
                raise FileContractError("UTF-8 text content must be at most 1 MiB")
            if candidate.suffix.lower() not in TEXT_EXTENSIONS:
                raise FileContractError("This file type cannot be edited as text")
            if action == "write":
                backup = candidate.with_name(candidate.name + ".bak")
                if backup.is_symlink():
                    raise FileContractError(
                        "Symlink backup is not allowed", HTTPStatus.FORBIDDEN
                    )
                shutil.copyfile(candidate, backup)
            candidate.parent.mkdir(parents=True, exist_ok=True)
            atomic_write(candidate, content.encode("utf-8"))
        elif action == "rename":
            destination = body.get("destination")
            if not isinstance(destination, str):
                raise FileContractError("Rename requires a destination")
            target = self.resolve(source, destination, must_exist=False)
            if target.exists() or file_is_read_only(source, destination):
                raise FileContractError(
                    "Destination exists or is protected", HTTPStatus.CONFLICT
                )
            target.parent.mkdir(parents=True, exist_ok=True)
            candidate.rename(target)
            path = destination
        else:
            trash = self.roots[source] / ".trash"
            if trash.is_symlink():
                raise FileContractError("Invalid trash directory", HTTPStatus.FORBIDDEN)
            trash.mkdir(exist_ok=True)
            target = trash / f"{time.time_ns()}-{candidate.name}"
            candidate.rename(target)
            return {"ok": True, "action": "trash", "path": path, "recoverable": True}
        return {"ok": True, "action": action, "file": self.preview(source, path)}


def handle_file_rendering(
    handler: Any, path: str, query: dict[str, list[str]], roots: Mapping[str, Path]
) -> bool:
    """Serve descriptors, bounded streaming/ranges and explicit same-origin edits."""
    match = re.fullmatch(r"/api/files/(preview|raw|document)/(.+)", path)
    if not match:
        return False
    kind, encoded = match.groups()
    source = query.get("source", ["research"])[0]
    file_path = unquote(encoded)
    service = FilePreviewService(roots)
    try:
        if kind == "document" and handler.command == "PUT":
            validate_file_write_access(handler)
            origin = handler.headers.get("Origin")
            if origin and urlparse(str(origin)).netloc != handler.headers.get("Host"):
                raise FileContractError(
                    "Cross-origin file changes are forbidden", HTTPStatus.FORBIDDEN
                )
            value: object = handler._read_json_body(max_size=EDIT_BYTES * 6 + 4096)
            if not isinstance(value, dict):
                raise FileContractError("File request must be a JSON object")
            body = cast(dict[str, object], value)
            handler._send_json(service.mutate(source, file_path, body))
        elif kind == "preview" and handler.command == "GET":
            handler._send_json(service.preview(source, file_path))
        elif kind == "raw" and handler.command == "GET":
            candidate = service.resolve(source, file_path)
            size = candidate.stat().st_size
            start, end = 0, size - 1
            range_value = handler.headers.get("Range")
            if range_value:
                parsed = re.fullmatch(r"bytes=(\d*)-(\d*)", str(range_value))
                if not parsed or not any(parsed.groups()):
                    raise FileContractError(
                        "Invalid byte range", HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE
                    )
                first, last = parsed.groups()
                start = int(first) if first else max(0, size - int(last))
                end = min(int(last), size - 1) if first and last else size - 1
                if start < 0 or start > end or start >= size:
                    raise FileContractError(
                        "Byte range outside file",
                        HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE,
                    )
            mime = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
            handler.send_response(
                HTTPStatus.PARTIAL_CONTENT if range_value else HTTPStatus.OK
            )
            handler.send_header("Content-Type", mime)
            handler.send_header("X-Content-Type-Options", "nosniff")
            handler.send_header(
                "Content-Security-Policy", "sandbox; default-src 'none'"
            )
            handler.send_header("Accept-Ranges", "bytes")
            handler.send_header("Content-Length", str(max(0, end - start + 1)))
            handler.send_header("Cache-Control", "no-store")
            if range_value:
                handler.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            disposition = (
                "attachment"
                if query.get("download") == ["1"]
                or mime in {"text/html", "image/svg+xml", "application/octet-stream"}
                else "inline"
            )
            handler.send_header(
                "Content-Disposition",
                f"{disposition}; filename*=UTF-8''{quote(candidate.name)}",
            )
            handler.end_headers()
            with candidate.open("rb") as stream:
                stream.seek(start)
                remaining = end - start + 1
                while remaining > 0:
                    chunk = stream.read(min(64 * 1024, remaining))
                    if not chunk:
                        break
                    handler.wfile.write(chunk)
                    remaining -= len(chunk)
        else:
            raise FileContractError("Unsupported method", HTTPStatus.METHOD_NOT_ALLOWED)
    except FileContractError as exc:
        handler._send_json({"error": str(exc)}, exc.status)
    except (OSError, ValueError, csv.Error) as exc:
        handler._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
    return True
