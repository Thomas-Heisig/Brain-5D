"""Fix pytestmark in all test files.

Ensures:
1. pytestmark is placed AFTER all imports (including __future__)
2. Multiple markers use proper syntax: pytestmark = [pytest.mark.a, pytest.mark.b]
"""

from __future__ import annotations

import re
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent.parent / "tests"


def _find_insert_position(lines: list[str]) -> int:
    """Find the line after the last import statement."""
    in_docstring = False
    last_import = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            in_docstring = not in_docstring
        if in_docstring:
            continue
        if stripped.startswith("import ") or stripped.startswith("from "):
            last_import = i
    return last_import + 1 if last_import >= 0 else 0


def _fix_pytestmark_line(line: str) -> str:
    """Fix pytestmark = pytest.mark.a, pytest.mark.b -> list syntax."""
    stripped = line.strip()
    if not stripped.startswith("pytestmark"):
        return line

    # Parse the right-hand side
    m = re.match(r"pytestmark\s*=\s*(.*)", stripped)
    if not m:
        return line

    rhs = m.group(1).strip()

    # Check if it already uses list syntax
    if rhs.startswith("[") or rhs.startswith("("):
        return line

    # Split by comma
    parts = [p.strip() for p in rhs.split(",") if p.strip()]
    if len(parts) == 1:
        # Single marker: pytestmark = pytest.mark.xxx
        indent = " " * (len(line) - len(line.lstrip()))
        return f"{indent}pytestmark = {parts[0]}"
    else:
        # Multiple markers: convert to list
        indent = " " * (len(line) - len(line.lstrip()))
        items = "\n" + "\n".join(f"{indent}    {p}," for p in parts)
        return f"{indent}pytestmark = [{items}\n{indent}]"


def main() -> None:
    fixed = 0
    for f in sorted(TESTS_DIR.glob("test_*.py")):
        content = f.read_text(encoding="utf-8")
        lines = content.split("\n")

        # Find pytestmark line
        pm_idx = None
        for i, line in enumerate(lines):
            if line.strip().startswith("pytestmark"):
                pm_idx = i
                break

        if pm_idx is None:
            continue

        # Fix the marker line syntax
        lines[pm_idx] = _fix_pytestmark_line(lines[pm_idx])

        # Move to after imports if needed
        insert_pos = _find_insert_position(lines)

        if pm_idx < insert_pos:
            pm_line = lines.pop(pm_idx)
            insert_pos = _find_insert_position(lines)
            lines.insert(insert_pos, pm_line)

        # Ensure import pytest exists
        has_pytest_import = any(
            line.strip() == "import pytest" for line in lines
        )
        if not has_pytest_import:
            # Check if pytest is imported via another import
            pytest_imported = any(
                "import pytest" in line or "from pytest" in line
                for line in lines
            )
            if not pytest_imported:
                insert_pos = _find_insert_position(lines)
                lines.insert(insert_pos, "import pytest")

        f.write_text("\n".join(lines), encoding="utf-8")
        fixed += 1

    print(f"Done: {fixed} files processed")


if __name__ == "__main__":
    main()
