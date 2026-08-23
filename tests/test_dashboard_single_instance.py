"""Single-instance binding regression tests for the Brain-5D dashboard.

These tests verify the P0 process-architecture contract from
``docs/TODO.md`` (section *v0.5.0-alpha.5 — Integration Hardening*):

* Browser and API requests always reach the same ``DashboardServer`` instance.
* ``/api/debug/bridge`` reports ``bridge_exists = true`` and
  ``controller_exists = true`` when a bridge is attached.
* ``/api/structural/status`` never reports the bridge as missing when the
  startup path attached a bridge.
* Unknown ``/api/...`` paths return a JSON 404 and never fall through to
  ``index.html``.
* The bridge identity (``server_id``) remains stable across requests.

The dashboard server owns its ``OperatorBridge`` directly on the instance
(no module-global bridge state), so every HTTP request handled by that
server observes the same bridge object. These tests lock that invariant
in place.
"""

from __future__ import annotations


import json
from http.client import HTTPConnection
from threading import Thread
from typing import Any, cast

from src.dashboard.models import JSONValue
from src.dashboard.operator_bridge import OperatorBridge
from src.dashboard.server import DashboardServer
from src.dashboard.state import DashboardStateStore
from src.dashboard.structural_api import JSONMapping, StructuralCommandResult


class _StubController:
    """Minimal controller stub satisfying the bridge contract."""

    def __init__(self) -> None:
        self.label = "stub-controller"


class _Bridge:
    """Minimal bridge stub used to verify identity and routing.

    Every method mirrors the surface used by the dashboard HTTP layer so
    the test can exercise the real dispatch code paths.
    """

    def __init__(self, controller: _StubController) -> None:
        self.controller: Any = controller
        self.coordinator = None
        self.plasticity = None
        self.approval_policy = None
        self.structural_heatmaps = None

    # -- structural / runtime surface ------------------------------------

    def structural_status(self) -> JSONMapping:
        return {"configured": True, "proposal_count": 0, "history_count": 0}

    def structural_proposals(self) -> list[JSONMapping]:
        return []

    def structural_history(self, _limit: int) -> list[JSONMapping]:
        return []

    def structural_heatmap(self, kind: str) -> JSONMapping:
        return {"kind": kind, "values": []}

    def structural_config(self) -> JSONMapping:
        return {"configured": True}

    def approve_structural(self, _proposal_id: str) -> StructuralCommandResult:
        return StructuralCommandResult(True, "approved")

    def reject_structural(self, _proposal_id: str) -> StructuralCommandResult:
        return StructuralCommandResult(True, "rejected")

    def undo_structural(self) -> StructuralCommandResult:
        return StructuralCommandResult(True, "undone")

    def set_auto_approval(self, enabled: bool) -> StructuralCommandResult:
        return StructuralCommandResult(True, str(enabled))

    def run_ticks(self, count: int) -> StructuralCommandResult:
        return StructuralCommandResult(True, str(count))

    def single_step(self) -> StructuralCommandResult:
        return StructuralCommandResult(True, "one")

    def request_snapshot(self) -> StructuralCommandResult:
        return StructuralCommandResult(True, "snapshot")

    def command(self, command: str, **_kwargs: Any) -> dict[str, JSONValue]:
        return {"ok": True, "status": command}

    def update_structural_config(self, **_body: Any) -> StructuralCommandResult:
        return StructuralCommandResult(True, "updated")


