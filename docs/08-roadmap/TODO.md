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
>   0 failed. A/B/C restore artifact remains failed (`A == B false`,
>   `A == C false`, `B == C true`).
>   The claim "all artifacts share the same tested_tree_digest" is
>   **not currently true** and will be re-established in the next
>   verification round.

## Priorität 1 — Alpha.5 Closure (aktuelle Sprint-Arbeiten)

- [ ] EXP-DET-0001: Determinism A/B/C experiment durchführen
  - Path C `--digest-k` Argument korrigiert (worker startet wieder)
  - A/B-Divergenz nach Restore bleibt offen (siehe Bekannte Probleme)
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
- [ ] Control/Console-Entkopplung: Eine einzige Control Plane; Console wird ausschließlich Output-Log; redundante Step/Run/Pause/Stop/Snapshot-Wege entfernen
- [x] Tab-Restrukturierung: `OVERVIEW | NETWORK | CONTROL | RESEARCH | VERIFY` mit Subtabs
  - `index.html` Tabs umbenannt; VERIFY ersetzt RELEASE
- [ ] Pending-Changes-Workflow: Jede Parameteränderung wird als pending dargestellt (`APPLY`, `APPLY + SAVE PROFILE`, `CANCEL`) mit reversibler Change-History
- [ ] Experiment Mode: Umschaltung Operator / Experiment / Debug mit protokollierter Experiment-Metadaten-Erfassung
- [ ] Frontend-Modularisierung: `app.js` reduzieren auf Bootstrap/Routing/Module-Lifecycle/Global Health; Fachlogik in domain-getriebene ES-Module auslagern

## Priorität 2 — Code-Qualität

- [x] Research-Registry Tests verstärken (Duplikate, Referenzen, Pflichtfelder)
- [ ] Pylance/Pyright clean: alle Typfehler beseitigen
- [ ] type:ignore-Kommentare auf Minimum reduzieren
- [ ] Testabdeckung für neue Module erhöhen
- [ ] Dokumentation zu den neuen API-Endpunkten schreiben

## Priorität 3 — Infrastruktur

- [ ] Hugging Face Space Deployment testen
- [x] CI/CD Pipeline für automatische Tests (GitHub Actions: lint, type-check,
      security, test matrix, build, docker, docs)
- [ ] Benchmark-Ladder für 5k-1M Neuronen vorbereiten

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
- Restore A/B/C: Path C worker startet wieder, aber A != B/C bleibt offen
  (vermutlich Synapsen-Reihenfolge nach Datei-Restore führt zu STDP-Misalignment)
