# 2026-09-05 — Network observability, CI repair and documentation synchronization

## Scope

This record documents the final repair pass on the current `main` line after the Wesen/frontend integration and the review of generated experiments `EXP-GEN-0009` through `EXP-GEN-0012`.

## Repository state

At the verification point:

- `main` was the canonical branch;
- there were no open pull requests;
- `tmp-do-not-use` was zero commits ahead of `main` and approximately 95 commits behind, so it contained nothing to merge;
- the latest completed full GitHub Continuous Integration run on the repaired baseline concluded `success`.

The obsolete branch is intentionally not merged. It should be deleted when branch-delete permissions/tooling are available.

## CI and regression repair

The repair cycle resolved all verified current-tree failures rather than disabling checks.

Resolved classes included:

- Black formatting drift;
- a Mypy narrowing issue in dashboard experiment-ID handling;
- Pyright JSON-boundary typing errors;
- a stale Wesen frontend regression assertion after causality UI ownership moved;
- a stale heatmap expectation that ignored configured synaptic-weight clipping;
- pre-commit behavior that would otherwise rewrite Markdown hard line breaks and frozen experiment manifests;
- optional spike-ID narrowing in the network probe.

Verified repair-suite result:

- 735 tests collected;
- 733 passed;
- 2 skipped;
- 0 failed.

The subsequent full GitHub CI run succeeded with Python 3.11/3.12/3.13, Scientific Integrity, typing, documentation, security, lint/format and test jobs green.

## Network impulse observability finding

Historical generated experiments `EXP-GEN-0009`, `EXP-GEN-0010`, `EXP-GEN-0011` and `EXP-GEN-0012` showed:

- no runtime exception;
- changing before/after state digest;
- zero `activated_neurons`;
- zero `total_spikes`;
- no measured recurrence.

Inspection showed that the older `NetworkImpulseProbe` derived activity primarily from `output_spike_ids`. This meant source and relay activity could occur without appearing in the stored response signature.

The historical experiment artifacts were **not modified**. Their observation remains part of the project record.

## Probe repair

`NetworkResponseSignature` now records and serializes additional observables:

- `ticks_executed`;
- `delivered_synaptic_events`;
- `synaptic_activity_ticks`;
- `max_synaptic_current_targets`;
- `total_synapses`.

The probe now observes the complete published `spike_ids` stream, with fallback to the older `output_spike_ids` contract when necessary. Activated-neuron and spike-sequence metrics therefore reflect the whole published network response rather than only the output projection.

## Recurrence topology repair

The impulse experiment recurrence condition now contains a real return edge from the output neuron back to the source neuron. This aligns the topology with the recurrence metric, which expects a return to the source.

## Direct runtime validation

A dedicated `scripts/verify_network_activity.py` diagnostic runs the actual `NeuralNetwork` path and fails if activity is absent.

For the validation configuration with seed 42 and 12 ticks, the observed response included:

### Recurrence off

- 12 ticks executed;
- 3 activated neurons;
- 3 total spikes;
- 2 delivered synaptic events;
- 2 synaptic-activity ticks;
- 2 total synapses;
- first/last output response at tick 4.

### Recurrence on

- 12 ticks executed;
- 3 activated neurons;
- 9 total spikes;
- 8 delivered synaptic events;
- 8 synaptic-activity ticks;
- 3 total synapses;
- first response at tick 4;
- last response at tick 10;
- recurrent return events observed;
- return latency observed at 6 ticks.

These values are a technical validation of observability and execution. They are not by themselves a scientific recurrence claim.

## Persistence

New Science Runner experiments serialize the complete response signature into:

`research/experiments/<EXP-ID>/DATA/runs.json`

The surrounding experiment workflow also persists configuration/provenance, workflow, manifest and report artifacts. Therefore future registered experiments can evaluate tick execution, spike propagation and synaptic activity from experiment-local DATA.

## Scientific consequence

The correct next step is a **new registered multi-seed experiment** using the repaired probe and recurrence topology. Historical runs must not be rewritten to produce the result that improved instrumentation would have measured.

Any EVID promotion still requires protocol validation, reproducibility as applicable, provenance checks and human review.
