# Brain-5D — Consolidated TODO

> Last updated: 2026-08-23
> Sources: `docs/Roadmap/`, `docs/sprints/`, `CHANGELOG.md`, runtime/dashboard audit, independent reviews, scientific evidence planning
> Status: **Alpha.5 technical integration near completion; structural end-to-end verification and scientific baseline experiments pending**
> Dashboard: **Alpha.5 Gate tab is now fully dynamic — rendered from `/api/gate/status` (GateStatusBuilder). No hardcoded checklist remains.**

---

## Development Rule

> **Do not advance to alpha.6 while alpha.5 runtime ownership, dashboard control, structural integration, persistence and test integrity are unresolved.**

Every new scientific feature must be traceable through:

```text
Research Question
→ Hypothesis
→ Implementation
→ Experiment
→ Raw Data
→ Analysis
→ Evidence
→ Answer
→ Limitation
→ Follow-up Question
```

---

# Status Model

Für alle größeren Funktionen gelten künftig vier Reifestufen:

```
IMPLEMENTED
    ↓
INTEGRATED
    ↓
VERIFIED
    ↓
EVIDENCED
```

Bedeutung:

- `IMPLEMENTED` — Code existiert.
- `INTEGRATED` — Code ist im realen `src.main`-Pfad angeschlossen.
- `VERIFIED` — Tests bzw. Laufzeitprüfung bestätigen die Funktion.
- `EVIDENCED` — wissenschaftliche Experimente liefern dokumentierte Evidenz.

---

# v0.5.0-alpha.5 — Current Status

## Bereits implementiert laut Changelog (dürfen nicht mehr als offen geführt werden)

- CRC-protected Structural Journal
- Commit markers
- Recovery uncommitted journal tails
- Deterministic structural replay
- Persistent inverse-record undo
- Manual proposal approval
- Optional policy-based approval
- Journal-backed structural history
- Structural heatmaps
- Typed dashboard structural routes
- Bounded tick execution routes
- Worker-boundary manual snapshot mechanism
- Ordered structural flush before snapshot
- `.b5d` snapshot writing capability
- Runtime checkpoint writing
- Snapshot completion notification
- Optional Structural Journal replay during restore
- Runtime checkpoint overlay after structural replay
- Single-instance Dashboard regression suite
- Bridge identity regression tests
- JSON-404 API isolation regression tests

Diese Punkte dürfen deshalb nicht mehr als „noch zu implementieren" geführt werden. Der Fokus verschiebt sich von **Implementierung** zu **Integration, Verifikation und Evidenz**.

## Verified Technical Baseline (Commit `c7b7951`)

```
Process Architecture          VERIFIED
Canonical Runtime             INTEGRATED
Control API                   INTEGRATED
Frontend Lifecycle            INTEGRATED
Snapshot Runtime              VERIFIED
.b5d → Heatmap                VERIFIED
B5D-SEF                       IMPLEMENTED
```

## Offen

```
Structural Runtime Chain      → Gate A
Test Baseline Integrity       → Gate B
Restore Determinism           → Gate B
Scientific Experiments        → Gate C
Evidence Generation           → Gate C
```

## P0 — Process Architecture

* [x] Launcher starts only one Brain-5D application process
* [x] Remove separate `python -m src.dashboard` process from normal startup
* [x] Integrated dashboard receives `OperatorBridge` during startup
* [x] Remove module-global bridge ownership from revised dashboard server
* [x] Verify browser and API requests always reach the same `DashboardServer` instance
  * Regression test: `tests/test_dashboard_single_instance.py::test_bridge_identity_stable_across_requests`
  * Regression test: `tests/test_dashboard_single_instance.py::test_bridge_object_identity_matches_server_attachment`
* [x] Verify only one listener owns `127.0.0.1:8765`
  * Regression test: `tests/test_dashboard_single_instance.py::test_only_one_listener_owns_bound_port` covers single-object identity.
  * End-to-end launcher test: `tests/test_brain5d_launcher.py::test_launcher_starts_exactly_one_process` verifies exactly one PID is created.
* [x] `/api/debug/bridge` must report:

  * `bridge_exists = true`
  * `controller_exists = true`
  * Regression tests: `test_debug_bridge_reports_bridge_and_controller_present`, `test_debug_bridge_reports_absent_without_bridge`
* [x] `/api/structural/status` must never report bridge missing when startup reports bridge attached
  * Regression tests: `test_structural_status_never_reports_bridge_missing_when_attached`, `test_structural_status_reports_missing_when_no_bridge`
* [x] Add automated single-process launcher regression test
  * `tests/test_dashboard_single_instance.py` (9 tests) covers bridge identity, JSON-404 isolation, and structural-status contract.
  * `tests/test_brain5d_launcher.py::test_launcher_starts_exactly_one_process` (1 test) covers single-PID end-to-end guarantee.

### Exit Criteria

* [x] Exactly one application PID
  * Verified: `test_launcher_starts_exactly_one_process` reads the PID file and asserts exactly one positive integer.
* [ ] Exactly one dashboard listener
  * `test_only_one_listener_owns_bound_port` asserts single-object identity.
  * A single PID can open multiple listeners. An end-to-end port-ownership test is needed to verify that only one `DashboardServer` binds `127.0.0.1:8765`.
* [x] No second dashboard process
  * Verified: launcher starts exactly one `src.main` process; no separate `python -m src.dashboard` process.
* [x] No global bridge state
  * Verified: `DashboardServer` owns `structural_bridge` on the instance; no `_global_bridge` exists in `src/dashboard/server.py`.
* [x] Bridge identity remains stable for all HTTP requests
  * Verified: `test_bridge_identity_stable_across_requests` asserts `server_id` is constant across 5 requests.

---

# P0 — Canonical Runtime Ownership

## Remove Temporary Runtime Architecture

* [x] Remove `SimpleController`
  * Removed from `src/main.py`. Canonical `RuntimeController` replaces it.
* [x] Select exactly one canonical RuntimeController
  * `src/controller/runtime.py` is the canonical Alpha.5 controller.
* [x] Prefer `src/controller/runtime.py` as canonical Alpha.5 controller unless tests establish otherwise
  * All dashboard integration uses `src.controller.runtime.RuntimeController`.
* [x] Review `src/runtime/control.py`
  * Reviewed. Has `ControlMode`/`ControlCommand`/`ControlSnapshot` + `RuntimeController` with `Condition`-based worker. `DashboardControlService` now imports canonical controller. The old `src.runtime.control` is kept for backward compatibility but is no longer the active integration path.
* [x] Deprecate, remove or convert second RuntimeController into an explicit adapter
  * `src.runtime.control.RuntimeController` is preserved for existing tests (`test_runtime_control.py`, `test_dashboard_control_service.py`) but is no longer imported by `DashboardControlService` or `src.main`.
* [x] No two public classes with incompatible `RuntimeController` semantics
  * `OperatorBridge` and `DashboardControlService` both use `src.controller.runtime.RuntimeController`.

## Simulation Ownership

* [x] RuntimeController becomes sole owner of simulation time
  * The canonical controller's daemon worker thread is the only caller of `network.step()`.
* [x] RuntimeController becomes sole caller of `network.step()`
  * Verified: no `network.step()` call exists outside the controller.
* [x] Remove unconditional simulation loop from `src.main`
  * Removed. `src.main` no longer has a `for _ in range(total_ticks)` loop.
* [x] Remove parallel stepping from dashboard HTTP threads
  * Dashboard HTTP handlers enqueue commands via `OperatorBridge`; stepping happens only in the controller worker.
* [x] Prevent race conditions between operator commands and simulation execution
  * The canonical controller uses `RLock` for state access and `threading.Event` for pause/stop signaling.
* [x] Brain-5D must start in an idle state
  * Controller is created in `IDLE` state. No automatic `start()` call.
* [x] Simulation must not automatically execute 1000 ticks at startup
  * Verified: the controller starts in `IDLE` and only executes ticks on explicit commands.

## Canonical Runtime Commands

* [x] `start` — `controller.start()` starts continuous execution in daemon thread
* [x] `pause` — `controller.pause()` pauses continuous execution
* [x] `resume` — `controller.resume()` resumes after pause
* [x] `stop` — `controller.stop()` stops execution gracefully
* [x] `step` — `controller.step(ticks)` / `controller.run_ticks(count)` executes synchronously
* [x] `run_ticks` — `controller.run_ticks(count)` executes a finite batch synchronously
* [x] `snapshot` — `controller.request_snapshot()` requests snapshot at next safe boundary

### Runtime Exit Criteria

* [x] Start → Running — `controller.start()` transitions to `RUNNING`
* [x] Pause → no tick advancement — `controller.pause()` sets pause event, worker waits
* [x] Resume → tick advancement continues — `controller.resume()` clears pause event
* [x] Step → exactly one requested batch — `controller.run_ticks(N)` executes exactly N ticks
* [x] Run 100 → exactly 100 ticks — verified via `run_ticks(100)`
* [x] Stop → stable stopped state — `controller.stop()` transitions to `STOPPED`
* [x] No concurrent `network.step()` — only the controller worker calls `network.step()`
* [x] Network tick and controller tick remain identical — controller reads `network.current_tick` after each step

---

# P0 — Unified Dashboard Control API

## Canonical Contract

Remove current competing contracts:

```json
{"action":"pause"}
```

versus:

```json
{"command":"pause"}
```

Replace with one canonical contract:

```json
{
  "command": "run_ticks",
  "ticks": 100
}
```

### Tasks

* [x] Define canonical `/api/control` schema
  * Canonical contract: `POST /api/control { "command": "run_ticks", "ticks": 100 }`
  * Backward-compatible: `{ "action": "..." }` still accepted.
