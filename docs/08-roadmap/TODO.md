# Brain-5D Current TODO

**Canonical TODO for `main`**
**Baseline:** `brain5d-core 0.5.0a7`
**Updated:** 2026-09-05

This file contains active work only. Historical Alpha/Sprint TODO files remain traceability records and are not the current backlog.

## Verified baseline

- [x] `main` is the canonical development line.
- [x] CI green across Python 3.11, 3.12 and 3.13.
- [x] 713 tests collected; 708 tests pass and 5 are skipped in the full current suite; the 2 large-storage tests are intentionally opt-in/skipped by default.
- [x] Fast-suite coverage currently 72%.
- [x] Scientific Integrity Gate green.
- [x] Security, lint/pre-commit, Mypy/Pyright, wheel build/install and Docker verification green.
- [x] Responsive dashboard experience merged for all seven workspaces.
- [x] Real-body host telemetry/device discovery integrated without fabricated fallback values.
- [x] Learning Preparation Studio foundation and AI proposal-only boundary implemented.
- [x] Structural proposal → approval → mutation → journal → undo/recovery chain implemented and tested.
- [x] Deterministic persistence/restore infrastructure implemented and tested.

## P0 — scientific evidence closure

These tasks should produce the next scientific gain before broad feature expansion.

### Productive learning

- [ ] Freeze a canonical productive-learning protocol and configuration.
- [ ] Bind every run to code/config/prompt/data digests.
- [ ] Enforce train/validation/holdout partition separation in the final protocol.
- [ ] Add matched learning-off and sham/replay controls.
- [ ] Persist pre/post behavioral probes together with weight/reward changes.
- [ ] Execute independent multi-seed repeats in clean processes.
- [ ] Promote only valid runs from `DATA` to `EVID` through the evidence gate.
- [ ] Human-review the resulting claim status: supported, rejected or inconclusive.

### Closed-loop embodiment

- [x] Freeze a deterministic embodiment protocol for Sensor → SNN → Actuator → Outcome → Reward.
- [x] Add replay/open-loop control condition.
- [x] Store action acceptance and observed effect as separate receipts.
- [x] Add sensor-loss/degraded-quality condition.
- [x] Add actuator failure/no-effect condition.
- [x] Repeat across seeds and compare adaptation/stability metrics.
- [ ] Promote validated results to evidence only after protocol checks.

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
- [x] Add a current-doc consistency check so fixed version/test claims cannot drift silently.
- [x] Expand evidence-engine negative tests for incomplete/mismatched provenance.
- [x] Ensure all quantitative AI-facing reports reject model-owned statistics unless statistics provenance exists.
- [ ] Add a stable action/outcome provenance view to the dashboard only when backed by a verified endpoint.
- [ ] Continue distinguishing UI log, DATA artifact, EVID artifact and interpretation in every workflow.

## P1 — test coverage on high-risk surfaces

Current global fast-suite coverage is useful but uneven. Prioritize behaviorally important low-coverage modules rather than chasing a vanity percentage.

- [ ] Increase coverage of dashboard server routing/error paths.
- [ ] Increase evidence-engine rejection/edge-path coverage.
- [ ] Increase operator bridge and control boundary coverage.
- [ ] Increase real-body platform-specific failure-path coverage.
- [ ] Add integration tests for unknown/stale telemetry propagation across API → store → UI.

## P2 — self-regulation and continuity experiments

- [ ] Define non-anthropomorphic regulatory metrics for resource/continuity pressure.
- [ ] Test missing sensor and uncertain sensor conditions.
- [ ] Test recovery after resource pressure in deterministic environments.
- [ ] Compare homeostasis/interoception enabled vs disabled under matched conditions.
- [ ] Avoid emotion labels as primary measured variables; keep them, if used, as interpretation layers.

## P2 — memory/world model

Start only after productive-learning and closed-loop baselines are reproducible.

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
- [ ] Require treatment identity and provenance in every AI-influenced scientific run.

## Repository/documentation hygiene

- [x] Consolidate canonical README, architecture, dashboard, roadmap and research roadmap.
- [x] Add a documentation source-of-truth index.
- [x] Classify versioned Alpha/Sprint/Release documents as historical rather than current state.
- [x] Identify accidental package snapshot and temporary JSON artifacts for removal.
- [ ] Keep remote branch list to `main` plus active short-lived work only; delete merged branches after merge.
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
- [ ] documentation records what was actually shown, not what was expected.
