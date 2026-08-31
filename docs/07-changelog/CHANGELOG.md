# Changelog

## 2026-08-31 — v0.5.0-alpha.6 Opened

### Version Transition
- **Alpha.5**: frozen, tagged `v0.5.0-alpha.5`, gate PASSED.
- **Alpha.6**: opened as current development version `0.5.0-alpha.6` / PEP-440 `0.5.0a6`.
- Added immutable release registry under `releases/` with `/api/releases` and `/api/releases/current`.
- Renamed dashboard `VERIFY` tab to `RELEASE` and added version history tree.
- Archived legacy v0.4 Alpha.6/Alpha.7 files to prevent version collisions.

### Opening Verification
- Full test suite: **463 passed, 2 skipped, 0 failed**.
- Alpha.6 gate: **OPEN** — no morphological self-regulation feature verified yet.

## 2026-08-31 — Alpha.5 Release Gate Re-Closed After Dashboard Fixes

### Final Gate Result
- **ALPHA.5 Overall**: ✅ **PASSED**
- **Gate A — Technical Integration**: ✅ passed
- **Gate B — Verification**: ✅ passed
- **Gate C — Scientific Baseline**: ✅ passed

### Verification Summary
- **Full test suite**: 457 passed, 2 skipped, 0 failed.
- **Pyright**: 0 errors.
- **Ruff**: 0 errors.
- **Source tree digest**: `063bc485695bc63c149344bcd9dfcffc6264814edaec120e51e7bf44d7e80107`.
- **Single TCP LISTEN socket on 127.0.0.1:8765**: verified.
- **Production HomeostasisSignal → Policy → Coordinator**: verified.
- **Structural Coordinator / PlasticityEngine / Manipulator / Approval-gated mutation / Journal**: verified via E2E proofs.
- **Restore-and-continue identity (A/B/C)**: verified (`A == B == C`).
- **Structural determinism, iteration-order determinism, full RNG state persistence, canonical full-state digest, homeostasis + learning state persistence**: verified.
- **EXP-DET-0001** and **EXP-STOR-0001** executed; first DATA-\* / EVID-\* artifacts produced; Research Catalog and Evidence Matrix rebuilt from real evidence.

### Dashboard Fixes
- Structural Live Loop renderer now shows Policy/Proposal/Undo/Replay as verified.
- Network tab populated with IO flow, population, spike raster and histogram values.
- Self-Organization gate correctly reports ACTIVE instead of disabled.
- Added `/api/structural/live-loop` endpoint and enriched network telemetry DTOs.

### Regenerated Evidence
| Artifact | Status | HEAD |
|----------|--------|------|
| `tests/test_baseline.json` | passed | `b3c13e2...` |
| `research/generated/verification/determinism_infrastructure.json` | verified | `b3c13e2...` |
| `research/generated/verification/restore_determinism.json` | verified (A == B == C) | `b3c13e2...` |
| `research/generated/verification/single_listener.json` | verified | `b3c13e2...` |
| `research/generated/verification/structural_e2e.json` | verified | `b3c13e2...` |
| `research/generated/verification/structural_live_loop.json` | verified | `b3c13e2...` |

## 2026-08-31 — Alpha.5 Release Gate Closed

### Final Gate Result
- **ALPHA.5 Overall**: ✅ **PASSED**
- **Gate A — Technical Integration**: ✅ passed
- **Gate B — Verification**: ✅ passed
- **Gate C — Scientific Baseline**: ✅ passed

### Verification Summary
- **Full test suite**: 457 passed, 2 skipped, 0 failed.
- **Pyright**: 0 errors.
- **Ruff**: 0 errors.
- **Source tree digest**: `2f0d6883d4a7010b7de8e0f4a4200b62d8d3d761f5c54c599c992c4560235d5c`.
- **Single TCP LISTEN socket on 127.0.0.1:8765**: verified.
- **Production HomeostasisSignal → Policy → Coordinator**: verified.
- **Structural Coordinator / PlasticityEngine / Manipulator / Approval-gated mutation / Journal**: verified via E2E proofs.
- **Restore-and-continue identity (A/B/C)**: verified (`A == B == C`).
- **Structural determinism, iteration-order determinism, full RNG state persistence, canonical full-state digest, homeostasis + learning state persistence**: verified.
- **EXP-DET-0001** and **EXP-STOR-0001** executed; first DATA-\* / EVID-\* artifacts produced; Research Catalog and Evidence Matrix rebuilt from real evidence.

### Regenerated Evidence
| Artifact | Status | HEAD |
|----------|--------|------|
| `tests/test_baseline.json` | passed | `5f583a6...` |
| `research/generated/verification/determinism_infrastructure.json` | verified | `5f583a6...` |
| `research/generated/verification/restore_determinism.json` | verified (A == B == C) | `5f583a6...` |
| `research/generated/verification/single_listener.json` | verified | `5f583a6...` |
| `research/generated/verification/structural_e2e.json` | verified | `5f583a6...` |
| `research/generated/verification/structural_live_loop.json` | verified | `5f583a6...` |

### Runtime Stability Fixes
- `src/main.py` now reconfigures `stdout`/`stderr` to UTF-8 on startup, preventing `UnicodeEncodeError` on Windows consoles / redirected output.
- Runtime delta persistence automatically recovers from a corrupt `latest.b5d.journal` by renaming the damaged file and starting fresh; the canonical `.b5d` snapshot remains the source of truth.

### Notes
- Evidence provenance aligned to the commit that contains the regenerated artefacts.
- Temporary provenance alignment script removed from repository tracking.
- Alpha.5 is now fully closed; work may advance to Alpha.6.

## 2026-08-30 — Dashboard Document Viewer: Full-Feature Suite

