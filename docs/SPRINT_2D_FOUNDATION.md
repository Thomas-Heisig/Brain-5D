# Sprint 2D Foundation - End-to-End Learning Proof

## Purpose

Before adding homeostasis or intrinsic motivation, Brain-5D must prove that its
existing plasticity mechanisms change system behaviour rather than merely passing
isolated mathematical tests.

This bridge release therefore adds a deterministic learning experiment without
changing the neuron model or introducing new plasticity rules.

## Causal chain under test

1. A convergent population of presynaptic neurons is externally driven to spike.
2. A target neuron is externally driven after a fixed positive timing interval.
3. The LearningEngine records positive eligibility for the convergent synapses.
4. A positive scalar reward is applied.
5. Three-factor plasticity changes the weights using `delta_w = eta * R * e`.
6. Training state is discarded.
7. A fresh baseline network and a fresh trained-weight network receive the same
   presynaptic probe.
8. The baseline remains subthreshold while the trained network produces a target
   spike.

The fresh evaluation networks are important: they prevent residual membrane
potential, adaptation state, queued events or eligibility state from being mistaken
for learning.

## Default experiment

Configuration: `configs/learning_experiment.yaml`

Key values:

- 48 convergent presynaptic neurons
- initial synaptic weight 0.05
- PRE/POST interval 5 ticks
- 20 independent training trials
- positive reward 1.0 per trial
- reward learning rate 0.5
- STDP weight updates disabled
- eligibility enabled
- reward-modulated updates enabled

The experiment intentionally resets timing and eligibility state after each reward,
while preserving learned weights. This makes each trial an independent temporal
credit-assignment episode.

## Acceptance condition

Run:

```powershell
python -m src.experiments.learning_lab --config configs/learning_experiment.yaml
```

The command exits with status 0 only if all of the following hold:

- final mean weight is greater than initial mean weight;
- the baseline evaluation network does not spike at the target;
- the trained-weight evaluation network does spike at the target.

## Repository synchronization

The public v0.3.0 tree had a mismatch: `LearningEngine.attach()` referenced the
network post-step hook while the published `src/core/network.py` did not contain the
hook implementation. v0.3.1 restores the generic hook and adds explicit regression
tests so this integration point cannot silently disappear again.

The README and Python 3.13 mypy/Pylint development targets are synchronized at the
same time.

## What is deliberately not included

This update does not add:

- homeostatic firing-rate control;
- intrinsic rewards;
- free-energy or prediction-error machinery;
- neurogenesis or pruning;
- new ion-channel dynamics.

Those mechanisms belong to the next full Sprint 2D step after the learning proof is
accepted on the real repository.
