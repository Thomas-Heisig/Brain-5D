# Brain-5D v0.4.0-alpha.1 Final Robustness Overlay

This overlay finalizes the `.b5d` Snapshot V1 contract without introducing the
alpha.2 delta journal.

## Changed

- `src/storage/b5d.py`
- `src/storage/__init__.py`
- `tests/test_b5d_storage.py`
- `docs/B5D_FORMAT.md`
- `docs/SPRINT_STORAGE_V1.md`
- `docs/CHANGELOG.md`
- `README.md`
- `CHANGELOG.md`
- `scripts/verify_b5d.ps1`

## Added

- `docs/ROADMAP_TO_USABLE_AI.md`
- `docs/RELEASE_CHECKLIST_V040A1.md`
- `pyrightconfig.json`

## Key decisions

- Snapshot format V1 is frozen after this robustness pass.
- V1 detects structural corruption but does not add CRC/checksum fields.
- Checksums, crash-safe commit markers and tick deltas are alpha.2 journal work.
- `src/storage/b5d.py` has no `Any` annotations and uses Protocol boundaries.
- The 50k scalability test is opt-in and executed by the release verifier.
