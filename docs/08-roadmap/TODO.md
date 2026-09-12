## Naming update — 2026-09-08

MHRN / Multi-Scale Homeostatic Recurrence Network. Publication: Recursive Epistemics / Rekursive Epistemik. [Migration and compatibility](../../NAMING.md). Historical scientific artifacts remain unchanged.

# MHRN Current TODO

**Canonical TODO for `main`**  
**Baseline:** `mhrn-core 0.6.0a1`
**Updated:** 2026-09-12
**Current release-blocking backlog:** **0**

## 2026-09-12 Scientific metrics workbench

- [x] Add `GET /api/science/metrics` with bounded live spike-window,
	topology, criticality, learning, homeostasis, statistics and provenance
	groups.
- [x] Expose ISI, CV(ISI), Fano factor, Victor-Purpura, van Rossum,
	Avalanche/Branching, degree/fan-in/fan-out and 5D synapse-distance metrics
	when the retained telemetry window supports them.
- [x] Add Research UI panels for measured values, explicit `UNKNOWN` states,
	falsification annotations, baseline comparison and drill-down controls.
- [x] Keep Lyapunov, UMAP/latent dynamics, null/surrogate statistics,
	confidence intervals, effect sizes, power and causal information flow
	`UNKNOWN` until a validated experiment data contract exists.
- [x] Rebuild the Research scientific surface as a twelve-layer workbench:
	Observatory, Spike trains, Topology/5D, Criticality, Learning,
	Energy/Homeostasis, Statistics, Causality, Embodiment, Provenance,
	Benchmarks and Falsification.
- [x] Wire the Observatory directly into the primary dashboard lifecycle and
	version the frontend assets so stale browser bundles cannot hide the new UI.

## 2026-09-12 Research workspace sub-tabs

- [x] Group Research into Experiments, Files and Registry tabs.
- [x] Keep the experiment runner and quick-access lanes in Experiments.
- [x] Mount research documents and reports in the Registry tab.
- [x] Add browser coverage for Research sub-tab switching.

## 2026-09-12 Sidebar navigation fix and dashboard cleanup

- [x] Link sidebar menu 07 to the runtime Parameter Inspector and keep it
	active while the inspector is open.
- [x] Remove all redundant dashboard elements: experience-status-cluster,
	⌘K button, header-context span, workspace headers, utility bars, ribbons,
	welcome panel, overview-command-bar, overview-actions, overview-status-rail.
- [x] Fix sidebar navigation: `nav` click handler was matching
	`data-primary-area` on `document.body` via `closest()`, causing all
	sidebar global-workspace button clicks to reset to overview.
- [x] Verify all 8 sidebar links navigate to correct destinations.

## 2026-09-11 Full backend API integration into frontend

- [x] Audit all 130 backend API routes and identify 25 endpoints not yet used
	in the frontend.
- [x] Create 7 new ES-module panels covering all 25 missing endpoints:
	cognition, gateway-monitor, docs-browser, research-docs, ai-report-tools,
	learning-prep, structural-inspector, system-info.
- [x] Wire all new modules into `index.js` `init()` and add shared CSS layout
	rules in `shell.css`.
- [x] Verify all relevant dashboard shell tests pass (7/7; 2 pre-existing
	failures from commit 9ef87300 remain unrelated).

## 2026-09-11 Frontend shell accessibility

- [x] Reserve measured fixed header/navigation and footer space so the active
	workspace remains reachable and scrollable at desktop and mobile widths.
- [x] Add a browser regression check for workspace clearance from fixed chrome
	and footer overlays.

## 2026-09-10 Memory / World Model / Behavior Profile foundation

- [x] Connect bounded working and episodic memory to the existing
	`ExperienceEngine` data flow with independent read/write controls.
- [x] Add one-step observation-only prediction before environment feedback and
	record later error and uncertainty without target-state leakage.
- [x] Add atomic, versioned and integrity-checked memory/world-model state plus
	bounded retention and capacity controls.
- [x] Add an operational, non-psychological behavior profile with explicit
	candidate-action influence and auditable bounded updates.
- [x] Construct configured Behavior Profiles in the canonical
	`ExperienceEngine` composition path.
