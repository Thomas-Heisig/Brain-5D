# Changelog

## v0.4.0-alpha.7 – Embodiment Foundation & Deterministic Restore V3

### Fixed

- exact restore now preserves neuron model parameters that `.b5d` V1 stores as
  float32 restart fields;
- exact synapse weights and eligibility values are restored from Runtime
  Checkpoint V3;
- checkpoint JSON parsing is strict-mypy safe without `Any` or `type: ignore`.

### Added

- typed sensor, actuator, environment, registry, and embodiment-agent contracts;
- read-only embodiment metrics in the operator dashboard;
- safe Markdown documentation browser;
- safe sibling `.b5d` snapshot selector;
- PID-tracked cross-platform launcher and consolidated quality runner;
- roadmap integration of embodiment, continual learning, causal evaluation, and
  neuro-symbolic research directions.

### Compatibility

- `.b5d` Snapshot V1 is unchanged;
- delta journal binary format is unchanged;
- Runtime Checkpoint JSON version advances to 3;
- versions 1 and 2 remain readable.

## v0.4.0-alpha.6 – Deterministic Restore & Research Alignment

- added exact dynamic neuron state to runtime checkpoints;
- added dashboard homeostasis bridge;
- aligned roadmap with project research documents.

## v0.4.0-alpha.5 – Operator Dashboard

- added local read-only dashboard and lazy snapshot heatmaps.

## v0.4.0-alpha.4 – Persistence Finalization

- bounded asynchronous storage queue;
- persistence telemetry;
- generation-based crash-safe compaction;
- runtime checkpoint and real network restore foundation.

## v0.4.0-alpha.3 – Runtime Storage & Lazy Views

- runtime storage session;
- lazy mmap activity/weight/energy projection;
- strict storage typing and verification tooling.

## v0.4.0-alpha.2 – Journal & Recovery

- append-only delta journal, CRC, commit markers, and crash recovery.

## v0.4.0-alpha.1 – `.b5d` Storage V1

- frozen binary snapshot format, mmap reader, deterministic layout, and format
  robustness tests.

## v0.3.x – Learning and Structural Foundation

- STDP and eligibility traces;
- reward-modulated three-factor learning;
- heatmap observability;
- optical state/manipulator experiments;
- optional pruning, sprouting, and neurogenesis.

## v0.1.0 – Verified Observable Core

- sparse 5D spatial index;
- Izhikevich reference neuron;
- delayed event propagation;
- deterministic Golden Chain;
- telemetry and run artifacts.