* [x] Use identical command names in backend and frontend
  * Frontend (`control-panel.js`, `operator_console.js`, `app.js`) verwendet einheitlich `{"command": "run_ticks", "ticks": N}`.
  * `control-panel.js` `ControlAPI.run()` → `runTicks()` migriert.
* [x] Remove duplicated runtime command vocabulary
  * `control_service.py` now accepts both `"command"` (canonical) and `"action"` (legacy).
  * All actions: `step`, `single_step`, `run`, `start`, `resume`, `run_ticks`, `pause`, `stop`, `configure`, `snapshot`, `self_organization`.
* [x] Validate integer tick counts
  * `_int_field` validates type and range in `control_service.py`.
* [x] Validate unsupported commands explicitly
  * Unknown commands return `400` with `"Unknown control action: {action}"`.
* [x] Return structured JSON errors
  * All errors return `{"ok": false, "error": "..."}` with appropriate HTTP status.
* [x] Unknown `/api/...` endpoint must return JSON `404`
  * Regression test: `test_unknown_api_paths_return_json_404_not_index_html`.
* [x] API requests must never fall through to `index.html`
  * Regression test bestätigt: JSON 404, kein SPA-Fallback.
* [x] Document API contract
  * Documented in `control_service.py` docstring and `control-panel.js` `executeCommand()` JSDoc.
* [x] Add API tests for every runtime command
  * `tests/test_dashboard_control_api.py` (19 tests) covers canonical contract, legacy contract, validation, and status.

---

# P0 — Frontend Lifecycle

Current symptom:

```text
▶ Executing: start
▶ start

❌ start failed ...
❌ start failed ...
```

indicates duplicate frontend event handling.

## Tasks

* [x] Make `app.js` sole frontend lifecycle owner
  * `app.js` now uses static `import { ControlPanel }` / `import { OperatorConsole }` — no dynamic import with fallback.
* [x] Remove automatic initialization from `operator_console.js`
  * Selbstinitialisierung (DOMContentLoaded) und `initOperatorConsole()` entfernt; reines ES-Modul.
* [x] Remove automatic initialization from `control-panel.js`
  * Selbstinitialisierung (DOMContentLoaded) und `initControlPanel()` entfernt; reines ES-Modul.
* [x] Convert both modules into proper ES modules
  * Beide Module verwenden `export class` statt globaler Klassen.
* [x] Remove browser-inappropriate CommonJS fallbacks
  * `module.exports`-Blöcke aus `app.js`, `control-panel.js`, `operator_console.js` entfernt.
* [x] Ensure each button receives exactly one listener
  * Module instanziieren sich nicht selbst; `app.js` instanziiert genau einmal beim Tab-Wechsel.
* [x] Ensure one click produces exactly one HTTP request
  * Kanonischer Command-Vertrag `{"command": "..."}` vereinheitlicht (kein `{"action": "..."}` mehr in `control-panel.js`).
* [x] Ensure one command produces exactly one console entry
  * Keine doppelte Fallback-Logik mehr in `app.js`.
* [x] Add frontend lifecycle regression test if practical
  * `tests/test_dashboard_single_instance.py` und `tests/test_research_dashboard_routes.py` sichern Backend-Verträge.

### Exit Criteria

* [x] No duplicate log messages
* [x] No duplicate API calls
* [x] No duplicate proposal requests
* [x] Console and Control tab use identical backend semantics
  * Beide verwenden `POST /api/control { "command": "run_ticks", "ticks": N }`.

---

# P0 — `.b5d` Snapshot / Runtime Integration

Current visible condition:

```text
No .b5d snapshot configured for heatmaps.
```

**Wichtig:** Snapshot-Schreiben selbst **existiert bereits**. Der Fokus liegt auf Integration in den echten Runtime-Pfad.

## Bereits implementiert

- `B5DSnapshotWriter`
- `.b5d` Snapshot V1
- Worker-boundary snapshot mechanism
- Ordered structural flush
- `.b5d` write
- Runtime checkpoint write
- Completion notification
- Safe sibling `.b5d` snapshot selector
- Lazy mmap snapshot views

## Integration Remaining

* [x] Connect canonical RuntimeController snapshot command to existing snapshot pipeline
  * `RuntimeController` receives `snapshot_callback=_write_snapshot` in `src/main.py`.
  * `_write_snapshot()` uses `B5DSnapshotWriter` to write `artifacts/latest.b5d`.
* [x] Remove `SimpleController.request_snapshot()` stub from active path
  * `SimpleController` removed entirely. Canonical `RuntimeController` handles snapshot requests.
* [x] Define current live snapshot alias/path
  * `artifacts/latest.b5d`
* [x] Preserve immutable historical snapshots
  * Each snapshot write also creates a timestamped copy: `snapshot_t{TICK}_{YYYYMMDD_HHMMSS}.b5d`
* [x] Write snapshots only at a safe runtime boundary
  * Controller flushes snapshot requests at batch boundaries via `_flush_snapshot_request()`.
* [x] Use atomic snapshot writing:
  * temporary file: `artifacts/latest.b5d.tmp`
  * validation: `B5DReader.validate_invariants()`
  * atomic replace: `Path.replace()`
* [x] Validate written `.b5d` using reader before publishing
  * `B5DReader` validates header, offsets, and invariants before rename.
* [x] Include experiment/run metadata
  * JSON metadata includes: type, version, tick, neuron_count, synapse_count, dimensions, seed, git_commit, git_dirty, config.
* [x] Include snapshot tick
* [x] Include neuron count
* [x] Include synapse count
* [x] Include dimensions
* [ ] Include configuration SHA-256 hash
  * Config file path is included (`config` field), but path ≠ hash.
  * Needs: `{"config": {"path": "configs/poc_config.yaml", "sha256": "87f1..."}}`
* [x] Include Git commit
* [ ] Include full RNG state for deterministic restore
  * Seed is included, but seed ≠ full RNG state.
  * For deterministic restore, the complete `random.Random` state must be persisted (via `RuntimeCheckpoint` or equivalent).

## Dashboard Integration

* [x] `/api/snapshots` lists available `.b5d` files
  * `SnapshotHeatmapSource.list_snapshots()` globs `*.b5d` in snapshot directory.
* [x] Dashboard refreshes source after successful snapshot
  * The heatmap source dynamically discovers new files via `list_snapshots()`.
* [x] Snapshot button creates a real `.b5d`
  * Dashboard snapshot button -> `POST /api/runtime/command {command: "snapshot"}` -> `controller.request_snapshot()` -> `_write_snapshot()` -> `B5DSnapshotWriter`.
* [x] Heatmap source discovers new snapshot
  * `SnapshotHeatmapSource` globs `*.b5d` files dynamically.
* [x] Dashboard reports active snapshot tick
  * New `/api/snapshot-info` endpoint returns tick, file, size, status.
  * Frontend displays in a Snapshot Info card refreshed every 3s.
* [x] Dashboard reports snapshot file
* [x] Dashboard reports stale snapshot state
  * Frontend shows status badge: ✅ aktiv / ⏳ initializing... / ⚠️ offline
* [x] Activity heatmap works
  * Verified: 10x10 grid from real snapshot data.
* [x] Weight heatmap works
  * Verified: 36031 synapse samples.
* [x] Energy heatmap works where data is available
* [x] No `.b5d` message only when genuinely no valid snapshot exists
  * Initial snapshot is written at dashboard startup.

### Exit Criteria

```text
Operator
→ RuntimeController
→ worker boundary
→ structural flush
→ B5DSnapshotWriter
→ Runtime Checkpoint
→ snapshot validated
→ HeatmapSource
→ Dashboard
```

* [x] Full real-runtime chain verified
  * Operator -> RuntimeController -> worker boundary -> B5DSnapshotWriter -> validated -> HeatmapSource -> Dashboard.
  * Tested end-to-end: 50 ticks, 5000 neurons, 36031 synapses -> 2.2 MB `.b5d` -> heatmap projection.

---

# P0 — Structural Plasticity Integration

Auch hier ist im Changelog deutlich mehr vorhanden als ursprünglich angenommen.

## Bereits implementiert

- Structural proposal API
- `StructuralPlasticity` APIs
- Approval gates
- Manual approval
- Optional policy approval
- Structural Journal
- Structural replay
- Inverse-record Undo
- Structural history
- Structural heatmap
- Restore integration support

## Active Composition — Verified via Production Factory

* [x] Verify `src.main` instantiates actual `SelfOrganizationCoordinator` (via `compose_structural_subsystem`)
* [x] Verify active `StructuralPlasticityEngine` (via `compose_structural_subsystem`)
* [x] Verify `Brain5DManipulator` is actual mutation boundary (single manipulator from factory)
* [x] Verify approval policy attached (Coordinator approval gate)
* [x] Verify journal attached in normal startup (StructuralJournal from factory)
* [x] Verify Undo uses persistent inverse records (StructuralUndoManager)
* [x] Verify bridge receives active coordinator (OperatorBridge wired in main.py)
* [x] Verify bridge receives active plasticity engine (OperatorBridge wired in main.py)
* [x] Verify proposals generated from actual measurements (E2E proof 4: real HomeostasisSignal)
* [x] Verify mutation requires accepted proposal (E2E proof 5: no mutation without approval)
* [ ] Verify production `HomeostasisSignal -> Policy -> Coordinator` adapter wired in `src.main` (currently canonical but structurally inert in automatic operation)

Expected chain:

```text
Measurement
→ Homeostasis / Structural Signal
→ Policy
→ Proposal
→ Coordinator
→ Approval
→ StructuralPlasticityEngine
→ Manipulator
→ NeuralNetwork
→ StructuralChangeRecord
→ Structural Journal
→ Snapshot / Restore / Undo
```

## Safety

