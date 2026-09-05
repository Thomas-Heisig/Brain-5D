# Brain-5D Development Roadmap

**Canonical roadmap for current `main`**  
**Baseline:** `brain5d-core 0.5.0a7`  
**Updated:** 2026-09-05

This roadmap separates **implemented engineering capability** from **scientific evidence still required**. A feature can be technically complete without its scientific hypothesis being confirmed.

## Current verified baseline

The repaired main baseline has:

- **735 collected tests**;
- **733 passed, 2 skipped, 0 failed** in the verified repair-suite run;
- successful completed GitHub CI across Python 3.11, 3.12 and 3.13;
- green Black, Ruff, Pylint, Pre-Commit, Mypy, Pyright, security and Scientific Integrity checks;
- no open pull requests at the verification point;
- one obsolete `tmp-do-not-use` branch with zero commits ahead of `main`, therefore nothing to merge.

Historical experiment DATA remains historical evidence. Instrumentation repairs create new observations and new experiments rather than rewriting previous DATA.

## Current baseline — completed engineering foundation

The following capabilities are part of `main`:

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
- deterministic embodiment controls with separate action/effect receipts, sensor-loss, actuator-failure and replay/open-loop conditions;
- source-freeze binding across protocol code, configuration, prompt sentinel and DATA digests;
- productive-learning controls with learning-on, learning-off and sham-replay conditions;
- canonical train/validation/holdout partition enforcement;
- clean-process repeats and human-review-gated EVID promotion;
- real host interoception and dynamic device discovery without fabricated fallback values;
- unified responsive dashboard design;
- dedicated adaptive `Wesen` workspace with machine-native dynamic morphology;
- `Network` removed from primary frontend navigation;
- Release/Gate moved to the footer;
- simplified technical `Embodiment` workspace;
- documentation link/version/test-count consistency checks and scheduled storage validation;
- protocol-driven Research Experiment Runner with automatic/manual traceable IDs;
- protocol-specific Runner presets with validated seed lists/ranges, effective tick budgets and documented condition templates;
- visible running-test progress in the Experiment Runner and explicit test activity in the dashboard footer;
- one `science_all_v1` protocol covering all registered Science-Suite runner groups;
- raw impulse spike sequences and deterministic cross-seed response digests persisted in DATA;
- network impulse response signatures that persist executed ticks, all observed spike IDs, activated neurons, delivered synaptic events, synaptic-activity ticks and total synapses;
- true recurrent impulse topology with a return edge to the source neuron;
- direct activity verification that fails if tick execution, neuron spikes or synaptic delivery are absent;
- CI across Python 3.11/3.12/3.13, security, typing, wheel and Docker verification as required release gates.

## Experiment interpretation after the observability repair

`EXP-GEN-0009` through `EXP-GEN-0012` are intentionally retained unchanged. Their zero-spike/zero-activation records describe what the older output-only probe observed, not a rewritten reconstruction of what the runtime may have done internally.

The current network probe observes complete published spike IDs and synaptic delivery. Direct validation on the actual runtime showed:

- ticks execute;
- all three neurons in the impulse chain can become active;
- feed-forward propagation produces observable spikes and synaptic events;
- the recurrent condition produces a return path and additional repeated activity;
- all new metrics are serializable into future experiment `DATA/runs.json` artifacts.

The next scientific step is therefore a **new registered multi-seed validation experiment**, not modification of the historical runs.

## Dashboard/Wesen direction

The frontend architecture is intentionally split:

- `Embodiment` = technical connection/configuration surface;
- `Wesen` = read-only live body projection;
- `Release` = footer access;
- `Network` = no primary workspace.

The `Wesen` body is not a fixed biological analogy. Its visible sensor and actuator branches are derived from observed connection data. Host telemetry is treated as machine-native interoception. The body envelope changes when endpoints appear/disappear.

Current visualization capabilities include:

- dynamic sensor/actuator morphology;
- adaptive membrane/body state;
- data pins;
- node inspection;
- signal animation;
- recurrence trend;
- delayed same-morphology self-model;
- session-local morphology history;
- candidate causal-path emphasis;
- explicit unknown-state rendering.

These remain operator/research visualizations and are not evidence of consciousness or causality by themselves.

## Roadmap principle

Development now moves away from simply adding more modules. The next scientific gain comes from **closing causal and evidential loops on the capabilities already built**.

---

## R0 — Revalidate network propagation on repaired instrumentation

