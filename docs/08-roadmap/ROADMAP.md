# Brain-5D Development Roadmap

**Canonical roadmap for current `main`**  
**Baseline:** `brain5d-core 0.5.0a7`  
**Updated:** 2026-09-07

## 2026-09-07 GitHub/Hugging Face mirror synchronization

- Refreshed the current baseline in the project, documentation and Hugging Face READMEs.
- Kept GitHub `main` as the canonical source and documented the Hugging Face mirror as a derived publication target.
- Updated the optional mirror workflow to publish a fresh one-commit source snapshot with Git LFS objects, avoiding rejected binary blobs from inherited history.

## 2026-09-07 Hugging Face Space

- Prepared the Docker entrypoint for the integrated dashboard on `0.0.0.0:8765`.
- Added Docker Space metadata and published the live dashboard as `superdigger/Brain-5D-Space`.
- Added the Space repository to the automatic GitHub-to-Hugging-Face synchronization workflow.

## 2026-09-07 Space API rate-limit handling

- Added a shared JSON response parser that reports HTML/429 proxy responses as API errors.
- Reduced dashboard polling frequency automatically on `*.hf.space` deployments.

## 2026-09-07 Full-stack dashboard E2E verification

- Added an executable Chromium Playwright suite for batch selection, per-protocol Seeds/Ticks editing, aggregate workflow output and Footer progress.
- Covered workspace routing, responsive shell overflow and box-state minimize/maximize behavior at 1440, 1024 and 390 pixel viewports.
- Made the registered per-protocol batch Seeds/Ticks inputs editable so the tested workflow contract is available to operators.
- Verified `npm run test:e2e`: 5 passed and `python -m pytest tests -q`: 825 passed, 5 skipped.

## 2026-09-07 Release timeline restoration

- Restored a documentation-backed Product Timeline in the Release workspace.
- The dashboard merges dated milestones from TODO, ROADMAP and CHANGELOG and keeps source provenance visible.
- Checklist completion remains derived from the source Markdown rather than copied into frontend code.
- The Release workspace now separates completed history, current Alpha.7 work and planned backlog into three timeline lanes.
- Release navigation now separates Gate, version history, current preview, chronological Timeline, and the three canonical project documents.
- Historical Git tags extend the visible release range from 0.1.0 through the current development node.
- Release document actions delegate to the existing File Viewer so Markdown, text, JSON and other supported formats keep one rendering path.

## 2026-09-07 Full-stack runtime phase profiling

- Added canonical RuntimeTelemetry phase slots for learning, homeostasis, structural, embodiment, Neural Symbiosis/MSBA, dashboard telemetry and storage.
- Added an external phase-recording API for runtime hooks and exposed active/total phase coverage in the Runtime dashboard panel.
- Inactive subsystem phases remain explicit `0.0` DATA rather than inferred measurements.

## 2026-09-07 Neuron/synapse scaling profile

- Extended `scripts/benchmark_ladder.py` with explicit connections-per-neuron, actual synapse counts and synapse throughput.
- Generated a bounded 100/500/1000-neuron profile with two connections per neuron; the artifact remains a performance measurement, not scientific evidence.

## 2026-09-07 RQ-SNN-001 clean-freeze rerun and AIRR retry

- Executed the exact frozen `sustained_activity_stability_v1` protocol as `EXP-SNN-001-R5` from a clean worktree: 20 runs, 10 seeds, 100,000 ticks per run, zero runtime errors and `dirty=false` provenance.
- Corrected semantic classification so the dedicated RQ-SNN-001 protocol is `DIRECT_MATCH`; Human Review and EVID promotion remain open.
- Attempted append-only AIRR retries for `EXP-GEN-0033`; local Ollama runs produced fallback/timeout or schema-invalid role outputs, so AIRR-2026-0003 remains review-pending and non-evidence.

## 2026-09-07 Pacing-only determinism proof

- Added a deterministic controller batch comparison proving target-Hz configuration does not alter ticks, spikes or state digest when simulated inputs and `dt` are identical.
- The proof uses synchronous bounded batches, isolating pacing configuration from simulation semantics.

## 2026-09-07 Runtime pacing benchmark

