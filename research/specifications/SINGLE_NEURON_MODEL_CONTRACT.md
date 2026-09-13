# Single-neuron model contract

Status: engineering contract for Stage 0. This document is not evidence of biological equivalence and does not promote any scientific claim.

## Purpose

Stage 0 defines the smallest executable unit of MHRN: one deterministic artificial spiking neuron. Higher-level network, plasticity, embodiment and learning claims must not compensate for ambiguity at this level.

The canonical membrane model remains the Izhikevich 2003 model. The dynamics model is nevertheless an explicit experimental treatment and may be replaced by another implemented, versioned model. A model switch must never be silent.

## Canonical model

Model id: `izhikevich-2003`

MHRN implementation version: `mhrn-1.0`

State variables:

- `v`: membrane potential
- `u`: recovery variable

For one configured step `dt_ms`, MHRN applies two half Euler updates to `v` and one Euler update to `u`:

```text
v <- v + 0.5*dt*(0.04*v^2 + 5*v + 140 - u + I)
v <- v + 0.5*dt*(0.04*v^2 + 5*v + 140 - u + I)
u <- u + dt*a*(b*v - u)
```

A spike is emitted when `v >= 30 mV + adaptive_offset` for the default parameterisation. The canonical reset is:

```text
v <- c
u <- u + d
```

Reference: E. M. Izhikevich, *Simple model of spiking neurons*, IEEE Transactions on Neural Networks 14(6), 2003, doi:10.1109/TNN.2003.820440.

## Refractory semantics

The canonical Izhikevich treatment has `refractory_ticks = 0`. Reset and the subsequent recovery dynamics are therefore the native mechanism.

MHRN also supports an explicit absolute refractory extension. When `refractory_ticks > 0`, the cell is held at the model reset potential for that many complete subsequent ticks. This is a separate parameterised treatment, not an implicit change to the canonical model.

## Isolated Stage-0 mode

`NeuronConfig.isolated_reference()` disables mechanisms that belong to later levels of the architecture:

- threshold adaptation
- energy dynamics
- STDP traces
- homeostatic threshold regulation

This produces a reference path consisting only of:

```text
input -> membrane integration -> threshold -> spike -> reset/recovery
```

The normal default configuration retains the historical secondary mechanisms for backward compatibility.

## Alternative model: current-based LIF

Model id: `lif-current-v1`

MHRN implementation version: `mhrn-1.0`

The implemented alternative is a current-based leaky integrate-and-fire model:

```text
dv = ((v_rest - v) + R*I) * dt/tau_m
v  = v + dv
```

A spike is emitted at the configured `lif_threshold`; the membrane potential is then set to `lif_reset`.

The LIF implementation is intentionally simple. Its purpose is not to assert that LIF is a better description of biology, but to make the neuron theory a controlled independent variable for ablation and robustness experiments.

## Model selection and provenance

Every implemented dynamics model has a stable descriptor containing model id, implementation version, equation family, state variables, integration rule, spike rule, reset rule, canonical status, and citation or implementation note.

`Neuron.to_dict()` persists the model id, implementation version, complete neuron configuration and continuation-critical internal state.

Changing the model on a neuron that has already executed through `set_config` is rejected. A live switch must use `switch_model(..., tick=...)`, which records `model_switch_count` and `last_model_switch_tick`.

For scientific experiments, separate matched treatment arms are preferred over switching a live neuron.

## Deterministic current provenance

External and synaptic current remain separately observable. Their sum is the membrane input. If explicit current components are supplied, MHRN rejects a mismatch between `external_current + synaptic_current` and the total `input_current`.

## Deterministic continuation / restore

Schema-v2 neuron serialization persists all state needed for exact continuation, including membrane state, energy, spike counters, threshold adaptation, traces, firing-rate estimate, enabled state, spike-count window, last update tick, refractory state, model identity, switch provenance and complete model configuration.

Legacy neuron dictionaries remain readable.

The contract test executes a prefix, serializes/deserializes the cell, then requires spike decisions and the complete serialized state to remain identical for every future tick.

## Pinned reference trajectory

`research/generated/verification/single_neuron_reference.json` pins the first ten ticks of the isolated canonical cell under constant input current `I=10` and `dt=1 ms`. Tests compare `v`, `u` and the spike decision against that fixture with a tight numerical tolerance.

The fixture is a software reference trajectory, not biological validation.

## Stage-0 decomposition

### 0A - Passive / subthreshold cell
- deterministic integration
- resting/subthreshold response
- explicit time step

### 0B - Spiking cell
- threshold crossing
- single spike event
- reset
- recovery
- optional explicit refractory extension

### 0C - Declared cell labels
- RS
- FS
- IB
- CH
- LTS
- resonator
- sensory
- motor

These labels parameterise the Izhikevich family when type defaults are used. They must not be interpreted as proof of biological cell-type equivalence.

### 0D - Adaptive cell
Threshold adaptation is enabled as a separable mechanism.

### 0E - Metabolic accounting
Energy cost and recovery are enabled as a separable mechanism.

### 0F - Plasticity/homeostasis interface
STDP traces and homeostatic regulation are enabled as interfaces to later learning stages. They are excluded from the isolated Stage-0 reference trajectory.

## Future model families

Candidate future treatments include Adaptive Exponential Integrate-and-Fire (AdEx), Hodgkin-Huxley conductance dynamics, FitzHugh-Nagumo and conductance-based LIF.

Adding a model requires explicit equations and units, state-variable definition, deterministic integration semantics, spike/reset semantics, serialization/provenance support, model-specific reference tests and matched experiments against the canonical baseline.

## Model-comparison research programme

A future preregistered comparison should hold topology, input sequence, seed, time budget and observation window constant while changing only the neuron model treatment. Relevant outputs include spike-train similarity and divergence, firing-rate distribution, stability/runaway activity, computational cost per simulated second, sensitivity to input perturbation, learning outcome under matched plasticity settings and reproducibility across seeds.

No model may become the new canonical default merely because it produces a preferred downstream result. Promotion requires an explicit scientific and engineering decision with preserved historical provenance.
