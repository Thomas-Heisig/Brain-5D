"""Rebuild the dashboard HTML from component templates.

Usage:
    python scripts/rebuild_dashboard_html.py

This script regenerates the complete index.html for the Brain-5D operator
dashboard by composing all section templates.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_DIR = REPO_ROOT / "src" / "dashboard"
HTML_DIR = DASHBOARD_DIR / "html"
INDEX_PATH = DASHBOARD_DIR / "index.html"


def main() -> int:
    """Rebuild index.html from component templates."""
    if not HTML_DIR.is_dir():
        print(f"Error: HTML components directory not found: {HTML_DIR}", file=sys.stderr)
        return 1

    parts: list[str] = []
    for template in sorted(HTML_DIR.glob("*.html")):
        parts.append(template.read_text(encoding="utf-8"))

    INDEX_PATH.write_text("\n".join(parts), encoding="utf-8")
    print(f"Dashboard rebuilt: {INDEX_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())