- Added `scripts/runtime_pacing_benchmark.py` for bounded low-rate, targeted and unlimited RuntimeController measurements.
- Benchmark artifacts record target/achieved Hz, realtime ratio, `dt`, tick cost, phase profile and simulation tick without making a scientific performance claim.

## 2026-09-07 Hard protection and ordering gates

- Added fail-closed thermal-safety, fan-failure and persistence-failure trips that force `SURVIVAL` and block learned gateway allocation regardless of utility.
- Locked the protection order to reduce plasticity first, freeze it at criticality, and preserve thermal sensing, persistence and storage integrity.

## 2026-09-07 Separate energy contribution accounting

- Added component-level normalized energy accounting for sensor, encoder, spikes, synaptic events, plasticity, structural events, memory, I/O and adapter contributions.
- Preserved the aggregate estimate while exposing the component breakdown as DATA.

## 2026-09-07 Energy provenance classes

- Added explicit provenance classes for normalized model units, calibrated joule conversions, direct telemetry measurements and unavailable values.
- Preserved measured and estimated joules as separate fields with an explicit non-equivalence flag.

## 2026-09-07 Preregistered increased-dimensional projection controls

- Added `PROTO-MSBA-PROJECTION-001` with structured 5D baseline and external 8D/16D projection controls.
- Required explicit projection mapping and prohibited productive-core dimension migration in the protocol contract.

## 2026-09-07 Dimension-shuffled 5D control

- Added a deterministic `5d_shuffled` control arm that preserves dimensions, graph topology, seed and tick contract while permuting the three-node coordinate embedding.
- Exposed control classification in run metrics without treating the shuffled embedding as productive N-D core support.

## 2026-09-07 Epistemic layer separation in workflows

- Added a shared machine-readable `epistemic_layers` contract to workflow JSON, manifests and API results.
- Reports now separate UI state, DATA, EVID and post-hoc interpretation; EVID remains explicitly uncreated until its gates pass.

## 2026-09-07 Embodiment treatment provenance

- Added deterministic `DATA_ONLY` provenance records binding adapter identity, projection mode/dimensions, gateway configuration and normalized energy coefficients.
- Provenance records require preregistration and human review and cannot promote themselves to EVID.

## 2026-09-07 Digital payload checksum persistence

- Added JSON provenance persistence for digital `SymbolFrame` payloads with SHA-256 checksum, payload size, codec, sequence and source provenance.
- Declared checksum persistence in the MSBA scientific boundary without copying the raw payload into the provenance record.

## 2026-09-07 Dynamic embodiment connection coverage

- Added API transition coverage for a sensor changing from available/active to unavailable/inactive.
- Added frontend contract coverage that clears stale organ details when a selected connection disappears; real browser E2E remains open because Chromium is unavailable in this environment.

## 2026-09-07 Experiment-only host telemetry observations

- Added an opt-in provider to the regulation runner so host telemetry is recorded only as an explicit `host_telemetry` experiment condition, with raw readings, typed signals and missing-value semantics preserved.

## 2026-09-07 Missing and uncertain sensor conditions

- Classified malformed numeric/boolean sensor values as `unknown` and propagated uncertainty through thermal and continuity drives without treating raw presence as valid telemetry.

## 2026-09-07 Peripheral adapter mutation boundary coverage

- Added a negative catalog test proving a peripheral adapter is not executed during registration or publication and cannot silently change canonical core or research state through that boundary.

## 2026-09-07 Real-body platform failure-path coverage

- Added Windows-compatible regression coverage for absent optional `psutil` sensors and unavailable `os.getloadavg`, preserving explicit unknown values without fabricated readings.

## 2026-09-07 Live telemetry propagation coverage

- Added HTTP integration coverage for unavailable telemetry (`503`) and stale frame metadata flowing from `TelemetryFrameStore` through `OperatorBridge` and the live projection API.

## 2026-09-07 Operator bridge control-boundary coverage

- Added regression coverage proving unknown structural proposals do not create decisions or history records and unknown runtime commands return explicit errors.

## 2026-09-07 Dashboard batch error-path coverage

- Added an HTTP regression test proving invalid batch protocols return a structured `400` JSON response.

## 2026-09-07 Evidence-engine edge coverage

- Added regression coverage proving dirty source trees and mismatched source-freeze digests cannot produce validated EVID promotion, even with a human review artifact.

## 2026-09-07 Regulation recovery experiment executed