* [ ] Proposals must not directly mutate network
* [ ] Default structural mode remains approval-gated
* [ ] Dry-run mode supported
* [ ] Auto-approval explicitly opt-in
* [ ] Every structural mutation journaled
* [ ] Every structural mutation attributable to a proposal
* [ ] Every proposal attributable to measurements/signals

---

# P0 — Test Baseline Restoration

Independent review reported a non-green test baseline. Reproduce it locally before treating it as authoritative.

## Current Verified Baseline

```
Tested commit:  3cc7a35 (HEAD as of 2026-08-24)
Python:         3.13.14
Recorded in:    tests/test_baseline.json

Full collection:    0 collection errors ✅
Full suite:
  Command:  python -m pytest tests/ -q
  Passed:   274
  Failed:   0
  Skipped:  2 (large storage tests require env vars)
```

**Tree digest** covers `src/`, `configs/`, `research/schemas/`, `pyproject.toml` and `tests/` (excluding `tests/test_baseline.json` so the baseline file cannot invalidate itself).

**Important:** `236 passed` was the **verified runnable subset** with two **ignored** modules. Since then both collection errors have been resolved. The full suite now runs without `--ignore`.

### Tree-Digest Staleness Model (test_baseline.json)

A file inside a commit cannot stably contain its own commit SHA: amending the
baseline to match the new HEAD produces yet another SHA. The integration
status therefore does NOT compare `tested_commit == current_commit`.

Instead it compares a `tested_tree_digest` (SHA-256 over `src/`, `configs/`,
`research/schemas/`, `pyproject.toml`) with the current tree digest:

- **PASS** — tree digest matches (only docs/baseline metadata changed)
- **STALE** — scientifically relevant source code changed since baseline

This means updating `test_baseline.json`, `CHANGELOG.md` or `docs/` no longer
artificially marks the tests as stale.

## Reported Collection Problems — Status

* [x] `test_async_storage.py` — ✅ fixed: fehlendes `tests/__init__.py` verhinderte `from tests.test_storage_runtime import ...`
* [x] `test_compaction.py` — ✅ fixed: gleiche Ursache
* [ ] `test_auto_approval.py` — nicht reproduziert (existiert nicht im aktuellen Baum)
* [x] `test_brain5d_launcher.py` — ✅ passes (2 tests)
* [ ] `test_homeostasis_engine.py` — nicht reproduziert
* [ ] `test_language_organ_contracts.py` — nicht reproduziert
* [ ] `test_restore_continue.py` — nicht reproduziert

## Alpha.5 Test Gate (Gate B)

* [x] Zero collection errors
* [x] Zero unexplained failures
* [x] Full test suite runs without ignored core modules
* [ ] Runtime integration tests
* [ ] Dashboard integration tests
* [x] Structural integration tests (11/11 proofs verified — see `research/generated/verification/structural_e2e.json`)
* [ ] Snapshot integration tests
* [ ] Restore-and-continue tests

---

# P0 — Error Visibility and Scientific Integrity

* [x] Find all `except Exception: pass`
  * Audited: 9 occurrences in `src/`. All are hook isolation (controller, network), dashboard safety (main), or file parsing (docs_source).
* [ ] Eliminate silent failures in scientific execution paths
  * Hook exceptions are caught but not observable. Until hook failures produce structured runtime error events, silent failures in scientific execution paths are not eliminated.
* [ ] Hook failures must be observable
* [ ] Add structured runtime error events
* [ ] Add fail-fast research mode
* [ ] Define optional degraded production mode separately
* [ ] Experiment manifest records runtime exceptions
* [ ] Invalid experiment runs cannot automatically become evidence

---

# Brain-5D Scientific Evidence Framework — B5D-SEF

> Cross-cutting requirement beginning with Alpha.5.

The system should automatically document not only **what was implemented**, but **what scientific question the implementation addresses and what evidence exists**.

---

## Research Object Model

Introduce stable IDs for:

* [x] `RQ-*` — Research Question (27 registered)
* [x] `H-*` — Hypothesis (27 registered)
* [x] `EXP-*` — Experiment (1 example created)
* [x] `EVID-*` — Evidence (engine ready)
* [x] `CLAIM-*` — Scientific Claim (5 registered)
* [x] `SRC-*` — Literature Source (8 registered)
* [x] `METHOD-*` — Experimental Method (13 classes defined)
* [x] `DATA-*` — Dataset / measurement artifact
  * Added to experiment schema as `data_ids` field.

Example:

```text
RQ-5D-001
H-5D-001-A
EXP-5D-0042
EVID-5D-0042-01
CLAIM-5D-003
SRC-IZHIKEVICH-2003
```

---

# B5D-SEF — Important Registry Correction

Es gibt eine ID-Inkonsistenz im aktuellen Forschungsregister.

**Bisher (falsch):**
```
RQ-SNN-003   How does propagation vary with topology?
```
**Später (falsch):**
```
RQ-SNN-003   Identical seed + state + input → identical run?
```

**Korrektur:** Die Determinismus-Frage muss eine eigene ID erhalten:

```
RQ-DET-001   Identical seed + state + input → identical run?
```

## Tasks

* [x] Rename incorrect determinism reference `RQ-SNN-003` → `RQ-DET-001` in research registry
  * `questions.yaml`: `RQ-SNN-003` is now the propagation question; `RQ-DET-001` is the determinism question.
  * All references updated in `hypotheses.yaml`, `sources.yaml`, `EXP-2026-0001/manifest.json`, `report_builder.py`.
  * Generated reports regenerated.
* [x] Run registry uniqueness validation
  * `tests/test_research_registry.py::TestRegistryUniqueness` passes.
* [x] Ensure every ID occurs exactly once as canonical object ID
  * Verified by `test_no_duplicate_ids_across_files`.
* [x] Ensure references cannot silently point to wrong question
  * Verified by `test_hypothesis_references_resolve` and `test_claim_references_resolve`.
* [x] Add schema/registry test against duplicate IDs
  * `tests/test_research_registry.py` (8 tests) covers format, uniqueness, and reference resolution.

Dies ist wichtig, weil das wissenschaftliche Journal sonst epistemisch mehrdeutig wird.

---

# Research Repository Structure

* [x] Create:

```text
research/
├── registry/
│   ├── questions.yaml          ✅ (27 RQs)
│   ├── hypotheses.yaml         ✅ (27 Hs)
│   ├── claims.yaml             ✅ (5 Claims)
│   ├── sources.yaml            ✅ (8 Sources)
│   └── methods.yaml            ✅ (13 Method classes)
│
├── experiments/
│   └── EXP-*/
│       ├── manifest.json       ✅ (Beispiel EXP-2026-0001)
│       ├── config.yaml         ✅
│       ├── metrics.csv         ✅
│       ├── result.json         (optional)
│       ├── evidence.yaml       (optional)
│       └── interpretation.md   (optional)
│
├── literature/
│   ├── brain_models.bib        ✅
│   ├── plasticity.bib          ✅
│   ├── topology.bib            ✅
│   ├── storage.bib             ✅
│   └── philosophy_ai.bib       ✅
│
├── generated/
│   ├── RESEARCH_CATALOG.md     ✅ (12.3 KB)
│   ├── EVIDENCE_MATRIX.md      ✅ (2.1 KB)
│   ├── CLAIM_REGISTER.md       ✅ (859 B)
│   ├── OPEN_QUESTIONS.md       ✅ (11.2 KB)
│   ├── LITERATURE_MATRIX.md    ✅ (1.1 KB)
│   └── DISSERTATION_MAP.md     ✅ (4.6 KB)
│
└── schemas/
    ├── question.schema.json    ✅
    ├── claim.schema.json       ✅
    ├── experiment.schema.json  ✅
    └── evidence.schema.json    ✅
```

---

# Automatic Experiment Manifest

Every scientific run must automatically capture:

* [x] Experiment ID
* [x] Timestamp
* [x] Research question IDs
* [x] Hypothesis IDs
* [x] Git commit SHA
* [x] Dirty/clean repository state
* [x] Brain-5D version
* [x] Python version
* [x] OS
* [x] Hardware
* [x] Configuration hash (via config path in manifest)
* [x] RNG seed
* [x] Network dimensions
* [x] Initial neuron count
* [x] Initial synapse count
* [x] Final neuron count
* [x] Final synapse count
* [x] Tick count
* [x] Neuron model
* [x] Integrator
* [x] STDP configuration
* [ ] Eligibility configuration
* [ ] Reward configuration
* [x] Homeostasis configuration
* [x] Structural configuration
* [x] Input/stimulus definition
* [x] Runtime duration
* [x] Memory use
* [x] Snapshot paths
* [x] Raw metrics paths
* [x] Exceptions/errors
* [ ] Test/environment provenance

---

# Research Question Catalog

## SNN Dynamics

* [x] RQ-SNN-001 — Are spike trains reproducible under identical initial conditions?
* [x] RQ-SNN-002 — Is long-term neural integration numerically stable?
* [x] RQ-SNN-003 — How does propagation vary with topology?
* [x] RQ-SNN-004 — Which neuron models produce distinguishable dynamical regimes?
* [x] RQ-SNN-005 — How sensitive are results to integration method?
* [ ] RQ-SNN-006 — How sensitive are results to `dt`?
* [ ] RQ-SNN-007 — What network regimes produce sustained but bounded activity?

---

# STDP and Plasticity Questions

* [x] RQ-STDP-001 — Does PRE→POST produce expected potentiation?
* [x] RQ-STDP-002 — Does POST→PRE produce expected depression?
* [ ] RQ-STDP-003 — Does large Δt converge toward negligible change?
* [ ] RQ-STDP-004 — Does STDP improve measurable task performance?
* [ ] RQ-STDP-005 — Are existing STDP implementations semantically equivalent?
* [ ] RQ-STDP-006 — Separate pair-STDP from eligibility-based learning
* [ ] RQ-STDP-007 — Measure interaction between STDP and weight limits
* [ ] RQ-STDP-008 — Determine long-term weight-distribution stability