### Backend
- **`src/dashboard/file_manager.py`**:
  - `GET /api/files/history/{path}` — Git-History via `git log --follow`.
  - `GET/PUT /api/files/meta/{path}` — Sidecar-Metadaten (`.meta.yaml`) für jede Datei.
  - `GET /api/files/analyze/{path}` — Lokale Dokumentenanalyse (Sprache, Lesbarkeit, Keywords, Sentiment, Zusammenfassung).
  - `GET /api/files/export/{path}?format={html|docx|md}` — Markdown-Export.
  - Markdown-to-HTML/DOCX-Generierung mit Inline-Formatierung.

### Frontend
- **`src/dashboard/static/file-viewer.js`**:
  - Jupyter Notebook (`.ipynb`), Log-Level-Highlighting, Graphviz DOT & PlantUML Renderer.
  - In-Document-Suche, Markdown-TOC, Vollbild, Diff, Auto-Save, Backup-Restore.
  - 🔍 Search, 🕰️ History, 📝 Notes, 🤖 Analyze, ⬇️ Export Buttons im Viewer-Header.
  - Research-Registry-Kartenansicht für YAML-Dateien unter `research/registry/`.
- **`src/dashboard/static/bibtex-viewer.js`**: Formular-Editor für `.bib`-Dateien mit Speichern.
- **`src/dashboard/static/styles.css`**: Stile für alle neuen Viewer, Panels und Karten.
- **`src/dashboard/static/index.html`**: CDN-Erweiterungen für js-yaml, xlsx, mammoth, d3, graphviz, plantuml-encoder.

### Tests
- **`tests/test_dashboard_file_manager.py`**: 10 Tests für Save, Meta, Analyze, Export, History.

## 2026-08-30 — Dashboard UI/UX Redesign: Footer-Status, Header-Steuerung, Kompaktes Overview

### Frontend
- **`src/dashboard/static/index.html`**: Header auf Dark/Light- und Accessibility-Buttons reduziert; Experiment-Mode-Switcher, System-Status und Health-Bar in den always-visible Footer verschoben; separate Runtime-Error-Card aus OVERVIEW entfernt.
- **`src/dashboard/static/styles.css`**: Footer fixed am unteren Rand (`z-index: 50`); Body-Padding für Footer; kompaktes Overview-Layout (kleinere Cards, engeres Grid, reduzierte Schriften) für 1080p @ 75% Zoom ohne vertikale Scrollbar; Light-Theme-Overrides; Accessibility-Mode-Styles.
- **`src/dashboard/static/health-drawer.js`**: Health-Bar wird jetzt in `#footer-status` gerendert; Runtime-Error-Count und -Details aus `/api/structural/errors` werden in Health-Bar und Drawer angezeigt.
- **`src/dashboard/static/overview-panel.js`**: Separate Runtime-Error-Visibility-Card entfernt; Fehlerdaten bleiben für Health-Drawer verfügbar.
- **`src/dashboard/static/app.js`**: Dark/Light-Toggle und Accessibility-Toggle implementiert (mit `localStorage`-Persistenz); überflüssige `refreshErrorVisibility`-Funktion entfernt.
- **`src/dashboard/static/state-store.js`**: `/api/structural/errors` wird im State Store geladen und als `structural_errors` veröffentlicht.

### Tests
- Dashboard-Test-Suite: **108 passed**.
- Gesamte Test-Suite: **454 passed, 2 skipped**.

## 2026-08-30 — Code Quality Cleanup: Pyright / Ruff / Pytest Green

### Quality Status
- **Pyright**: 0 errors, 0 warnings, 0 informations across `src/` and `tests/`.
- **Ruff**: 0 lint/import errors after auto-fix pass.
- **Pytest**: 454 passed, 2 skipped (large-storage slow tests), 1 external deprecation warning.

### Backend fixes
- **`src/dashboard/models.py`**: Replaced mutable `None` defaults for `components`, `parameters`, `pending_changes` with typed `field(default_factory=...)` to eliminate unnecessary `is None` comparisons and unknown-type diagnostics.
- **`src/dashboard/server.py`**: Added explicit casts for `int()` conversions and `_send_json` payloads containing `list[str]` values.
- **`src/dashboard/health_builder.py`**: Tightened `_is_enabled` / `_nested_get` typing to avoid partially-unknown `dict` diagnostics.
- **`src/dashboard/file_manager.py`**: Added missing `_root()` helper and typed `history` list; removed unnecessary casts.
- **`src/research/canonical_state.py`**: Switched protocol `neurons`/`synapses`/`event_slots` properties to covariant `Mapping` / `Sequence` so real network types match the protocol.
- **`src/storage/checkpoint.py`** / **`src/storage/core_restore.py`**: Added `# pyright: ignore[reportPrivateUsage]` markers for intentional internal field access.

### Test fixes
- **`tests/conftest.py`**: Renamed `TestConfig` to `Config` to avoid pytest collection warning.
- **`tests/test_artifacts.py`**: Updated import to `Config`.
- **`tests/test_dashboard_file_manager.py`**: Fixed undefined `host`/`port` variables by extracting them from `server.server_address`.
- **`tests/test_dashboard_pending_parameters.py`**: Removed unused model imports; typed fixture as `Iterator[DashboardServer]`.
- **`tests/dashboard_http.py`**: Simplified `_server_address` cast.
- **`tests/_restore_helpers.py`**: Added private-usage ignores and removed unused `Path` import.

## 2026-08-30 — Verification Audit: Restore Verified, Evidence Scopes Required

### Verification Status
- **Restore A/B/C determinism** is now verified (`A == B == C`, tested at commit `93620ecc...`).
- **Structural E2E** and **Structural Live Loop** are verified.
- **Test baseline** `tests/test_baseline.json` is stale (2026-08-28, 418 passed / 3 failed / 2 skipped, commit `39a4b6e...`); full suite must be re-run and baseline regenerated.
- **Evidence-freshness model** is too coarse: dashboard/UI changes under `src/dashboard/` currently invalidate restore/structural evidence artifacts. This must be replaced with scoped evidence digests.

