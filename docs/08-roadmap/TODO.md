# Brain-5D Current TODO

**Canonical TODO for `main`**  
**Baseline:** `brain5d-core 0.5.0a7`  
**Updated:** 2026-09-05

This file contains active work only. Historical Alpha/Sprint TODO files remain traceability records and are not the current backlog.

## Current engineering baseline

- [x] `main` is the canonical development line.
- [x] 746 tests collected on the current main tree.
- [x] Verified repair-suite result: 733 passed, 2 skipped, 0 failed.
- [x] Latest completed GitHub Continuous Integration run on the repaired main baseline finished successfully.
- [x] Python 3.11, 3.12 and 3.13 CI matrix passes.
- [x] Black, Ruff, Pylint and Pre-Commit pass.
- [x] Mypy and Pyright pass.
- [x] Scientific Integrity Gate remains a required release check and passes on the repaired baseline.
- [x] Security checks remain required and pass on the repaired baseline.
- [x] Fast-suite coverage baseline is 72%.
- [x] Unified responsive dashboard design applied across the system.
- [x] `Network` removed from primary frontend navigation.
- [x] Release/Gate moved to a footer action.
- [x] `Embodiment` simplified to the technical sensor/device/actuator/body-boundary surface.
- [x] Dedicated read-only `Wesen` workspace added.
- [x] `Wesen` morphology derived dynamically from observed embodiment connections.
- [x] Sensor and actuator branches appear from real connection inventory; missing capabilities remain explicit placeholders.
- [x] Icon-first endpoint rendering, semantic device symbols and guaranteed icon-dock access implemented.
- [x] Anatomy v3 adds a body-like machine-native scaffold with sensory head zone, central SNN core, torso interoception, feedback/spine path and actuator limb regions.
- [x] Anatomy v3 is the sole owner of body positions; organism v2 no longer overrides anatomical placement.
- [x] Empirical overlay reads `/api/embodiment/metrics`, `/api/embodiment/history`, `/api/embodiment/pipeline`, `/api/live/io-flow` and `/api/live/population` read-only.
- [x] Empirical display can expose available active fraction, spike count, input/output flow, quality, sensory integrity, resource pressure and continuity risk.
- [x] Missing empirical values remain explicit `—`/unknown; no fabricated constants are introduced.
- [x] External environment satellites represent real reported external sources/services where available.
- [x] Machine-native interoception represented from available CPU/RAM/temperature/fan/storage/runtime telemetry.
- [x] Adaptive visual states cover resource/thermal pressure and reported sensor/actuator/network degradation, recovery and unknown telemetry.
- [x] Node inspection, pointer-centered zoom, pan, reset, focus fading and event filtering implemented.
- [x] Recurrence trend and delayed same-morphology self-model implemented where telemetry exists.
- [x] Delayed self-model uses a bounded frame ring buffer and measured loopback latency when available.
- [x] Browser-local morphology snapshots and timeline scrubber implemented for operator time-travel inspection.
- [x] Causal-path emphasis can surface observed event/decision/action/receipt IDs without inventing missing identifiers.
- [x] Central neutral terminology constants added for SNN core, endpoints, interoception, environment and feedback.
- [x] `Wesen` remains read-only: no learning execution, language output, actuator writes or `/api/control` calls.
- [x] Real-body host telemetry/device discovery integrated without fabricated fallback values.
- [x] Learning Preparation Studio foundation and AI proposal-only boundary implemented.
- [x] Structural proposal → approval → mutation → journal → undo/recovery chain implemented and tested.
- [x] Deterministic persistence/restore infrastructure implemented and tested.
- [x] Research Experiment Runner separates execution protocol from automatic/manual experiment IDs.
- [x] Science-suite impulse responses publish observable propagation and complete DATA/configuration provenance.
- [x] Experiment Runner exposes protocol-specific defaults, seed ranges and effective tick budgets in the persisted workflow.
- [x] Running experiments expose progress state in the Runner and a clearly labelled test-activity state in the footer.
- [x] `science_all_v1` executes all registered Science-Suite runner groups with grouped conditions in one DATA/Manifest run.
- [x] Network impulse DATA persists observed spike sequences and cross-seed reproducibility metrics without changing historical experiments.
- [x] Network impulse observability now includes executed ticks, all published spike IDs, activated neurons, delivered synaptic events, synaptic-activity ticks and total synapses.
- [x] Recurrence impulse topology contains a true return path to the source neuron.
- [x] Direct runtime validation confirmed nonzero neuron and synaptic activity in feed-forward and recurrent conditions.
- [x] Historical `EXP-GEN-0009` to `EXP-GEN-0012` remain unchanged as traceable zero-observation artifacts from the older probe contract.

