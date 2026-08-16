# v0.4.0-alpha.4 Update Manifest

## Modified

- `src/storage/runtime.py`
- `src/storage/recovery.py`
- `src/storage/__init__.py`
- `configs/poc_config.yaml`
- `pyproject.toml`
- `scripts/verify_b5d.py`
- `CHANGELOG.md`
- `docs/CHANGELOG.md`
- `docs/ROADMAP_TO_USABLE_AI.md`

## Added

- `src/storage/async_runtime.py`
- `src/storage/checkpoint.py`
- `src/storage/compaction.py`
- `src/storage/core_restore.py`
- `tests/test_async_storage.py`
- `tests/test_checkpoint.py`
- `tests/test_compaction.py`
- `scripts/apply_alpha4_quality_fixes.py`
- `scripts/prepare_alpha4.py`
- `docs/SPRINT_STORAGE_V4.md`
- `docs/ROADMAP_ALPHA4.md`

## Compatibility

No byte-level change to frozen `.b5d` V1 or `.b5d.journal` V1.
