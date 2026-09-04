# Brain-5D Research Roadmap

**Canonical research roadmap**  
**Updated:** 2026-09-04  
**Engineering baseline:** `brain5d-core 0.5.0a7`

## Research objective

Brain-5D investigates whether a sparse, locally learning, structurally adaptive and embodied spiking system can develop reproducible functional organization under controlled causal conditions. The project also studies what changes when language models participate as bounded interpreters/proposers rather than hidden controllers.

The research program deliberately separates four levels:

1. **implemented mechanism** — code exists and its contract is tested;
2. **executed experiment** — a protocol produced valid run data;
3. **accepted evidence** — run data passed validity/provenance/evidence gates;
4. **scientific interpretation** — a human/registered analysis explains what the evidence supports, rejects or leaves unresolved.

No level may be silently substituted for another.

## Current research readiness

Engineering now supports:

- deterministic SNN execution and restore;
- local STDP/eligibility/reward learning;
- productive learning experiments;
- homeostasis and bounded interoception;
- structural self-organization with explicit approval and persistence;
- deterministic embodiment environments and authorized actuator paths;
- real host/device observations;
- experiment registries, manifests, DATA/EVID separation and evidence gates;
- AI governance, frozen replay/sham backends and provenance-bound analysis;
- a dashboard that exposes research state without treating presentation as evidence.

This readiness makes the next phase an **evidence program**, not primarily another architecture expansion.

## Research questions

### RQ1 — Productive local learning

Does reward-modulated local plasticity produce reproducible changes in subsequent network behavior beyond weight change alone?

Required evidence:

- pre/post behavioral probe;
- learning-on vs learning-off control;
- reward and eligibility provenance;
- holdout evaluation;
- independent seeds/repeats.

### RQ2 — Temporal dependence

Can the system exploit temporal order/history rather than only instantaneous input statistics?

Required evidence:

- order-sensitive tasks;
- shuffled/reversed temporal controls;
- state-history or temporal-memory ablations;
- reproducible response difference.

### RQ3 — Structural self-organization

Does structural plasticity improve measurable function, robustness or efficiency compared with topology-frozen controls?

Required evidence:

- matched initial topology;
- structural-on vs structural-off conditions;
- topology/motif trajectories;
- behavioral and resource-cost metrics.

### RQ4 — Functional role of 5D organization

Does the 5D coordinate organization contribute functional value?

Required evidence:

- dimension shuffling;
- reduced-dimensional ablation;
- topology-matched non-spatial controls where feasible;
- metrics for locality, propagation, learning, motifs and robustness.

### RQ5 — Homeostasis and regulation

Do homeostatic/interoceptive mechanisms improve stability or recovery under perturbation?

Required evidence:

- regulation-on vs regulation-off;
- resource/continuity perturbations;
- missing/uncertain sensor conditions;
- recovery/stability metrics.

### RQ6 — Closed-loop embodiment

Does adaptation differ when actions have observed consequences and outcome-derived reward compared with replay/open-loop conditions?

Required evidence:

- deterministic environment baseline;
- action acceptance vs observed effect receipts;
- replay/open-loop control;
- actuator no-effect/failure control;
- episode-level adaptation metrics.

### RQ7 — Sensor loss and continuity

How does the system respond when an available sense becomes unavailable or unreliable?

Required evidence:

- explicit quality/unknown state;
- controlled sensor dropout;
- restoration phase;
- behavioral/regulatory recovery measures.

No anthropomorphic label such as fear is a measured variable unless separately operationalized; primary variables remain observable functional/regulatory quantities.

### RQ8 — Memory and predictive state

Can an explicit memory mechanism improve prediction, recall or action selection under held-out temporal conditions?

Required evidence:

- memory-on vs memory-off;
- prediction/recall metrics;
- persistence/restart equivalence;
- avoidance of data leakage.

### RQ9 — Multimodal grounding

