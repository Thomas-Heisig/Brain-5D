# Changelog

## Unreleased

### Added

- **Scientific Research Assistant v0**: A separate read-only assistant builds
  deterministic `ResearchPacket` inputs and stores schema-validated `AIAR-*`
  records under `research/analysis/`. Its optional local Ollama adapter returns
  interpretation JSON only; it cannot execute experiments, alter runtime or
  registry state, create evidence, or answer research questions. Every record
  carries prompt and input digests and requires human review.
- **AI-assisted research foundation**: `RQ-AIR-001`, `H-AIR-001-A`, and
  `CLAIM-AIR-001` now define a structured-versus-unstructured methodological
  review study. `AIR-METHODOLOGY-GOLD-V1` provides 30 held-out, labelled cases;
  no model has received the labels and no benchmark evidence has been created.
- **AIR benchmark safeguards**: The pre-registered `EXP-AIR-0001` protocol
  denies assistant access to gold labels, includes 21 defective and 9 negative
  control cases, and requires three repetitions per case/condition with frozen
  SHA, external CI success, and full model/sampling provenance before execution.

- **Research Experiment Runner**: The RESEARCH workspace now provides the
  traceable workflow Forschungsfrage -> Bedingungen -> Experiment ->
  Ausfuehren -> Bericht -> Ergebnis. A run validates research-question and
  hypothesis links against the registry, permits only bounded
  `controller.step(ticks)` execution, and writes `workflow.json`,
  `manifest.json`, and `report.md` under `research/experiments/EXP-*/`.
  Optional Ollama assistance has no execution, configuration, or evidence
  authority.
- **First registered STDP pilot**: `EXP-STDP-0001` ran the deterministic
  `stdp_pair_timing_v1` protocol with 11 timing conditions and 10 identical
  repeated evaluations each. It produced `DATA-2026-17` and a detailed pilot
  report, but no EVID: the source tree was dirty and the evaluations were not
  independent runs. Evidence generation now fails closed for dirty Git trees
  and distinguishes deterministic verification from stochastic and
  observational experiments.

## v0.5.0-alpha.5 - Dashboard State & Health Repair (2026-08-30)

### Fixed

- **Dashboard offline / stale PID**: `artifacts/brain5d.pid` wurde nicht
  bereinigt, wenn der Prozess extern beendet wurde. Der Port war blockiert
  durch einen verwaisten Prozess. Empfohlene Abhilfe: Prozess hart beenden
  und neu starten; `stop.cmd` wurde verbessert, indem es den Fehlerfall
  robuster meldet.
- **Checkpoint-Tests**: `MockNeuron` in `tests/test_checkpoint_v4.py`,
  `tests/test_rng_persistence.py` und die lokale `Neuron`-Klasse in
  `tests/test_checkpoint.py` fehlten Felder, die `capture_runtime_checkpoint`
  seit Checkpoint v4 erwartet (`firing_rate_estimate`, `_spike_count_window`,
  `_last_update_tick`, `pre_trace`, `post_trace`). Alle 452 Tests laufen
  jetzt grün.
- **Dashboard Health unavailable**: Veröffentlichte Snapshots wurden nicht
  mit `enrich_snapshot()` angereichert, daher blieb `health.overall`
  auf `unknown`. `publish_state()` reichert jetzt automatisch Components,
  Parameters und Health an; `src/main.py` übergibt die Runtime-Config an
  den StateManager.
- **Health-State-Semantik**: `enabled ≠ active` und
  `unavailable ≠ disabled` werden jetzt korrekt unterschieden. Learning,
  Homeostasis, Structural und Storage lesen `enabled` aus der Config und
  `active` aus den Runtime-Metriken. Deaktivierte Komponenten melden
  `disabled` mit `source: config`.
- **Neuer API-Endpoint**: `/api/state` liefert den vollständigen
  angereicherten Dashboard-Snapshot für den Frontend-StateStore.

