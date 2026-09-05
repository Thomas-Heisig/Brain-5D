# EXP-GEN-0014 — Corrected Scientific Review

## Status

**Post-hoc scientific pre-review; not scientific evidence. Human review remains required.**

This document corrects the interpretation scope of EXP-GEN-0014 without rewriting the original raw data or AI analysis records.

## 1. Primary consistency finding

The registered research question and hypothesis do **not** match the executed protocol:

- Registered RQ: `RQ-TEMP-001` — FAST/MEDIUM/SLOW temporal reference-state comparison.
- Registered hypothesis: `H-TEMP-001-A` — deterministic differences among FAST/MEDIUM/SLOW horizons.
- Executed design: `recurrence_off` versus `recurrence_on` network impulse response.

Therefore EXP-GEN-0014 cannot be used as direct evidence for `RQ-TEMP-001` or `H-TEMP-001-A`. Its valid scope is a **descriptive controlled recurrence/impulse-response test**.

## 2. Experimental design actually executed

- Seeds: 42, 43, 44
- Ticks per run: 100
- Conditions per seed: `recurrence_off`, `recurrence_on`
- Runs: 6
- Initial impulse current: 100.0 according to workflow metadata
- Runtime errors: none reported
- Network mode: OFFLINE
- Research run mode: EXPLORATORY

The recurrence treatment is the manipulated condition. All claims below are restricted to the measured outputs in `DATA/runs.json`.

## 3. Operational quantities

Let condition `c` be either recurrence off (`R0`) or recurrence on (`R1`). For each seed `s`:

- `N_spike(c,s)` = total number of observed spikes.
- `t_first(c,s)` = tick of first observed response.
- `t_last(c,s)` = tick of last observed response.
- `D(c,s)` = reported `propagation_depth`.
- `A(c,s)` = reported number of activated neurons.
- `r_peak(c,s)` = reported peak spike rate.

A descriptive spike-count ratio is

\[
RR_{spike} = \frac{N_{spike}(R1)}{N_{spike}(R0)}.
\]

A descriptive persistence extension is

\[
\Delta t_{last} = t_{last}(R1)-t_{last}(R0).
\]

A descriptive propagation-depth difference is

\[
\Delta D = D(R1)-D(R0).
\]

These are deterministic descriptive contrasts, **not inferential effect sizes**.

## 4. Exact observed results

Across seeds 42, 43 and 44, the stored spike sequences are identical within each condition.

### Recurrence off

- Spike sequence: `(neuron 2, tick 2)`
- `N_spike = 1`
- `t_first = 2`
- `t_last = 2`
- `propagation_depth = 1`
- `activated_neurons = 1`
- `peak_spike_rate = 1.0`
- `recurrent_events = 0`
- `return_latency = null`
- spike-sequence digest: `5602477722d9dde1146cf5dd6bab781f4f4293f70852dc155e6a33333017bdbb`

### Recurrence on

- Spike sequence ticks: `2, 4, 8, 12, 16, 20, 24, 30`
- all observed spikes are from neuron 2
- `N_spike = 8`
- `t_first = 2`
- `t_last = 30`
- `propagation_depth = 29`
- `activated_neurons = 1`
- `peak_spike_rate = 1.0`
- `recurrent_events = 0`
- `return_latency = null`
- spike-sequence digest: `7b8bd6dcf18da41f08211e41cdf5d325ffc757105665ba7ab2a5e2d1fb474808`

### Descriptive contrasts

For every stored seed:

\[
RR_{spike}=\frac{8}{1}=8.
\]

Thus recurrence-on produced eight times as many observed spikes as recurrence-off in this implementation and parameterization.

\[
\Delta t_{last}=30-2=28\;\text{ticks}.
\]

The final observed spike therefore occurred 28 ticks later with recurrence enabled.

\[
\Delta D=29-1=28.
\]

The reported propagation-depth metric increased by 28 units.

The first-response latency did not change:

\[
\Delta t_{first}=2-2=0.
\]

The number of activated neurons also did not change:

\[
\Delta A=1-1=0.
\]

The measured difference is therefore not broader recruitment of neurons; it is repeated activity of the same observed neuron over a longer interval.

## 5. Spike timing / inter-spike intervals

For recurrence-on, spike ticks are

\[
T=(2,4,8,12,16,20,24,30).
\]

The inter-spike intervals are

