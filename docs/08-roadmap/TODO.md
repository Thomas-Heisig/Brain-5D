# Brain-5D — Consolidated TODO

> Last updated: 2026-09-01
>
> Infrastructure: Hugging Face Repository vorbereitet (HF_README.md,
> .gitattributes LFS, .huggingface/ metadata, Space-Konfiguration,
> GitHub→HF Sync Workflow).
> Verification basis:
>   Current verification → tests/test_baseline.json (tree-digest authority)
>   **Historical Alpha.6 baseline (2026-09-01): 489 passed / 5 skipped / 0 failed**
>   at final source-freeze commit `3025e68...`, digest `90439f88...`.
>   **Current development version**: v0.5.0-alpha.7 / 0.5.0a7.
>   Alpha.6 scientific gate: PASSED; Continuous Integration #145/#147/#148:
>   PASSED; release readiness: READY.
>   **A/B/C restore artifact verified** (`A == B == C`).
>   Evidence scope digests are planned but **not yet implemented**; the Gate
>   Builder still uses the global source-tree digest, so UI changes can still
>   mark scientific evidence as `stale`.
>   Runtime start stabilized: UTF-8 console reconfiguration and corrupt
>   delta-journal recovery in `src/main.py`.

## Priorität 0 — Alpha.7 Embodiment Foundation & Safe Environment I/O

- [x] Alpha.6 historical boundary fixed at closure commit `8fac75d` and tag `v0.5.0-alpha.6`
- [x] Alpha.6 immutable release manifest with source/evidence/closure provenance
- [x] Alpha.7 version line and release registry opened
- [x] Read-only Embodiment and connection discovery foundation
- [ ] First deterministic EnvironmentAdapter integrated end-to-end
- [ ] Explicit sensor/actuator authorization enforced
- [ ] Per-adapter capability and rate limits enforced
- [ ] Immutable action audit trail implemented
- [ ] Emergency stop and human override enforced below policy execution

## Alpha.6 Phase B Evidence Freeze (released)

- [x] Source freeze `f1c4df8...` against successful Continuous Integration #141
- [x] Canonical baseline regenerated without production-source changes
- [x] Restore Determinism A/B/C regenerated and verified
- [x] Structural E2E and Structural Live Loop regenerated and verified
- [x] Single-Listener / Runtime integration regenerated and verified
- [x] Determinism Infrastructure regenerated: 7/7 proofs
- [x] EXP-DET-0001 / EXP-STOR-0001 rerun as DATA-2026-15/16 and EVID-2026-15/16
- [x] Claims, hypotheses, evidence links, manifests, registry, and research routes validated
- [x] Gate status regenerated: A 22/22, B 24/24, C 17/17; scientific gate PASSED
- [x] Freeze reopened for dashboard/runtime fixes; release-readiness test now follows the actual scientific-gate result
- [x] Dashboard browser acceptance: version alpha.6, real network values, Health ok, Problems empty, Storage healthy
- [x] OVERVIEW als responsive Operator-Zentrale: Status-Rail, Live-Dynamik, Komponenten, Problems und Bereichsnavigation
- [x] NETWORK, CONTROL, RESEARCH und RELEASE als konsistente Workbenches mit realen Bereichsstatus ausbauen
- [x] CONTROL kausal ordnen: Experimentziel → Ursache → Ausführung → Wirkung → Nachweis; aktuelle RuntimeTelemetry anzeigen
- [x] CONTROL auf 1080p verdichten: Console priorisieren, Structural Live Loop als Leiste, Footer mit aktivem Experiment
- [x] Alle Tabs auf stabile Control-Größe bringen; Network/Release in Unteransichten und Research in logische Schnellzugriffe gliedern
- [x] SCIENTIFIC SETTINGS als eigene Seite: Parameterdomänen, Sensitivität, Mutability, Restart/Pending und Experimentmodus
- [x] Einheitliches 1080p-Design für alle Seiten mit Back/Home/Help, Dark/Light/Kontrast und kompaktem Footer
- [x] Network-Projektionen mit echten Resolution-/Bins-/Sample-Reglern und kompakter Kachelansicht
- [x] Embodiment-Tab auf realem Metrics-Vertrag vorbereiten; unconfigured statt Demo-Daten
- [x] Embodiment Read API (`state`, `metrics`, `history`) und geschlossene Kausalschleife visualisieren
- [x] Animiertes Brain-5D-Wesen als Living-System-Karte mit allen publizierten Quellen und Funktionen integrieren
- [x] Dashboard fuer Localhost/Intranet konfigurierbar machen und sicheren Internetzugriff ueber TLS/Auth-Proxy vorbereiten
- [x] Verbindungsmanager mit realer Compute-, Storage-, Netzwerk-, Internet-, Kamera-, Mikrofon-, Audio- und Drucker-Erkennung samt dynamischem Körpergraph integrieren
- [x] Windows-Launcher gegen lokalisierte tasklist/taskkill-Codepages härten
- [ ] Ersten deterministischen EnvironmentAdapter samt Sensor-/Aktor-Detailpublikation integrieren; erst danach manuelle Aktionen freigeben
- [ ] Rechtevergabe, Audit, Grenzwerte, Not-Aus und Human Override pro realem Adapter implementieren
- [x] NETWORK, CONTROL, RESEARCH, RELEASE and Operator/Experiment/Debug switching verified without browser errors
- [x] All 101 public runtime-config leaves exposed; uncurated values remain fixed/restart-required
- [x] GitHub/Docker actions migrated to Node 24-compatible majors
- [x] Experiment generator records commands/DATA links automatically and fails closed
- [x] Local quality gates: 489 tests, Black, Ruff, Mypy, Pyright, Pylint, Pre-commit, Bandit, pip-audit and build pass
- [ ] Extend evidence freshness authority: generated research evidence currently changes gate-test behavior without changing the canonical source digest
- [x] Commit final source candidate and verify Continuous Integration #145
- [x] Regenerate baseline, Phase B evidence and gate status for `3025e68...`
- [x] Evidence commit `70a4ee2...` and Continuous Integration #147 verified
- [ ] Resolve Sync to Hugging Face #66 if Hugging Face publication is required

