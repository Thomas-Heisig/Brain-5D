# Brain-5D Development Roadmap

**Canonical roadmap for current `main`**  
**Baseline:** `brain5d-core 0.5.0a7`  
**Updated:** 2026-09-06

This roadmap separates **implemented engineering capability** from **scientific evidence still required**. A feature can be technically complete without its scientific hypothesis being confirmed.

## Current verified baseline

At the 2026-09-06 verification point:

- **773 tests** are collected;
- the full GitHub CI matrix on the Neural Symbiosis merge commit completed successfully;
- Python 3.11, 3.12 and 3.13 full/slow suites passed;
- Black, Ruff, Pylint, Pre-Commit, Mypy, Pyright, security and Scientific Integrity passed;
- wheel build/install and Docker build/runtime verification passed;
- no open pull requests remained;
- all development work found outside `main` was already merged; no unmerged branch content remained.

Historical experiment DATA remains historical evidence. Instrumentation repairs and new architecture produce new observations/experiments rather than rewriting prior DATA.

## Completed engineering foundation

Current `main` contains:

- sparse 5D spiking core with delayed event propagation and deterministic RNG/state;
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
- **Neural Symbiosis** open-set peripheral network/virtual-area contracts at the embodiment boundary;
- read-only Neural Symbiosis panel in `Wesen`;
- inert candidate gateway math for STDP, homeostatic scaling, structural formation/pruning and efferent reward-modulated gating.

## Roadmap principle

Development now prioritizes **evidence closure** and controlled experiments over feature accumulation.

---

## R0 — Post-repair propagation and recurrence validation

**Goal:** establish a clean multi-seed baseline for propagation and recurrent return using the repaired instrumentation.

Tasks:

- execute the registered recurrence/propagation protocol over independent seeds;
- persist complete spike, synapse, latency and digest metrics;
- compare recurrence-on/off using preregistered metrics;
- review before any EVID promotion;
- never rewrite `EXP-GEN-0009` to `EXP-GEN-0012`.

**Priority:** immediate.

---

## R1 — Productive-learning evidence closure

**Goal:** demonstrate whether learning changes later behavior rather than merely internal weights.

Maintain:

- frozen protocol/configuration;
- train/validation/holdout separation;
- pre/post behavior probes;
- learning-off and sham/replay controls;
- independent seeds and clean-process repeats;
- human-review-gated EVID promotion.

---

## R2 — Closed-loop embodiment evidence

**Goal:** test Sensor → SNN → Actuator → Outcome → Reward as a controlled causal loop.

Required comparisons include replay/open-loop, sensor-loss, degraded-quality and actuator-no-effect conditions. Action acceptance and measured effect must remain separate receipts.

---

## R3 — Neural Symbiosis experimental gateway program

**Goal:** test whether the SNN can learn to select, weight or compensate across peripheral neural/virtual areas without compromising the canonical core.

The first implementation stage is **experiment-only**. Production peripheral activation remains out of scope until controls are validated.

Required work:

1. add an experiment-runner adapter that constructs explicitly declared peripheral areas;
2. persist exact adapter/model/version/artifact hashes;
3. persist gateway state independently from core synapse state;
4. keep gateway plasticity disabled outside registered experiments;
5. support matched frozen-gateway, random-gateway, timing-shuffle and information/activity controls;
6. evaluate noisy-area suppression and sensor-lesion compensation;
7. compare alternative homeostatic reward/error formulations rather than assuming a signed population mean is valid;
8. require independent seeds and evidence review before claims of learned tool/area use.

Candidate research hypotheses are documented in [`../02-architecture/NEURAL_SYMBIOSIS.md`](../02-architecture/NEURAL_SYMBIOSIS.md).

---

## R4 — Time-scale and runtime calibration

Benchmark target Hz, achieved Hz, realtime ratio, `dt` and per-subsystem tick cost. Prove pacing-only changes do not alter deterministic simulated outcomes when `dt` and inputs remain unchanged.

---

## R5 — Scientific test of the 5D organization

Compare full 5D organization against dimension-shuffled, reduced-dimensional and topology-matched non-spatial controls. Measure propagation, locality, learning efficiency, structural motifs, robustness and computational cost.

---

## R6 — Self-regulation, continuity and sensor-loss studies

Test homeostasis/interoception as functional control mechanisms without anthropomorphic interpretation. Persist body-boundary/sensor availability changes when they are experimental variables.

---

## R7 — Memory and world-model layer

Only after stable behavioral baselines exist:

- define explicit memory-state contracts;
- compare memory-on/off;
- add prediction/recall metrics;
- distinguish observation history, learned internal state and external knowledge;
- require predictive/behavioral utility before using the term world model.

---

## R8 — Multimodal grounding and knowledge intake

Introduce camera/audio/document/network/knowledge observations through typed provenance-rich SignalFrames and Neural Symbiosis adapters. Scientific runs require frozen/replayable source snapshots and explicit treatment identity.

---

## R9 — AI-as-treatment research

Compare no-AI, frozen replay, sham/random proposer and model-family conditions under identical research packets. AI involvement remains provenance-bound and cannot be silently mixed into controls.

---

## R10 — Scaling and performance engineering

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
8. dashboard visualizations remain separated from scientific evidence;
9. historical DATA has not been rewritten to fit newer instrumentation.

## Historical roadmaps

Files such as `ROADMAP_ALPHA4.md`, `ROADMAP_ALPHA5*.md`, `ROADMAP_V*.md` and sprint-specific plans are historical records and do not override this roadmap.