**Goal:** Establish a clean post-repair baseline for propagation and recurrence without changing historical DATA.

Engineering/scientific tasks:

- register a new experiment ID from the current catalog;
- freeze current code/configuration and probe contract;
- run feed-forward and recurrence conditions over multiple independent seeds;
- persist complete spike sequences, latencies, tick counts, synaptic events, synapse counts and before/after digests;
- verify cross-seed determinism where the protocol expects deterministic equality;
- compare recurrence-on against recurrence-off using predefined metrics;
- independently review the run before any EVID promotion.

Scientific deliverable:

- a defensible post-repair baseline showing whether propagation and recurrent return are reproducibly observable under the registered impulse protocol.

**Priority:** immediate.

---

## R1 — Evidence closure for productive learning

**Goal:** Demonstrate, under preregistered conditions, that learning changes later network behavior rather than only internal weights.

Engineering tasks:

- maintain the frozen reproducible learning protocol/configuration;
- enforce train/validation/holdout separation and leakage checks;
- capture pre-training and post-training response probes;
- persist reward accounting, weight deltas and behavior deltas in the same manifest-bound run;
- retain matched learning-off / sham controls;
- repeat across independent seeds and clean processes when replication is required.

Scientific deliverable:

- evidence supporting, rejecting or leaving inconclusive the claim that reward-modulated local learning produces reproducible task-relevant behavioral change.

**Priority:** highest after R0 validation.

---

## R2 — Closed-loop embodiment evidence

**Goal:** Turn the existing Sensor → SNN → Actuator → Outcome → Reward infrastructure into controlled evidence.

Engineering tasks:

- standardize episode manifests and terminal-state verification;
- persist observation/action/outcome/reward receipts;
- compare deterministic simulated environments before relying on real devices;
- retain sensor-loss, actuator-loss and degraded-quality conditions;
- distinguish command acceptance from measured physical/logical effect;
- expose receipt-linked causal paths to `Wesen` only when the backend can verify the chain.

Scientific deliverable:

- evidence on whether the network adapts differently when consequences are closed-loop versus replayed/open-loop.

---

## R3 — Time-scale and runtime calibration

**Goal:** Make simulation time, wall-clock pacing and experiment timing explicit and independently controllable.

Engineering tasks:

- benchmark target-Hz controller from slow real-time through unlimited mode;
- profile per-tick cost by network size and enabled subsystem;
- expose achieved Hz, target Hz and realtime ratio consistently;
- verify pacing changes do not alter deterministic simulation outcomes when `dt` and inputs are unchanged;
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

---

## R5 — Self-regulation, continuity and sensor-loss studies

**Goal:** Test homeostasis/interoception as control mechanisms without anthropomorphic interpretation.

Engineering tasks:

- formalize bounded drive/regulatory-state observables;
- preregister thermal/resource/continuity perturbations in deterministic environments;
- measure adaptation under missing/unreliable sensors;
- persist body-boundary/sensor availability changes when they are part of an experiment;
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

No memory mechanism should be labelled a world model merely because it stores history; predictive utility must be measured.

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

Conditions may include no AI, frozen replay AI, sham/random proposer, different LLM families under an identical research packet, and proposal accepted versus rejected by the same governance path.

AI involvement must remain provenance-bound and cannot be silently mixed into control runs.

---

## R9 — Scaling and performance engineering

Scaling should follow evidence needs rather than headline neuron counts.

Work includes:

- storage/journal stress tests;
- network/tick profiling at increasing neuron/synapse counts;
- async persistence backpressure characterization;
- bounded telemetry sampling;
- memory footprint profiling;
- optional accelerator/native kernels only after semantic equivalence tests exist.

A larger network is not automatically a more valid model.

---

## Release direction

Before a new major research milestone is declared:

1. `main` CI is green;
2. deterministic/recovery contracts remain intact;
3. Scientific Integrity Gate is green;
4. new causal capabilities have matched controls;
5. experiment artifacts are reproducible from recorded manifests;
6. documentation source-of-truth is current;
7. AI involvement is registered as provenance/treatment where applicable;
8. dashboard visualizations remain clearly separated from scientific evidence;
9. historical DATA has not been rewritten to fit newer instrumentation.

## Historical roadmaps

Files such as `ROADMAP_ALPHA4.md`, `ROADMAP_ALPHA5*.md`, `ROADMAP_V*.md` and sprint-specific plans are historical records and do not override this roadmap.
