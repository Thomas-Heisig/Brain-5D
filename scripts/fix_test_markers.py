"""Fix pytestmark placement — must be after imports, not before docstring."""

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

        # Check if it's in the right position (after imports)
        insert_pos = _find_insert_position(lines)

        if pm_idx < insert_pos:
            # Move pytestmark line to after imports
            pm_line = lines.pop(pm_idx)
            # Recalculate insert_pos (may have shifted)
            insert_pos = _find_insert_position(lines)
            lines.insert(insert_pos, pm_line)
            f.write_text("\n".join(lines), encoding="utf-8")
            print(f"  {f.name}: moved pytestmark to line {insert_pos + 1}")
            fixed += 1

    print(f"\nDone: {fixed} files fixed")


if __name__ == "__main__":
    main()