## v0.5.0-alpha.5 - Dashboard Operator-Workbench Design Decision (2026-08-30)

### Planned

- Dashboard architecture decision recorded in `docs/07-changelog/CHANGELOG.md`:
  workflow-oriented operator workbench (`OVERVIEW | NETWORK | CONTROL | RESEARCH | VERIFY`)
  with `StatusModel`, `StateStore`, `ParameterSchema`, `Health/Problems Drawer`,
  unified Control/Console, pending-changes workflow, experiment mode, and
  domain-driven frontend modularization.
- See `docs/08-roadmap/TODO.md` and `docs/08-roadmap/ROADMAP.md` for detailed task list
  and alpha.6 milestone scope.

## v0.5.0-alpha.5 - Scientific Verification Infrastructure (2026-08-26)

### Added

- **Scientific error integrity** (Phase 1):
  - `ExperimentRecorder.record_runtime_error()` — captures structured RuntimeErrorEvents
  - `ExperimentRecorder.mark_completed()` / `mark_failed()` — explicit status semantics
  - `validity` field in manifest: `valid`, `reason`, `runtime_error_count`, `fatal_error_count`
  - `EvidenceEngine` rejects template/not_started/running/failed/invalid experiments
  - Only `completed` + `valid` experiments can produce `EVID-*` evidence
  - Tests: `test_experiment_validity.py` (21 tests)

- **Research fail-fast mode** (Phase 2):
  - `ExperimentRecorder(fail_fast=True)` — auto-invalidates on first runtime error
  - Default mode (`fail_fast=False`) captures errors without stopping

- **Canonical scientific state definition** (Phase 3-4):
  - `src/research/canonical_state.py` — defines `State(t)` contract
  - `canonical_state_digest()` — SHA-256 of full scientific runtime state
  - Deterministic serialization: sorted neurons, synapses, events
  - No memory addresses, no repr(), no wall-clock timestamps
  - Tests: `test_canonical_state.py` (17 tests)

- **Full RNG state persistence** (Phase 5):
  - Checkpoint captures `rng.getstate()` — complete `random.Random` state
  - Restore via `rng.setstate()` — exact bitwise equality
  - Tests: `test_rng_persistence.py` (6 tests)

- **Iteration-order determinism** (Phase 6):
  - Verified neuron/synapse/event iteration produces identical sequences
  - Three independent runs produce identical canonical digests
  - Tests: `test_iteration_determinism.py` (8 tests)

- **Structural determinism** (Phase 7):
  - Same initial state + config + RNG → same proposals, mutations, topology
  - N >= 3 independent runs produce identical results
  - Tests: `test_structural_determinism.py` (5 tests)

- **Checkpoint v4 — homeostasis + learning state** (Phase 8):
  - `HomeostasisRuntimeRecord` — per-neuron smoothed firing rates
  - `LearningRuntimeRecord` — STDP traces, eligibility values
  - Backward compatible with v3 checkpoints
  - Tests: `test_checkpoint_v4.py` (7 tests)

### Fixed

- **Version inconsistency** (`src/main.py`): corrected `"v0.5.0-alpha.1"` to `"v0.5.0-alpha.5"` in startup banner
- **Duplicate startup print removed** (`src/main.py`): removed hardcoded `:8765` print that duplicated the dynamic-port print below it
- **Listener parsing hardened** (`tests/test_single_listener.py`): `_get_listener_pids()` now checks for local address (`127.0.0.1:{port}`), LISTEN state (locale-agnostic), and valid PID — no longer matches remote addresses or non-listening connections
- **Renamed test reference fixed** (`tests/test_single_listener.py`): artifact writer referenced `test_exactly_one_listener_owns_port_8765` but the actual function is `test_exactly_one_listener_owns_port` (no `_8765` suffix)
- **Gate status test sources updated** (`tests/test_gate_status.py`): added `research/generated/verification/single_listener.json` to allowed sources; structural-disabled tests now also remove the live loop artifact to avoid false PASSED status