- Executed frozen `closed_loop_regulation_v1` / `PREREG-REG-002` as `EXP-REG-0002-R1`.
- Completed 40 runs across 20 seeds and regulation-off/on arms at 128 ticks with zero runtime errors.
- Regulation-on reduced pressure-phase spikes from 15 to 5 and increased recovery-phase spikes from 21 to 25; recovery-ratio means were 5.0 versus 1.4.
- Results remain review-pending because source provenance is dirty and human review is required.

## 2026-09-07 Recurrence/propagation validation executed

- Executed frozen `recurrence_map_v1` / `PREREG-REC-001` as `EXP-REC-0001-R1`.
- Completed 300 runs across 20 seeds, five recurrent weights including the zero control, and three delays at 256 ticks.
- Observed immediate decay, transient recurrence and persistent-to-window classes without runtime errors; human review and EVID promotion remain open.
- Added regression coverage for the registered grid and its persistence classifications.

## 2026-09-07 Dashboard batch HTTP contract coverage

- Added HTTP coverage for the experiment workflow catalog route and batch POST route.
- The route contract now verifies structured workflow responses independently of browser automation.
- Batch service tests cover sequential order, per-protocol parameters and partial failure isolation.

## 2026-09-07 Batch service contract coverage

- Added automated coverage for sequential protocol order, per-protocol Seeds/Ticks and child failure isolation.
- Aggregate JSON/Markdown workflow reports are covered independently of browser availability.
- Browser-level interaction coverage remains a separate environment-dependent gate.

## 2026-09-07 Current-head verification and protocol contracts

- Fixed the stale frontend ExperimentMode lifecycle contract.
- Updated the operational protocol contract test for the new frozen `RQ-SNN-001` stability protocol.
- Current head verification: 796 passed, 5 skipped, 0 failed.

## 2026-09-07 Batch route verification

- Added an HTTP contract test for the workflow catalog and batch POST routes.
- Current head verifies structured batch responses independently of browser availability.

## 2026-09-07 Dissertation results synchronization

- Added the verified Brain-5D experiment results to `KI_Die_geliehene_Intelligenz_Kontrollverlust_Embodiment_Dissertationsbasis.docx`.
- The DOCX now distinguishes technical completion, exploratory/replication status, dirty-tree provenance and pending human review.
- A repeatable updater is retained at `scripts/update_dissertation_results.py`.

## 2026-09-07 Failed experiment retries repaired

- `independent_replication_v1` failed because the valid preregistration mode `REPLICATION` was missing from the manifest governance enum; this is now supported.
- `learning_interference_screen_v1` failed because neuronal transient state was not reset between declared independent task episodes; the reset is now protocol-scoped and preserves learned weights.
- Retries completed successfully as `EXP-REPL-0001-R1` and `EXP-LIFE-0001-R1` with zero runtime errors.

## 2026-09-06 Registry-driven sequential workflow

- The Experiment-Workflow now plans all catalog entries by default and executes selected experiments sequentially.
- Operational protocols use their registered seed expressions and tick budgets automatically.
- Exploratory entries use bounded Runtime-Ticks diagnostic defaults; per-entry plan values are visible and read-only.

## 2026-09-06 Batch result visibility

- Batch start now shows immediate running state, persistent result text and explicit errors in the workflow dialog/output area.
- Successful batch dialogs close only after the aggregate workflow report has been rendered.
- Footer status now shows the batch as a live test run and preserves the completed workflow result.

## 2026-09-06 Exploratory experiment artifacts

- Exploratory Runtime-Ticks runs now write the same visible experiment artifacts as normal runs: manifest, report, `DATA/runs.json` and `summary.md`.
- Batch results include the child summary path and explicit `EXPLORATORY` / `test_run` markers.

## 2026-09-06 Batch execution options and exploratory start

- Batch execution now accepts per-protocol seed and tick settings from the dialog.
- Operational-only batches no longer require a runtime bridge; exploratory selections require it and use bounded runtime ticks.
- The dialog shows all 48 catalog questions, provides all/none selection, and no longer disables exploratory entries.

## 2026-09-06 Exploratory workflow execution

