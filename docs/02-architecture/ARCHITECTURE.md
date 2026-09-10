# MHRN Architecture

## Purpose

MHRN is a modular research framework around a sparse five-dimensional spiking neural network. Its architecture separates **neural dynamics**, **learning**, **structural adaptation**, **embodiment**, **peripheral multi-network processing**, **persistence**, **research evidence**, **AI interpretation** and **operator tooling** so that changes in one layer do not silently redefine the scientific meaning of another.

The SNN is the primary adaptive system. External AI components and peripheral neural networks may observe, interpret, transform or propose within explicit contracts, but they do not gain implicit authority to write canonical neural state, rewards, memory or scientific evidence.

## System map

```text
External / simulated / virtual environment
            |
            v
Sensors / network / camera / audio / database / logic / devices
            |
            v
+---------------------------------------------+
| Embodiment adapters                         |
| authorization + audit + quality + provenance|
+----------------------+----------------------+
                       |
              optional peripheral area(s)
        CNN / Transformer / RNN / GNN / memory
         logic/projector / custom open-set area
                       |
                explicit gateway
                       |
                       v
+------------------------------------------------------------+
| Sparse 5D SNN Core                                         |
| neurons | synapses | event queue | deterministic RNG | I/O |
+----------------------+----------------------+--------------+
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
                     | proposal -> approval     |
                     | -> bounded mutation      |
                     +------------+-------------+
                                  |
                                  v
                         controlled topology

SNN action proposal
        |
        v
explicit efferent gateway
        |
optional peripheral decoder/control area
        |
        v
authorization/safety -> ActuatorHub -> observed outcome -> feedback/reward

Persistence surrounds mutable state.
Research provenance surrounds execution.
Wesen is primarily observational and consumes published state; its explicit
sensor, memory-control and experiment-only gateway actions remain bounded by
their backend safety and research gates.
```

## 1. Sparse 5D neural core

MHRN does not materialize a full five-dimensional tensor. Existing neurons are stored sparsely and identified by packed 5D coordinates. Synapses are explicit graph edges with delay and weight state.

Core responsibilities include deterministic neuron integration, delayed event delivery, spike propagation, topology accounting, I/O boundaries, deterministic RNG state capture and bounded post-step integrations.

The core must not depend on dashboard rendering, language models or peripheral ANN frameworks.

## 2. Tick and time semantics

A simulation tick is a causal execution unit, not automatically a claim about biological time. Configured `dt` defines simulation time; runtime target Hz controls wall-clock pacing and must not silently change neural equations.

Scientific protocols must record `dt`, pacing mode and timing parameters. Changing wall-clock execution speed is an engineering change unless it also changes model/protocol time semantics.

## 3. Learning

The learning layer contains pair-based STDP, signed eligibility traces, delayed reward handling, reward-modulated/three-factor updates, productive-learning experiments and preparation contracts.

A preparation plan is not a neural write. AI-generated preparation is proposal-only and provenance-bound.

## 4. Homeostasis and interoception

Homeostasis regulates explicitly modeled quantities such as firing-rate targets, thresholds and energy. Embodiment interoception converts host/system observations into typed signals with quality/availability metadata.

Machine-native interoception may include CPU, memory, temperature/fan, storage, network and continuity signals where available. Missing sensor values remain unknown.

## 5. Structural self-organization

Structural change remains staged:

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

The embodiment layer provides typed sensor, actuator and environment abstractions plus authorization, capability limits, rate limits, emergency stop and durable audit paths. Device discovery states availability only; it does **not** grant permission to capture or actuate.

The intended loop is:

```text
observation -> encoding -> SNN -> action proposal -> authorization
-> actuator/environment -> observed terminal state -> verified outcome -> reward
```

Reward should be derived from an observed/verifiable outcome contract, not merely from an accepted action command.

## 7. Neural Symbiosis — peripheral multi-network boundary

`Neural Symbiosis` is part of **Embodiment**. It is not a replacement core and does not redefine canonical SNN learning.

The open-set `NetworkAreaAdapter` contract allows dedicated processing stages to be inserted between endpoints and the SNN. Built-in descriptors cover common families such as CNN, Vision Transformer, Transformer, LSTM, GRU, RNN, GNN, Modern Hopfield, reservoir/ESN, MLP, VAE, GAN, diffusion, autoencoder, peripheral SNN, multimodal and neuro-symbolic networks. Custom architectures remain possible.

Virtual areas can represent symbolic logic engines, databases, knowledge graphs, retrieval systems, external memory stores or other non-neural services. When needed, an explicit neural projector can bridge a virtual representation into the SNN boundary.

Typical paths are:

```text
Camera -> CNN / ViT -> afferent gateway -> 5D-SNN
Microphone -> Audio/Speech Transformer -> gateway -> 5D-SNN
Database -> Knowledge adapter / GNN -> gateway -> 5D-SNN
Logic engine -> neuro-symbolic projector -> gateway -> 5D-SNN
5D-SNN -> gateway -> Speech/Language network -> audio output
5D-SNN -> gateway -> GRU / control MLP -> robotics
```

Scientific invariants for this layer:

