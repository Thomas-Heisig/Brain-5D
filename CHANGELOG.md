# Changelog

## 0.4.0-alpha.1 - `.b5d` Storage V1 robustness freeze - 2026-08-16

### Added

- frozen `.b5d` Snapshot Format V1 contract;
- exact 128-byte little-endian header invariant;
- exact 128-byte optical, 160-byte restart, and 40-byte synapse records;
- 64 KiB deterministic JSON metadata limit;
- strict format/version/flag validation;
- truncation, overlap, padding and file-size checks;
- full-scan sorted/unique neuron validation;
- synapse sort and referential-integrity validation;
- O(log n) neuron lookup and O(log m + degree) source-scoped synapse lookup;
- public resource-state check and idempotent mmap/file close;
- deterministic byte output when a fixed creation timestamp is supplied;
- opt-in 50k-neuron mmap/storage scalability smoke test;
- strict Pylance/Pyright configuration for `src/storage/b5d.py`;
- project roadmap from storage persistence through the measurable v1.0
  "usable AI" milestone.

### Clean Code

- `src/storage/b5d.py` uses typed Protocol boundaries instead of `Any`;
- recursive JSON metadata aliases replace untyped dictionaries;
- runtime format checks use explicit exceptions rather than optimization-sensitive
  `assert` statements;
- storage verification script runs regression, Black, mypy, Pylint, format
  invariants and the opt-in large smoke test.

### Compatibility

- the V1 snapshot byte layout is frozen;
- arbitrary data-bit checksums and crash commit markers are intentionally deferred
  to v0.4.0-alpha.2 journal files;
- no automatic snapshot I/O is added to `src.main` in alpha.1;
- the existing optical 128-byte codec remains unchanged.

## 0.3.1 - learning proof and repository synchronization

- generic network post-step hook synchronized with LearningEngine
- deterministic end-to-end reward-learning proof
- Python 3.13 development/lint target with Python 3.11 runtime syntax target
- optical manipulator, optical codec and optional self-organization extensions

## 0.3.0 - Sprint 2C

- signed three-factor reward plasticity
- eligibility traces and reward delay
- activity, weight and energy heatmaps

## 0.1.0 - Sprint 1C reference

- sparse 5D spatial index and mixed-radix position conversion
- Izhikevich reference neuron
- delayed ring-buffer spike propagation
- deterministic input/output hyperfaces
- diagnostic stimulus engine and developer observatory
- reproducible run artifacts and Golden Chain regression
