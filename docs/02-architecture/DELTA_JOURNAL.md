# Brain-5D Delta Journal v1

## Status

The journal is the append-only companion to the frozen `.b5d` Snapshot V1.
It does **not** modify the snapshot byte layout. Snapshot and journal therefore
have independent format versions.

## Guarantees

- little-endian fixed structures;
- immutable 64-byte journal header;
- monotonic 64-bit sequence numbers;
- monotonic signed 64-bit ticks;
- payloads limited to 1 MiB per entry;
- CRC32 for every entry and commit marker;
- commit marker is a protocol record, not a semantic delta;
- only entries covered by the latest complete valid commit are durable state;
- incomplete tail bytes are recoverable and may be truncated;
- CRC damage inside committed state is a hard error.

CRC32 is an accidental-corruption detector, not cryptographic authentication.

## Layout

```text
JournalHeader             64 bytes
Record*                    variable

Record := Entry | CommitMarker
Entry := EntryHeader(32) + payload(N)
CommitMarker := 32 bytes
```

### Header – 64 bytes

```text
magic[8]        B5DJNL1\0
version u16     1
header_size u16 64
flags u32
created_ns u64
base_tick u64
reserved0 u64   0
reserved1 u64   0
padding[16]     zero
```

The header is written once. Counts are intentionally absent because updating
header counters would violate append-only crash semantics.

### Entry header – 32 bytes

```text
magic[4]        ENT1
sequence u64
tick i64
delta_type u16
flags u16
payload_size u32
crc32 u32
```

The entry CRC covers the same header with the CRC field set to zero plus the
payload bytes.

### Commit marker – 32 bytes

```text
magic[4]             CMT1
sequence u64
tick i64
committed_count u32
crc32 u32
padding[4]            zero
```

`commit()` performs:

1. flush previously appended entries;
2. optional `fsync()`;
3. append commit marker;
4. flush;
5. optional `fsync()`.

## Delta types

`NEURON_STATE`, `SYNAPSE_WEIGHT`, `NEURON_ADD`, `NEURON_REMOVE`,
`SYNAPSE_ADD`, `SYNAPSE_REMOVE`, `PARAMETER`, and `SPIKE_EVENT` have stable
numeric IDs. Payload encoders live in `src/storage/delta_codec.py`.

`PARAMETER` is reserved for the later homeostasis phase. Alpha.3 recovery
rejects committed PARAMETER deltas rather than silently discarding state.

## Tail policy

A journal reopened with a pre-existing uncommitted tail refuses new appends.
The operator or recovery layer must call `truncate_uncommitted_tail()` first.
This prevents an old, unintended tail from being accidentally included in a
future commit.
