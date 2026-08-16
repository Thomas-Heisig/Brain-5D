# Storage Sprint V1 – v0.4.0-alpha.1 Final Robustness Freeze

## Objective

Freeze a small, deterministic `.b5d` snapshot contract before introducing
journaling or live-simulation I/O. This stage is deliberately conservative:
one reliable base snapshot is more valuable than a feature-rich persistence
layer whose recovery semantics are unclear.

## Implemented

- fixed 128-byte little-endian header;
- 64 KiB bounded deterministic JSON metadata;
- optical 128-byte and restart-capable 160-byte neuron records;
- fixed 40-byte synapse records;
- 64-byte section alignment and zero padding;
- mmap reader;
- O(log n) neuron lookup;
- O(log m + degree) source-scoped synapse lookup;
- explicit V1 format-size assertions;
- strict version/flag/header validation;
- truncation and section-overlap detection;
- unique/sorted neuron validation;
- sorted and referentially valid synapse validation;
- context-manager cleanup and idempotent close;
- deterministic byte output when `created_ns` is fixed;
- opt-in 50k-neuron scalability smoke test.

## Typing and Clean Code

The new `src/storage/b5d.py` intentionally contains no `Any` annotations.
Static boundaries are expressed with `Protocol` types:

- `NetworkSnapshotLike`
- `NeuronSnapshotLike`
- `SynapseSnapshotLike`

JSON metadata uses recursive `JSONValue` / `JSONMapping` aliases. The storage
module is therefore suitable for strict mypy/Pylance checking without making
the pre-existing Sprint-1C core depend on the storage package.

## Verification

Normal release verification:

```powershell
python -m pytest -v
black --check src/storage/b5d.py tests/test_b5d_storage.py
mypy src/storage/b5d.py
pylint src/storage/b5d.py
```

The large storage smoke test is intentionally opt-in:

```powershell
$env:BRAIN5D_RUN_LARGE_STORAGE_TEST = "1"
python -m pytest tests/test_b5d_storage.py::test_large_storage_50k_neurons -v -s
Remove-Item Env:BRAIN5D_RUN_LARGE_STORAGE_TEST
```

or use:

```powershell
.\scripts\verify_b5d.ps1
```

## Exit criteria

alpha.1 is complete when the user's real repository passes:

- complete pytest regression;
- the robustness storage suite;
- Black;
- strict mypy on `b5d.py`;
- Pylint >= 9.0;
- the opt-in 50k storage smoke test;
- a normal Brain-5D headless run.

## Explicit non-goals

Not part of alpha.1:

- delta journal;
- CRC/checksum sections;
- crash-safe commit markers;
- event-queue persistence;
- automatic periodic snapshots from `src.main`;
- Observatory lazy-file mode.

These are intentionally separated to keep the V1 snapshot contract frozen.
