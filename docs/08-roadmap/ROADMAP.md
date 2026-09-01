# Roadmap (Stand 1)

> Last updated: 2026-09-01
> Detailed task list: `docs/08-roadmap/TODO.md`

## Stand 1 – abgeschlossenes Zielbild

Verified Observable Core: Raum, Neuronendynamik, Delay-Events, reale Spike-Historie, Diagnose, Topologieprüfung und Observatory.

## v0.5.0-alpha.5 — Integration Hardening (released)

> Frozen at commit `0503264` and tag `v0.5.0-alpha.5`. Gate A/B/C: PASSED.

- [x] Single-process launcher, single DashboardServer, OperatorBridge attached
- [x] Frontend lifecycle unified (app.js sole owner, ES modules, no CommonJS)
- [x] Canonical command contract `{"command":"run_ticks","ticks":N}`
- [x] B5D-SEF research API + Research tab in dashboard
- [x] Alpha.5 Integration Gate tab with live checks
- [x] Viewer als Overlay-Panel (Close-Button, Sidebar expandiert)
- [x] Fehlende Dateitypen ergänzt (`.bib`, `.patch`, `.rst`, `.tex`, `.schema.json`, u.a.)
- [x] YAML Syntax-Highlighting (renderFMYaml mit farblichen Token-Klassen)
- [x] Multi-Language Code Syntax-Highlighting (renderFMCode für 17 Sprachen)
- [x] Research-Registry Validierung verstärkt (Duplikate, Referenzen, Pflichtfelder)
- [x] Restore A/B/C determinism verified (`A == B == C`)
- [x] Structural E2E verified
- [x] Structural Live Loop verified
- [x] Canonical RuntimeController (SimpleController removed)
- [x] .b5d snapshot pipeline → heatmap
- [x] Structural plasticity wired through approval-gated manipulator
- [x] Evidence Scope Digests statt globaler Tree-Digest
- [x] Green test baseline (zero collection errors)

## v0.5.0-alpha.6 — Operator Workbench & Morphological Self-Regulation (current)

> Final source freeze `3025e68`; Continuous Integration #145 and regenerated Phase B evidence PASSED. Release readiness: READY.

- [x] Version transition and immutable release registry
- [x] CI recovery: local lint/type/test gates green (Black, Ruff, Pylint ≥9.0, mypy, pyright)
- [x] Operator/Experiment/Debug mode switching wired and tested
- [x] Release readiness model exposes `scientific_gate`, `ci_status`, `release_readiness` separately
- [x] Source baseline: 483 passed, 5 skipped, zero failures/collection errors
- [x] Restore A/B/C, Structural E2E, Structural Live Loop, Single Listener, Determinism Infrastructure verified
- [x] EXP-DET-0001 / EXP-STOR-0001 rerun with complete DATA/EVID provenance links
- [x] Gate A 22/22, Gate B 24/24, Gate C 17/17
- [x] Resolve frozen release-readiness test expectation before evidence-only commit
- [x] Dashboard version, Health/Storage, real Network values and all major tabs verified
- [x] Store-driven responsive Overview command center with readiness, dynamics, components, problems and workspace actions
- [x] Network, Control, Research and Release workbench headers with live summaries and section navigation
- [x] Control cause→execution→effect→evidence workflow with current RuntimeTelemetry mapping
- [x] Single-screen 1080p Control composition, prioritized console, compact Structural proof strip and experiment-aware footer
- [x] Stable viewport-bounded canvas for every desktop tab; Network/Release subviews and Research quick lanes remove page-length layout jumps and footer overlap
- [x] Dedicated Scientific Settings workspace with 101 parameters, domain filters, guardrails and synchronized execution mode
- [x] Unified full-width 1080p design, global Back/Home/Help, Dark/Light/Contrast and compact footer
- [x] Network resolution/bin/sample controls wired to real APIs and compact two-column visualization tiles
- [x] Embodiment workspace prepared against real dashboard metrics without synthetic fallback
- [x] Read-only Embodiment state/metrics/history API and closed perception-action loop visualization
- [x] Animated Brain-5D living-system map connecting all published system sources to one embodied creature
- [x] Configurable local/intranet dashboard binding and authenticated TLS reverse-proxy template for internet operation
- [ ] Compose the first permission-bounded deterministic EnvironmentAdapter and publish sensor/actuator details
- [x] Operator/Experiment/Debug mode selector verified end-to-end
- [x] All 101 public runtime-config parameters exposed conservatively
- [x] Launcher process tree and storage restart hardened
- [x] CI and Hugging Face workflows use Node 24-compatible action majors
- [x] Experiment DATA/EVID provenance generated automatically and fail-closed
- [x] Local source candidate: 489 passed, 5 skipped, no failures or warnings
- [x] Regenerate baseline and Phase B evidence for the final source candidate
- [x] Source CI #145 green for exact SHA `3025e68`
- [x] Evidence commit `70a4ee2` passed Continuous Integration #147
- [ ] Resolve Sync to Hugging Face #66 before a release that includes Hugging Face publication
- [ ] Chronic structural signals
- [ ] Regional 5D pressure
- [ ] Age / lifetime
- [ ] Budgets, costs, hysteresis and anti-oscillation

