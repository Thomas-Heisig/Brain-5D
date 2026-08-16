"""HTTP glue for the dashboard control service.

Kept separate from ``server.py`` so the control plane can be tested without opening
sockets and so JSON validation remains centralized.
"""

from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler

from src.dashboard.models import JSONValue

from .control_service import DashboardControlService

_MAX_CONTROL_BODY_BYTES = 16 * 1024


def read_json_body(handler: BaseHTTPRequestHandler) -> object:
    """Read one bounded JSON request body."""
    raw_length = handler.headers.get("Content-Length")
    if raw_length is None:
        raise ValueError("Content-Length header is required.")
    try:
        length = int(raw_length)
    except ValueError as exc:
        raise ValueError("Invalid Content-Length header.") from exc
    if length < 0 or length > _MAX_CONTROL_BODY_BYTES:
        raise ValueError("Control request body is too large.")
    raw = handler.rfile.read(length)
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid UTF-8 JSON request body.") from exc


def execute_control_request(
    handler: BaseHTTPRequestHandler,
    service: DashboardControlService,
) -> tuple[HTTPStatus, dict[str, JSONValue]]:
    """Read, validate and execute a control request."""
    try:
        body = read_json_body(handler)
    except ValueError as exc:
        return HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)}
    response = service.execute(body)
    return HTTPStatus(response.status), response.payload
