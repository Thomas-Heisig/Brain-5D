# Neural Symbiosis — Embodied Multi-Network Interface

## Status

**Architecture contract / experimental preparation. Not empirical evidence.**

`Neural Symbiosis` is the international-facing name for the multi-network
embodiment layer shown inside the `Wesen` workspace. It extends the technical
embodiment boundary; it does **not** redefine the canonical MHRN neural
core, canonical learning rules, historical DATA, accepted EVID, or scientific
gates.

The key separation is:

```text
physical / digital / virtual source
        ↓
optional dedicated neural area(s)
        ↓
explicit embodiment gateway
        ↓
MHRN 5D-SNN core
        ↓
explicit embodiment gateway
        ↓
optional dedicated neural area(s)
        ↓
physical / digital / virtual sink
```

Camera, microphone and audio output therefore do not need to connect directly
to the 5D-SNN. Dedicated neural stages can be inserted between the endpoint and
the core. The same contract applies to virtual sources and sinks such as logic
engines, databases, knowledge graphs, associative memories, web/API streams,
document pipelines or future external systems.

## 1. Scientific boundary

The implementation is intentionally located under `src/embodiment/` and its
Wesen visualization remains read-only.

The following rules are normative:

1. No peripheral network receives implicit write access to canonical core
   state.
2. Merely detecting an endpoint, registering an area, or marking a pipeline as
   reachable is **not** a scientific finding.
3. Gateway plasticity is disabled by default.
4. Enabling synaptic, structural or reward-modulated gateway learning requires
   an explicit experiment configuration and preregistration.
5. Gateway RNG must be owned by the experiment runner and persisted with the
   run state. The gateway module itself does not draw random numbers.
6. Existing historical experiment DATA and accepted EVID are never rewritten
   to reflect new instrumentation or new models.
7. Scientific claims must continue to be derived from preregistered experiments
   and their DATA/EVID artifacts, not from dashboard state.

This preserves the distinction between **engineering capability** and
**scientific evidence**.

## 2. Open-set network architecture

The system does not maintain a closed enum of permitted neural-network types.
Instead, a peripheral implementation satisfies the framework-neutral
`NetworkAreaAdapter` protocol and is described by an `AreaDescriptor`.

Common built-in catalog families include:

- CNN;
- Vision Transformer;
- generic Transformer;
- LSTM;
- GRU;
- RNN;
- GNN;
- Modern Hopfield Network;
- Echo State / reservoir networks;
- MLP;
- VAE;
- GAN;
- diffusion networks;
- autoencoders;
- peripheral SNNs;
- multimodal Transformers;
- neuro-symbolic projectors;
- custom/open-set neural areas.

The adapter boundary is deliberately backend-neutral. A future adapter may be
implemented with PyTorch, TensorFlow, JAX, ONNX Runtime, a remote inference
service or a custom runtime without importing those frameworks into the
MHRN core package.

## 3. Virtual cognitive areas

Not every peripheral area must itself be a neural network. `AreaKind.VIRTUAL`
allows explicit virtual systems to participate in a pipeline, for example:

- symbolic logic engines;
- databases;
- knowledge graphs;
- retrieval systems;
- external memory stores;
- planning services;
- simulation environments.

If a virtual system produces a representation that is not directly suitable
for the SNN boundary, a neural projector can be inserted before the gateway.
This keeps symbolic/record semantics outside the 5D-SNN while still allowing a
controlled projection into spike-compatible or current-compatible inputs.

## 4. Dedicated endpoint pipelines

Initial disabled templates include:

### Afferent

```text
Camera
  → CNN / Vision Transformer
  → afferent gateway
  → 5D-SNN
```

```text
Microphone
  → Audio CNN / Audio Transformer
  → afferent gateway
  → 5D-SNN
```

```text
Microphone
  → Speech Transformer
  → Language Transformer
  → afferent gateway
  → 5D-SNN
```

```text
Web/API
  → Language Transformer
  → afferent gateway
  → 5D-SNN
```

```text
Database
  → Knowledge adapter
  → GNN / representation projector
  → afferent gateway
  → 5D-SNN
```

### Cognitive

```text
Logic engine
  → neuro-symbolic projector
  → cognitive gateway
  → 5D-SNN
```

```text
Associative memory
  ↔ cognitive gateway
  ↔ 5D-SNN
```

### Efferent

```text
5D-SNN
  → efferent gateway
  → Language / Speech Transformer
  → Audio output
```

```text
5D-SNN
  → efferent gateway
  → multimodal decoder
  → Display
```

```text
5D-SNN
  → efferent gateway
  → language/document projector
  → Printer
```

```text
5D-SNN
  → efferent gateway
  → GRU / control MLP
  → Robotics adapter
```

All templates are published as `enabled: false` and `instantiated: false` until
an explicit runtime/experiment path exists.

## 5. Plastic gateway candidate model

The current module contains pure mathematical helpers for future experiments.
They calculate candidate updates only; they do not apply updates to the core.

For a peripheral pre-event and SNN post-event, a bounded pair-based STDP
candidate is:

\[
\Delta w_{ij}=
\begin{cases}
\eta_+ (w_{max}-w_{ij})e^{-\Delta t/\tau_+}, & \Delta t>0\\
-\eta_- (w_{ij}-w_{min})e^{\Delta t/\tau_-}, & \Delta t\le 0
\end{cases}
\]

