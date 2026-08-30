# Alpha.7 Overlay Manifest

Copy the overlay into the repository root.

## Replaced

- `src/storage/checkpoint.py`
- `src/storage/core_restore.py`
- `src/dashboard/models.py`
- `src/dashboard/server.py`
- `src/dashboard/heatmap_source.py`
- `src/dashboard/static/index.html`
- `src/dashboard/static/app.js`
- `src/dashboard/static/styles.css`
- `tests/test_checkpoint.py`
- `tests/test_restore_continue.py`
- `docs/08-roadmap/ROADMAP_TO_USABLE_AI.md`
- `pyproject.toml`

## Added

- `src/dashboard/docs_source.py`
- `src/embodiment/`
- `tests/test_embodiment.py`
- `tests/test_dashboard_alpha7.py`
- `docs/02-architecture/EMBODIMENT_FOUNDATION.md`
- `docs/02-architecture/DETERMINISTIC_RESTORE_V3.md`
- `docs/03-dashboard/DASHBOARD_ALPHA7.md`
- `docs/05-quality/QUALITY_GATE_V040.md`
- `scripts/brain5d_launcher.py`
- `scripts/verify_all.py`
- `start.ps1`, `stop.ps1`, `start.cmd`, `stop.cmd`
- `README_ALPHA7.md`, `CHANGELOG_ALPHA7.md`

No binary storage-format migration is required.