### Changed

- **Gate status builder** (`src/dashboard/gate_status.py`): Gate B now dynamically checks for experiment validity tests, determinism tests, and checkpoint v4 tests
- **TODO.md**: updated Gate B/C status, open items, and execution order

### Test Results (real run, 2026-08-26)

- **Python**: 3.13.14
- **Command**: `python -m pytest tests/ -q`
- **Result**: 356 passed, 2 skipped, 0 failed, 0 collection errors
- **New tests**: 64 (experiment validity, canonical state, RNG persistence, iteration determinism, structural determinism, checkpoint v4)
- **Structural E2E**: 11/11 proofs verified
- **Single listener**: 2/2 tests passed
- **Gate status**: 23/23 tests passed

---

## v0.5.0-alpha.5 - Structural Evidence Hardening Complete (2026-08-24)

### Fixed

- **Production path regression** (`src/main.py`): restored `Brain5DManipulator` import that was removed during the composition factory refactor; removed the legacy `SelfOrganizationEngine` from the direct mutation path — structural mutation now flows exclusively through the canonical Coordinator -> Approval -> PlasticityEngine path
- **Manual proposal fallback removed** (`tests/test_structural_e2e.py`): `_make_neurogenesis_proposal()` now raises `AssertionError` if the policy does not produce a proposal from the real signal — no more manual `StructuralProposal` creation as fallback
- **GateBuilder fail-closed validation** (`src/dashboard/gate_status.py`): missing `schema_version`, `tested_tree_digest`, `current_digest`, or proof count != 10 all result in NOT VERIFIED — no more silent pass on incomplete artifacts

### Changed

- **Artifact writer** (`tests/test_structural_e2e.py`): now runs proofs via real pytest subprocess (not manual function calls); includes `test_complete_canonical_e2e` in the required proof set; topology digests must be non-null (fail-closed)
- **Persistent verification artifact** committed to `research/generated/verification/structural_e2e.json` — a fresh clone can now verify the structural E2E status
- `tests/test_baseline.json`: updated to current tree digest (includes `tests/`)

### Test Results (real run, 2026-08-24)

- **Python**: 3.13.14
- **Command**: `python -m pytest tests/ -q`
- **Result**: 274 passed, 2 skipped, 0 failed, 0 collection errors
- **Structural E2E**: 11/11 proofs verified (10 proofs + complete canonical E2E)
- **Production path**: single canonical mutation path (legacy engine NOT attached)

---

## v0.5.0-alpha.5 - Structural Evidence Hardening (2026-08-24)

### Added

- **Production composition factory** (`src/self_organization/composition.py`):
  - `compose_structural_subsystem()` — single canonical function used by both `src.main` and E2E tests
  - Tests no longer recreate a parallel architecture; they use the production path
- **Real HomeostasisSignal in Proof 4** (`tests/test_structural_e2e.py`):
  - Uses `HomeostasisEngine.build_signal()` — the canonical production signal builder
  - `_FakeSignal` removed from the main E2E proof chain
- **Complete canonical E2E test** — full chain from real signal to journaled mutation without manual proposal creation
- **Real journal reopen for Proof 10** — new `StructuralJournal` object from same path (simulates process restart)
- **Persistent verification artifact** at `research/generated/verification/structural_e2e.json` (not gitignored)
  - Full provenance: schema_version, timestamp, python_version, tested_commit, tested_tree_digest, test_command
  - Topology digests before/after mutation/undo, journal_record_count
  - Staleness binding: GateStatusBuilder rejects/stales when artifact tree digest != current tree digest
- **Extended tree digest** (`src/dashboard/verification.py`):
  - Now includes `tests/` so changing a verification test makes the baseline STALE
  - Excludes `tests/test_baseline.json` so the baseline file cannot invalidate itself

### Changed

