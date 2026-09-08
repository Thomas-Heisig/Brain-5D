## Naming update — 2026-09-08

MHRN / Multi-Scale Homeostatic Recurrence Network. Publication: Recursive Epistemics / Rekursive Epistemik. [Migration and compatibility](../../NAMING.md). Historical scientific artifacts remain unchanged. Platform completion is recorded separately from requested names.

# MHRN Current TODO

**Canonical TODO for `main`**  
**Baseline:** `brain5d-core 0.5.0a7`  
**Updated:** 2026-09-08

## 2026-09-08 Cross-platform gate and browser contract repair

- [x] Keep manifest-backed `.bib`, `.cff`, `.tex` and `SHA256SUMS.txt` artifacts byte-stable on Windows checkouts.
- [x] Preserve exact viewer text and byte ranges in Windows-focused file-rendering tests.
- [x] Normalize CRLF Markdown before shared browser rendering.
- [x] Isolate browser inventory E2E status from host camera and robotics discovery.
- [x] Verify the complete 15-test Chromium suite after the contract repair.

## 2026-09-07 DOCX viewer surface alignment

- [x] Remove the nested white DOCX card from the viewer modal.
- [x] Align DOCX headings, links, tables, lists and images with the base dashboard CSS.
- [x] Add optional page-break and section markers when Mammoth exposes them without recreating a nested paper surface.

## 2026-09-07 BibTeX links and prose rendering

- [x] Link DOI and publication URL fields in BibTeX previews.
- [x] Reuse base table/link styling for BibTeX output.
- [x] Preserve flowing prose when Markdown source lines are wrapped.
- [x] Reserve stable width for four-digit BibTeX years in both table previews.
- [x] Add RIS export and richer citation style previews.

## 2026-09-07 Functional viewer restoration

- [x] Add a viewer back button and cross-module `openBrain5DFile` API.
- [x] Add read-only central LLM analysis to the viewer.
- [x] Add natural-language read-aloud controls to the viewer, shared file cards and Research Chat.
- [x] Restore sanitized DOCX layout rendering through Mammoth.
- [x] Add safe multicolor syntax rendering for common source formats.
- [x] Add a richer split-pane editor with language-aware preview and conflict diff.

## 2026-09-07 Viewer regression restoration

- [x] Restore full-width Markdown rendering.
- [x] Preserve Human Review and workflow artifact actions when the Docs source was opened previously.

## 2026-09-07 Viewer path compatibility

- [x] Normalize Windows-style separators for preview, raw and document requests.
- [x] Cover encoded workflow artifact paths with an HTTP regression test.

## 2026-09-07 Structured archive and JSON previews

- [x] Add bounded ZIP-compatible archive manifests without extraction.
- [x] Mark unsafe archive member paths in the preview.
- [x] Add a bounded expandable JSON tree to the shared renderer.
- [x] Add browser media metadata (dimensions, duration and codec) without decoding full files.
- [x] Add bounded PDF text/page metadata and optional local Graphviz/PlantUML conversion.

## 2026-09-07 File Viewer format and rendering pass

- [x] Give Mermaid, Graphviz, PlantUML and LaTeX source files explicit preview kinds.
- [x] Render Markdown fenced Mermaid blocks through the shared safe viewer path.
- [x] Improve formula-aware Markdown and notebook cell rendering, including bounded image outputs.
- [x] Keep BibTeX structured previews free of duplicate raw source output.
- [x] Add an optional local Graphviz/PlantUML to SVG converter without sending research sources to a remote service.

## 2026-09-07 GitHub/Hugging Face mirror synchronization

- [x] Refresh the current baseline in `README.md`, `docs/README.md` and `HF_README.md`.
- [x] Document GitHub `main` as canonical and Hugging Face as the derived mirror.
- [x] Configure the optional mirror workflow to publish a fresh LFS-normalized source snapshot.

## 2026-09-07 Hugging Face Space

