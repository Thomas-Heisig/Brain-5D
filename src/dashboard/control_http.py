"""HTTP glue for the dashboard control service.

This module provides HTTP integration for the control service, keeping the
control plane separate from the main server implementation. This separation
allows the control logic to be tested without opening sockets and keeps
JSON validation centralized.

The module provides:
1. Safe JSON body reading with size limits
2. Control request execution with proper HTTP status codes
3. Error handling and logging
4. Content-Type validation for JSON requests
"""

from __future__ import annotations

import json
import logging
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler

from src.dashboard.models import JSONValue

from .control_service import DashboardControlService

logger = logging.getLogger(__name__)

# Maximum request body size for control endpoints (16KB)
_MAX_CONTROL_BODY_BYTES = 16 * 1024

# Allowed Content-Types for control requests
_ALLOWED_CONTENT_TYPES = {"application/json", "application/json; charset=utf-8"}

# HTTP 413 Payload Too Large (not available in all Python versions)
_HTTP_413_PAYLOAD_TOO_LARGE = 413


# ============================================================================
# Custom Exceptions
# ============================================================================


class ControlHTTPError(Exception):
    """Base exception for HTTP control layer errors."""

    def __init__(self, message: str, status: int = HTTPStatus.BAD_REQUEST) -> None:
        self.message = message
        self.status = status
        super().__init__(message)


class ContentTypeError(ControlHTTPError):
    """Raised when the Content-Type header is invalid."""

    def __init__(self, message: str = "Content-Type must be application/json") -> None:
        super().__init__(message, HTTPStatus.UNSUPPORTED_MEDIA_TYPE)


class BodyTooLargeError(ControlHTTPError):
    """Raised when the request body exceeds the size limit."""

    def __init__(self, max_size: int = _MAX_CONTROL_BODY_BYTES) -> None:
        super().__init__(
            f"Control request body too large (max {max_size} bytes)",
            _HTTP_413_PAYLOAD_TOO_LARGE,
        )


# ============================================================================
# JSON Body Reader
# ============================================================================


def read_json_body(handler: BaseHTTPRequestHandler) -> object:
    """Read one bounded JSON request body.

    This function handles all the HTTP-specific details of reading and parsing
    a JSON request body, including size limits and content-type validation.

    Args:
        handler: The HTTP request handler instance.

    Returns:
        The parsed JSON object (typically a dict or list).

    Raises:
        ContentTypeError: If the Content-Type header is invalid.
        BodyTooLargeError: If the request body exceeds the size limit.
        ValueError: If the Content-Length header is missing or invalid,
            or if the body is not valid JSON.
    """
    # Validate Content-Type
    content_type = handler.headers.get("Content-Type", "")
    if not content_type or content_type not in _ALLOWED_CONTENT_TYPES:
        if content_type and content_type.startswith("application/json"):
            # Allow slight variations (e.g., with charset)
            pass
        else:
            raise ContentTypeError(f"Invalid Content-Type: {content_type}")

    # Get and validate Content-Length
    raw_length = handler.headers.get("Content-Length")
    if raw_length is None:
        raise ValueError("Content-Length header is required.")

    try:
        length = int(raw_length)
    except ValueError as exc:
        raise ValueError("Invalid Content-Length header.") from exc

    if length < 0:
        raise ValueError("Content-Length cannot be negative.")

    if length > _MAX_CONTROL_BODY_BYTES:
        raise BodyTooLargeError()

    # Read and parse the body
    raw = handler.rfile.read(length)

    if not raw:
        return {}

    try:
        return json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise ValueError("Request body is not valid UTF-8.") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON request body: {exc.msg}") from exc


def safe_read_json_body(
    handler: BaseHTTPRequestHandler,
) -> tuple[object | None, str | None]:
    """Read a JSON body with safe error handling.

    This is a convenience wrapper that catches all exceptions and returns
    a tuple of (body, error_message) instead of raising.

    Args:
        handler: The HTTP request handler instance.

    Returns:
        A tuple of (parsed_body, error_message). If successful, error_message is None.
        If an error occurs, parsed_body is None and error_message contains the error.
    """
    try:
        return read_json_body(handler), None
    except ContentTypeError as e:
        return None, e.message
    except BodyTooLargeError as e:
        return None, e.message
    except ValueError as e:
        return None, str(e)
    except Exception as e:
        logger.warning(f"Unexpected error reading JSON body: {e}")
        return None, f"Internal error reading request body: {e}"