- [x] Expose cognition status, memory, episodes, predictions, world-model and
	Behavior Profile telemetry in the existing Wesen surface.
- [x] Add backend-confirmed Memory Read/Write controls without arbitrary
	memory-content injection.
- [x] Add individual sensor lifecycle routes and UI controls with fail-closed
	adapter/authorization/safety checks and audit records.
- [x] Add experiment-only Gateway lifecycle controls while keeping productive
	Gateway activation locked.
- [x] Add explicit Profile Snapshot binding metadata and central File Viewer
	access, plus a machine-readable backend/frontend coverage contract.
- [ ] Connect coupled cognition state to the canonical runtime snapshot/
	checkpoint boundary and prove pause/resume equivalence.
- [ ] Add registered delayed-information control runs and dashboard/File Viewer
	inspection; engineering implementation is not scientific evidence.

Neural Symbiosis gateway status: **experimental activation implemented; Frozen / Random / Shuffle controls implemented; experimental plasticity implemented; productive activation locked pending validation**.

Profile & Identitaet status: **holistic technical profile implemented; senses / learning / morphology / actuators implemented; save / load / clone / import / export implemented; versioned identity + snapshot binding implemented; autonomous identity mutation locked**.

This file contains **active release-blocking work only**. Long-horizon engineering and scientific work is tracked in [ROADMAP.md](ROADMAP.md) and in the versioned research programme. Moving an item out of this file does **not** claim that the future research has already been performed. Source-freeze CI verification and the subsequent immutable release-record publication are gate/publication steps, not unfinished implementation backlog.

## 2026-09-08 Review and gate closure

- [x] Record the completed AIRR interpretation reviews as append-only `*.review.json` artifacts with reviewer, timestamp, comments and report-content digest.
- [x] Close the stale `AIRR-2026-0003` review-pending TODO: its human interpretation review is recorded on 2026-09-08 as `accepted_as_interpretation`.
- [x] Preserve the epistemic boundary: `accepted_as_interpretation` does not by itself promote DATA or an AI report to scientific EVID.
- [x] Complete the review disposition for `EXP-GEN-0033`: review is complete, while the source experiment remains exploratory and `git.dirty=true`; therefore no EVID promotion is performed.
- [x] Complete the retry-experiment review disposition: `EXP-REPL-0001-R1` remains non-promotable because its recorded run is `git.dirty=true`; `EXP-LIFE-0001-R1` remains an exploratory precursor and is not promoted to EVID.
- [x] Complete the `RQ-SNN-001` review decision conservatively: `EXP-SNN-001-R5` is a valid clean run (`dirty=false`), but no EvidenceEngine `human_review.json` containing a `supports` / `refutes` / `inconclusive` decision is present. No EVID promotion is inferred from an AIRR interpretation review.
- [x] Resolve RQ/H evidence-link synchronization for this closure: no new validated EVID was promoted, so canonical RQ/H evidence links intentionally remain unchanged.
- [x] Resolve dissertation EVID synchronization for this closure: no new promotable EVID record was created, therefore no EVID-derived DOCX mutation is required.
- [x] Keep a future clean replication of dirty/exploratory experiments in the scientific roadmap rather than misrepresenting the historical run metadata.

## 2026-09-08 Quality-gate state

- [x] Resolve **Cross-platform source-freeze digest mismatch on Windows** with Git-canonical text content, explicit dirty/untracked diagnostics and byte-exact binary handling.
- [x] Scientific Integrity Gate passes on the reviewed `main` state.
- [x] Lint/format checks pass: Black, Ruff, Pylint, pre-commit and whitespace/merge-conflict checks.
- [x] Type checks pass: Mypy and both Pyright scopes.
- [x] Documentation checks pass.
- [x] Security checks pass.
- [x] Catalog audit passes.
- [x] Chromium browser smoke and Playwright E2E checks pass.
- [x] Cognition Programme workflow passes.
- [x] Keep scientific validity independent from UI/checklist colour: a green engineering gate never substitutes for experimental evidence.

## 2026-09-08 Hugging Face Space disposition

- [x] Resolve the external Space smoke item as **non-blocking/deferred**, not as a claimed public smoke pass. The local Space-specific smoke contract and Chromium browser CI are green; a future public proxy check remains an operational follow-up when Hugging Face rate limiting permits it.

