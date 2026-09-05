# Brain-5D Research Positioning and Evidence Program

**Status:** canonical research-positioning document  
**Baseline:** `brain5d-core 0.5.0a7`  
**Date:** 2026-09-05

## 1. Project classification

Brain-5D is an experimental research framework at the intersection of computational neuroscience, neuromorphic artificial intelligence, embodied adaptive systems and reproducible AI-assisted research.

Its technical core is a sparse five-dimensional spiking neural network using Izhikevich-type neurons, delayed event propagation, local plasticity, homeostatic regulation and bounded structural plasticity. Around that core, the project provides deterministic persistence, embodiment interfaces, experience loops, observability, experiment registries, evidence gates and read-only/proposal-only AI research assistance.

The project explicitly does **not** treat implementation, visual complexity, passing tests, recurrence, adaptive morphology or language output as evidence of AGI, consciousness, sentience or biological equivalence. Scientific claims must be tied to controlled experiments and accepted evidence artifacts.

## 2. Distinguishing characteristics

Brain-5D is differentiated by the combination of the following properties rather than by any single mechanism:

1. **Sparse 5D neural organization** with explicit coordinates and experimentally testable dimensionality claims.
2. **Deterministic persistence** through snapshots, journals, checkpoints and reproducible RNG/state restoration.
3. **Wesen/Embodiment separation** between technical body interfaces and read-only live visualization.
4. **Scientific provenance by construction** with DATA/EVID separation, manifests, digests, integrity gates and frozen replay.
5. **Unknown-state rendering** in which missing telemetry remains missing rather than being replaced by plausible constants.
6. **Bounded AI participation** in which research assistants, language organs and proposal systems have no implicit write authority over neural state, reward, memory or scientific evidence.
7. **Observable causal chain support** from sensor input through SNN/action to receipts and outcomes, while preserving the distinction between a traced sequence and experimentally demonstrated causality.

## 3. Scientific opportunity

The principal opportunity is not to add more mechanisms, but to convert the existing engineering substrate into a sequence of falsifiable, preregistered and independently repeatable experiments.

The highest-value scientific targets are:

- whether five-dimensional organization has measurable functional value beyond an equivalent lower-dimensional or shuffled representation;
- whether recurrence supports persistent activity, temporal integration or working-memory-like behavior under controlled conditions;
- whether local reward-modulated learning improves held-out behavior rather than only changing weights;
- whether structural plasticity improves function, robustness or efficiency beyond topology-frozen controls;
- whether homeostasis and interoceptive regulation improve stability and recovery under resource or sensor perturbation;
- whether closed-loop embodiment produces learning differences that disappear in replay/open-loop controls;
- whether a machine-native self-model can be operationalized as predictive/useful internal state without anthropomorphic assumptions;
- whether bounded AI participation changes experiment design, topology proposals or research efficiency in systematic and model-specific ways.

## 4. Evidence hierarchy

Every project claim must be associated with one of the following levels:

1. **Implemented mechanism** — code exists and the contract is tested.
2. **Observed runtime behavior** — a run produced measurable state/activity.
3. **Executed controlled experiment** — a fixed protocol with controls produced valid DATA.
4. **Accepted evidence** — DATA passed the scientific integrity/evidence gate.
5. **Replicated finding** — an independent repeat reproduced the relevant effect.
6. **Scientific interpretation** — a bounded conclusion states what the evidence supports and what remains unresolved.

A higher level may use lower levels as prerequisites, but no lower level may be described as if it already established a higher one.

## 5. Benchmark and replication program

### 5.1 Internal reference benchmarks

Brain-5D should maintain a small, versioned benchmark suite whose purpose is scientific comparability rather than leaderboard optimization. At minimum it should include:

- deterministic spike-response benchmark;
- propagation/recurrence benchmark;
- productive-learning benchmark with learning-on, learning-off and sham conditions;
- temporal-order benchmark;
- structural-plasticity benchmark;
- sensor-loss/recovery benchmark;
- deterministic closed-loop embodiment benchmark;
- persistence/restart equivalence benchmark;
- scaling benchmark for wall time, memory, storage and telemetry overhead.

### 5.2 External comparison tasks

Where compatible with the research question, standardized tasks may be added to compare Brain-5D with conventional baselines. Candidate classes include event/spike-coded classification tasks, temporal sequence tasks and simple control environments. The purpose is not to claim broad superiority, but to establish whether an effect survives comparison with simpler alternatives.

For any external benchmark:

- conversion from raw input to spikes must be declared;
- train/validation/holdout partitions must be fixed;
- baseline model capacity and compute must be reported;
- hyperparameter search must be separated from final evaluation;
- negative results must be retained.

### 5.3 Independent replication

A claim labeled reproducible should require at least one replication that is distinct from the original evidence-producing run. Strong claims should prefer a clean process, frozen protocol, different seeds and, where practical, execution by another operator or environment.

## 6. Preregistration and Open Science workflow

