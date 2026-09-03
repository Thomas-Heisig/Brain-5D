# Brain-5D — Learning Preparation Studio

> Status: architecture and guarded-contract foundation
> Canonical principle: AI may prepare learning; Brain-5D performs learning.

## 1. Purpose

Brain-5D already contains the neural learning mechanisms (`LearningEngine`, STDP,
eligibility traces and reward-modulated plasticity). What is still missing is a
coherent operator-facing workflow that answers a different question:

> What should be prepared before the learning mechanisms are allowed to change
> the network, and how can that preparation be made observable and reproducible?

The Learning Preparation Studio fills this gap. It does **not** synthesize a
neural pattern and does not prescribe how the SNN must represent information.
It prepares the conditions under which the SNN can learn from experience.

## 2. Architectural boundary

```text
Human / AI assistant
        |
        v
Learning Preparation Proposal
        |
        +--> objective
        +--> source provenance
        +--> train / validation / holdout partition
        +--> baseline protocol
        +--> exposure protocol
        +--> evaluation protocol
        +--> stopping rule
        +--> controls
        |
        v
Human approval / protocol registration
        |
        v
PreparedLearningPlan
        |
        |  NO direct weights / spikes / currents / reward values
        v
Experience / Environment / Sensor pipeline
        |
        v
Brain-5D SNN
        |
        v
LearningEngine
        |
        v
observed network and behavior change
```

The preparation layer is therefore upstream of experience and plasticity. It
may determine *what is presented, in which experimental order, from which
provenance-bearing source, with which evaluation*, but not *what neural pattern
the network should contain afterwards*.

## 3. AI role

AI assistance is useful for preparation tasks such as:

- converting an operator learning goal into a measurable objective;
- suggesting baseline measurements;
- proposing train/validation/holdout separation;
- checking whether source provenance is complete;
- suggesting task difficulty progression;
- proposing repetitions and stopping criteria;
- identifying missing controls;
- proposing evaluation metrics;
- comparing a planned learning run with existing research protocols;
- explaining why a planned run may be scientifically confounded.

AI has **proposal-only authority**. AI output must never directly provide or
apply:

- synaptic weights or weight matrices;
- target spike trains or spike patterns;
- injected current arrays;
- direct eligibility traces;
- direct plasticity updates;
- reward values that bypass the environment or deterministic verifier;
- structural mutation commands.

A discussion may mention STDP, reward or spikes conceptually. The prohibition
applies to executable/direct mutation data.

## 4. Core contracts

The initial implementation lives in `src/learning/preparation.py`.

### `LearningObjective`

Defines a measurable goal without prescribing its neural representation.

Required fields:

- `objective_id`
- `description`
- `success_metric`
- `evaluation_question`

### `LearningSourceRef`

Links the plan to provenance-bearing inputs.

Required fields:

- `source_id`
- `digest`
- `origin`
- `partition`: `train`, `validation` or `holdout`
- `trust`

### `LearningPreparationProposal`

A non-executable preparation proposal containing:

- objective;
- sources;
- baseline protocol;
- exposure protocol;
- evaluation protocol;
- stopping rule;
- controls;
- origin (`human` or `ai_assisted`);
- AI interaction provenance when applicable;
- canonical digest;
- `authority = proposal_only`;
- `executed = false`.

### `PreparedLearningPlan`

Human-approved preparation artifact. Approval changes the governance status,
not the runtime authority:

```text
runtime_authority = none
executed = false
```

Execution remains a separate registered workflow.

### `LearningPreparationGuard`

Fail-closed validation rejects direct neural-control fields in future API or AI
payloads. This is an additional boundary; it does not replace the existing
Scientific AI Firewall.

## 5. Frontend model

The operator dashboard should expose a dedicated **LEARNING** workspace between
CONTROL and RESEARCH.

The recommended visual workflow is:

```text
1. Lernziel
      |
2. Quellen & Provenienz
      |
3. Baseline
      |
4. Lernvorbereitung
      |
5. Lernen / Experience Run
      |
6. Post-Learning Evaluation
      |
7. Vergleich & Evidence
```

### Panel A — Current learning state

Read-only values from the existing dashboard snapshot:

- LearningEngine attached/unavailable;
- STDP enabled / armed / active;
- eligibility enabled;
- reward path enabled;
- STDP updates;
- reward updates;
- pending rewards;
- learning update time;
- current experiment mode/session.

### Panel B — Learning objective

Operator enters a goal in semantic terms, for example:

> Learn to distinguish whether an actuator action produced the expected
> environment effect.

The UI must not ask the operator or AI for a desired spike pattern.

### Panel C — AI preparation assistant

The assistant receives only preparation context and returns a proposal for:

- operational objective;
- baseline;
- source/data partition;
- exposure sequence at the task/environment level;
- controls;
- evaluation;
- stopping rule;
- risks/confounds.

The response is visibly labeled **AI PROPOSAL — NOT APPLIED**.

### Panel D — Pre/Post diagnostics

The recently added impulse-response and temporal-comparison tools should be used
as optional learning diagnostics:

```text
Pre-learning NetworkImpulseProbe
        |
Learning exposure
        |
Post-learning NetworkImpulseProbe
        |
NetworkResponseSignature comparison
```

and:

```text
TemporalStateFrame before
        |
learning interval
        |
TemporalStateFrame after
        |
TemporalComparator
```

A changed signature is **not** automatically evidence of successful learning.
It becomes informative only together with task performance, control groups and
registered metrics.

## 6. Recommended learning workflow

### Phase 0 — Freeze and baseline

- capture source commit / snapshot;
- record seed and effective settings;
- execute task baseline;
- optional impulse-response baseline;
- optional temporal reference frame;
- verify train/validation/holdout separation.

### Phase 1 — Prepared exposure

- environment presents observations/tasks;
- SNN produces its own activity;
- LearningEngine applies only configured plasticity rules;
- reward originates from the environment or deterministic TaskOutcomeVerifier;
- AI has no causal write access.

### Phase 2 — Evaluation

- disable or freeze learning if protocol requires it;
- repeat preregistered evaluation;
- compare behavior before/after;
- compare weight/state diagnostics only as secondary measures;
- evaluate holdout/generalization.

### Phase 3 — Scientific interpretation

AI may summarize or critique the resulting DATA after the run, but quantitative
metrics must come from deterministic code. Any AIRR remains interpretation, not
evidence.

## 7. What the quoted external assessment gets right

Useful elements:

- treating the impulse probe as a repeatable diagnostic stimulus;
- measuring latency, propagation and recurrence rather than narrating the spike;
- comparing state over multiple time horizons;
- making learning visible as a before/after process;
- keeping consciousness claims outside technical results.

## 8. What must be corrected

### Recurrence is not self-reflection

A spike returning to a source or previously active region demonstrates recurrent
dynamics. Self-causal reflection requires an action record, predicted effect,
independent observation and causal attribution.

### No known "critical mass" at 5,000 neurons or 36,031 synapses

Those numbers describe a useful engineering scale, not a scientifically known
threshold for pattern formation, cognition or thinking.

### FAST/MEDIUM/SLOW are currently reference horizons

The implemented `TemporalStateMemory` provides bounded references without
rewinding runtime state. A true multirate scheduler is a separate planned
feature and must not be claimed from the reference-memory implementation alone.

### A sixth dimension does not automatically create cognition

Adding another coordinate dimension may change topology and capacity, but any
claim about learning, interference or cognition requires explicit ablation and
measurement.

## 9. Definition of done for the full Learning Studio

- typed preparation contracts are implemented and tested;
- AI direct-neural-write fields fail closed;
- LEARNING workspace is visible in the dashboard;
- current learning state is read from real snapshot fields;
- AI assistant creates proposal-only preparation text/structured drafts;
- AI proposal cannot start a run or alter settings directly;
- human approval is explicit;
- prepared plan is digest-bound and persisted with experiment provenance;
- execution is a separate structured workflow;
- Pre/Post task evaluation is first-class;
- optional impulse and temporal diagnostics are attached to the learning run;
- TaskOutcomeVerifier is the only automated source of task-success reward;
- train/validation/holdout partitions remain separate;
- learning-off, sham or equivalent controls are supported;
- scientific claims require preregistration, independent repetitions and EVID.

## 10. Scientific principle

> The AI may design the lesson. The environment may present the lesson. The
> plasticity mechanisms may change the network. Only the Brain-5D system may
> develop the internal neural representation.