- [x] Configure the Docker image to start the integrated dashboard on the Space port.
- [x] Publish the dashboard as `superdigger/MHRN-Space`.
- [x] Synchronize future GitHub updates to both the model repository and the Space repository.
- [x] Add a Space-specific smoke check against the local Docker dashboard API.
- [ ] Re-run the public Space browser smoke check after HF proxy rate limits clear.

## 2026-09-07 Space API rate-limit handling

- [x] Handle HTML/429 responses without surfacing `Unexpected token '<'`.
- [x] Increase polling intervals automatically for Hugging Face Space deployments.

## 2026-09-07 Chromium browser checks

- [x] Provide a reproducible Playwright + Chromium installation path.
- [x] Add a self-starting dashboard browser smoke check.
- [x] Run the Chromium smoke check in CI.

## 2026-09-07 Release timeline restoration

- [x] Restore the Release workspace timeline from the canonical TODO, ROADMAP and CHANGELOG documents.
- [x] Merge duplicate dated milestones while preserving their source labels and checklist state.
- [x] Add regression coverage for the timeline data contract and frontend wiring.
- [x] Show one complete past/present/future timeline, including the current release registry and open P0 backlog.
- [x] Organize Release into Gate, Releases, current preview, chronological Timeline, and TODO/CHANGELOG/ROADMAP tabs.
- [x] Include historical tagged releases from 0.1.0 through the current development release.
- [x] Route Release document actions through the single repository File Viewer; do not add parallel text/Markdown renderers.

## 2026-09-07 Dashboard batch HTTP contract coverage

- [x] Test workflow catalog GET route.
- [x] Test batch POST route and structured workflow response.
- [x] Keep browser-independent route coverage for the batch workflow.
- [x] Add browser E2E coverage for the interactive batch dialog.

## 2026-09-07 Batch service contract coverage

- [x] Test sequential protocol execution order.
- [x] Test per-protocol Seeds/Ticks propagation.
- [x] Test partial failure isolation and aggregate workflow reports.
- [x] Add browser E2E coverage for the interactive batch dialog.

## 2026-09-07 Dissertation results synchronization

- [x] Insert verified MHRN experiment results into the dissertation-basis DOCX.
- [x] Preserve dirty-source and human-review limitations in the document.
- [x] Keep the DOCX update repeatable through `scripts/update_dissertation_results.py`.
- [ ] Synchronize future reviewed EVID records into the DOCX after human approval. No reviewed EVID record exists yet.

## 2026-09-07 Failed experiment retries repaired

- [x] Support frozen `REPLICATION` run mode in manifests.
- [x] Reset transient neuron/event state between independent Learning-Interference tasks.
- [x] Re-run `independent_replication_v1` successfully.
- [x] Re-run `learning_interference_screen_v1` successfully.
- [ ] Complete human review and clean-freeze checks for both retry experiments.

## 2026-09-06 Registry-driven sequential workflow

- [x] Execute selected experiments sequentially.
- [x] Derive Seeds/Ticks from each registered protocol.
- [x] Preselect the complete experiment plan while allowing deselection.
- [x] Add browser E2E coverage for the full sequential workflow.

## 2026-09-06 Batch result visibility

- [x] Show immediate running feedback after `Auswahl starten`.
- [x] Show aggregate workflow ID and report paths in the main workflow output.
- [x] Close the dialog robustly after successful report rendering.
- [x] Show batch running/completed/failed state in the Footer.
- [x] Add browser E2E coverage for batch completion UI.

## 2026-09-06 Exploratory experiment artifacts

- [x] Write DATA and summary artifacts for exploratory Runtime-Ticks runs.
- [x] Mark exploratory child results as `EXPLORATORY` and `test_run`.
- [x] Add browser E2E coverage for the visible experiment list refresh after a batch run.

## 2026-09-06 Batch execution options and exploratory start

- [x] Allow operational batches to start without an attached Runtime Bridge.
- [x] Provide independent seed and tick settings per selected protocol.
- [x] Keep all exploratory questions selectable and route them through Runtime-Ticks.
- [x] Add browser E2E coverage for batch start and per-protocol option editing.

