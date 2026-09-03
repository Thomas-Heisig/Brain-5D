# Brain-5D — Recursive Causal Loopbacks and Multirate Control

## Status

Architecture proposal for `v0.5.0-alpha.8`.

This document defines a non-anthropomorphic recursive self-causality layer for Brain-5D. It does **not** claim consciousness, subjective self-awareness, biological equivalence, or human-like introspection. The goal is narrower and experimentally testable: Brain-5D should be able to distinguish between effects caused by its own authorized actions, effects caused externally, and cases where causality remains uncertain.

## 1. Problem

The existing Alpha.7 experience loop is external:

```text
sensor -> encoder -> SNN -> decoder -> action -> environment -> reward -> learning
```

This is sufficient for action learning but not for explicit self-attribution. The system currently does not maintain a typed internal record equivalent to:

```text
I issued action A
I expected consequence E
I observed consequence O
E and O agree / disagree
therefore the observed change was probably self-caused / externally caused / uncertain
```

The missing capability is called **Recursive Causal Loopback**.

## 2. Design principle

Self-reflection must not be implemented as generated prose or an LLM judgment. It must emerge from typed, auditable causal records.

The canonical loop is:

```text
Current State
    |
    v
Action Selection
    |
    +--------------------> Efference Copy
    |                         |
    v                         v
Bounded Action          Effect Prediction
    |                         |
    v                         |
Environment / Actuator        |
    |                         |
    v                         |
Observed Consequence ---------+
    |
    v
Causal Comparator
    |
    +--> SELF_CAUSED
    +--> EXTERNAL_CAUSE
    +--> MIXED
    +--> UNCERTAIN
    |
    v
Self-Causal Model Update
    |
    v
Next Decision / Learning
```

The loopback is therefore an internal causal feedback loop layered on top of the existing perception-action loop.

## 3. Core contracts

### 3.1 EfferenceCopy

Immutable record created before an authorized action is executed.

Recommended fields:

- `command_id`
- `tick`
- `actuator_id`
- `action`
- `payload_digest`
- `predicted_effects`
- `prediction_horizon_ticks`
- `prediction_confidence`
- `source = SNN | deterministic_decoder | policy`
- `experiment_id`

### 3.2 EffectPrediction

A typed prediction, never natural-language-only.

Recommended fields:

- `signal_id`
- `expected_direction`
- `expected_min`
- `expected_max`
- `expected_delay_ticks`
- `tolerance`
- `confidence`

### 3.3 ObservedEffect

Derived exclusively from sensor or environment observations.

Recommended fields:

- `signal_id`
- `value_before`
- `value_after`
- `delta`
- `observation_tick`
- `source`
- `freshness`
- `confidence`

### 3.4 CausalAttribution

Recommended enum:

```text
SELF_CAUSED
EXTERNAL_CAUSE
MIXED
UNCERTAIN
NO_EFFECT
```

Recommended fields:

- `command_id`
- `expected_effect_digest`
- `observed_effect_digest`
- `match_score`
- `temporal_score`
- `alternative_cause_score`
- `classification`
- `confidence`
- `reason_codes`

No free-text reasoning is required for the scientific path.

## 4. Self-Causal Model

Introduce a `SelfCausalModel` that learns statistical or deterministic relations between:

```text
state + own_action -> expected_state_change
```

It must not write directly to synaptic state. It publishes typed signals that may be encoded into the SNN through the same controlled interfaces as other inputs.

The model should support:

- action-effect history;
- expected consequence prediction;
- confidence calibration;
- actuator-specific causal models;
- sensor-specific reliability;
- delayed consequences;
- missing observations;
- competing external causes;
- reset and deterministic replay;
- snapshot/persistence support.

## 5. Recursive loopbacks

A loopback is recursive when the result of causal attribution becomes a new input for later processing.

Example:

```text
Action A
 -> expected effect E
 -> observed effect E
 -> SELF_CAUSED confidence 0.92
 -> self-causal feedback encoded into SNN
 -> future action selection changes
```

A second-order loop may later compare the model's own prediction quality:

```text
prediction
 -> observation
 -> prediction error
 -> confidence update
 -> changed future prediction
```

This is the intended meaning of self-reflection in Alpha.8: measurable recursive evaluation of the system's own action-effect model.

## 6. Multirate architecture

Brain-5D should not force all mechanisms to run at the same cadence.

The SNN remains tick-based and event-driven. The multirate controller is an additional scheduler above the existing runtime.

Default conceptual layers:

### FAST

Target default: **100 Hz** (10 ms period).

Purpose:

- safety-relevant interoception;
- actuator feedback;
- fan/thermal/network integrity;
- fast causal consequence matching;
- emergency or withdrawal responses;
- short-horizon prediction error.

100 Hz is a configurable control cadence, **not** a claim that all SNN operations run at exactly 100 Hz.

### MEDIUM

Target default: **10 Hz** (100 ms period).

Purpose:

- drive integration;
- body-schema updates;
- causal-confidence accumulation;
- task progress;
- resource-pressure integration;
- action policy updates.

### SLOW

Target default: **1 Hz** (1000 ms period).

Purpose:

- long-horizon self-model update;
- structural regulation proposals;
- persistence summaries;
- long-term trend integration;
- operator/dashboard summaries.

### VERY_SLOW / ADAPTIVE

Optional, default disabled.

Purpose:

- minute-scale adaptation;
- chronic signal integration;
- morphology/growth budgeting;
- long-horizon consolidation.

## 7. Scheduler rules