- `src/main.py`: structural composition now delegates to `compose_structural_subsystem()` factory
- `src/dashboard/gate_status.py`: reads artifact from persistent `research/generated/verification/` path with staleness binding
- `tests/test_gate_status.py`: updated artifact paths and stale-acceptance logic
- `tests/test_baseline.json`: updated to 274 passed, 2 skipped, 0 failed, 0 collection errors

### Test Results (real run, 2026-08-24)

- **Python**: 3.13.14
- **Command**: `python -m pytest tests/ -q`
- **Result**: 274 passed, 2 skipped, 0 failed, 0 collection errors
- **Structural E2E**: 10/10 proofs verified with real signal, production composition, and journal reopen

---

## v0.5.0-alpha.5 - Structural E2E Verification (2026-08-23)

### Added

- **Structural E2E Ten Proofs** (`tests/test_structural_e2e.py`):
  - Proof 1: Coordinator is instantiated
  - Proof 2: PlasticityEngine is instantiated
  - Proof 3: Bridge contains exactly these instances
  - Proof 4: Proposal originates from real runtime signal
  - Proof 5: Proposal alone does NOT mutate the network
  - Proof 6: Reject does NOT mutate the network
  - Proof 7: Approve produces exactly one mutation
  - Proof 8: Mutation produces exactly one Journal record
  - Proof 9: Undo restores the previous topology
  - Proof 10: Restart + Replay produces the same state
  - Machine-readable verification artifact written to `artifacts/structural_e2e_results.json`
- **Evidence-based structural gate** (`src/dashboard/gate_status.py`):
  - GateStatusBuilder now reads `artifacts/structural_e2e_results.json`
  - Structural criteria in Gate A and proofs in Gate B are set from real evidence
  - When artifact shows `status: verified`, criteria move from `pending` to `passed`
  - When artifact is absent, criteria remain `pending` (no guessing)

### Changed

- `tests/test_gate_status.py`: updated structural tests to account for the E2E artifact
- `tests/test_baseline.json`: updated to 273 passed, 2 skipped, 0 failed, 0 collection errors

### Test Results (real run, 2026-08-23)

- **Python**: 3.13.14
- **Command**: `python -m pytest tests/ -q`
- **Result**: 273 passed, 2 skipped, 0 failed, 0 collection errors
- **Structural E2E**: 10/10 proofs verified

---

## v0.5.0-alpha.5 - Dynamic Alpha.5 Release Gate (2026-08-23)

### Added

- **Dynamic Alpha.5 Release Gate** (`src/dashboard/gate_status.py`):
  - `GET /api/gate/status` — evidence-based gate status for Gate A (Technical Integration), Gate B (Verification), Gate C (Scientific Baseline)
  - Strict separation: Live Runtime Status (active/disabled/unavailable/error) vs Gate Status (passed/pending/blocked/stale/failed) vs Maturity (implemented/integrated/verified/evidenced)
  - Runtime disabled ≠ gate failed. Runtime disabled ≠ gate passed. IMPLEMENTED ≠ VERIFIED. VERIFIED ≠ EVIDENCED.
  - Gate A criteria carry test-file evidence (`evidence.test_ids`), not hardcoded `passed` flags
  - Config-aware live status: `config.enabled=false` → DISABLED; `config.enabled=true` + component missing → ERROR
  - Experiment `executed` requires `experiment_status=completed` only (not_started/template/running/failed are NOT executed)
  - Registry counts use the typed `ResearchRegistry` API, not string counting
  - Tests and Research are NOT live runtime subsystems — Tests belong to Gate B, evidence belongs to Gate C
- **Shared verification module** (`src/dashboard/verification.py`):
  - Single `compute_source_tree_digest()` and `evaluate_test_baseline()` used by both `IntegrationStatusBuilder` and `GateStatusBuilder`
  - Prevents `/api/integration/status` and `/api/gate/status` from disagreeing about the same source tree
  - Handles both new (`full_suite`/`full_collection`) and legacy (`verified_subset`) baseline formats
