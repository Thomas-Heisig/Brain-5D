# Brain-5D — Consolidated TODO

> Last updated: 2026-08-30
>
> Infrastructure: Hugging Face Repository vorbereitet (HF_README.md,
> .gitattributes LFS, .huggingface/ metadata, Space-Konfiguration,
> GitHub→HF Sync Workflow).
> Verification basis:
>   Current verification → tests/test_baseline.json (tree-digest authority)
>   **STALE:** Last recorded baseline is 2026-08-28 (418 passed / 3 failed /
>   2 skipped, commit `39a4b6e...`).
>   Current fast-suite run (2026-08-30, excluding slow+restore): 397 passed /
>   0 failed.
>   **A/B/C restore artifact is now verified** (`A == B == C`, tested at
>   commit `93620ecc...`). The actual restore determinism issue is resolved.
>   However, the global tree-digest freshness model is too coarse: changes
>   under `src/dashboard/` (styles, JS, HTML) currently invalidate
>   restore/structural evidence artifacts even though the scientific proof
>   is unaffected. This must be replaced by scoped evidence digests.

## Priorität 1 — Alpha.5 Closure (aktuelle Sprint-Arbeiten)

- [x] EXP-DET-0001: Determinism A/B/C experiment durchführen
  - Path C `--digest-k` Argument korrigiert (worker startet wieder)
  - A/B/C digests are now equal; artifact status = `verified`
  - [ ] Härten: Path C1 muss im pytest-Prozess laufen, C2 als neuer
        Subprozess; „completed“-Proofs dürfen nicht hartkodiert `true` sein
- [ ] EXP-STOR-0001: Storage persistence experiment durchführen
- [ ] Erste DATA-* / EVID-* Artefakte generieren
- [ ] Research Catalog aus echten Evidenzen neu aufbauen
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
- [~] Control/Console-Entkopplung: Grundstruktur vorhanden, aber
      Doppel-Shortcut-Bug noch offen
  - `src/dashboard/static/control-panel.js` zentralisiert alle Runtime-Commands
  - `src/dashboard/static/operator_console.js` reiner Output + Proposals
  - `src/dashboard/static/console-log.js` gemeinsames Log
  - [ ] `ControlPanel` als einziger Command Owner: Runtime-Shortcuts
        (`Ctrl+Enter`, `Ctrl+Shift+R`, `Ctrl+Shift+P`, `Ctrl+Shift+Space`,
        `Ctrl+Shift+N`) aus `OperatorConsole` entfernen
  - [ ] `OperatorConsole` auf reines Output/Proposal-Panel reduzieren oder
        in `StructuralProposalPanel` überführen
- [x] Tab-Restrukturierung: `OVERVIEW | NETWORK | CONTROL | RESEARCH | VERIFY` mit Subtabs
  - `index.html` Tabs umbenannt; VERIFY ersetzt RELEASE
- [ ] Pending-Changes-Workflow: Jede Parameteränderung wird als pending dargestellt (`APPLY`, `APPLY + SAVE PROFILE`, `CANCEL`) mit reversibler Change-History
- [ ] Experiment Mode: Umschaltung Operator / Experiment / Debug mit protokollierter Experiment-Metadaten-Erfassung
- [ ] Frontend-Modularisierung: `app.js` reduzieren auf Bootstrap/Routing/Module-Lifecycle/Global Health; Fachlogik in domain-getriebene ES-Module auslagern
  - [ ] StateStore vollständig integrieren: `app.js` darf keine eigenen
        `/api/gate/status`, `/api/structural/errors`, `/api/integration/status`,
        `/api/snapshot-info`, `/api/heatmap`-Requests mehr starten; nur
        globale State- und Health-Daten kommen aus dem Store; große
        wissenschaftliche Daten (heatmap, raster, projection, Tabellen)
        bleiben separat/lazy geladen
  - [ ] Health-State-Semantik korrigieren:
        - `enabled ≠ active` (z. B. Learning: enabled aus Config, activity
          aus `stdp_updates` / `reward_updates`)
        - `unavailable ≠ disabled`
        - Verification-Status muss Gate-Zustand widerspiegeln
          (`active/stale/failed/pending`), nicht nur Endpoint-Erreichbarkeit

## Priorität 2 — Code-Qualität

- [x] Research-Registry Tests verstärken (Duplikate, Referenzen, Pflichtfelder)
- [ ] Pylance/Pyright clean: alle Typfehler beseitigen
- [ ] type:ignore-Kommentare auf Minimum reduzieren
- [ ] Testabdeckung für neue Module erhöhen
- [ ] Dokumentation zu den neuen API-Endpunkten schreiben

## Priorität 1c — Evidence-Freshness & Verification Architecture

> Ziel: Dashboard-/UI-Änderungen dürfen wissenschaftliche Nachweise nicht
> mehr fälschlich als `stale` markieren.

- [ ] Evidence Scopes einführen: jeder Nachweis bekommt seinen eigenen
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
- [ ] Full Test Baseline neu erzeugen (aktuell 2026-08-28, stale)
  - `xfailed` / `xpassed` in `BaselineEvaluation` auswerten
  - Source Freeze → komplette Suite → neue `tests/test_baseline.json`
  - Alle Evidence-Artefakte sauber regenerieren

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
- Evidence-Freshness-Modell ist zu grob: Dashboard-/UI-Änderungen machen
  wissenschaftliche Nachweise fälschlich `stale` (siehe Priorität 1c)
- Test-Baseline `tests/test_baseline.json` ist alt (2026-08-28) und muss neu
  erzeugt werden; `BaselineEvaluation` wertet weder `xfailed` noch `xpassed` aus
- `tmp/restore_diag/` und `tmp/trace_diag/` enthalten eingecheckte State-Dumps
  und müssen entweder `.gitignore`d oder nach `research/generated/diagnostics/`
  verschoben werden
- Restore A/B/C: A/B/C Digests sind jetzt gleich (`verified`); verbleibender
  Vorbehalt: Path C führt C1 im pytest-Prozess aus und nur C2 im Subprozess;
  einige „completed“-Proofs im Artefaktwriter sind hartkodiert `true`
