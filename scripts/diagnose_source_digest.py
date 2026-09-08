"""Diagnose source-freeze digest mismatches on Windows and Linux."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import cast

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.dashboard.verification import (  # noqa: E402
    SCIENTIFIC_PATHS,
    TEST_PATHS,
    canonical_source_file_bytes,
    compute_legacy_raw_source_tree_digest,
    git_source_blob,
    inspect_source_tree,
    read_test_baseline,
    source_digest_paths,
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_blob(root: Path, relative: str) -> bytes | None:
    return git_source_blob(root, relative)


def _first_difference(left: bytes, right: bytes) -> str:
    limit = min(len(left), len(right))
    for offset in range(limit):
        if left[offset] != right[offset]:
            return f"first_byte_offset={offset}"
    if len(left) != len(right):
        return f"length_difference={len(left)}:{len(right)}"
    return "no_byte_difference"


def _difference_kind(root: Path, relative: str, data: bytes, expected: str) -> str:
    canonical = canonical_source_file_bytes(root, relative)
    if _sha256(canonical) == expected and canonical != data:
        return "line_endings_only"
    if data.startswith(b"\xef\xbb\xbf") != canonical.startswith(b"\xef\xbb\xbf"):
        return "encoding_or_bom_difference"
    if b"\r\n" in data:
        return "line_endings_and_content_difference"
    reference = _git_blob(root, relative)
    if reference is not None:
        return f"content_or_encoding_difference ({_first_difference(data, reference)})"
    return "content_or_encoding_difference"


def main() -> int:
    baseline = read_test_baseline(ROOT) or {}
    raw_expected_files = baseline.get("source_files", {})
    expected_files: dict[str, str] = {}
    if isinstance(raw_expected_files, dict):
        expected_files = {
            str(path): str(digest)
            for path, digest in cast(dict[str, object], raw_expected_files).items()
        }

    scope_paths = SCIENTIFIC_PATHS + TEST_PATHS
    local_files = set(source_digest_paths(ROOT, scope_paths))
    inspection = inspect_source_tree(ROOT)

    print(f"platform: {inspection.platform}")
    print(f"normalization: {inspection.line_ending_normalization_mode}")
    print(f"dirty_relevant_paths: {list(inspection.dirty_relevant_paths)}")
    print(f"untracked_relevant_paths: {list(inspection.untracked_relevant_paths)}")
    print(f"missing_relevant_paths: {list(inspection.missing_relevant_paths)}")

    for relative in sorted(set(expected_files) | local_files):
        path = ROOT / relative
        expected = expected_files.get(relative)
        if not path.is_file():
            print(f"MISSING {relative}")
            continue
        data = path.read_bytes()
        local_digest = _sha256(data)
        canonical = canonical_source_file_bytes(ROOT, relative)
        canonical_digest = _sha256(canonical)
        if expected is None:
            print(
                f"ADDITIONAL {relative}: local_sha256={local_digest} "
                f"canonical_sha256={canonical_digest}"
            )
        elif local_digest != expected:
            kind = _difference_kind(ROOT, relative, data, expected)
            print(
                f"MISMATCH {relative}: local_sha256={local_digest} "
                f"expected_sha256={expected} canonical_sha256={canonical_digest} "
                f"difference={kind}"
            )

    print(f"expected_tree_digest: {baseline.get('tested_tree_digest')}")
    print(f"current_tree_digest: {inspection.digest}")
    print(f"legacy_raw_tree_digest: {compute_legacy_raw_source_tree_digest(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