- **22 new tests** in `tests/test_gate_status.py` covering all six architectural guarantees

### Fixed

- **Baseline format bug** (`src/dashboard/integration_status.py`): `_check_tests` now reads `full_suite` (new format) with `verified_subset` fallback, so the integration status no longer reports `0 passed` after a current baseline run
- **Duplicate tree-digest implementations** removed: `integration_status.py` and `gate_status.py` now delegate to `verification.py`
- **Config-aware live status**: structural and delta storage live status now distinguishes "disabled by config" from "config enabled but component missing" (ERROR)
- **Experiment execution semantics**: `_experiment_executed` now requires `completed` status only
- **Registry counts**: now use `ResearchRegistry` typed API instead of fragile YAML string counting
- **test_structural_e2e.py**: fixed malformed docstrings (escaped `\"\"\"` → `"""`)

### Changed

- `index.html`: removed hardcoded `gate-todo`/`gate-done` checklist; replaced with dynamic `gate-a-list`/`gate-b-list`/`gate-c-list` containers rendered from `/api/gate/status`
- `app.js`: `refreshGateStatus` now fetches `/api/gate/status` and renders Gate A/B/C criteria tables with Live/Maturity/Gate columns
- `styles.css`: added dynamic gate criteria table, live runtime grid, maturity badge colors
- `src/main.py`: `OperatorBridge` now carries `config_dict` attribute so the gate builder can distinguish disabled-by-config from config-enabled-component-missing
- `docs/08-roadmap/TODO.md`: normalized contradictory baseline numbers (236/2 collection errors → 261/0 collection errors); removed duplicated historical sections
- `tests/test_baseline.json`: updated to 261 passed, 2 skipped, 0 failed, 0 collection errors (full suite without `--ignore`)

### Test Results (real run, 2026-08-23)

- **Python**: 3.13.14
- **Command**: `python -m pytest tests/ -q`
- **Result**: 261 passed, 2 skipped, 0 failed, 0 collection errors
- **Full suite runs without `--ignore`**

---

## v0.5.0-alpha.5 - Dashboard Completion & Scientific Observability (2026-08-23)

### Added

- **Real 5D Network Inspector** (`src/dashboard/network_inspector.py`):
  - `GET /api/network/summary` — real neuron/synapse counts, dimensions, mean energy/v
  - `GET /api/network/neurons` — paginated real 5D coordinates (x1-x5), v, u, energy, last_spike, spike_count
  - `GET /api/network/synapses` — paginated real source/target, weight, delay, eligibility
  - `GET /api/network/projection` — real 5D→3D projection with stride sampling, honestly labelled
- **Real Integration Status** (`src/dashboard/integration_status.py`):
  - `GET /api/integration/status` — computes Bridge/Controller/Runtime/Structural/Snapshot/Delta-Storage/Structural-Journal/Research/Tests/Error-Visibility
  - Status values: `passed`, `disabled`, `pending`, `stale`, `failed`
  - Disabled-by-config is NEVER `failed`
  - Tests-STALE detection reads `tests/test_baseline.json` and compares `tested_commit` with current git HEAD
- **Inspect Tab** in dashboard (`index.html`, `app.js`) with network summary, 5D projection canvas, neurons/synapses paginated tables
- **Provenance badges** (`LIVE`/`SNAPSHOT`/`CONFIG`/`RESEARCH`/`TEST`) in `styles.css`
- **20 new tests** in `tests/test_dashboard_completion.py` covering Tick-0 real size, null serialization, disabled≠failed, canonical commands, 5D coordinates, projection, stale detection, no demo source

### Fixed