## Priorität 1 — Alpha.5 Closure (teilweise offen)

- [x] EXP-DET-0001: Determinismus A/B/C experiment durchführen
  - Path C `--digest-k` Argument korrigiert (worker startet wieder)
  - A/B/C digests are now equal; artifact status = `verified`
  - [ ] Härten: Strenger Fresh-Process-Nachweis
    - P0 pytest orchestrator startet **kein** C1-Netzwerkobjekt im Orchestrator
    - C1 subprocess: `0 → K`, speichert Dateisystem-Artefakte, schreibt PID, terminiert
    - C2 subprocess: liest nur Dateisystem, `restore_full()`, `K → N`, schreibt PID + Digest, terminiert
    - `assert PID_C1 != PID_C2`
    - `assert A == B == C`
    - „completed"-Proofs sind nicht mehr hartkodiert `true`

    > **Status:** Noch nicht vollständig umgesetzt. C1 läuft aktuell noch im
    > Pytest-Prozess; nur C2 wird als Subprozess gestartet. Die
    > `completed`-Proofs im Artifact Writer sind weiterhin hartkodiert `true`.
    > A=B=C ist bewiesen, der maximale strenge C1→exit→C2 Nachweis noch nicht.
- [x] EXP-STOR-0001: Storage persistence experiment durchführen
- [x] Erste DATA-* / EVID-* Artefakte generieren
- [x] Research Catalog aus echten Evidenzen neu aufgebaut
- [x] Dashboard: IO-Fluss Visualisierung finalisieren
- [x] Dashboard: Populationen-Übersicht finalisieren
- [x] Dashboard: 5D Isometrische Projektion verbessern

## Priorität 1b — Dashboard Operator-Workbench Refactoring

> Ziel: Vom funktionsgetriebenen Dashboard zur arbeitsprozess-orientierten
> Operator-Workbench: beobachten → verstehen → verändern → prüfen →
> dokumentieren. Health, Console und Problems werden querschnittlich
> sichtbar, nicht versteckt.

- [x] `StatusModel`: Standardisierter Komponenten-Status (enabled/active/degraded/unavailable/error/stale/disabled) mit `reason`, `last_update`, `source`, `last_error`, `maturity`
  - Implementiert in `src/dashboard/models.py` als `ComponentStatus`
  - Validierungsmengen `VALID_COMPONENT_STATUS` / `VALID_MATURITY`
- [x] `StateStore`: Zentraler Dashboard-State (`runtime`, `network`, `learning`, `homeostasis`, `structural`, `storage`, `telemetry`, `health`, `verification`) statt panel-individueller `fetch`-Aufrufe
  - Frontend-Store `src/dashboard/static/state-store.js`
  - Backend `DashboardSnapshot` erweitert um `components`, `parameters`, `health`
- [x] `ParameterSchema`: Generischer Parameter-Inspector mit Metadaten (`value`, `default`, `min`, `max`, `unit`, `description`, `source`, `runtime_mutable`, `requires_restart`, `scientific_sensitive`)
  - Implementiert in `src/dashboard/models.py` als `ParameterSchema`
  - API-Endpunkte `/api/parameters` und `/api/parameters/{name}`
- [x] Health/Problems Drawer: Permanent sichtbare Leiste + einblendbare Drawer für Fehler, Warnungen, Unavailable-Zustände und stale Daten
  - `src/dashboard/static/health-drawer.js`
  - `src/dashboard/health_builder.py` baut aggregierte Health aus Komponenten
  - API-Endpunkt `/api/health`