# ============================================================================
# Control Request Executor
# ============================================================================


def execute_control_request(
    handler: BaseHTTPRequestHandler,
    service: DashboardControlService,
) -> tuple[int, dict[str, JSONValue]]:
    """Read, validate and execute a control request.

    This function handles the complete request lifecycle:
    1. Read the JSON body
    2. Execute the control command via the service
    3. Return the appropriate HTTP status and response body

    Args:
        handler: The HTTP request handler instance.
        service: The control service instance.

    Returns:
        A tuple of (HTTP_status_code, response_body_dict).

    Example:
        >>> status, body = execute_control_request(handler, service)
        >>> handler.send_response(status)
        >>> handler.send_header("Content-Type", "application/json")
        >>> handler.end_headers()
        >>> handler.wfile.write(json.dumps(body).encode())
    """
    try:
        body = read_json_body(handler)
    except ContentTypeError as e:
        return e.status, {"ok": False, "error": e.message}
    except BodyTooLargeError as e:
        return e.status, {"ok": False, "error": e.message}
    except ValueError as e:
        return HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(e)}
    except Exception as e:
        logger.warning(f"Unexpected error reading control request: {e}")
        return HTTPStatus.INTERNAL_SERVER_ERROR, {
            "ok": False,
            "error": "Internal server error",
        }

    # Execute the command
    try:
        response = service.execute(body)
        return response.status, response.payload
    except Exception as e:
        logger.error(f"Control execution failed: {e}")
        return HTTPStatus.INTERNAL_SERVER_ERROR, {
            "ok": False,
            "error": "Internal server error",
        }


def execute_control_request_with_logging(
    handler: BaseHTTPRequestHandler,
    service: DashboardControlService,
    log_prefix: str = "Control request",
) -> tuple[int, dict[str, JSONValue]]:
    """Execute a control request with logging.

    This is a convenience wrapper that logs the request and response details.

    Args:
        handler: The HTTP request handler instance.
        service: The control service instance.
        log_prefix: Prefix for log messages.

    Returns:
        A tuple of (HTTP_status_code, response_body_dict).
    """
    # Log the request
    method = handler.command
    path = handler.path
    logger.info(f"{log_prefix}: {method} {path}")

    status, body = execute_control_request(handler, service)

    # Log the response
    ok = body.get("ok", False)
    logger.debug(f"{log_prefix} response: status={status}, ok={ok}")

    return status, body


# ============================================================================
# Integration with server.py
# ============================================================================


def handle_control_post(
    handler: BaseHTTPRequestHandler,
    service: DashboardControlService,
) -> None:
    """Handle a POST request to the control endpoint.

    This function reads the request body, executes the command, and sends
    the response directly to the client.

    Args:
        handler: The HTTP request handler instance.
        service: The control service instance.
    """
    status, body = execute_control_request(handler, service)

    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()

    encoded = json.dumps(body, separators=(",", ":")).encode("utf-8")
    handler.wfile.write(encoded)


def handle_control_get(
    handler: BaseHTTPRequestHandler,
    service: DashboardControlService,
) -> None:
    """Handle a GET request to the control endpoint (status).

    Args:
        handler: The HTTP request handler instance.
        service: The control service instance.
    """
    try:
        state = service.state()
        body: dict[str, JSONValue] = {"ok": True, "state": state}
        status = HTTPStatus.OK
    except AttributeError as e:
        logger.error(f"Control status failed (AttributeError): {e}")
        body = {"ok": False, "error": f"Control status failed: {e}"}
        status = HTTPStatus.INTERNAL_SERVER_ERROR
    except Exception as e:
        logger.error(f"Control status failed: {e}")
        body = {"ok": False, "error": f"Failed to get control status: {e}"}
        status = HTTPStatus.INTERNAL_SERVER_ERROR

    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()

    encoded = json.dumps(body, separators=(",", ":")).encode("utf-8")
    handler.wfile.write(encoded)


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "read_json_body",
    "safe_read_json_body",
    "execute_control_request",
    "execute_control_request_with_logging",
    "handle_control_post",
    "handle_control_get",
    "ControlHTTPError",
    "ContentTypeError",
    "BodyTooLargeError",
    "_MAX_CONTROL_BODY_BYTES",
]