- **Config-authoritative storage** (`src/main.py`): `AsyncStorageSession` is now ONLY started when `storage.runtime.enabled=true`. With `poc_config.yaml` (disabled), Delta Storage reports "disabled by config" instead of silently running with fake zeros.
- **Truthful null/disabled formatting** (`src/dashboard/static/app.js`): `formatNumber`/`formatFloat`/`formatBytes` now return `"—"` for null/undefined instead of fake `0`. Storage/Homeostasis/Self-Org panels show "disabled by config" / "—" when disabled, not measured zeros.
- **Structural config-aware UI** (`src/dashboard/static/control-panel.js`): Self-Organization badge shows `DISABLED BY CONFIG` when `self_organization.enabled=false` (was static `Configured`). Controls auto-disable.
- **Integration status badges** (`app.js`): `refreshIntegrationStatus` and `refreshGateStatus` now use the real `/api/integration/status` backend instead of frontend heuristics that hardcoded `int-tests` to `false`.
- **Tree-digest staleness model** (`src/dashboard/integration_status.py`): Tests status no longer compares `tested_commit == current_commit` (a file inside a commit cannot stably contain its own SHA). Instead it compares a `tested_tree_digest` (SHA-256 over `src/`, `configs/`, `research/schemas/`, `pyproject.toml`) with the current tree digest. Pure docs/baseline changes no longer artificially invalidate the test status.
- **Gate tab** (`index.html`): added Runtime, Delta Storage, Structural Journal, Tests, Error Visibility gate items with real backend data.

### Changed

- `tests/test_baseline.json`: updated from real test run — **verified runnable subset**: 236 passed, 2 skipped; full collection still blocked by 2 collection errors (test_async_storage.py, test_compaction.py import non-existent tests.test_storage_runtime). Now includes `tested_tree_digest` so baseline/docs-only changes no longer artificially invalidate the test status.
- `docs/TODO.md`: Alpha.5 Dashboard Completion section added; Gate visualization updated

### Test Results (real run, 2026-08-23)

- **Python**: 3.13.14
- **Command**: `python -m pytest tests/ -q --ignore=tests/test_async_storage.py --ignore=tests/test_compaction.py`
- **Result (verified runnable subset)**: 236 passed, 2 skipped, 0 failed
- **Full collection**: still blocked by 2 collection errors (pre-existing: test_async_storage.py, test_compaction.py) — not a complete suite run

### Manual E2E Verification

- Fresh start at Tick 0: 5000 real neurons, 36031 real synapses, idle, storage disabled by config
- `step` → exactly +1 tick; `run_ticks 100` → exactly +100 ticks; `snapshot` → new real .b5d file
- `/api/integration/status`: overall=stale (Tests baseline 4fa22a4 vs HEAD 4b8502b), 6 passed, 3 disabled, 0 failed

---

## v0.5.0-alpha.5 - Structural Persistence (CI & Test-Suite Overhaul)

### Added

- **CI pipeline** (`.github/workflows/ci.yml`) mit 5 Jobs:
  - `lint-format`: Black, Ruff, Pylint, Whitespace-Check
  - `type-check`: Mypy + Pyright (2 Scopes)
  - `tests`: Pytest-Matrix auf Python 3.11 / 3.12 / 3.13
  - `build`: Wheel-Build + Installations-Verifikation
  - `smoke`: Import-Smoke-Tests, Config-Loader, Verifier
- **Smoke-Test-Suite** (`tests/test_ci_smoke.py`): 24 schnelle Import-/Config-/Netzwerk-Tests
- **Automatische pytest-Marker** via `conftest.py`: `core`, `storage`, `plasticity`,
  `dashboard`, `homeostasis`, `learning`, `embodiment`, `integration`, `slow`, `smoke`
- **Ruff-Linter-Konfiguration** in `pyproject.toml`
- **Coverage-Konfiguration** (`pytest-cov`) in `pyproject.toml`

### Fixed

- **Circular imports** in `src/self_organization/` (`coordinator.py`, `policy.py`)
  durch `TYPE_CHECKING`-Imports