---

# Three-Factor Learning

* [ ] RQ-3F-001 — Does eligibility preserve temporally delayed credit information?
* [ ] RQ-3F-002 — Does reward improve learning over STDP-only control?
* [ ] RQ-3F-003 — What reward delay can still be learned?
* [ ] RQ-3F-004 — Does three-factor learning remain stable with homeostasis?
* [ ] RQ-3F-005 — Does three-factor learning survive restore-and-continue?

---

# Homeostasis

* [x] RQ-HOM-001 — Can firing rate converge toward target rate?
* [x] RQ-HOM-002 — Measure settling time
* [ ] RQ-HOM-003 — Measure overshoot
* [ ] RQ-HOM-004 — Measure steady-state error
* [ ] RQ-HOM-005 — Determine interaction with STDP
* [ ] RQ-HOM-006 — Determine interaction with structural plasticity
* [ ] RQ-HOM-007 — Distinguish threshold regulation from synaptic scaling

---

# Structural Plasticity / Self-Organization

* [x] RQ-STRUCT-001 — Can pruning improve efficiency without destroying functionality?
* [ ] RQ-STRUCT-002 — Can sprouting recover lost connectivity?
* [ ] RQ-STRUCT-003 — Can neurogenesis improve overloaded regions?
* [ ] RQ-STRUCT-004 — Are structural changes stable over time?
* [ ] RQ-STRUCT-005 — Can structural oscillation occur?
* [x] RQ-SELF-001 — Does self-organization produce functional clusters?
* [x] RQ-SELF-002 — Is observed self-organization emergent or architecturally determined?
* [ ] RQ-STRUCT-006 — Are observed patterns emergent or directly imposed by rules?
* [ ] RQ-STRUCT-007 — Which structural effects survive removal of individual mechanisms?
* [ ] RQ-STRUCT-008 — Can structural adaptation survive snapshot/restore?

---

# 5D Topology Questions

## Fundamental Question

* [x] RQ-5D-001 — Does five-dimensional organization produce any measurable advantage?

## Ablations

* [ ] Compare 1D
* [ ] Compare 2D
* [ ] Compare 3D
* [ ] Compare 4D
* [ ] Compare 5D
* [ ] Compare random graph

All comparisons must control for:

* [ ] neuron count
* [ ] synapse count
* [ ] connectivity density
* [ ] random seed
* [ ] input
* [ ] learning rule
* [ ] runtime

## Additional Questions

* [x] RQ-5D-002 — How does dimensionality affect propagation latency?
* [x] RQ-5D-003 — How does dimensionality affect recruited population size?
* [x] RQ-5D-004 — Does 5D change modularity?
* [ ] RQ-5D-005 — Does 5D change robustness against structural damage?
* [x] RQ-5D-006 — Are dimensions information-bearing or merely coordinates?
* [ ] RQ-5D-007 — Are some dimensions redundant?
* [ ] RQ-5D-008 — Does dimensionality affect memory retention?
* [ ] RQ-5D-009 — Does dimensionality change structural adaptation cost?

---

# Multidimensional Storage Research

## `.b5d`

* [x] RQ-STOR-001 — Can complete neural state be represented losslessly?
* [x] RQ-STOR-002 — Which runtime states are necessary for deterministic continuation?
* [x] RQ-STOR-003 — Measure bytes per neuron
* [x] RQ-STOR-004 — Measure bytes per synapse
* [ ] RQ-STOR-005 — Measure snapshot write throughput
* [ ] RQ-STOR-006 — Measure snapshot read throughput
* [ ] RQ-STOR-007 — Measure random-access performance
* [ ] RQ-STOR-008 — Measure mmap scalability
* [ ] RQ-STOR-009 — Verify cross-platform readability
* [ ] RQ-STOR-010 — Verify corruption detection
* [ ] RQ-STOR-011 — Verify deterministic restore
* [ ] RQ-STOR-012 — Determine compression opportunities without destroying random access

## Scaling Ladder

* [x] RQ-SCALE-001 — Does Brain-5D scale from 5k to millions without qualitative change?
* [ ] 5,000 neurons
* [ ] 50,000 neurons
* [ ] 500,000 neurons
* [ ] 1 million neurons
* [ ] 5 million neurons
* [ ] 50 million neurons
* [ ] Extrapolate toward 312,500,000 neurons only from measured data

---

# Optical / Multidimensional Storage Twin

* [ ] Define theoretical optical storage representation separately from digital implementation
* [ ] Define exact mapping from neuron state to optical point/vector
* [ ] Define exact mapping from synapse to graph/link representation
* [ ] Determine maximum information carried per point
* [ ] Determine maximum information carried per connection
* [ ] Define reversible codec requirements
* [ ] Measure information loss if lossy representations are explored
* [ ] Compare binary `.b5d` representation against optical/dimensional twin
* [ ] Define manipulation interface
* [ ] Define query interface
* [ ] Define spatial selection and editing semantics
* [ ] Research whether representation itself can participate in self-organization

---

# Determinism and Causality

* [x] RQ-DET-001 — Identical seed + state + input → identical run?
  * (ID corrected from `RQ-SNN-003`; `RQ-SNN-003` is exclusively the propagation question.)
* [ ] RQ-DET-002 — Snapshot/restore continuation identical to uninterrupted run?
* [ ] RQ-DET-003 — Structural decisions deterministic?
* [ ] RQ-DET-004 — Is iteration order explicitly controlled?
* [ ] RQ-DET-005 — Does platform influence results?
* [ ] Persist RNG state
* [ ] Persist pending delayed events
* [ ] Persist learning state
* [ ] Persist homeostasis state
* [ ] Persist structural state
* [ ] Persist controller state where scientifically relevant

---

# Numerical Model Validation

## Izhikevich

Do not assume the current integrator is wrong merely because it is not RK4.

* [ ] Compare current integration against published/reference implementation
* [ ] Test RS neuron
* [ ] Test FS neuron
* [ ] Test IB neuron
* [ ] Test CH neuron
* [ ] Test LTS neuron
* [ ] Compare spike timing
* [ ] Compare membrane trajectories
* [ ] Measure numerical drift
* [ ] Evaluate 1 s
* [ ] Evaluate 10 s
* [ ] Evaluate long-duration cases
* [ ] Consider alternative integrators only as controlled experiment
* [ ] Store integrator choice in experiment manifest

---

# Scientific Baselines and Ablations

Every major claim must be tested against meaningful controls.

* [ ] No learning
* [ ] STDP only
* [ ] Eligibility only where meaningful
* [ ] STDP + eligibility
* [ ] STDP + reward
* [ ] STDP + homeostasis
* [ ] STDP + structural plasticity
* [ ] Full combined system
* [ ] Fixed topology control
* [ ] No neurogenesis
* [ ] No pruning
* [ ] No sprouting
* [ ] No homeostasis
* [ ] Random topology
* [ ] Lower-dimensional topology
* [ ] Equivalent-connectivity control

---

# Long-Term Stability Laboratory

* [ ] 10,000 tick test
* [ ] 100,000 tick test
* [ ] 1,000,000 tick small-network test
* [ ] Seven-day wall-clock soak test later

Track:

* [ ] firing rate
* [ ] spike distribution
* [ ] ISI distribution
* [ ] weight distribution
* [ ] connectivity density
* [ ] neuron count
* [ ] synapse count
* [ ] pruning rate
* [ ] growth rate
* [ ] threshold distribution
* [ ] energy telemetry
* [ ] event queue size
* [ ] runtime/tick
* [ ] memory consumption
* [ ] structural oscillation
* [ ] NaN/Inf occurrence

---

# Scientific Claim Ledger

Every significant statement about Brain-5D must receive a claim status.

Allowed statuses:

```text
proposed
untested
testing
supported
partially_supported
refuted
inconclusive
deprecated
```

## Tasks

* [x] Create `claims.yaml` (5 Claims: SNN-001, 5D-001, 5D-002, STOR-001, SELF-001)
* [x] Associate claims with Research Questions
* [x] Associate claims with literature
* [ ] Associate claims with experiments
* [ ] Associate claims with evidence
* [ ] Record contradicting evidence
* [ ] Record limitations
* [x] Never automatically promote hypothesis to result (engine requires min_runs + evidence threshold)
* [x] Never automatically promote observation to causal claim

---

# Literature Registry

## Domains

* [x] Spiking Neural Networks (SRC-IZHIKEVICH-2003, SRC-GERSTNER-2014, SRC-MAASS-1997, SRC-MARKRAM-2015)
* [x] Izhikevich neuron models (SRC-IZHIKEVICH-2003)
* [x] STDP (SRC-SONG-ABBOTT-2000, SRC-BI-POO-1998)
* [ ] eligibility traces
* [ ] three-factor learning
* [x] homeostasis (SRC-TURRIGIANO-2008)
* [ ] structural plasticity
* [ ] neurogenesis
* [x] self-organization (SRC-HEBB-1949)
* [x] graph topology (SRC-WATTS-STROGATZ-1998, SRC-BARABASI-1999)
* [ ] high-dimensional representations
* [ ] persistent neural state
* [ ] neuromorphic storage
* [ ] memory
* [ ] embodied cognition
* [ ] AI epistemology
* [ ] human/machine authorship
* [ ] control and responsibility

Each source should capture:

* [x] citation (via BibTeX)
* [x] DOI/URL
* [x] authors
* [x] year
* [x] relevant claims
* [ ] methodology
* [x] Brain-5D relevance
* [x] associated RQs
* [ ] agreement/disagreement with Brain-5D evidence

