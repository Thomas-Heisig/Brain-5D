# v0.4.0-alpha.3 – Runtime Storage & Lazy Snapshot Views

- completed alpha.2 append-only journal protocol with immutable header;
- added typed delta codecs and real snapshot replay;
- added CRC32 and committed-corruption detection;
- added uncommitted-tail truncation and atomic recovered snapshot publication;
- added `StorageSession` post-step persistence hook;
- added mmap-backed lazy activity/weight/energy snapshot projector;
- added strict no-`Any` storage boundaries and Pyright coverage;
- `.b5d` Snapshot V1 remains byte-for-byte frozen.

# Documentation Changelog

## 0.4.0-alpha.1 - Storage V1 final robustness freeze - 2026-08-16

### Storage contract

- `.b5d` V1 byte layout is now documented as frozen.
- Little-endian encoding, exact struct sizes and 64-byte section alignment are
  explicit compatibility requirements.
- Metadata is a deterministic UTF-8 JSON object capped at 65,536 bytes.
- The reader documents structural corruption guarantees and the deliberate
  absence of payload CRC in V1.
- Neuron IDs are strictly increasing; synapse source/target references must
  resolve to persisted neurons.

### Verification

- robustness suite covers format sizes, endian policy, roundtrip, random access,
  source-scoped synapse lookup, duplicate-ID corruption, dangling targets,
  metadata limits/JSON corruption, version/magic failures, truncation,
  non-zero padding, resource cleanup and byte determinism;
- 50k-neuron scalability smoke test is available as an explicit opt-in release
  check rather than slowing normal unit-test runs;
- PowerShell verifier runs full regression and Clean Code gates.

### Clean Code / Pylance

- `b5d.py` contains no explicit `Any` types;
- Protocol-based typed boundaries describe the required network/neuron/synapse
  surfaces;
- strict `pyrightconfig.json` targets the new storage boundary.

### Roadmap

- added `ROADMAP_TO_USABLE_AI.md` with staged milestones from persistence,
  journaling and homeostasis through learning curriculum, multimodal adapters,
  memory/context, HMI, bounded autonomy, evaluation and v1.0 release criteria.

## 0.4.0-alpha.1 - Storage V1 foundation - 2026-08-16

- `.b5d` fixed-layout snapshot format V1 introduced.
- Memory-mapped `B5DReader` and deterministic `B5DSnapshotWriter` introduced.
- Optional restart-capable neuron extension introduced.

## 0.3.0 - Sprint 2C - 2026-08-16

- RewardSignal with configurable delay.
- Signed three-factor plasticity (`eta * reward * eligibility`).
- Activity, incoming-weight and energy heatmap projections.

### Verification follow-up

- Added cross-platform `scripts/verify_b5d.py` as canonical storage verifier.
- Added `scripts/verify_b5d.cmd` for Windows environments that block unsigned PowerShell scripts.
- Added repository-hygiene rules for generated `*.egg-info`, caches and runtime storage artifacts.
- No binary storage format changes.
