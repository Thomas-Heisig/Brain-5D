# Brain-5D Development Roadmap

**Canonical roadmap for current `main`**
**Baseline:** `brain5d-core 0.5.0a7`
**Updated:** 2026-09-05

This roadmap separates **implemented engineering capability** from **scientific evidence still required**. A feature can be technically complete without its scientific hypothesis being confirmed.

## Current baseline — completed engineering foundation

The following capabilities are already part of `main` and are covered by current tests/contracts:

- sparse 5D spiking core with delayed event propagation;
- deterministic RNG/state capture and restore/continue infrastructure;
- STDP, signed eligibility and reward-modulated learning;
- homeostatic regulation;
- structural proposal/approval/mutation/journal/undo/recovery chain;
- `.b5d` storage, delta journaling and checkpoints;
- research registries, manifests, DATA/EVID separation and scientific integrity gates;
- bounded Language Organ / Research Assistant contracts;
- Learning Preparation Studio foundation;
- typed embodiment, actuator authorization, audit chain and deterministic environment loop;
- deterministic embodiment DATA controls with separate action/effect receipts,
    sensor-loss, actuator-failure and pre-registered replay/open-loop conditions;
- independent deterministic seeds with per-condition stability metrics;
- real host interoception and dynamic device discovery without fabricated fallback values;
- responsive seven-workspace operator/research dashboard;
- documentation link/version/test-count consistency checks and scheduled storage validation;
- CI across Python 3.11/3.12/3.13, security, typing, wheel and Docker verification.

## Roadmap principle

Development now moves away from simply adding more modules. The next scientific gain comes from **closing causal and evidential loops on the capabilities already built**.

---

## R1 — Evidence closure for productive learning

**Goal:** Demonstrate, under preregistered conditions, that learning changes later network behavior rather than only internal weights.

Engineering tasks:

- freeze reproducible learning protocol/configuration;
- enforce train/validation/holdout separation and leakage checks;
- capture pre-training and post-training response probes;
- persist reward accounting, weight deltas and behavior deltas in the same manifest-bound run;
- add matched learning-off / sham controls;
- repeat across independent seeds and clean processes.

Scientific deliverable:

- evidence package supporting, rejecting or leaving inconclusive the claim that reward-modulated local learning produces reproducible task-relevant behavioral change.

**Priority:** highest.

---

## R2 — Closed-loop embodiment evidence

**Goal:** Turn the existing Sensor → SNN → Actuator → Outcome → Reward infrastructure into controlled experiments.

Engineering tasks:

- standardize episode manifests and terminal-state verification;
- persist observation/action/outcome/reward receipts;
- compare deterministic simulated environments before relying on real devices;
- add sensor-loss, actuator-loss and degraded-quality conditions;
- distinguish command acceptance from measured physical/logical effect.

Scientific deliverable:

- evidence on whether the network adapts differently when consequences are closed-loop versus replayed/open-loop.

---

## R3 — Time-scale and runtime calibration

**Goal:** Make simulation time, wall-clock pacing and experiment timing explicit and independently controllable.

Engineering tasks:

- benchmark target-Hz controller from slow real-time through unlimited mode;
- profile per-tick cost by network size and enabled subsystem;
- expose achieved Hz, target Hz and realtime ratio consistently;
- verify that pacing changes do not alter deterministic simulation outcomes when `dt` and inputs are unchanged;
- define experiment-specific timing profiles.

Scientific deliverable:

- defensible mapping between configured simulation time and experimental protocol time, without claiming biological equivalence.

---

## R4 — Scientific test of the 5D organization

**Goal:** Determine whether the five-dimensional spatial organization contributes measurable function or is only an indexing/design choice.

Required comparisons:

- full 5D organization;
- dimension-shuffled controls;
- reduced-dimensional ablations;
- topology-matched non-spatial controls where feasible.

Metrics should include propagation, locality, learning efficiency, structural motifs, robustness and storage/runtime cost.

Scientific deliverable:

- evidence for or against a functional contribution of the 5D embedding.

---

## R5 — Self-regulation, continuity and sensor-loss studies

**Goal:** Test homeostasis/interoception as control mechanisms without anthropomorphic interpretation.

Engineering tasks:

- formalize bounded drive/regulatory-state observables;
- preregister thermal/resource/continuity perturbations in deterministic environments;
- measure adaptation under missing or unreliable sensors;
- keep functional-state metrics separate from emotion labels.

Scientific deliverable:

- evidence on whether internal regulatory signals improve stability, recovery or task continuity.

---

## R6 — Memory and world-model layer

**Goal:** Add persistent learned temporal/world state only after R1–R5 provide clear behavioral baselines.

Planned work:

- explicit short/medium/long temporal state contracts;
- causal comparison of memory-on versus memory-off conditions;
- recall/reconstruction metrics;
- separation of stored observation, learned representation and external knowledge;
- deterministic persistence/replay of memory state.

No memory mechanism should be labeled a world model merely because it stores history; predictive utility must be measured.

---

## R7 — Multimodal grounding and knowledge intake

**Goal:** Introduce camera/audio/network/document observations through typed, provenance-rich intake rather than direct LLM-to-SNN writes.

Planned work:

- deterministic SignalFrame/feature contracts for multimodal input;
- source identity, timestamp, digest and trust metadata;
- frozen/replayable knowledge snapshots for scientific runs;
- comparison of raw sensory learning versus externally structured knowledge conditions.

---

## R8 — AI-as-treatment research

**Goal:** Study AI participation itself as an experimental variable.

Conditions may include:

- no AI;
- frozen replay AI;
- sham/random proposer;
- different LLM families under an identical research packet;
- AI proposal accepted versus rejected by the same governance path.

Measurements include topology fingerprints, proposal characteristics, interpretation distance and downstream behavioral effects. AI involvement must remain fully provenance-bound and cannot be silently mixed into control runs.

---

## R9 — Scaling and performance engineering

Scaling should follow evidence needs rather than headline neuron counts.

Work includes:

- storage and journal stress tests beyond current opt-in tests;
- network/tick profiling at increasing neuron/synapse counts;
- async persistence backpressure characterization;
- bounded telemetry sampling;
- memory footprint profiling;
- optional accelerator/native kernels only after semantic equivalence tests exist.

A larger network is not automatically a more valid model.

---

## Release direction

The next release boundary should be earned by evidence and contracts, not only by feature volume. Before a new major research milestone is declared:

1. `main` CI is green;
2. deterministic and recovery contracts remain intact;
3. Scientific Integrity Gate is green;
4. new causal capabilities have matched controls;
5. experiment artifacts are reproducible from recorded manifests;
6. documentation source-of-truth is current;
7. AI involvement is registered as provenance/treatment where applicable.

## Historical roadmaps

Files such as `ROADMAP_ALPHA4.md`, `ROADMAP_ALPHA5*.md`, `ROADMAP_V*.md` and sprint-specific plans are retained as historical records. They describe earlier planning states and do not override this roadmap.
