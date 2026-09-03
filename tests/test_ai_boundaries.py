"""Structural tests for the scientific AI import boundary."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).parents[1]
AI_PACKAGES = (ROOT / "src" / "research_assistant", ROOT / "src" / "language_organ")
FORBIDDEN_ROOTS = ("src.core", "src.main")


def _imported_modules(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            modules.append(node.module)
    return modules


def test_ai_packages_do_not_import_core_or_main_directly() -> None:
    violations: list[str] = []
    for package in AI_PACKAGES:
        for path in package.glob("*.py"):
            for module in _imported_modules(path):
                if module == "src.core" or module.startswith("src.core.") or module == "src.main":
                    violations.append(f"{path.relative_to(ROOT)} imports {module}")

    assert violations == [], "AI boundary import violations: " + "; ".join(violations)
