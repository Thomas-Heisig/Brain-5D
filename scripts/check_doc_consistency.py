"""Validate documentation links and canonical baseline claims."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"
ROADMAP_DOCS = (
    DOCS_ROOT / "08-roadmap" / "TODO.md",
    DOCS_ROOT / "08-roadmap" / "ROADMAP.md",
)
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
BASELINE_PATTERN = re.compile(r"\*\*Baseline:\*\*\s+`?brain5d-core\s+([^`\s]+)`?")
COLLECTED_PATTERN = re.compile(r"(\d+)\s+tests collected")


def markdown_files() -> tuple[Path, ...]:
    """Return tracked documentation files in stable order."""
    return tuple(sorted(DOCS_ROOT.rglob("*.md")))


def check_markdown_links(files: tuple[Path, ...], root: Path = REPO_ROOT) -> list[str]:
    """Return one error for every missing local Markdown link target."""
    root = root.resolve()
    errors: list[str] = []
    for source in files:
        source = source.resolve()
        text = source.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK.finditer(text):
            target = match.group(1).strip().strip("<>")
            target = target.split("#", 1)[0].strip()
            if not target or target.startswith(
                ("http://", "https://", "mailto:", "data:")
            ):
                continue
            candidate = (source.parent / unquote(target)).resolve()
            try:
                candidate.relative_to(root)
            except ValueError:
                errors.append(f"{source}: link escapes repository: {target}")
                continue
            if not candidate.exists():
                errors.append(f"{source}: missing link target: {target}")
    return errors


def check_baseline_version() -> list[str]:
    """Ensure the canonical roadmap baseline matches ``pyproject.toml``."""
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    version_match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject, re.MULTILINE)
    if version_match is None:
        return ["pyproject.toml: canonical project version is missing"]
    expected = version_match.group(1)
    errors: list[str] = []
    for path in ROADMAP_DOCS:
        text = path.read_text(encoding="utf-8")
        match = BASELINE_PATTERN.search(text)
        if match is None:
            errors.append(f"{path.relative_to(REPO_ROOT)}: baseline claim is missing")
        elif match.group(1) != expected:
            errors.append(
                f"{path.relative_to(REPO_ROOT)}: baseline {match.group(1)} "
                f"does not match {expected}"
            )
    return errors


def check_collected_test_count() -> list[str]:
    """Compare the documented collected-test count with pytest collection."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    output = f"{result.stdout}\n{result.stderr}"
    actual_match = COLLECTED_PATTERN.search(output)
    if actual_match is None:
        return ["pytest collection did not report a collected test count"]

    declared_text = (DOCS_ROOT / "08-roadmap" / "TODO.md").read_text(encoding="utf-8")
    declared_match = re.search(r"- \[x\] (\d+) tests collected", declared_text)
    if declared_match is None:
        return ["docs/08-roadmap/TODO.md: collected-test claim is missing"]
    if declared_match.group(1) != actual_match.group(1):
        return [
            "docs/08-roadmap/TODO.md: collected-test claim "
            f"{declared_match.group(1)} does not match pytest ({actual_match.group(1)})"
        ]
    return []


def main() -> int:
    """Run documentation checks and return a shell-friendly status code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-tests",
        action="store_true",
        help="also compare the documented test count with pytest collection",
    )
    args = parser.parse_args()

    errors = check_markdown_links(markdown_files())
    errors.extend(check_baseline_version())
    if args.check_tests:
        errors.extend(check_collected_test_count())

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Documentation consistency checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
