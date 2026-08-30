"""Unified file manager for Research and Docs sources in the dashboard.

Provides a unified API over both ``research/`` and ``docs/`` directories
with proper MIME type detection, binary file serving, and directory trees.
"""

from __future__ import annotations

from http import HTTPStatus
from pathlib import Path
from typing import Any, cast
from urllib.parse import unquote

from .docs_source import DocumentationSource, create_docs_source
from .research_source import ResearchSource


# ---------------------------------------------------------------------------
# MIME type map
# ---------------------------------------------------------------------------

_MEDIA_TYPES: dict[str, str] = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".ogg": "video/ogg",
    ".mov": "video/quicktime",
    ".avi": "video/x-msvideo",
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".flac": "audio/flac",
    ".aac": "audio/aac",
    ".m4a": "audio/mp4",
    ".opus": "audio/opus",
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

_BINARY_EXTENSIONS = frozenset({
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg",
    ".mp4", ".webm", ".ogg", ".mov", ".avi",
    ".mp3", ".wav", ".flac", ".aac", ".m4a", ".opus",
    ".pdf", ".docx", ".xlsx", ".xls",
    ".ico", ".bmp",
})


def _mime_type(ext: str) -> str:
    return _MEDIA_TYPES.get(ext.lower(), "application/octet-stream")


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class FileManagerError(Exception):
    """Base error for file manager operations."""


class SourceNotAvailableError(FileManagerError):
    """Raised when a requested source is not configured."""


class InvalidSourceError(FileManagerError):
    """Raised when an unknown source name is given."""


class PathTraversalError(FileManagerError):
    """Raised on path traversal attempts."""


# ---------------------------------------------------------------------------
# File Manager
# ---------------------------------------------------------------------------


class FileManager:
    """Unified file manager for Research and Docs sources.

    Provides directory tree listing, file search, statistics, and
    content retrieval (text as JSON, binary as raw bytes).
    """

    def __init__(
        self,
        research_source: ResearchSource | None,
        docs_source: DocumentationSource | None,
        default_docs_root: Path,
    ) -> None:
        self._research = research_source
        self._docs = docs_source
        self._default_docs_root = default_docs_root

    # ------------------------------------------------------------------
    # Source resolution
    # ------------------------------------------------------------------

    def _resolve_source(self, source: str) -> tuple[Any, Path, str]:
        if source == "research":
            s = self._research
            if s is None or not s.is_available():
                raise SourceNotAvailableError("Research source is not configured.")
            return s, s.root(), "research"

        if source == "docs":
            s = self._docs or create_docs_source(self._default_docs_root)
            return s, s.docs_root, "docs"

        raise InvalidSourceError(f"Unknown source: {source}")

    # ------------------------------------------------------------------
    # Directory tree
    # ------------------------------------------------------------------

    def get_tree(self, source: str = "research") -> dict[str, Any]:
        """Return the full directory tree for a source."""
        try:
            _obj, root, _ = self._resolve_source(source)
        except FileManagerError as exc:
            return {"available": False, "error": str(exc), "children": []}

        def _build(path: Path, rel_prefix: str = "") -> dict[str, Any]:
            children: list[dict[str, Any]] = []
            try:
                entries = sorted(path.iterdir())
            except PermissionError:
                return {
                    "name": path.name,
                    "path": rel_prefix or ".",
                    "type": "directory",
                    "children": [],
                }

            for child in entries:
                if child.name.startswith("."):
                    continue
                if child.name in {"__pycache__", ".git", ".venv", "node_modules"}:
                    continue

                if child.is_dir():
                    child_rel = (
                        str(child.relative_to(root)) if child != root else ""
                    )
                    children.append(_build(child, child_rel))
                elif child.is_file():
                    ext = child.suffix.lower()
                    children.append({
                        "name": child.name,
                        "path": str(child.relative_to(root)),
                        "type": "file",
                        "size_bytes": child.stat().st_size,
                        "ext": ext,
                        "is_binary": ext in _BINARY_EXTENSIONS,
                        "is_image": ext in {
                            ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp",
                        },
                        "is_video": ext in {".mp4", ".webm", ".ogg", ".mov", ".avi"},
                        "is_audio": ext in {".mp3", ".wav", ".flac", ".aac", ".m4a", ".opus"},
                        "is_spreadsheet": ext in {".xlsx", ".xls", ".xlsm", ".ods"},
                        "is_document": ext in {".docx", ".doc"},
                    })

            return {
                "name": root.name if rel_prefix == "" else path.name,
                "path": rel_prefix or ".",
                "type": "directory",
                "children": children,
            }

        tree = _build(root)
        tree["available"] = True
        return tree

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, source: str, query: str) -> list[dict[str, Any]]:
        """Search files by name or path."""
        q = query.lower().strip()
        if not q or len(q) < 2:
            return []

        try:
            _obj, root, _ = self._resolve_source(source)
        except FileManagerError:
            return []

        results: list[dict[str, Any]] = []
        for f in sorted(root.rglob("*")):
            if not f.is_file() or f.name.startswith("."):
                continue
            rel = str(f.relative_to(root))
            if q in f.name.lower() or q in rel.lower():
                ext = f.suffix.lower()
                results.append({
                    "name": f.name,
                    "path": rel,
                    "size_bytes": f.stat().st_size,
                    "ext": ext,
                    "is_binary": ext in _BINARY_EXTENSIONS,
                })
        return results

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def get_statistics(self) -> dict[str, Any]:
        """Return combined statistics for both sources."""
        stats: dict[str, Any] = {}
        for src_name in ("research", "docs"):
            try:
                _obj, root, _ = self._resolve_source(src_name)
                total = 0
                total_size = 0
                for f in root.rglob("*"):
                    if f.is_file() and not f.name.startswith("."):
                        total += 1
                        total_size += f.stat().st_size
                stats[src_name] = {
                    "available": True,
                    "total_files": total,
                    "total_size_bytes": total_size,
                }
            except FileManagerError:
                stats[src_name] = {
                    "available": False,
                    "total_files": 0,
                    "total_size_bytes": 0,
                }
        return {"sources": stats}

    # ------------------------------------------------------------------
    # Content retrieval
    # ------------------------------------------------------------------

    def get_content(
        self, source: str, file_path: str
    ) -> tuple[bytes | str, str | None, bool]:
        """Get file content.

        Returns:
            Tuple of (content, mime_type_or_None, is_binary).
            For text files: (str, None, False).
            For binary files: (bytes, mime_type, True).
        """
        if not file_path or ".." in file_path:
            raise PathTraversalError("Path traversal is not allowed.")

        try:
            _obj, root, _ = self._resolve_source(source)
        except FileManagerError:
            raise SourceNotAvailableError(f"Source '{source}' is not available.")

        candidate = (root / file_path).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            raise PathTraversalError("Path traversal detected.")

        if not candidate.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = candidate.suffix.lower()

        if ext in _BINARY_EXTENSIONS:
            data = candidate.read_bytes()
            return data, _mime_type(ext), True

        content = candidate.read_text(encoding="utf-8", errors="replace")
        return content, None, False


