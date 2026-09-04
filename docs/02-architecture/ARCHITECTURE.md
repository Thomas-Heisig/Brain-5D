# Brain-5D Architecture

## Purpose

Brain-5D is a modular research framework around a sparse five-dimensional spiking neural network. Its architecture is designed to separate **neural dynamics**, **learning**, **structural adaptation**, **embodiment**, **persistence**, **research evidence**, **AI interpretation** and **operator tooling** so that changes in one layer do not silently redefine the scientific meaning of another.

The SNN is the primary adaptive system. External AI components may observe, interpret or propose within explicit contracts, but they do not gain implicit authority to write neural state, rewards, memory or scientific evidence.

## System map

```text
                  External / simulated environment
                              |
                sensors + host interoception
                              |
                              v
                  +-----------------------+
                  | Embodiment / adapters |
                  | auth + audit + quality|
                  +-----------+-----------+
                              |
                              v
                  +-----------------------+
                  | Signal / Experience   |
                  | encoding + outcome    |
                  +-----------+-----------+
                              |
                              v
+------------------------------------------------------------------+
|                    Sparse 5D SNN Core                            |
| neurons | synapses | event queue | deterministic RNG | I/O cells |
+----------------------+----------------------+--------------------+
                       |                      |
                       v                      v
              +----------------+     +-------------------+
              | Learning       |     | Homeostasis       |
              | STDP / elig.   |     | rate / threshold  |
              | reward / 3F    |     | energy regulation|
              +-------+--------+     +---------+---------+
                      |                        |
                      +-----------+------------+
                                  |
                                  v
                     +--------------------------+
                     | Self-organization        |
                     | signal -> proposal       |
                     | -> approval -> mutation  |
                     +------------+-------------+
                                  |
                                  v
                         controlled topology

Persistence surrounds the mutable system:
  .b5d snapshots + delta journal + structural journal + checkpoints + restore

Research surrounds execution:
  registries + manifests + DATA + EVID + scientific integrity + provenance

Dashboard and AI layers connect only through explicit APIs/contracts.
```

## 1. Sparse 5D neural core

Brain-5D does not materialize a full five-dimensional tensor. Existing neurons are stored sparsely and identified by packed 5D coordinates. Synapses are explicit graph edges with delay and weight state.

Core responsibilities include:

- deterministic neuron integration;
- delayed event delivery;
- spike production and propagation;
- topology accounting;
- input/output cell boundaries;
- deterministic RNG state capture;
- post-step hooks for bounded integrations.

The core must not depend on dashboard rendering, language models or research prose.

## 2. Tick and time semantics

A simulation tick is a causal execution unit, not automatically a claim about biological time. The configured `dt` defines simulation time; runtime target Hz controls wall-clock pacing and must not silently change neural equations.

The core ordering is deterministic: deliver due inputs/events, integrate neurons once, record spikes, schedule delayed events, publish the completed step result, and advance the tick. Components that observe a step consume completed state rather than partially mutated state.

Scientific protocols must record `dt`, pacing mode and relevant timing parameters. Changing wall-clock execution speed is an engineering change unless it also changes simulated `dt` or protocol timing.

## 3. Learning

The learning layer contains:

- pair-based STDP;
- signed eligibility traces;
- delayed reward handling;
- reward-modulated / three-factor updates;
- productive learning experiments;
- preparation contracts that separate proposed training material from execution.

A preparation plan is not a neural write. AI-generated preparation is proposal-only and provenance-bound. Direct AI writes to synapses, neurons or rewards are rejected by contract.

## 4. Homeostasis and interoception

Homeostasis regulates explicitly modeled quantities such as firing-rate targets, thresholds and energy. Embodiment interoception converts host/system observations into typed signals with quality/availability metadata.

Missing sensor values remain unknown. Unknown is not converted into nominal, healthy or zero without an explicit transformation rule.

## 5. Structural self-organization

Structural change is intentionally split into stages:

```text
Homeostasis/observations
        -> SelfOrganizationPolicy
        -> StructuralProposal
        -> Coordinator
        -> reject / manual approval / bounded auto-approval
        -> StructuralPlasticityEngine
        -> Manipulator
        -> NeuralNetwork
        -> StructuralChangeRecord
        -> StructuralJournal
        -> Undo / Recovery
```