- **NullBackend-Klassen** in `src/language_organ/null_backend.py` definiert
  (bisher nur Dummy-Imports)
- **ConfigDict TypeAlias** + `queued_event_count` Property in `src/core/network.py`
- **Mypy-Typfehler** in `src/research/` (registry, report_builder, experiment_recorder,
  evidence_engine), `src/dashboard/` (server, operator_bridge, research_source),
  `src/self_organization/` (undo, plasticity)
- **Pylint E-Level**: `__all__` in `learning_engine.py` bereinigt,
  `inconsistent-return-statements` in `undo.py` und `plasticity.py` korrigiert
- **test_brain5d_launcher.py**: an `build_command`-API angepasst
- **test_dashboard_alpha7.py**: `DocumentationSource.read()` Fehlerbehandlung
- **test_homeostasis_engine.py**: `threshold_adaptation`/`energy` Toleranz
- **test_restore_continue.py**: `ConfigDict`-Import + `queued_event_count`
- **test_self_organization.py**: `max_neurons` in `SelfOrganizationParameters`
- **Black-Formatierung**: 54 Dateien automatisch formatiert

### Changed

- `pyproject.toml`: dev-Dependencies um `ruff`, `pytest-cov` erweitert;
  `[tool.ruff]`, `[tool.coverage]` Konfiguration hinzugefügt
- `pyrightconfig.json`: unverändert (strict mode für `src/storage`, `src/homeostasis`)
- README.md: CI-Badges, aktualisierte Test-Statistiken (166 passed),
  Ruff in Quality-Gates aufgenommen, CI-Pipeline-Dokumentation

### CI Status

- **166 Tests passed**, 2 skipped
- **Mypy**: 0 echte Typfehler
- **Pyright**: 0 errors, 0 warnings
- **Pylint**: `--fail-under=9.0` pass
- **Black + Ruff**: clean
- **Python-Matrix**: 3.11 / 3.12 / 3.13

## v0.5.0-alpha.5 - Structural Persistence

### Added

- B5D-SEF research dashboard API (`/api/research`, `/api/research/documents`,
  `/api/research/reports`, `/api/research/experiments`, `/api/research-files/`)
  exposing the Scientific Evidence Framework registry, generated reports and
  experiment manifests to the operator dashboard;
- `src/dashboard/research_source.py` — read-only, path-traversal-safe
  research source with registry summary, generated-report listing and
  experiment manifest loading;
- research dashboard route tests
  (`tests/test_research_dashboard_routes.py`, 6 tests) covering summary,
  reports, file content, path-traversal rejection and JSON-404 isolation;
- single-instance binding regression suite
  (`tests/test_dashboard_single_instance.py`, 9 tests) verifying the P0
  process-architecture contract: bridge identity stability across HTTP
  requests, `/api/debug/bridge` reporting `bridge_exists`/`controller_exists`,
  `/api/structural/status` never reporting the bridge as missing when attached,
  JSON-404 isolation for unknown `/api/...` paths, and bridge object identity
  matching the server attachment;
- dashboard frontend expanded with Research tab (B5D-SEF browser) and
  Alpha.5 Integration Gate tab (live criteria board with automated checks
  and remaining manual checklist);
- dashboard frontend now shows integration status badges on the Dashboard tab;
- CRC-protected structural journal with commit markers and uncommitted-tail
  recovery;

### Changed

- `control-panel.js` converted to a pure ES module: `export class` syntax,
  no self-initialization on `DOMContentLoaded`, no CommonJS `module.exports`,
  no module-global state; `ControlAPI.run()` renamed to `runTicks()` to match
  the canonical `{"command": "run_ticks", "ticks": N}` contract;
- `operator_console.js` converted to a pure ES module: `export class` syntax,
  no self-initialization, no CommonJS fallbacks;
- `app.js` is now the sole frontend lifecycle owner: static ES module imports
  replace dynamic `import()` with try/catch fallback; duplicate fallback
  command handlers removed; `module.exports` block removed; canonical command
  contract unified across Control and Console tabs;