## 2026-09-06 Exploratory workflow execution

- [x] Allow exploratory questions to start from the batch dialog.
- [x] Route exploratory selections through bounded `runtime_ticks_v1` execution.
- [x] Preserve explicit exploratory status and prevent evidence promotion.
- [x] Add browser E2E coverage for starting an exploratory selection and reading its report.

## 2026-09-06 Experiment workflow selection repair

- [x] Show all Research Catalog questions in the batch dialog.
- [x] Mark non-operational questions explicitly as exploratory.
- [x] Show batch progress/errors/results in the dialog and workflow output.
- [x] Add browser E2E coverage for the batch dialog interaction.

## 2026-09-06 Experiment workflow UI activation

- [x] Activate the Experiment-Workflow button.
- [x] Open the options popup from the `batch_workflow_v1` protocol selection.
- [x] Submit selected protocols and display the aggregate workflow report.
- [x] Add browser interaction coverage for popup start/cancel and report rendering.

## 2026-09-06 EXP-GEN-0033 replication

- [x] Re-run the complete science suite under a new immutable experiment ID.
- [x] Verify 57 runs, 100,000 ticks, satisfied tick contract and zero runtime errors.
- [x] Preserve deterministic data and fallback report artifacts.
- [ ] Complete human review and clean-freeze verification for the replication.

## 2026-09-06 AIRR missing-artifact recovery

- [x] Generate missing reviewer/writer analysis records for `EXP-GEN-0033`.
- [x] Generate its missing AIRR JSON/Markdown report files.
- [x] Keep deterministic data authoritative and scientific evidence disabled when AI analysis is unavailable.
- [ ] Re-run AI roles with a schema-conforming backend and complete human review. Local Ollama retries remain fallback/timeout or schema-invalid; AIRR-2026-0003 is review-pending and non-evidence.

## 2026-09-06 RQ-SNN-001 operationalization

- [x] Define a frozen sustained-activity protocol with explicit controls, metrics, thresholds and stopping rules.
- [x] Execute 100,000 ticks over ten independent seeds and retain full raw traces.
- [x] Produce deterministic run/statistics/manifests for `EXP-SNN-001-R2`.
- [x] Run the exact frozen protocol from a clean source tree (`EXP-SNN-001-R5`, dirty=false, 20 runs, 10 seeds, 100000 ticks).
- [ ] Complete mandatory human review and decide whether `H-SNN-001-A` merits EVID promotion.
- [ ] Update RQ/H evidence links only after clean-freeze and human-review gates pass.

## 2026-09-06 Live experiment footer status

- [x] Show the active workflow experiment ID in the Footer.
- [x] Show running status, label and progress percentage.
- [x] Prevent dashboard refreshes from resetting the active workflow display.
- [x] Add browser interaction coverage for the live Footer experiment state.

## 2026-09-06 Runtime & Wesen grid readability

- [x] Place body map, state sidebar, inspector sidebar and technical interface in explicit grid areas.
- [x] Keep Neural Symbiosis full-width instead of squeezing it into a single column.
- [x] Reflow technical cards for desktop, tablet and mobile.
- [x] Add browser screenshots for Runtime & Wesen at desktop, tablet and mobile widths.

## 2026-09-06 Full-page tabs and responsive box states

- [x] Treat active workspaces as full-page tab surfaces.
- [x] Add minimize, standard and maximize controls to dashboard boxes.
- [x] Support dynamically created boxes and native-header-less containers.
- [x] Add browser viewport coverage for box-state controls and maximized overlays.

## 2026-09-06 Wissenschaft Network route restored

- [x] Make `Wissenschaft → Neuronales Netzwerk` callable again.
- [x] Restore Network subview tabs without showing hidden panels simultaneously.
- [x] Add browser interaction coverage for the Wissenschaft route.

## 2026-09-06 Fixed application header and primary areas