Introduce a deterministic `MultirateScheduler`.

Requirements:

1. Scheduling must be based on logical simulation time for reproducible experiments.
2. Wall-clock execution may be used in Operator mode but must be explicitly classified.
3. Each layer receives a stable cadence configuration.
4. A layer may be disabled independently.
5. Catch-up behavior must be explicit: `drop`, `catch_up`, or `single_latest`.
6. The scheduler must record the effective execution tick for each layer.
7. Scientific runs must persist effective cadence settings in the experiment manifest.
8. Changing cadence in a scientific run is treatment-sensitive and requires protocol/version tracking.

## 8. Massive parallelism

"Parallel" must not mean uncontrolled nondeterministic threading in scientific runs.

Brain-5D should distinguish:

- **logical parallelism**: many signals, regions, sensors or causal hypotheses evaluated in the same logical step;
- **physical parallelism**: CPU/GPU/thread/process execution used as an optimization.

Scientific correctness is defined by logical ordering and deterministic state, not by OS scheduling.

Recommended rule:

```text
parallel execution is allowed only if canonical output ordering and state digest remain identical
```

Performance experiments may compare sequential and parallel execution, but scientific behavior must remain equivalent.

## 9. Settings catalog

The canonical Dashboard `Scientific Settings` catalog must expose these parameters through `build_parameters()`.

Recommended configuration:

```yaml
recursive_loopback:
  enabled: false
  self_causal_feedback_enabled: false
  prediction_horizon_ticks: 25
  causal_window_ticks: 50
  attribution_threshold: 0.75
  uncertainty_threshold: 0.40
  max_pending_actions: 256
  persist_records: true
  feedback_gain: 0.0

multirate:
  enabled: false
  mode: logical_time
  fast_hz: 100.0
  medium_hz: 10.0
  slow_hz: 1.0
  very_slow_hz: 0.0
  catch_up_policy: single_latest
  parallel_mode: logical
```

### Required Scientific Settings metadata

| Parameter | Default | Runtime mutable | Restart | Scientific sensitive |
|---|---:|---|---|---|
| `recursive_loopback.enabled` | false | no | yes | yes |
| `recursive_loopback.self_causal_feedback_enabled` | false | no | yes | yes |
| `recursive_loopback.prediction_horizon_ticks` | 25 | yes* | no | yes |
| `recursive_loopback.causal_window_ticks` | 50 | yes* | no | yes |
| `recursive_loopback.attribution_threshold` | 0.75 | yes* | no | yes |
| `recursive_loopback.uncertainty_threshold` | 0.40 | yes* | no | yes |
| `recursive_loopback.max_pending_actions` | 256 | no | yes | yes |
| `recursive_loopback.persist_records` | true | no | yes | yes |
| `recursive_loopback.feedback_gain` | 0.0 | yes* | no | yes |
| `multirate.enabled` | false | no | yes | yes |
| `multirate.mode` | logical_time | no | yes | yes |
| `multirate.fast_hz` | 100.0 | yes* | no | yes |
| `multirate.medium_hz` | 10.0 | yes* | no | yes |
| `multirate.slow_hz` | 1.0 | yes* | no | yes |
| `multirate.very_slow_hz` | 0.0 | yes* | no | yes |
| `multirate.catch_up_policy` | single_latest | no | yes | yes |
| `multirate.parallel_mode` | logical | no | yes | yes |

`yes*` means mutable only in Operator/Exploratory mode. Confirmatory experiments must treat changes as protocol-sensitive pending changes.

## 10. Safety and scientific boundaries

- Loopback feedback must be disabled by default.
- The Language Organ may describe causal records but may not create or overwrite them.
- LLM output may not set `SELF_CAUSED` or any causal classification.
- Rewards remain environment-derived.
- The causal model may not directly mutate network structure or weights.
- Unknown or missing observations must reduce confidence rather than be interpreted as successful self-causation.
- External actuator effects require independent observation when possible.
- Operator mode and scientific mode must remain distinguishable in provenance.

## 11. Experiments

### EXP-SELF-0001 — Self vs external causation

Conditions:

1. own action causes expected effect;
2. same effect occurs without own action;
3. own action occurs but expected effect is blocked;
4. own action and external cause occur together;
5. sensor observation is delayed;
6. sensor observation is missing.

Primary measures:

- attribution accuracy;
- false self-attribution rate;
- false external-attribution rate;
- uncertainty calibration;
- temporal matching error;
- adaptation across repeated trials.

### EXP-RATE-0001 — Multirate ablation

Compare at minimum:

- single-rate baseline;
- FAST=10 Hz;
- FAST=50 Hz;
- FAST=100 Hz;
- FAST=200 Hz;
- FAST=100 Hz with MEDIUM/SLOW disabled;
- default multirate stack.

Measure:

- causal attribution latency;
- task success;
- stability;
- CPU/RAM/storage cost;
- deterministic state digest;
- missed/late safety signals.

No cadence is scientifically privileged before evidence exists.

## 12. Definition of done

The feature is implemented only when:

- deterministic unit tests cover all causal classifications;
- replay produces identical attribution records;
- loopback-off reproduces the previous Alpha.7 behavior;
- all new settings appear in Scientific Settings with correct metadata;
- scientific manifests persist effective loopback and cadence settings;
- no LLM has causal write authority;
- Python 3.11/3.12/3.13 tests pass;
- mypy, pyright, Black, Ruff and Scientific Integrity CI are green;
- `EXP-SELF-0001` and `EXP-RATE-0001` are preregistered before any evidence claim.
