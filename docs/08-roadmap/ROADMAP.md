# Roadmap (Stand 1)

> Last updated: 2026-09-02
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
- [x] Evidence Scope Digests statt globaler Tree-Digest für neue Artefakte
	(Restore, Structural E2E/Live Loop, Runtime Integration; Legacy-Fallback erhalten)
- [x] Green test baseline (zero collection errors)

## v0.5.0-alpha.6 — Operator Workbench & Observable Runtime (released)

> Historical release boundary: source freeze `3025e68`, evidence commit `70a4ee2`, closure commit `8fac75d`, tag `v0.5.0-alpha.6`. Continuous Integration #145/#147/#148 PASSED; release readiness READY.

- [x] Version transition and immutable release registry
- [x] CI recovery: local lint/type/test gates green (Black, Ruff, Pylint ≥9.0, mypy, pyright)
- [x] Operator/Experiment/Debug mode switching wired and tested
- [x] Release readiness model exposes `scientific_gate`, `ci_status`, `release_readiness` separately
- [x] Source baseline: 489 passed, 5 skipped, 0 failed, 0 collection errors
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
- [x] Operator/Experiment/Debug mode selector verified end-to-end
- [x] All 101 public runtime-config parameters exposed conservatively
- [x] Launcher process tree and storage restart hardened
- [x] CI and Hugging Face workflows use Node 24-compatible action majors
- [x] Experiment DATA/EVID provenance generated automatically and fail-closed
- [x] Orthogonal state modes (`operator` / `experiment` / `dev`) and observability profiles (`full` / `scientific` / `minimal` / `compute`) defined and config-validated
- [x] Storage capture policy is explicit; `full_change_scan` remains the correctness baseline until dirty-state emission is complete
- [x] Dashboard API reference documents runtime, experiment, parameter, health and embodiment endpoints
- [x] Local source candidate: 489 passed, 5 skipped, no failures or warnings
- [x] Regenerate baseline and Phase B evidence for the final source candidate
- [x] Source CI #145 green for exact SHA `3025e68`
- [x] Evidence commit `70a4ee2` passed Continuous Integration #147
- [ ] Resolve Sync to Hugging Face #66 before a release that includes Hugging Face publication
- [x] Reproducible 5k-1M benchmark ladder prepared with explicit large-run guard

## v0.5.0-alpha.7 — Embodiment Foundation & Safe Environment I/O (current)
- [x] Research Experiment Runner: Forschungsfrage -> Bedingungen -> Experiment -> Ausfuehren -> Bericht -> Ergebnis; validiert Registry-Links und legt `manifest.json`, `workflow.json` und `report.md` unter `research/experiments/EXP-*/` ab
- [x] Experiment execution is limited to bounded `controller.step(ticks)` calls; optional Ollama assistance has no execution, configuration, or evidence authority
- [x] First STDP pilot: `EXP-STDP-0001` produced `DATA-2026-17` for the isolated pair-timing mechanism; dirty-tree provenance and non-independent repeats exclude it from EVID/Claim/RQ evidence counting
- [x] Current executable experiment sweep completed 2026-09-02: focused protocols and full test suite passed; large storage checks enabled
- [x] Maximum bounded runtime slice completed: 1000 ticks with STDP and homeostasis; long-run evidence remains open because the runtime guard caps a single call at 1000 ticks
- [x] Research evidence is fail-closed for a dirty Git tree; deterministic verification, stochastic experiments and observational experiments have separate evidence modes
- [x] Scientific Research Assistant v0: deterministic ResearchPacket -> schema-validated `AIAR-*` interpretation record; optional local Ollama is read-only and has no runtime, evidence, claim or RQ authority
- [x] OllamaBackend is usable through LanguageOrgan for read-only signal descriptions and monitoring; failures are returned as data
- [x] ResearchPacket/AIAR v1 provenance and `RQ-AIR-001` foundation: packet includes evidence, literature, protocol, limitations and prior AIARs; the 30-case methodology gold standard is registered but not yet executed
- [x] `EXP-AIR-0001` pre-registered: benchmark labels are technically excluded from ResearchPacket, 21 defective plus 9 negative-control cases are fixed, and three model repetitions with exact model/sampling provenance are required
- [x] Effective live-profile verification: `/api/config` publishes the absolute config path and SHA-256; `poc_alpha5_live.yaml` reaches the active runtime with STDP, Eligibility and Reward enabled
- [x] Shared dashboard truth: Health, Overview, Footer, Settings and Release consume the enriched DashboardSnapshot; Network live endpoints consume the same OperatorBridge runtime and report unavailable E/I explicitly instead of hiding populations
- [ ] Replace storage's current full $O(N+E)$ per-tick change scan with a causally complete dirty-state pipeline before treating interactive throughput as a performance result; dirty emitters are now complete, but the fallback remains active
- [x] Evidence feedback updates question maturity (`in_progress` / `inconclusive` / `ready_for_answer`) while final answers remain human-reviewed