- [x] Fix Header and `Dashboard` / `Wissenschaft` / `Runtime & Wesen` navigation to the top edge.
- [x] Reserve measured header/navigation height in the workspace.
- [x] Add browser viewport checks for wrapped primary navigation and content offset.

## 2026-09-06 Fixed bottom Footer

- [x] Fix the Footer to the bottom edge of the viewport.
- [x] Reserve responsive Footer space so workspace content is not obscured.
- [x] Support mobile safe-area insets.
- [x] Add browser viewport checks for fixed Footer overlap and mobile wrapping.

## 2026-09-06 Footer status-bar consolidation

- [x] Use one responsive Footer grid for Runtime, I/O, Experiment, Mode, Health and vitals.
- [x] Expose Runtime tick and command feedback in the Footer DOM.
- [x] Remove the duplicate Settings/Release Footer row.
- [x] Add automated browser viewport checks for Footer wrapping and action reachability.

## 2026-09-06 Dashboard CSS consolidation pass II

- [x] Remove the unscoped white Topbar override.
- [x] Reduce Overview to one coordinated header/status/data composition.
- [x] Replace remaining fixed workbench heights with responsive viewport guardrails.
- [x] Fix the Embodiment unavailable-connection initialization error.

## 2026-09-06 Canonical dashboard CSS and accessibility

- [x] Route all dashboard component styles through one canonical `styles.css` entry point.
- [x] Normalize typography, surfaces, status colors and responsive behavior across 4K, 1080p, tablet and mobile.
- [x] Provide full-size popup/dialog behavior, tab-driven visibility and limited local scrolling for dense content.
- [x] Add Reader view, contrast mode, larger controls, focus visibility and reduced-motion support.
- [x] Initialize the Wesen timeline before the first telemetry frame.
- [x] Add browser/E2E viewport checks with the local Chromium runtime.

## 2026-09-06 Footer 6/3 grid alignment

- [x] Arrange the upper Footer row into six equal columns.
- [x] Arrange the lower telemetry row into three equal columns.
- [x] Unify Footer symbol and text sizes.

## 2026-09-06 Compact Footer controls

- [x] Reduce Footer symbols and text density for the 1080p/100% layout.
- [x] Preserve usable Runtime control targets and accessible labels.

## 2026-09-06 Fixed 1080p application shell

- [x] Pin Header and primary menu at the top.
- [x] Use the middle `main` region as the only scrollable display area.
- [x] Keep Footer visible at the bottom for 1080p/100%.

## 2026-09-06 Responsive viewport and footer flow

- [x] Remove the fixed active-tab height tied to one viewport/zoom combination.
- [x] Keep the complete Footer reachable across viewport sizes and zoom levels.
- [x] Preserve the full content area between Header and Footer without horizontal overflow.

## 2026-09-06 Frontend shell consolidation

- [x] Prevent legacy/new navigation flash during load.
- [x] Keep one Footer Runtime control implementation.
- [x] Consolidate Footer CSS into the current Experience shell.
- [x] Remove the obsolete MAX batch-yield note.

## 2026-09-06 Header and footer shell stabilization

- [x] Stabilize Header sizing and responsive wrapping.
- [x] Restore Footer Runtime controls and live I/O fields.
- [x] Remove fixed Footer layout conflicts that clipped the document.

This file contains active work only. Historical Alpha/Sprint TODO files remain traceability records and are not the current backlog.

## Current engineering baseline

