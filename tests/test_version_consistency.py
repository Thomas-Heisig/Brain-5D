"""Tests for Phase 21: Central version consistency.

Ensures the canonical version source is consistent across:
- pyproject.toml
- src/version.py
- Dashboard server version
- Snapshot metadata
"""

from __future__ import annotations

import re
from pathlib import Path

from src.version import BRAIN5D_VERSION, BRAIN5D_VERSION_DISPLAY


def _read_pyproject_version() -> str:
    """Extract version from pyproject.toml."""
    text = Path("pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if match:
        return match.group(1)
    raise AssertionError("version not found in pyproject.toml")


class TestVersionConsistency:
    """Version strings are consistent across the project."""

    def test_version_matches_pyproject(self) -> None:
        """BRAIN5D_VERSION matches pyproject.toml."""
        pyproject_version = _read_pyproject_version()
        assert BRAIN5D_VERSION == pyproject_version, (
            f"src/version.py has {BRAIN5D_VERSION!r} "
            f"but pyproject.toml has {pyproject_version!r}"
        )

    def test_display_format(self) -> None:
        """BRAIN5D_VERSION_DISPLAY is a valid alpha display string."""
        assert BRAIN5D_VERSION_DISPLAY.startswith("0.5.0-alpha.")
        # Should match pattern like 0.5.0-alpha.5
        assert re.match(r"^\d+\.\d+\.\d+-alpha\.\d+$", BRAIN5D_VERSION_DISPLAY)

    def test_dashboard_server_uses_central_version(self) -> None:
        """Dashboard server version is derived from central source."""
        from src.dashboard.server import DashboardRequestHandler

        assert BRAIN5D_VERSION_DISPLAY in DashboardRequestHandler.server_version

    def test_dashboard_defaults_use_central_version(self) -> None:
        """Dashboard package and empty snapshots use the canonical version."""
        from src.dashboard import __version__
        from src.dashboard.models import DashboardSnapshot

        assert __version__ == BRAIN5D_VERSION_DISPLAY
        assert DashboardSnapshot().version == BRAIN5D_VERSION_DISPLAY

    def test_main_py_uses_central_version(self) -> None:
        """main.py imports and uses BRAIN5D_VERSION_DISPLAY."""
        text = Path("src/main.py").read_text(encoding="utf-8")
        assert "from src.version import" in text
        assert "BRAIN5D_VERSION_DISPLAY" in text
