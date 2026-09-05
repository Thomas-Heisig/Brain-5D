"""Repair strict Pyright typing at JSON deserialization boundaries."""

from __future__ import annotations

from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"target block not found in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    replace_once(
        Path("src/dashboard/file_manager.py"),
        '''                        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                        if isinstance(manifest, dict):
                            created_at = manifest.get("created_at") or manifest.get(
                                "timestamp"
                            )
                            if created_at:
                                result["created_at"] = str(created_at)''',
        '''                        manifest_raw: object = json.loads(
                            manifest_path.read_text(encoding="utf-8")
                        )
                        if isinstance(manifest_raw, dict):
                            manifest = cast(dict[str, object], manifest_raw)
                            created_at = manifest.get("created_at") or manifest.get(
                                "timestamp"
                            )
                            if created_at is not None:
                                result["created_at"] = str(created_at)''',
    )

    replace_once(
        Path("src/research/evidence_engine.py"),
        '''        provenance = manifest.get("provenance_digests")
        source_freeze_sha = manifest.get("source_freeze_sha")
        if not isinstance(provenance, dict) or not isinstance(source_freeze_sha, str):
            raise ValueError("Validated promotion requires source-freeze digests")
        if _json_digest(provenance) != source_freeze_sha:
            raise ValueError("Source-freeze digest does not match provenance digests")

        review_path = EXPERIMENTS_DIR / experiment_id / "human_review.json"
        try:
            review = json.loads(review_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError("Validated promotion requires a human review") from exc
        if not isinstance(review, dict):
            raise ValueError("Human review artifact is invalid")
        if review.get("experiment_id") != experiment_id:
            raise ValueError("Human review experiment identity does not match")''',
        '''        provenance_raw = manifest.get("provenance_digests")
        source_freeze_sha = manifest.get("source_freeze_sha")
        if not isinstance(provenance_raw, dict) or not isinstance(source_freeze_sha, str):
            raise ValueError("Validated promotion requires source-freeze digests")
        provenance = cast(dict[str, object], provenance_raw)
        if _json_digest(provenance) != source_freeze_sha:
            raise ValueError("Source-freeze digest does not match provenance digests")

        review_path = EXPERIMENTS_DIR / experiment_id / "human_review.json"
        try:
            review_raw: object = json.loads(review_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError("Validated promotion requires a human review") from exc
        if not isinstance(review_raw, dict):
            raise ValueError("Human review artifact is invalid")
        review = cast(dict[str, object], review_raw)
        if review.get("experiment_id") != experiment_id:
            raise ValueError("Human review experiment identity does not match")''',
    )
    replace_once(
        Path("src/research/evidence_engine.py"),
        "            status=cast(str, decision),\n",
        "            status=decision,\n",
    )

    replace_once(
        Path("src/research/productive_learning.py"),
        '''    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("clean worker returned invalid JSON") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("result"), dict):
        raise RuntimeError("clean worker returned an invalid result envelope")
    return payload''',
        '''    try:
        payload_raw: object = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("clean worker returned invalid JSON") from exc
    if not isinstance(payload_raw, dict):
        raise RuntimeError("clean worker returned an invalid result envelope")
    payload = cast(dict[str, Any], payload_raw)
    if not isinstance(payload.get("result"), dict):
        raise RuntimeError("clean worker returned an invalid result envelope")
    return payload''',
    )

    replace_once(
        Path("src/research/productive_learning.py"),
        "from typing import Any\n",
        "from typing import Any, cast\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
