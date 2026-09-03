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
import datetime
import json
import os
import secrets
import signal
import threading
from collections.abc import Mapping
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, cast
from urllib.parse import parse_qs, quote, unquote, urlencode, urlparse
from urllib.request import Request, urlopen

from src.embodiment import ConnectionManager
from src.learning import (
    LearningDataPartition,
    LearningObjective,
    LearningPlanOrigin,
    LearningPreparationService,
    LearningSourceRef,
)
from src.research_assistant import (
    AIRRPipeline,
    AnalysisBackend,
    ChatBackend,
    ResearchChat,
    chat_backend_from_text_backend,
    write_human_review,
)
from src.research_assistant.ollama_backend import OllamaBackend

from .control_http import handle_control_get, handle_control_post
from .control_service import DashboardControlService
from .docs_source import DocumentationSource, create_docs_source
from .experiment_workflow import ExperimentWorkflowService
from .file_manager import register_file_manager_routes
from .gate_status import GateStatusBuilder
from .heatmap_source import SnapshotHeatmapSource, create_heatmap_source
from .integration_status import IntegrationStatusBuilder
from .live_projection import (
    ActivityWindowAccumulator,
    compute_io_flow,
    compute_population_data,
    compute_rate_histogram,
    compute_spike_raster,
)
from .models import (
    ExperimentSession,
    JSONScalar,
    JSONValue,
    ParameterChangeRecord,
    ParameterSchema,
    PendingParameterChange,
)
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
        connection_manager: ConnectionManager | None = None,
    ) -> None:
        super().__init__(address, DashboardRequestHandler)

        self.dashboard_state = state
        self.heatmap_source = heatmaps
        self.structural_bridge = structural_bridge
        self.docs_source = docs_source
        self.research_source = research_source
        self.research_ai_backend: AnalysisBackend | None = None
        self.research_chat_backend: ChatBackend | None = None
        self.research_chat_context_chars = 24_000
        self.research_chat_web_search_enabled = False
        self.research_chat_system_prompt = ""
        self.research_chat_handoff_prompt = ""
        self.research_chat_vision_enabled = False
        self.research_chat_tools_enabled = False
        self.research_chat_oauth_state: str | None = None
        self.research_chat_oauth_token: str | None = None
        self.research_chat_ollama_backend: OllamaBackend | None = None
        self.research_chat_settings: dict[str, JSONValue] = {
            "provider": "unconfigured",
            "model": None,
            "endpoint": None,
            "temperature": 0.0,
            "top_p": 0.9,
            "max_tokens": 2048,
            "max_context_chars": 24_000,
            "read_only": True,
            "vision_enabled": False,
            "tools_enabled": False,
            "system_prompt": "",
            "handoff_prompt": "",
        }
        self.connection_manager = connection_manager or ConnectionManager()
        self.embodiment_pipeline_config: dict[str, bool] = {
            "sensor": False,
            "encoder": False,
            "snn": False,
            "decoder": False,
            "actuator": False,
            "feedback": False,
        }
        self.embodiment_pipeline_lock = threading.Lock()


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

            if path == "/api/state":
                self._send_json(server.dashboard_state.snapshot().to_json())
                return

            if path == "/api/config":
                snapshot = server.dashboard_state.snapshot()
                self._send_json({"runtime": snapshot.runtime})
                return

            # ----------------------------------------------------------------
            # Operator Workbench: components, parameters, health
            # ----------------------------------------------------------------

            if path == "/api/components":
                self._send_components()
                return

            if path.startswith("/api/components/"):
                self._send_component(path[len("/api/components/") :])
                return

            if path == "/api/parameters":
                self._send_parameters()
                return

            if path.startswith("/api/parameters/"):
                remainder = path[len("/api/parameters/") :]
                if remainder == "pending":
                    self._send_pending_parameters()
                    return
                self._send_parameter(remainder)
                return

            if path == "/api/health":
                self._send_health()
                return

            if path == "/api/experiment/mode":
                self._send_experiment_mode()
                return

            if path == "/api/experiment/sessions":
                self._send_experiment_sessions()
                return

            if path == "/api/experiment/workflow/catalog":
                self._send_experiment_workflow_catalog()
                return

            if path == "/api/embodiment/state":
                self._send_embodiment_state()
                return

            if path == "/api/embodiment/metrics":
                self._send_embodiment_metrics()
                return

            if path == "/api/embodiment/history":
                limit = self._query_int(query, "limit", default=100, maximum=1000)
                self._send_embodiment_history(limit)
                return

            if path == "/api/embodiment/connections":
                self._send_embodiment_connections()
                return

            if path == "/api/embodiment/pipeline":
                self._send_embodiment_pipeline()
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

            if path == "/api/live/io-flow":
                self._serve_live_io_flow()
                return

            if path == "/api/live/population":
                self._serve_live_population()
                return

            if path == "/api/live/histogram":
                self._serve_live_histogram(query)
                return

            if path == "/api/live/raster":
                self._serve_live_raster()
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
            if path == "/api/learning/preparation":
                self._list_learning_preparations()
                return

            if path == "/api/research/documents":
                self._serve_research_documents()
                return

            if path == "/api/research/reports":
                self._serve_research_reports()
                return

            if path == "/api/research/ai-reports":
                self._serve_ai_reports(query)
                return

            if path == "/api/research/chat/settings":
                self._send_json(self.dashboard_server.research_chat_settings)
                return
            if path == "/api/research/chat/health":
                self._research_chat_health()
                return
            if path == "/api/research/chat/providers":
                self._research_chat_providers()
                return
            if path == "/api/research/chat/oauth/start":
                self._research_chat_oauth_start()
                return
            if path == "/api/research/chat/oauth/callback":
                self._research_chat_oauth_callback(query)
                return

            if path.startswith("/api/research/ai-reports/"):
                self._serve_ai_report(path)
                return

            if path == "/api/research/experiments":
                self._serve_research_experiments()
                return

            if path.startswith("/api/research-files/"):
                self._serve_research_file(path)
                return

            # ----------------------------------------------------------------
            # Unified File Manager (Research + Docs combined)
            # ----------------------------------------------------------------

            if register_file_manager_routes(
                self,
                path,
                query,
                self.dashboard_server.research_source,
                self.dashboard_server.docs_source,
            ):
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
            # Release history (immutable release records + current development)
            # ----------------------------------------------------------------

            if path == "/api/releases":
                self._serve_releases()
                return

            if path == "/api/releases/current":
                self._serve_release_current()
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
                self._send_json(
                    {
                        "available": True,
                        "count": len(errors),
                        "events": cast(list[JSONValue], errors),
                    }
                )
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
            # Parameter pending changes
            # ----------------------------------------------------------------

            body = self._read_json_object()

            if path == "/api/parameters/pending/apply":
                self._apply_pending_parameters(body)
                return

            if path == "/api/parameters/pending/save-profile":
                self._apply_pending_parameters(body, save_profile=True)
                return

            if path == "/api/parameters/pending/cancel":
                self._cancel_pending_parameters(body)
                return

            if path == "/api/embodiment/pipeline":
                self._set_embodiment_pipeline(body)
                return

            if path.startswith("/api/parameters/") and path.endswith("/pending"):
                name = unquote(path[len("/api/parameters/") : -len("/pending")])
                self._set_pending_parameter(name, body)
                return

            # ----------------------------------------------------------------
            # Experiment mode
            # ----------------------------------------------------------------

            if path == "/api/experiment/mode":
                self._set_experiment_mode(body)
                return

            if path == "/api/experiment/session/start":
                self._start_experiment_session(body)
                return

            if path == "/api/experiment/session/stop":
                self._stop_experiment_session(body)
                return

            if path == "/api/experiment/note":
                self._add_experiment_note(body)
                return

            if path == "/api/experiment/workflow/run":
                self._run_experiment_workflow(body)
                return

            if path == "/api/research/ai-reports/generate":
                self._generate_ai_report(body)
                return

            if path == "/api/research/chat":
                self._research_chat(body)
                return

            if path == "/api/learning/run":
                self._run_learning_workflow(body)
                return

            if path == "/api/learning/preparation":
                self._learning_preparation(body)
                return

            if path == "/api/research/chat/settings":
                self._update_research_chat_settings(body)
                return

            if path.startswith("/api/research/ai-reports/") and path.endswith(
                "/review"
            ):
                self._write_ai_review(path, body)
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
        query = parse_qs(parsed.query)

        try:
            # ----------------------------------------------------------------
            # Unified File Manager save endpoint
            # ----------------------------------------------------------------
            if register_file_manager_routes(
                self,
                path,
                query,
                self.dashboard_server.research_source,
                self.dashboard_server.docs_source,
            ):
                return

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

    def log_message(self, format: str, *args: object) -> None:  # noqa: ARG001
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

        elif path == "/api/structural/live-loop":
            payload = self._read_structural_live_loop_artifact()

        else:
            self._send_api_not_found(path)
            return

        self._send_json(payload)

    # ========================================================================
    # Structural live loop artifact reader
    # ========================================================================

    def _read_structural_live_loop_artifact(self) -> dict[str, Any]:
        """Read the structural live loop verification artifact.

        Returns a dict with the artifact content, or a minimal error payload
        if the artifact is missing or unparseable.
        """
        artifact_path = (
            _DEFAULT_RESEARCH_ROOT.parent
            / "research"
            / "generated"
            / "verification"
            / "structural_live_loop.json"
        )
        if not artifact_path.exists():
            return {
                "available": False,
                "status": "missing",
                "proofs": {},
                "message": "Artifact not found",
            }
        try:
            data = json.loads(artifact_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return {
                "available": False,
                "status": "unparseable",
                "proofs": {},
                "message": str(exc),
            }

        proofs = data.get("proofs", {})
        if not isinstance(proofs, dict):
            proofs = {}

        return {
            "available": True,
            "status": data.get("status", "unknown"),
            "proofs": proofs,
            "tested_tree_digest": data.get("tested_tree_digest"),
            "message": data.get("message", ""),
        }

    # ========================================================================
    # Network Inspector (real 5D coordinates, Phase 8/9)
    # ========================================================================

    def _embodiment_payload(self) -> dict[str, JSONValue]:
        snapshot = self.dashboard_server.dashboard_state.snapshot()
        embodiment = snapshot.embodiment
        metrics = embodiment.to_json()
        environment_kind = embodiment.environment_kind
        configured = environment_kind != "unconfigured"
        return {
            "available": configured,
            "configured": configured,
            "tick": snapshot.system.tick,
            "loop_status": "active" if configured else "unconfigured",
            "loop": [
                {
                    "id": "environment",
                    "label": "Environment",
                    "status": environment_kind,
                },
                {
                    "id": "sensor",
                    "label": "Sensor",
                    "status": (
                        "active" if embodiment.active_sensors > 0 else "unavailable"
                    ),
                },
                {"id": "encoder", "label": "Encoder", "status": "not_reported"},
                {"id": "snn", "label": "SNN", "status": snapshot.status},
                {"id": "decoder", "label": "Decoder", "status": "not_reported"},
                {
                    "id": "actuator",
                    "label": "Actuator",
                    "status": (
                        "active" if embodiment.active_actuators > 0 else "unavailable"
                    ),
                },
            ],
            "metrics": metrics,
            "details": {
                "sensor_values": None,
                "actuator_values": None,
                "environment_state": metrics.get("last_observation_state"),
                "observation_tick": metrics.get("last_observation_tick"),
                "observation_terminated": metrics.get("last_observation_terminated"),
                "observation_truncated": metrics.get("last_observation_truncated"),
                "message": (
                    "Environment observation is published; sensor and actuator "
                    "self-feedback values are not published by the current adapters."
                    if metrics.get("last_observation_state") is not None
                    else "No environment observation is published by the current embodiment runtime."
                ),
            },
        }

    def _send_embodiment_state(self) -> None:
        """Serve the current closed-loop embodiment contract."""
        self._send_json(self._embodiment_payload())

    def _send_embodiment_metrics(self) -> None:
        """Serve only measured embodiment metrics from the latest snapshot."""
        payload = self._embodiment_payload()
        self._send_json(
            {
                "available": payload["available"],
                "tick": payload["tick"],
                "metrics": payload["metrics"],
            }
        )

    def _send_embodiment_history(self, limit: int) -> None:
        """Serve measured embodiment history without synthesizing samples."""
        history: list[JSONValue] = []
        seen: set[tuple[int, str, int, float, str]] = set()
        for snapshot in self.dashboard_server.dashboard_state.get_history(limit):
            metrics = snapshot.embodiment
            key = (
                snapshot.system.tick,
                metrics.environment_kind,
                metrics.episode,
                metrics.episode_reward,
                metrics.last_action,
            )
            if key in seen:
                continue
            seen.add(key)
            history.append(
                {
                    "tick": snapshot.system.tick,
                    "metrics": metrics.to_json(),
                }
            )
        configured = any(
            snapshot.embodiment.environment_kind != "unconfigured"
            for snapshot in self.dashboard_server.dashboard_state.get_history(limit)
        )
        self._send_json(
            {
                "available": configured and bool(history),
                "count": len(history),
                "history": history,
            }
        )

    def _send_embodiment_connections(self) -> None:
        """Serve discovered and configured body connections without activating them."""
        self._send_json(self.dashboard_server.connection_manager.to_json())

    def _send_embodiment_pipeline(self) -> None:
        """Serve pipeline switches separately from hardware availability."""
        metrics = self.dashboard_server.dashboard_state.snapshot().embodiment
        with self.dashboard_server.embodiment_pipeline_lock:
            enabled = dict(self.dashboard_server.embodiment_pipeline_config)
        implemented = {
            "sensor": metrics.active_sensors > 0,
            "encoder": False,
            "snn": True,
            "decoder": False,
            "actuator": metrics.active_actuators > 0,
            "feedback": metrics.last_observation_state is not None,
        }
        self._send_json(
            {
                "stages": {
                    stage: {
                        "enabled": enabled[stage],
                        "implemented": implemented[stage],
                    }
                    for stage in enabled
                },
                "message": "Enabled stages are configuration intent; unavailable adapters remain inactive.",
            }
        )

    def _set_embodiment_pipeline(self, body: dict[str, object]) -> None:
        """Set one pipeline switch without activating an adapter or device."""
        stage = body.get("stage")
        enabled = body.get("enabled")
        valid_stages = {"sensor", "encoder", "snn", "decoder", "actuator", "feedback"}
        if not isinstance(stage, str) or stage not in valid_stages:
            self._send_json(
                {"error": "Unknown embodiment pipeline stage."}, HTTPStatus.BAD_REQUEST
            )
            return
        if not isinstance(enabled, bool):
            self._send_json(
                {"error": "Pipeline enabled must be boolean."}, HTTPStatus.BAD_REQUEST
            )
            return
        with self.dashboard_server.embodiment_pipeline_lock:
            self.dashboard_server.embodiment_pipeline_config[stage] = enabled
        self._send_json({"ok": True, "stage": stage, "enabled": enabled})

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
                inspector.neurons(
                    limit=limit, offset=offset, active_only=active_only
                ).to_json()
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
        config_dict: dict[str, object] = cast(
            "dict[str, object]", getattr(bridge, "config_dict", None) or {}
        )
        builder = GateStatusBuilder(
            bridge=bridge,
            research_source=server.research_source,
            repo_root=Path(__file__).resolve().parents[2],
            config_dict=config_dict,
        )
        self._send_json(builder.build())

    def _serve_releases(self) -> None:
        """Serve the immutable release history plus the current development node.

        Historical releases are read from ``releases/*.json`` and are never
        re-evaluated against the current source tree. The current node is read
        from ``releases/current.json``.
        """
        repo_root = Path(__file__).resolve().parents[2]
        releases_dir = repo_root / "releases"
        records: list[dict[str, object]] = []
        current: dict[str, object] | None = None

        if releases_dir.is_dir():
            for path in sorted(releases_dir.glob("*.json")):
                if path.name == "current.json":
                    continue
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    records.append(cast("dict[str, object]", data))
                except Exception:
                    pass

        current_path = releases_dir / "current.json"
        if current_path.exists():
            try:
                current = cast(
                    "dict[str, object]",
                    json.loads(current_path.read_text(encoding="utf-8")),
                )
            except Exception:
                current = None

        self._send_json(
            {
                "releases": cast(list[JSONValue], records),
                "current": cast(JSONValue, current),
                "source": "releases/",
            }
        )

    def _serve_release_current(self) -> None:
        """Serve the current development release record only."""
        repo_root = Path(__file__).resolve().parents[2]
        current_path = repo_root / "releases" / "current.json"
        if not current_path.exists():
            self._send_json(
                {
                    "version": "unknown",
                    "status": "unknown",
                    "source": "releases/current.json",
                    "error": "releases/current.json not found",
                }
            )
            return
        try:
            data = json.loads(current_path.read_text(encoding="utf-8"))
            self._send_json(cast("dict[str, JSONValue]", data))
        except Exception as exc:
            self._send_json(
                {
                    "version": "unknown",
                    "status": "unknown",
                    "source": "releases/current.json",
                    "error": str(exc),
                }
            )

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

        # Check if telemetry is available
        if bridge.live_projection.frame_store is None:
            self._send_json(
                {
                    "error": "Live telemetry is not enabled (no TelemetryFrameStore configured)."
                },
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
    # Live IO Flow
    # ========================================================================

    def _serve_live_io_flow(self) -> None:
        try:
            bridge = self._require_bridge()
        except BridgeNotConfiguredError:
            self._send_json(
                {"error": "No live runtime available."},
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return

        network = getattr(bridge.controller, "network", None)
        if network is None:
            self._send_json(
                {"error": "Live network is not available."},
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return

        telemetry = bridge.live_projection.frame_store
        acc: ActivityWindowAccumulator | None = (
            telemetry.accumulator if telemetry is not None else None
        )

        try:
            data = compute_io_flow(network, acc)
        except Exception as exc:
            self._send_json(
                {"error": str(exc)},
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
            return

        self._send_json(data.to_json())

    # ========================================================================
    # Live Population Overview
    # ========================================================================

    def _serve_live_population(self) -> None:
        try:
            bridge = self._require_bridge()
        except BridgeNotConfiguredError:
            self._send_json(
                {"error": "No live runtime available."},
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return

        network = getattr(bridge.controller, "network", None)
        if network is None:
            self._send_json(
                {"error": "Live network is not available."},
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return

        telemetry = bridge.live_projection.frame_store
        acc: ActivityWindowAccumulator | None = (
            telemetry.accumulator if telemetry is not None else None
        )

        try:
            data = compute_population_data(network, acc)
        except Exception as exc:
            self._send_json(
                {"error": str(exc)},
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
            return

        self._send_json(data.to_json())

    # ========================================================================
    # Live Rate Histogram
    # ========================================================================

    def _serve_live_histogram(self, query: dict[str, list[str]]) -> None:
        try:
            bridge = self._require_bridge()
        except BridgeNotConfiguredError:
            self._send_json(
                {"error": "No live runtime available."},
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return

        network = getattr(bridge.controller, "network", None)
        if network is None:
            self._send_json(
                {"error": "Live network is not available."},
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return

        telemetry = bridge.live_projection.frame_store
        acc: ActivityWindowAccumulator | None = (
            telemetry.accumulator if telemetry is not None else None
        )
        num_bins = int(query.get("bins", ["30"])[0])

        try:
            data = compute_rate_histogram(network, acc, num_bins=num_bins)
        except Exception as exc:
            self._send_json(
                {"error": str(exc)},
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
            return

        self._send_json(data.to_json())

    # ========================================================================
    # Live Spike Raster
    # ========================================================================

    def _serve_live_raster(self) -> None:
        try:
            bridge = self._require_bridge()
        except BridgeNotConfiguredError:
            self._send_json(
                {"error": "No live runtime available."},
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return

        network = getattr(bridge.controller, "network", None)
        if network is None:
            self._send_json(
                {"error": "Live network is not available."},
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return

        telemetry = bridge.live_projection.frame_store
        acc: ActivityWindowAccumulator | None = (
            telemetry.accumulator if telemetry is not None else None
        )

        try:
            data = compute_spike_raster(network, acc)
        except Exception as exc:
            self._send_json(
                {"error": str(exc)},
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
            return

        self._send_json(data.to_json())

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

    def _serve_ai_reports(self, query: dict[str, list[str]]) -> None:
        source = self.dashboard_server.research_source
        if source is None:
            self._send_json({"reports": []})
            return
        experiment_id = query.get("experiment_id", [None])[0]
        self._send_json(
            {"reports": cast(list[JSONValue], source.ai_reports(experiment_id))}
        )

    def _serve_ai_report(self, path: str) -> None:
        source = self._require_research_source()
        report_path = unquote(path[len("/api/research/ai-reports/") :])
        if not report_path or report_path.endswith("/review"):
            self._send_api_not_found(path)
            return
        try:
            content = source.read_content(f"reports/{report_path}")
        except FileNotFoundError:
            self._send_json({"error": "AI report not found."}, HTTPStatus.NOT_FOUND)
            return
        self._send_json({"path": f"reports/{report_path}", "content": content})

    def _generate_ai_report(self, body: dict[str, object]) -> None:
        experiment_id = body.get("experiment_id")
        if not isinstance(experiment_id, str) or not experiment_id:
            raise InvalidRequestError("experiment_id is required.")
        backend = self.dashboard_server.research_ai_backend
        source = self._require_research_source()
        if backend is None:
            self._send_json(
                {"error": "No AI backend is configured; report was not generated."},
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return
        report = AIRRPipeline(source.root()).analyze(experiment_id, backend)
        self._send_json(report.to_dict(), HTTPStatus.CREATED)

    def _research_chat(self, body: dict[str, object]) -> None:
        source = self._require_research_source()
        action = body.get("action", "ask")
        if action == "execute_registered_experiment":
            workflow = body.get("workflow")
            if not isinstance(workflow, dict):
                raise InvalidRequestError("workflow object is required for execution.")
            self._run_experiment_workflow(cast(dict[str, object], workflow))
            return
        if action != "ask":
            raise InvalidRequestError("Unknown research chat action.")
        response_mode = body.get("response_mode", "detailed")
        if response_mode not in {"short", "detailed", "scientific"}:
            raise InvalidRequestError(
                "response_mode must be short, detailed, or scientific."
            )
        response_mode = str(response_mode)
        message = body.get("message")
        if not isinstance(message, str) or not message.strip():
            raise InvalidRequestError("message is required.")
        backend = self.dashboard_server.research_chat_backend
        if backend is None:
            self._send_json(
                {"error": "No research chat backend is configured."},
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return
        docs = self.dashboard_server.docs_source or create_docs_source(
            _DEFAULT_DOCS_ROOT
        )
        web_context = ""
        if body.get("web_search") is True:
            if not self.dashboard_server.research_chat_web_search_enabled:
                raise InvalidRequestError("Web search is disabled in chat settings.")
            web_context = self._search_web(message)
        conversation_context = body.get("conversation_context", "")
        if (
            not isinstance(conversation_context, str)
            or len(conversation_context) > 20_000
        ):
            raise InvalidRequestError(
                "conversation_context must be text up to 20000 characters."
            )
        images = body.get("images", [])
        if not isinstance(images, list):
            raise InvalidRequestError(
                "images must contain at most four small base64 strings."
            )
        raw_images = cast(list[object], images)
        if (
            any(
                not isinstance(image, str) or len(image) > 4_000_000
                for image in raw_images
            )
            or len(raw_images) > 4
        ):
            raise InvalidRequestError(
                "images must contain at most four small base64 strings."
            )
        images = cast(list[str], raw_images)
        if images and not self.dashboard_server.research_chat_vision_enabled:
            raise InvalidRequestError("Vision is disabled in chat settings.")
        context_chars = self.dashboard_server.research_chat_context_chars
        requested_context_chars = body.get("max_context_chars")
        if requested_context_chars is not None:
            if (
                not isinstance(requested_context_chars, int)
                or not 4_000 <= requested_context_chars <= 120_000
            ):
                raise InvalidRequestError(
                    "max_context_chars must be between 4000 and 120000."
                )
            context_chars = requested_context_chars
        snapshot = self.dashboard_server.dashboard_state.snapshot()
        system_context = json.dumps(
            {
                "current_time": datetime.datetime.now().astimezone().isoformat(),
                "runtime": snapshot.runtime,
                "system": snapshot.system,
                "health": snapshot.health.to_json(),
            },
            default=str,
            sort_keys=True,
        )
        request_backend = backend
        ollama = self.dashboard_server.research_chat_ollama_backend
        if ollama is not None and (
            images or self.dashboard_server.research_chat_tools_enabled
        ):
            request_backend = chat_backend_from_text_backend(
                lambda prompt: ollama.generate_text(
                    prompt,
                    images=images,
                    tools=(
                        []
                        if not self.dashboard_server.research_chat_tools_enabled
                        else []
                    ),
                )
            )
        answer, metadata = ResearchChat(
            cast(Any, source),
            cast(Any, docs),
            request_backend,
            max_context_chars=context_chars,
            system_context=system_context,
            system_prompt=self.dashboard_server.research_chat_system_prompt,
            conversation_context=conversation_context,
            handoff_prompt=self.dashboard_server.research_chat_handoff_prompt,
            response_mode=response_mode,
            web_context=web_context,
        ).answer(message)
        self._send_json(
            {"answer": answer, "metadata": cast(JSONValue, metadata), "grounded": True}
        )

    def _run_learning_workflow(self, body: dict[str, object]) -> None:
        """Run only the fixed, explicitly operator-triggered learning workflow."""
        if body.get("operator_confirmed") is not True:
            raise InvalidRequestError(
                "operator_confirmed must be true to start learning."
            )
        workflow = dict(body)
        workflow.pop("operator_confirmed", None)
        workflow["protocol"] = "science_suite_v1"
        self._run_experiment_workflow(workflow)

    def _learning_preparation(self, body: dict[str, object]) -> None:
        """Persist or approve a guarded, non-executable learning preparation."""
        source = self._require_research_source()
        service = LearningPreparationService(
            source.root() / "learning" / "preparations"
        )
        action = body.get("action", "create")
        if action == "approve":
            plan_id = self._string_field(body, "plan_id")
            approved_by = self._string_field(body, "approved_by")
            plan = service.approve(
                service.load_proposal(plan_id),
                approved_by=approved_by,
                approval_note=str(body.get("approval_note", "")),
            )
            path = service.persist_approved(plan)
            self._send_json(
                {
                    "status": "approved",
                    "path": str(path.relative_to(source.root())).replace("\\", "/"),
                    "plan": cast(JSONValue, plan.to_dict()),
                },
                HTTPStatus.CREATED,
            )
            return
        if action != "create":
            raise InvalidRequestError("action must be create or approve")
        objective = body.get("objective")
        if not isinstance(objective, dict):
            raise InvalidRequestError("objective object is required")
        typed_objective = cast(dict[str, object], objective)
        raw_sources = body.get("sources", [])
        if not isinstance(raw_sources, list):
            raise InvalidRequestError("sources must be a list")
        typed_sources = cast(list[object], raw_sources)
        sources = [
            self._learning_source_from_mapping(cast(dict[str, object], item))
            for item in typed_sources
            if isinstance(item, dict)
        ]
        proposal = service.create_proposal(
            plan_id=self._string_field(body, "plan_id"),
            objective=LearningObjective(
                objective_id=self._mapping_string(typed_objective, "objective_id"),
                description=self._mapping_string(typed_objective, "description"),
                success_metric=self._mapping_string(typed_objective, "success_metric"),
                evaluation_question=self._mapping_string(
                    typed_objective, "evaluation_question"
                ),
            ),
            sources=sources,
            baseline_protocol=self._string_field(body, "baseline_protocol"),
            exposure_protocol=self._string_field(body, "exposure_protocol"),
            evaluation_protocol=self._string_field(body, "evaluation_protocol"),
            stopping_rule=self._string_field(body, "stopping_rule"),
            controls=(
                [str(value) for value in cast(list[object], body.get("controls", []))]
                if isinstance(body.get("controls", []), list)
                else []
            ),
            origin=LearningPlanOrigin(
                str(body.get("origin", LearningPlanOrigin.HUMAN.value))
            ),
            rationale=str(body.get("rationale", "")),
            ai_interaction_id=(
                cast(str | None, body.get("ai_interaction_id"))
                if isinstance(body.get("ai_interaction_id"), str)
                else None
            ),
            raw_proposal_payload=body,
        )
        path = service.persist_proposal(proposal)
        self._send_json(
            {
                "status": "created",
                "path": str(path.relative_to(source.root())).replace("\\", "/"),
                "proposal": cast(JSONValue, proposal.to_dict()),
            },
            HTTPStatus.CREATED,
        )

    def _list_learning_preparations(self) -> None:
        source = self._require_research_source()
        service = LearningPreparationService(
            source.root() / "learning" / "preparations"
        )
        self._send_json({"plans": cast(JSONValue, service.list_plans())})

    @staticmethod
    def _mapping_string(mapping: dict[str, object], name: str) -> str:
        value = mapping.get(name)
        if not isinstance(value, str) or not value.strip():
            raise InvalidRequestError(f"'{name}' must be a non-empty string.")
        return value.strip()

    @classmethod
    def _learning_source_from_mapping(
        cls, item: dict[str, object]
    ) -> LearningSourceRef:
        return LearningSourceRef(
            source_id=cls._mapping_string(item, "source_id"),
            digest=cls._mapping_string(item, "digest"),
            origin=cls._mapping_string(item, "origin"),
            partition=LearningDataPartition(cls._mapping_string(item, "partition")),
            trust=str(item.get("trust", "UNKNOWN")),
        )

    def _update_research_chat_settings(self, body: dict[str, object]) -> None:
        """Update bounded runtime chat preferences from the settings panel."""
        server = self.dashboard_server
        if "system_prompt" in body:
            prompt = body["system_prompt"]
            if not isinstance(prompt, str) or len(prompt) > 8_000:
                raise InvalidRequestError(
                    "system_prompt must be text up to 8000 characters."
                )
            server.research_chat_system_prompt = prompt.strip()
        if "handoff_prompt" in body:
            prompt = body["handoff_prompt"]
            if not isinstance(prompt, str) or len(prompt) > 8_000:
                raise InvalidRequestError(
                    "handoff_prompt must be text up to 8000 characters."
                )
            server.research_chat_handoff_prompt = prompt.strip()
        for key in ("vision_enabled", "tools_enabled"):
            if key in body:
                value = body[key]
                if not isinstance(value, bool):
                    raise InvalidRequestError(f"{key} must be boolean.")
                setattr(server, f"research_chat_{key}", value)
                server.research_chat_settings[key] = value
        for key in ("model", "endpoint"):
            if key in body:
                value = body[key]
                if not isinstance(value, str) or not value.strip() or len(value) > 500:
                    raise InvalidRequestError(f"{key} must be a non-empty string.")
                if server.research_chat_ollama_backend is not None:
                    setattr(server.research_chat_ollama_backend, key, value.strip())
                server.research_chat_settings[key] = value.strip()
        for key, minimum, maximum in (
            ("temperature", 0.0, 2.0),
            ("top_p", 0.0, 1.0),
        ):
            if key in body:
                value = body[key]
                if (
                    not isinstance(value, (int, float))
                    or not minimum <= float(value) <= maximum
                ):
                    raise InvalidRequestError(f"{key} is outside its allowed range.")
                if server.research_chat_ollama_backend is not None:
                    setattr(server.research_chat_ollama_backend, key, float(value))
                server.research_chat_settings[key] = float(value)
        if "max_tokens" in body:
            value = body["max_tokens"]
            if not isinstance(value, int) or not 128 <= value <= 16_384:
                raise InvalidRequestError("max_tokens must be between 128 and 16384.")
            if server.research_chat_ollama_backend is not None:
                server.research_chat_ollama_backend.max_tokens = value
            server.research_chat_settings["max_tokens"] = value
        if "max_context_chars" in body:
            value = body["max_context_chars"]
            if not isinstance(value, int) or not 4_000 <= value <= 120_000:
                raise InvalidRequestError(
                    "max_context_chars must be between 4000 and 120000."
                )
            server.research_chat_context_chars = value
            server.research_chat_settings["max_context_chars"] = value
        server.research_chat_settings["system_prompt"] = (
            server.research_chat_system_prompt
        )
        server.research_chat_settings["handoff_prompt"] = (
            server.research_chat_handoff_prompt
        )
        self._send_json(server.research_chat_settings)

    def _research_chat_oauth_start(self) -> None:
        """Start Microsoft Entra PKCE authorization without exposing client secrets."""
        client_id = os.environ.get("BRAIN5D_MICROSOFT_CLIENT_ID", "").strip()
        tenant = os.environ.get("BRAIN5D_MICROSOFT_TENANT", "common").strip()
        redirect_uri = os.environ.get(
            "BRAIN5D_MICROSOFT_REDIRECT_URI",
            "http://127.0.0.1:8765/api/research/chat/oauth/callback",
        ).strip()
        if not client_id:
            self._send_json(
                {
                    "ok": False,
                    "error": "BRAIN5D_MICROSOFT_CLIENT_ID is not configured.",
                },
                HTTPStatus.NOT_IMPLEMENTED,
            )
            return
        state = secrets.token_urlsafe(32)
        self.dashboard_server.research_chat_oauth_state = state
        params = {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "response_mode": "query",
            "scope": "openid profile offline_access",
            "state": state,
        }
        authorize = f"https://login.microsoftonline.com/{quote(tenant)}/oauth2/v2.0/authorize?{urlencode(params)}"
        self._send_json(
            {"ok": True, "authorize_url": authorize, "provider": "microsoft-copilot"}
        )

    def _research_chat_oauth_callback(self, query: dict[str, list[str]]) -> None:
        """Validate the OAuth callback state; token exchange remains server-side configuration."""
        state = query.get("state", [""])[0]
        code = query.get("code", [""])[0]
        if not state or not secrets.compare_digest(
            state, self.dashboard_server.research_chat_oauth_state or ""
        ):
            self._send_json(
                {"ok": False, "error": "Invalid OAuth state."}, HTTPStatus.BAD_REQUEST
            )
            return
        if not code:
            self._send_json(
                {
                    "ok": False,
                    "error": query.get(
                        "error_description", ["Authorization was denied."]
                    )[0],
                },
                HTTPStatus.BAD_REQUEST,
            )
            return
        self.dashboard_server.research_chat_oauth_token = code
        self.dashboard_server.research_chat_oauth_state = None
        self._send_json(
            {
                "ok": True,
                "message": "Authorization code received. Configure the server-side token exchange before enabling Copilot chat.",
            },
            HTTPStatus.OK,
        )

    def _research_chat_health(self) -> None:
        """Probe the configured Ollama provider without generating tokens."""
        backend = self.dashboard_server.research_chat_ollama_backend
        if backend is None:
            self._send_json(
                {
                    "ok": False,
                    "provider": "unconfigured",
                    "error": "No provider configured.",
                },
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return
        tags_endpoint = backend.endpoint.rsplit("/api/", 1)[0] + "/api/tags"
        try:
            with urlopen(
                tags_endpoint, timeout=3
            ) as response:  # nosec B310: configured local provider endpoint
                ok = 200 <= response.status < 300
            self._send_json({"ok": ok, "provider": backend.name})
        except OSError as exc:
            self._send_json(
                {"ok": False, "provider": backend.name, "error": str(exc)},
                HTTPStatus.SERVICE_UNAVAILABLE,
            )

    def _research_chat_providers(self) -> None:
        """Return configured provider choices and locally available Ollama models."""
        backend = self.dashboard_server.research_chat_ollama_backend
        models: list[str] = []
        if backend is not None:
            tags_endpoint = backend.endpoint.rsplit("/api/", 1)[0] + "/api/tags"
            try:
                with urlopen(
                    tags_endpoint, timeout=3
                ) as response:  # nosec B310: configured local provider endpoint
                    payload = cast(
                        dict[str, Any], json.loads(response.read().decode("utf-8"))
                    )
                raw_models = payload.get("models", [])
                if isinstance(raw_models, list):
                    for raw_model in cast(list[object], raw_models):
                        if isinstance(raw_model, dict):
                            model = cast(dict[str, object], raw_model)
                            model_name = model.get("name")
                            if isinstance(model_name, str):
                                models.append(model_name)
            except (OSError, ValueError, TypeError):
                pass
        self._send_json(
            cast(
                dict[str, JSONValue],
                {
                    "providers": [
                        {
                            "id": "ollama",
                            "label": "Ollama",
                            "available": backend is not None,
                            "capabilities": ["chat", "vision", "tools"],
                        },
                        {
                            "id": "microsoft-copilot",
                            "label": "Microsoft Copilot",
                            "available": bool(
                                self.dashboard_server.research_chat_oauth_token
                            ),
                            "reason": "Requires Microsoft Entra OAuth and an approved Copilot API endpoint.",
                        },
                    ],
                    "models": cast(list[JSONValue], models),
                },
            )
        )

    def _search_web(self, query: str) -> str:
        """Read a small set of structured public search results."""
        request = Request(
            "https://api.duckduckgo.com/?q=" + quote(query) + "&format=json&no_html=1",
            headers={"User-Agent": "Brain-5D Research Assistant/1.0"},
        )
        with urlopen(request, timeout=10) as response:  # nosec B310: fixed HTTPS host
            payload = cast(
                dict[str, Any], json.loads(response.read(256_000).decode("utf-8"))
            )
        results: list[str] = []
        abstract = payload.get("AbstractText")
        abstract_url = payload.get("AbstractURL")
        if isinstance(abstract, str) and abstract and isinstance(abstract_url, str):
            results.append(f"- {abstract} ({abstract_url})")
        for topic in payload.get("RelatedTopics", []):
            if not isinstance(topic, dict):
                continue
            topic_data = cast(dict[str, object], topic)
            text = topic_data.get("Text")
            url = topic_data.get("FirstURL")
            if isinstance(text, str) and isinstance(url, str):
                results.append(f"- {text} ({url})")
            if len(results) >= 5:
                break
        return "\n".join(results) or "No structured web results were returned."

    def _write_ai_review(self, path: str, body: dict[str, object]) -> None:
        source = self._require_research_source()
        prefix = "/api/research/ai-reports/"
        report_ref = unquote(path[len(prefix) : -len("/review")])
        parts = report_ref.split("/", 1)
        if len(parts) != 2:
            raise InvalidRequestError("AI report review path is invalid.")
        review = dict(body)
        review.pop("report_id", None)
        review_path = write_human_review(source.root(), parts[0], parts[1], review)
        self._send_json(
            {
                "ok": True,
                "path": str(review_path.relative_to(source.root())).replace("\\", "/"),
            },
            HTTPStatus.CREATED,
        )

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
    # Unified File Manager (Research + Docs)
    # ========================================================================

    def _serve_files_tree(self, query: dict[str, list[str]]) -> None:
        """Serve the unified file tree (research + docs)."""
        self._send_json(
            {
                "tree": [],
                "source": "unified",
            }
        )

    def _serve_files_search(self, query: dict[str, list[str]]) -> None:
        """Serve unified file search results."""
        self._send_json(
            {
                "results": [],
                "total": 0,
                "source": "unified",
            }
        )

    def _serve_files_statistics(self) -> None:
        """Serve unified file statistics."""
        self._send_json(
            {
                "total_files": 0,
                "total_size_bytes": 0,
                "source": "unified",
            }
        )

    def _serve_file_content(self, path: str, query: dict[str, list[str]]) -> None:
        """Serve content of a unified file."""
        self._send_json(
            {
                "path": path,
                "content": "",
                "size_bytes": 0,
            }
        )

    # ========================================================================
    # Operator Workbench Helpers
    # ========================================================================

    def _send_components(self) -> None:
        """Serve all component statuses."""
        snapshot = self.dashboard_server.dashboard_state.snapshot()
        components = snapshot.components or {}
        self._send_json(
            {
                "components": {k: v.to_json() for k, v in components.items()},
                "count": len(components),
            }
        )

    def _send_component(self, name: str) -> None:
        """Serve a single component status."""
        snapshot = self.dashboard_server.dashboard_state.snapshot()
        components = snapshot.components or {}
        component = components.get(name)
        if component is None:
            self._send_json(
                {"error": f"Component '{name}' not found"},
                HTTPStatus.NOT_FOUND,
            )
            return
        self._send_json(component.to_json())

    def _send_parameters(self) -> None:
        """Serve all parameter schemas."""
        snapshot = self.dashboard_server.dashboard_state.snapshot()
        parameters = snapshot.parameters or {}
        self._send_json(
            {
                "parameters": {k: v.to_json() for k, v in parameters.items()},
                "count": len(parameters),
            }
        )

    def _send_parameter(self, name: str) -> None:
        """Serve a single parameter schema."""
        snapshot = self.dashboard_server.dashboard_state.snapshot()
        parameters = snapshot.parameters or {}
        # Support both raw name and URL-encoded dotted names
        decoded = unquote(name)
        parameter = parameters.get(decoded) or parameters.get(name)
        if parameter is None:
            self._send_json(
                {"error": f"Parameter '{decoded}' not found"},
                HTTPStatus.NOT_FOUND,
            )
            return
        self._send_json(parameter.to_json())

    def _send_health(self) -> None:
        """Serve the aggregated health snapshot."""
        snapshot = self.dashboard_server.dashboard_state.snapshot()
        self._send_json(snapshot.health.to_json())

    def _send_experiment_mode(self) -> None:
        """Serve the current experiment mode and active session."""
        snapshot = self.dashboard_server.dashboard_state.snapshot()
        self._send_json(snapshot.experiment_state.to_json())

    def _send_experiment_sessions(self) -> None:
        """Serve the full experiment session history."""
        snapshot = self.dashboard_server.dashboard_state.snapshot()
        sessions = snapshot.experiment_state.sessions
        self._send_json(
            {
                "sessions": [s.to_json() for s in sessions],
                "count": len(sessions),
            }
        )

    def _send_experiment_workflow_catalog(self) -> None:
        """Serve valid registry links for a new controlled experiment."""
        source = self._require_research_source()
        service = ExperimentWorkflowService(source.root())
        self._send_json(service.catalog())

    def _run_experiment_workflow(self, body: dict[str, object]) -> None:
        """Run bounded controller ticks and publish reproducible artifacts."""
        source = self._require_research_source()
        protocol = body.get("protocol")
        if protocol in {"science_suite_v1", "science_time_v1", "science_5d_v1"}:
            runtime_result = ExperimentWorkflowService(
                source.root(), self.dashboard_server.research_ai_backend
            ).run_science(body)
            self._send_json(cast(dict[str, JSONValue], {"ok": True, **runtime_result}))
            return
        if protocol == "stdp_pair_timing_v1":
            from src.research.stdp_pair_experiment import execute_stdp_pair_experiment

            protocol_result = execute_stdp_pair_experiment()
            self._send_json(cast(dict[str, JSONValue], {"ok": True, **protocol_result}))
            return
        if protocol not in {None, "runtime_ticks_v1"}:
            raise InvalidRequestError(f"Unknown experiment protocol: {protocol!r}")
        bridge = self._require_bridge()
        step = getattr(bridge.controller, "step", None)
        if not callable(step):
            raise BridgeNotConfiguredError(
                "Runtime controller does not support step()."
            )

        state = self.dashboard_server.dashboard_state

        def metrics() -> dict[str, int]:
            snapshot = state.snapshot().system
            return {
                "tick": snapshot.tick,
                "neurons": snapshot.neurons,
                "synapses": snapshot.synapses,
            }

        runtime_result = ExperimentWorkflowService(source.root()).run(
            body,
            step,
            metrics(),
            metrics,
        )
        runtime_result["ai_report"] = self._append_ai_report(
            cast(str, runtime_result["experiment_id"])
        )
        self._send_json(cast(dict[str, JSONValue], {"ok": True, **runtime_result}))

    def _append_ai_report(self, experiment_id: str) -> dict[str, JSONValue]:
        """Append an AIRR interpretation after a completed experiment.

        AIRR generation is post-hoc and therefore cannot influence the run. A
        missing or failing AI backend is reported without changing run status.
        """
        backend = self.dashboard_server.research_ai_backend
        if backend is None:
            return {"status": "unavailable", "reason": "AI backend not configured"}
        try:
            report = AIRRPipeline(self._require_research_source().root()).analyze(
                experiment_id, backend
            )
        except Exception as exc:
            return {
                "status": "failed",
                "error": type(exc).__name__,
                "message": str(exc),
            }
        return {
            "status": "generated",
            "report_id": report.report_id,
            "json": f"reports/{experiment_id}/{report.report_id}.json",
            "markdown": f"reports/{experiment_id}/{report.report_id}.md",
            "human_review": "PENDING",
            "scientific_evidence": False,
        }

    def _set_experiment_mode(
        self,
        body: dict[str, object],
    ) -> None:
        """Set the current experiment mode."""
        mode = self._string_field(body, "mode")
        if mode not in {"operator", "experiment", "debug"}:
            self._send_json(
                {"error": f"Invalid experiment mode: {mode!r}"},
                HTTPStatus.BAD_REQUEST,
            )
            return

        state = self.dashboard_server.dashboard_state
        state.set_experiment_mode(mode)

        self._send_json(
            {
                "ok": True,
                "message": f"Experiment mode set to '{mode}'",
                "mode": mode,
            }
        )

    def _start_experiment_session(
        self,
        body: dict[str, object],
    ) -> None:
        """Start a new experiment or debug session."""
        mode = self._string_field(body, "mode")
        if mode not in {"operator", "experiment", "debug"}:
            self._send_json(
                {"error": f"Invalid experiment mode: {mode!r}"},
                HTTPStatus.BAD_REQUEST,
            )
            return

        session_id = self._string_field(body, "session_id")
        hypothesis = str(body.get("hypothesis", ""))
        note = str(body.get("note", ""))

        state = self.dashboard_server.dashboard_state
        snapshot = state.snapshot()
        start_tick = snapshot.system.tick

        # Capture a lightweight config snapshot from current parameters.
        config_snapshot: dict[str, JSONValue] = {}
        for name, param in (snapshot.parameters or {}).items():
            config_snapshot[name] = param.value

        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        notes: tuple[str, ...] = ()
        if note:
            notes = (f"[{now}] {note}",)

        session = ExperimentSession(
            session_id=session_id,
            mode=mode,
            hypothesis=hypothesis,
            notes=notes,
            start_tick=start_tick,
            start_time=now,
            config_snapshot=config_snapshot,
            active=True,
        )
        state.start_experiment_session(session)

        self._send_json(
            {
                "ok": True,
                "message": f"Started {mode} session '{session_id}'",
                "session": session.to_json(),
            }
        )

    def _stop_experiment_session(
        self,
        body: dict[str, object],
    ) -> None:
        """Stop the active experiment/debug session."""
        state = self.dashboard_server.dashboard_state
        snapshot = state.snapshot()
        end_tick = int(cast(Any, body.get("end_tick", snapshot.system.tick)))
        state.stop_experiment_session(end_tick=end_tick)

        self._send_json(
            {
                "ok": True,
                "message": "Experiment session stopped",
                "end_tick": end_tick,
            }
        )

    def _add_experiment_note(
        self,
        body: dict[str, object],
    ) -> None:
        """Add a note to the active experiment session."""
        note = body.get("note")
        if note is None or str(note).strip() == "":
            self._send_json(
                {"error": "Missing or empty 'note' field"},
                HTTPStatus.BAD_REQUEST,
            )
            return

        state = self.dashboard_server.dashboard_state
        state.add_experiment_note(str(note).strip())

        self._send_json(
            {
                "ok": True,
                "message": "Note added to active session",
            }
        )

    def _send_pending_parameters(self) -> None:
        """Serve all pending parameter changes."""
        snapshot = self.dashboard_server.dashboard_state.snapshot()
        pending = snapshot.pending_changes or {}
        self._send_json(
            {
                "pending": {k: v.to_json() for k, v in pending.items()},
                "count": len(pending),
                "history": [r.to_json() for r in snapshot.change_history],
            }
        )

    def _set_pending_parameter(
        self,
        name: str,
        body: dict[str, object],
    ) -> None:
        """Record a proposed value for a parameter without applying it."""
        state = self.dashboard_server.dashboard_state
        snapshot = state.snapshot()
        parameter = (snapshot.parameters or {}).get(name)
        if parameter is None:
            self._send_json(
                {"error": f"Parameter '{name}' not found"},
                HTTPStatus.NOT_FOUND,
            )
            return

        proposed = body.get("value")
        if proposed is None:
            self._send_json(
                {"error": "Missing 'value' field"},
                HTTPStatus.BAD_REQUEST,
            )
            return

        # Coerce numeric strings back to numbers when the schema expects it.
        coerced = self._coerce_parameter_value(parameter, proposed)

        change = PendingParameterChange(
            name=name,
            current_value=parameter.value,
            proposed_value=coerced,
            default_value=parameter.default,
            timestamp=datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
            requires_restart=parameter.requires_restart,
            scientific_sensitive=parameter.scientific_sensitive,
        )
        state.set_pending_change(change)

        self._send_json(
            {
                "ok": True,
                "message": f"Pending change recorded for '{name}'",
                "pending": change.to_json(),
            }
        )

    def _apply_pending_parameters(
        self,
        body: dict[str, object],
        save_profile: bool = False,
    ) -> None:
        """Apply selected or all pending parameter changes.

        Args:
            body: Request body. May contain ``names`` to apply a subset.
            save_profile: Whether this application should also persist a profile.
        """
        state = self.dashboard_server.dashboard_state
        snapshot = state.snapshot()
        pending = dict(snapshot.pending_changes or {})

        requested_names = body.get("names")
        if requested_names is None:
            names = list(pending.keys())
        elif isinstance(requested_names, list):
            names = [str(n) for n in cast(list[object], requested_names)]
        else:
            self._send_json(
                {"error": "'names' must be a list or omitted"},
                HTTPStatus.BAD_REQUEST,
            )
            return

        if not names:
            self._send_json(
                {
                    "ok": True,
                    "message": "No pending changes to apply",
                    "applied": [],
                }
            )
            return

        applied: list[str] = []
        failed: list[str] = []
        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()

        for name in names:
            change = pending.pop(name, None)
            if change is None:
                failed.append(name)
                continue

            parameter = (snapshot.parameters or {}).get(name)
            if parameter is None:
                failed.append(name)
                continue

            old_value = parameter.value
            new_parameter = ParameterSchema(
                name=parameter.name,
                value=change.proposed_value,
                default=parameter.default,
                min=parameter.min,
                max=parameter.max,
                unit=parameter.unit,
                description=parameter.description,
                source="operator" if not save_profile else "profile",
                runtime_mutable=parameter.runtime_mutable,
                requires_restart=parameter.requires_restart,
                scientific_sensitive=parameter.scientific_sensitive,
            )
            state.update_parameter(new_parameter)

            record = ParameterChangeRecord(
                name=name,
                action="applied",
                old_value=old_value,
                new_value=change.proposed_value,
                timestamp=now,
                saved_profile=save_profile,
            )
            state.append_change_history(record)
            applied.append(name)

        state.update(pending_changes=pending)

        self._send_json(
            cast(
                dict[str, Any],
                {
                    "ok": True,
                    "message": f"Applied {len(applied)} parameter(s)",
                    "applied": applied,
                    "failed": failed,
                    "saved_profile": save_profile,
                },
            )
        )

    def _cancel_pending_parameters(
        self,
        body: dict[str, object],
    ) -> None:
        """Cancel selected or all pending parameter changes."""
        state = self.dashboard_server.dashboard_state
        snapshot = state.snapshot()
        pending = dict(snapshot.pending_changes or {})

        requested_names = body.get("names")
        if requested_names is None:
            names = list(pending.keys())
        elif isinstance(requested_names, list):
            names = [str(n) for n in cast(list[object], requested_names)]
        else:
            self._send_json(
                {"error": "'names' must be a list or omitted"},
                HTTPStatus.BAD_REQUEST,
            )
            return

        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        cancelled: list[str] = []

        for name in names:
            change = pending.pop(name, None)
            if change is not None:
                record = ParameterChangeRecord(
                    name=name,
                    action="cancelled",
                    old_value=change.current_value,
                    new_value=None,
                    timestamp=now,
                    saved_profile=False,
                )
                state.append_change_history(record)
                cancelled.append(name)

        state.update(pending_changes=pending)

        self._send_json(
            cast(
                dict[str, Any],
                {
                    "ok": True,
                    "message": f"Cancelled {len(cancelled)} pending change(s)",
                    "cancelled": cancelled,
                },
            )
        )

    def _coerce_parameter_value(
        self,
        parameter: ParameterSchema,
        value: object,
    ) -> JSONScalar | list[JSONValue] | dict[str, JSONValue]:
        """Coerce a proposed value towards the parameter's expected type."""
        if isinstance(value, (list, dict)):
            return cast("JSONScalar | list[JSONValue] | dict[str, JSONValue]", value)

        current = parameter.value
        if isinstance(current, bool):
            if isinstance(value, str):
                return value.lower() in {"true", "1", "yes", "on"}
            return bool(value)
        if isinstance(current, (int, float)):
            try:
                if isinstance(current, int):
                    return int(cast("Any", value))
                return float(cast("Any", value))
            except (TypeError, ValueError):
                return cast(
                    "JSONScalar | list[JSONValue] | dict[str, JSONValue]", value
                )
        if isinstance(current, str):
            return str(value)
        return cast("JSONScalar | list[JSONValue] | dict[str, JSONValue]", value)

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

    def _read_json_body(self, max_size: int = _MAX_BODY_SIZE) -> dict[str, Any]:
        """Read and parse a JSON request body."""
        content_length = self.headers.get("Content-Length")
        if content_length is None:
            raise ValueError("Missing Content-Length header")

        length = int(content_length)
        if length > max_size:
            raise ValueError(f"Request body too large: {length} bytes")

        raw = self.rfile.read(length)
        if len(raw) != length:
            raise ValueError("Incomplete request body")

        return cast(dict[str, Any], json.loads(raw.decode("utf-8")))

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

        try:
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
        except (
            BrokenPipeError,
            ConnectionResetError,
            ConnectionAbortedError,
        ):
            pass

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

        # Client disconnect – socket is dead, do not attempt any write.
        if isinstance(
            exc,
            (
                BrokenPipeError,
                ConnectionResetError,
                ConnectionAbortedError,
            ),
        ):
            return

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
    chat_settings: Mapping[str, Any] | None = None,
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

    chat_backend: ChatBackend | None = None
    configured_chat = chat_settings or {}
    chat_model = os.environ.get(
        "BRAIN5D_CHAT_MODEL", str(configured_chat.get("model", ""))
    ).strip()
    context_chars = int(
        os.environ.get(
            "BRAIN5D_CHAT_CONTEXT_CHARS",
            str(configured_chat.get("max_context_chars", 24_000)),
        )
    )
    web_search_enabled = os.environ.get(
        "BRAIN5D_CHAT_WEB_SEARCH",
        str(configured_chat.get("web_search_enabled", False)),
    ).lower() in {"1", "true", "yes", "on"}
    system_prompt = os.environ.get(
        "BRAIN5D_CHAT_SYSTEM_PROMPT", str(configured_chat.get("system_prompt", ""))
    ).strip()
    top_p = float(
        os.environ.get("BRAIN5D_CHAT_TOP_P", str(configured_chat.get("top_p", 0.9)))
    )
    max_tokens = int(
        os.environ.get(
            "BRAIN5D_CHAT_MAX_TOKENS", str(configured_chat.get("max_tokens", 2048))
        )
    )
    handoff_prompt = os.environ.get(
        "BRAIN5D_CHAT_HANDOFF_PROMPT", str(configured_chat.get("handoff_prompt", ""))
    ).strip()
    vision_enabled = os.environ.get(
        "BRAIN5D_CHAT_VISION", str(configured_chat.get("vision_enabled", False))
    ).lower() in {"1", "true", "yes", "on"}
    tools_enabled = os.environ.get(
        "BRAIN5D_CHAT_TOOLS", str(configured_chat.get("tools_enabled", False))
    ).lower() in {"1", "true", "yes", "on"}
    ollama_backend: OllamaBackend | None = None
    resolved_chat_settings: dict[str, JSONValue] = {}
    if chat_model:
        chat_endpoint = os.environ.get(
            "BRAIN5D_CHAT_ENDPOINT",
            str(configured_chat.get("endpoint", "http://127.0.0.1:11434/api/generate")),
        ).strip()
        temperature = float(
            os.environ.get(
                "BRAIN5D_CHAT_TEMPERATURE",
                str(configured_chat.get("temperature", 0.0)),
            )
        )
        ollama_backend = OllamaBackend(
            chat_model, chat_endpoint, temperature, top_p, max_tokens
        )
        chat_backend = chat_backend_from_text_backend(ollama_backend.generate_text)
        resolved_chat_settings = {
            "provider": "ollama",
            "model": chat_model,
            "endpoint": chat_endpoint,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "max_context_chars": context_chars,
            "read_only": True,
            "web_search_enabled": web_search_enabled,
            "system_prompt": system_prompt,
            "handoff_prompt": handoff_prompt,
            "vision_enabled": vision_enabled,
            "tools_enabled": tools_enabled,
        }
        print(f"🤖 Research chat backend: Ollama ({chat_model})")

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
        server.research_chat_backend = chat_backend
        server.research_ai_backend = cast(AnalysisBackend | None, ollama_backend)
        server.research_chat_context_chars = context_chars
        server.research_chat_system_prompt = system_prompt
        server.research_chat_handoff_prompt = handoff_prompt
        server.research_chat_vision_enabled = vision_enabled
        server.research_chat_tools_enabled = tools_enabled
        server.research_chat_ollama_backend = ollama_backend
        server.research_chat_settings = cast(
            dict[str, JSONValue],
            (
                {
                    **resolved_chat_settings,
                    "web_search_enabled": web_search_enabled,
                }
                if chat_model
                else {**configured_chat, "web_search_enabled": web_search_enabled}
            ),
        )
        server.research_chat_web_search_enabled = web_search_enabled
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