- `DashboardServer` now accepts an optional `ResearchSource` and exposes
  `/api/research*` routes;
- `serve_dashboard()` accepts a `research_root` parameter; `src/main.py`
  passes `research/` as the research root.
- deterministic structural replay and persistent inverse-record undo;
- safe manual and optional policy-based proposal approval;
- journal-backed structural history and heatmaps;
- typed dashboard routes for proposals, decisions, undo, configuration,
  snapshots, and bounded tick execution;
- worker-boundary manual snapshots with ordered structural flush, `.b5d` write,
  runtime checkpoint write, and completion notification;
- optional structural journal replay in the central restore path before runtime
  checkpoint overlay.

### Compatibility

- alpha.3 coordinator and alpha.4 proposal/plasticity APIs remain available;
- automatic approval, neuron pruning, and mutation outside reviewed boundaries
  remain disabled by default.

## v0.5.0-alpha.4 - Compatibility Repair

### Fixed

- restored the public `SelfOrganizationEngine` and alpha.3 policy contracts;
- added the immutable canonical `HomeostasisSignal` contract and engine builder;
- added `src/homeostasis` to the strict Pyright project graph;
- separated launcher-only dashboard, browser, host, and port options from the
  `src.main` subprocess command.

### Compatibility

- alpha.4 proposal and structural-plasticity APIs remain available alongside
  the alpha.2/alpha.3 interfaces.

## v0.4.0-alpha.7 – Embodiment Foundation & Deterministic Restore V3

### Fixed

- exact restore now preserves neuron model parameters that `.b5d` V1 stores as
  float32 restart fields;
- exact synapse weights and eligibility values are restored from Runtime
  Checkpoint V3;
- checkpoint JSON parsing is strict-mypy safe without `Any` or `type: ignore`.

### Added

- typed sensor, actuator, environment, registry, and embodiment-agent contracts;
- read-only embodiment metrics in the operator dashboard;
- safe Markdown documentation browser;
- safe sibling `.b5d` snapshot selector;
- PID-tracked cross-platform launcher and consolidated quality runner;
- roadmap integration of embodiment, continual learning, causal evaluation, and
  neuro-symbolic research directions.

### Compatibility

- `.b5d` Snapshot V1 is unchanged;
- delta journal binary format is unchanged;
- Runtime Checkpoint JSON version advances to 3;
- versions 1 and 2 remain readable.

## v0.4.0-alpha.6 – Deterministic Restore & Research Alignment

- added exact dynamic neuron state to runtime checkpoints;
- added dashboard homeostasis bridge;
- aligned roadmap with project research documents.

## v0.4.0-alpha.5 – Operator Dashboard

- added local read-only dashboard and lazy snapshot heatmaps.

## v0.4.0-alpha.4 – Persistence Finalization

- bounded asynchronous storage queue;
- persistence telemetry;
- generation-based crash-safe compaction;
- runtime checkpoint and real network restore foundation.

## v0.4.0-alpha.3 – Runtime Storage & Lazy Views

- runtime storage session;
- lazy mmap activity/weight/energy projection;
- strict storage typing and verification tooling.

## v0.4.0-alpha.2 – Journal & Recovery

- append-only delta journal, CRC, commit markers, and crash recovery.

## v0.4.0-alpha.1 – `.b5d` Storage V1

- frozen binary snapshot format, mmap reader, deterministic layout, and format
  robustness tests.

## v0.3.x – Learning and Structural Foundation

- STDP and eligibility traces;
- reward-modulated three-factor learning;
- heatmap observability;
- optical state/manipulator experiments;
- optional pruning, sprouting, and neurogenesis.

## v0.1.0 – Verified Observable Core

- sparse 5D spatial index;
- Izhikevich reference neuron;
- delayed event propagation;
- deterministic Golden Chain;
- telemetry and run artifacts.
