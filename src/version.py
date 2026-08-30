"""Canonical Brain-5D version source.

All version strings in the project should derive from this single source.
Use ``BRAIN5D_VERSION`` for the PEP-440 compatible version string and
``BRAIN5D_VERSION_DISPLAY`` for human-readable display.

Usage:
    >>> from src.version import BRAIN5D_VERSION, BRAIN5D_VERSION_DISPLAY
    >>> print(BRAIN5D_VERSION)
    0.5.0a5
    >>> print(BRAIN5D_VERSION_DISPLAY)
    0.5.0-alpha.5
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

# ============================================================================
# Canonical version — single source of truth
# ============================================================================
# The authoritative version is in pyproject.toml. At runtime we attempt to
# read it from the installed package metadata. If the package is not
# installed (e.g. running from source), we fall back to a hardcoded value
# that MUST match pyproject.toml.

# The authoritative version is in pyproject.toml. We attempt to read it
# from the installed package metadata, but fall back to pyproject.toml
# directly if the package is not installed or the version is stale.
_pyproject_version: str | None = None
try:
    import re as _re
    from pathlib import Path as _Path
    _src_dir = _Path(__file__).resolve().parent
    _project_root = _src_dir.parent
    _pyproject_path = _project_root / "pyproject.toml"
    if _pyproject_path.exists():
        _text = _pyproject_path.read_text(encoding="utf-8")
        _match = _re.search(r'^version\s*=\s*"([^"]+)"', _text, _re.MULTILINE)
        if _match:
            _pyproject_version = _match.group(1)
except Exception:
    pass

try:
    _pkg_version_str: str = _pkg_version("brain5d-core")
    # If the installed version is older than the pyproject.toml version,
    # prefer pyproject.toml (likely running from source with stale install)
    if _pyproject_version is not None and _pkg_version_str != _pyproject_version:
        _pkg_version_str = _pyproject_version
except PackageNotFoundError:
    _pkg_version_str = _pyproject_version or "0.5.0a5"

BRAIN5D_VERSION: str = _pkg_version_str
"""PEP-440 compatible version string (e.g. '0.5.0a5')."""

# Normalize for human-readable display
# PEP-440: 0.5.0a5 -> 0.5.0-alpha.5
_BASE = BRAIN5D_VERSION
if "a" in _BASE:
    _parts = _BASE.split("a", 1)
    _display: str = f"{_parts[0]}-alpha.{_parts[1]}"
elif "b" in _BASE:
    _parts = _BASE.split("b", 1)
    _display = f"{_parts[0]}-beta.{_parts[1]}"
else:
    _display = _BASE

BRAIN5D_VERSION_DISPLAY: str = _display
"""Human-readable version string (e.g. '0.5.0-alpha.5')."""
