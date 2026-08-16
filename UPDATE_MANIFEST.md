# Brain-5D v0.4.0-alpha.3 cumulative persistence update

This overlay contains the frozen alpha.1 snapshot implementation plus the
corrected alpha.2 journal/recovery layer and the alpha.3 runtime/lazy-view
foundation.

## New modules

- `src/storage/crc.py`
- `src/storage/delta_journal.py`
- `src/storage/delta_codec.py`
- `src/storage/recovery.py`
- `src/storage/runtime.py`
- `src/storage/lazy_view.py`

## New tests

- `tests/test_crc.py`
- `tests/test_delta_journal.py`
- `tests/test_recovery.py`
- `tests/test_storage_runtime.py`
- `tests/test_lazy_storage_view.py`

## Important compatibility rule

`src/storage/b5d.py` remains the frozen `.b5d` Snapshot V1 implementation.
Journal evolution uses a separate `.b5d.journal` format version.

## Alpha.3 is not final persistence yet

The current runtime hook deliberately uses an O(N+E) change scan when enabled.
Asynchronous bounded queues, measured storage latency, crash-safe compaction,
and real-network restore-and-continue remain the exit work for alpha.3/final.


## Recovery hotfix

`src/storage/recovery.py` contains a Windows-specific durability fix: the
temporary recovered snapshot is opened with write access before `os.fsync()`.
This addresses `[Errno 9] Bad file descriptor` observed on Python 3.13/Windows.
The storage and journal formats remain unchanged.
