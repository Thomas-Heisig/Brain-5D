"""Dependency-free local HTTP server for the Brain-5D operator dashboard.

The dashboard server is intentionally lightweight and uses only Python's
standard HTTP server infrastructure.

Architecture
------------
The DashboardServer instance owns all runtime-facing dependencies:

- DashboardStateStore
- SnapshotHeatmapSource
- OperatorBridge
- DocumentationSource

The request handler never relies on module-global runtime state. In
particular, the OperatorBridge is obtained exclusively through the active
DashboardServer instance.

This is important because the dashboard, controller and Brain-5D runtime
must operate inside one coherent application process.

API requests are strictly separated from SPA/static-file routing:
unknown ``/api/...`` paths always return JSON errors and can never fall
through to ``index.html``.

Mutation is possible only through explicit operator endpoints.
"""

from __future__ import annotations

import argparse
import json
import signal
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from collections.abc import Mapping
from typing import Any, cast
from urllib.parse import parse_qs, unquote, urlparse

from .control_http import handle_control_get, handle_control_post
from .control_service import DashboardControlService
from .docs_source import DocumentationSource, create_docs_source
from .heatmap_source import SnapshotHeatmapSource, create_heatmap_source
from .gate_status import GateStatusBuilder
from .integration_status import IntegrationStatusBuilder
from .models import JSONValue
from .network_inspector import NetworkInspector
from .operator_bridge import OperatorBridge
from .research_source import ResearchSource, create_research_source
from .state import DashboardStateStore
from .structural_api import StructuralCommandResult

# ============================================================================
# Paths and limits
# ============================================================================

_STATIC_ROOT = Path(__file__).with_name("static")
_DEFAULT_DOCS_ROOT = Path(__file__).resolve().parents[2] / "docs"
_DEFAULT_RESEARCH_ROOT = Path(__file__).resolve().parents[2] / "research"

_MAX_BODY_SIZE = 64 * 1024
_MAX_HISTORY_LIMIT = 1000

_ALLOWED_STATIC_EXTENSIONS = {
    ".html",
    ".css",
    ".js",
    ".svg",
    ".ico",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
}


# ============================================================================
# Exceptions
# ============================================================================


class DashboardError(Exception):
    """Base class for dashboard request errors."""


class InvalidRequestError(DashboardError):
    """Raised when an HTTP request cannot be validated."""


class BridgeNotConfiguredError(DashboardError):
    """Raised when an operator command requires an unavailable bridge."""


class RequestBodyTooLargeError(DashboardError):
    """Raised when an incoming JSON request exceeds the configured limit."""


class UnsupportedMediaTypeError(DashboardError):
    """Raised when a JSON endpoint receives an unsupported content type."""


# ============================================================================
# HTTP server
# ============================================================================


class DashboardServer(ThreadingHTTPServer):
    """Threaded Brain-5D dashboard HTTP server.

    All dependencies used by request handlers are stored on this server
    instance. No mutable module-global runtime state is used.
    """

    allow_reuse_address = True
    daemon_threads = True

    def __init__(
        self,
        address: tuple[str, int],
        state: DashboardStateStore,
        heatmaps: SnapshotHeatmapSource | None,
        structural_bridge: OperatorBridge | None = None,
        docs_source: DocumentationSource | None = None,
        research_source: ResearchSource | None = None,
    ) -> None:
        super().__init__(address, DashboardRequestHandler)

        self.dashboard_state = state
        self.heatmap_source = heatmaps
        self.structural_bridge = structural_bridge
        self.docs_source = docs_source
        self.research_source = research_source


# ============================================================================
# Request handler
# ============================================================================


class DashboardRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Brain-5D dashboard and operator APIs."""

    from src.version import BRAIN5D_VERSION_DISPLAY
    server_version = f"Brain5DDashboard/{BRAIN5D_VERSION_DISPLAY}"

    @property
    def dashboard_server(self) -> DashboardServer:
        """Return the concrete Brain-5D dashboard server."""
        return cast(DashboardServer, self.server)

    # ========================================================================
    # Bridge access
    # ========================================================================

    def _require_bridge(self) -> OperatorBridge:
        """Return the active OperatorBridge or raise a service error."""
        bridge = self.dashboard_server.structural_bridge

        if bridge is None:
            raise BridgeNotConfiguredError(
                "Structural operator bridge is not configured."
            )

        return bridge

    # ========================================================================
    # GET
    # ========================================================================

    def do_GET(self) -> None:
        server = self.dashboard_server
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        try:
            # ----------------------------------------------------------------
            # Debug / diagnostics
            # ----------------------------------------------------------------

            if path == "/api/debug/bridge":
                bridge = server.structural_bridge

                self._send_json(
                    {
                        "bridge_exists": bridge is not None,
                        "bridge_type": (
                            f"{type(bridge).__module__}.{type(bridge).__qualname__}"
                            if bridge is not None
                            else None
                        ),
                        "server_id": id(server),
                        "controller_exists": (
                            bridge is not None
                            and getattr(bridge, "controller", None) is not None
                        ),
                    }
                )
                return

            # ----------------------------------------------------------------
            # Control API
            # ----------------------------------------------------------------

            if path == "/api/control":
                bridge = self._require_bridge()

                # Transitional adapter boundary:
                #
                # DashboardControlService currently declares a concrete
                # RuntimeController type while OperatorBridge exposes its own
                # controller contract. The controller architecture should be
                # unified separately. Runtime behavior is intentionally not
                # altered here.
                service = DashboardControlService(cast(Any, bridge.controller))

                handle_control_get(self, service)
                return

            # ----------------------------------------------------------------
            # Dashboard state
            # ----------------------------------------------------------------

            if path == "/api/status":
                self._send_json(server.dashboard_state.snapshot().to_json())
                return

            # ----------------------------------------------------------------
            # Heatmaps / snapshots
            # ----------------------------------------------------------------

            if path == "/api/heatmap":
                self._serve_heatmap(query)
                return

            if path == "/api/live/projection":
                self._serve_live_projection(query)
                return

            if path == "/api/snapshots":
                self._serve_snapshots()
                return

            if path == "/api/snapshot-info":
                self._serve_snapshot_info()
                return

            # ----------------------------------------------------------------
            # Documentation
            # ----------------------------------------------------------------

            if path == "/api/docs":
                self._serve_docs(query)
                return

            if path == "/api/docs/tree":
                self._serve_docs_tree()
                return

            if path == "/api/docs/statistics":
                self._serve_docs_statistics()
                return

            if path == "/api/docs/search":
                self._serve_docs_search(query)
                return

            if path.startswith("/api/docs-files/"):
                self._serve_doc_file(path, query)
                return

            # ----------------------------------------------------------------
            # Research API (B5D-SEF)
            # ----------------------------------------------------------------

            if path == "/api/research":
                self._serve_research_summary()
                return

            if path == "/api/research/documents":
                self._serve_research_documents()
                return

            if path == "/api/research/reports":
                self._serve_research_reports()
                return

            if path == "/api/research/experiments":
                self._serve_research_experiments()
                return

            if path.startswith("/api/research-files/"):
                self._serve_research_file(path)
                return

            # ----------------------------------------------------------------
            # Structural API
            # ----------------------------------------------------------------

            if path.startswith("/api/structural/"):
                self._serve_structural_get(path, query)
                return

            # ----------------------------------------------------------------
            # Network Inspector (real 5D coordinates, Phase 8/9)
            # ----------------------------------------------------------------

            if path.startswith("/api/network/"):
                self._serve_network_get(path, query)
                return

            # ----------------------------------------------------------------
            # Integration Status (real backend data, Phase 14)
            # ----------------------------------------------------------------

            if path == "/api/integration/status":
                self._serve_integration_status()
                return

            # ----------------------------------------------------------------
            # Alpha.5 Release Gate Status (dynamic, evidence-based)
            # ----------------------------------------------------------------

            if path == "/api/gate/status":
                self._serve_gate_status()
                return

            # ----------------------------------------------------------------
            # Runtime Errors (dedicated endpoint, Phase 5)
            # ----------------------------------------------------------------

            if path == "/api/errors":
                bridge = server.structural_bridge
                if bridge is None:
                    self._send_json({"available": False, "count": None, "events": []})
                    return
                limit = self._query_int(query, "limit", default=100, maximum=1000)
                errors = bridge.runtime_errors()
                if limit > 0 and limit < len(errors):
                    errors = errors[-limit:]
                self._send_json({
                    "count": len(errors),
                    "events": cast(list[JSONValue], errors),
                })
                return

            # ----------------------------------------------------------------
            # Health
            # ----------------------------------------------------------------

            if path == "/healthz":
                self._send_json(
                    {
                        "status": "ok",
                        "version": self.server_version,
                        "bridge_configured": (server.structural_bridge is not None),
                    }
                )
                return

            # ----------------------------------------------------------------
            # IMPORTANT:
            # API paths must NEVER fall through into SPA/static routing.
            # ----------------------------------------------------------------

            if path.startswith("/api/"):
                self._send_api_not_found(path)
                return

            # ----------------------------------------------------------------
            # Static / SPA
            # ----------------------------------------------------------------

            self._serve_static(path)

        except Exception as exc:
            self._handle_exception(exc)

    # ========================================================================
    # POST
    # ========================================================================

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        try:
            # ----------------------------------------------------------------
            # Control API
            # ----------------------------------------------------------------

            if path == "/api/control":
                bridge = self._require_bridge()

                service = DashboardControlService(cast(Any, bridge.controller))

                handle_control_post(self, service)
                return

            # ----------------------------------------------------------------
            # Structural / runtime operator commands
            # ----------------------------------------------------------------

            if path.startswith("/api/structural/") or path.startswith("/api/runtime/"):
                bridge = self._require_bridge()
                body = self._read_json_object()

                result = self._dispatch_structural_post(
                    bridge,
                    path,
                    body,
                )

                if result is None:
                    self._send_api_not_found(path)
                    return

                self._send_command_result(result)
                return

            # ----------------------------------------------------------------
            # Unknown API
            # ----------------------------------------------------------------

            if path.startswith("/api/"):
                self._send_api_not_found(path)
                return

            self._send_json(
                {
                    "error": f"POST is not supported for path: {path}",
                },
                HTTPStatus.METHOD_NOT_ALLOWED,
            )

        except Exception as exc:
            self._handle_exception(exc)

    # ========================================================================
    # PUT
    # ========================================================================

    def do_PUT(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        try:
            if path == "/api/structural/config":
                bridge = self._require_bridge()
                body = self._read_json_object()

                result = bridge.update_structural_config(**body)

                self._send_command_result(result)
                return

            if path.startswith("/api/"):
                self._send_api_not_found(path)
                return

            self._send_json(
                {
                    "error": f"PUT is not supported for path: {path}",
                },
                HTTPStatus.METHOD_NOT_ALLOWED,
            )

        except Exception as exc:
            self._handle_exception(exc)

    # ========================================================================
    # DELETE
    # ========================================================================

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        # Structural history is deliberately append-only.
        # The dashboard must not silently erase audit history.
        if path == "/api/structural/history":
            self._send_json(
                {
                    "ok": False,
                    "error": (
                        "Structural history is append-only and cannot be "
                        "cleared through the dashboard."
                    ),
                },
                HTTPStatus.METHOD_NOT_ALLOWED,
            )
            return

        if path.startswith("/api/"):
            self._send_api_not_found(path)
            return

        self._send_json(
            {
                "error": f"DELETE is not supported for path: {path}",
            },
            HTTPStatus.METHOD_NOT_ALLOWED,
        )

    # ========================================================================
    # HTTP logging
    # ========================================================================

    def log_message(self, format: str, *args: object) -> None:
        """Suppress BaseHTTPRequestHandler's default stderr logging.

        Runtime/dashboard logging is handled by Brain-5D itself.
        """
        return

    # ========================================================================
    # Structural GET
    # ========================================================================

    def _serve_structural_get(
        self,
        path: str,
        query: dict[str, list[str]],
    ) -> None:
        bridge = self._require_bridge()

        if path == "/api/structural/status":
            payload = bridge.structural_status()

        elif path == "/api/structural/proposals":
            proposals = bridge.structural_proposals()

            payload = {
                "proposals": cast(
                    list[JSONValue],
                    proposals,
                )
            }

        elif path == "/api/structural/history":
            limit = self._query_int(
                query,
                "limit",
                default=100,
                maximum=_MAX_HISTORY_LIMIT,
            )

            history = bridge.structural_history(limit)

            payload = {
                "history": cast(
                    list[JSONValue],
                    history,
                )
            }

        elif path == "/api/structural/heatmap":
            kind = query.get(
                "kind",
                ["total_structural_activity"],
            )[0]

            payload = bridge.structural_heatmap(kind)

        elif path == "/api/structural/config":
            payload = bridge.structural_config()

        elif path == "/api/structural/errors":
            payload = {
                "errors": cast(
                    list[JSONValue],
                    bridge.runtime_errors(),
                )
            }

        else:
            self._send_api_not_found(path)
            return

        self._send_json(payload)

    # ========================================================================
    # Network Inspector (real 5D coordinates, Phase 8/9)
    # ========================================================================

    def _serve_network_get(
        self,
        path: str,
        query: dict[str, list[str]],
    ) -> None:
        bridge = self._require_bridge()
        network = getattr(bridge.controller, "network", None)
        if network is None:
            self._send_json(
                {"error": "Live network is not available through the controller."},
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return

        inspector = NetworkInspector(network)

        if path == "/api/network/summary":
            self._send_json(inspector.summary().to_json())
            return

        if path == "/api/network/neurons":
            limit = self._query_int(query, "limit", default=500, maximum=5000)
            offset = self._query_offset(query, "offset", default=0, maximum=10_000_000)
            active_only = query.get("active_only", ["false"])[0].lower() == "true"
            self._send_json(
                inspector.neurons(limit=limit, offset=offset, active_only=active_only).to_json()
            )
            return

        if path == "/api/network/synapses":
            limit = self._query_int(query, "limit", default=500, maximum=5000)
            offset = self._query_offset(query, "offset", default=0, maximum=10_000_000)
            source_id = self._optional_query_int(query, "source")
            target_id = self._optional_query_int(query, "target")
            min_weight = self._optional_query_float(query, "min_weight")
            self._send_json(
                inspector.synapses(
                    limit=limit,
                    offset=offset,
                    source_id=source_id,
                    target_id=target_id,
                    min_weight=min_weight,
                ).to_json()
            )
            return

        if path == "/api/network/projection":
            limit = self._query_int(query, "limit", default=2000, maximum=2000)
            mode = query.get("mode", ["activity"])[0]
            self._send_json(inspector.projection(limit=limit, mode=mode).to_json())
            return

        self._send_api_not_found(path)

    # ========================================================================
    # Integration Status (real backend data, Phase 14)
    # ========================================================================

    def _serve_integration_status(self) -> None:
        server = self.dashboard_server
        bridge = server.structural_bridge
        builder = IntegrationStatusBuilder(
            server.dashboard_state.snapshot(),
            bridge=bridge,
            heatmap_source=server.heatmap_source,
            research_source=server.research_source,
            repo_root=Path(__file__).resolve().parents[2],
        )
        self._send_json(builder.build())

    def _serve_gate_status(self) -> None:
        """Serve the dynamic Alpha.5 release-gate status.

        This endpoint returns the evidence-based gate status (Gate A, B, C)
        plus the live runtime profile. The browser must NEVER infer
        scientific completion from this data — the gate truth is built here.
        """
        server = self.dashboard_server
        bridge = server.structural_bridge
        # The bridge may carry a config_dict attribute (set by main.py);
        # if absent, the builder uses an empty dict (all subsystems unknown).
        config_dict = getattr(bridge, "config_dict", None) or {}
        builder = GateStatusBuilder(
            bridge=bridge,
            research_source=server.research_source,
            repo_root=Path(__file__).resolve().parents[2],
            config_dict=config_dict,
        )
        self._send_json(builder.build())

    # ========================================================================
    # Structural / runtime POST dispatch
    # ========================================================================

    def _dispatch_structural_post(
        self,
        bridge: OperatorBridge,
        path: str,
        body: dict[str, object],
    ) -> StructuralCommandResult | None:
        """Dispatch one explicit operator mutation command."""

        if path == "/api/structural/approve":
            return bridge.approve_structural(
                self._string_field(
                    body,
                    "proposal_id",
                )
            )

        if path == "/api/structural/reject":
            return bridge.reject_structural(
                self._string_field(
                    body,
                    "proposal_id",
                )
            )

        if path == "/api/structural/undo":
            return bridge.undo_structural()

        if path == "/api/structural/auto-approval":
            return bridge.set_auto_approval(
                self._bool_field(
                    body,
                    "enabled",
                )
            )

        if path == "/api/runtime/ticks":
            count = self._int_field(
                body,
                "count",
                minimum=1,
                maximum=10_000,
            )

            return bridge.run_ticks(count)

        if path == "/api/runtime/single-step":
            return bridge.single_step()

        if path == "/api/runtime/snapshot":
            return bridge.request_snapshot()

        if path == "/api/runtime/command":
            command = self._string_field(
                body,
                "command",
            )

            ticks_value = body.get("ticks")

            if ticks_value is not None:
                ticks = self._int_field(
                    body,
                    "ticks",
                    minimum=1,
                    maximum=10_000,
                )

                result = bridge.command(
                    command,
                    ticks=ticks,
                )

            else:
                result = bridge.command(command)

            ok = bool(result.get("ok", False))

            if ok:
                message = str(
                    result.get(
                        "status",
                        "command completed",
                    )
                )
            else:
                message = str(
                    result.get(
                        "error",
                        "command failed",
                    )
                )

            return StructuralCommandResult(
                ok,
                message,
            )

        return None

    # ========================================================================
    # Heatmap
    # ========================================================================

    def _serve_heatmap(
        self,
        query: dict[str, list[str]],
    ) -> None:
        source = self.dashboard_server.heatmap_source

        if source is None:
            self._send_json(
                {"error": ("No .b5d snapshot configured for heatmaps.")},
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return

        kind = query.get(
            "kind",
            ["activity"],
        )[0]

        snapshot_name = query.get(
            "snapshot",
            [None],
        )[0]

        try:
            payload = source.build(
                kind,
                snapshot_name,
            )

        except ValueError as exc:
            self._send_json(
                {"error": str(exc)},
                HTTPStatus.BAD_REQUEST,
            )
            return

        except FileNotFoundError as exc:
            self._send_json(
                {"error": str(exc)},
                HTTPStatus.NOT_FOUND,
            )
            return

        except RuntimeError as exc:
            self._send_json(
                {"error": str(exc)},
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return

        self._send_json(payload.to_json())

    # ========================================================================
    # Live Projection (LIVE_RUNTIME source — never from snapshot)
    # ========================================================================

    def _serve_live_projection(
        self,
        query: dict[str, list[str]],
    ) -> None:
        """Serve a live runtime projection.

        This endpoint reads directly from the in-memory NeuralNetwork,
        never from a .b5d snapshot file. The response is tagged as
        ``live_runtime`` so the frontend can distinguish it from
        snapshot-based heatmaps.
        """
        try:
            bridge = self._require_bridge()
        except BridgeNotConfiguredError:
            self._send_json(
                {"error": "No live runtime available."},
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return

        kind = query.get("kind", ["activity"])[0]
        dim_x = int(query.get("dimension_x", ["0"])[0])
        dim_y = int(query.get("dimension_y", ["1"])[0])
        bins = int(query.get("resolution", ["50"])[0])
        aggregation = query.get("aggregation", ["mean"])[0]

        try:
            projection = bridge.live_projection.project(
                kind=kind,
                dim_x=dim_x,
                dim_y=dim_y,
                bins=bins,
                aggregation=aggregation,
            )
        except ValueError as exc:
            self._send_json(
                {"error": str(exc)},
                HTTPStatus.BAD_REQUEST,
            )
            return

        self._send_json(projection.to_json())

    # ========================================================================
    # Snapshots
    # ========================================================================

    def _serve_snapshots(self) -> None:
        source = self.dashboard_server.heatmap_source

        if source is None:
            self._send_json(
                {
                    "error": "No heatmap source configured.",
                },
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return

        try:
            entries = source.list_snapshots()

            snapshots = [entry.to_json() for entry in entries]

            self._send_json(
                {
                    "snapshots": cast(
                        list[JSONValue],
                        snapshots,
                    )
                }
            )

        except Exception as exc:
            self._send_json(
                {
                    "error": str(exc),
                },
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    def _serve_snapshot_info(self) -> None:
        """Return info about the current active snapshot."""
        source = self.dashboard_server.heatmap_source

        if source is None or not hasattr(source, "snapshot_path"):
            self._send_json(
                {
                    "active": False,
                    "path": None,
                    "tick": None,
                    "size_bytes": None,
                    "message": "No snapshot source configured.",
                }
            )
            return

        try:
            path = source.snapshot_path
            info: dict[str, object] = {
                "active": path.exists(),
                "path": str(path.name) if path.exists() else None,
                "tick": None,
                "size_bytes": path.stat().st_size if path.exists() else None,
            }

            if path.exists():
                try:
                    from src.storage.b5d import B5DReader

                    reader = B5DReader(str(path))
                    info["tick"] = reader.header.snapshot_tick
                    reader.close()
                except Exception:
                    pass

            self._send_json(cast(dict[str, JSONValue], info))
        except Exception as exc:
            self._send_json(
                {"active": False, "error": str(exc)},
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    # ========================================================================
    # Documentation
    # ========================================================================

    def _serve_docs(
        self,
        query: dict[str, list[str]],
    ) -> None:
        docs_source = self.dashboard_server.docs_source or create_docs_source(
            _DEFAULT_DOCS_ROOT
        )

        recursive = (
            query.get(
                "recursive",
                ["false"],
            )[0].lower()
            == "true"
        )

        file_type = query.get(
            "type",
            [None],
        )[0]

        try:
            from .docs_source import DocumentationEntry

            entries: list[DocumentationEntry] = list(
                docs_source.list_documents(recursive=recursive)
            )

            if file_type:
                from .docs_source import FileType

                try:
                    requested_type = FileType(file_type)

                    entries = [
                        entry for entry in entries if entry.file_type == requested_type
                    ]

                except ValueError:
                    self._send_json(
                        {
                            "error": (
                                f"Unknown documentation file type: " f"{file_type}"
                            )
                        },
                        HTTPStatus.BAD_REQUEST,
                    )
                    return

            documents = [entry.to_json() for entry in entries]

            self._send_json(
                {
                    "documents": cast(
                        list[JSONValue],
                        documents,
                    )
                }
            )

        except FileNotFoundError as exc:
            self._send_json(
                {"error": str(exc)},
                HTTPStatus.NOT_FOUND,
            )

        except Exception as exc:
            self._send_json(
                {"error": str(exc)},
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    def _serve_doc_file(
        self,
        path: str,
        query: dict[str, list[str]],
    ) -> None:
        docs_source = self.dashboard_server.docs_source or create_docs_source(
            _DEFAULT_DOCS_ROOT
        )

        prefix = "/api/docs-files/"

        if not path.startswith(prefix):
            self._send_api_not_found(path)
            return

        file_path = unquote(path[len(prefix) :])

        if not file_path:
            raise InvalidRequestError("Document path must not be empty.")

        preview = query.get(
            "preview",
            ["false"],
        )[
            0
        ].lower() in {"1", "true", "yes", "on"}

        try:
            entry = docs_source.get_document(file_path)

            if preview:
                content = docs_source.read_preview(file_path)
            else:
                content = docs_source.read_content(file_path)

            self._send_json(
                {
                    "metadata": entry.to_json(),
                    "content": content,
                    "is_preview": preview,
                }
            )

        except FileNotFoundError:
            self._send_json(
                {"error": (f"Document not found: {file_path}")},
                HTTPStatus.NOT_FOUND,
            )

        except ValueError as exc:
            self._send_json(
                {
                    "error": str(exc),
                },
                HTTPStatus.BAD_REQUEST,
            )

    # ========================================================================
    # Docs API – Tree, Statistics, Search
    # ========================================================================

    def _serve_docs_tree(self) -> None:
        docs_source = self.dashboard_server.docs_source or create_docs_source(
            _DEFAULT_DOCS_ROOT
        )
        try:
            tree = docs_source.get_directory_structure()
            self._send_json(tree)
        except Exception as exc:
            self._send_json(
                {"error": str(exc)},
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    def _serve_docs_statistics(self) -> None:
        docs_source = self.dashboard_server.docs_source or create_docs_source(
            _DEFAULT_DOCS_ROOT
        )
        try:
            entries = docs_source.list_documents(recursive=True)
            total_files = len(entries)
            total_size = sum(e.size_bytes for e in entries)
            supported = sum(1 for e in entries if e.supported)
            self._send_json(
                {
                    "total_files": total_files,
                    "total_size_bytes": total_size,
                    "supported_files": supported,
                }
            )
        except Exception as exc:
            self._send_json(
                {"error": str(exc)},
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    def _serve_docs_search(self, query: dict[str, list[str]]) -> None:
        docs_source = self.dashboard_server.docs_source or create_docs_source(
            _DEFAULT_DOCS_ROOT
        )
        q = query.get("q", [""])[0].lower().strip()
        if not q or len(q) < 2:
            self._send_json({"results": []})
            return
        try:
            entries = docs_source.list_documents(recursive=True)
            results = [
                {
                    "name": e.name,
                    "path": e.path,
                    "size_bytes": e.size_bytes,
                    "file_type": e.file_type.value,
                }
                for e in entries
                if q in e.name.lower() or q in e.path.lower()
            ]
            self._send_json({"results": cast(list[JSONValue], results)})
        except Exception as exc:
            self._send_json(
                {"error": str(exc)},
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    # ========================================================================
    # Research API (B5D-SEF)
    # ========================================================================

    def _require_research_source(self) -> ResearchSource:
        source = self.dashboard_server.research_source
        if source is None or not source.is_available():
            raise BridgeNotConfiguredError("Research source is not configured.")
        return source

    def _serve_research_summary(self) -> None:
        source = self.dashboard_server.research_source
        if source is None:
            self._send_json(
                {"available": False, "categories": {}},
                HTTPStatus.OK,
            )
            return
        self._send_json(source.registry_summary())

    def _serve_research_documents(self) -> None:
        source = self.dashboard_server.research_source
        if source is None:
            self._send_json(
                {"documents": []},
                HTTPStatus.OK,
            )
            return
        documents = [
            {
                "name": doc.name,
                "path": doc.path,
                "kind": doc.kind,
                "size_bytes": doc.size_bytes,
                "category": doc.category,
            }
            for doc in source.list_documents()
        ]
        self._send_json({"documents": cast(list[JSONValue], documents)})

    def _serve_research_reports(self) -> None:
        source = self.dashboard_server.research_source
        if source is None:
            self._send_json(
                {"reports": []},
                HTTPStatus.OK,
            )
            return
        self._send_json({"reports": cast(list[JSONValue], source.generated_reports())})

    def _serve_research_experiments(self) -> None:
        source = self.dashboard_server.research_source
        if source is None:
            self._send_json(
                {"experiments": []},
                HTTPStatus.OK,
            )
            return
        self._send_json(
            {"experiments": cast(list[JSONValue], source.list_experiments())}
        )

    def _serve_research_file(self, path: str) -> None:
        source = self._require_research_source()
        prefix = "/api/research-files/"
        if not path.startswith(prefix):
            self._send_api_not_found(path)
            return

        file_path = unquote(path[len(prefix) :])
        if not file_path:
            raise InvalidRequestError("Research document path must not be empty.")

        try:
            content = source.read_content(file_path)
        except FileNotFoundError:
            self._send_json(
                {"error": f"Research document not found: {file_path}"},
                HTTPStatus.NOT_FOUND,
            )
            return
        except ValueError as exc:
            self._send_json(
                {"error": str(exc)},
                HTTPStatus.BAD_REQUEST,
            )
            return

        self._send_json(
            {
                "path": file_path,
                "content": content,
                "size_bytes": len(content.encode("utf-8")),
            }
        )

    # ========================================================================
    # Static / SPA
    # ========================================================================

    def _serve_static(
        self,
        request_path: str,
    ) -> None:
        """Serve dashboard assets or the SPA entry point.

        This method must never be called for ``/api/...`` requests.
        """

        if request_path.startswith("/api/"):
            self._send_api_not_found(request_path)
            return

        if request_path in {"", "/"}:
            relative = "index.html"
        else:
            relative = request_path.lstrip("/")

        if ".." in relative or relative.startswith("/"):
            self._send_static_not_found()
            return

        static_root = _STATIC_ROOT.resolve()
        candidate = (_STATIC_ROOT / relative).resolve()

        try:
            candidate.relative_to(static_root)

        except ValueError:
            self._send_static_not_found()
            return

        # SPA fallback is allowed only outside /api.
        if not candidate.is_file():
            candidate = (_STATIC_ROOT / "index.html").resolve()

        if candidate.suffix.lower() not in _ALLOWED_STATIC_EXTENSIONS:
            self._send_static_not_found()
            return

        try:
            content = candidate.read_bytes()

        except OSError:
            self._send_static_not_found()
            return

        self.send_response(HTTPStatus.OK)

        self.send_header(
            "Content-Type",
            _media_type(candidate.suffix),
        )

        self.send_header(
            "Content-Length",
            str(len(content)),
        )

        self.send_header(
            "Cache-Control",
            "no-cache",
        )

        self.end_headers()

        self.wfile.write(content)

    def _send_static_not_found(self) -> None:
        """Return a minimal non-API 404 response."""
        content = b"404 Not Found"

        self.send_response(HTTPStatus.NOT_FOUND)

        self.send_header(
            "Content-Type",
            "text/plain; charset=utf-8",
        )

        self.send_header(
            "Content-Length",
            str(len(content)),
        )

        self.end_headers()

        self.wfile.write(content)

    # ========================================================================
    # JSON response helpers
    # ========================================================================

    def _send_json(
        self,
        payload: Mapping[str, JSONValue],
        status: HTTPStatus = HTTPStatus.OK,
    ) -> None:
        """Serialize and send a JSON HTTP response."""

        try:
            encoded = json.dumps(
                payload,
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8")

        except (TypeError, ValueError) as exc:
            status = HTTPStatus.INTERNAL_SERVER_ERROR

            encoded = json.dumps(
                {"error": (f"JSON serialization error: {exc}")},
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8",
        )

        self.send_header(
            "Cache-Control",
            "no-store, no-cache, must-revalidate",
        )

        self.send_header(
            "Content-Length",
            str(len(encoded)),
        )

        self.end_headers()

        self.wfile.write(encoded)

    def _send_api_not_found(
        self,
        path: str,
    ) -> None:
        """Return a JSON 404 for unknown API routes."""
        self._send_json(
            {"error": (f"Unknown API endpoint: {path}")},
            HTTPStatus.NOT_FOUND,
        )

    def _send_command_result(
        self,
        result: StructuralCommandResult,
    ) -> None:
        """Serialize a structural command result."""

        status = HTTPStatus.OK if result.ok else HTTPStatus.CONFLICT

        self._send_json(
            {
                "ok": result.ok,
                "message": result.message,
            },
            status,
        )

    # ========================================================================
    # Request parsing
    # ========================================================================

    def _read_json_object(
        self,
    ) -> dict[str, object]:
        """Read one bounded JSON object from the request body."""

        content_type = self.headers.get_content_type()

        if content_type != "application/json":
            raise UnsupportedMediaTypeError("Content-Type must be application/json.")

        length_header = self.headers.get("Content-Length")

        if length_header is None:
            raise InvalidRequestError("Content-Length header is required.")

        try:
            length = int(length_header)

        except ValueError as exc:
            raise InvalidRequestError("Invalid Content-Length header.") from exc

        if length < 0:
            raise InvalidRequestError("Content-Length cannot be negative.")

        if length > _MAX_BODY_SIZE:
            raise RequestBodyTooLargeError(
                f"Request body too large " f"(max {_MAX_BODY_SIZE} bytes)."
            )

        if length == 0:
            return {}

        raw_bytes = self.rfile.read(length)

        try:
            raw_text = raw_bytes.decode("utf-8")

        except UnicodeDecodeError as exc:
            raise InvalidRequestError("Request body must be UTF-8.") from exc

        try:
            decoded: Any = json.loads(raw_text)

        except json.JSONDecodeError as exc:
            raise InvalidRequestError(f"Invalid JSON: {exc.msg}") from exc

        if not isinstance(decoded, dict):
            raise InvalidRequestError("JSON body must be an object.")

        decoded_dict = cast("dict[str, object]", decoded)
        return {k: cast("JSONValue", v) for k, v in decoded_dict.items()}

    # ========================================================================
    # Exception handling
    # ========================================================================

    def _handle_exception(
        self,
        exc: Exception,
    ) -> None:
        """Translate request exceptions into JSON responses."""

        if isinstance(
            exc,
            BridgeNotConfiguredError,
        ):
            self._send_json(
                {
                    "error": str(exc),
                },
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return

        if isinstance(
            exc,
            RequestBodyTooLargeError,
        ):
            self._send_json(
                {
                    "error": str(exc),
                },
                HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
            )
            return

        if isinstance(
            exc,
            UnsupportedMediaTypeError,
        ):
            self._send_json(
                {
                    "error": str(exc),
                },
                HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
            )
            return

        if isinstance(
            exc,
            (
                InvalidRequestError,
                TypeError,
                ValueError,
                json.JSONDecodeError,
            ),
        ):
            self._send_json(
                {
                    "error": str(exc),
                },
                HTTPStatus.BAD_REQUEST,
            )
            return

        if isinstance(
            exc,
            FileNotFoundError,
        ):
            self._send_json(
                {
                    "error": str(exc),
                },
                HTTPStatus.NOT_FOUND,
            )
            return

        if isinstance(
            exc,
            RuntimeError,
        ):
            self._send_json(
                {
                    "error": str(exc),
                },
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return

        self._send_json(
            {"error": (f"Internal server error: " f"{type(exc).__name__}: {exc}")},
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )

    # ========================================================================
    # Field validation
    # ========================================================================

    @staticmethod
    def _string_field(
        body: dict[str, object],
        name: str,
    ) -> str:
        value = body.get(name)

        if not isinstance(value, str) or not value.strip():
            raise TypeError(f"'{name}' must be a non-empty string.")

        return value.strip()

    @staticmethod
    def _bool_field(
        body: dict[str, object],
        name: str,
    ) -> bool:
        value = body.get(name)

        if not isinstance(value, bool):
            raise TypeError(f"'{name}' must be boolean.")

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
            raise TypeError(f"'{name}' must be an integer.")

        if not minimum <= value <= maximum:
            raise ValueError(f"'{name}' must be in " f"[{minimum}, {maximum}].")

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
        raw = query.get(
            name,
            [str(default)],
        )[0]

        try:
            value = int(raw)

        except ValueError:
            raise ValueError(f"Query parameter '{name}' " f"must be an integer.")

        return cls._int_field(
            {
                name: value,
            },
            name,
            minimum=1,
            maximum=maximum,
        )

    @staticmethod
    def _optional_query_int(
        query: dict[str, list[str]],
        name: str,
    ) -> int | None:
        """Return an optional integer query parameter, or None if absent."""
        raw_list = query.get(name)
        if not raw_list or not raw_list[0]:
            return None
        try:
            return int(raw_list[0])
        except ValueError:
            raise ValueError(f"Query parameter '{name}' must be an integer.")

    @staticmethod
    def _optional_query_float(
        query: dict[str, list[str]],
        name: str,
    ) -> float | None:
        """Return an optional float query parameter, or None if absent."""
        raw_list = query.get(name)
        if not raw_list or not raw_list[0]:
            return None
        try:
            return float(raw_list[0])
        except ValueError:
            raise ValueError(f"Query parameter '{name}' must be a number.")

    @staticmethod
    def _query_offset(
        query: dict[str, list[str]],
        name: str,
        *,
        default: int,
        maximum: int,
    ) -> int:
        """Return a non-negative integer offset query parameter."""
        raw = query.get(name, [str(default)])[0]
        try:
            value = int(raw)
        except ValueError:
            raise ValueError(f"Query parameter '{name}' must be an integer.")
        if value < 0:
            raise ValueError(f"Query parameter '{name}' must be >= 0.")
        if value > maximum:
            raise ValueError(f"Query parameter '{name}' exceeds maximum {maximum}.")
        return value


# ============================================================================
# MIME types
# ============================================================================


def _media_type(
    suffix: str,
) -> str:
    """Return MIME type for one supported dashboard asset."""

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
    }.get(
        suffix.lower(),
        "application/octet-stream",
    )


# ============================================================================
# Signal handling
# ============================================================================


def _setup_signal_handlers(
    server: DashboardServer,
) -> None:
    """Install graceful process shutdown handlers."""

    def signal_handler(
        signum: int,
        frame: object,
    ) -> None:
        del signum
        del frame

        print("\n⏹️ Shutting down Brain-5D dashboard...")

        server.shutdown()

    signal.signal(
        signal.SIGINT,
        signal_handler,
    )

    signal.signal(
        signal.SIGTERM,
        signal_handler,
    )


# ============================================================================
# Server composition
# ============================================================================


def serve_dashboard(
    host: str,
    port: int,
    state: DashboardStateStore | None = None,
    snapshot_path: Path | None = None,
    structural_bridge: OperatorBridge | None = None,
    docs_root: Path | None = None,
    research_root: Path | None = None,
) -> None:
    """Run the local Brain-5D operator dashboard until interrupted."""

    store = state if state is not None else DashboardStateStore()

    # ------------------------------------------------------------------------
    # Snapshot / heatmap source
    # ------------------------------------------------------------------------

    heatmaps: SnapshotHeatmapSource | None = None

    if snapshot_path is not None and snapshot_path.exists():
        try:
            heatmaps = create_heatmap_source(snapshot_path)

        except FileNotFoundError:
            print(f"⚠️ Snapshot not found: " f"{snapshot_path}")

    # If no real heatmap source, do NOT create a demo source.
    # Synthetic demo data must never be presented as real network state.
    # The dashboard will show "NO REAL SNAPSHOT AVAILABLE" instead.
    if heatmaps is None:
        print("⚠️ No .b5d snapshot available — heatmap projection disabled")

    # ------------------------------------------------------------------------
    # Documentation source
    # ------------------------------------------------------------------------

    docs_source: DocumentationSource | None = None

    effective_docs_root = docs_root if docs_root is not None else _DEFAULT_DOCS_ROOT

    if effective_docs_root.exists():
        try:
            docs_source = create_docs_source(effective_docs_root)

        except Exception as exc:
            print("⚠️ Documentation source could not " f"be initialized: {exc}")

    # ------------------------------------------------------------------------
    # Research source (B5D-SEF)
    # ------------------------------------------------------------------------

    effective_research_root = (
        research_root if research_root is not None else _DEFAULT_RESEARCH_ROOT
    )

    research_source: ResearchSource | None = None
    if effective_research_root.exists():
        try:
            research_source = create_research_source(effective_research_root)
        except Exception as exc:
            print("⚠️ Research source could not " f"be initialized: {exc}")

    # ------------------------------------------------------------------------
    # Server
    # ------------------------------------------------------------------------

    print("🌉 Operator bridge configured: " f"{structural_bridge is not None}")

    with DashboardServer(
        (host, port),
        store,
        heatmaps,
        structural_bridge,
        docs_source,
        research_source,
    ) as server:
        if structural_bridge is not None:
            print("✅ Operator bridge attached to " "dashboard server")
        else:
            print(
                "⚠️ Dashboard started without an "
                "operator bridge; control APIs are unavailable."
            )

        print(f"🧠 Brain-5D dashboard: " f"http://{host}:{port}")

        print("Press Ctrl+C to stop")

        _setup_signal_handlers(server)

        try:
            server.serve_forever(poll_interval=0.25)

        except KeyboardInterrupt:
            print("\n⏹️ Dashboard stopped.")


# ============================================================================
# Standalone CLI
# ============================================================================


def main() -> None:
    """Run a standalone dashboard.

    A standalone dashboard has no Brain-5D OperatorBridge and therefore
    exposes monitoring/documentation only. Runtime control requires the
    integrated ``src.main`` application path.
    """

    parser = argparse.ArgumentParser(description=("Brain-5D operator dashboard"))

    parser.add_argument(
        "--host",
        default="127.0.0.1",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8765,
    )

    parser.add_argument(
        "--snapshot",
        type=Path,
    )

    parser.add_argument(
        "--docs",
        type=Path,
    )

    args = parser.parse_args()

    if not 1 <= args.port <= 65535:
        parser.error("--port must be in the range 1..65535")

    serve_dashboard(
        args.host,
        args.port,
        snapshot_path=args.snapshot,
        docs_root=args.docs,
    )


if __name__ == "__main__":
    main()