with \(\Delta t=t_{post}-t_{pre}\).

A bounded homeostatic scaling candidate is:

\[
w' = \operatorname{clip}\left(
 w \left(\frac{\rho_{target}}{\max(\bar\rho,\epsilon)}\right)^\alpha,
 w_{min},w_{max}
\right)
\]

The scalar efferent gate is represented as:

\[
g_a(t)=\sigma(d_a(t)-\theta_a)
\]

and a third-factor candidate update as:

\[
\Delta v=\eta_{gate}\,R(t)\,\Delta v_{STDP}
\]

### Important correction to the initial research sketch

A global reward defined only as

\[
\frac{1}{N}\sum_i(\rho_{target}-\bar\rho_i)
\]

can cancel opposing deviations: an overactive population and an underactive
population can sum to approximately zero while the system is far from
homeostasis. Therefore this quantity must **not** be treated as an already
validated reward definition.

Future experiments should preregister and compare alternatives, for example:

- signed population error when direction is the intended signal;
- mean absolute deviation;
- squared deviation / homeostatic cost;
- local population-specific modulators;
- task reward separated from homeostatic regulation;
- multi-objective combinations with explicit coefficients.

This distinction prevents an engineering convenience from silently becoming a
scientific assumption.

## 6. Structural plasticity candidate model

The module exposes deterministic probability calculations only. Formation may
be parameterized from co-activity:

\[
p_{form}=\operatorname{clip}\left(
 \eta_{struct}\frac{\bar\rho_{pre}\bar\rho_{post}}{\rho_{max}^2},0,1
\right)
\]

and weak-weight pruning as:

\[
p_{prune}=\operatorname{clip}\left(
 \eta_{prune}(1-\tilde w),0,1
\right)
\]

where \(\tilde w\) is the normalized gateway weight.

The Bernoulli draw is intentionally excluded from the gateway helper. A
preregistered experiment must perform that draw through the deterministic
experiment RNG so state restoration and replay remain auditable.

## 7. Falsifiable research program

The architecture enables, but does not yet establish, hypotheses such as:

- **H-GW-01**: task-relevant peripheral areas acquire higher effective gateway
  influence than matched irrelevant controls.
- **H-GW-02**: the system suppresses a deliberately noisy peripheral area more
  strongly than an information-matched control area.
- **H-GW-03**: structural gateway density changes with experimentally
  manipulated predictive information, after controlling for raw activity.
- **H-GW-04**: homeostatic regulation reduces a preregistered firing-rate error
  metric relative to a no-regulation ablation.
- **H-GW-05**: a planning/imagination area is activated before defined complex
  decisions more often than in temporal-shuffle and random-gate controls.
- **H-GW-06**: after a preregistered sensor lesion, alternative gateways change
  in a direction that improves retained performance relative to frozen-gateway
  and random-rewiring controls.

Required controls include random gateways, frozen gateways, shuffled timing,
matched activity without information, and lesion/ablation comparisons. A
correlation between gateway weight and task performance alone is insufficient
for a causal tool-use claim.

## 8. Experiment identity

Historical experiment identifiers must not be reused. Earlier `EXP-GEN-0013`
and `EXP-GEN-0014` already exist in the repository history and therefore cannot
be reassigned to Neural Symbiosis studies.

New experiments must obtain fresh identifiers from the current experiment
registry/runner and declare at minimum:

- exact peripheral area adapter and model version;
- model artifact/hash where applicable;
- endpoint identity and modality;
- encoding/decoding contract;
- gateway parameters and enabled mechanisms;
- RNG seed/state;
- control condition;
- learning and evaluation windows;
- primary/secondary outcomes;
- stopping criteria;
- DATA/EVID provenance.

## 9. Frontend representation

`Wesen` contains a `Neural Symbiosis` panel. It shows:

- the open-set family catalog;
- real/virtual pipeline templates;
- endpoint reachability derived from `/api/embodiment/connections`;
- explicit `disabled` state for all pipelines;
- explicit `INERT` state for gateway learning;
- the scientific boundary.

The panel performs GET-only observation. It contains no POST/PUT/DELETE path,
no `/api/control` call and no mechanism to activate an actuator or learning
rule.

## 10. Implementation files

- `src/embodiment/neural_symbiosis.py` — typed open-set adapter, area, pipeline
  and gateway-math contracts;
- `src/dashboard/static/wesen-neural-symbiosis.js` — read-only Wesen panel;
- `src/dashboard/static/wesen-neural-symbiosis.css` — responsive presentation;
- `tests/test_neural_symbiosis.py` — fail-closed, open-set, math and frontend
  boundary tests.

## 11. Next implementation stage

The next stage should not directly connect production peripherals to plastic
gateways. It should first add an **experiment-only runner adapter** that:

1. constructs one declared peripheral area;
2. records exact model/version hashes;
3. uses a deterministic gateway state with explicit persistence;
4. writes new DATA rather than changing canonical historical records;
5. exposes gateway metrics separately from core synapse metrics;
6. supports frozen/random/shuffled controls;
7. produces EVID only after the existing scientific review path accepts the
   corresponding run.

Only after those controls are validated should runtime activation outside
experiments be considered.