- Exploratory research questions can now be selected and executed through the batch workflow as explicit `runtime_ticks_v1` diagnostic runs.
- Questions without a registered hypothesis use the explicit `EXPLORATORY-UNSPECIFIED` marker; no evidence or confirmatory claim is implied.
- The batch endpoint now attaches exploratory selections to the runtime controller instead of rejecting them as unknown operational protocols.

## 2026-09-06 Experiment workflow selection repair

- The batch dialog now renders all Research Catalog questions, not only questions with an operational protocol.
- Questions without a frozen operational protocol remain visible as disabled `EXPLORATORY` entries rather than disappearing.
- Batch start errors and completion results are shown in the dialog/workflow output.

## 2026-09-06 Experiment workflow UI activation

- Activated the existing Experiment-Workflow button and dialog in the Research workspace.
- The `batch_workflow_v1` protocol selection now opens the same start/cancel options dialog.
- Selected registered protocols are submitted to `/api/experiment/workflow/batch`; the aggregate JSON/Markdown report is shown in the workflow result area.

## 2026-09-06 EXP-GEN-0033 replication

- Re-ran the complete science suite as `EXP-GEN-0033-R1` without modifying the original experiment.
- The replication completed 57 runs, 100,000 requested ticks, `SATISFIED` tick validation and zero runtime errors.
- Deterministic data, statistics and a transparent fallback AIRR report are archived for the replication.

## 2026-09-06 AIRR missing-artifact recovery

- Added a safe AIRR fallback for schema-invalid or unavailable AI role responses.
- Existing valid role analyses are reused; missing reviewer/writer roles become explicit `analysis_unavailable` records instead of deleting the deterministic data analysis.
- Repaired `EXP-GEN-0033` with a reviewable AIRR JSON/Markdown report while keeping scientific evidence disabled.

## 2026-09-06 RQ-SNN-001 operationalization and long-run result

- Added frozen operational protocol `sustained_activity_stability_v1` with 100,000 ticks, ten independent seeds, no-input control, tonic-drive treatment, burn-in, windowed traces, finite-state/topology gates and explicit thresholds.
- Final replication `EXP-SNN-001-R2` completed 20 runs with 0 runtime errors and 20/20 preregistered stability passes.
- The result is operational and reviewable, but not promoted to scientific EVID: the recorded source tree is dirty and mandatory human review remains pending.

## 2026-09-06 Live experiment footer status

- The Footer now receives the running workflow's real experiment ID, progress percentage and status label from `brain5d:experiment-progress`.
- Periodic dashboard refreshes no longer overwrite an active workflow with `inactive / no session`.

## 2026-09-06 Runtime & Wesen grid readability

- Runtime & Wesen now uses explicit grid areas for left state controls, the central body map, right inspection controls and the full-width Neural Symbiosis row.
- The Embodied Multi-Network Interface is no longer squeezed into a single leftover column.
- Symbiosis cards reflow from three to two to one column across desktop, tablet and mobile widths.

## 2026-09-06 Full-page tabs and responsive box states

- Active workspaces now use the full available page area beneath the fixed application chrome.
- Dashboard panels receive shared `minimized`, `standard` and `maximized` states with responsive controls and Escape-to-standard behavior.
- Dynamically created panels and containers without a native header receive the same presentation controls without changing runtime data contracts.

## 2026-09-06 Wissenschaft Network route restored

- The `Wissenschaft → Neuronales Netzwerk` context route now reveals the active Network workbench instead of being hidden by the retired-workspace CSS rule.
- Network view tabs are available again and continue to respect JavaScript-controlled `hidden` panels.

## 2026-09-06 Fixed application header and primary areas

- Header and the three primary areas `Dashboard`, `Wissenschaft` and `Runtime & Wesen` remain fixed together at the top of the viewport.
- The frontend architecture measures their actual wrapped heights and reserves the matching workspace offset for tablet and mobile layouts.
- Only the active workspace content scrolls; the fixed Footer remains independently reserved at the bottom.

## 2026-09-06 Fixed bottom Footer

- Footer is fixed to the bottom edge of the viewport across desktop, tablet and mobile layouts.
- Body and main reserve the responsive Footer height so the last workspace content remains reachable instead of being covered.
- Safe-area padding is applied for mobile browser insets.

## 2026-09-06 Footer status-bar consolidation

