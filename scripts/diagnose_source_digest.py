"""Diagnose source-freeze digest mismatches on Windows and Linux."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.dashboard.verification import (
    SCIENTIFIC_PATHS,
    TEST_PATHS,
    _canonical_text_bytes,
    _filesystem_digest_paths,
    _git_output,
    _git_text_paths,
    compute_legacy_raw_source_tree_digest,
    inspect_source_tree,
    read_test_baseline,
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_blob(root: Path, relative: str) -> bytes | None:
    output = _git_output(root, ["show", f"HEAD:{relative}"])
    return output


def _first_difference(left: bytes, right: bytes) -> str:
    limit = min(len(left), len(right))
    for offset in range(limit):
        if left[offset] != right[offset]:
            return f"first_byte_offset={offset}"
    if len(left) != len(right):
        return f"length_difference={len(left)}:{len(right)}"
    return "no_byte_difference"


def _difference_kind(root: Path, relative: str, data: bytes, expected: str) -> str:
    canonical = _canonical_text_bytes(data) if b"\0" not in data else data
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
    expected_files = baseline.get("source_files", {})
    if not isinstance(expected_files, dict):
        expected_files = {}
    expected_files = {str(path): str(digest) for path, digest in expected_files.items()}

    scope_paths = SCIENTIFIC_PATHS + TEST_PATHS
    local_files = set(_filesystem_digest_paths(ROOT, scope_paths))
    text_paths = _git_text_paths(ROOT, sorted(local_files))
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
        canonical = _canonical_text_bytes(data) if relative in text_paths or b"\0" not in data else data
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