- [x] `main` is the canonical development line.
- [x] 835 tests collected on the current head; 800 fast tests passed, 3 platform tests skipped, 32 slow tests deselected, 0 failed.
- [x] Research Catalog / variable-projection-dimension PR #21 merged to `main` at `85e7209509b348bf7912dde01d3d9ebb078a2e61`.
- [x] Latest fully completed pre-merge `main` CI baseline: #598, success.
- [x] Confirm the current-head fast suite after the documentation refresh: 800 passed, 3 skipped, 32 slow tests deselected, 0 failed.
- [x] Unified responsive dashboard design applied across the system.
- [x] Primary frontend reduced to Dashboard, Wissenschaft and Runtime & Wesen while legacy workspaces remain internal routed surfaces.
- [x] `Network` removed from primary frontend navigation and integrated into Wissenschaft.
- [x] Release/Gate moved to a footer action.
- [x] `Embodiment` remains the technical sensor/device/actuator/body-boundary surface and is integrated into Runtime & Wesen.
- [x] Dedicated read-only `Wesen` workspace added.
- [x] PCA-based bounded Neuron Model Viewer, correlation heatmap and parallel-coordinate view added to the scientific Network Workbench.
- [x] Neural Symbiosis and MSBA are embodiment-only/read-only by default and do not silently mutate the canonical SNN core.
- [x] Research DATA v2 preserves raw runs while exposing bounded `runs.json` and `analysis/ai_packet.json` projections.

## P0 — research catalog, hypotheses and experiment reachability

- [x] Make the canonical research registry extensible through deterministic `questions.*.yaml` and `hypotheses.*.yaml` fragments.
- [x] Fail closed on duplicate research IDs across registry fragments.
- [x] Canonically register `RQ-MSBA-E01` through `RQ-MSBA-E05` and `H-MSBA-E01-A` through `H-MSBA-E05-A` so they are visible to the existing Experiment Workflow.
- [x] Preserve `research/registry/msba_experiments.yaml` as the detailed MSBA programme/falsification source rather than rewriting it as historical evidence.
- [x] Generalize research/experiment schema ID validation so extensible families such as `RQ-MSBA-E01` are valid first-class identifiers.
- [x] Add a repository-wide, read-only RQ/H reference audit that reports unregistered identifiers and broken registry links without rewriting historical documents.
- [x] Replace the long research-question pulldown as the primary UX with a searchable Research Catalog, full-text RQ/H matching and an operational-only filter while retaining the underlying select as an accessibility/compatibility fallback.
- [x] Visibly distinguish `OPERATIONAL` frozen/preregistered questions from `EXPLORATORY` questions.
- [x] Route non-operational questions only to the existing exploratory `runtime_ticks_v1` path; never silently substitute an unrelated science runner or promote those runs to EVID.
- [x] Publish a CI Markdown/JSON report from the repository-wide catalog audit and maintain a reasoned historical/test-fixture allow-list; unknown missing IDs fail the job.
- [ ] Operationalize every still-unmapped canonical RQ/H with a dedicated protocol, controls, stopping rule, preregistration and runner before claiming that hypothesis can be confirmatorily tested.
- [x] Decide which non-canonical references remain explicit historical/design references or test fixtures; canonical registry entries remain authoritative.
- [x] Add domain/status/evidence/experiment-progress facets to the Research Catalog through the workflow catalog API.
- [x] Regenerate current research catalog/evidence/open-question reports after every accepted canonical registry change; never rewrite historical experiment-owned reports.

## P0 — variable dimensionality

- [x] Add configurable MSBA/external projection dimensionality from 1 through 32 dimensions without changing productive core neuron IDs.
- [x] Expose the projection-dimension range and the current productive-core 5D limitation explicitly in the MSBA contract and experiment UI.
- [x] Extend experiment schema metadata to distinguish generic/projection dimensions from the persisted productive 5D core.
- [ ] Add a dedicated preregistered N-D projection-sweep experiment so selected dimension counts are causal experiment parameters rather than documentation-only requests.
- [ ] Design a versioned neuron-ID/storage format for productive SNN dimensions above five, including `.b5d` migration, reader compatibility, canonical state digests and rollback.
- [ ] Generalize productive spatial indexing, neighborhood generation, distance functions, topology diagnostics, visualizations and structural-plasticity locality from fixed 5D to N-D only after the versioned format is frozen.
- [ ] Add equivalence tests proving the generalized implementation reproduces legacy 5D behavior bit-for-bit for unchanged 5D configurations.
- [ ] Add scaling guards for combinatorial N-D neighborhood growth and memory cost before enabling high dimensions in productive runtime.

## P0 — repository and frontend verification