### Architecture Findings
- `StateStore` exists but is not yet the single source of truth: `app.js` still issues parallel requests to `/api/gate/status`, `/api/structural/errors`, `/api/integration/status`, `/api/snapshot-info`, `/api/heatmap`, etc.
- `ControlPanel` and `OperatorConsole` both register runtime keyboard shortcuts, creating a double-shortcut bug.
- `HealthBuilder` conflates `enabled` with `active` for Learning and reports Verification as `active` based only on endpoint availability rather than actual gate/evidence state.
- `tmp/restore_diag/` and `tmp/trace_diag/` contain checked-in diagnostic state dumps that should not live in the normal source tree.

### Next Steps
1. Make `ControlPanel` the sole command owner; remove runtime shortcuts from `OperatorConsole`.
2. Introduce evidence scope digests so UI changes do not mark scientific proofs stale.
3. Fix health-state semantics: `enabled ≠ active`, `unavailable ≠ disabled`, verification status reflects gate state.
4. Source freeze → full test suite → new baseline → regenerate all evidence artifacts.

## 2026-08-30 — Dashboard Operator-Workbench: Pending-Changes-Workflow

### Backend
- **`src/dashboard/models.py`**: Neue Dataclasses `PendingParameterChange` und `ParameterChangeRecord`; `DashboardSnapshot` um `pending_changes` und `change_history` erweitert.
- **`src/dashboard/state.py`**: `set_pending_change`, `remove_pending_change`, `clear_pending_changes`, `append_change_history` hinzugefügt.
- **`src/dashboard/server.py`**: Neue API-Endpunkte für Pending-Changes:
  - `GET /api/parameters/pending`
  - `POST /api/parameters/{name}/pending`
  - `POST /api/parameters/pending/apply`
  - `POST /api/parameters/pending/save-profile`
  - `POST /api/parameters/pending/cancel`

### Frontend
- **`src/dashboard/static/parameter-inspector.js`**: Neuer Parameter-Inspector mit Filter, Edit/Reset, Pending-Bar (Apply / Apply+Save Profile / Cancel) und Change-History.
- **`src/dashboard/static/index.html`**: Parameter-Inspector-Card im CONTROL-Tab ergänzt.
- **`src/dashboard/static/styles.css`**: Stile für Parameter-Tabelle, Pending-Bar und Change-History.
- **`src/dashboard/static/app.js`**: `ParameterInspector` importiert und initialisiert.

### Tests
- **`tests/test_dashboard_pending_parameters.py`**: 8 neue Tests für den Pending-Changes-Workflow.
- Dashboard-Test-Suite: **51 passed**.
## 2026-08-30 — Dashboard Operator-Workbench: Frontend Modularisierung

### Frontend
- **`src/dashboard/static/state-store.js`**: Fetching von `/api/gate/status`, `/api/integration/status`, `/api/snapshot-info`, `/api/structural/errors` integriert; Status wird sofort veröffentlicht, Hilfsendpunkte mit 2s-Timeout im Hintergrund nachgeladen.
- **`src/dashboard/static/app.js`**: Reduziert auf Bootstrap, Tab-Routing, Modul-Lifecycle und globale Health-Integration; keine direkten Requests mehr an Gate/Integration/Snapshot/Error-Endpunkte.
- **`src/dashboard/static/overview-panel.js`**: Neues Modul für den OVERVIEW-Tab (System-Status, Snapshot-Info, Integration, Live-Loop, Runtime Errors).
- **`src/dashboard/static/gate-board.js`**: Neues Modul für den VERIFY/Gate-Tab.
- **`src/dashboard/static/network-tab.js`**: Koordinator für den NETWORK-Tab.
- **`src/dashboard/static/visualizations/`**: Neue Module für Heatmap/Projection, IO-Flow, Population, Dynamics (Raster/Histogram/Layer) und Network Inspector.

### Tests
- Dashboard-Test-Suite: **58 passed**.

## 2026-08-30 — Dashboard Operator-Workbench: Experiment Mode

### Backend
- **`src/dashboard/models.py`**: Neue Dataclasses `ExperimentState` und `ExperimentSession`; `DashboardSnapshot` um `experiment_state` erweitert.
- **`src/dashboard/state.py`**: `set_experiment_mode`, `start_experiment_session`, `stop_experiment_session`, `add_experiment_note` hinzugefügt.
- **`src/dashboard/server.py`**: Neue API-Endpunkte für Experiment Mode:
  - `GET /api/experiment/mode`
  - `GET /api/experiment/sessions`
  - `POST /api/experiment/mode`
  - `POST /api/experiment/session/start`
  - `POST /api/experiment/session/stop`
  - `POST /api/experiment/note`

### Frontend
- **`src/dashboard/static/experiment-mode.js`**: Neues Modul für Operator/Experiment/Debug-Umschaltung, Session-Management, Notizen und Historie.
- **`src/dashboard/static/index.html`**: Mode-Switcher in Topbar + Experiment-Panel im CONTROL-Tab.
- **`src/dashboard/static/styles.css`**: Stile für Mode-Switcher, Experiment-Panel und Session-Liste.
- **`src/dashboard/static/app.js`**: `ExperimentMode` importiert und initialisiert.

### Tests
- **`tests/test_dashboard_experiment_mode.py`**: 7 neue Tests für Experiment Mode.
- Dashboard-Test-Suite: **58 passed**.
## 2026-08-30 — Dashboard Operator-Workbench: Control/Console Entkopplung

### Frontend
- **`src/dashboard/static/control-panel.js`**: Zentrale Control Plane für alle Runtime-Commands (Step, Run, Start, Pause, Resume, Stop, Snapshot, Structural Undo, Auto-Approval); Keyboard-Shortcuts konsolidiert.
- **`src/dashboard/static/console-log.js`**: Gemeinsames, output-only Console-Log-Modul.
- **`src/dashboard/static/operator_console.js`**: Reiner Output + Structural Proposals; redundante Runtime-Command-Handler entfernt.
- **`src/dashboard/static/app.js`**: Importiert `consoleLog` für globale Konsolenausgaben.

