# v0.4.0-alpha.3 – Runtime Storage & Lazy Snapshot Views

- completed alpha.2 append-only journal protocol with immutable header;
- added typed delta codecs and real snapshot replay;
- added CRC32 and committed-corruption detection;
- added uncommitted-tail truncation and atomic recovered snapshot publication;
- added `StorageSession` post-step persistence hook;
- added mmap-backed lazy activity/weight/energy snapshot projector;
- added strict no-`Any` storage boundaries and Pyright coverage;
- `.b5d` Snapshot V1 remains byte-for-byte frozen.

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

### v0.4.0-alpha.3 verification follow-up

- Cross-platform Python release verification runner.
- Windows CMD launcher avoids PowerShell execution-policy/signature failures.
- Generated package metadata and caches excluded from source-control hygiene.
- `.b5d` and journal wire formats remain unchanged.

## v0.4.0-alpha.4 – Persistence Finalization

### Added
- bounded asynchronous storage queue with explicit backpressure/drop policy
- storage telemetry for queue depth, deltas, bytes and write/commit latency
- runtime checkpoint sidecar for RNG/event queue/pending currents
- generation manifest for crash-safe compaction promotion
- real NeuralNetwork restore foundation
- alpha.4 preparation/verification scripts

### Fixed
- mypy variable-inference collisions in runtime/recovery storage code
- Windows recovery fsync uses a writable file descriptor
- narrow legacy typing fixes for manipulator, self-organization and learning lab