- [ ] Verify Neural Symbiosis/MSBA CSS/JS and the Research Catalog are served in integrated runtime and dashboard-only modes on a live host.
- [ ] Verify `Wesen` anatomy + Neural Symbiosis/MSBA rendering with a real connection inventory.
- [ ] Add browser/E2E checks for three-area routing, Neuron Model Viewer 2D/3D interaction, Research Catalog search/filter/selection, pan/zoom, icon-dock navigation, anatomy placement, timeline scrubbing and pipeline reachability.
- [ ] Add a provenance-bound backend projection-job contract before implementing t-SNE/UMAP, cluster scores or cluster export in the Neuron Model Viewer.
- [ ] Expose a true bounded per-neuron firing-rate-Hz field if scientific colour encoding requires Hz rather than the current inspector activity proxy.
- [ ] Implement mutable per-sense controls only after explicit authorization/state-transition contracts exist; keep current connection inventory read-only.
- [ ] Implement holistic Wesen profile load/save/export/delete only after the persisted profile/state contract is versioned.
- [ ] Keep automatic deletion of merged branches enabled/maintained when repository settings/tooling permit.

## P0 — propagation and recurrence evidence

- [x] Measure complete published spike sequences instead of only output spikes.
- [x] Persist tick, neuron, synapse and recurrence metrics in new DATA.
- [x] Add direct verification that fails when ticks, spikes or synaptic delivery are absent.
- [x] Keep historical zero-observation experiments immutable.
- [x] Execute the registered multi-seed recurrence/propagation validation experiment: `EXP-REC-0001-R1`, 300 runs, 20 seeds, full weight×delay grid, 0 runtime errors.
- [x] Add an automated contract test for the recurrence weight×delay grid, seed coverage, tick budget and persistence classes.
- [ ] Independently review the result before any EVID promotion.

## P0 — closed-loop embodiment evidence

- [x] Freeze deterministic Sensor → SNN → Actuator → Outcome → Reward protocols.
- [x] Retain replay/open-loop, sensor-loss and actuator-no-effect controls.
- [x] Store action acceptance and observed effect separately.
- [ ] Promote results to EVID only after protocol and review checks.
- [ ] Expose receipt-linked action/outcome chains to `Wesen` only when backend verification exists.

## P1 — Neural Symbiosis / MSBA experiment runner

- [x] Add an experiment-only adapter that instantiates one declared peripheral network/virtual area.
- [x] Record adapter class, framework, model/version, artifact hash and endpoint identity.
- [x] Persist gateway state separately from canonical SNN synapse state.
- [x] Add frozen-gateway and random-gateway controls.
- [x] Add timing-shuffle and activity-matched information-destroyed controls.
- [x] Implement explicit structured/shuffled/random/reduced-dimensional/increased-dimensional projection treatments for MSBA.
- [x] Run RQ-MSBA-E01 energy-per-useful-information comparisons with matched tasks.
- [x] Run RQ-MSBA-E02 adaptive-vs-fixed-vs-random resource allocation under equal budgets.
- [x] Run RQ-MSBA-E03 adaptive ROI/foveation against centre/random/full-image controls.
- [x] Run RQ-MSBA-E04 digital integrity tests with exact input/output checksums.
- [x] Run RQ-MSBA-E05 modality-loss compensation with fixed/shuffled/no-compensation controls.
- [x] Add noisy-area suppression and sensor-lesion compensation studies.
- [x] Compare signed, absolute, squared and local homeostatic error/reward formulations rather than assuming one default.
- [x] Require independent seeds and preregistration before enabling gateway plasticity, structural growth or adaptive allocation.
- [x] Keep production peripheral activation disabled until experiment controls are validated.

## P1 — energy/resource calibration