> Development began after the Alpha.6 closure commit `8fac75d`. Alpha.6 evidence remains historical and is not evidence for this changed source tree.

- [x] Typed sensor, actuator, environment and connection descriptors
- [x] Read-only Embodiment state/metrics/history/connections APIs
- [x] Animated living-system and dynamic body graph without synthetic telemetry
- [x] Embodiment anatomy maps senses near the brain data core, inner regulation states and changeable extremities without inventing unavailable values
- [x] Clickable read-only detail view exposes published adapter and system fields while marking absent future data as not implemented
- [x] Embodiment contract retains post-action EnvironmentObservation state, reward and termination feedback without inventing self-sensing data
- [x] Dashboard metric aggregation can receive real embodiment feedback without treating adapter discovery as active I/O
- [x] Explicit Full-Stack `EmbodimentPipeline` proves SensorFrame -> SNN -> safe actuator -> EnvironmentObservation feedback with deterministic integration coverage
- [ ] Add configured audio self-hearing and visual self-reflection adapters with measured echo/reflection data
- [x] Pipeline stages can be enabled or disabled from Embodiment elements; configuration intent remains separate from adapter implementation
- [x] Runtime pipeline honors stage configuration and the Embodiment appearance exposes bilateral symmetry as a structural cue
- [x] Embodiment nodes expose their names and concrete data meaning on hover; unavailable capabilities remain marked unavailable
- [x] Fail-closed discovery for compute, storage, network, camera, microphone, display, audio and print queues
- [x] Local/intranet binding and authenticated TLS reverse-proxy template
- [x] First deterministic `EnvironmentAdapter` integrated end-to-end (`DeterministicTargetEnvironment` + safety proof)
- [x] Explicitly configured Experience composition is attached to the canonical runtime when enabled; unknown adapters fail closed and the default remains disabled
- [x] Explicit authorization before actuator execution; unauthorized calls fail closed
- [x] Capability and rate limits enforced per adapter
- [x] Every actuator attempt recorded in a hash-linked immutable audit trail
- [x] Emergency stop and human override enforced below the policy layer

### Alpha.7 exit criteria

Alpha.7 closes only when one deterministic environment proves the complete
observation → encoding → SNN → decoding → bounded action → feedback loop, and
authorization, capability/rate limits, audit, emergency stop and human override
are technically enforced. Read-only device discovery alone is insufficient.

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

## v0.5.0-alpha.8 — Morphological Self-Regulation (next)

- [ ] Chronic structural signals
- [ ] Regional 5D pressure
- [ ] Neuron and synapse age / lifetime
- [ ] Growth budgets and explicit costs
- [ ] Hysteresis and anti-oscillation safeguards
- [ ] Long-horizon morphology stability evidence

## v0.5.0-alpha.9 — Memory, World Model & Embodied Learning

- [ ] Persistent world model linked to provenance
- [ ] Episodic and semantic memory integration
- [ ] Learned body models for authorized external organs
- [ ] Transfer and retention across changing sensor/actuator graphs

## Später

Reward/3-Faktor-Lernen, Pruning, Neurogenese, metabolische Dynamik, performantere Backends, Sharding und große 5D-Räume.
