# MSBA — Modalitaets-spezifische Synaptische Bahn-Architektur

## Status

MSBA is an **experimental embodiment contract** below Neural Symbiosis. It is implemented in `src/embodiment/msba.py` and visualized read-only in `Wesen`.

MSBA does **not** change the canonical MHRN SNN core, its neuron model, canonical STDP, structural-plasticity engine or historical DATA/EVID. All MSBA learning/growth/allocation flags are disabled by default and require a separate preregistered experiment before activation.

## Scientific correction to the biological analogy

The architecture uses modality-specific engineering constraints without claiming a one-to-one cortical mapping. Audio is strongly temporal but not exclusively phase-coded. Vision is massively parallel but still temporal and hierarchical. The prefrontal cortex is not a biological digital bus. Therefore MSBA treats the three pathways as engineering abstractions whose value must be experimentally established.

The persisted productive MHRN core remains **five-dimensional**. MSBA does not assign fixed semantics such as time, x, y or frequency to those axes. Modality adapters instead define explicit feature tuples and a projection mapping. The external/MSBA projection space now supports **1 through 32 dimensions** via `MSBAGatewayConfig.projection_dimensions`; increasing this value does not mutate the productive 5D neuron-ID/storage format.

This distinction is scientific and technical: an increased-dimensional MSBA projection is **not** evidence that the productive SNN core is N-D. A future versioned neuron-ID/`.b5d` migration is required before the core itself can persist more than five coordinates. Experiments must keep projection dimensionality, productive core dimensionality and mapping provenance separate.

Projection experiments must compare structured, shuffled, random, reduced-dimensional and, where preregistered, increased-dimensional mappings.

## Pathways

### Audio — temporal coherence pathway

Feature coordinates:

`band × phase-or-envelope × channel × lag × feature × optional additional projection features`

Candidate processing:

1. filter-bank decomposition (default contract: 32 bands);
2. phase/envelope-aware event representation;
3. fixed bounded delay taps;
4. explicit mapping into the declared MSBA projection space;
5. candidate phase-weighted temporal STDP.

The phase term is non-negative:

`C_phase = (1 + cos(delta_phi)) / 2`

so it scales an existing STDP candidate without reversing its causal sign.

Candidate MSBA learning is inert unless an experiment enables it.

### Vision — spatial multiplex pathway

Feature coordinates:

`x × y × feature × scale × frame × optional additional projection features`

The default contract is 100 × 100 input resolution with a **fixed sparse target degree** rather than a fixed percentage. With `k=8`, 10,000 inputs imply 80,000 candidate gateway edges rather than a 2.5-million-edge 5% graph.

Candidate structural growth uses information value, projected locality and resource availability:

`p_grow = eta × information_value × exp(-d_projection^2/(2 sigma^2)) × (1 - resource_pressure)`

The current helper retains the historical parameter name `distance_5d` for API compatibility; increased-dimensional projection experiments must compute and record the distance metric used rather than silently treating it as core 5D distance.

High firing rate alone is not accepted as a growth signal because noise could otherwise create self-reinforcing connectivity.

Throttles are ordered: freeze/reduce plasticity first, then FPS, resolution, ROI/foveation and feature channels; learned structure is not deleted merely to save energy.

### Digital — quantized high-fidelity pathway

Exact digital information remains **outside the SNN** in a `SymbolFrame` containing payload, codec, sequence, provenance and SHA-256 checksum.

The SNN receives only a deterministic population representation. Learning may later alter routing, gain, admission or association, but never the original payload, bit values or checksum.

This distinction is mandatory: SNN dynamics may be noisy or approximate while digital payload integrity remains exact.

## Energy/resource accounting

MSBA separates:

- `normalized_energy_units` — model-internal cost;
- `estimated_joules` — optional calibrated estimate;
- `measured_joules` — physical observation when hardware telemetry exists.

An estimate must never be presented as a measurement.

The cost model includes sensor/adapter work, spikes, synaptic events, plasticity updates, structural events, memory and I/O. Coefficients are normalized model parameters until empirical calibration exists.