- Footer Runtime controls, tick, command feedback, I/O, experiment, mode and health now share one responsive semantic grid.
- Settings and Release actions are nested in the existing Health area instead of being injected as an extra grid row.
- Footer controls retain accessible click targets at desktop, tablet and mobile widths.

## 2026-09-06 Dashboard CSS consolidation pass II

- Removed the unscoped legacy white Topbar rule that overrode the coordinated shell theme.
- Reduced the Overview chrome to one workspace header, one status rail and the actual data surfaces.
- Replaced remaining fixed research/runtime workbench heights with viewport-aware guardrails and preserved local scrolling only where content requires it.
- Fixed the Embodiment renderer initialization order so unavailable connection lists no longer raise a runtime error.

## 2026-09-06 Canonical dashboard CSS and accessible views

- `src/dashboard/static/styles.css` is now the single CSS entry point and imports the component layers once; runtime stylesheet injection no longer duplicates the cascade.
- Shared tokens, fixed typography roles, surface types and green/orange/red status semantics now cover 4K, 1080p, tablet and mobile layouts.
- Tabs and `hidden` state are authoritative for dense workspaces; tables/logs retain local scrolling and dialogs use the available viewport as a full-size overlay.
- Contrast, reduced motion, larger controls and a persisted Reader view are available from the header; the Wesen morphology timeline is initialized before telemetry arrives.

## 2026-09-06 Footer 6/3 grid alignment

- Footer top row uses six equal columns for product, Runtime, I/O, experiment, mode and health.
- Footer bottom row uses three equal telemetry columns for activity, spikes and resource pressure.
- Symbols and Footer text share fixed compact sizing for consistent alignment.

## 2026-09-06 Compact Footer controls

- Footer symbols use compact 20px controls and reduced spacing.
- Footer labels, vital values and I/O text use a denser 1080p/100% scale while remaining readable.

## 2026-09-06 Fixed 1080p application shell

- Header and the primary menu band are fixed shell regions at the top of the viewport.
- `main` is the only vertically scrollable display area between the chrome regions.
- Footer remains visible at the bottom and does not shrink away at 1080p/100%.

## 2026-09-06 Responsive viewport and footer flow

- Removed the fixed active-tab viewport canvas that only fit a narrow 1080p/67% combination.
- Active workspaces now grow naturally and keep the complete Footer reachable at other resolutions and zoom levels.
- The Experience shell prevents horizontal overflow while preserving the full content area between Header and Footer.

## 2026-09-06 Frontend shell consolidation

- The visible frontend shell now has one navigation owner; legacy tab buttons remain internal routing targets only.
- Footer Runtime controls are static DOM elements with one controller and no dynamically appended duplicate panel.
- Legacy footer CSS and the MAX batch-yield note were removed; current shell styling lives in the Experience stylesheet.

## 2026-09-06 Header and footer shell stabilization

- Header sizing and responsive wrapping are centralized in the final Experience shell rules.
- Footer markup includes global Runtime controls and live I/O while remaining compatible with the flat legacy DOM.
- Footer and header no longer rely on fixed viewport positioning that can clip the document.

This roadmap separates **implemented engineering capability** from **scientific evidence still required**. A feature can be technically complete without its scientific hypothesis being confirmed.

## Current baseline

At the 2026-09-06 research-catalog integration point:

- **791 tests** are collected on current `main`;
- Research Catalog / variable-projection-dimension PR #21 is merged; merge commit `85e7209509b348bf7912dde01d3d9ebb078a2e61`;
- the latest fully completed pre-merge `main` CI baseline was #598 and successful;
- post-merge/current-head CI is the authoritative verification and must complete before the current head is described as fully green;
- Python 3.11/3.12/3.13, Black, Ruff, Pylint, Pre-Commit, Mypy, Pyright, security, Scientific Integrity, wheel and Docker remain mandatory gates;
- historical experiment DATA remains immutable evidence history.

Instrumentation repairs, registry repairs and new architecture produce new observations/experiments rather than rewriting prior DATA/EVID.

## Completed engineering foundation

Current development contains:

- sparse persisted 5D spiking core with delayed event propagation and deterministic RNG/state;
- STDP, signed eligibility and reward-modulated learning;
- homeostatic regulation;
- structural proposal/approval/mutation/journal/undo/recovery;
- `.b5d` storage, delta journaling and checkpoints;
- research registries, manifests, DATA/EVID separation and scientific integrity gates;
- bounded Language Organ / Research Assistant / Cognitive Advisor contracts;
- typed embodiment, actuator authorization, audit chain and deterministic environment loop;
- source-freeze binding across protocol code, configuration and DATA digests;
- productive-learning controls and train/validation/holdout partition enforcement;
- real host interoception and dynamic device discovery without fabricated fallback values;
- adaptive read-only `Wesen` workspace;
- protocol-driven Research Experiment Runner and Science Suite;
- network impulse response instrumentation for ticks, spikes, activated neurons, synaptic events, latency, recurrence and state digests;
- compressed immutable raw-run preservation plus bounded `runs.json` / `analysis/ai_packet.json` projections;
- Neural Symbiosis open-set peripheral network/virtual-area contracts at the embodiment boundary;
- MSBA modality-specific pathways, energy/resource accounting and fail-closed candidate allocation/plasticity;
- fragmentable canonical RQ/H registry with duplicate-ID rejection;
- canonical MSBA RQ/H integration into the normal Experiment Workflow;
- searchable Research Catalog UI that distinguishes operational from exploratory questions;
- repository-wide read-only RQ/H reference audit support;
- configurable MSBA/external projection dimensionality from 1 through 32 while preserving the productive 5D persistence contract.

## Roadmap principle

Development now prioritizes **evidence closure**, research-catalog completeness and controlled experiments over feature accumulation. Reachability in the UI is not evidence and an exploratory runtime run is not a substitute for a hypothesis-specific protocol.

---

## R0 — Research catalog closure and experiment operationalization

**Goal:** every canonical research question and hypothesis is discoverable, link-valid and explicitly classified by experiment readiness.

Implemented foundation:

1. load `questions.yaml` / `hypotheses.yaml` plus deterministic `questions.*.yaml` / `hypotheses.*.yaml` fragments;
2. fail closed on duplicate identifiers;
3. expose MSBA RQ/H entries through the existing Experiment Workflow;
4. provide searchable RQ/H selection instead of relying on a long pulldown;
5. allow exploratory runtime experiments for unmapped questions while preventing accidental EVID promotion;
6. provide a repository-wide reference audit so documentation/code references can be compared with the canonical registry.

Still required:

1. assign every still-unmapped canonical RQ/H a dedicated runner or an explicit `design_pending` state;
2. freeze controls, stopping rules, primary outcomes and preregistrations before confirmatory execution;
3. expose domain/status/evidence/progress facets through the workflow catalog API;
4. publish the registry audit as a CI Markdown/JSON artifact and maintain an explicit, reasoned historical/test-fixture allow-list where appropriate;
5. regenerate only current generated catalog/matrix documents after registry changes, never experiment-owned historical reports.

**Priority:** immediate.

---

## R1 — Post-repair propagation and recurrence validation

**Goal:** establish a clean multi-seed baseline for propagation and recurrent return using the repaired instrumentation.

Tasks:

- execute the registered recurrence/propagation protocol over independent seeds;
- persist complete spike, synapse, latency and digest metrics;
- compare recurrence-on/off using preregistered metrics;
- review before any EVID promotion;
- never rewrite `EXP-GEN-0009` to `EXP-GEN-0012`.

---

## R2 — Productive-learning evidence closure

**Goal:** demonstrate whether learning changes later behavior rather than merely internal weights.

Maintain frozen protocol/configuration, train/validation/holdout separation, pre/post behavior probes, learning-off and sham/replay controls, independent seeds and human-review-gated EVID promotion.

---

## R3 — Closed-loop embodiment evidence

**Goal:** test Sensor → SNN → Actuator → Outcome → Reward as a controlled causal loop.

Required comparisons include replay/open-loop, sensor-loss, degraded-quality and actuator-no-effect conditions. Action acceptance and measured effect must remain separate receipts.

---

## R4 — Neural Symbiosis / MSBA experimental gateway program

**Goal:** test whether the SNN can learn to select, weight or compensate across peripheral neural/virtual areas without compromising the canonical core.

The first implementation stage is **experiment-only**. Production peripheral activation remains out of scope until controls are validated.

Required work:

