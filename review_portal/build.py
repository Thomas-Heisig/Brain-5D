"""Build the static catalogue, or verify the checked-in artifact with --check."""
from __future__ import annotations

import argparse
from pathlib import Path

from .catalogue import javascript


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    target = Path(__file__).resolve().parents[1] / "src/dashboard/static/review/instrument.js"
    expected = javascript()
    if args.check:
        if target.read_text(encoding="utf-8") != expected:
            raise SystemExit("Catalogue drift: run python -m review_portal.build")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(expected, encoding="utf-8")


if __name__ == "__main__":
    main()
