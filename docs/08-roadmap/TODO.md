# Brain-5D Current TODO

**Canonical TODO for `main`**  
**Baseline:** `brain5d-core 0.5.0a7`  
**Updated:** 2026-09-06

## 2026-09-06 Wissenschaft Network route restored

- [x] Make `Wissenschaft → Neuronales Netzwerk` callable again.
- [x] Restore Network subview tabs without showing hidden panels simultaneously.
- [ ] Add browser interaction coverage for the Wissenschaft route.

## 2026-09-06 Fixed application header and primary areas

- [x] Fix Header and `Dashboard` / `Wissenschaft` / `Runtime & Wesen` navigation to the top edge.
- [x] Reserve measured header/navigation height in the workspace.
- [ ] Add browser viewport checks for wrapped primary navigation and content offset.

## 2026-09-06 Fixed bottom Footer

- [x] Fix the Footer to the bottom edge of the viewport.
- [x] Reserve responsive Footer space so workspace content is not obscured.
- [x] Support mobile safe-area insets.
- [ ] Add browser viewport checks for fixed Footer overlap and mobile wrapping.

## 2026-09-06 Footer status-bar consolidation

- [x] Use one responsive Footer grid for Runtime, I/O, Experiment, Mode, Health and vitals.
- [x] Expose Runtime tick and command feedback in the Footer DOM.
- [x] Remove the duplicate Settings/Release Footer row.
- [ ] Add automated browser viewport checks for Footer wrapping and action reachability.

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
- [ ] Add browser/E2E viewport checks once a Chromium runtime is available in the development environment.

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
- [x] 791 tests collected on the 2026-09-06 merged research-catalog baseline.
- [x] Research Catalog / variable-projection-dimension PR #21 merged to `main` at `85e7209509b348bf7912dde01d3d9ebb078a2e61`.
- [x] Latest fully completed pre-merge `main` CI baseline: #598, success.
- [ ] Confirm the final current-head `main` CI after the documentation refresh before calling the refreshed head fully green.
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
- [ ] Operationalize every still-unmapped canonical RQ/H with a dedicated protocol, controls, stopping rule, preregistration and runner before claiming that hypothesis can be confirmatorily tested.
- [ ] Add a CI report artifact from the repository-wide catalog audit and decide which historical-only identifiers belong on an explicit allow-list versus the canonical registry.
- [ ] Add domain/status/evidence/experiment-progress facets to the Research Catalog once those fields are exposed by the workflow catalog API.
- [ ] Regenerate current research catalog/evidence/open-question reports after every accepted canonical registry change; never rewrite historical experiment-owned reports.

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
- [ ] Execute the registered multi-seed recurrence/propagation validation experiment.
- [ ] Independently review the result before any EVID promotion.

## P0 — closed-loop embodiment evidence

- [x] Freeze deterministic Sensor → SNN → Actuator → Outcome → Reward protocols.
- [x] Retain replay/open-loop, sensor-loss and actuator-no-effect controls.
- [x] Store action acceptance and observed effect separately.
- [ ] Promote results to EVID only after protocol and review checks.
- [ ] Expose receipt-linked action/outcome chains to `Wesen` only when backend verification exists.

## P1 — Neural Symbiosis / MSBA experiment runner

- [ ] Add an experiment-only adapter that instantiates one declared peripheral network/virtual area.
- [ ] Record adapter class, framework, model/version, artifact hash and endpoint identity.
- [ ] Persist gateway state separately from canonical SNN synapse state.
- [ ] Add frozen-gateway and random-gateway controls.
- [ ] Add timing-shuffle and activity-matched information-destroyed controls.
- [ ] Implement explicit structured/shuffled/random/reduced-dimensional/increased-dimensional projection treatments for MSBA.
- [ ] Run RQ-MSBA-E01 energy-per-useful-information comparisons with matched tasks.
- [ ] Run RQ-MSBA-E02 adaptive-vs-fixed-vs-random resource allocation under equal budgets.
- [ ] Run RQ-MSBA-E03 adaptive ROI/foveation against centre/random/full-image controls.
- [ ] Run RQ-MSBA-E04 digital integrity tests with exact input/output checksums.
- [ ] Run RQ-MSBA-E05 modality-loss compensation with fixed/shuffled/no-compensation controls.
- [ ] Add noisy-area suppression and sensor-lesion compensation studies.
- [ ] Compare signed, absolute, squared and local homeostatic error/reward formulations rather than assuming one default.
- [ ] Require independent seeds and preregistration before enabling gateway plasticity, structural growth or adaptive allocation.
- [ ] Keep production peripheral activation disabled until experiment controls are validated.