Before a confirmatory experiment starts, its preregistration record should contain:

- research-question and hypothesis IDs;
- primary and secondary outcomes;
- experimental and control conditions;
- seed strategy and number of repeats;
- stopping rule;
- inclusion/exclusion criteria;
- planned statistical analysis;
- expected failure modes;
- code/config/protocol identifiers;
- AI treatment identity, prompt digest and authority boundary if AI participates.

The preregistration artifact should be immutable after the first scientific run. Deviations belong in an amendment with timestamp and rationale.

## 7. Causal inference standard

Because Brain-5D is highly recurrent and adaptive, correlations between activity, topology and behavior are insufficient for causal claims.

Causal questions should use interventions such as:

- mechanism on/off ablation;
- topology-frozen vs structural-plasticity conditions;
- recurrence intact vs recurrence removed;
- dimensionality preserved vs shuffled/reduced controls;
- sensor present vs degraded/lost/restored;
- actuator effective vs accepted-but-no-effect;
- closed-loop vs replay/open-loop;
- memory/self-model enabled vs disabled;
- AI treatment vs no-AI/frozen/sham treatment.

Whenever possible, matched initial state, identical input schedule and deterministic replay should be used to isolate the intervention.

## 8. Performance and scaling strategy

Performance work must preserve scientific equivalence. Optimization should follow this sequence:

1. measure target Hz, achieved Hz, wall-time ratio, tick cost and telemetry/storage overhead;
2. profile by subsystem before changing algorithms;
3. establish scaling curves over increasing neuron and synapse counts;
4. optimize only demonstrated bottlenecks;
5. verify deterministic equivalence before and after optimization;
6. document any optimization that changes numerical precision, event ordering or timing semantics as a scientific protocol change.

Potential acceleration technologies such as vectorization, Numba/Cython, compiled kernels or GPU execution should therefore be treated as optional implementation tracks, not assumed scientific improvements.

## 9. Dashboard and research tooling

The research dashboard should evolve from live inspection toward longitudinal comparison without turning presentation into evidence. Useful additions include:

- experiment-to-experiment comparison using accepted DATA/EVID artifacts;
- historical metric trajectories across protocol versions;
- control-vs-treatment overlays;
- provenance and preregistration status indicators;
- direct navigation from a plotted result to the underlying DATA, transformation and claim;
- explicit labels for exploratory, confirmatory, invalid and replicated runs.

Browser-local Wesen history remains operator visualization unless a scientific protocol explicitly persists the same state in DATA.

## 10. Additional research questions

The following questions extend the current canonical roadmap and should be represented in the registry/protocol backlog before execution.

### RQ-REC-001 — Recurrence and persistent activity

Under matched topology and input conditions, does recurrent connectivity produce reproducible persistent activity or delayed response structure beyond an acyclic control?

### RQ-GEN-001 — Generalization after local learning

Does reward-modulated local learning improve performance on held-out or perturbed conditions that were not used during adaptation?

### RQ-LIFE-001 — Lifelong learning and interference

Can combined STDP, homeostasis and structural plasticity support sequential learning with less catastrophic interference than matched ablated conditions?

### RQ-SELFMDL-001 — Functional self-model

Does access to delayed/predicted machine-body state improve prediction, regulation or action selection compared with a matched system without that internal body-state representation?

### RQ-LAT-001 — Sensor-actuator latency

How does controlled sensor-to-actuator latency affect closed-loop learning, stability and action effectiveness?

### RQ-CAUSAL-001 — Causal attribution in adaptive recurrent systems

Which intervention and replay methods provide stable causal estimates when topology, weights and internal state are changing over time?

### RQ-REPL-001 — Independent replication reliability

What fraction of accepted Brain-5D findings survives clean-process replication across seeds, operators and supported Python/runtime environments?

### RQ-AI-DESIGN-001 — Model-specific design fingerprints

Do different LLMs produce systematically distinguishable topology, parameter or experimental-design proposals when given the same frozen research packet and the same authority limits?

### RQ-AI-EFF-001 — AI-assisted research efficiency

Can bounded research AI reduce time or errors in experiment design/review without increasing invalid runs, provenance violations or unsupported claims?

## 11. Publication pathway

A suitable publication sequence is:

1. **Methods/software paper** describing deterministic architecture, provenance and evidence contracts without overstating scientific findings.
2. **Benchmark/ablation paper** on the functional role of 5D organization and recurrence.
3. **Learning/embodiment paper** on productive local learning and closed-loop consequences with matched controls.
4. **AI-assisted research paper** on model-specific proposal fingerprints, authorship/control and causal contamination safeguards.

A preprint should not be released as a claim-bearing scientific result until the corresponding DATA/EVID package is reproducible from a frozen manifest.

## 12. Success criteria for the next phase

The next phase is successful if Brain-5D produces a smaller number of stronger results rather than a larger number of mechanisms. The target is a chain of preregistered experiments in which at least one central architectural claim is either supported or clearly rejected by replicated evidence.
