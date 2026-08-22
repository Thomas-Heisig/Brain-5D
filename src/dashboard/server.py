"""Dependency-free local HTTP server for the Brain-5D operator dashboard.

This module provides a lightweight HTTP server that serves the dashboard
frontend and provides RESTful API endpoints for controlling and monitoring
the Brain-5D runtime. All endpoints are read-only except for explicit
operator commands that go through the StructuralOperatorBridge.
"""

from __future__ import annotations

import argparse
import json
import signal
from collections.abc import Mapping
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import cast
from urllib.parse import parse_qs, urlparse

from .control_http import handle_control_get, handle_control_post
from .docs_source import DocumentationSource, create_docs_source
from .heatmap_source import SnapshotHeatmapSource, create_heatmap_source
from .models import JSONValue
from .operator_bridge import OperatorBridge
from .state import DashboardStateStore
from .structural_api import StructuralCommandResult

# Static assets directory
_STATIC_ROOT = Path(__file__).with_name("static")
_DOCS_ROOT = Path(__file__).resolve().parents[2] / "docs"

# Maximum request body size (64KB)
_MAX_BODY_SIZE = 64 * 1024

# Maximum number of history records to return
_MAX_HISTORY_LIMIT = 1000

# Allowed static file extensions
_ALLOWED_STATIC_EXTENSIONS = {
    ".html", ".css", ".js", ".svg", ".ico",
    ".png", ".jpg", ".jpeg", ".gif", ".webp"
}

# HTTP 413 Payload Too Large
_HTTP_413_PAYLOAD_TOO_LARGE = 413

# ================================================================
# 🔥 GLOBALE BRIDGE (Kleinbuchstaben, damit Pylance es nicht als Konstante sieht)
# ================================================================
_global_bridge: OperatorBridge | None = None


# ============================================================================
# Custom Exceptions
# ============================================================================

class DashboardError(Exception):
    pass


class InvalidRequestError(DashboardError):
    pass


class BridgeNotConfiguredError(DashboardError):
    pass


# ============================================================================
# HTTP Server
# ============================================================================

class DashboardServer(ThreadingHTTPServer):
    def __init__(
        self,
        address: tuple[str, int],
        state: DashboardStateStore,
        heatmaps: SnapshotHeatmapSource | None,
        structural_bridge: OperatorBridge | None = None,
        docs_source: DocumentationSource | None = None,
    ) -> None:
        super().__init__(address, DashboardRequestHandler)
        self.dashboard_state = state
        self.heatmap_source = heatmaps
        self.structural_bridge = structural_bridge
        self.docs_source = docs_source
        self._running = True

    def shutdown(self) -> None:
        self._running = False
        super().shutdown()

    def serve_forever(self, poll_interval: float = 0.5) -> None:
        self._running = True
        super().serve_forever(poll_interval)


