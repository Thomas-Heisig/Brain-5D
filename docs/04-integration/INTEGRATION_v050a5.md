# v0.5.0-alpha.5 Integration Guide

## 1. Version and docs

Set `pyproject.toml` version to `0.5.0a5`. Update README, CHANGELOG and the existing `docs/08-roadmap/` file non-destructively.

## 2. StructuralPlasticityEngine

Wire a `StructuralJournal` instance into the existing engine. After a proposal passes safety and approval and the Manipulator succeeds, append a `StructuralChangeRecord` and commit it. Add:

- `apply_structural_record(record)` for deterministic recovery/undo
- `undo_last_change()` delegating to `StructuralUndoManager`
- `history(limit=100)` delegating to the journal

Do not mutate the network anywhere except through the Manipulator or an existing public core API.

## 3. Coordinator

Keep both compatibility surfaces:

- alpha.3: `submit`, `configure`, `snapshot`
- alpha.4+: `publish`, `find`, `decision`

Add `approve(proposal_id)`, `reject(proposal_id)` and `auto_process(...)`. Coordinator decisions do not directly change the network.

## 4. RuntimeController

Add thread-safe APIs:

- `single_step()`
- `run_ticks(count)`
- `run_loop(count | None)`
- `request_snapshot()`

Validate `0 < count <= max_manual_ticks`. Prevent a second run thread while one is active. Snapshot requests must be processed only at a safe batch boundary.

## 5. Dashboard/OperatorBridge

Dashboard must only call the bridge/controller. Add read routes:

- `GET /api/structural/status`
- `GET /api/structural/proposals`
- `GET /api/structural/history`
- `GET /api/structural/heatmap?kind=...`
- `GET /api/structural/config`

Add write routes:

- `POST /api/structural/approve`
- `POST /api/structural/reject`
- `POST /api/structural/undo`
- `POST /api/structural/auto-approval`

Also expose runtime controls for 1/10/100/1000/custom ticks. Never pass arbitrary commands or shell text from the browser.

## 6. Snapshot lifecycle

A manual snapshot should flush/commit the structural journal, persist the normal `.b5d` snapshot and runtime checkpoint, then report completion to the dashboard.

## 7. Restore order

1. Base `.b5d`
2. state delta recovery
3. structural journal replay
4. runtime checkpoint
5. topology/invariant validation
6. continue simulation

## 8. Type safety

Keep Pyright/Pylance strict: typed collections, validated JSON/YAML boundaries, no dynamic neuron attributes, no `dict[str, object]` expanded into `subprocess`, no untyped `Mapping` values, and no blanket ignores.

## 9. Quality gate

After integration:

```powershell
.\.venv\Scripts\python.exe -m black src tests scripts
.\.venv\Scripts\python.exe -m pytest -v -m "not slow"
.\.venv\Scripts\python.exe -m mypy src
.\.venv\Scripts\python.exe -m black --check src tests scripts
.\.venv\Scripts\python.exe -m pyright src scripts tests
pylint src
git diff --check
.\.venv\Scripts\python.exe scripts\verify_v050a5.py
```

Run slow soak tests separately.