## Completed platform consolidation

- [x] Replace the t-SNE / UMAP / Clusterexport placeholder with a provenance-bound technical analysis job and Research UI controls.
- [x] Add Research experiment-series launch plus immutable archive/restore organization to the dashboard workflow.
- [x] `main` is the canonical development line and GitHub is the source of truth; Hugging Face is a derived mirror.
- [x] File Viewer is the canonical file renderer shared by Dashboard, Research and Chat surfaces.
- [x] Research Review Inbox is available for completing open interpretation reviews without automatic evidence promotion.
- [x] Runtime, Research, File Viewer, Release/Gate and responsive dashboard integrations have automated browser/API coverage.
- [x] Review records are append-only and preserve reviewer identity, decision semantics, comments and provenance digests.
- [x] Historical experiment artifacts remain immutable; dirty, exploratory or AI-generated records are not rewritten to appear scientifically validated.

## Current development milestone — v0.6 Scaling & Deterministic Performance

The reviewed v0.5.0a7 release gate is closed. Version `0.6.0a1` opens the development line. The engineering acceptance contract is documented in [V06_ACCEPTANCE.md](V06_ACCEPTANCE.md). The final release-record step deliberately remains open until the exact source-freeze CI and release-readiness snapshot are green.

- [x] Freeze the v0.6 compatibility contract for runtime state, snapshots and resumable runs. (`src/storage/v06_contract.py`, frozen B5D V1 + journal V1)
- [x] Add reproducible scaling benchmarks across increasing neuron/synapse counts with explicit memory and tick-cost budgets. (`scripts/benchmark_ladder.py`, `configs/v06_performance_budgets.json`)
- [x] Introduce bounded telemetry/storage compaction so long experiment histories never require an AI consumer to ingest unbounded `runs.json` files. (`src/research/data_v2.py`, bounded compact projection + compressed raw runs)
- [x] Persist one compact current-run packet plus immutable raw-run indexes with SHA-verified provenance. (`DATA/current_run.json`, `DATA/runs_index.json`, deterministic detail extraction)
- [x] Verify deterministic pause/resume/restart identity for the v0.6 runtime contract across supported Python versions. (`tests/test_v06_pause_resume_identity.py`, existing restore/golden-chain tests, CI Python matrix)
- [x] Add performance regression thresholds for RuntimeController, structural phases, learning, storage and dashboard telemetry. (`src/diagnostics/performance_contract.py`)
- [x] Make target-Hz pacing and unlimited mode observable with achieved-Hz/realtime-ratio acceptance criteria. (`tests/test_runtime_controller_alpha4.py`, `tests/test_v06_contract.py`)
- [x] Add clean migration/rollback tests for all v0.6 persisted-state schema changes. v0.6 keeps the frozen binary formats; migration is an explicitly tested byte-identical no-op rather than an untracked rewrite.
- [x] Require full Python 3.11/3.12/3.13, browser, type, lint, security, build and Docker gates before v0.6 release. (`.github/workflows/ci.yml`; aggregate `ci-status`)
- [ ] Generate the v0.6 release record only after the exact source-freeze CI and release-readiness snapshot are both green. **Do not close this checkbox before the post-merge source-freeze gate is green.**

## 2026-09-09 Research workspace cleanup

- [x] Replace move-based experiment archiving with a non-destructive metadata-only work-view index; canonical experiment paths remain stable.
- [x] Preserve one-time restore compatibility for legacy archives that were physically moved by older dashboard versions.
- [x] Split Research into Planen & Ausführen, Läufe & Reihen, Reviews, and Dateien & Analyse work views.
- [x] Extend shared panel state controls to Research workspace surfaces so working areas can be minimized, restored and maximized.
- [x] Keep Review/AIRR handling separate from automatic EVID promotion.

## 2026-09-09 Complete roadmap audit

- [x] Verify the five requested v0.6 acceptance areas against implementation and focused tests: 10 passed.
- [x] Reconcile the roadmap archive description with the current metadata-only archive index and stable canonical experiment paths.
- [x] Separate the remaining v0.6 release publication gate from unfinished engineering implementation.
- [x] Record the remaining research backlog explicitly without promoting engineering completion to scientific evidence.