### Tests
- Dashboard-Test-Suite (43 Tests) weiterhin grün.

## 2026-08-30 — Dashboard Operator-Workbench Foundation

### Backend
- **`src/dashboard/models.py`**:
  - `ComponentStatus` mit standardisierten Zuständen `enabled/active/degraded/unavailable/error/stale/disabled` und Metadaten `reason`, `last_update`, `source`, `last_error`, `maturity`.
  - `ParameterSchema` mit `value`, `default`, `min`, `max`, `unit`, `description`, `source`, `runtime_mutable`, `requires_restart`, `scientific_sensitive`.
  - `HealthSnapshot` zur Aggregation von Problemen/Warnungen/stale/unavailable.
  - `DashboardSnapshot` erweitert um `components`, `parameters`, `health`.
- **`src/dashboard/health_builder.py`**: Neuer Builder, der aus Runtime-Metriken, Config und Bridge die Komponenten-Status und Health-Probleme ableitet.
- **`src/dashboard/state.py`**: Erweitert um `update_component`, `update_parameter`, `set_health`.
- **`src/dashboard/server.py`**: Neue API-Endpunkte `/api/components`, `/api/components/{name}`, `/api/parameters`, `/api/parameters/{name}`, `/api/health`.
- **`src/main.py`**: Jeder veröffentlichte Snapshot wird via `enrich_snapshot()` mit Komponenten-, Parameter- und Health-Daten angereichert.

### Frontend
- **`src/dashboard/static/state-store.js`**: Zentraler Frontend-State-Store ersetzt panel-individuelle `/api/status`-Aufrufe.
- **`src/dashboard/static/health-drawer.js`**: Health/Problems Drawer mit permanenter Leiste und einblendbarem Drawer.
- **`src/dashboard/static/styles.css`**: Stile für Health-Bar, Drawer, Problem-Listen und Komponenten-Status.
- **`src/dashboard/static/index.html`**: Tabs auf `OVERVIEW | NETWORK | CONTROL | RESEARCH | VERIFY` umgestellt; Health-Drawer-Container ergänzt.
- **`src/dashboard/static/app.js`**: Integriert `dashboardStore` und `HealthDrawer`; `renderStatus` liest aus dem zentralen Store.

### Tests
- Dashboard-Test-Suite (43 Tests) weiterhin grün.
- Allgemeine Test-Suite zeigt vorbestehenden Fehler in `src/storage/checkpoint.py` (`Neuron` ohne `firing_rate_estimate`), nicht durch diese Änderungen verursacht.

## 2026-08-30 — Dashboard Editor Erweiterungen: Shortcuts, Diff, Auto-Save, BibTeX-Editor

### Editor-Erweiterungen
- **`src/dashboard/static/file-viewer.js`**:
  - **Tastaturkürzel**: `Ctrl+S` speichert, `Esc` bricht den Editor ab.
  - **Auto-Save**: Automatisches Speichern alle 30 Sekunden bei aktiven Änderungen.
  - **Diff-Ansicht**: "Diff"-Button zeigt Änderungen gegenüber der Originaldatei farblich an.
  - **Restore from backup**: "Restore"-Button lädt den Inhalt der `.bak`-Datei zurück.
  - Verbesserte Editor-Toolbar mit Diff-, Restore-, Save- und Cancel-Buttons.
- **`src/dashboard/static/bibtex-viewer.js`**:
  - Neuer **Formular-Editor** für `.bib`-Dateien mit feldbasierter Bearbeitung.
  - Auswahl des Entry-Typs (article, book, inproceedings, etc.).
  - Direktes Speichern der geänderten BibTeX-Einträge über den neuen PUT-Endpunkt.
- **`src/dashboard/static/styles.css`**:
  - Stile für Diff-Tabelle (grün/rot), Editor-Action-Buttons, BibTeX-Formular-Editor.
- **`tests/test_dashboard_file_manager.py`**: Zusätzlicher Test für Backup-Erstellung.

## 2026-08-30 — Dashboard File Manager: In-Browser Text & Code Editor

### In-Browser-Editor für Text- und Code-Dateien
- **`src/dashboard/file_manager.py`**:
  - Neue `save_content()`-Methode zum Speichern von Textdateien innerhalb eines konfigurierten Quellverzeichnisses.
  - Automatische `.bak`-Sicherungskopie vor dem Überschreiben.
  - Pfadvalidierung gegen Path-Traversal; Binärdateien werden abgelehnt.
  - Neuer API-Endpunkt `PUT /api/files/save/{path}?source={research|docs}`.
- **`src/dashboard/server.py`**:
  - `do_PUT()` ruft jetzt `register_file_manager_routes()` auf, damit Speicheranfragen erreichbar sind.
  - Neue Hilfsmethode `_read_json_body()` zum Lesen von JSON-Request-Bodys.
- **`src/dashboard/static/file-viewer.js`**:
  - `isFMEditable()` bestimmt, ob eine Datei bearbeitet werden kann.
  - `activateFMEditor()` öffnet einen Inline-Editor mit Save-/Cancel-Buttons.
  - Markdown-Dateien erhalten eine Split-Ansicht mit Live-Vorschau.
  - Speichern erfolgt per `fetch()` gegen den neuen PUT-Endpunkt; bei Erfolg wird die Datei neu geladen.
- **`src/dashboard/static/styles.css`**:
  - Stile für Editor-Wrapper, Split-Ansicht, Textarea, Statusmeldungen und Editor-Toolbar-Buttons.
- **`tests/test_dashboard_file_manager.py`**: Neue Tests für Speichern, Traversal-Schutz, fehlenden Inhalt und Binärdatei-Ablehnung.

