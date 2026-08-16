# v0.4.0-alpha.3 – Runtime Storage & Lazy Observatory Foundation

## Scope implemented in this update

### `StorageSession`

A generic post-step hook captures state changes while storage is explicitly
enabled. It keeps typed fingerprints and emits deltas only when a neuron,
synapse or topology element changed.

The alpha.3 correctness baseline performs an O(N+E) change scan per captured
tick. This is intentionally transparent and **not** presented as the final
large-scale solution. v0.6 will replace this with chunk/dirty tracking.

### Lazy `.b5d` projector

`B5DLazyProjector` builds Activity, Weight and Energy X-Y projections directly
from the memory-mapped snapshot. It stores only the 2D aggregation arrays plus,
for the weight projection, a compact target-coordinate lookup. The live
`NeuralNetwork` is not required.

### Safety defaults

All runtime storage and lazy observatory settings remain disabled by default.
The established core benchmark therefore does not silently include storage I/O.

## Remaining before v0.4.0 final

- bounded asynchronous write queue and back-pressure metrics;
- compaction/rotation policy for long journals;
- explicit `StorageBackend` public interface;
- integration CLI in `src.main` after benchmark impact is measured;
- restore-and-continue test against the real `NeuralNetwork`, not only the
  storage reconstruction model.
