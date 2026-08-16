# Deterministic Restore Contract

## Status

Brain-5D v0.4.0-alpha.6 closes a precision gap discovered by the end-to-end
`restore-and-continue` test.

## Why the extra runtime layer is required

The frozen `.b5d` V1 optical record is optimized for compact observation. It
stores membrane voltage and recovery state with finite scaling and energy as a
normalized 16-bit value. That is sufficient for visualization and approximate
inspection, but it is not a bit-exact representation of Python `float` state.

A deterministic continuation cannot therefore depend on the compact optical
record alone.

## Contract

A deterministic checkpoint consists of three coordinated artifacts:

```text
base.b5d
base.b5d.journal
runtime.json
```

- `.b5d` stores topology, core parameters and compact optical state.
- `.journal` stores committed changes after the base snapshot.
- `runtime.json` stores non-snapshot runtime state and exact neuron dynamics at
  the checkpoint boundary.

The runtime sidecar stores exact values for:

- `v`
- `u`
- `energy`
- `threshold_adaptation`
- `spike_counter`
- `last_spike_tick`
- RNG state
- pending currents
- queued events
- input/output cell sets
- global tick and counters

During restore the recovered snapshot is loaded first. The exact dynamic neuron
state from the runtime checkpoint is then applied as the final precision layer.

## Compatibility

Runtime checkpoint version 2 contains exact neuron states. The reader remains
able to load version 1 sidecars; version 1 simply has no exact-state overlay and
must not be advertised as bit-exact continuation.

## Important terminology

From alpha.6 onward:

- **restart-capable snapshot** means the snapshot contains the core structural
  parameters needed to construct the network.
- **deterministic checkpoint** means snapshot + committed journal + runtime
  checkpoint version 2.

These terms must not be used interchangeably.