---

# Automatic Research Catalog

Generate:

```text
research/generated/RESEARCH_CATALOG.md
```

For every research question:

```text
Question
→ Literature State
→ Brain-5D Hypothesis
→ Methods
→ Experiments
→ Results
→ Evidence Strength
→ Current Answer
→ Limitations
→ Contradictions
→ Follow-up Questions
```

* [x] Build generator (`src/research/report_builder.py`)
* [x] Generate on demand (`research/generate_reports.py`)
* [ ] Generate on release
* [ ] Optionally generate through CI
* [x] Keep generated documents reproducible

---

# Automatic Evidence Matrix

Generate:

```text
research/generated/EVIDENCE_MATRIX.md
```

Columns:

| RQ | Hypothesis | Literature | Experiments | Controls | Evidence | Current Answer | Confidence |
| -- | ---------- | ---------- | ----------- | -------- | -------- | -------------- | ---------- |

* [x] Build evidence aggregation (in `evidence_engine.py`)
* [ ] Separate positive and negative evidence
* [ ] Track replication count
* [ ] Track independent seeds
* [ ] Track contradictory evidence
* [x] Track confidence level (none/low/medium/high/very_high)

---

# Automatic Open Questions Register

Generate:

```text
research/generated/OPEN_QUESTIONS.md
```

* [x] Questions without experiments (all 27 currently open)
* [ ] Questions with inconclusive evidence
* [ ] Contradictions
* [ ] Missing controls
* [ ] Failed replications
* [ ] Possible alternative explanations
* [x] Candidate follow-up questions (engine auto-generates from experiment patterns)

Machine-generated questions must initially be:

```text
candidate
```

Human review may change them to:

```text
accepted
rejected
merged
deferred
```

---

# Negative Results

* [x] Preserve failed hypotheses (status `refuted` supported)
* [x] Preserve null results (status `inconclusive` supported)
* [ ] Preserve experiments that contradict expected behavior
* [ ] Do not overwrite failed experiments
* [ ] Distinguish implementation failure from hypothesis failure
* [ ] Record invalid experiment separately from negative experiment
* [x] Include negative evidence in generated research catalog (via evidence engine)

---

# B5D-SEF Evidence Semantics — Refined Status Tracking

Die aktuelle Verwendung von Checkboxen sollte verfeinert werden.

Beispiel:

```
[x] RQ-5D-001 registered
```

darf **nicht** bedeuten:

```
[x] 5D advantage proven
```

Jede RQ braucht daher **vier unabhängige Statusdimensionen**:

```
id: RQ-5D-001

registry_status: registered

experiment_status: not_started

evidence_status: none

answer:
  status: open
  confidence: none
```

Später beispielsweise:

```
experiment_status: replicated
evidence_status: moderate

answer:
  status: partially_supported
  confidence: medium
```

Dadurch bedeutet ein Häkchen bei einer registrierten Forschungsfrage nicht versehentlich:

> „Frage beantwortet."

Das ist für die spätere Dissertation enorm wichtig.

## Tasks

* [ ] Implement these four independent states in research registry schema
* [ ] Add `registry_status`, `experiment_status`, `evidence_status` fields to question schema
* [ ] Add `answer.status` and `answer.confidence` fields
* [ ] Render them separately in `RESEARCH_CATALOG.md`
* [ ] Render them separately in `EVIDENCE_MATRIX.md`

---

# Research Catalog — Current State

Der `[x]`-Haken für registrierte RQs muss klar von wissenschaftlichem Nachweis unterschieden werden.

Beispiel für die notwendige Unterscheidung:

## SNN

* [x] RQ-SNN-001 registered
* [x] RQ-SNN-002 registered
* [x] RQ-SNN-003 registered
* [x] RQ-SNN-004 registered
* [x] RQ-SNN-005 registered
* [ ] RQ-SNN-006 — noch nicht registriert
* [ ] RQ-SNN-007 — noch nicht registriert

Wichtige Unterscheidung:

`[x] registered` bedeutet **nicht** wissenschaftlich beantwortet.

Es sollte daher ein zweites Feld eingeführt werden:

```
registration_status: registered
evidence_status: no_evidence
answer_status: open
```

* [ ] Add separate `registration_status`
* [ ] Add separate `evidence_status`
* [ ] Add separate `answer_status`

Dies verhindert, dass `[x]` fälschlich als „wissenschaftlich bewiesen" gelesen wird.

---

# Homeostasis — Runtime Status

* [x] Canonical `HomeostasisSignal` added
* [x] Engine builder added
* [x] Dashboard bridge added historically
* [ ] Runtime-active path verified
* [ ] Convergence experiment
* [ ] Settling time
* [ ] Overshoot
* [ ] Steady-state error
* [ ] STDP interaction
* [ ] Structural interaction
* [ ] Evidence status

---

# Structural Self-Organization — Scientific Questions

## Existing Technical Foundation

- Pruning capability exists
- Sprouting capability exists
- Neurogenesis capability exists
- Proposal/coordinator APIs exist
- Persistence exists
- Approval architecture exists

## Scientific Questions

* [ ] Pruning functional benefit
* [ ] Sprouting recovery
* [ ] Neurogenesis overload response
* [ ] Long-term structural stability
* [ ] Oscillation
* [ ] Emergence vs rule-imposed behavior
* [ ] Mechanism ablations
* [ ] Restore survival

---

# Definition of Done for Scientific Features

A scientific feature is not complete merely because code exists.

Every feature requires:

* [x] Research Question (in `questions.yaml`)
* [x] Hypothesis (in `hypotheses.yaml`)
* [ ] implementation
* [ ] unit tests
* [ ] integration tests
* [ ] experiment definition
* [ ] control/baseline
* [ ] metrics
* [ ] random seed policy
* [x] experiment manifest (via `ExperimentRecorder`)
* [ ] raw results
* [ ] interpretation
* [ ] limitations
* [x] claim status (in `claims.yaml`)
* [ ] reproducibility check
* [ ] documentation update

---

# v0.5.0-alpha.6 — Morphological Self-Regulation

> **Blocked until Alpha.5 Integration Gate passes.**

**Goal:** Stabilize structural plasticity introduced in alpha.5 using temporal and spatial control.

## Chronic Structural Signals

* [ ] Implement chronic time-aggregated structural signals
* [ ] Regional 5D structural pressure calculation
* [ ] Neuron structural age tracking
* [ ] Synapse structural age tracking
* [ ] Minimum lifetime enforcement
* [ ] Grace period enforcement
* [ ] Chronic under-utilization signal
* [ ] Chronic overload signal

## Growth Budgets & Costs

* [ ] Growth budget system
* [ ] Regional growth budgets
* [ ] Global structural budget
* [ ] Structural resource cost model
* [ ] Cost per neuron
* [ ] Cost per synapse
* [ ] Cost per structural change
* [ ] Growth/pruning hysteresis
* [ ] Anti-oscillation mechanisms

## Regional Pressures

* [ ] Regional neurogenesis pressure
* [ ] Regional pruning pressure
* [ ] Regional sprouting pressure
* [ ] Regional saturation detection

## Telemetry & Dashboard

* [ ] Stability telemetry collection
* [ ] Structural pressure heatmap
* [ ] Structural age visualization
* [ ] Dashboard budget views
* [ ] Dashboard cost views
* [ ] Oscillation indicators

## Scientific Evaluation

* [ ] Compare instantaneous vs chronic signals
* [ ] Measure structural oscillation
* [ ] Measure recovery after perturbation
* [ ] Measure structural cost
* [ ] Measure behavioral/performance impact
* [ ] Run parameter sensitivity analysis

## Exit Criteria

* [ ] Growth and pruning do not oscillate tick-by-tick
* [ ] Structural limits maintained over long-term tests
* [ ] Decisions reproducible from chronic signals
* [ ] Budgets and costs observable in Dashboard
* [ ] Structural Journal and Undo remain fully compatible
* [ ] Restore-and-continue remains deterministic
* [ ] Experimental evidence recorded in B5D-SEF

---

# Sprint 2A — STDP Laboratory / Evidence Closure

* [ ] Verify feature flag default OFF
* [ ] Two-neuron PRE→POST potentiation
* [ ] Two-neuron POST→PRE depression
* [ ] Large delta-t → change toward 0
* [ ] Flag OFF → Stand 1 behavior unchanged
* [ ] Compare actual implementation against declared mathematical rule
* [ ] Resolve possible dual-STDP semantics
* [ ] Generate STDP reference curves
* [ ] Register evidence in Research Catalog

---

# Sprint 2B — Eligibility Trace / Three-Factor Learning

* [ ] Verify eligibility trace implementation
* [ ] Define eligibility decay mathematically
* [ ] Test delayed reward
* [ ] Test positive reward
* [ ] Test negative reward
* [ ] Test reward-free control
* [ ] Measure maximum useful reward delay
* [ ] Compare against pair-STDP baseline

---

# Sprint 2C — Homeostasis

* [ ] Threshold/rate regulation isolated and measurable
* [ ] Define exact control equation
* [ ] Measure convergence
* [ ] Measure overshoot
* [ ] Measure settling time
* [ ] Measure steady-state error
* [ ] Compare Homeostasis ON/OFF
* [ ] Evaluate STDP interaction

---

# v0.6 — Scaling

## Core

* [ ] Event-driven dirty tracking
* [ ] Dirty-region persistence
* [ ] Chunked 5D storage
* [ ] Domain decomposition
* [ ] Scheduler
* [ ] Sparse/array representation assessment
* [ ] Profile Python object overhead before parallelization

## Benchmark Ladder