- [ ] Calibrate normalized MSBA energy units against measured CPU/GPU/system power where reliable telemetry exists.
- [x] Preserve `measured_joules`, `estimated_joules` and normalized units as separate fields and provenance classes.
- [x] Measure sensor, encoder, spike, synaptic-event, plasticity, structural, memory, I/O and adapter contributions separately where possible.
- [x] Verify that hard thermal/fan/persistence protection cannot be overridden by learned allocation.
- [x] Verify protection ordering: reduce/freeze plasticity before deleting learned structure or disabling safety-critical sensing.

## P1 — runtime/time semantics and performance

- [x] Benchmark target-Hz pacing from low real-time rates to unlimited mode.
- [x] Record target Hz, achieved Hz, realtime ratio, `dt` and tick cost in benchmark artifacts.
- [x] Prove pacing-only changes do not alter deterministic simulation results when simulated inputs/`dt` remain identical.
- [x] Extend profiling to learning, homeostasis, structural, embodiment, Neural Symbiosis/MSBA, dashboard telemetry and storage as distinct measured phases through the canonical RuntimeTelemetry phase contract and external hook API.
- [x] Profile increasing neuron/synapse counts before optimizing kernels.

## P1 — 5D causal/ablation program

- [x] Define preregistered topology-matched 5D-vs-control experiments.
- [x] Implement dimension-shuffled control with a deterministic topology-matched 5D coordinate permutation.
- [x] Implement reduced-dimensional matched embeddings for initial comparisons.
- [x] Add preregistered increased-dimensional projection controls without conflating them with productive-core N-D support.
- [ ] Measure locality, propagation, learning efficiency, structural motifs, robustness and cost at larger scale.
- [ ] Keep dimensionality claims open until ablation evidence exists.

## P1 — evidence and provenance hardening

- [x] Automated documentation link checking in CI.
- [x] Current-doc consistency checks for fixed version/test claims.
- [x] Evidence-engine negative tests for incomplete/mismatched provenance.
- [x] Compact AI-packet provenance and SHA-verified raw-run indexing.
- [x] Persist Neural Symbiosis/MSBA adapter, projection, gateway and energy provenance whenever these components become experimental treatments.
- [x] Persist exact digital checksums for every digital-path experiment.
- [x] Continue distinguishing UI state, DATA, EVID and interpretation in every workflow.

## P1 — high-risk test coverage

- [x] Increase dashboard server routing/error-path coverage with invalid batch protocol response testing.
- [x] Increase evidence-engine rejection/edge-path coverage with dirty-tree and source-freeze mismatch tests.
- [x] Increase operator bridge and control-boundary coverage for unknown proposals and commands.
- [x] Increase real-body platform-specific failure-path coverage for missing optional host APIs.
- [x] Add integration tests for unknown/stale telemetry propagation across API → store → UI.
- [x] Add browser-independent API and static UI coverage for dynamic sensor appearance/disappearance.
- [ ] Add browser-level tests for dynamic sensor/actuator appearance/disappearance.
- [x] Add negative tests proving peripheral adapters cannot silently mutate canonical core/research state.

## P2 — self-regulation and continuity experiments

- [x] Define non-anthropomorphic resource/continuity pressure states in MSBA.
- [x] Integrate measured host telemetry into experiment-only resource observations with explicit missing/unknown values.
- [x] Test missing and uncertain sensor conditions, including malformed numeric and boolean readings.
- [x] Register deterministic recovery comparison with regulation enabled/disabled.
- [x] Execute the recovery experiment across the required seed set: `EXP-REG-0002-R1`, 40 runs, 20 seeds, 0 runtime errors.
- [ ] Independently review `EXP-REG-0002-R1` before any EVID promotion.
- [ ] Test whether body-boundary changes predictably alter behavior under matched conditions.

## P2 — memory/world model

- [ ] Specify memory-state and persistence contracts.
- [ ] Define memory-on / memory-off controls.
- [ ] Add temporal prediction/recall metrics.
- [ ] Separate observation history, learned internal state and external knowledge.
- [ ] Require predictive/behavioral benefit before calling a mechanism a world model.

## P2 — multimodal and knowledge grounding