## 2026-08-30 — Dashboard File Manager: Media & Office Previews

### Neue Dateiformat-Vorschauen
- **`src/dashboard/static/file-viewer.js`**:
  - **Audio-Player**: Dateien mit `audio/*`-MIME-Type (`.mp3`, `.wav`, `.flac`, `.aac`, `.m4a`, `.opus`) werden mit nativem HTML5-Audio-Player abgespielt.
  - **PDF-Inline-Viewer**: `.pdf`-Dateien werden per `<iframe>` direkt im Dashboard angezeigt, inklusive Download-Button.
  - **XLSX-Tabellenansicht**: `.xlsx`, `.xls`, `.xlsm`, `.ods` werden mit SheetJS geparst und als interaktive Tabelle mit Sheet-Tabs dargestellt.
  - **DOCX-HTML-Vorschau**: `.docx`, `.doc` werden client-seitig mit mammoth.js nach HTML konvertiert und als formatierte Vorschau angezeigt.
  - **TypeScript-Syntax-Highlighting**: `.ts`-Dateien erhalten eigenes Highlighting inklusive TypeScript-Typen (`string`, `number`, `any`, `unknown`, `never`, etc.).
- **`src/dashboard/file_manager.py`**:
  - MIME-Typen und `is_audio`-Flag für Audio-Dateien ergänzt.
  - MIME-Typen für `.pdf`, `.docx`, `.xlsx` ergänzt.
  - `is_spreadsheet` und `is_document` Flags für Dateibaum-Metadaten ergänzt.
- **`src/dashboard/static/styles.css`**:
  - Stile für Audio-Player, PDF-Viewer, Spreadsheet-Tabs, Spreadsheet-Tabelle und DOCX-Vorschau hinzugefügt.
  - BibTeX-Tabellen-Abstände verbessert: größere Padding-Werte, klarere Zeilenabgrenzung, bessere Lesbarkeit.
- **`src/dashboard/static/index.html`**: CDN-Abhängigkeiten für SheetJS (`xlsx`) und mammoth.js (`mammoth`) eingebunden.

### Dateibaum-Icons
- Audio-Dateien erhalten ein 🎵-Icon.
- Tabellen erhalten ein 📊-Icon.
- Word-Dokumente erhalten ein 📘-Icon.

## 2026-08-30 — Dashboard Operator-Workbench Design Decision

### Design Decision: From Feature Dashboard to Operator Workbench

- **Information architecture** moves from module-oriented layout to workflow-oriented
  layout aligned with `observe → understand → modify → verify → document`.
- **Top-level tabs** become: `OVERVIEW | NETWORK | CONTROL | RESEARCH | VERIFY`.
- **OVERVIEW** shrinks to four sections: `SYSTEM`, `NETWORK`, `ADAPTATION`, `HEALTH`.
  Roadmap and integration status move to `RESEARCH`/`VERIFY`.
- **NETWORK** gains subtabs `Live`, `Dynamics`, `Structure`, `Inspector` for progressive
  disclosure from coarse to fine-grained observation.
- **CONTROL** becomes the single workbench for input. `Runtime Control` and
  `Operator Console` are unified; Console becomes output-only log.
- **VERIFY** replaces `RELEASE` and covers `Health`, `Tests`, `Determinism`,
  `Persistence`, `Integration`, `Evidence Freshness`, `Release Gate`.
- **Health/Problems** becomes a permanent, cross-cutting concern (top-right status
  bar + right/bottom drawers) instead of hidden panels.
- **Parameter system** introduces `current / configured / default` semantics,
  runtime-mutable flags, restart requirements, and pending-change workflow.
- **Status model** standardizes component states: `enabled`, `active`, `degraded`,
  `unavailable`, `error`, `stale`, `disabled`, each with `reason`, `last_update`,
  `source`, `last_error`, `maturity`.
- **State store** centralizes dashboard state instead of letting every panel fetch
  independently.
- **Experiment Mode** adds `Operator / Experiment / Debug` switch with logged
  experiment metadata and extra debug instrumentation.
- **Frontend modularization** target: `app.js` limited to bootstrap, routing,
  module lifecycle, global health, global state; domain logic split into
  `overview/`, `network/`, `control/`, `console/`, `research/`, `verify/`,
  `components/`.

## 2026-08-30 — Dashboard Cleanup & Alpha.5 Hygiene

### Dashboard-Informationsarchitektur vereinfacht
- **`src/dashboard/static/index.html`**:
  - `OVERVIEW` entdoppelt: Roadmap und Integration-Status entfernt; neue
    **Active Profile**-Card.
  - `CONTROL & CONSOLE` entdoppelt: `Runtime Control` umbenannt zu
    **Runtime Configuration** und auf Loop-Size, Delay und Self-Organization
    reduziert. Operator Console bleibt die zentrale Bedienfläche für Step,
    Run, Pause, Resume, Stop, Snapshot, Undo, Console Log und Proposals.
  - Gemeinsame Loop-Size für `Run N Ticks` aus Runtime Configuration.
- **`src/dashboard/static/control-panel.js`**: Entfernt redundante
  Steuerbuttons (Step/Run/Pause/Stop/Snapshot); behält Konfiguration und
  Self-Organization.
- **`src/dashboard/static/operator_console.js`**: `Run N Ticks` liest jetzt
  die gemeinsame `#loop-size`; Shortcuts auf `Ctrl+Shift+R` = Run,
  `Ctrl+Shift+P` = Pause, `Ctrl+Shift+Space` = Stop harmonisiert.
- **`src/dashboard/static/styles.css`**: Stil für `loop-size-hint` hinzugefügt.
- **`src/dashboard/static/app.js`**: Header-Kommentar auf die aktuellen fünf
  Hauptbereiche aktualisiert.

### Repository-Hygiene
- **`tmp_append.py`** und **`src/dashboard/static/_build_viewer.py`** entfernt.

