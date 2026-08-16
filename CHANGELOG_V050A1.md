# v0.5.0-alpha.1

## Added

- `src/homeostasis/` firing-rate and energy regulator.
- Bounded adaptive spike threshold in the neuron model.
- Homeostasis metrics in the operator dashboard.
- Homeostasis tests and release quality-gate documentation.

## Fixed

- Dashboard JSON list typing keeps the recursive `JSONValue` contract strict.
- Runtime checkpoint writer/reader aligned with deterministic restore V3.

## Compatibility

- `.b5d` V1 remains frozen and unchanged.
- Homeostasis is disabled by default, preserving v0.4 behavior.