## Sprint 2A – STDP-Labor

Feature-Flag standardmäßig AUS. Zuerst nur zwei Neuronen:

- PRE vor POST -> Potenzierung
- POST vor PRE -> Depression
- großes Delta-t -> Änderung gegen 0
- Flag AUS -> Stand-1-Verhalten unverändert

## Sprint 2B – Eligibility Trace

Erst nach isolierter STDP-Verifikation.

## Sprint 2C – Homöostase

Schwellen-/Ratenregulation isoliert messen.

## v0.5.0-alpha.6 — Operator Workbench & Morphological Self-Regulation

> Alpha.5 Integration Gate re-closed on 2026-08-31 after dashboard fixes; Alpha.6 work is unblocked.

### Dashboard Operator-Workbench

- [x] Zentrale Architekturbausteine: `StatusModel`, `StateStore`, `ParameterSchema`, `Health/Problems Drawer`
- [x] Tab-Restrukturierung: `OVERVIEW | NETWORK | CONTROL | RESEARCH | VERIFY`
- [ ] Subtabs in NETWORK (`Live`, `Dynamics`, `Structure`, `Inspector`) und VERIFY (`Health`, `Tests`, `Determinism`, `Persistence`, `Integration`, `Evidence`, `Release Gate`)
- [~] Entkopplung von Control/Console: Console wird Output-Log
  - [x] ControlPanel als einziger Command Owner; doppelte Runtime-Shortcuts
        aus `OperatorConsole` entfernt (verbleibend: `Ctrl+L` für Clear)
  - [x] StateStore vollständig integrieren; Backend publiziert angereicherte
        Snapshots; `/api/state` liefert den vollständigen Store
  - [x] Health-State-Semantik korrigieren: `enabled ≠ active`,
        `unavailable ≠ disabled`, Verification-Status aus Gate-Zustand
- [x] Pending-Changes-Workflow für wissenschaftlich reversible Parameteränderungen
- [ ] Experiment Mode (Operator / Experiment / Debug)
- [ ] Domain-getriebene Frontend-Modularisierung in `src/dashboard/static/`

### Morphological Self-Regulation

- Feature-Flag standardmäßig AUS
- Isolierte STDP-Verifikation (zwei Neuronen: PRE vor POST, POST vor PRE, großes Delta-t)
- Eligibility Trace
- Homöostase (Schwellen-/Ratenregulation)

## Später

Reward/3-Faktor-Lernen, Pruning, Neurogenese, metabolische Dynamik, performantere Backends, Sharding und große 5D-Räume.