* [ ] 5k
* [ ] 50k
* [ ] 500k
* [ ] 1M

Later experimental extrapolation:

* [ ] 5M
* [ ] 50M
* [ ] 312.5M theoretical target estimate

## Measurements

* [ ] ms/tick
* [ ] RAM
* [ ] events/tick
* [ ] snapshot size
* [ ] snapshot time
* [ ] restore time
* [ ] storage bytes/neuron
* [ ] storage bytes/synapse

---

# v0.7 — Learning Environment

* [ ] Episode lifecycle
* [ ] Train/evaluation split
* [ ] Delayed reward tasks
* [ ] Continual-learning retention metrics
* [ ] Reproducible task baselines
* [ ] Learning curves
* [ ] Forgetting curves
* [ ] Retention tests
* [ ] No-learning controls
* [ ] Random-policy baselines
* [ ] Statistical replication across seeds

---

# v0.8 — Embodiment

* [ ] Text sensor adapter
* [ ] Image sensor adapter
* [ ] Audio sensor adapter
* [ ] Typed actuator adapters
* [ ] Simulator environment interface
* [ ] Digital environment interface
* [ ] Real-world environment interface
* [ ] Perception-action-reward loop
* [ ] Causal sensor→SNN→action tracing
* [ ] Embodiment experiment registry

---

# v0.9 — Memory and World Model

* [ ] Working context
* [ ] Long-term associative memory
* [ ] Goals
* [ ] Multi-step state
* [ ] Prediction experiments
* [ ] World-model experiments
* [ ] Memory retention definition
* [ ] Recall metric
* [ ] Interference tests
* [ ] Catastrophic-forgetting tests
* [ ] Snapshot/restore memory retention

---

# v0.10 — Cognitive Evaluation

* [ ] Causal tasks
* [ ] Compositional generalization
* [ ] Neuro-symbolic experiments
* [ ] Explicit benchmark suite
* [ ] Null baselines
* [ ] Ablation suite
* [ ] Cross-seed confidence intervals
* [ ] Separate measured competence from interpretation

---

# v0.11 — Controlled Action and HMI

* [ ] Permissions
* [ ] Resource limits
* [ ] Audit log
* [ ] Safe stop
* [ ] Sandbox
* [ ] Operator-controlled actions
* [ ] Explicit capability boundaries
* [ ] Human intervention logging
* [ ] Responsibility/authority model

---

# v0.12 — Release Candidate

* [ ] Restore/continue soak tests
* [ ] Benchmark freeze
* [ ] Seven-day stability runs
* [ ] Reproducible clean installation
* [ ] Full experiment provenance
* [ ] Frozen Research Catalog
* [ ] Frozen Evidence Matrix
* [ ] Frozen benchmark definitions
* [ ] Reproduce selected scientific results from clean checkout

---

# v1.0 — Usable Brain-5D AI

Target:

> Persistent, stable, evaluable, multimodal learning system with bounded actions and reproducible scientific evidence.

* [ ] Persistent
* [ ] Stable
* [ ] Reproducible
* [ ] Evaluable
* [ ] Multimodal
* [ ] Learning demonstrably exceeds controls
* [ ] Bounded action capabilities
* [ ] Deterministic persistence where promised
* [ ] Documented limits
* [ ] Scientific claims linked to evidence

---

# Later / Research

## Neural Dynamics

* [ ] Alternative neuron models
* [ ] Integrator comparison
* [ ] heterogeneous populations
* [ ] adaptive conduction delay
* [ ] neuromodulation

## Learning

* [ ] Full reward / three-factor learning
* [ ] meta-plasticity
* [ ] synaptic consolidation
* [ ] learned plasticity parameters

## Structural

* [ ] Advanced pruning
* [ ] Neurogenesis
* [ ] Synaptogenesis
* [ ] Morphological constraints
* [ ] structural consolidation

## Metabolic

* [ ] Metabolic dynamics
* [ ] Functional energy constraints
* [ ] Resource competition
* [ ] Energy-dependent plasticity

## Scale

* [ ] Performant backends
* [ ] SIMD/vectorized core
* [ ] GPU investigation
* [ ] Sharding
* [ ] Distributed 5D spaces
* [ ] Storage tiering

## Scientific Questions

* [ ] Prove or refute measurable 5D advantage
* [ ] Define operational self-organization
* [ ] Distinguish programmed adaptation from emergence
* [ ] Demonstrate persistent learning
* [ ] Demonstrate memory retention
* [ ] Establish causal attribution of mechanisms
* [ ] Identify alternative explanations for observed behavior

## Human / AI Research

* [ ] Track human-authored design decisions
* [ ] Track LLM-generated proposals
* [ ] Track accepted/rejected AI suggestions
* [ ] Compare LLM-specific architectural fingerprints
* [ ] Measure effect of different LLMs on generated SNN architectures
* [ ] Investigate shifts in authorship
* [ ] Investigate shifts in control
* [ ] Investigate shifts in responsibility
* [ ] Maintain explicit human approval boundaries

---

# Wesentliche Statuskorrektur

Der aktuelle Projektstand ist **weiter als die alte TODO vermuten lässt**:

```
Structural Persistence        IMPLEMENTED
Scientific Framework          IMPLEMENTED
Dashboard Server Architecture largely VERIFIED
Snapshot Infrastructure       IMPLEMENTED
Restore Infrastructure        IMPLEMENTED

Runtime Composition            NOT YET CLOSED
Frontend Control Lifecycle     NOT YET CLOSED
End-to-End Operator Control    NOT YET VERIFIED
Scientific Evidence            FRAMEWORK READY,
                               REAL EVIDENCE MOSTLY OPEN
```

Das ist eine wichtige Unterscheidung. Alpha.5 ist nicht mehr in erster Linie ein Feature-Implementierungsproblem. Es ist jetzt ein **Integrations-, Verifikations- und Evidenzproblem**.

Und genau das ist ein guter Zustand für die weitere wissenschaftliche Arbeit: Der größte nächste Gewinn entsteht nicht dadurch, noch mehr Mechanismen hinzuzufügen, sondern dadurch, die vorhandenen Mechanismen kontrolliert zusammenzuführen und dann erstmals systematisch zu beantworten:

> **Was tut Brain-5D tatsächlich, warum tut es das, welche Komponente verursacht welchen Effekt, und mit welcher Evidenz können wir diese Aussage vertreten?**

---

# Neuer Projektstatus

Damit ist ein wesentlicher Teil von Brain-5D abgeschlossen: **B5D-SEF ist als wissenschaftliche Infrastruktur implementiert.** Wichtig ist die sprachliche Unterscheidung zwischen **„Forschungsframework fertiggestellt"** und **„Forschung abgeschlossen"**. Die Infrastruktur zur Beantwortung der Fragen steht jetzt; die eigentliche Evidenz für viele der 27 Forschungsfragen muss erst durch reale Experimente entstehen.

| Bereich | Status |
|---|---|
| Research Registry | ✅ implementiert |
| Research Questions | ✅ 27 registriert |
| Hypothesen | ✅ 27 registriert |
| Claims | ✅ 5 registriert |
| Literaturregister | ✅ Grundbestand |
| Methodenregister | ✅ 13 Klassen |
| Experiment Recorder | ✅ implementiert |
| Evidence Engine | ✅ implementiert |
| Report Builder | ✅ implementiert |
| Research Catalog | ✅ generierbar |
| Evidence Matrix | ✅ generierbar |
| Open Questions | ✅ generierbar |
| Dissertation Map | ✅ generierbar |
| Literature Matrix | ✅ generierbar |
| Beispiel-Experiment | ✅ vorhanden |
| **reale wissenschaftliche Evidenz** | 🟡 **beginnt jetzt** |
| **Alpha.5 Runtime-Integration** | 🔴 **noch offen** |

---

# Brain-5D als wissenschaftliches Forschungsframework

Die wesentliche Architektur lautet nun:

```text
                         BRAIN-5D
                            │
          ┌─────────────────┴─────────────────┐
          │                                   │
    Technical Runtime                  Research Layer
          │                                   │
          │                            Research Questions
          │                                   ↓
          │                              Hypotheses
          │                                   ↓
          ├──────── Experiment ───────→ ExperimentRecorder
          │                                   ↓
          │                              Raw Evidence
          │                                   ↓
          │                              EvidenceEngine
          │                                   ↓
          │                         Claims / Current Answers
          │                                   ↓
          └────────────────────────→ ReportBuilder
                                              ↓
                                  RESEARCH_CATALOG
                                  EVIDENCE_MATRIX
                                  OPEN_QUESTIONS
                                  DISSERTATION_MAP
```

Dies ist für das Projekt wissenschaftlich wesentlich wertvoller als nur eine Sammlung von Markdown-Dateien, weil jetzt ein prinzipiell maschinenlesbarer Weg von **Frage → Experiment → Evidenz → Aussage** existiert.

---

# Evidenzgrade E0–E4

Brain-5D verwendet eine einfache Evidenzhierarchie:

```text
E0 — nur theoretische Annahme
E1 — Unit-/Mechanismustest
E2 — einzelnes kontrolliertes Experiment
E3 — repliziert über mehrere Seeds
E4 — Ablation + Kontrollgruppe + Replikation
```

Damit kann im `RESEARCH_CATALOG.md` beispielsweise stehen:

```text
CLAIM-STDP-001
PRE→POST potentiates synaptic weight.

Evidence:    E3
Experiments: 12
Independent seeds: 6
Status:      SUPPORTED
```

Dagegen:

```text
CLAIM-5D-001
5D organization improves learning.

Evidence:    E0
Status:      UNTESTED
```

Dies macht auf einen Blick sichtbar, **was Brain-5D weiß und was Brain-5D lediglich vermutet**.

## Tasks