## P1 — energy/resource calibration

- [ ] Calibrate normalized MSBA energy units against measured CPU/GPU/system power where reliable telemetry exists.
- [ ] Preserve `measured_joules`, `estimated_joules` and normalized units as separate fields and provenance classes.
- [ ] Measure sensor, encoder, spike, synaptic-event, plasticity, structural, memory, I/O and adapter contributions separately where possible.
- [ ] Verify that hard thermal/fan/persistence protection cannot be overridden by learned allocation.
- [ ] Verify protection ordering: reduce/freeze plasticity before deleting learned structure or disabling safety-critical sensing.

## P1 — runtime/time semantics and performance

- [ ] Benchmark target-Hz pacing from low real-time rates to unlimited mode.
- [ ] Record target Hz, achieved Hz, realtime ratio, `dt` and tick cost in benchmark artifacts.
- [ ] Prove pacing-only changes do not alter deterministic simulation results when simulated inputs/`dt` remain identical.
- [ ] Extend profiling to learning, homeostasis, structural, embodiment, Neural Symbiosis/MSBA, dashboard telemetry and storage as distinct measured phases.
- [ ] Profile increasing neuron/synapse counts before optimizing kernels.

## P1 — 5D causal/ablation program

- [x] Define preregistered topology-matched 5D-vs-control experiments.
- [ ] Implement dimension-shuffled control.
- [x] Implement reduced-dimensional matched embeddings for initial comparisons.
- [ ] Add preregistered increased-dimensional projection controls without conflating them with productive-core N-D support.
- [ ] Measure locality, propagation, learning efficiency, structural motifs, robustness and cost at larger scale.
- [ ] Keep dimensionality claims open until ablation evidence exists.

## P1 — evidence and provenance hardening

- [x] Automated documentation link checking in CI.
- [x] Current-doc consistency checks for fixed version/test claims.
- [x] Evidence-engine negative tests for incomplete/mismatched provenance.
- [x] Compact AI-packet provenance and SHA-verified raw-run indexing.
- [ ] Persist Neural Symbiosis/MSBA adapter, projection, gateway and energy provenance whenever these components become experimental treatments.
- [ ] Persist exact digital checksums for every digital-path experiment.
- [ ] Continue distinguishing UI state, DATA, EVID and interpretation in every workflow.

## P1 — high-risk test coverage

- [ ] Increase dashboard server routing/error-path coverage.
- [ ] Increase evidence-engine rejection/edge-path coverage.
- [ ] Increase operator bridge and control-boundary coverage.
- [ ] Increase real-body platform-specific failure-path coverage.
- [ ] Add integration tests for unknown/stale telemetry propagation across API → store → UI.
- [ ] Add browser-level tests for dynamic sensor/actuator appearance/disappearance.
- [ ] Add negative tests proving peripheral adapters cannot silently mutate canonical core/research state.

## P2 — self-regulation and continuity experiments

- [x] Define non-anthropomorphic resource/continuity pressure states in MSBA.
- [ ] Integrate measured host telemetry into experiment-only resource observations with explicit missing/unknown values.
- [ ] Test missing and uncertain sensor conditions.
- [x] Register deterministic recovery comparison with regulation enabled/disabled.
- [ ] Execute and review the recovery experiment across the required seed set.
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
