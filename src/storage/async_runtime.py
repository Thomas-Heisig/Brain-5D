"""Bounded asynchronous journal writer for Brain-5D runtime persistence."""

from __future__ import annotations

import time
from dataclasses import dataclass
from queue import Full, Queue
from threading import Event, Lock, Thread
from typing import Final

from .delta_journal import DeltaJournal, DeltaRecord
from .runtime import (
    RuntimeNetworkLike,
    StepResultLike,
    StorageRuntimeConfig,
    StorageSession,
)

_STOP: Final[object] = object()


@dataclass(frozen=True, slots=True)
class AsyncStorageConfig:
    """Configuration for bounded asynchronous persistence."""

    queue_size: int = 1000
    drop_on_overflow: bool = False
    enqueue_timeout_s: float = 0.25

    def __post_init__(self) -> None:
        if self.queue_size <= 0:
            raise ValueError("queue_size must be positive")
        if self.enqueue_timeout_s < 0.0:
            raise ValueError("enqueue_timeout_s must be non-negative")


@dataclass(frozen=True, slots=True)
class StorageTelemetrySnapshot:
    """Immutable storage runtime telemetry."""

    queue_depth: int
    queue_capacity: int
    batches_enqueued: int
    batches_written: int
    deltas_written: int
    bytes_written: int
    dropped_batches: int
    write_latency_ms: float
    commit_latency_ms: float
    journal_size_bytes: int
    worker_failed: bool


@dataclass(frozen=True, slots=True)
class _Batch:
    tick: int
    deltas: tuple[DeltaRecord, ...]


class AsyncStorageSession:
    """Persist typed delta batches on a bounded background worker thread.

    Delta detection remains on the simulation thread so the worker never reads
    mutable network state. Only immutable ``DeltaRecord`` instances cross the
    queue boundary.
    """

    def __init__(
        self,
        network: RuntimeNetworkLike,
        runtime_config: StorageRuntimeConfig,
        async_config: AsyncStorageConfig,
    ) -> None:
        self.network = network
        self.runtime_config = runtime_config
        self.async_config = async_config
        self._collector = StorageSession(network, runtime_config)
        self._queue: Queue[_Batch | object] = Queue(maxsize=async_config.queue_size)
        self._thread: Thread | None = None
        self._stop = Event()
        self._failure: BaseException | None = None
        self._lock = Lock()
        self._attached = False
        self._batches_enqueued = 0
        self._batches_written = 0
        self._deltas_written = 0
        self._bytes_written = 0
        self._dropped_batches = 0
        self._write_latency_ms = 0.0
        self._commit_latency_ms = 0.0

    def __enter__(self) -> AsyncStorageSession:
        self.start()
        return self

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc: BaseException | None,
        _traceback: object,
    ) -> None:
        self.close()

    @property
    def attached(self) -> bool:
        """Return whether the network hook is active."""
        return self._attached

    @property
    def telemetry(self) -> StorageTelemetrySnapshot:
        """Return a consistent snapshot of queue and write telemetry."""
        with self._lock:
            journal_size = (
                self.runtime_config.journal_path.stat().st_size
                if self.runtime_config.journal_path.exists()
                else 0
            )
            return StorageTelemetrySnapshot(
                queue_depth=self._queue.qsize(),
                queue_capacity=self.async_config.queue_size,
                batches_enqueued=self._batches_enqueued,
                batches_written=self._batches_written,
                deltas_written=self._deltas_written,
                bytes_written=self._bytes_written,
                dropped_batches=self._dropped_batches,
                write_latency_ms=self._write_latency_ms,
                commit_latency_ms=self._commit_latency_ms,
                journal_size_bytes=journal_size,
                worker_failed=self._failure is not None,
            )

    def start(self) -> None:
        """Initialize snapshot/fingerprints and start the storage worker."""
        if self._attached:
            return
        self._prepare_collector()
        self._stop.clear()
        self._thread = Thread(
            target=self._worker_main,
            name="brain5d-storage",
            daemon=True,
        )
        self._thread.start()
        self.network.add_post_step_hook(self.capture)
        self._attached = True

    def _prepare_collector(self) -> None:
        """Prime the synchronous collector without leaving its journal open."""
        self._collector.prepare_snapshot()
        self._collector.prime()

    def capture(self, result: StepResultLike) -> None:
        """Collect immutable deltas and enqueue one tick batch."""
        self._raise_worker_failure()
        deltas = self._collector.collect_deltas(result)
        batch = _Batch(int(result.tick), deltas)
        if self.async_config.drop_on_overflow:
            try:
                self._queue.put_nowait(batch)
            except Full:
                with self._lock:
                    self._dropped_batches += 1
                return
        else:
            self._queue.put(batch, timeout=self.async_config.enqueue_timeout_s or None)
        with self._lock:
            self._batches_enqueued += 1

    def flush(self) -> None:
        """Wait until all queued batches have been processed."""
        self._queue.join()
        self._raise_worker_failure()

    def close(self) -> None:
        """Drain pending work, commit, detach, and stop the worker."""
        if self._attached:
            self.network.remove_post_step_hook(self.capture)
            self._attached = False
        if self._thread is None:
            return
        self.flush()
        self._queue.put(_STOP)
        self._thread.join()
        self._thread = None
        self._raise_worker_failure()

    def _raise_worker_failure(self) -> None:
        if self._failure is not None:
            raise RuntimeError("asynchronous storage worker failed") from self._failure

    def _worker_main(self) -> None:
        try:
            with DeltaJournal(
                self.runtime_config.journal_path,
                base_tick=self.network.current_tick,
            ) as journal:
                scan = journal.validate()
                if scan.has_uncommitted_tail:
                    journal.truncate_uncommitted_tail()
                while not self._stop.is_set():
                    item = self._queue.get()
                    try:
                        if item is _STOP:
                            if journal.dirty_entry_count:
                                self._record_commit(journal)
                            return
                        if not isinstance(item, _Batch):
                            raise TypeError("invalid async storage queue item")
                        self._write_batch(journal, item)
                    finally:
                        self._queue.task_done()
        except BaseException as exc:  # worker must surface all failures
            self._failure = exc

    def _write_batch(self, journal: DeltaJournal, batch: _Batch) -> None:
        started = time.perf_counter()
        written_bytes = 0
        for delta in batch.deltas:
            journal.append(delta)
            written_bytes += len(delta.payload)
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        if (
            batch.tick % self.runtime_config.commit_interval_ticks == 0
            and journal.dirty_entry_count
        ):
            self._record_commit(journal)
        with self._lock:
            self._batches_written += 1
            self._deltas_written += len(batch.deltas)
            self._bytes_written += written_bytes
            self._write_latency_ms = elapsed_ms

    def _record_commit(self, journal: DeltaJournal) -> None:
        started = time.perf_counter()
        journal.commit()
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        with self._lock:
            self._commit_latency_ms = elapsed_ms