- pipeline availability/reachability is not evidence of learned use;
- gateway plasticity is disabled by default;
- candidate STDP/homeostatic/structural/efferent-gating math does not mutate the core automatically;
- experiment RNG must be owned and persisted by the experiment runner;
- model/version hashes, controls and gateway parameters must be recorded for experiments;
- historical DATA/EVID remains unchanged when adapters or instrumentation evolve;
- scientific activation requires an explicit preregistered experiment.

Detailed contract: [`NEURAL_SYMBIOSIS.md`](NEURAL_SYMBIOSIS.md).

## 8. Adaptive machine-native body view (`Wesen`)

`Wesen` is a **dashboard projection**, not a new runtime subsystem. It consumes published status, embodiment, connection and selected pipeline state and renders a machine-native body whose visible morphology changes with observed endpoints. Explicit controls do not grant productive learning or actuator authority.

Architecture rules:

- the SNN core is represented as the neural center;
- host/system telemetry is represented as interoception;
- discovered sensor endpoints become input branches;
- discovered actuator endpoints become output branches;
- feedback/loopback remains a distinct return structure;
- Neural Symbiosis is displayed as an observational peripheral-pipeline layer with experiment-only lifecycle controls;
- missing sensors/actuators remain explicit placeholders/unavailable states;
- the visualization does not write `/api/control` or actuator state;
- visual connectivity or reachability is not automatically causal evidence;
- recurrence/loopback is not interpreted as consciousness.

Detailed contract: [`WESEN_ADAPTIVE_BODY.md`](WESEN_ADAPTIVE_BODY.md).

## 9. Persistence and deterministic recovery

Persistence includes `.b5d` snapshots, append/commit delta journal, structural journal, runtime checkpoints, canonical state digests, restore-and-continue verification and structural undo/replay.

Scientific value depends on causal-state completeness and deterministic continuation, not merely successful file loading.

Large experiment run sets may use immutable/compressed raw artifacts plus bounded projections for dashboards or small/local AI review. Any compact projection must preserve provenance to the raw record and must never replace scientific raw DATA.

## 10. Research and evidence architecture

Research state is separated from runtime state. Registries define questions, hypotheses, claims, methods and sources. Experiments produce manifests and `DATA`; evidence promotion occurs through explicit validity checks.

```text
implementation test != experiment result != accepted evidence != interpretation
```

Dashboard animations, self-model views, pipeline reachability and UI logs are interpretation/inspection surfaces unless a protocol explicitly records their source data.

## 11. AI boundaries

Authority is fail-closed:

- observing: may read authorized state;
- interpreting: may produce labeled interpretation;
- proposing: may create bounded proposals;
- causal intervention: requires explicit registered treatment/capability and approval.

Scientific runs reject uncontrolled AI influence where reproducibility cannot be established.

## 12. Dashboard boundary

The dashboard is the operator/research interface, not a second simulation engine. Runtime mutations continue through explicit domain services.

Current primary navigation is:

- Overview
- Control
- Research
- Settings
- Wesen
- Embodiment

`Network` is not a primary user-facing workspace. Release/Gate is accessed from the footer. Unknown measurements remain visibly unknown.

## 13. Architectural invariants

1. **Determinism where claimed** — identical controlled inputs/seeds/configuration must be testable for identical state evolution.
2. **No hidden scientific writes** — UI/LLM/peripheral interpretation cannot mutate evidence or neural state by implication.
3. **Fail closed** — missing permissions, provenance or data do not default to success.
4. **Observed ≠ inferred** — measured state and derived interpretation remain separate.
5. **Availability ≠ authorization** — especially for devices/actuators.
6. **Reachability ≠ learned use** — a reachable Neural Symbiosis pipeline is not evidence that the SNN selected or benefited from it.
7. **DATA ≠ EVID** — output requires validity/evidence promotion before claim support.
8. **Simulation time ≠ wall time** — pacing is separate from model time semantics.
9. **Recovery is part of correctness** — persistence must preserve causal state.
10. **Visualization ≠ causality** — highlighted paths are not causal proof without intervention/outcome evidence.
11. **Recurrence ≠ consciousness** — recurrence/loopback metrics are technical observables only.

## Detailed subsystem documents

- [`B5D_FORMAT.md`](B5D_FORMAT.md)
- [`DETERMINISTIC_RESTORE.md`](DETERMINISTIC_RESTORE.md)
- [`STRUCTURAL_PLASTICITY_ALPHA5.md`](STRUCTURAL_PLASTICITY_ALPHA5.md)
- [`EMBODIMENT_FOUNDATION.md`](EMBODIMENT_FOUNDATION.md)
- [`EMBODIMENT_REAL_BODY.md`](EMBODIMENT_REAL_BODY.md)
- [`NEURAL_SYMBIOSIS.md`](NEURAL_SYMBIOSIS.md)
- [`WESEN_ADAPTIVE_BODY.md`](WESEN_ADAPTIVE_BODY.md)
- [`LEARNING_PREPARATION_STUDIO.md`](LEARNING_PREPARATION_STUDIO.md)
- [`RECURSIVE_CAUSAL_LOOPBACKS.md`](RECURSIVE_CAUSAL_LOOPBACKS.md)
- [`../03-dashboard/DASHBOARD.md`](../03-dashboard/DASHBOARD.md)
- [`../../research/README.md`](../../research/README.md)
