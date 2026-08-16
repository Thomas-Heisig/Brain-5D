"""Dependency-free local HTTP server for the Brain-5D operator dashboard."""

from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .heatmap_source import SnapshotHeatmapSource
from .models import JSONValue
from .state import DashboardStateStore

_STATIC_ROOT = Path(__file__).with_name("static")
_DOCS_ROOT = Path(__file__).resolve().parents[2] / "docs"


class DashboardServer(ThreadingHTTPServer):
    """HTTP server carrying typed dashboard dependencies."""

    def __init__(
        self,
        address: tuple[str, int],
        state: DashboardStateStore,
        heatmaps: SnapshotHeatmapSource | None,
    ) -> None:
        super().__init__(address, DashboardRequestHandler)
        self.dashboard_state = state
        self.heatmap_source = heatmaps


class DashboardRequestHandler(BaseHTTPRequestHandler):
    """Serve the dashboard application and read-only JSON endpoints."""

    server_version = "Brain5DDashboard/0.5.0-alpha.1"

    def do_GET(self) -> None:  # pylint: disable=invalid-name
        """Serve one read-only request using the stdlib handler contract."""
        server = self.server
        if not isinstance(server, DashboardServer):
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR)
            return
        parsed = urlparse(self.path)
        if parsed.path == "/api/status":
            self._send_json(server.dashboard_state.snapshot().to_json())
            return
        if parsed.path == "/api/heatmap":
            self._serve_heatmap(server, parse_qs(parsed.query))
            return
        if parsed.path == "/api/snapshots":
            self._serve_snapshots()
            return
        if parsed.path == "/api/docs":
            query = parse_qs(parsed.query)
            names = query.get("name")
            if names:
                self._serve_doc(names[0])
            else:
                self._serve_docs()
            return
        if parsed.path == "/healthz":
            self._send_json({"status": "ok"})
            return
        self._serve_static(parsed.path)

    def log_message(self, format: str, *args: object) -> None:
        """Keep the local operator console quiet by default."""
        _ = (format, args)

    def _serve_heatmap(
        self,
        server: DashboardServer,
        query: dict[str, list[str]],
    ) -> None:
        source = server.heatmap_source
        if source is None:
            self._send_json(
                {"error": "No .b5d snapshot configured for heatmaps."},
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return
        kind = query.get("kind", ["activity"])[0]
        try:
            payload = source.build(kind)
        except (ValueError, OSError) as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return
        self._send_json(payload.to_json())

    def _serve_snapshots(self) -> None:
        """List available `.b5d` snapshots newest first."""
        artifacts = Path("artifacts")
        paths = (
            sorted(
                artifacts.glob("*.b5d"),
                key=lambda path: path.stat().st_mtime,
                reverse=True,
            )
            if artifacts.exists()
            else []
        )
        snapshots: list[JSONValue] = []
        for path in paths:
            stat = path.stat()
            snapshots.append(
                {
                    "name": path.name,
                    "path": str(path),
                    "size": stat.st_size,
                    "mtime": stat.st_mtime,
                }
            )
        self._send_json({"snapshots": snapshots})

    def _serve_docs(self) -> None:
        """List all Markdown documents without serving arbitrary paths."""
        documents: list[JSONValue] = []
        if _DOCS_ROOT.exists():
            for path in sorted(_DOCS_ROOT.glob("*.md")):
                stat = path.stat()
                documents.append(
                    {
                        "name": path.name,
                        "size": stat.st_size,
                        "mtime": stat.st_mtime,
                    }
                )
        self._send_json({"documents": documents})

    def _serve_doc(self, name: str) -> None:
        """Serve one Markdown document after strict path validation."""
        if ".." in name or "/" in name or "\\" in name or not name.endswith(".md"):
            self.send_error(HTTPStatus.BAD_REQUEST)
            return
        docs_root = _DOCS_ROOT.resolve()
        target = (docs_root / name).resolve()
        if not target.is_file() or docs_root not in target.parents:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        self._send_json({"name": name, "content": target.read_text(encoding="utf-8")})

    def _serve_static(self, request_path: str) -> None:
        relative = (
            "index.html" if request_path in {"", "/"} else request_path.lstrip("/")
        )
        candidate = (_STATIC_ROOT / relative).resolve()
        static_root = _STATIC_ROOT.resolve()
        if static_root not in candidate.parents and candidate != static_root:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        if not candidate.is_file():
            candidate = _STATIC_ROOT / "index.html"
        content = candidate.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", _media_type(candidate.suffix))
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _send_json(
        self,
        payload: dict[str, JSONValue],
        status: HTTPStatus = HTTPStatus.OK,
    ) -> None:
        encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def _media_type(suffix: str) -> str:
    return {
        ".html": "text/html; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".js": "text/javascript; charset=utf-8",
        ".svg": "image/svg+xml",
    }.get(suffix, "application/octet-stream")


def serve_dashboard(
    host: str,
    port: int,
    state: DashboardStateStore | None = None,
    snapshot_path: Path | None = None,
) -> None:
    """Run the local operator dashboard until interrupted."""
    store = state or DashboardStateStore()
    heatmaps = SnapshotHeatmapSource(snapshot_path) if snapshot_path else None
    with DashboardServer((host, port), store, heatmaps) as server:
        print(f"Brain-5D dashboard: http://{host}:{port}")
        server.serve_forever()


def main() -> None:
    """CLI entry point for standalone dashboard operation."""
    parser = argparse.ArgumentParser(description="Brain-5D operator dashboard")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--snapshot", type=Path)
    args = parser.parse_args()
    serve_dashboard(args.host, args.port, snapshot_path=args.snapshot)


if __name__ == "__main__":
    main()
