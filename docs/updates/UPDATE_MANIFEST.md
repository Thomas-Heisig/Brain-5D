# v0.4.0-alpha.6 Overlay Manifest

## Replaced files

- `src/storage/checkpoint.py`
- `src/storage/core_restore.py`
- `src/dashboard/models.py`
- `src/dashboard/static/index.html`
- `src/dashboard/static/app.js`
- `tests/test_checkpoint.py`

## New files

- `tests/test_dashboard_alpha6.py`
- `scripts/apply_alpha6_quality_fixes.py`
- `scripts/apply_alpha6_metadata.py`
- `docs/DETERMINISTIC_RESTORE.md`
- `docs/RESEARCH_ALIGNMENT.md`
- `docs/QUALITY_GATE.md`
- `README_ALPHA6.md`

## In-place migrations performed by scripts

- `src/manipulation/manipulator.py`: explicit `int` return from neuron creation
- `src/self_organization/engine.py`: typed `Coord5D | None` return
- `src/experiments/learning_lab.py`: typed `ConfigDict` bridge
- `src/storage/recovery.py`: mutable protocol adapter for mypy
- `pyproject.toml`: alpha.6 package version
- `README.md`: deterministic restore and strategy links
- `docs/ROADMAP_TO_USABLE_AI.md`: research alignment marker
