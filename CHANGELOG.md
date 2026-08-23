# Changelog

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