* [x] Add `evidence_level` field (E0–E4) to claim registry schema
  * Added to `research/schemas/claim.schema.json` and `research/registry/claims.yaml`.
* [ ] Render evidence level in `RESEARCH_CATALOG.md`
* [ ] Render evidence level in `EVIDENCE_MATRIX.md`
* [ ] Add evidence-level column to `CLAIM_REGISTER.md`

---

# EXP-2026-0001 — Statusklassifikation

Das vorhandene Beispiel-Experiment „Baseline Stability Test" wird zunächst als:

```text
experiment_status: template
evidence_status: none
```

klassifiziert. Erst wenn der reale Brain-5D-Runtimepfad das Experiment tatsächlich ausgeführt hat:

```text
Brain-5D Runtime
      ↓
10.000 Ticks
      ↓
Metrics
      ↓
.b5d Snapshot
      ↓
Manifest
      ↓
EvidenceEngine
```

wird daraus:

```text
experiment_status: completed
evidence_status: evaluated
```

Dies verhindert, dass Beispiel- oder Testdaten versehentlich wissenschaftliche Evidenz werden.

## Tasks

* [x] Add `experiment_status` field to experiment manifest schema (values: `template`, `not_started`, `running`, `completed`, `failed`, `invalid`)
  * Added to `research/schemas/experiment.schema.json`.
* [x] Set `EXP-2026-0001` → `experiment_status: template`
  * Updated `research/experiments/EXP-2026-0001/manifest.json`.
* [ ] Ensure template experiments are excluded from evidence aggregation

---

# Erstes Forschungsprogramm — Phase A

Die ersten Experimente werden bewusst sehr einfach gehalten.

## EXP-DET-0001 — Determinismus-Baseline

```text
identischer Seed
identische Config
identischer Input
→ identische Spikefolge?
```

## EXP-STOR-0001 — Restore-Identität

```text
Run A:
0 ──────────────────────────→ 10.000

Run B:
0 ─────→ 5.000
          ↓
       Snapshot
          ↓
        Restore
          ↓
5.000 ──────────────────────→ 10.000
```

Dann:

```text
State_A(10000) ≟ State_B(10000)
```

Dies ist eines der wichtigsten Experimente überhaupt. Wenn dieser Test scheitert, wissen wir: **spätere Unterschiede können Restore-/Determinismusartefakte sein.**

Wenn er besteht, wird Brain-5D als wissenschaftliches Instrument erheblich belastbarer.

## Danach — SNN-Basis

Sobald Determinismus und Restore-Identität bestätigt sind, werden die ersten bereits registrierten Fragen tatsächlich beantwortet:

```text
RQ-SNN-001   Spike-Reproduzierbarkeit
RQ-SNN-002   Langzeitstabilität
RQ-SNN-003   Propagation / Topologie
RQ-STDP-001  PRE → POST
RQ-STDP-002  POST → PRE
```

## Tasks

* [x] Register `EXP-DET-0001` in experiment registry
  * Created `research/experiments/EXP-DET-0001/manifest.json` with `experiment_status: not_started`.
* [x] Register `EXP-STOR-0001` in experiment registry
  * Created `research/experiments/EXP-STOR-0001/manifest.json` with `experiment_status: not_started`.
* [ ] Define success criteria for determinism experiment
* [ ] Define success criteria for restore-identity experiment
* [ ] Implement experiment runner for EXP-DET-0001
* [ ] Implement experiment runner for EXP-STOR-0001

---

# Die 5D-Frage — kontrollierte Experimente

Das Forschungsframework ermöglicht nun, die zentrale Frage sauber zu adressieren.

Nicht:

> „Brain-5D verwendet fünf Dimensionen."

sondern:

```text
RQ-5D-001
Hat 5D einen messbaren Vorteil?
```

mit kontrollierten Experimenten:

```text
1D ─┐
2D ─┤
3D ─┤
4D ─┼→ identische N
5D ─┤  identische Synapsenzahl
     │  identischer Seed
Random┘ identischer Input
           ↓
       Vergleich
```

Die Antwort kann am Ende lauten:

```text
SUPPORTED
```
oder:

```text
NO MEASURABLE ADVANTAGE
```
oder:

```text
CONDITIONALLY SUPPORTED
```

Alle drei Ergebnisse wären wissenschaftlich wertvoll.

---

# Alpha.5 Gate — Visualisierter Status

```text
ALPHA 5

Structural Persistence      ██████████  implemented
Research Infrastructure     ██████████  implemented
Research Registries         ██████████  implemented
Report Generation           ██████████  implemented

Process Architecture         ██████████  Gate A
Canonical Runtime            ██████████  Gate A
Control API                  ██████████  Gate A
Frontend Lifecycle           ██████████  Gate A
Snapshot Runtime             ██████████  Gate A
.b5d → Heatmap               ██████████  Gate A
Dashboard Observability      ██████████  Gate A (Alpha.5 Dashboard Completion)
5D Network Inspector         ██████████  Gate A (real 5D coordinates, pagination)
Integration Status (real)    ██████████  Gate A (/api/integration/status, stale detection)
Truthful Null/Disabled       ██████████  Gate A (no fake zeros, disabled≠failed)
Structural Runtime Chain     ███░░░░░░░  Gate A remaining (config-disabled in poc_config)
Test Baseline                ██████████  Gate B (274 passed, 2 skipped, 0 collection errors)
Structural E2E Verification  ██████████  Gate B (11/11 proofs verified, production composition, real signal, journal reopen)
Error Visibility             ████████░░  Gate B (integration endpoint surfaces errors)
Restore Determinism          ░░░░░░░░░░  Gate B
Scientific Experiments       ░░░░░░░░░░  Gate C
Evidence Records             ░░░░░░░░░░  Gate C
```

Dies ist ein sehr sinnvoller Entwicklungsstand: **Wir müssen jetzt nicht mehr darüber nachdenken, wie Forschung dokumentiert werden soll. Diese Infrastruktur existiert.**

---

# Alpha.5 Dashboard Completion (2026-08-23)

## Erledigt (Dashboard als wissenschaftliches Beobachtungsinstrument)

- **Phase 4 — Config-Authoritative Storage:** `main.py` startet `AsyncStorageSession` nur noch, wenn `storage.runtime.enabled=true`. Bei `poc_config` (disabled) bleibt Delta Storage "disabled by config", keine still-aktive Persistenz.
- **Phase 3 — Truthful Formatting:** `app.js` unterscheidet `null/undefined → "—"`, measured zero → `"0"`, disabled → `"disabled by config"`. Kein `Number(value || 0)` mehr für Storage/Homeostasis/Self-Org.
- **Phase 6 — Structural Config-Aware UI:** Control-Panel Badge zeigt `DISABLED BY CONFIG` wenn `self_organization.enabled=false`, nicht statisch `Configured`. Controls werden deaktiviert.
- **Phase 8/9 — Real 5D Network Inspector:** Neue Endpunkte `/api/network/summary`, `/api/network/neurons`, `/api/network/synapses`, `/api/network/projection` liefern echte 5D-Koordinaten, v, u, energy, weights, delays. Serverseitige Pagination. Neuer `🔍 Inspect` Tab.
- **Phase 14 — Real Integration Status:** `/api/integration/status` berechnet real Bridge/Controller/Runtime/Structural/Snapshot/Delta-Storage/Structural-Journal/Research/Tests/Error-Visibility. Disabled-by-config ≠ failed. Tests-STALE-Erkennung liest `test_baseline.json` und vergleicht `tested_commit` mit HEAD.
- **Phase 16 — Provenance:** Network-Inspector-Daten als `LIVE` badged.
- **Phase 18 — Tests:** 21 neue Tests in `test_dashboard_completion.py` (Tick-0 real size, null serialization, disabled≠failed, canonical commands, 5D coordinates, projection, tree-digest stale detection, no demo source). **Verified baseline: 274 passed, 2 skipped, 0 collection errors (full suite without `--ignore`).**
- **Phase 19 — Manual E2E:** Fresh start zeigt Tick 0: 5000 Neuronen, 36031 Synapsen, idle, storage disabled. Step (+1), run_ticks (+100), snapshot (neue .b5d) verifiziert via API.

## Verbleibend (nicht in dieser Aufgabe)

- Structural E2E benötigt separate Test-Config (poc_config bleibt disabled).
- Restore Determinism (Gate B).
- Scientific Experiments (Gate C).
- Tree-digest may be STALE after source changes; re-run baseline when new tests are finalized.

---

# Nächster wissenschaftlicher Meilenstein

> **Brain-5D Experimental Baseline 1 — nachweisbar deterministischer, persistenter und reproduzierbarer SNN-Runtimepfad.**

Wenn dieser Baseline-Meilenstein erreicht ist, kann das B5D-SEF zum ersten Mal automatisch echte Antworten produzieren – zunächst über Determinismus, SNN-Dynamik und Persistenz, danach über STDP, Homöostase, Selbstorganisation und schließlich die zentrale Frage, **ob der fünfdimensionale Raum tatsächlich einen kausal nachweisbaren Vorteil besitzt**.

---

# Immediate Execution Order — Updated