1. add an experiment-runner adapter that constructs explicitly declared peripheral areas;
2. persist exact adapter/model/version/artifact hashes;
3. persist gateway state independently from core synapse state;
4. keep gateway plasticity disabled outside registered experiments;
5. support matched frozen-gateway, random-gateway, timing-shuffle and information/activity controls;
6. support reduced-, native- and increased-dimensional projection treatments with explicit mappings;
7. execute `RQ-MSBA-E01` through `RQ-MSBA-E05` only after their hypothesis-specific runners and preregistrations exist;
8. evaluate noisy-area suppression and sensor-lesion compensation;
9. compare alternative homeostatic reward/error formulations rather than assuming a signed population mean is valid;
10. require independent seeds and evidence review before claims of learned tool/area use.

---

## R5 — Variable dimensionality and versioned N-D core research

**Goal:** allow dimensionality to become an explicit experimental variable without breaking existing 5D evidence or persistence.

### Implemented safe layer

- MSBA/external projection spaces accept 1–32 dimensions;
- schemas can record projection dimension count separately from productive core dimensions;
- UI exposes the projection-dimension request and states the productive 5D limitation;
- historical 5D neuron IDs and `.b5d` snapshots remain unchanged.

### Required before productive core >5D

1. design and freeze a versioned N-D neuron-ID/storage representation;
2. define backward-compatible `.b5d` readers/migration and canonical state hashing;
3. generalize spatial indexing, coordinate packing, neighbor generation, distances, topology diagnostics and structural locality;
4. add combinatorial-growth/memory guards for high dimensions;
5. prove bit-for-bit equivalence for unchanged 5D configurations;
6. create a preregistered N-D projection sweep first, then a separate productive-core N-D experiment after storage migration;
7. never reinterpret earlier 5D experiments as N-D evidence.

---

## R6 — Time-scale and runtime calibration

Benchmark target Hz, achieved Hz, realtime ratio, `dt` and per-subsystem tick cost. Prove pacing-only changes do not alter deterministic simulated outcomes when `dt` and inputs remain unchanged.

---

## R7 — Scientific test of the 5D organization

Compare full 5D organization against dimension-shuffled, reduced-dimensional, increased-dimensional projection and topology-matched non-spatial controls. Measure propagation, locality, learning efficiency, structural motifs, robustness and computational cost. Increased-dimensional *projection* results must not be mislabeled as productive-core N-D results.

---

## R8 — Self-regulation, continuity and sensor-loss studies

Test homeostasis/interoception as functional control mechanisms without anthropomorphic interpretation. Persist body-boundary/sensor availability changes when they are experimental variables.

---

## R9 — Memory and world-model layer

Only after stable behavioral baselines exist: define explicit memory-state contracts, compare memory-on/off, add prediction/recall metrics, distinguish observation history from learned internal state and external knowledge, and require predictive/behavioral utility before using the term world model.

---

## R10 — Multimodal grounding and knowledge intake

Introduce camera/audio/document/network/knowledge observations through typed provenance-rich SignalFrames and Neural Symbiosis/MSBA adapters. Scientific runs require frozen/replayable source snapshots and explicit treatment identity.

---

## R11 — AI-as-treatment research

Compare no-AI, frozen replay, sham/random proposer and model-family conditions under identical research packets. AI involvement remains provenance-bound and cannot be silently mixed into controls.

---

## R12 — Scaling and performance engineering

Scale only when evidence needs justify it. Profile network/tick cost, memory footprint, storage/journal backpressure and bounded telemetry before adding accelerator/native kernels. Any optimization requires semantic-equivalence tests.

## Release direction

Before a new major research milestone is declared:

1. `main` CI is green;
2. deterministic/recovery contracts remain intact;
3. Scientific Integrity Gate is green;
4. new causal capabilities have matched controls;
5. experiment artifacts are reproducible from recorded manifests;
6. documentation source-of-truth is current;
7. AI/peripheral-network involvement is registered as provenance/treatment where applicable;
8. dashboard/catalog visualization remains separated from scientific evidence;
9. historical DATA has not been rewritten to fit newer instrumentation;
10. any open research operationalization or N-D migration work remains explicitly listed in both TODO and this roadmap.

## Historical roadmaps

Files such as `ROADMAP_ALPHA4.md`, `ROADMAP_ALPHA5*.md`, `ROADMAP_V*.md` and sprint-specific plans are historical records and do not override this roadmap.