## 2026-09-09 Development Timeline

- [x] Add the routed Release tab **Entwicklungs-Timeline** without creating a separate application.
- [x] Add the second development bar to the existing chronological release timeline.
- [x] Derive stage classification from structured repository artifacts, implementation paths, tests, verification artifacts, registries and runtime/snapshot data.
- [x] Expose separate technical and scientific markers plus Engineering, Verification and Scientific Evidence scores.
- [x] Keep Stage 10 as a research frontier with `consciousness_claim=unsupported` and no automatic consciousness assertion.
- [x] Add stage detail panels, runtime `unavailable`/`last_observed` handling and responsive browser/API coverage.

## 2026-09-09 Trusted-LAN dashboard access

- [x] Make the standard Windows start wrappers bind the dashboard to `0.0.0.0:8765` for access through the machine's network IP.
- [x] Preserve loopback-only defaults for direct Python startup and support explicit host overrides.
- [x] Document private-network and Windows Firewall requirements; do not claim public Internet exposure is supported.
- [x] Improve terminal startup output with missing version, configuration, runtime mode, URL and process information; keep UTF-8 symbols readable on Windows.
- [x] Report the owning listener PID for occupied dashboard ports, including localized Windows `netstat` states.

### Non-blocking roadmap backlog

These items remain open but are not release blockers for the v0.6 engineering foundation. Their detailed task lists remain in the linked roadmap documents.

- [ ] Close R0 research-catalog operationalization: assign unmapped RQ/H entries or mark them `design_pending`, freeze confirmatory controls/preregistrations, and publish the registry audit artifact. ([ROADMAP.md](ROADMAP.md))
- [ ] Execute and review the evidence programme for R1-R4: recurrence, productive learning, closed-loop embodiment and Neural Symbiosis/MSBA controls. ([ROADMAP.md](ROADMAP.md), [RESEARCH_ROADMAP.md](RESEARCH_ROADMAP.md))
- [ ] Design the versioned productive N-D storage/core migration and its equivalence tests before any productive core beyond 5D. ([ROADMAP.md](ROADMAP.md))
- [ ] Complete the remaining R6-R12 research tracks: time calibration, 5D ablations, regulation/sensor loss, memory/world model, multimodal grounding, AI treatments and evidence-driven scaling. ([ROADMAP.md](ROADMAP.md), [RESEARCH_ROADMAP.md](RESEARCH_ROADMAP.md))
- [ ] Implement the persistent Learning Studio/API and execution-boundary work before productive-learning claims. ([TODO_LEARNING_STUDIO.md](TODO_LEARNING_STUDIO.md))
- [ ] Complete the Alpha.8 recursive loopback, multirate and deterministic parallelism programme only after the release freeze. ([TODO_ALPHA8_RECURSIVE_LOOPBACKS.md](TODO_ALPHA8_RECURSIVE_LOOPBACKS.md))
- [ ] Complete self-model, functional-thinking, metacognition and philosophical research only through preregistered, controlled experiments. ([TODO_SELF_MODEL_THINKING.md](TODO_SELF_MODEL_THINKING.md), [RESEARCH_ROADMAP_POST_THESIS.md](RESEARCH_ROADMAP_POST_THESIS.md))

## Future work is roadmap work, not an open release blocker

The following programmes remain intentionally **future research/engineering**, and are therefore maintained in [ROADMAP.md](ROADMAP.md) rather than as release-blocking TODO checkboxes:

- v0.7 knowledge/learning experiments, interference, retention, transfer and retrieval;
- v0.8 Embodiment / Neural Symbiosis / MSBA validation and governed peripheral adapters;
- v0.9 controlled memory, world model and operational self-model experiments;
- v1.0 stable reproducible research-platform APIs and artifact schemas;
- v1.1 independent replication, cross-hardware reproducibility and control families;
- v1.2 governed adaptive allocation, structural growth, peripheral plasticity, rollback and failure recovery;
- productive N-D core/storage migration beyond the current persisted 5D core;
- additional preregistered projection sweeps, large-scale dimensionality ablations and energy calibration;
- confirmatory follow-ups for exploratory or dirty historical runs;
- additional independent reviews before any future EVID promotion;
- branch-reference deletion when repository tooling exposes a supported delete-ref action.

