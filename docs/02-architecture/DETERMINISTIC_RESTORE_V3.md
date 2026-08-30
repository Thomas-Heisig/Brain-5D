# Deterministic Restore – Runtime Checkpoint V3

## Problem

The frozen `.b5d` V1 format intentionally stores several restart fields as
32-bit floats.  This is sufficient for compact restart snapshots, but it cannot
reproduce Python double-precision dynamics bit-for-bit.  In particular,
Izhikevich parameters such as `a=0.02` and learned synapse weights can be rounded
when they pass through the binary snapshot.

## Alpha.7 solution

The `.b5d` V1 wire format remains unchanged.  Runtime checkpoint V3 overlays the
exact Python values required for deterministic continuation:

### Neurons

- `a`, `b`, `c`, `d`;
- `v`, `u`, `energy`;
- `spike_cost`;
- `threshold_adaptation`;
- `spike_counter` and `last_spike_tick`.

### Synapses

- source and target IDs;
- exact `weight`;
- exact `eligibility`;
- delay;
- `last_pre_spike`.

### Runtime

- RNG state;
- pending currents;
- future spike events;
- current tick and counters;
- input/output cell sets.

Restore order is:

1. recover snapshot + committed journal;
2. reconstruct topology from `.b5d`;
3. restore queues/counters/RNG;
4. overlay exact neuron state;
5. overlay exact synapse state;
6. continue the simulation.

Checkpoint V1/V2 remain readable.  They cannot promise bit-exact continuation
when their missing exact fields were quantized in `.b5d`.