- [~] Control/Console-Entkopplung: Grundstruktur vorhanden, Command-Duplizierung
      weitgehend beseitigt
  - `src/dashboard/static/control-panel.js` zentralisiert alle Runtime-Commands
  - `src/dashboard/static/operator_console.js` reiner Output + Proposals
  - `src/dashboard/static/console-log.js` gemeinsames Log
  - [x] `ControlPanel` ist alleiniger Runtime-Command-Owner
  - [x] Runtime-Shortcuts aus `OperatorConsole` entfernt (`OperatorConsole.bindKeyboardShortcuts()`
        verarbeitet nur noch `Ctrl+L` für Console-Clear)
  - [ ] `OperatorConsole` vollständig in `ConsoleLog` + `StructuralProposalPanel`
        zerlegen
- [x] Tab-Restrukturierung: `OVERVIEW | NETWORK | CONTROL | RESEARCH | VERIFY` mit Subtabs
  - `index.html` Tabs umbenannt; VERIFY ersetzt RELEASE
- [x] Pending-Changes-Workflow: Jede Parameteränderung wird als pending dargestellt (`APPLY`, `APPLY + SAVE PROFILE`, `CANCEL`) mit reversibler Change-History
  - Backend: `PendingParameterChange`, `ParameterChangeRecord`, API-Endpunkte `/api/parameters/pending/*`
  - Frontend: `parameter-inspector.js` mit Parameter-Tabelle, Pending-Bar und Change-History
  - Tests: `tests/test_dashboard_pending_parameters.py` (8 Tests)
- [x] Experiment Mode: Umschaltung Operator / Experiment / Debug mit protokollierter Experiment-Metadaten-Erfassung  - Frontend wiring in `app.js`; `ExperimentMode` instantiated on CONTROL tab init
  - Backend API tests: `tests/test_dashboard_experiment_mode.py`
  - Static asset regression tests: `tests/test_dashboard_experiment_mode_wiring.py`
- [x] CI recovery: Black, Ruff, Pylint ≥9.0, mypy, pyright all green locally
- [x] GitHub Actions SARIF permissions and HF sync explicit-failure wiring
- [x] Release readiness model exposes `scientific_gate`, `ci_status`, `release_readiness` separately  - Backend: `ExperimentState`, `ExperimentSession`, API-Endpunkte `/api/experiment/*`
  - Frontend: `experiment-mode.js` mit Mode-Switcher, Session-Start/Stop, Notizen, Historie
  - Tests: `tests/test_dashboard_experiment_mode.py` (7 Tests)
- [~] Frontend-Modularisierung: `app.js` reduzieren auf Bootstrap/Routing/Module-Lifecycle/Global Health; Fachlogik in domain-getriebene ES-Module auslagern
  - [x] StateStore vollständig integrieren: Backend publiziert jetzt- [x] UI-Redesign: Status-Elemente (Experiment-Mode, System-Status, Health-Bar) in always-visible Footer verschieben; Header auf Dark/Light + Accessibility reduzieren; Runtime-Errors in Health-Bar integrieren; Overview für 1080p @ 75% Zoom kompaktieren        angereicherte Snapshots; `/api/state` liefert den vollständigen
        Store; globale State- und Health-Daten kommen aus dem Store.
        Wissenschaftliche Daten (heatmap, raster, projection, Tabellen)
        bleiben separat/lazy geladen.
  - [x] Health-State-Semantik korrigieren:
        - `enabled ≠ active`: Learning/Homeostasis/Structural/Storage
          unterscheiden jetzt `enabled` (Config), `active` (Runtime),
          `disabled` (Config aus) und `unavailable` (Fehlerzustand).
        - `unavailable ≠ disabled`: Komponenten, die in der Config
          deaktiviert sind, melden `disabled` mit `source: config`;
          fehlende/fehlerhafte Komponenten melden `unavailable`.
        - Verification-Status spieglt Gate-Zustand wider
          (`active/stale/failed/pending`), nicht nur Endpoint-Erreichbarkeit.
          Der Health-Builder leitet den Status aus den Gate-Artefakten ab.

## Priorität 2 — Code-Qualität

- [x] Research-Registry Tests verstärken (Duplikate, Referenzen, Pflichtfelder)
- [ ] Pylance/Pyright clean: alle Typfehler beseitigen
- [ ] type:ignore-Kommentare auf Minimum reduzieren
- [ ] Testabdeckung für neue Module erhöhen
- [ ] Dokumentation zu den neuen API-Endpunkten schreiben

## Priorität 1c — Evidence-Freshness & Verification Architecture

> Ziel: Dashboard-/UI-Änderungen dürfen wissenschaftliche Nachweise nicht
> mehr fälschlich als `stale` markieren.

