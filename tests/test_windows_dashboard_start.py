from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_windows_start_wrappers_default_to_trusted_lan_binding() -> None:
    cmd = (ROOT / "start.cmd").read_text(encoding="utf-8")
    powershell = (ROOT / "start.ps1").read_text(encoding="utf-8")

    assert "--host 0.0.0.0" in cmd
    assert '[string]$DashboardHost = "0.0.0.0"' in powershell


def test_direct_python_entrypoint_remains_loopback_by_default() -> None:
    main = (ROOT / "src" / "main.py").read_text(encoding="utf-8")

    assert 'default="127.0.0.1"' in main
    assert "use 0.0.0.0 for LAN" in main