### Dokumentation & Evidence
- **`docs/08-roadmap/TODO.md`**: Verifikationshinweis als **STALE** markiert;
  aktueller Fast-Suite-Stand (397 passed / 0 failed) und offener A/B/C-Fehler
  dokumentiert.

### Tests
- **`tests/test_restore_determinism_abc.py`**: Fehlendes `--digest-k`
  Argument für Path-C-Worker ergänzt (worker startet wieder). A/B/C bleibt
  aufgrund der A/B-Divergenz nach Restore offen.

## 2026-08-30 — BibTeX Viewer für Literaturverwaltung im Dashboard

### Neues Feature: Dedizierter BibTeX-Viewer
- **`src/dashboard/static/bibtex-viewer.js`**: Neues ES-Modul für strukturierte BibTeX-Darstellung.
  - Parser für BibTeX-Entries (`@article`, `@book`, `@inproceedings`, etc.)
  - **Tabellarische Ansicht**: Sortierbare Tabelle (Autor, Titel, Jahr, Typ, Key) mit Spalten-Kopf-Klick
  - **Code-Ansicht**: Raw-BibTeX mit Syntax-Highlighting (umschaltbar per Button)
  - **Zitierfunktion**: "Cite" kopiert `(Autor, Jahr)`, "Bib" kopiert den BibTeX-Eintrag
  - **Export**: "Copy all" kopiert alle Einträge, "Download" lädt als `.bib`-Datei herunter
  - **DOI-Link**: Öffnet `doi.org/…` in neuem Tab
  - **Validierung**: Prüft Pflichtfelder, Jahreszahl (4-stellig), DOI-Format; zeigt Warnungen an
  - **Footer-Statistiken**: Anzahl Entries, Artikel, Bücher, Inproceedings, mit DOI
- **`src/dashboard/static/file-viewer.js`**: `.bib`-Dateien werden automatisch mit dem neuen BibTeX-Viewer geöffnet (statt Raw-Code-Ansicht).
- **`src/dashboard/static/styles.css`**: Umfangreiches BibTeX-Styling (Toolbar, Tabelle, Badges, Action-Buttons, Footer-Statistiken).

## 2026-08-30 — Research Registry Validation Hardening

### Tests
- **`tests/test_research_registry.py`**: Strukturelle Tests für die Research-Registry überarbeitet und erweitert.
  - Bugfix: `test_no_duplicate_ids_across_files` prüft jetzt tatsächlich auf Duplikate (vorher tautologische Assertion).
  - Bugfix: `test_no_duplicate_ids_within_each_file` zählt jetzt echte Vorkommen statt `pass`.
  - Neu: ID-Format-Test für Quellen (`SRC-{AUTHOR}-{YEAR}`).
  - Neu: Referenz-Tests für Literaturangaben in Fragen, Quellenangaben in Claims und Fragenreferenzen in Quellen.
  - Neu: Pflichtfeld-Test für alle Registry-Typen.

### Registry-Daten
- **`research/registry/sources.yaml`**: Fehlende Quellen `SRC-WATTS-STROGATZ-1998` und `SRC-BARABASI-1999` ergänzt, die von `RQ-SNN-003` referenziert wurden.

## 2026-08-30 — Viewer Improvements: Decoupling + Missing File Types + YAML Highlighting

### Viewer als eigenständiges Overlay-Element
- **`src/dashboard/static/index.html`**: Viewer (`fm-viewer`) ist jetzt standardmäßig ausgeblendet (`fm-viewer-hidden`) und öffnet sich als Overlay-Panel über der Sidebar, wenn eine Datei angeklickt wird.
- **`src/dashboard/static/app.js`**: Close-Button (✕) im Datei-Header. Klick schließt den Viewer und die Sidebar nimmt wieder die volle Breite ein.
- **`src/dashboard/static/styles.css`**: Viewer hat jetzt `z-index: 10`, Akzent-Rahmen und eine Übergangsanimation. Sidebar expandiert auf `flex: 1` wenn Viewer verborgen ist.

### Fehlende Dateitypen ergänzt
- **`src/dashboard/static/app.js`**: Neue Code-Dateitypen: `.bib` (BibTeX), `.patch`, `.rst`, `.tex`, `.sh`, `.bat`, `.ps1`, `.dockerfile`, `.cmake`, `.makefile`, `.txt`. JSON-Erkennung jetzt über `ext.endsWith('.json')` — fängt auch `.schema.json` und `.ipynb` ab.
- **`src/dashboard/static/index.html`**: Neue Filter-Chips für BibTeX und Patch.
- `.bib`-Dateien werden jetzt als Code (Syntax-Highlighting) statt als Plain Text angezeigt.
- `.patch`-Dateien werden jetzt als Code statt als Plain Text angezeigt.
- `.schema.json`-Dateien werden jetzt als JSON (mit Formatierung) statt als Plain Text angezeigt.

### YAML Syntax-Highlighting
- **`src/dashboard/static/app.js`**: Neue `renderFMYaml()` Funktion mit Syntax-Highlighting für YAML-Dateien. Farbliche Unterscheidung von: Keys (blau), Strings (orange), Kommentare (grün), Booleans (blau), Zahlen (hellgrün), Null-Werte (grau), List-Marker (gelb), Anchor/Alias (lila), Dokument-Separatoren (grau).
- **`src/dashboard/static/styles.css`**: 12 neue CSS-Klassen für YAML-Token-Farben im VS Code Dark Theme-Stil.

