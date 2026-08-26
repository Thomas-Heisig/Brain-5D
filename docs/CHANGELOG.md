# Changelog

## 2026-08-26 — Pre-Experiment Closure Sprint (Part 1)

### Gate Evidence Binding (Breaking Change)
- **`src/dashboard/gate_status.py`**: Replaced file-existence-based determinism checks with verification artifact (`research/generated/verification/determinism_infrastructure.json`). File existence alone no longer produces VERIFIED/PASSED status.
- Added `REQUIRED_DETERMINISM_PROOFS` with 7 proof IDs.
- Added `_read_determinism_artifact()` and `_determinism_infrastructure_verified()` methods with fail-closed validation.
- Error visibility criteria (experiment validity) now also use the determinism artifact.
- **`scripts/generate_determinism_artifact.py`**: New script to run determinism tests and produce the verification artifact.

### LearningEngine Determinism (Bug Fix)
- **`src/learning/learning_engine.py`**: Changed `_states` key from `id(synapse)` (Python memory address, non-deterministic across restarts) to stable `(pre_id, target_id)` tuples.
- Changed `events` dict key from `id(synapse)` to `(pre_id, target_id)`.
- Changed `set(spike_ids)` iteration to `sorted(set(...))` for deterministic order.
- Changed `events.values()` iteration to `sorted(events)` for deterministic order.
- Updated `get_eligibility()` and `_process_synapse_event()` to use stable keys.

### Production Restore Bundle (New Feature)
- **`src/storage/core_restore.py`**: Added `RestoredBundle` dataclass and `restore_full()` function that restores network + HomeostasisEngine + LearningEngine atomically.
- Fixed `restore_learning_state()` to use stable `(pre_id, target_id)` key lookup instead of linear scan with `id(synapse)` matching.
- Fixed `restore_learning_state()` to set `EligibilityTrace.value` instead of non-existent `_trace`.

### Tests
- **`tests/test_production_restore.py`**: New test file with 3 tests covering full restore bundle, engine-less restore, and continue-determinism.
- **`tests/test_engine_restore.py`**: Updated to use stable key lookup and correct `eligibility.value` attribute.

### Documentation
- `docs/todo.md`: Updated baseline to 367 passed, added determinism artifact info, updated gate status.
- `docs/ROADMAP.md`: Created with current status and future plans.
- `docs/changelog.md`: This file.

### Baseline
- `tests/test_baseline.json`: Updated to 367 passed, tree digest `dcd2d461...`.
- `research/generated/verification/determinism_infrastructure.json`: Created with 7/7 proofs verified.

---

## 2026-08-26 — Live Visualization & Verification Freshness Sprint (Part 2)

### Verification Artifact Generation Fix (Bug Fix)
- **`scripts/generate_determinism_artifact.py`**: Replaced custom `compute_tree_digest()` with canonical `compute_source_tree_digest()` from `src.dashboard.verification`. The custom function had different file filtering (only `.py/.toml/.yaml/.json/.cfg/.md`) and no path-interleaving, producing a different digest than the canonical function.
- Added `sys.path.insert(0, str(REPO_ROOT))` so the script can import from `src/`.
- Added `current_git_head()` function for provenance tracking.

### Verification Semantics Cleanup
- **`tests/test_structural_e2e.py`**, **`tests/test_structural_live_loop.py`**, **`tests/test_single_listener.py`**: Changed artifact field from `tested_commit` to `test_run_head` for semantic clarity. The tree digest is the freshness authority; commit hash is provenance only.
- **`scripts/generate_determinism_artifact.py`**: Uses `test_run_head` instead of `tested_commit`.

### Live Projection Service (New Feature)
- **`src/dashboard/live_projection.py`**: New module — `LiveProjectionService` reads directly from the in-memory `NeuralNetwork`, never from `.b5d` snapshots. Supports 5 projection kinds (activity, energy, membrane, spike, weight) with configurable aggregation (mean, max, sum, spike_count, active_fraction) and resolution (bins).
- **`src/dashboard/operator_bridge.py`**: Added `live_projection` attribute with automatic `LiveProjectionService` creation from the controller's network.
- **`src/dashboard/server.py`**: Added `GET /api/live/projection` endpoint with parameters: `kind`, `dimension_x`, `dimension_y`, `resolution`, `aggregation`. Response tagged as `live_runtime`.
- **`src/dashboard/heatmap_source.py`**: Added `source: str = "snapshot"` field to `HeatmapPayload` to distinguish from live data.

### LIVE vs SNAPSHOT Separation
- **`src/dashboard/static/index.html`**: Added `#source-badge` element showing LIVE or SNAPSHOT. Added `#live-toggle` button. Added membrane and spike kind buttons. Changed subtitle to show source badge.
- **`src/dashboard/static/app.js`**: Added `liveSource` toggle variable. Added `refreshLiveProjection()` function polling `/api/live/projection` at 500ms. Added `updateSourceBadge()` function. Heatmap metadata now shows source prefix (LIVE/SNAPSHOT).
- **`src/dashboard/static/styles.css`**: Added `.badge`, `.badge-live`, `.badge-snapshot`, `.provenance-badge` styles with distinct green (LIVE) and amber (SNAPSHOT) colors.

### Tests
- **`tests/test_live_projection.py`**: 12 tests covering energy accuracy, activity timing, weight projection, tick coherence, no-mutation guarantee, snapshot separation, bounded payload, and invalid parameter handling.

### Verification Freshness Restored
- All 5 verification artifacts now share the same `tested_tree_digest`.
- `tests/test_baseline.json`: 379 passed, 0 failed, 2 skipped.

### Baseline
- `tests/test_baseline.json`: 379 passed, canonical tree digest.
- All structural and determinism artifacts regenerated with matching digests.

