# Brain-5D Roadmap – From Persistent SNN to Usable AI

## Definition of usable AI

Brain-5D v1.0 is an engineering milestone, not a claim of AGI, consciousness,
or biological equivalence.  A usable system must demonstrate persistent
learning, stable self-regulation, measurable task improvement, multimodal
inputs, retained context, bounded actions, observability, deterministic
recovery, and documented limits.

The roadmap is informed by `Analyse_Deepseek.md`, `Der_weg_zur_KI.md`, and
`Research.md`.  Ideas from those documents become roadmap items only when they
have an implementation boundary, experiment, and exit criterion.

## v0.4 – Persistence Contract

### alpha.1

Frozen `.b5d` Snapshot V1, mmap access, format invariants and 50k smoke test.

### alpha.2

Append-only journal, CRC, commit markers, crash-tail handling and replay.

### alpha.3

Runtime capture and lazy snapshot views.

### alpha.4

Bounded asynchronous I/O, storage telemetry, generation compaction and runtime
checkpoint foundation.

### alpha.5-alpha.6

Read-only operator dashboard, research alignment and deterministic checkpoint
work.

### alpha.7

- runtime checkpoint V3 overlays exact neuron model parameters and synapse
  floating-point state;
- deterministic restore is required to match a continuous reference exactly;
- dashboard adds safe documentation browsing, snapshot selection and embodiment
  status;
- typed embodiment interfaces are introduced without enabling autonomous
  external actions.

### v0.4.0 final exit

- full quality gate in `docs/QUALITY_GATE_V040.md` passes;
- persistent state survives restart exactly at the defined tick boundary;
- dashboard and recovery runbooks are documented;
- binary `.b5d` V1 remains frozen.

## v0.5 – Self-Regulation

- target firing-rate bands;
- adaptive threshold/excitability control;
- energy homeostasis;
- bounded neurogenesis and pruning;
- dirty tracking for changed neurons/synapses;
- dashboard homeostasis metrics become live.

**Exit:** reference workloads remain active without runaway excitation or
permanent silence over long deterministic runs.

## v0.6 – Scaling

- dirty regions/chunks;
- chunked persistence and indexing;
- deterministic domain decomposition fallback;
- subsystem profiling;
- staged 50k -> 500k -> 1M benchmarks before larger claims.

**Exit:** measured scaling curves for RAM, ticks/s, queue pressure and storage.

## v0.7 – Learning Environments

- deterministic episodes and seeds;
- train/evaluation split;
- delayed reward tasks;
- baseline agents;
- continual-learning retention and forgetting measurements;
- embodiment environment contract used by simulated reference tasks.

**Exit:** repeatable held-out improvement over untrained/random baselines.

## v0.8 – Embodiment and Sensory Representation

- text/scalar/image/audio feature adapters;
- sensor adapters and actuator adapters;
- simulated, physical, digital and hybrid environment implementations;
- explicit encoding/decoding contracts;
- permissioned action boundary;
- dashboard sensor/action observability.

**Exit:** at least two modalities drive trained tasks through the same learning
API, and actions remain bounded and auditable.

## v0.9 – Memory, Context and World Model

- working context;
- long-term memory retrieval;
- goal/task state;
- novelty and prediction-error signals;
- explicit observed/learned/hypothesized knowledge separation.

**Exit:** retained context measurably improves multi-step tasks.

## v0.10 – Cognitive Evaluation

- causal intervention tasks;
- compositional generalization;
- neuro-symbolic bridge experiments;
- confidence/provenance metrics;
- language/HMI experiments as an observable bridge rather than hidden core.

**Exit:** fixed causal/compositional suites show repeatable gains over baselines.

## v0.11 – HMI, Permissions and Bounded Autonomy

- stable API/chat interface;
- capability permissions;
- resource/time/action budgets;
- audit log;
- sandboxed tools;
- reversible external actions where practical;
- safe stop and recovery.

**Exit:** autonomous experiment loops remain inside configured permissions.

## v0.12 – Release Candidate

- benchmark freeze;
- restore-and-continue regression;
- long soak tests;
- clean install/reproduction tests;
- operator runbook and API stability review.

## v1.0 – Usable Brain-5D AI

Release only after demonstrated persistent learning, stable self-regulation,
held-out task improvement, multimodal perception, retained context, bounded
and auditable actions, deterministic recovery, and reproducible installation.
