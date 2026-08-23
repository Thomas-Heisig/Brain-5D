"""Final fix: ensure pytestmark is always AFTER __future__ and docstring."""

from __future__ import annotations

import re
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent.parent / "tests"


def _find_docstring_end(lines: list[str]) -> int:
    """Find the line index where the module-level docstring ends."""
    in_docstring = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            if not in_docstring:
                in_docstring = True
                # Check if it's a one-liner
                if stripped.count('"""') == 2 or stripped.count("'''") == 2:
                    return i + 1
            else:
                return i + 1
    return 0


def _find_last_import(lines: list[str]) -> int:
    """Find the line index of the last import statement."""
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
    return last_import


def main() -> None:
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

        # Remove pytestmark and import pytest from current position
        pm_line = lines.pop(pm_idx)

        # Also remove import pytest if it was before the docstring
        new_lines = []
        for line in lines:
            if line.strip() == "import pytest":
                continue
            new_lines.append(line)
        lines = new_lines

        # Find the correct insert position (after all imports)
        docstring_end = _find_docstring_end(lines)
        last_import = _find_last_import(lines)
        insert_pos = max(docstring_end, last_import + 1)

        # Fix the marker line syntax
        stripped = pm_line.strip()
        m = re.match(r"pytestmark\s*=\s*(.*)", stripped)
        if m:
            rhs = m.group(1).strip()
            parts = [p.strip() for p in rhs.split(",") if p.strip()]
            if len(parts) > 1 and not rhs.startswith("[") and not rhs.startswith("("):
                indent = " " * 4
                items = "\n" + "\n".join(f"{indent}{p}," for p in parts)
                pm_line = f"pytestmark = [{items}\n]"

        # Check if pytest needs to be imported
        has_pytest = any(
            "import pytest" in line or "from pytest" in line
            for line in lines
        )
        if not has_pytest:
            lines.insert(insert_pos, "import pytest")
            insert_pos += 1

        lines.insert(insert_pos, pm_line)

        f.write_text("\n".join(lines), encoding="utf-8")
        print(f"  {f.name}: fixed")

    print("Done!")


if __name__ == "__main__":
    main()