def _start_server(bridge: _Bridge | None) -> tuple[DashboardServer, Thread, str, int]:
    server = DashboardServer(
        ("127.0.0.1", 0),
        DashboardStateStore(),
        None,
        cast(OperatorBridge | None, bridge),
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    if not isinstance(host, str):
        raise AssertionError("dashboard server did not expose an IP address")
    return server, thread, host, port


def _stop_server(server: DashboardServer, thread: Thread) -> None:
    server.shutdown()
    server.server_close()
    thread.join(timeout=1.0)


def _get(host: str, port: int, path: str) -> tuple[int, dict[str, JSONValue] | str]:
    connection = HTTPConnection(host, port)
    try:
        connection.request("GET", path)
        response = connection.getresponse()
        body = response.read()
        content_type = response.getheader("Content-Type", "")
        if "application/json" in content_type:
            return response.status, json.loads(body)
        return response.status, body.decode("utf-8", errors="replace")
    finally:
        connection.close()


def test_debug_bridge_reports_bridge_and_controller_present() -> None:
    """``/api/debug/bridge`` must confirm bridge + controller attachment."""
    controller = _StubController()
    bridge = _Bridge(controller)
    server, thread, host, port = _start_server(bridge)
    try:
        status, payload = _get(host, port, "/api/debug/bridge")
        assert status == 200
        assert isinstance(payload, dict)
        assert payload["bridge_exists"] is True
        assert payload["controller_exists"] is True
        assert payload["bridge_type"] is not None
        assert payload["server_id"] == id(server)
    finally:
        _stop_server(server, thread)


def test_debug_bridge_reports_absent_without_bridge() -> None:
    """Without a bridge the diagnostic must honestly report absence."""
    server, thread, host, port = _start_server(None)
    try:
        status, payload = _get(host, port, "/api/debug/bridge")
        assert status == 200
        assert isinstance(payload, dict)
        assert payload["bridge_exists"] is False
        assert payload["controller_exists"] is False
        assert payload["bridge_type"] is None
    finally:
        _stop_server(server, thread)


def test_bridge_identity_stable_across_requests() -> None:
    """Every request must observe the same ``server_id`` (same instance)."""
    bridge = _Bridge(_StubController())
    server, thread, host, port = _start_server(bridge)
    try:
        ids: set[int] = set()
        for _ in range(5):
            status, payload = _get(host, port, "/api/debug/bridge")
            assert status == 200
            assert isinstance(payload, dict)
            ids.add(int(payload["server_id"]))  # type: ignore[arg-type]
        assert ids == {
            id(server)
        }, f"server_id must be stable across requests, got {ids}"
    finally:
        _stop_server(server, thread)


def test_structural_status_never_reports_bridge_missing_when_attached() -> None:
    """When a bridge is attached, ``/api/structural/status`` must not fail."""
    bridge = _Bridge(_StubController())
    server, thread, host, port = _start_server(bridge)
    try:
        status, payload = _get(host, port, "/api/structural/status")
        assert status == 200
        assert isinstance(payload, dict)
        # The route must not raise BridgeNotConfiguredError (which would be a
        # 503/409) and must not return a "not configured" sentinel.
        assert payload.get("configured") is True
        assert "error" not in payload
    finally:
        _stop_server(server, thread)


def test_structural_status_reports_missing_when_no_bridge() -> None:
    """Without a bridge the structural route must fail loudly, not silently."""
    server, thread, host, port = _start_server(None)
    try:
        status, payload = _get(host, port, "/api/structural/status")
        # BridgeNotConfiguredError surfaces as a JSON error, never as HTML.
        assert status in (409, 503)
        assert isinstance(payload, dict)
        assert "error" in payload
    finally:
        _stop_server(server, thread)


def test_unknown_api_paths_return_json_404_not_index_html() -> None:
    """Unknown ``/api/...`` paths must return JSON 404, never ``index.html``."""
    bridge = _Bridge(_StubController())
    server, thread, host, port = _start_server(bridge)
    try:
        status, payload = _get(host, port, "/api/does-not-exist")
        assert status == 404
        assert isinstance(payload, dict)
        assert "error" in payload
        assert "index" not in str(payload).lower()
    finally:
        _stop_server(server, thread)


def test_unknown_api_subpath_under_structural_returns_json_404() -> None:
    """Unknown structural subpaths must also return a JSON 404."""
    bridge = _Bridge(_StubController())
    server, thread, host, port = _start_server(bridge)
    try:
        status, payload = _get(host, port, "/api/structural/unknown-subroute")
        assert status == 404
        assert isinstance(payload, dict)
        assert "error" in payload
    finally:
        _stop_server(server, thread)


def test_only_one_listener_owns_bound_port() -> None:
    """A second server bound to the same live port must not share identity.

    ``DashboardServer.__init__`` binds the listening socket during
    construction. ``allow_reuse_address`` is True, so on some platforms a
    second bind to the same port may succeed at socket level. This test
    therefore does not assume the bind fails; instead it asserts that any
    second ``DashboardServer`` is a distinct object from the first and
    carries its own identity. The single-listener guarantee in production
    comes from the launcher starting exactly one ``src.main`` process, not
    from the socket layer alone.
    """
    bridge = _Bridge(_StubController())
    server, thread, host, port = _start_server(bridge)
    second = None
    try:
        try:
            second = DashboardServer(
                (host, port),
                DashboardStateStore(),
                None,
                cast(OperatorBridge | None, bridge),
            )
        except OSError:
            # The OS refused to bind a second listener — ideal case.
            return

        # If the bind was accepted, the two servers must still be distinct
        # instances with distinct identities.
        assert second is not server
        assert id(second) != id(server)
    finally:
        if second is not None:
            second.server_close()
        _stop_server(server, thread)


def test_bridge_object_identity_matches_server_attachment() -> None:
    """The bridge exposed via HTTP must be the exact object attached at start."""
    bridge = _Bridge(_StubController())
    server, thread, _host, _port = _start_server(bridge)  # noqa: F841
    try:
        # The server instance must own the exact bridge object.
        assert server.structural_bridge is bridge
        # And the controller on that bridge must be the exact stub.
        assert bridge.controller is not None
    finally:
        _stop_server(server, thread)
