"""Add 'import pytest' to test files that use pytestmark but don't import pytest."""

from __future__ import annotations

from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent.parent / "tests"


def main() -> None:
    modified = 0
    for f in sorted(TESTS_DIR.glob("test_*.py")):
        content = f.read_text(encoding="utf-8")
        if "pytestmark" in content and "import pytest" not in content:
            lines = content.split("\n")
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
            if last_import >= 0:
                lines.insert(last_import + 1, "import pytest")
                f.write_text("\n".join(lines), encoding="utf-8")
                print(f"  {f.name}: added import pytest")
                modified += 1
            else:
                print(f"  {f.name}: no imports found, skipped")

    print(f"\nDone: {modified} files modified")


if __name__ == "__main__":
    main()
