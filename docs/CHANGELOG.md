# Changelog

## 2026-08-26 — Pre-Experiment Closure Sprint

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