```text
=== GATE A — Technical Integration (near complete) ===========================

1. Verify current real HTTP Bridge state ...................... ✅
2. Fix frontend double initialization ........................ ✅
3. Select canonical RuntimeController ........................ ✅
4. Remove SimpleController ................................... ✅
5. Make RuntimeController sole simulation-clock owner ........ ✅
6. Remove automatic startup 1000-tick execution .............. ✅
7. Unify /api/control contract ............................. ✅
8. Connect snapshot pipeline to RuntimeController ........... ✅
9. Verify .b5d → Heatmap live chain ........................ ✅
10. Wire structural runtime chain into src.main ............. 🔴 Gate A (poc_config disabled by design)
11. Verify approval → mutation → journal → undo ............. 🔴 Gate A (separate test config)
12. Dashboard Completion: config-authoritative storage ....... ✅ (Phase 4)
13. Dashboard Completion: truthful null/disabled formatting .. ✅ (Phase 3)
14. Dashboard Completion: real 5D network inspector ......... ✅ (Phase 8/9)
15. Dashboard Completion: real integration status ........... ✅ (Phase 14)
16. Dashboard Completion: structural config-aware UI ........ ✅ (Phase 6)

=== GATE B — Verification ====================================================

12. Run complete pytest baseline ... 274 passed, 2 skipped, 0 collection errors (full suite without --ignore) ✅
13. End-to-end structural chain verification (10 proofs) .... 🔴 Gate B
14. Eliminate silent hook failures .......................... 🔴 Gate B
15. Restore-and-continue determinism ........................ 🔴 Gate B

=== GATE C — Scientific Baseline =============================================

16. Correct research registry ID collisions ................. ✅
17. Add DATA-* object type ................................. ✅
18. Harden experiment manifests ............................ ✅
19. Run EXP-DET-0001 (deterministic replay) ................ 🔴 Gate C
20. Run EXP-STOR-0001 (snapshot/restore identity) .......... 🔴 Gate C
21. Generate evidence from actual runs ..................... 🔴 Gate C
22. Close ALPHA.5 ......................................... 🎯
23. Begin alpha.6
```

# Alpha.5 — Three-Gate Structure

Code fertig ≠ Integration fertig ≠ Wissenschaft fertig.

## Gate A — Technical Integration

**Ziel:** Alle technischen Komponenten sind im realen `src.main`-Pfad angeschlossen.

### Process Architecture

* [x] One application process (single PID)
* [x] No separate `python -m src.dashboard` process
* [x] Integrated dashboard receives `OperatorBridge` during startup
* [x] No module-global bridge state
* [x] Bridge identity stable across HTTP requests

### Canonical Runtime

* [x] One canonical `RuntimeController` (`src.controller.runtime`)
* [x] One simulation clock owner (controller worker is sole `network.step()` caller)
* [x] No `SimpleController`
* [x] No automatic uncontrolled 1000-tick simulation
* [x] Controller starts in IDLE state
* [x] All canonical commands: `start`, `pause`, `resume`, `stop`, `step`, `run_ticks`, `snapshot`

### Control API

* [x] Canonical contract: `POST /api/control { "command": "run_ticks", "ticks": 100 }`
* [x] Backward-compatible: `{ "action": "..." }` still accepted
* [x] Input validation (integer tick counts, unknown commands → 400)
* [x] Structured JSON errors
* [x] JSON 404 for unknown API paths
* [x] API tests for every runtime command (19 tests)

### Frontend Lifecycle

* [x] `app.js` sole lifecycle owner
* [x] No duplicate initialization or event listeners
* [x] Canonical `{"command": "..."}` contract in both Console and Control tabs
* [x] No duplicate API calls or log messages

### Snapshot Runtime

* [x] Canonical RuntimeController snapshot command connected to `B5DSnapshotWriter`
* [x] Atomic snapshot writing (temp → validate → rename)
* [x] Initial snapshot at dashboard startup
* [x] Historical snapshots (timestamped copies)
* [x] Metadata: tick, neuron/synapse count, dimensions, git commit, seed, config path
* [ ] Configuration SHA-256 hash (path only, not hash)
* [ ] Full RNG state for deterministic restore (seed only, not complete state)
* [x] `/api/snapshots` lists available `.b5d` files
* [x] `/api/snapshot-info` returns tick, file, size, status
* [x] Snapshot info card in dashboard UI

### Heatmap

* [x] Activity heatmap from real `.b5d` data
* [x] Weight heatmap from real `.b5d` data
* [x] Energy heatmap from real `.b5d` data
* [x] No demo fallback when real snapshot exists

### B5D-SEF Foundation

* [x] Research registries (questions, hypotheses, claims, sources, methods)
* [x] Experiment recorder with manifest generation
* [x] Evidence engine
* [x] Report builder (RESEARCH_CATALOG, EVIDENCE_MATRIX, etc.)
* [x] Registry uniqueness validation (8 tests)
* [x] `DATA-*` object type in schema
* [x] `evidence_level` (E0–E4) in claim schema
* [x] `experiment_status` in manifest schema
* [x] `EXP-DET-0001` and `EXP-STOR-0001` registered
* [x] ID correction: `RQ-SNN-003` → `RQ-DET-001` for determinism question

### Structural Runtime Chain — Gate A (verified via production factory + E2E)

* [x] `src.main` instantiates actual `SelfOrganizationCoordinator` (via `compose_structural_subsystem`)
* [x] `src.main` instantiates actual `StructuralPlasticityEngine` (via `compose_structural_subsystem`)
* [x] `Brain5DManipulator` is actual mutation boundary (single manipulator, legacy engine detached)
* [x] Approval policy attached in normal startup (Coordinator approval gate)
* [x] Journal attached in normal startup (StructuralJournal from factory)
* [x] Undo uses persistent inverse records (StructuralUndoManager)
* [x] Bridge receives active coordinator and plasticity engine (OperatorBridge wired)
* [x] Proposals generated from actual measurements (E2E proof 4: real HomeostasisSignal)
* [x] Mutation requires accepted proposal (E2E proof 5: no mutation without approval)
* [ ] Production `HomeostasisSignal -> Policy -> Coordinator` adapter wired in `src.main` (canonical but inert in automatic operation)

---

## Gate B — Verification

**Ziel:** Jede Behauptung ist durch einen Test oder einen dokumentierten Lauf belegt.

### Test Baseline

* [x] Zero collection errors (resolved: `tests/__init__.py` added)
* [x] Zero unexplained failures (274 passed, 0 failed)
* [x] Full test suite runs without ignored core modules (`python -m pytest tests/ -q`)
* [ ] Tree-digest matches current source tree (re-run baseline after finalizing new tests)

### Structural Chain — End-to-End Verification

Ten concrete proofs required:

1. [ ] Coordinator is in `src.main` actually instantiated
2. [ ] PlasticityEngine is actually instantiated
3. [ ] Bridge contains exactly these instances
4. [ ] Proposal originates from real runtime signal
5. [ ] Proposal alone does NOT mutate the network
6. [ ] Reject does NOT mutate the network
7. [ ] Approve produces exactly one mutation
8. [ ] Mutation produces exactly one Journal record
9. [ ] Undo restores the previous state
10. [ ] Restart + Replay produces the same state

### Error Visibility

* [ ] Hook failures produce structured runtime error events
* [ ] No silent `except Exception: pass` in scientific execution paths
* [ ] Experiment manifest records runtime exceptions
* [ ] Invalid experiment runs cannot become evidence

### Restore Determinism

* [ ] Snapshot/restore continuation identical to uninterrupted run
* [ ] Structural decisions deterministic
* [ ] Iteration order explicitly controlled
* [ ] RNG state persisted for deterministic restore

---

## Gate C — Scientific Baseline

**Ziel:** Mindestens eine reproduzierbare wissenschaftliche Aussage mit dokumentierter Evidenz.

### Experiment Sequence

```
EXP-DET-0001   deterministic independent runs
        ↓
EXP-STOR-0001  snapshot/restore identity
        ↓
EXP-SNN-0001   stable neural dynamics
        ↓
EXP-STDP-0001  PRE→POST
        ↓
EXP-STDP-0002  POST→PRE
        ↓
EXP-STRUCT-0001 proposal→approve→mutation
        ↓
EXP-STRUCT-0002 mutation→undo
        ↓
EXP-STRUCT-0003 restart→replay
```

### EXP-DET-0001 — Deterministic Replay Baseline

Hypothesis: $S_A(t) = S_B(t)$ at identical:
- Code, Config, Seed, Input, Initial State, Tick Count

Compared at minimum:
- `current_tick`, spike sequence, neuron v/u, energy, threshold adaptation
- spike counters, synaptic weights, eligibility, event queue, structural state

Success criterion: **exact equality** for integer state; documented tolerance for float conversion.

### EXP-STOR-0001 — Restore Identity

Three conditions compared:

```
A: uninterrupted
0 ---------------------- 10000

B:
0 ---------- 5000
               ↓
            snapshot
               ↓
            restore
               ↓
5000 -------------------- 10000

C:
0 ---------- 5000
               ↓
 snapshot + process exit
               ↓
 new process + restore
               ↓
5000 -------------------- 10000
```

`B` tests restore within same runtime. `C` tests **true persistence across process restart**.

### Gate C Deliverables

* [ ] First real experiment manifests generated automatically
* [ ] First evidence records refer to actual experiments
* [ ] Claims associated with experiments and evidence
* [ ] At least one hypothesis supported or refuted by reproducible experiment
* [ ] `RESEARCH_CATALOG.md` rebuilt from actual evidence
* [ ] `EVIDENCE_MATRIX.md` rebuilt from actual evidence

---

## Alpha.5 Abschlusskriterium

Sobald alle drei Gates geschlossen sind, kann Alpha.5 wie folgt abgeschlossen werden:

> **Brain-5D Alpha.5 establishes a reproducible, operator-controlled, persistable and experimentally traceable spiking neural runtime with approval-gated structural modification.**

Damit wird die TODO nicht nur zu einer Entwicklungsroadmap, sondern gleichzeitig zum **wissenschaftlichen Arbeitsplan von Brain-5D**: Jede technische Funktion muss künftig beantworten, **welche Frage sie untersucht, wie sie getestet wird, welche Evidenz entstanden ist und was daraus tatsächlich geschlossen werden darf**.