## P0 — engineering verification after current frontend/runtime integration

- [x] Require the latest `main` CI run to finish green across the complete job matrix.
- [x] Fix only verified current-tree CI failures; no typing/scientific-integrity checks were masked.
- [x] Documentation consistency updated to the 735-test current collection.
- [ ] Verify `/wesen-adaptive.css`, `/wesen-organism.css` and `/wesen-anatomy-v3.css` are served in integrated runtime and dashboard-only modes on a live host.
- [ ] Verify anatomy v3 rendering in at least one live-host session with real connection inventory and populated empirical endpoints.
- [ ] Add a browser/E2E check for pointer-centered camera pan/zoom, icon-dock navigation, anatomy placement and timeline scrubbing.

## P0 — scientific evidence closure

### Productive learning

- [x] Freeze a canonical productive-learning protocol and configuration.
- [x] Bind every run to code/config/prompt/data digests.
- [x] Enforce train/validation/holdout partition separation in the final protocol.
- [x] Add matched learning-off and sham/replay controls.
- [x] Persist pre/post behavioral probes together with weight/reward changes.
- [x] Execute independent multi-seed repeats in clean processes.
- [x] Promote only valid runs from `DATA` to `EVID` through the evidence gate.
- [x] Human-review the resulting claim status: supported, rejected or inconclusive.

### Network impulse observability / recurrence

- [x] Measure complete published spike sequences instead of only output spikes.
- [x] Persist tick, neuron, synapse and recurrence metrics in new DATA.
- [x] Add a direct verification script that fails if ticks, spikes or synaptic delivery are absent.
- [x] Keep historical zero-observation experiments immutable.
- [ ] Run a new registered multi-seed validation experiment on the repaired probe/topology and evaluate it independently rather than retroactively editing `EXP-GEN-0009` to `EXP-GEN-0012`.
- [ ] Promote a recurrence/propagation claim only if the new controlled experiment and review support it.

### Closed-loop embodiment

- [x] Freeze a deterministic embodiment protocol for Sensor → SNN → Actuator → Outcome → Reward.
- [x] Add replay/open-loop control condition.
- [x] Store action acceptance and observed effect as separate receipts.
- [x] Add sensor-loss/degraded-quality condition.
- [x] Add actuator failure/no-effect condition.
- [x] Repeat across seeds and compare adaptation/stability metrics.
- [ ] Promote validated results to evidence only after protocol checks.
- [ ] Expose receipt-linked action/outcome chains to `Wesen` only when a backend endpoint can verify them.

## P1 — runtime/time semantics and performance

- [ ] Benchmark target-Hz pacing from low real-time rates to unlimited mode.
- [ ] Record target Hz, achieved Hz, realtime ratio, `dt` and tick cost in benchmark artifacts.
- [ ] Prove pacing-only changes do not alter deterministic simulation results when simulated inputs/`dt` remain identical.
- [ ] Profile tick cost by subsystem: core, learning, homeostasis, structural, embodiment, dashboard telemetry and storage.
- [ ] Profile increasing neuron/synapse counts before optimizing kernels.
- [x] Run the two opt-in large-storage tests in a scheduled/explicit large-test job and archive the results.

## P1 — 5D causal/ablation program

- [ ] Define a preregistered 5D-vs-control experiment.
- [ ] Implement dimension-shuffled control.
- [ ] Implement reduced-dimensional ablations.
- [ ] Add topology-matched non-spatial control where feasible.
- [ ] Measure locality, propagation, learning efficiency, structural motifs, robustness and cost.
- [ ] Keep dimensionality claims open until the ablation evidence exists.

## P1 — evidence and provenance hardening

