#!/usr/bin/env python3
"""Verify the delivered package against SHA256SUMS.txt (standard library only)."""
from __future__ import annotations
import hashlib
import sys
from pathlib import Path

def main() -> int:
    root = Path(__file__).resolve().parent
    try:
        lines = (root / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
        failures = []
        checked = 0
        for line in lines:
            if not line.strip():
                continue
            expected, name = line.split("  ", 1)
            target = (root / name).resolve()
            if root not in target.parents:
                raise ValueError("Path outside package: " + name)
            if not target.is_file():
                failures.append("MISSING " + name)
                continue
            digest = hashlib.sha256()
            with target.open("rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(block)
            checked += 1
            if digest.hexdigest() != expected:
                failures.append("CHANGED " + name)
        for failure in failures:
            print(failure)
        print(f"Checked {checked} files; failures: {len(failures)}")
        return 1 if failures else 0
    except (OSError, UnicodeError, ValueError) as exc:
        print("Verification error: " + str(exc), file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