## Resource pressure and homoeostasis

Soft resource pressure combines bounded energy, thermal, compute and memory pressure. Fan failure is a hard override and directly yields `SURVIVAL`.

States:

1. `NORMAL`
2. `CONSERVE`
3. `CRITICAL`
4. `SURVIVAL`

The protection policy is deterministic and separate from learned allocation. A learning policy may optimize soft quotas, but it cannot override thermal/fan/persistence safety.

The internal candidate energy price is:

`lambda(t) = base_price + resource_pressure(t)`

A candidate modality quota is:

`g_m = sigmoid(beta × (utility_m - lambda × cost_m - threshold_m))`

This computes a candidate value only. It does not activate a gateway.

## Safety ordering

`CONSERVE`:

- reduce learning/plasticity first;
- reduce redundant visual/audio fidelity;
- reduce digital admission rate.

`CRITICAL`:

- freeze plasticity;
- use ROI/low-resolution vision;
- reduce audio bands;
- admit priority symbols only.

`SURVIVAL`:

- preserve thermal sensing;
- preserve fan monitoring;
- preserve core persistence and storage integrity;
- preserve emergency actuator paths;
- disable non-essential expensive paths unless safety-critical.

## Research registry and experiment reachability

The canonical Experiment Workflow loads `research/registry/questions.yaml` plus `questions.*.yaml` fragments and the corresponding hypothesis files. MSBA therefore registers its first-class entries in:

- `research/registry/questions.msba.yaml`;
- `research/registry/hypotheses.msba.yaml`.

`research/registry/msba_experiments.yaml` remains the detailed programme/falsification source. The dashboard Research Catalog makes all canonical RQs searchable. Questions without a dedicated frozen/preregistered protocol remain **EXPLORATORY** and may only use the generic runtime experiment path; that reachability is not confirmatory evidence.

## Research programme

### RQ-MSBA-E01 — information/task value per energy

Do audio, visual and digital MSBA gateways differ in energy cost per useful decision/information unit?

Primary metrics: energy units/correct decision, measured or estimated J/correct decision, synaptic events/correct decision.

### RQ-MSBA-E02 — adaptive allocation

Does cost-adaptive allocation outperform fixed, random and exhaustion-until-stop allocation under the same total resource budget?

### RQ-MSBA-E03 — adaptive visual foveation

Can useful ROI concentration emerge without hard-coding the relevant image region?

Controls: adaptive ROI, fixed-centre ROI, random ROI and full-image processing.

### RQ-MSBA-E04 — digital integrity under throttling

Does digital payload integrity remain exact while only throughput/admission changes under resource pressure?

Required criterion: zero payload/checksum mutation attributable to SNN dynamics.

### RQ-MSBA-E05 — compensatory modality allocation

After loss or degradation of one modality, does the system increase another modality when its expected utility justifies the extra cost?

## Intermodal experiment rule

Do not preregister "supra-linear summation" as the required success result. Compare congruent, incongruent, temporally shifted and randomized combinations and measure task performance, latency, decoder information, spike/synaptic cost and cross-modal prediction error. Linear, super-additive or sub-additive responses are all admissible empirical outcomes.

## Mandatory controls and provenance

Any activated MSBA experiment must record:

- fresh experiment ID;
- code commit and environment;
- seeds/RNG state;
- gateway configuration;
- modality adapter/model/version hashes;
- projection dimension count;
- productive core dimension count;
- projection mapping and its control condition;
- raw DATA and compact AI projection separately;
- frozen-gateway control;
- random/shuffled mapping controls where applicable;
- reduced/increased-dimensional mapping controls where applicable;
- information-destroyed or timing-shuffled controls where applicable;
- measured vs estimated energy provenance;
- exact digital checksums for digital-path experiments;
- EVID review separate from exploratory summaries.

No historical experiment artifact may be rewritten to make MSBA appear previously active or to relabel a 5D core experiment as N-D evidence.