Proposal generation does not mutate topology. Approval does not bypass validation. Accepted mutations are journaled and recoverable.

## 6. Embodiment and experience loop

The embodiment layer provides typed sensor, actuator and environment abstractions plus authorization, capability limits, rate limits, emergency stop and durable audit paths. Device discovery only states that a device appears available; it does **not** grant permission to capture or actuate.

The intended closed loop is:

```text
observation -> encoding -> SNN -> action proposal -> authorization
-> actuator/environment -> observed terminal state -> verified outcome -> reward
```

Reward should be derived from an observed/verifiable outcome contract, not merely from an accepted action command.

The real-body subsystem may expose CPU, memory, temperatures/fans where the host provides them, plus discovered camera/audio/display/printer capabilities. Unavailable host telemetry remains `None`/unknown rather than fabricated.

## 7. Persistence and deterministic recovery

Persistence is not just serialization. Brain-5D maintains explicit recovery boundaries:

- `.b5d` snapshots;
- append/commit delta journal;
- structural journal;
- runtime checkpoints;
- canonical state digests;
- restore-and-continue verification;
- undo/replay for structural changes.

The scientific value of a restored run depends on state completeness and deterministic continuation, not merely successful file loading.

## 8. Research and evidence architecture

Research state is separated from runtime state. Registries define questions, hypotheses, claims, methods and sources. Experiments produce manifests and `DATA`; evidence promotion occurs through explicit validity checks.

A critical distinction is:

```text
implementation test != experiment result != accepted evidence != interpretation
```

AI analysis records, AIRR reports and narrative summaries are interpretations unless a protocol explicitly defines their role. Quantitative scientific metrics must carry deterministic/statistics provenance rather than being invented by a language model.

## 9. AI boundaries

Brain-5D includes research-assistant and language-organ contracts, but authority is fail-closed:

- observing: may read authorized state;
- interpreting: may produce labeled interpretation;
- proposing: may create bounded proposals;
- causal intervention: requires an explicit registered treatment/capability and human or protocol approval.

Scientific runs reject uncontrolled live-network AI where reproducibility cannot be established. Frozen replay/sham conditions exist so AI involvement can itself become an experimental variable.

## 10. Dashboard boundary

The dashboard is the operator/research interface, not a second simulation engine. Its presentation shell and experience layer are presentation/navigation only. Runtime mutations continue through explicit control services, structural APIs and approved domain paths.

Primary workspaces are Overview, Network, Control, Research, Release, Settings and Embodiment. Unknown measurements must remain visibly unknown.

## 11. Architectural invariants

1. **Determinism where claimed** — identical controlled inputs/seeds/configuration must be testable for identical state evolution.
2. **No hidden scientific writes** — UI/LLM interpretation cannot mutate evidence or neural state by implication.
3. **Fail closed** — missing permissions, missing provenance or unknown data do not default to success.
4. **Observed ≠ inferred** — measured state and model interpretation are represented separately.
5. **Availability ≠ authorization** — especially for devices and actuators.
6. **DATA ≠ EVID** — experiment output requires validity/evidence promotion before claim support.
7. **Simulation time ≠ wall time** — runtime pacing is separate from model time semantics.
8. **Recovery is part of correctness** — persistence must preserve causal state, not only visible values.

## Detailed subsystem documents

- [`B5D_FORMAT.md`](B5D_FORMAT.md)
- [`DETERMINISTIC_RESTORE.md`](DETERMINISTIC_RESTORE.md)
- [`STRUCTURAL_PLASTICITY_ALPHA5.md`](STRUCTURAL_PLASTICITY_ALPHA5.md) — historical phase contract still useful for subsystem detail
- [`EMBODIMENT_FOUNDATION.md`](EMBODIMENT_FOUNDATION.md)
- [`EMBODIMENT_REAL_BODY.md`](EMBODIMENT_REAL_BODY.md)
- [`LEARNING_PREPARATION_STUDIO.md`](LEARNING_PREPARATION_STUDIO.md)
- [`RECURSIVE_CAUSAL_LOOPBACKS.md`](RECURSIVE_CAUSAL_LOOPBACKS.md)
- [`../03-dashboard/DASHBOARD.md`](../03-dashboard/DASHBOARD.md)
- [`../../research/README.md`](../../research/README.md)