- [x] Add automated documentation link checking to CI.
- [x] Add current-doc consistency checks for fixed version/test claims.
- [x] Expand evidence-engine negative tests for incomplete/mismatched provenance.
- [x] Ensure quantitative AI-facing reports reject model-owned statistics unless statistics provenance exists.
- [ ] Add a stable action/outcome provenance view only when backed by a verified endpoint.
- [ ] Persist morphology/body-boundary change records when they are part of a scientific protocol instead of relying on browser-local UI history.
- [ ] Continue distinguishing UI log, DATA artifact, EVID artifact and interpretation in every workflow.

## P1 — test coverage on high-risk surfaces

- [ ] Increase coverage of dashboard server routing/error paths.
- [ ] Increase evidence-engine rejection/edge-path coverage.
- [ ] Increase operator bridge and control boundary coverage.
- [ ] Increase real-body platform-specific failure-path coverage.
- [ ] Add integration tests for unknown/stale telemetry propagation across API → store → UI.
- [ ] Add browser-level tests for dynamic sensor/actuator appearance/disappearance in `Wesen`.

## P2 — self-regulation and continuity experiments

- [ ] Define non-anthropomorphic regulatory metrics for resource/continuity pressure.
- [ ] Test missing sensor and uncertain sensor conditions.
- [ ] Test recovery after resource pressure in deterministic environments.
- [ ] Compare homeostasis/interoception enabled vs disabled under matched conditions.
- [ ] Test whether body-boundary changes predictably alter behavior under matched conditions.
- [ ] Avoid emotion labels as primary measured variables; keep them, if used, as interpretation layers.

## P2 — memory/world model

- [ ] Specify memory state and persistence contracts.
- [ ] Define memory-on / memory-off controls.
- [ ] Add temporal prediction/recall metrics.
- [ ] Separate observation history, learned internal state and external knowledge.
- [ ] Require predictive/behavioral benefit before calling a mechanism a world model.

## P2 — multimodal and knowledge grounding

- [ ] Define typed SignalFrames for camera/audio/document/network inputs.
- [ ] Store source, timestamp, digest and trust/provenance metadata.
- [ ] Provide frozen/replayable snapshots for scientific runs.
- [ ] Compare raw sensory learning against externally structured knowledge conditions.
- [ ] Keep LLM transformation outside the causal SNN state unless explicitly registered as a treatment.

## P2 — AI treatment experiments

- [ ] Standardize identical research packets for multi-model comparisons.
- [ ] Add no-AI, frozen replay, sham/random and model-family conditions.
- [ ] Measure proposal/topology fingerprints without allowing direct hidden writes.
- [ ] Keep AI self-confidence separate from empirical performance metrics.
- [ ] Require treatment identity/provenance in every AI-influenced scientific run.

## Repository/documentation hygiene

- [x] Consolidate canonical README, architecture, dashboard, roadmap and research roadmap.
- [x] Add documentation source-of-truth index.
- [x] Add canonical `WESEN_ADAPTIVE_BODY.md` architecture contract.
- [x] Add dated changelog record for the 2026-09-05 Wesen redesign.
- [x] Remove superseded unreferenced organism prototype from `main` after review.
- [x] Classify versioned Alpha/Sprint/Release documents as historical rather than current state.
- [x] Identify accidental package snapshot and temporary JSON artifacts for removal.
- [x] Confirm there are no open pull requests requiring merge at the current verification point.
- [x] Confirm `tmp-do-not-use` is zero commits ahead and therefore contains nothing to merge.
- [ ] Delete obsolete `tmp-do-not-use` when branch-delete capability/permissions are available.
- [ ] Enable/maintain automatic deletion of merged PR branches when repository settings permit.

## Definition of done for a scientific milestone

A milestone is not complete because a UI card is green. It is complete only when:

- [ ] protocol is frozen/preregistered;
- [ ] implementation and controls are tested;
- [ ] runs are reproducible from manifests;
- [ ] data partitions and AI treatments are explicit;
- [ ] runtime errors/provenance checks pass;
- [ ] evidence artifacts are accepted by the evidence gate;
- [ ] human interpretation distinguishes positive, negative and inconclusive outcomes;
- [ ] documentation records what was actually shown, not what was expected;
- [ ] dashboard visualization is not substituted for experimental evidence.