- [ ] Evidence Scopes eingeführt: jeder Nachweis bekommt seinen eigenen
      Digest über die relevanten Dateien
  - `restore_determinism`: `core`, `storage`, `learning`, `homeostasis`,
    relevante Config + Restore-Tests
  - `structural_e2e`: Structural Engine, Coordinator, Manipulator, Journal,
    relevante Tests
  - `runtime_integration`: Controller, Bridge, Main, relevante Tests
  - `dashboard`: `src/dashboard/`, HTML/CSS/JS, Dashboard-Tests
  - `research`: Registry, Schemas, Recorder, Research-Tests
  - `release`: gesamter produktiver Source Tree + komplette Tests
- [ ] Artefakte speichern `scope`, `scope_digest`, `tested_commit` statt
      eines globalen Tree-Digests
- [ ] Gate Builder vergleicht nur den passenden Scope-Digest
- [x] Full Test Baseline neu erzeugt (2026-08-31, 457 passed / 2 skipped / 0 failed)
  - `xfailed` / `xpassed` in `BaselineEvaluation` ausgewertet
  - Source Freeze → komplette Suite → neue `tests/test_baseline.json`
  - Alle Evidence-Artefakte sauber regeneriert

> **Hinweis:** Evidence Scopes sind aktuell noch nicht implementiert. Die
> Artefakte verwenden weiterhin `tested_tree_digest` und der Gate Builder
> nutzt weiterhin `compute_source_tree_digest()` über den gesamten Source
> Tree. Siehe auch `src/dashboard/verification.py` und
> `src/dashboard/gate_status.py`.

## Priorität 3 — Infrastruktur

- [ ] Hugging Face Space Deployment testen
- [x] CI/CD Pipeline für automatische Tests (GitHub Actions: lint, type-check,
      security, test matrix, build, docker, docs)
- [ ] Benchmark-Ladder für 5k-1M Neuronen vorbereiten
- [ ] Repository-Hygiene: Diagnoseartefakte unter `tmp/restore_diag/` und
      `tmp/trace_diag/` aus Source Tree entfernen oder nach
      `research/generated/diagnostics/` mit Provenance verschieben

## Erledigt

- [x] Viewer als eigenständiges Overlay-Element (Close-Button, expandiert bei Bedarf)
- [x] Fehlende Dateitypen ergänzt: `.bib`, `.patch`, `.rst`, `.tex`, `.sh`, `.bat`, `.ps1`, `.dockerfile`, `.cmake`, `.makefile`, `.txt`
- [x] JSON-Erkennung jetzt über `ext.endsWith('.json')` — fängt auch `.schema.json` ab
- [x] YAML Syntax-Highlighting (renderFMYaml mit farblichen Token-Klassen)
- [x] Research-Registry Validierung verstärkt: Duplikate, ID-Formate, Referenzen, Pflichtfelder
- [x] Fehlende Quellen `SRC-WATTS-STROGATZ-1998` und `SRC-BARABASI-1999` in `research/registry/sources.yaml` ergänzt
- [x] Multi-Language Code Syntax-Highlighting (renderFMCode für 17 Sprachen)
- [x] Dashboard-Informationsarchitektur auf 5 Bereiche vereinfacht
- [x] File-Viewer als eigenständiges Modul `src/dashboard/static/file-viewer.js` ausgekoppelt
- [x] CONTROL & CONSOLE entdoppelt: Runtime Configuration + Operator Console
- [x] OVERVIEW entdoppelt: Roadmap/Integration-Status entfernt, Active Profile hinzugefügt
- [x] Repository-Hygiene: Placeholder-Dateien `tmp_append.py` und
      `src/dashboard/static/_build_viewer.py` entfernt

## Bekannte Probleme

- Dashboard State Publishing darf niemals die Simulation blockieren (bereits gelöst)
- Self-Organization nur über canonical Coordinator->Approval->PlasticityEngine Pfad
- Storage ist per Konfiguration deaktiviert (poc_config.yaml)
- Evidence-Freshness-Modell ist zu grob (Evidence Scope Digests noch nicht implementiert)
- ~~Test-Baseline `tests/test_baseline.json` ist alt~~ (neu erzeugt am 2026-08-31)
- `tmp/restore_diag/` und `tmp/trace_diag/` enthalten eingecheckte State-Dumps
  und müssen entweder `.gitignore`d oder nach `research/generated/diagnostics/`
  verschoben werden
- Restore A/B/C: A/B/C Digests sind gleich (`verified`); Fresh-Process-Nachweis
  noch nicht vollständig erfüllt (C1 läuft aktuell im Pytest-Prozess)
- Evidence Scopes sind noch nicht implementiert; Gate Builder nutzt weiterhin
  den globalen Source Tree Digest