class DashboardRequestHandler(BaseHTTPRequestHandler):
    server_version = "Brain5DDashboard/0.5.0-alpha.2"

    @property
    def dashboard_server(self) -> DashboardServer:
        return cast(DashboardServer, self.server)

    # -------------------------------------------------------------------------
    # HTTP Methods
    # -------------------------------------------------------------------------

    def do_GET(self) -> None:
        server = self.dashboard_server
        parsed = urlparse(self.path)

        try:
            # ================================================================
            # DEBUG: Bridge-Status
            # ================================================================
            if parsed.path == "/api/debug/bridge":
                self._send_json({
                    "global_bridge_exists": _global_bridge is not None,
                    "global_bridge_type": str(type(_global_bridge)) if _global_bridge else None,
                    "server_bridge_exists": server.structural_bridge is not None,
                    "server_bridge_type": str(type(server.structural_bridge)) if server.structural_bridge else None,
                })
                return

            # ================================================================
            # CONTROL API (GET)
            # ================================================================
            if parsed.path == "/api/control":
                bridge = _global_bridge
                if bridge is None:
                    self._send_json(
                        {"error": "Bridge not configured"},
                        HTTPStatus.SERVICE_UNAVAILABLE,
                    )
                    return

                # Controller aus der Bridge holen
                if not hasattr(bridge, "controller"):
                    self._send_json(
                        {"error": "Bridge has no controller"},
                        HTTPStatus.SERVICE_UNAVAILABLE,
                    )
                    return

                ctrl = bridge.controller

                # ControlService mit dem Controller erstellen
                from .control_service import DashboardControlService
                service = DashboardControlService(ctrl)  # type: ignore[reportArgumentType]
                handle_control_get(self, service)
                return

            # ================================================================
            # Status & Heatmap & Docs & Structural
            # ================================================================
            if parsed.path == "/api/status":
                self._send_json(server.dashboard_state.snapshot().to_json())
                return

            if parsed.path == "/api/heatmap":
                self._serve_heatmap(parse_qs(parsed.query))
                return

            if parsed.path == "/api/snapshots":
                self._serve_snapshots()
                return

            if parsed.path == "/api/docs":
                self._serve_docs(parse_qs(parsed.query))
                return

            if parsed.path.startswith("/api/structural/"):
                self._serve_structural_get(parsed.path, parse_qs(parsed.query))
                return

            if parsed.path.startswith("/api/docs-files/"):
                self._serve_doc_file(parsed.path)
                return

            if parsed.path == "/healthz":
                self._send_json({"status": "ok", "version": self.server_version})
                return

            self._serve_static(parsed.path)

        except (ValueError, TypeError, json.JSONDecodeError) as e:
            self._send_json({"error": str(e)}, HTTPStatus.BAD_REQUEST)
        except FileNotFoundError as e:
            self._send_json({"error": str(e)}, HTTPStatus.NOT_FOUND)
        except (RuntimeError, DashboardError) as e:
            self._send_json({"error": str(e)}, HTTPStatus.SERVICE_UNAVAILABLE)
        except Exception as e:
            self._send_json(
                {"error": f"Internal server error: {e}"},
                HTTPStatus.INTERNAL_SERVER_ERROR
            )

    def do_POST(self) -> None:
        parsed = urlparse(self.path)

        try:
            # ================================================================
            # CONTROL API (POST)
            # ================================================================
            if parsed.path == "/api/control":
                bridge = _global_bridge
                if bridge is None:
                    self._send_json(
                        {"error": "Bridge not configured"},
                        HTTPStatus.SERVICE_UNAVAILABLE,
                    )
                    return

                if not hasattr(bridge, "controller"):
                    self._send_json(
                        {"error": "Bridge has no controller"},
                        HTTPStatus.SERVICE_UNAVAILABLE,
                    )
                    return

                ctrl = bridge.controller

                from .control_service import DashboardControlService
                service = DashboardControlService(ctrl)  # type: ignore[reportArgumentType]

                handle_control_post(self, service)
                return

            # ================================================================
            # Structural POST
            # ================================================================
            bridge = _global_bridge
            if bridge is None:
                self._send_json(
                    {"error": "Structural operator bridge is not configured."},
                    HTTPStatus.SERVICE_UNAVAILABLE,
                )
                return

            body = self._read_json_object()
            result = self._dispatch_structural_post(bridge, parsed.path, body)
            if result is None:
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            self._send_command_result(result)

        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        except BridgeNotConfiguredError as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.SERVICE_UNAVAILABLE)

    def do_PUT(self) -> None:
        bridge = _global_bridge
        if bridge is None:
            self._send_json(
                {"error": "Structural operator bridge is not configured."},
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return

        parsed = urlparse(self.path)
        try:
            body = self._read_json_object()
            if parsed.path == "/api/structural/config":
                result = bridge.update_structural_config(**body)
                self._send_command_result(result)
                return
            self.send_error(HTTPStatus.NOT_FOUND)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/structural/history":
            self._send_json({"ok": True, "message": "History cleared"})
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args: object) -> None:
        pass

    # =========================================================================
    # Structural GET
    # =========================================================================

    def _serve_structural_get(self, path: str, query: dict[str, list[str]]) -> None:
        bridge = _global_bridge
        if bridge is None:
            self._send_json(
                {"error": "Structural operator bridge is not configured."},
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return

        if path == "/api/structural/status":
            payload = bridge.structural_status()
        elif path == "/api/structural/proposals":
            proposals = bridge.structural_proposals()
            payload = {"proposals": cast(list[JSONValue], proposals)}
        elif path == "/api/structural/history":
            limit = self._query_int(query, "limit", default=100, maximum=_MAX_HISTORY_LIMIT)
            history = bridge.structural_history(limit)
            payload = {"history": cast(list[JSONValue], history)}
        elif path == "/api/structural/heatmap":
            kind = query.get("kind", ["total_structural_activity"])[0]
            payload = bridge.structural_heatmap(kind)
        elif path == "/api/structural/config":
            payload = bridge.structural_config()
        else:
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        self._send_json(payload)  # type: ignore[arg-type]

    # =========================================================================
    # Dispatch Structural POST
    # =========================================================================

    def _dispatch_structural_post(
        self,
        bridge: OperatorBridge,
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
            count = self._int_field(body, "count", minimum=1, maximum=10_000)
            return bridge.run_ticks(count)
        if path == "/api/runtime/single-step":
            return bridge.single_step()
        if path == "/api/runtime/snapshot":
            return bridge.request_snapshot()
        if path == "/api/runtime/command":
            command = self._string_field(body, "command")
            ticks = body.get("ticks")
            if ticks is not None and isinstance(ticks, int):
                result = bridge.command(command, ticks=ticks)
                return StructuralCommandResult(
                    bool(result.get("ok", False)),
                    str(result.get("status", {}))
                )
            result = bridge.command(command)
            return StructuralCommandResult(
                bool(result.get("ok", False)),
                str(result.get("status", {}))
            )
        return None

    # =========================================================================
    # Heatmap, Snapshots, Docs, Static
    # =========================================================================

    def _serve_heatmap(self, query: dict[str, list[str]]) -> None:
        source = self.dashboard_server.heatmap_source
        if source is None:
            self._send_json(
                {"error": "No .b5d snapshot configured for heatmaps."},
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return

        kind = query.get("kind", ["activity"])[0]
        snapshot_name = query.get("snapshot", [None])[0]

        try:
            payload = source.build(kind, snapshot_name)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return
        except FileNotFoundError as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.NOT_FOUND)
            return
        except RuntimeError as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.SERVICE_UNAVAILABLE)
            return

        self._send_json(payload.to_json())

    def _serve_snapshots(self) -> None:
        source = self.dashboard_server.heatmap_source
        if source is None:
            self._send_json(
                {"error": "No heatmap source configured."},
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return

        try:
            entries = source.list_snapshots()
            snapshots = [entry.to_json() for entry in entries]
            self._send_json({"snapshots": snapshots})  # type: ignore[arg-type]
        except Exception as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def _serve_docs(self, query: dict[str, list[str]]) -> None:
        docs_source = self.dashboard_server.docs_source or create_docs_source(_DOCS_ROOT)
        recursive = query.get("recursive", ["false"])[0].lower() == "true"
        file_type = query.get("type", [None])[0]

        try:
            entries = docs_source.list_documents(recursive=recursive)
            if file_type:
                from .docs_source import FileType
                try:
                    ft = FileType(file_type)
                    entries = [e for e in entries if e.file_type == ft]
                except ValueError:
                    pass
            documents = [e.to_json() for e in entries]
            self._send_json({"documents": documents})  # type: ignore[arg-type]
        except Exception as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def _serve_doc_file(self, path: str) -> None:
        docs_source = self.dashboard_server.docs_source or create_docs_source(_DOCS_ROOT)
        prefix = "/api/docs-files/"
        if not path.startswith(prefix):
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        file_path = path[len(prefix):]
        preview = "preview" in parse_qs(urlparse(path).query)

        try:
            entry = docs_source.get_document(file_path)
            content = docs_source.read_preview(file_path) if preview else docs_source.read_content(file_path)
            self._send_json({
                "metadata": entry.to_json(),
                "content": content,
                "is_preview": preview,
            })
        except FileNotFoundError:
            self._send_json({"error": f"Document not found: {file_path}"}, HTTPStatus.NOT_FOUND)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)

    def _serve_static(self, request_path: str) -> None:
        if request_path in {"", "/"}:
            relative = "index.html"
        else:
            relative = request_path.lstrip("/")

        if ".." in relative or relative.startswith("/"):
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        candidate = (_STATIC_ROOT / relative).resolve()
        static_root = _STATIC_ROOT.resolve()

        try:
            candidate.relative_to(static_root)
        except ValueError:
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        if not candidate.is_file():
            candidate = _STATIC_ROOT / "index.html"

        if candidate.suffix.lower() not in _ALLOWED_STATIC_EXTENSIONS:
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        try:
            content = candidate.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", _media_type(candidate.suffix))
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND)

    # =========================================================================
    # JSON Helpers
    # =========================================================================

    def _send_json(self, payload: dict[str, JSONValue], status: HTTPStatus = HTTPStatus.OK) -> None:
        try:
            encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        except TypeError as e:
            encoded = json.dumps({"error": f"Serialization error: {e}"}).encode("utf-8")
            status = HTTPStatus.INTERNAL_SERVER_ERROR

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_command_result(self, result: StructuralCommandResult) -> None:
        status = HTTPStatus.OK if result.ok else HTTPStatus.CONFLICT
        self._send_json({"ok": result.ok, "message": result.message}, status)

    def _read_json_object(self) -> dict[str, object]:
        length_header = self.headers.get("Content-Length")
        if length_header is None:
            return {}

        length = int(length_header)
        if not 0 <= length <= _MAX_BODY_SIZE:
            raise ValueError(f"Request body too large (max {_MAX_BODY_SIZE} bytes)")

        raw = json.loads(self.rfile.read(length).decode("utf-8"))
        if not isinstance(raw, Mapping):
            raise TypeError("JSON body must be an object")

        return {str(k): v for k, v in raw.items()}  # type: ignore[arg-type, var-annotated]

    # =========================================================================
    # Field Validation
    # =========================================================================

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
    def _int_field(body: dict[str, object], name: str, *, minimum: int, maximum: int) -> int:
        value = body.get(name)
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"'{name}' must be an integer")
        if not minimum <= value <= maximum:
            raise ValueError(f"'{name}' must be in [{minimum}, {maximum}]")
        return value

    @classmethod
    def _query_int(cls, query: dict[str, list[str]], name: str, *, default: int, maximum: int) -> int:
        raw = query.get(name, [str(default)])[0]
        try:
            value = int(raw)
        except ValueError:
            value = default
        return cls._int_field({name: value}, name, minimum=1, maximum=maximum)