# ---------------------------------------------------------------------------
# HTTP handler integration
# ---------------------------------------------------------------------------

_DEFAULT_DOCS_ROOT = Path(__file__).resolve().parents[2] / "docs"


def register_file_manager_routes(
    handler: Any,
    path: str,
    query: dict[str, list[str]],
    research_source: ResearchSource | None,
    docs_source: DocumentationSource | None,
) -> bool:
    """Try to handle a file manager API route. Returns True if handled."""
    fm = FileManager(research_source, docs_source, _DEFAULT_DOCS_ROOT)

    if path == "/api/files/tree":
        source = query.get("source", ["research"])[0]
        handler._send_json(cast(dict[str, Any], fm.get_tree(source)))
        return True

    if path == "/api/files/search":
        source = query.get("source", ["research"])[0]
        q = query.get("q", [""])[0]
        handler._send_json({"results": fm.search(source, q)})
        return True

    if path == "/api/files/statistics":
        handler._send_json(cast(dict[str, Any], fm.get_statistics()))
        return True

    if path == "/api/files/open":
        source = query.get("source", ["research"])[0]
        try:
            _obj, root, _name = fm._resolve_source(source)
            import subprocess
            import os
            if os.name == "nt":
                subprocess.Popen(["explorer", str(root.resolve())])
            else:
                subprocess.Popen(["xdg-open", str(root.resolve())])
            handler._send_json({"ok": True, "path": str(root.resolve())})
        except Exception as exc:
            handler._send_json({"ok": False, "error": str(exc)})
        return True

    if path.startswith("/api/files/content/"):
        prefix = "/api/files/content/"
        file_path = unquote(path[len(prefix):])
        source = query.get("source", ["research"])[0]

        try:
            content, mime, is_binary = fm.get_content(source, file_path)
        except FileNotFoundError:
            handler._send_json(
                {"error": f"File not found: {file_path}"},
                HTTPStatus.NOT_FOUND,
            )
            return True
        except (SourceNotAvailableError, PathTraversalError) as exc:
            status = HTTPStatus.NOT_FOUND if isinstance(exc, SourceNotAvailableError) else HTTPStatus.FORBIDDEN
            handler._send_json({"error": str(exc)}, status)
            return True
        except OSError as exc:
            handler._send_json(
                {"error": str(exc)},
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
            return True

        if is_binary and mime:
            data = cast(bytes, content)
            handler.send_response(HTTPStatus.OK)
            handler.send_header("Content-Type", mime)
            handler.send_header("Content-Length", str(len(data)))
            handler.send_header("Cache-Control", "no-cache")
            handler.send_header("Access-Control-Allow-Origin", "*")
            handler.end_headers()
            handler.wfile.write(data)
        else:
            text_content = cast(str, content)
            handler._send_json({
                "path": file_path,
                "name": Path(file_path).name,
                "content": text_content,
                "size_bytes": len(text_content.encode("utf-8")),
                "ext": Path(file_path).suffix.lower(),
                "is_binary": False,
            })
        return True

    return False
