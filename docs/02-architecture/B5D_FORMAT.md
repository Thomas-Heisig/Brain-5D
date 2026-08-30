# Brain-5D `.b5d` Snapshot Format V1

## Status

**FROZEN SNAPSHOT FORMAT – V1**

The V1 snapshot layout is immutable after the v0.4.0-alpha.1 robustness
freeze. Breaking changes require a new snapshot format version. The software
release itself remains alpha until journaling, recovery and main-loop
integration are complete.

## Design goals

`.b5d` V1 provides a deterministic, memory-mappable snapshot of a Brain-5D
network with fixed-size neuron and synapse records. It is intended for:

- large snapshots that must not be loaded completely into RAM,
- reproducible experiment artifacts,
- random access by neuron ID,
- viewer/observatory data sources,
- a stable base snapshot for a later append-only delta journal.

V1 is **not** a bit-exact process checkpoint. Pending events, injected-current
queues, LearningEngine-private traces and transaction history are intentionally
outside this snapshot contract.

## Byte order and alignment

All multibyte values are **little-endian**. Sections containing fixed-size
records start on a **64-byte boundary**. Alignment padding is zero-filled.

## File layout

```text
0
├── 128-byte V1 header
├── UTF-8 JSON metadata (0..65,536 bytes)
├── zero padding to 64-byte boundary
├── neuron records, strictly ascending neuron_id
├── zero padding to 64-byte boundary
└── synapse records, sorted by (source_id, target_id)
```

## Header – 128 bytes

The header uses the exact struct layout:

```text
<8sHHIQQQQII5H6xQQQQQ16x
```

| Offset | Size | Field | Encoding |
|---:|---:|---|---|
| 0 | 8 | magic | `BRAIN5D\0` |
| 8 | 2 | format_version | uint16 |
| 10 | 2 | header_size | uint16, always 128 |
| 12 | 4 | flags | uint32 |
| 16 | 8 | created_ns | uint64 |
| 24 | 8 | snapshot_tick | uint64 |
| 32 | 8 | neuron_count | uint64 |
| 40 | 8 | synapse_count | uint64 |
| 48 | 4 | neuron_record_size | uint32 |
| 52 | 4 | synapse_record_size | uint32 |
| 56 | 10 | five dimensions | 5 × uint16 |
| 66 | 6 | reserved | zero |
| 72 | 8 | metadata_offset | uint64 |
| 80 | 8 | metadata_size | uint64 |
| 88 | 8 | neuron_offset | uint64 |
| 96 | 8 | synapse_offset | uint64 |
| 104 | 8 | file_size | uint64 |
| 112 | 16 | reserved | zero |

### Flags

- `0x0001`: restart-capable neuron records are present.
- all other V1 flag bits are reserved and must be zero.

## Metadata

Metadata is a UTF-8 JSON object serialized deterministically by the writer.
The encoded payload must be at most **65,536 bytes**. NaN and Infinity are not
accepted because they are not portable JSON values.

## Neuron records

### Optical mode – 128 bytes

The first 128 bytes are exactly the existing `OpticalPointState` record from
`src/storage/optical_codec.py`. `.b5d` does not reinterpret or duplicate that
codec.

### Restart-capable mode – 160 bytes

A restart-capable neuron consists of:

```text
128-byte OpticalPointState record
+ 32-byte core extension
```

The core extension uses:

```text
<5fIq
```

and stores:

- `a`, `b`, `c`, `d` as float32,
- `spike_cost` as float32,
- `spike_counter` as uint32,
- `last_spike_tick` as int64.

The extension is deliberately separate from the optical codec so the optical
128-byte contract remains stable.

## Synapse records – 40 bytes

The exact struct is:

```text
<QQffH2xq4x
```

| Field | Type | Size |
|---|---|---:|
| source_id | uint64 | 8 |
| target_id | uint64 | 8 |
| weight | float32 | 4 |
| eligibility | float32 | 4 |
| delay | uint16 | 2 |
| alignment | reserved | 2 |
| last_pre_spike | int64 | 8 |
| reserved | zero/padding | 4 |

Brain-5D currently uses 40 significant bits for packed neuron IDs, but V1
stores IDs as uint64. This keeps records aligned and simple. A packed 40-bit
variant requires a future format version and benchmark evidence.

## Frozen invariants

A conforming V1 snapshot satisfies all of the following:

1. header is exactly 128 bytes;
2. byte order is little-endian;
3. optical records are exactly 128 bytes;
4. restart-capable records are exactly 160 bytes;
5. synapse records are exactly 40 bytes;
6. metadata is a JSON object and at most 65,536 bytes;
7. neuron IDs are strictly increasing and therefore unique;
8. synapses are sorted by `(source_id, target_id)`;
9. each synapse source and target exists in the neuron table;
10. fixed-record section offsets are 64-byte aligned;
11. alignment padding is zero;
12. header counts and offsets reproduce the exact file size;
13. unknown V1 flags and unsupported format versions are rejected.

`assert_format_invariants()` protects the compile-time record sizes.
`B5DReader.validate_invariants()` performs the optional full record scan.

## Reader guarantees

`B5DReader`:

- uses `mmap` rather than loading the complete snapshot;
- performs `get_neuron(id)` in O(log n);
- performs source-scoped `get_synapses(source_id)` in O(log m + degree);
- validates header, offsets, metadata and truncation during open;
- supports deterministic resource cleanup through a context manager;
- exposes `closed` for resource-safety tests.

```python
from src.storage import B5DReader

with B5DReader("artifacts/run.b5d") as reader:
    reader.validate_invariants()
    neuron = reader.get_neuron(1234)
    outgoing = list(reader.get_synapses(1234))
```

## Writer guarantees

`B5DSnapshotWriter`:

- sorts neuron records by ID;
- sorts synapses by source/target;
- rejects dangling source/target IDs;
- rejects out-of-range uint64 values and invalid delays;
- enforces metadata limits;
- zero-fills alignment gaps;
- can accept `created_ns=` for byte-reproducible test artifacts.

## Corruption model

V1 detects **structural corruption**: invalid magic/version, bad flags, invalid
sizes/offsets, truncation, malformed metadata, invalid sort order, dangling
synapse references and non-zero reserved alignment gaps.

V1 does **not** detect arbitrary bit flips inside otherwise valid records.
Checksums/CRC, append-only commit markers and crash recovery are intentionally
part of v0.4.0-alpha.2 and do not modify the frozen snapshot layout.

## Compatibility policy

- V1 snapshot layout: frozen.
- implementation bug fixes: allowed without layout changes.
- new journal sidecar: allowed without changing V1 snapshot bytes.
- breaking snapshot change: requires V2 and a migration utility.