- [ ] Define typed SignalFrames for camera/audio/document/network/knowledge inputs around the MSBA gateway boundary.
- [ ] Store source, timestamp, digest and trust/provenance metadata.
- [ ] Provide frozen/replayable snapshots for scientific runs.
- [ ] Route peripheral models through Neural Symbiosis/MSBA adapters rather than hidden direct core writes.
- [ ] Compare raw sensory learning against externally structured knowledge conditions.
- [ ] Keep LLM transformation outside causal SNN state unless explicitly registered as a treatment.

## P2 — AI treatment experiments

- [ ] Standardize identical research packets for multi-model comparisons.
- [ ] Add no-AI, frozen replay, sham/random and model-family conditions.
- [ ] Measure proposal/topology fingerprints without allowing hidden writes.
- [ ] Keep AI self-confidence separate from empirical performance metrics.
- [ ] Require treatment identity/provenance in every AI-influenced scientific run.

## Repository/documentation hygiene

- [x] Canonical architecture documentation includes Neural Symbiosis and MSBA contracts.
- [x] Historical dated experiment/changelog artifacts left unchanged.
- [x] Canonical RQ/H registry can grow through independent fragments without rewriting the historical base files.
- [ ] Delete already-merged feature refs when a branch-delete action is available in repository tooling.
- [ ] Prefer one current test-count snapshot in canonical docs and avoid propagating fixed numbers into historical documents.

## Definition of done for a scientific milestone

A milestone is not complete because a UI card is green. It is complete only when:

- [ ] protocol is frozen/preregistered;
- [ ] implementation and controls are tested;
- [ ] runs are reproducible from manifests;
- [ ] data partitions and AI/peripheral-network treatments are explicit;
- [ ] runtime errors/provenance checks pass;
- [ ] evidence artifacts are accepted by the evidence gate;
- [ ] human interpretation distinguishes positive, negative and inconclusive outcomes;
- [ ] documentation records what was actually shown, not what was expected;
- [ ] dashboard visualization, catalog reachability or pipeline reachability is not substituted for experimental evidence.

## 2026-09-07 Main consolidation

- [x] Merge reviewed branches while preserving concurrent File Viewer development.
- [x] Integrate the complete scientific publication and verify all 41 files plus archive.
- [x] Expose publications through the shared research/file renderer without write access.
- [x] Prepare source-bound verification, safe exact-tip branch cleanup and corrected packaging.

See [the consolidation record](MAIN_CONSOLIDATION_2026-09-07.md). Technical CI
and independent scientific review remain separate; existing open research
items above are not closed by this maintenance operation.

- [ ] Operationalize the eight synthesis hypotheses from the publication in
  canonical questions, hypotheses and protocols before treating them as
  executable experiments; their current status is PROPOSED_NOT_REGISTERED.

## Bewusstseinskritik und Kognitionsprogramm (2026-09-07)

- [x] Kritik, Definitionen, Testverträge und Ethik in Publikationsfassung 1.2 integrieren.
- [x] 22 neue kanonische Fragen/Hypothesen mit Quellen und 22 prospektiven Entwürfen registrieren.
- [x] Stimulus-/Auswertungsinstrumente und Start-/Promotionsgrenzen mit Regressionstests ergänzen.
- [ ] Native Adapter einzeln implementieren und unabhängig gegen Referenzaufgaben prüfen; vorher keine Entwürfe als ausführbare Evidenz ausgeben.
- [ ] Unabhängige Methoden-/Ethikexpertise gewinnen; kein bereits bestehendes Gremium behaupten.
- [ ] Geeigneten lizenzierten EEG-Datensatz und ein physikalisch geprüftes Beobachtungsmodell festlegen.
- [ ] Meta-d-prime-Fitter, live-process safe-state controller und authentifizierte externe Reviewkette separat validieren.
- [ ] Echte präregistrierte Versuche mit begründeter Stichprobe, Holdout, Alternativmodellen und unabhängiger Replikation durchführen.
- [ ] DOCX-Export der aktuellen kapitelweisen Edition und Hugging-Face-Deployment gesondert prüfen.