\[
ISI=(2,4,4,4,4,4,6).
\]

Mean ISI:

\[
\overline{ISI}=\frac{2+4+4+4+4+4+6}{7}=4.0\;\text{ticks}.
\]

Median ISI is 4 ticks. The sequence contains a long central run of 4-tick intervals, but the first and final intervals differ. This supports describing a regular repeated response pattern; it does **not** by itself establish an oscillator, attractor, biological rhythm, or memory mechanism.

## 6. Reproducibility

The condition-specific spike-sequence digests are identical across seeds 42, 43 and 44. This demonstrates reproducibility of the stored deterministic response pattern under these three seed settings.

However, identical outputs across seeds must not automatically be treated as `n=3` statistically independent biological or stochastic replications. If the tested pathway is deterministic or seed-insensitive, these runs are repeated executions rather than independent samples. Inferential statistics require a justified sampling model and non-pseudoreplicated experimental units.

## 7. State digests

`network_state_digest_before` and `network_state_digest_after` differ between conditions and seeds. A cryptographic digest only establishes that serialized state representations differ; it does not provide a metric distance or a biological/functional magnitude of state change.

Therefore statements such as "further away", "more complex state" or "deeper processing" are not justified from hashes alone.

## 8. Metric inconsistency requiring correction

`recurrent_events` is reported as `0` in all stored runs, including recurrence-on. This is semantically surprising because repeated spike activity is visible under the recurrence treatment.

Possible explanations include:

1. `recurrent_events` has a narrower operational definition than repeated spikes;
2. instrumentation is incomplete;
3. the metric is not connected to the event path used by this experiment;
4. recurrence is represented indirectly and therefore not counted by that field.

Until its implementation and mathematical definition are documented, this metric must not be used to support or reject recurrence claims.

Likewise `propagation_depth` needs an explicit implementation definition before it is interpreted as network depth, causal-chain length, path length, processing complexity, or a biological quantity.

## 9. What the experiment supports

A defensible statement is:

> Under the tested configuration, enabling the recurrence treatment changes the deterministic impulse response from one observed spike at tick 2 to eight observed spikes extending through tick 30, while the observed active-neuron count remains one. The condition-specific spike sequence is reproduced for seeds 42, 43 and 44.

This is a valid engineering/experimental observation.

## 10. What the experiment does not support

EXP-GEN-0014 does not currently establish:

- the registered FAST/MEDIUM/SLOW temporal-state hypothesis;
- statistical significance or population-level robustness;
- memory formation;
- learning;
- biological recurrence equivalence;
- increased network complexity;
- deeper cognitive processing;
- an attractor or oscillator;
- causal generalization beyond the manipulated implementation and tested parameters.

The controlled on/off manipulation supports a local implementation-level attribution of the observed response difference to the treatment **if all other execution parameters truly remained identical**, but broader causal language should remain qualified until instrumentation and protocol consistency are verified.

## 11. Required follow-up experiments

1. **Correct RQ/protocol registration:** run recurrence experiments under a recurrence-specific RQ/hypothesis, and run `RQ-TEMP-001` with the temporal-state runner producing FAST/MEDIUM/SLOW metrics.
2. **Recurrence-strength sweep:** vary recurrent weight over a preregistered grid and measure spike count, duration, ISI and termination.
3. **Impulse-amplitude sweep:** verify whether the observed eight-spike sequence depends on the 100.0 input amplitude.
4. **Longer observation window:** determine whether activity terminates, repeats, or changes beyond tick 30.
5. **Metric validation:** define and unit-test `recurrent_events` and `propagation_depth` against hand-constructed networks.
6. **Independent stochastic replication:** if statistical inference is intended, introduce or identify meaningful stochastic variation and define the independent experimental unit before computing p-values or confidence intervals.
7. **Ablation/control:** replace recurrent connection with matched feed-forward or delayed control to distinguish recurrence from generic extra excitation/delay.
8. **Topology scaling:** repeat on multi-neuron recurrent motifs to test whether the effect generalizes beyond repeated activity of one neuron.

## 12. Scientific disposition

- Technical run: **valid according to manifest**
- Semantic match to registered RQ/H: **failed**
- Descriptive recurrence result: **usable as exploratory engineering observation**
- Statistical evidence: **not established**
- Evidence registry promotion: **not recommended before corrected registration and human review**
- Human review: **PENDING**