### Multi-Language Code Syntax-Highlighting
- **`src/dashboard/static/app.js`**: Neue `renderFMCode()` Funktion mit Syntax-Highlighting für alle Code-Dateitypen. Unterstützt 17 Sprachen:
  - **Python** (`.py`): Keywords, Builtins, Dekorateure, f-Strings, Magic Methods
  - **JavaScript/TypeScript** (`.js`, `.ts`): Keywords, Builtins, Template Literals
  - **HTML** (`.html`): Tags, Attribute, Entities
  - **CSS** (`.css`): Selektoren, Properties, Values, !important
  - **Shell/Batch/PowerShell** (`.sh`, `.bat`, `.ps1`): Keywords, Builtins, Variablen
  - **TOML/Config** (`.toml`, `.cfg`, `.conf`, `.ini`): Sections, Keys, Booleans, Datum
  - **XML** (`.xml`): Tags, Attribute, CDATA, Entities
  - **BibTeX** (`.bib`): Entry-Typen, Felder, Querverweise
  - **Patch/Diff** (`.patch`): Diff-Marker, Hunks, Add/Delete
  - **LaTeX** (`.tex`): Commands, Math-Umgebungen, Labels
  - **reStructuredText** (`.rst`): Directives, Roles, Sections
  - **Dockerfile**: Instructions, Variablen
- **`src/dashboard/static/styles.css`**: 25 neue CSS-Klassen für Code-Token-Farben (VS Code Dark+ Palette): Kommentare (grün), Keywords (blau), Builtins (cyan), Strings (orange), Zahlen (hellgrün), Dekorateure (gelb-grün), Tags (blau), Attribute (gelb), Selektoren (gelb), Properties (hellblau), Variablen (cyan), Sections (gelb), Diff-Marker (rot/grün), Hunk-Header (lila).

## 2026-08-29 — Dynamics Tab + Collapsible Architecture

### Neuer Dynamics Tab (Spike Raster, Rate Histogram, 5D Layer Explorer)
- **`src/dashboard/static/index.html`**: New "📈 Dynamics" tab with three panels:
  - **Spike Raster**: Canvas-drawn scatter plot of recent spike times (last 100 ticks) for the most active neurons. Shows spike density and firing patterns over time.
  - **Feuerraten-Histogramm**: Bar chart showing the distribution of firing rates across all neurons. Includes mean (μ) and standard deviation (σ) overlay, plus silent/active neuron counts.
  - **5D Layer Explorer**: Interactive slice through the 5D space. User selects dimension (Z, d4, d5), layer value via slider, and display kind (activity, energy, membrane). The heatmap updates in real-time.
- **`src/dashboard/static/app.js`**: New `initDynamicsTab()`, `refreshSpikeRaster()`, `drawSpikeRaster()`, `refreshRateHistogram()`, `drawRateHistogram()`, `refreshLayerExplorer()`, `drawLayerSlice()` functions. Lazy-initialized when tab is first clicked.
- **`src/dashboard/static/styles.css`**: New styles for raster, histogram, and layer explorer panels with dark theme canvas backgrounds and slider controls.

### Backend: Rate Histogram & Spike Raster Endpoints
- **`src/dashboard/live_projection.py`**: New `RateHistogramData`/`compute_rate_histogram()` — computes firing rate distribution with 30 bins, mean/median/std statistics, and silent/active counts.
- **`src/dashboard/live_projection.py`**: New `SpikeRasterData`/`compute_spike_raster()` — extracts recent spike times from the activity accumulator window for the most active neurons.
- **`src/dashboard/server.py`**: New `GET /api/live/histogram` and `GET /api/live/raster` endpoints.

### Tab-Architektur: Lazy Loading für Performance
- Dynamics Tab wird nur initialisiert, wenn der Benutzer ihn das erste Mal anklickt. Keine Canvas-Rendering-Last im Dashboard-Tab.
- Alle Dynamics-Panels haben eigene Refresh-Intervalle (2s Raster/Histogram, 3s Layer Explorer).

### Documentation
- `docs/changelog.md`: This entry.
- `docs/todo.md`: Added new API endpoints to truth sources list.

## 2026-08-28 — Dashboard Hardening + Engine Attach Fix

### Dashboard Disconnect Hardening
- **`src/dashboard/server.py`**: `_send_json()` now wraps the entire HTTP response emission (send_response, send_header, end_headers, wfile.write) in a single try/except for BrokenPipeError, ConnectionResetError, ConnectionAbortedError. Previously only wfile.write was protected.
- **`src/dashboard/server.py`**: `_handle_exception()` immediately returns for client disconnect errors at the top of the method, preventing a second write attempt on a dead socket.
- **`tests/test_dashboard_disconnect_hardening.py`**: 6 new regression tests covering disconnect at every stage of response emission.

### Engine Attach Fix (one confirmed cause of restore divergence)
- **`src/storage/core_restore.py`**: `restore_full()` now calls `.attach()` on created homeostasis and learning engines. Without attach(), the engines were passive — they existed but were not registered as post-step hooks. This was one confirmed cause of Path C divergence in the A/B/C protocol.
- After this fix, A and C match at K (restore point), but still diverge during K→N due to synapse list order after file restore affecting learning engine iteration.
- **B/C protocol not yet fully compliant** until fresh-process proof passes (see below).

### Restore A/B/C Protocol Correction
- **`tests/test_restore_determinism_abc.py`**: Complete protocol rewrite:
  - Path B now uses production `restore_full()` and asserts the restored network is a **different object**.
  - Path C now uses a real **subprocess** (`tests/_restore_worker.py`) — C1 runs 0→K in-process, C2 runs via `subprocess.run()` in a fresh Python process.
  - Stimulus schedule is now **absolute ticks** 0..N-1, serialized as JSON, shared by A, B, and C2.
  - All artifact proof fields are **machine-measured**, never hardcoded.
  - Artifact includes `pid_C1`, `pid_C2`, `config_sha256`, and all proof booleans.
- **Results**: `fresh_process_is_real=True` (PID 27804 vs 30296), `production_restore_path_used=True`, B==C. But A still diverges from B/C — the restore itself produces a different final state than uninterrupted running.

---

## 2026-08-28 — Hugging Face Repository Preparation

