# Brain-5D Roadmap – From Storage Foundation to a Usable AI

## Definition of “usable AI” for this project

Brain-5D reaches a **usable AI** milestone when it can reproducibly:

1. persist and restore its learned state;
2. receive structured sensory/input signals;
3. learn measurable tasks from feedback without manual weight editing;
4. retain useful learning across restarts;
5. regulate unstable activity instead of diverging or becoming silent;
6. expose an observable decision/output path;
7. communicate through a stable application/API interface;
8. run bounded autonomous experiments with safety/resource limits;
9. report confidence, provenance and internal telemetry for debugging;
10. pass a fixed evaluation suite on unseen task episodes.

This definition does **not** assume AGI, consciousness or human-equivalent
intelligence. Each milestone must be demonstrated by tests and repeatable
experiments.

---

## v0.4 – Persistent Brain-5D State

### v0.4.0-alpha.1 – `.b5d` Snapshot V1

**Status:** DONE – frozen snapshot foundation.

- fixed snapshot header and records;
- mmap/random access;
- strict structural validation;
- optical/restart modes;
- 50k scalability smoke test.

**Exit:** full regression + Clean Code + format invariants green.

### v0.4.0-alpha.2 – Delta Journal & Crash Safety

**Status:** DONE in the cumulative alpha.3 update.

- append-only tick journal;
- changed-neuron deltas;
- synapse weight deltas;
- topology add/remove deltas;
- commit markers;
- per-frame checksum/CRC;
- recovery that ignores incomplete tail records;
- snapshot + journal replay to an arbitrary committed tick.

**Exit:** forced-crash tests reconstruct exactly the last committed state.

### v0.4.0-alpha.3 – Storage Integration & Lazy Observatory

**Status:** CURRENT – runtime capture and lazy snapshot projections implemented.

Implemented:

- optional `StorageSession` post-step integration;
- changed-neuron/synapse/topology journal capture;
- configurable commit cadence;
- lazy mmap-backed activity/weight/energy projections;
- storage remains disabled by default.

Still required before alpha.3 exit:

- bounded asynchronous write queue/back-pressure;
- storage latency telemetry and benchmark budget;
- crash-safe compaction/rotation policy;
- CLI/main integration after measured overhead;
- restore-and-continue against the real `NeuralNetwork`.

**Exit:** storage enabled without violating the agreed simulation latency
budget and without loading full large snapshots into RAM.

### v0.4.0 final – Persistence Contract

- migration/compatibility tests;
- documented recovery procedure;
- deterministic experiment IDs and metadata;
- stable public `StorageBackend` interface.

**Exit:** multi-run training state survives restart and produces the same
post-restore behavior within defined numeric tolerances.

---

## v0.5 – Stable Self-Organization

### v0.5.0-alpha – Homeostatic Regulation

- target firing-rate bands;
- slow threshold/excitability adaptation;
- energy-aware regulation;
- configurable time constants;
- heatmaps for firing-rate error and homeostatic state.

### v0.5.0-beta – Structural Plasticity Safety

- bounded sprouting/pruning budgets;
- minimum/maximum degree constraints;
- transaction rollback for topology mutations;
- interaction tests with STDP and reward learning;
- persistent topology deltas.

### v0.5.0 final

**Exit:** long-running networks neither explode nor collapse into permanent
silence under the reference workloads, and topology mutations remain valid.

---

## v0.6 – Scalable Simulation Engine

- chunk-aware neuron iteration;
- sparse event scheduling improvements;
- profiling by subsystem;
- parallel execution experiments with deterministic fallback;
- memory budgets and back-pressure;
- 50k -> 500k -> multi-million-neuron staged benchmarks.

**Exit:** documented scaling curves for RAM, ticks/s and storage throughput;
no claim of 312.5M real-time operation until measured.

---

## v0.7 – Learning Environment & Curriculum

- stable Environment/Input/Action interfaces;
- deterministic episodes and seeds;
- positive/negative/delayed reward tasks;
- train/evaluate split;
- checkpointed learning curves;
- baseline agents for comparison;
- catastrophic-forgetting tests.

Reference tasks progress from simple to harder:

1. conditioned response;
2. temporal association;
3. delayed reward choice;
4. multi-step navigation/state task;
5. transfer to unseen episode variants.

**Exit:** statistically repeatable improvement over untrained and random
baselines on held-out episodes.

---

## v0.8 – Sensory Representation Layer

- typed adapters for text tokens, scalar sensors, image features and audio
  features;
- explicit encoding/decoding contracts;
- no direct dependency of the core on a particular sensor;
- representation quality diagnostics;
- persistent learned associations.

The first production path should use **feature adapters**, not raw megapixel or
raw-waveform fan-out, until scaling evidence supports more direct encoding.

**Exit:** at least two input modalities can drive trained tasks through the
same network/learning API.

---

## v0.9 – Memory, Context and Goal Loop

- short-term working context;
- long-term `.b5d`-backed memory retrieval/index;
- goal state and task context;
- bounded action selection;
- novelty/error signals as optional intrinsic reward inputs;
- explicit separation of observed facts, learned associations and generated
  hypotheses.

**Exit:** multi-step tasks require and measurably benefit from retained context
and persistent memory.

---

## v0.10 – Language / HMI Bridge

- stable chat/API interface;
- token/text encoder and decoder experiments;
- optional external language-model bridge as a **tool/teacher**, not hidden
  inside the neural core;
- provenance showing whether an answer came from Brain-5D memory, an external
  model, or a deterministic tool;
- file/input adapters and observable output traces.

**Exit:** Brain-5D can accept a user request, select a bounded learned/tool
behavior, and return a traceable result through one HMI/API.

---

## v0.11 – Bounded Autonomy & Safety

- capability permissions;
- resource/time/action budgets;
- sandboxed tool execution;
- audit log;
- reversible/transactional external actions where possible;
- safe-stop and recovery;
- adversarial and malformed-input tests;
- no self-modifying executable code without a separate sandbox and explicit
  policy gate.

**Exit:** autonomous experiment loops remain inside configured permissions and
recover cleanly from failures.

---

## v0.12 – Evaluation & Release Candidate

- fixed benchmark suite;
- regression baselines for learning, memory and latency;
- reproducibility across fresh installations;
- restore-and-continue tests;
- long-duration soak tests;
- documentation and operator runbook;
- API stability review.

**Exit:** release candidate satisfies all “usable AI” criteria at the top of
this document on the defined reference hardware/workloads.

---

## v1.0 – Usable Brain-5D AI

A v1.0 release is earned only when the system demonstrates, rather than merely
contains code for:

- persistent learning;
- stable self-regulation;
- reproducible task improvement;
- multimodal input through typed adapters;
- retained context/memory;
- an observable HMI/API output path;
- bounded autonomous operation;
- deterministic recovery and auditability;
- documented performance limits.

### v1.0 non-goals

The release must not be described as conscious, sentient, generally
intelligent or biologically equivalent unless separate empirical evidence
supports such claims. Brain-5D v1.0 is defined by useful, measurable behavior
and engineering reliability.

---

## Post-v1.0 directions

Only after v1.0 evidence should the project evaluate:

- distributed multi-node simulation;
- larger 5D spaces and adaptive chunk placement;
- learned compression of inactive regions;
- richer neuromodulators and cell types;
- hardware accelerators;
- physical/neuromorphic sensor bridges;
- continual-learning research beyond the fixed curriculum.
