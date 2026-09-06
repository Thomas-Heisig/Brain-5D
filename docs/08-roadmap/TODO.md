# Brain-5D Current TODO

**Canonical TODO for `main`**  
**Baseline:** `brain5d-core 0.5.0a7`  
**Updated:** 2026-09-06

This file contains active work only. Historical Alpha/Sprint TODO files remain traceability records and are not the current backlog.

## Current engineering baseline

- [x] `main` is the canonical development line.
- [x] 773 tests collected on the verified 2026-09-06 baseline.
- [x] Python 3.11, 3.12 and 3.13 full and slow suites pass.
- [x] Black, Ruff, Pylint and Pre-Commit pass.
- [x] Mypy and Pyright pass.
- [x] Scientific Integrity Gate passes.
- [x] Security checks pass.
- [x] Wheel build/install and Docker build/runtime verification pass.
- [x] No open pull requests remained at the verification point.
- [x] All non-main work found at the verification point was already merged into `main`.
- [x] Unified responsive dashboard design applied across the system.
- [x] `Network` removed from primary frontend navigation.
- [x] Release/Gate moved to a footer action.
- [x] `Embodiment` remains the technical sensor/device/actuator/body-boundary surface.
- [x] Dedicated read-only `Wesen` workspace added.
- [x] `Wesen` morphology derives dynamically from observed embodiment connections.
- [x] Empirical overlays use backend observations and preserve unknown values.
- [x] Neural Symbiosis added as an embodiment-only, read-only multi-network interface.
- [x] Open-set `NetworkAreaAdapter` contract added for arbitrary peripheral network implementations.
- [x] Built-in descriptors cover CNN, Transformer, LSTM/GRU/RNN, GNN, Modern Hopfield, reservoir/ESN, MLP, VAE/GAN/diffusion, autoencoder, peripheral SNN, multimodal, neuro-symbolic and custom areas.
- [x] Virtual logic/knowledge/database/memory areas are representable without being folded into canonical SNN state.
- [x] Camera, microphone, web/API, database, logic, memory, audio, display, printer and robotics pipeline templates are represented.
- [x] Gateway plasticity remains disabled by default.
- [x] Candidate pair-STDP, homeostatic scaling, structural formation/pruning and reward-modulated gate math is implemented without hidden core mutation.
- [x] Gateway RNG sampling is intentionally left to an explicit experiment runner.
- [x] Pipeline reachability is explicitly not treated as evidence of learned use.
- [x] Research DATA v2 preserves raw runs while exposing bounded `runs.json` and `analysis/ai_packet.json` projections.

## P0 — repository and frontend verification

- [ ] Verify Neural Symbiosis CSS/JS is served in integrated runtime and dashboard-only modes on a live host.
- [ ] Verify `Wesen` anatomy + Neural Symbiosis rendering with a real connection inventory.
- [ ] Add browser/E2E checks for pan/zoom, icon-dock navigation, anatomy placement, timeline scrubbing and Neural Symbiosis pipeline reachability.
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

## P1 — Neural Symbiosis experiment runner

- [ ] Add an experiment-only adapter that instantiates one declared peripheral network/virtual area.
- [ ] Record adapter class, framework, model/version, artifact hash and endpoint identity.
- [ ] Persist gateway state separately from canonical SNN synapse state.
- [ ] Add frozen-gateway control.
- [ ] Add random-gateway control.
- [ ] Add timing-shuffle control.
- [ ] Add activity-matched but information-destroyed control.
- [ ] Add noisy-area suppression study.
- [ ] Add sensor-lesion compensation study.
- [ ] Compare signed, absolute, squared and local homeostatic error/reward formulations.
- [ ] Require independent seeds and preregistration before enabling gateway plasticity.
- [ ] Keep production peripheral activation disabled until experiment controls are validated.

## P1 — runtime/time semantics and performance

- [ ] Benchmark target-Hz pacing from low real-time rates to unlimited mode.
- [ ] Record target Hz, achieved Hz, realtime ratio, `dt` and tick cost in benchmark artifacts.
- [ ] Prove pacing-only changes do not alter deterministic simulation results when simulated inputs/`dt` remain identical.
- [ ] Extend profiling to learning, homeostasis, structural, embodiment, Neural Symbiosis, dashboard telemetry and storage as distinct measured phases.
- [ ] Profile increasing neuron/synapse counts before optimizing kernels.

## P1 — 5D causal/ablation program

- [x] Define preregistered topology-matched 5D-vs-control experiments.
- [ ] Implement dimension-shuffled control.
- [x] Implement reduced-dimensional matched embeddings for initial comparisons.
- [ ] Measure locality, propagation, learning efficiency, structural motifs, robustness and cost at larger scale.
- [ ] Keep dimensionality claims open until ablation evidence exists.

## P1 — evidence and provenance hardening

- [x] Automated documentation link checking in CI.
- [x] Current-doc consistency checks for fixed version/test claims.
- [x] Evidence-engine negative tests for incomplete/mismatched provenance.
- [x] Compact AI-packet provenance and SHA-verified raw-run indexing.
- [ ] Add stable action/outcome provenance views only when backed by verified endpoints.
- [ ] Persist morphology/body-boundary change records when part of a scientific protocol.
- [ ] Persist Neural Symbiosis adapter/gateway provenance whenever those components become experimental treatments.
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

- [ ] Define non-anthropomorphic regulatory metrics for resource/continuity pressure.
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

- [ ] Define typed SignalFrames for camera/audio/document/network/knowledge inputs.
- [ ] Store source, timestamp, digest and trust/provenance metadata.
- [ ] Provide frozen/replayable snapshots for scientific runs.
- [ ] Route peripheral models through Neural Symbiosis adapters rather than hidden direct core writes.
- [ ] Compare raw sensory learning against externally structured knowledge conditions.
- [ ] Keep LLM transformation outside causal SNN state unless explicitly registered as a treatment.

## P2 — AI treatment experiments

- [ ] Standardize identical research packets for multi-model comparisons.
- [ ] Add no-AI, frozen replay, sham/random and model-family conditions.
- [ ] Measure proposal/topology fingerprints without allowing hidden writes.
- [ ] Keep AI self-confidence separate from empirical performance metrics.
- [ ] Require treatment identity/provenance in every AI-influenced scientific run.

## Repository/documentation hygiene

- [x] Canonical README, architecture, documentation index and roadmap updated after Neural Symbiosis merge.
- [x] Historical dated experiment/changelog artifacts left unchanged.
- [x] No open PRs remained at repository-cleanup verification point.
- [x] No unmerged feature content remained outside `main`.
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
- [ ] dashboard visualization or pipeline reachability is not substituted for experimental evidence.