Can typed camera/audio/document/network signals be integrated without making an LLM the hidden primary learner?

Required evidence:

- provenance-rich SignalFrames;
- frozen replay inputs;
- modality ablations;
- comparison of raw sensory vs externally structured representations.

### RQ10 — Scaling

Which mechanisms remain stable, deterministic and tractable as neuron/synapse counts grow?

Required evidence:

- scaling curves for wall time, memory and storage;
- deterministic equivalence after optimization;
- telemetry overhead measurement;
- no inference that larger scale implies greater cognition.

### RQ11 — Emergent functional organization

Do reproducible motifs or dynamical structures emerge that predict later behavior better than simple density/activity baselines?

Required evidence:

- preregistered motif/dynamics metrics;
- null/shuffled topology controls;
- held-out predictive evaluation;
- replication across seeds.

## AI research track — borrowed intelligence and control

AI participation is itself a research variable. Core questions include:

- Do different LLMs produce systematically different structural/experimental proposals from the same research packet?
- Are model-specific design fingerprints detectable in topology, motif or parameter proposals?
- How does human authorship/control shift when AI proposes but cannot directly execute?
- Can AI improve research efficiency without contaminating causal attribution?

Minimum experimental conditions should include, where relevant:

1. no-AI control;
2. frozen replay AI;
3. sham/random proposer;
4. one or more explicitly versioned LLM conditions;
5. identical input/research packet across model comparisons.

AI output is not empirical measurement. Model confidence is not empirical confidence. Any causal AI treatment must be manifest-bound and visible in provenance.

## Immediate experimental sequence

### Stage A — Freeze the baseline

- keep `main` CI and Scientific Integrity green;
- freeze canonical configs/protocol versions;
- record code/config/data/prompt digests;
- eliminate documentation ambiguity and accidental repository artifacts.

### Stage B — Productive learning replication

Run preregistered learning-on/off/sham conditions with holdout probes and multiple seeds. Existing experiment artifacts can inform protocol design but are not automatically promoted to evidence simply because they exist or completed.

### Stage C — Closed-loop embodiment replication

Use deterministic environments first. Compare closed-loop consequences with replay/open-loop and failure conditions. Only after the logical loop is evidentially stable should real-device experiments be treated as primary research runs.

### Stage D — Time calibration and 5D ablations

Calibrate simulation-vs-wall time, then execute 5D functional ablations under matched timing and topology constraints.

### Stage E — Regulation and sensor-loss

Test homeostasis/interoception and continuity under controlled perturbations, including explicit unknown sensor state.

### Stage F — Memory/world model

Introduce memory only after a stable no-memory behavioral baseline exists. Measure predictive value rather than relying on architectural naming.

### Stage G — Multimodal and AI treatment studies

Add provenance-rich multimodal inputs and compare AI conditions without weakening SNN causal boundaries.

## Evidence standard

A result is eligible to support a scientific claim only when:

- protocol identity is fixed;
- code/config/data partitions are recorded;
- execution completed without disqualifying runtime errors;
- controls are valid and comparable;
- AI treatment/provenance is explicit;
- quantitative analysis is traceable to deterministic/statistics tooling;
- DATA is promoted through the evidence gate;
- negative and inconclusive outcomes are retained rather than filtered out;
- independent repetition is performed when the claim requires reproducibility.

## Reporting standard

Every scientific report should distinguish:

- **Observation** — what was measured;
- **Transformation** — deterministic/statistical processing;
- **Evidence status** — accepted/rejected/inconclusive;
- **Interpretation** — human or AI narrative;
- **Limitation** — alternative explanations and missing controls.

## Relationship to development roadmap

[`ROADMAP.md`](ROADMAP.md) defines engineering sequencing. This document defines the research questions/evidence sequence. [`TODO.md`](TODO.md) is the active execution backlog. Historical research roadmaps and thesis notes remain useful context but do not override this canonical research plan.
