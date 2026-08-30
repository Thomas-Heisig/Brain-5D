"""Shared helpers for dashboard HTTP tests."""

from __future__ import annotations

import json
from http.client import HTTPConnection
from socketserver import BaseServer
from typing import Any, cast


def _server_address(server: BaseServer) -> tuple[str, int]:
    """Extract and cast the server address to typed host/port."""
    addr = cast(tuple[str, int], server.server_address)
    host, port = addr
    return host, port


def request_json(
    server: BaseServer,
    method: str,
    path: str,
    body: dict[str, Any] | None = None,
    timeout: float = 5,
) -> tuple[int, dict[str, Any]]:
    """Send a JSON request and return (status, parsed body)."""
    host, port = _server_address(server)
    conn = HTTPConnection(host, port, timeout=timeout)
    try:
        headers = {"Content-Type": "application/json"} if body is not None else {}
        data = json.dumps(body).encode() if body is not None else None
        conn.request(method, path, body=data, headers=headers)
        response = conn.getresponse()
        status = response.status
        raw = response.read()
        try:
            payload = json.loads(raw.decode())
        except json.JSONDecodeError:
            payload = {"raw": raw.decode(errors="replace")}
        return status, cast(dict[str, Any], payload)
    finally:
        conn.close()


def post_json(
    server: BaseServer,
    path: str,
    body: dict[str, Any],
) -> tuple[int, dict[str, Any] | str]:
    """Send a JSON POST request and return (status, parsed body or raw text)."""
    host, port = _server_address(server)
    conn = HTTPConnection(host, port)
    try:
        conn.request(
            "POST",
            path,
            json.dumps(body),
            {"Content-Type": "application/json"},
        )
        resp = conn.getresponse()
        data = resp.read()
        ct = resp.getheader("Content-Type", "")
        if "application/json" in ct:
            return resp.status, cast(dict[str, Any], json.loads(data))
        return resp.status, data.decode("utf-8", errors="replace")
    finally:
        conn.close()