def _media_type(suffix: str) -> str:
    return {
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
    }.get(suffix.lower(), "application/octet-stream")


# ============================================================================
# Signal Handling
# ============================================================================

def _setup_signal_handlers(server: DashboardServer) -> None:
    def signal_handler(sig: int, frame: object) -> None:
        print("\nShutting down dashboard...")
        server.shutdown()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


# ============================================================================
# Main Functions
# ============================================================================

def serve_dashboard(
    host: str,
    port: int,
    state: DashboardStateStore | None = None,
    snapshot_path: Path | None = None,
    structural_bridge: OperatorBridge | None = None,
    docs_root: Path | None = None,
) -> None:
    """Run the local operator dashboard until interrupted."""
    global _global_bridge

    store = state or DashboardStateStore()

    # Setup heatmap source
    heatmaps = None
    if snapshot_path and snapshot_path.exists():
        try:
            heatmaps = create_heatmap_source(snapshot_path)
        except FileNotFoundError:
            print(f"Warning: Default snapshot not found: {snapshot_path}")

    # Setup docs source
    docs_source = None
    if docs_root and docs_root.exists():
        try:
            docs_source = create_docs_source(docs_root)
        except Exception as e:
            print(f"Warning: Failed to initialize docs source: {e}")

    # 🔥 Globale Bridge setzen – bevor der Server startet
    _global_bridge = structural_bridge
    print(f"🌉 Global bridge set: {_global_bridge is not None}")

    with DashboardServer(
        (host, port),
        store,
        heatmaps,
        structural_bridge,
        docs_source,
    ) as server:

        if structural_bridge is not None:
            server.structural_bridge = structural_bridge
            print("✅ Bridge stored in server instance")

        print(f"🧠 Brain-5D dashboard: http://{host}:{port}")
        print("Press Ctrl+C to stop")
        _setup_signal_handlers(server)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nDashboard stopped.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Brain-5D operator dashboard")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--docs", type=Path)
    args = parser.parse_args()
    serve_dashboard(args.host, args.port, snapshot_path=args.snapshot, docs_root=args.docs)


if __name__ == "__main__":
    main()