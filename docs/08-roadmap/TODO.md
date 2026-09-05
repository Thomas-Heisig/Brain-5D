# Brain-5D Current TODO

**Canonical TODO for `main`**  
**Baseline:** `brain5d-core 0.5.0a7`  
**Updated:** 2026-09-05

This file contains active work only. Historical Alpha/Sprint TODO files remain traceability records and are not the current backlog.

## Current engineering baseline

- [x] `main` is the canonical development line.
- [x] Current test collection is 725 tests after the icon-first Wesen accessibility regression addition.
- [x] Fast-suite coverage baseline is 72%.
- [x] Scientific Integrity Gate remains a required release check.
- [x] Security, lint/pre-commit, Mypy/Pyright, wheel build/install and Docker verification remain required CI/release gates.
- [x] Unified responsive dashboard design applied across the system.
- [x] `Network` removed from primary frontend navigation.
- [x] Release/Gate moved to a footer action.
- [x] `Embodiment` simplified to the technical sensor/device/actuator/body-boundary surface.
- [x] Dedicated read-only `Wesen` workspace added.
- [x] `Wesen` morphology derived dynamically from observed embodiment connections.
- [x] Sensor and actuator branches appear from real connection inventory; missing capabilities remain explicit placeholders.
- [x] Force-directed presentation layout removes the rigid fixed-coordinate body arrangement.
- [x] Dense sensor/actuator populations are distributed over multiple radii with stronger same-class repulsion.
- [x] Convex-hull membrane follows the currently observed body nodes.
- [x] External environment satellites represent real reported external sources/services where available.
- [x] Machine-native interoception represented from available CPU/RAM/temperature/fan/storage/runtime telemetry.
- [x] Adaptive visual states cover resource/thermal pressure and reported sensor/actuator/network degradation, recovery and unknown telemetry.
- [x] Body view is icon-first: labels/metric strings are removed from crowded SVG nodes and exposed through tooltips/inspector instead.
- [x] Device-type symbols distinguish camera, microphone, speaker, display, GPU, network, USB, storage, printer, robotics and generic endpoints.
- [x] Scrollable icon dock provides guaranteed mouse/keyboard access to every discovered body node.
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

## P0 — engineering verification after current frontend integration

- [ ] Require the latest `main` CI run to finish green across the complete job matrix.
- [ ] Fix only verified current-tree CI failures; do not mask typing/scientific-integrity failures.
- [ ] Confirm documentation consistency checker accepts the 725-test baseline.
- [ ] Verify `/wesen-adaptive.css` and `/wesen-organism.css` are served in integrated runtime and dashboard-only modes.
- [ ] Verify adaptive body rendering in at least one live-host session with real connection inventory.
- [ ] Add a browser/E2E check for pointer-centered camera pan/zoom, icon-dock navigation and timeline scrubbing.

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
- [ ] Keep remote branch list to `main` plus active short-lived work only; delete obsolete `tmp-do-not-use` when branch-delete access is available.
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