These items are **not marked completed here**. Their implementation, controls, preregistration, replication and evidence requirements remain governed by the roadmap and research registry.

## Definition of done for future scientific milestones

A scientific milestone is complete only when all applicable requirements are satisfied:

- protocol is frozen/preregistered;
- implementation and controls are tested;
- runs are reproducible from manifests;
- data partitions and AI/peripheral-network treatments are explicit;
- runtime errors and provenance checks pass;
- source cleanliness requirements pass for promotion-eligible runs;
- mandatory human scientific review is recorded in the required schema;
- evidence artifacts are accepted by the evidence gate before RQ/H promotion;
- documentation distinguishes positive, negative and inconclusive outcomes;
- dashboard visualization, review completion or pipeline reachability is never substituted for empirical evidence.

## Current status

**Engineering implementation TODO:** none.  
**Source-freeze verification:** pending the exact final branch/main gate run; this is verification, not implementation backlog.  
**Release-record publication:** intentionally deferred until that verified source freeze is green.  
**Scientific roadmap:** active and intentionally not represented as completed work.

## Connectome-informed embodiment integration (2026-09-09)

- [x] Add canonical questions/hypotheses/source provenance without duplicate RQ-EMB-001, RQ-REG-002 or RQ-MSBA-E05.
- [x] Register six native exploratory joint/SNN screens and six explicitly blocked advanced designs.
- [x] Add bounded reference import, topology controls, body-state sidecars and design/evidence gates.
- [x] Add source-bytecode consistency, uncertainty-aware Wesen telemetry and a scientific supplement.
- [ ] Obtain and independently validate a pinned licensed biological subset; implement exact source-model replication.
- [ ] Validate three-factor sensorimotor learning, frozen/random gateway controls and disjoint holdout.
- [ ] Execute sensor-compensation, homeostasis, efference-copy and morphology-transfer studies after adapter review.
- [ ] Extend Wesen with separately labelled live/replay/reference modes, causal intervention links and File Viewer inspection.
- [ ] Run prospectively reviewed multi-seed confirmatory experiments and independent replication; no automatic EVID promotion.

[Architecture and execution](../02-architecture/CONNECTOME_EMBODIMENT.md) and
[scientific supplement](../../research/publications/2026-09-09_connectome-embodiment_supplement/README.md).

## 2026-09-10 External review integration

- [x] Preserve the 135-question portal and bind its public instrument provenance.
- [x] Connect the Research subtab Probanden & Ethik, read-only readiness API and central File Viewer.
- [x] Separate generated methodological templates from completed human reviews.
- [x] Exclude private response exports and symlinks from repository AI retrieval.
- [ ] Organize independent administration, pilot the instrument and freeze each cohort/wave.
- [ ] Obtain actual qualified reviews and any required institutional ethics decision; a questionnaire alone cannot close these findings.
- [ ] Complete coupled cognition snapshot/restore and controlled SNN-specific learning validation; component screens do not establish these capabilities.

## Empirical evaluation, 2026-09-10

- [x] Execute the available protocol campaign with immutable raw observations, failures and source receipts.
- [x] Add real graph geometry ablations, frozen native association tests, Brian2 conformance and active scaling with explicit amendment.
- [x] Publish manuscript 1.4 and data-bound uncertainty analysis without automatic EVID promotion.
- [ ] Diagnose Brian2 numerical divergence using separately frozen interventions.
- [x] Register operational contracts for the remaining 43 RQs: directly instrumentable questions resolve to dedicated runners; non-instrumented or non-causal questions resolve to explicit `boundary_audit` contracts with `direct_test_of_hypothesis=false`.
- [ ] Replace boundary-audit contracts with validated causal instruments only where scientifically appropriate; protected Connectome/Embodiment designs remain blocked until their native adapter/reference requirements are met.
- [ ] Obtain independent replication, human EVID review and required external ethics decisions.
- [ ] Add NEST/Lava task-matched network/learning benchmarks and long-horizon scaling.