### New Files for Hugging Face
- **`HF_README.md`**: Hugging Face-spezifische README mit YAML Frontmatter (license, tags, pipeline_tag) und angepasstem Inhalt für die Hugging Face Platform.
- **`.huggingface/metadata.yaml`**: Repository-Metadaten für huggingface_hub (library_name, tags, card-info).
- **`.huggingface/space_config.yaml`**: Konfiguration für einen optionalen Hugging Face Space (Docker-basiert, Port 8765).
- **`.huggingface/README.md`**: Dokumentation zur Nutzung des Hugging Face Repositories.
- **`.github/workflows/sync-huggingface.yml`**: GitHub Actions Workflow zur automatischen Synchronisation von GitHub → Hugging Face.

### Infrastructure
- **`.gitattributes`**: Erweitert um Git LFS-Konfiguration für große Dateien (`.b5d`, `.ckpt`, `artifacts/`, Bilder, Model Weights).

---

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

---

## 2026-08-29 — Dashboard Enhancement Sprint (Part 3)

### IO-Fluss Visualisierung (New Feature)
- **`src/dashboard/live_projection.py`**: New `IOFlowData` dataclass and `compute_io_flow()` function that analyzes signal propagation from input cells through hidden layers to output cells. Returns per-layer activity rates, neuron counts, and propagation status.
- **`src/dashboard/server.py`**: New `GET /api/live/io-flow` endpoint that reads directly from the live network. Uses the TelemetryFrameStore's ActivityWindowAccumulator for rolling window rates.
- **`src/dashboard/static/index.html`**: New IO-Fluss panel with three-layer flow visualization (Input → Hidden → Output), activity bars, rate displays, and propagation status badge.
- **`src/dashboard/static/app.js`**: New `refreshIOFlow()` function polling `/api/live/io-flow` at 2s intervals. Updates flow bars, layer stats, and propagation badge.
- **`src/dashboard/static/styles.css`**: New `.io-flow-panel`, `.io-flow-grid`, `.io-flow-layer` styles with color-coded layer borders (input=teal, hidden=blue, output=amber).

### Populationen-Übersicht (New Feature)
- **`src/dashboard/live_projection.py`**: New `PopulationData`/`_PopulationEntry` dataclasses and `compute_population_data()` function that groups neurons by type (excitatory, inhibitory, sensory_input, motor_output) with per-population statistics.
- **`src/dashboard/server.py`**: New `GET /api/live/population` endpoint returning population metrics including E/I ratio.
- **`src/dashboard/static/index.html`**: New Population panel with dynamic card grid showing per-type stats and active-fraction progress bars.
- **`src/dashboard/static/app.js`**: New `refreshPopulation()` function polling `/api/live/population` at 2s intervals. Renders population cards with rate, energy, membrane V, and activity bars.
- **`src/dashboard/static/styles.css`**: New `.population-panel`, `.population-card`, `.population-bar` styles with color-coded progress bars per population type.

### Verbesserte 5D Isometrische Projektion
- **`src/dashboard/static/app.js`**: Enhanced `draw5DProjection()` with isometric floor grid, axis labels (X, Y), Z-range legend, and 5D dimension info overlay. Better visual depth perception with grid dots and glow effects.

### Documentation
- `docs/ROADMAP.md`: Added Dashboard Enhancement Sprint section with 4 completed items.
- `docs/changelog.md`: This entry.
- `docs/todo.md`: Added new dashboard API endpoints to truth sources list.

### Verification Freshness Restored
- All 5 verification artifacts now share the same `tested_tree_digest`.
- `tests/test_baseline.json`: 379 passed, 0 failed, 2 skipped.

### Baseline
- `tests/test_baseline.json`: 379 passed, canonical tree digest.
- All structural and determinism artifacts regenerated with matching digests.

---

## 2026-08-26 — Live Visualization Correctness Sprint (Part 3)

### Critical Bug Fixes

1. **`unpack_coords` correction** — `LiveProjectionService` now uses `src.core.spatial_index.unpack_coords()` (the canonical packed-5D decoder) instead of a custom `_unpack_coord()` that treated neuron IDs as linear row-major indices. This was the root cause of neurons appearing in wrong spatial bins.

2. **Activity is now a real firing-rate estimate** — Replaced `1.0 / max(1, age)` (recency of last spike) with `1.0 / window` (firing rate over the activity window). The old implementation gave identical activity to neurons with very different spike counts if their last spike was equally recent.

3. **Empty bins = null, not 0** — Bins with no neurons now return `None` in the `values` array, with a corresponding `mask` boolean array. The range (min/max/mean) is computed only over non-empty bins. This prevents empty regions from distorting the color scale.

4. **Aggregation semantics are now correct** — `_final_value()` dispatches correctly:
   - `mean`: sum/count
   - `sum` / `spike_count`: raw sum (no division)
   - `max`: stored max value (separate accumulator)
   - `active_fraction`: active_count / total_count

5. **MAX works with negative values** — Changed MAX accumulator initialization from `0.0` to `float("-inf")`. Membrane potentials (-70mV to -50mV) now correctly resolve their maximum.

6. **Dimension validation** — `dim_x` and `dim_y` must differ and be in 0..4. Raises `ValueError` otherwise.

7. **TelemetryFrame** — Introduced `capture_frame()` that atomically captures all neuron/synapse state from a single tick into an immutable `TelemetryFrame`. The `LiveProjectionService.project()` reads from the frame, not directly from the live network, preventing incoherent reads across a concurrently stepping simulation.

### Tests
- **`tests/test_live_projection.py`**: Expanded from 12 to 24 tests. New tests cover:
  - Known 5D coordinate lands in expected bin (H)
  - Empty bin is null, not 0 (I)
  - Mask matches null values (I)
  - MAX with negative membrane potentials (J)
  - Spiking vs silent neuron activity difference (K)
  - TelemetryFrame tick/neuron/synapse coherence (L)
  - Invalid dimension axes and values (M)


