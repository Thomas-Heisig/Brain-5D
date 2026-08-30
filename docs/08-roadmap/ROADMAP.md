# Roadmap (Stand 1)

> Last updated: 2026-08-30
> Detailed task list: `docs/08-roadmap/TODO.md`

## Stand 1 – abgeschlossenes Zielbild

Verified Observable Core: Raum, Neuronendynamik, Delay-Events, reale Spike-Historie, Diagnose, Topologieprüfung und Observatory.

## v0.5.0-alpha.5 — Integration Hardening (in progress)

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
- [ ] Canonical RuntimeController (remove SimpleController)
- [ ] .b5d snapshot pipeline → heatmap
- [ ] Structural plasticity wired through approval-gated manipulator
- [ ] Evidence Scope Digests statt globaler Tree-Digest
- [ ] Green test baseline (zero collection errors, current baseline is stale)

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

> Blocked until Alpha.5 Integration Gate passes.

### Dashboard Operator-Workbench

- [x] Zentrale Architekturbausteine: `StatusModel`, `StateStore`, `ParameterSchema`, `Health/Problems Drawer`
- [x] Tab-Restrukturierung: `OVERVIEW | NETWORK | CONTROL | RESEARCH | VERIFY`
- [ ] Subtabs in NETWORK (`Live`, `Dynamics`, `Structure`, `Inspector`) und VERIFY (`Health`, `Tests`, `Determinism`, `Persistence`, `Integration`, `Evidence`, `Release Gate`)
- [~] Entkopplung von Control/Console: Console wird Output-Log
  - [ ] ControlPanel als einziger Command Owner; doppelte Runtime-Shortcuts
        aus `OperatorConsole` entfernen
  - [ ] StateStore vollständig integrieren; `app.js` führt keine parallelen
        Status-/Health-Requests mehr aus
  - [ ] Health-State-Semantik korrigieren: `enabled ≠ active`,
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
