"""Dependency-free local HTTP server for the Brain-5D operator dashboard."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import cast
from urllib.parse import parse_qs, urlparse

from .heatmap_source import SnapshotHeatmapSource
from .models import JSONValue
from .state import DashboardStateStore
from .structural_api import StructuralCommandResult, StructuralOperatorBridge

_STATIC_ROOT = Path(__file__).with_name("static")
_DOCS_ROOT = Path(__file__).resolve().parents[2] / "docs"


class DashboardServer(ThreadingHTTPServer):
    """HTTP server carrying typed dashboard dependencies."""

    def __init__(
        self,
        address: tuple[str, int],
        state: DashboardStateStore,
        heatmaps: SnapshotHeatmapSource | None,
        structural_bridge: StructuralOperatorBridge | None = None,
    ) -> None:
        super().__init__(address, DashboardRequestHandler)
        self.dashboard_state = state
        self.heatmap_source = heatmaps
        self.structural_bridge = structural_bridge


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
        if parsed.path.startswith("/api/structural/"):
            self._serve_structural_get(server, parsed.path, parse_qs(parsed.query))
            return
        if parsed.path == "/healthz":
            self._send_json({"status": "ok"})
            return
        self._serve_static(parsed.path)

    def do_POST(self) -> None:  # pylint: disable=invalid-name
        """Serve validated operator commands without accepting arbitrary text."""
        server = self.server
        if not isinstance(server, DashboardServer):
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR)
            return
        bridge = server.structural_bridge
        if bridge is None:
            self._send_json(
                {"error": "Structural operator bridge is not configured."},
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return
        parsed = urlparse(self.path)
        try:
            body = self._read_json_object()
            result = self._dispatch_structural_post(bridge, parsed.path, body)
        except (TypeError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return
        if result is None:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        self._send_command_result(result)

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

    def _serve_structural_get(
        self,
        server: DashboardServer,
        path: str,
        query: dict[str, list[str]],
    ) -> None:
        bridge = server.structural_bridge
        if bridge is None:
            self._send_json(
                {"error": "Structural operator bridge is not configured."},
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return
        payload: dict[str, JSONValue]
        try:
            if path == "/api/structural/status":
                payload = bridge.structural_status()
            elif path == "/api/structural/proposals":
                proposal_values: list[JSONValue] = []
                proposal_values.extend(bridge.structural_proposals())
                payload = {"proposals": proposal_values}
            elif path == "/api/structural/history":
                limit = self._query_int(query, "limit", default=100, maximum=1_000)
                history_values: list[JSONValue] = []
                history_values.extend(bridge.structural_history(limit))
                payload = {"history": history_values}
            elif path == "/api/structural/heatmap":
                kind = query.get("kind", ["total_structural_activity"])[0]
                payload = bridge.structural_heatmap(kind)
            elif path == "/api/structural/config":
                payload = bridge.structural_config()
            else:
                self.send_error(HTTPStatus.NOT_FOUND)
                return
        except (TypeError, ValueError, RuntimeError) as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return
        self._send_json(payload)

    def _dispatch_structural_post(
        self,
        bridge: StructuralOperatorBridge,
        path: str,
        body: dict[str, object],
    ) -> StructuralCommandResult | None:
        if path == "/api/structural/approve":
            return bridge.approve_structural(self._string_field(body, "proposal_id"))
        if path == "/api/structural/reject":
            return bridge.reject_structural(self._string_field(body, "proposal_id"))
        if path == "/api/structural/undo":
            return bridge.undo_structural()
        if path == "/api/structural/auto-approval":
            return bridge.set_auto_approval(self._bool_field(body, "enabled"))
        if path == "/api/runtime/ticks":
            return bridge.run_ticks(
                self._int_field(body, "count", minimum=1, maximum=1_000)
            )
        if path == "/api/runtime/single-step":
            return bridge.single_step()
        if path == "/api/runtime/snapshot":
            return bridge.request_snapshot()
        return None

    def _read_json_object(self) -> dict[str, object]:
        length_header = self.headers.get("Content-Length")
        if length_header is None:
            return {}
        length = int(length_header)
        if not 0 <= length <= 64 * 1024:
            raise ValueError("request body is too large")
        raw: object = json.loads(self.rfile.read(length).decode("utf-8"))
        if not isinstance(raw, Mapping):
            raise TypeError("JSON body must be an object")
        mapping = cast(Mapping[object, object], raw)
        result: dict[str, object] = {}
        for key, value in mapping.items():
            if not isinstance(key, str):
                raise TypeError("JSON object keys must be strings")
            result[key] = value
        return result

    def _send_command_result(self, result: StructuralCommandResult) -> None:
        status = HTTPStatus.OK if result.ok else HTTPStatus.CONFLICT
        self._send_json({"ok": result.ok, "message": result.message}, status)

    @staticmethod
    def _string_field(body: dict[str, object], name: str) -> str:
        value = body.get(name)
        if not isinstance(value, str) or not value:
            raise TypeError(f"'{name}' must be a non-empty string")
        return value

    @staticmethod
    def _bool_field(body: dict[str, object], name: str) -> bool:
        value = body.get(name)
        if not isinstance(value, bool):
            raise TypeError(f"'{name}' must be boolean")
        return value

    @staticmethod
    def _int_field(
        body: dict[str, object],
        name: str,
        *,
        minimum: int,
        maximum: int,
    ) -> int:
        value = body.get(name)
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"'{name}' must be an integer")
        if not minimum <= value <= maximum:
            raise ValueError(f"'{name}' must be in [{minimum}, {maximum}]")
        return value

    @classmethod
    def _query_int(
        cls,
        query: dict[str, list[str]],
        name: str,
        *,
        default: int,
        maximum: int,
    ) -> int:
        raw = query.get(name, [str(default)])[0]
        return cls._int_field(
            {name: int(raw)},
            name,
            minimum=1,
            maximum=maximum,
        )

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
    structural_bridge: StructuralOperatorBridge | None = None,
) -> None:
    """Run the local operator dashboard until interrupted."""
    store = state or DashboardStateStore()
    heatmaps = SnapshotHeatmapSource(snapshot_path) if snapshot_path else None
    with DashboardServer((host, port), store, heatmaps, structural_bridge) as server:
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
