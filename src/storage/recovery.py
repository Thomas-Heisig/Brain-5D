"""Crash-safe snapshot reconstruction from frozen `.b5d` + committed journal."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
import os
from pathlib import Path
import tempfile
import time

from .b5d import (
    B5DFormatError,
    B5DReader,
    B5DSnapshotWriter,
    JSONValue,
    NeuronSnapshotLike,
    SynapseSnapshotLike,
)
from .delta_codec import (
    decode_neuron_add,
    decode_neuron_remove,
    decode_neuron_state,
    decode_spike_event,
    decode_synapse_add,
    decode_synapse_remove,
    decode_synapse_weight,
)
from .delta_journal import DeltaJournal, DeltaType, JournalCorruptionError, JournalEntry
from .optical_codec import OpticalPointState


class RecoveryError(RuntimeError):
    """Raised when snapshot+journal reconstruction cannot be completed safely."""


@dataclass(slots=True)
class _NeuronState:
    """Mutable restart state implementing the snapshot writer protocol."""

    a: float
    b: float
    c: float
    d: float
    spike_cost: float
    spike_counter: int
    last_spike_tick: int
    v: float
    u: float
    energy: float
    threshold_adaptation: float


@dataclass(slots=True)
class _SynapseState:
    """Mutable synapse state implementing the snapshot writer protocol."""

    target_id: int
    weight: float
    delay: int
    eligibility: float
    last_pre_spike: int


@dataclass(slots=True)
class _RecoveredNetwork:
    """Minimal network surface consumed by :class:`B5DSnapshotWriter`."""

    dimensions: tuple[int, int, int, int, int]
    current_tick: int
    neurons: dict[int, _NeuronState]
    synapses: dict[int, list[_SynapseState]]


@dataclass(slots=True)
class _SnapshotView:
    """Read-only typed adapter passed to the frozen V1 snapshot writer."""

    dimensions: tuple[int, int, int, int, int]
    current_tick: int
    neurons: Mapping[int, NeuronSnapshotLike]
    synapses: Mapping[int, Sequence[SynapseSnapshotLike]]


@dataclass(frozen=True, slots=True)
class RecoveryResult:
    """Summary of one successful or failed reconstruction."""

    success: bool
    recovered_tick: int
    recovered_sequence: int
    applied_entries: int
    ignored_spike_events: int
    output_path: Path | None
    error: str | None
    duration_ms: float


@dataclass(frozen=True, slots=True)
class RecoveryInspection:
    """Read-only status for a snapshot/journal pair."""

    snapshot_exists: bool
    journal_exists: bool
    committed_entries: int
    last_committed_tick: int | None
    uncommitted_tail_bytes: int


class RecoveryManager:
    """Reconstruct a restart-capable Brain-5D snapshot from committed deltas."""

    def __init__(self, snapshot_path: str | Path, journal_path: str | Path) -> None:
        self.snapshot_path = Path(snapshot_path)
        self.journal_path = Path(journal_path)

    def inspect(self) -> RecoveryInspection:
        """Inspect persistence state without mutating either file."""
        if not self.journal_path.exists():
            return RecoveryInspection(
                snapshot_exists=self.snapshot_path.exists(),
                journal_exists=False,
                committed_entries=0,
                last_committed_tick=None,
                uncommitted_tail_bytes=0,
            )
        with DeltaJournal(self.journal_path) as journal:
            scan = journal.validate()
            marker = scan.last_commit
            return RecoveryInspection(
                snapshot_exists=self.snapshot_path.exists(),
                journal_exists=True,
                committed_entries=len(scan.committed_entries),
                last_committed_tick=marker.tick if marker is not None else None,
                uncommitted_tail_bytes=scan.file_size - scan.committed_end_offset,
            )

    def recover(self, output_path: str | Path | None = None) -> RecoveryResult:
        """Replay committed deltas and atomically produce a validated snapshot."""
        started = time.perf_counter()
        try:
            if not self.snapshot_path.exists():
                raise RecoveryError(f"snapshot not found: {self.snapshot_path}")
            if not self.journal_path.exists():
                return RecoveryResult(
                    success=True,
                    recovered_tick=self._snapshot_tick(),
                    recovered_sequence=0,
                    applied_entries=0,
                    ignored_spike_events=0,
                    output_path=self.snapshot_path,
                    error=None,
                    duration_ms=(time.perf_counter() - started) * 1000.0,
                )

            with B5DReader(self.snapshot_path) as reader:
                if not reader.header.restart_capable:
                    raise RecoveryError(
                        "journal recovery requires a restart-capable base snapshot"
                    )
                network, optical_states, metadata = self._load_state(reader)

            with DeltaJournal(
                self.journal_path, base_tick=network.current_tick
            ) as journal:
                scan = journal.validate()
                entries = scan.committed_entries
                marker = scan.last_commit

            applied = 0
            ignored_spikes = 0
            for entry in entries:
                changed = self._apply_entry(network, optical_states, entry)
                if changed:
                    applied += 1
                else:
                    ignored_spikes += 1
                network.current_tick = max(network.current_tick, entry.tick)

            destination = (
                Path(output_path) if output_path is not None else self.snapshot_path
            )
            self._write_atomic(destination, network, optical_states, metadata)
            return RecoveryResult(
                success=True,
                recovered_tick=network.current_tick,
                recovered_sequence=marker.sequence if marker is not None else 0,
                applied_entries=applied,
                ignored_spike_events=ignored_spikes,
                output_path=destination,
                error=None,
                duration_ms=(time.perf_counter() - started) * 1000.0,
            )
        except (
            RecoveryError,
            JournalCorruptionError,
            B5DFormatError,
            ValueError,
            OSError,
        ) as exc:
            return RecoveryResult(
                success=False,
                recovered_tick=-1,
                recovered_sequence=-1,
                applied_entries=0,
                ignored_spike_events=0,
                output_path=None,
                error=str(exc),
                duration_ms=(time.perf_counter() - started) * 1000.0,
            )

    def truncate_uncommitted_tail(self) -> int:
        """Safely discard bytes after the latest durable commit marker."""
        if not self.journal_path.exists():
            return 0
        with DeltaJournal(self.journal_path) as journal:
            return journal.truncate_uncommitted_tail()

    def _snapshot_tick(self) -> int:
        with B5DReader(self.snapshot_path) as reader:
            return reader.header.snapshot_tick

    @staticmethod
    def _load_state(
        reader: B5DReader,
    ) -> tuple[
        _RecoveredNetwork,
        dict[int, OpticalPointState],
        dict[str, JSONValue],
    ]:
        neurons: dict[int, _NeuronState] = {}
        optical: dict[int, OpticalPointState] = {}
        for record in reader.iter_neurons():
            a = record.a
            b = record.b
            c = record.c
            d = record.d
            spike_cost = record.spike_cost
            spike_counter = record.spike_counter
            last_spike_tick = record.last_spike_tick
            if (
                a is None
                or b is None
                or c is None
                or d is None
                or spike_cost is None
                or spike_counter is None
                or last_spike_tick is None
            ):
                raise RecoveryError("restart-capable neuron record is incomplete")
            neurons[record.neuron_id] = _NeuronState(
                a=a,
                b=b,
                c=c,
                d=d,
                spike_cost=spike_cost,
                spike_counter=spike_counter,
                last_spike_tick=last_spike_tick,
                v=record.optical.membrane_v,
                u=record.optical.recovery_u,
                energy=record.optical.energy,
                threshold_adaptation=record.optical.threshold_adaptation,
            )
            optical[record.neuron_id] = record.optical
        synapses: dict[int, list[_SynapseState]] = {}
        for record in reader.iter_synapses():
            synapses.setdefault(record.source_id, []).append(
                _SynapseState(
                    target_id=record.target_id,
                    weight=record.weight,
                    delay=record.delay,
                    eligibility=record.eligibility,
                    last_pre_spike=record.last_pre_spike,
                )
            )
        network = _RecoveredNetwork(
            dimensions=reader.header.dimensions,
            current_tick=reader.header.snapshot_tick,
            neurons=neurons,
            synapses=synapses,
        )
        return network, optical, reader.metadata

    @staticmethod
    def _find_synapse(
        network: _RecoveredNetwork, source_id: int, target_id: int
    ) -> _SynapseState:
        for synapse in network.synapses.get(source_id, []):
            if synapse.target_id == target_id:
                return synapse
        raise RecoveryError(f"synapse not found: {source_id}->{target_id}")

    def _apply_entry(
        self,
        network: _RecoveredNetwork,
        optical_states: dict[int, OpticalPointState],
        entry: JournalEntry,
    ) -> bool:
        if entry.delta_type is DeltaType.NEURON_STATE:
            delta = decode_neuron_state(entry.payload)
            neuron = network.neurons.get(delta.neuron_id)
            optical = optical_states.get(delta.neuron_id)
            if neuron is None or optical is None:
                raise RecoveryError(f"neuron not found: {delta.neuron_id}")
            neuron.v = delta.membrane_v
            neuron.u = delta.recovery_u
            neuron.energy = delta.energy
            neuron.spike_counter = delta.spike_counter
            neuron.last_spike_tick = delta.last_spike_tick
            optical_states[delta.neuron_id] = replace(
                optical,
                membrane_v=delta.membrane_v,
                recovery_u=delta.recovery_u,
                energy=delta.energy,
            )
            return True

        if entry.delta_type is DeltaType.SYNAPSE_WEIGHT:
            delta = decode_synapse_weight(entry.payload)
            synapse = self._find_synapse(network, delta.source_id, delta.target_id)
            synapse.weight = delta.weight
            synapse.eligibility = delta.eligibility
            synapse.last_pre_spike = delta.last_pre_spike
            return True

        if entry.delta_type is DeltaType.SYNAPSE_ADD:
            delta = decode_synapse_add(entry.payload)
            if (
                delta.source_id not in network.neurons
                or delta.target_id not in network.neurons
            ):
                raise RecoveryError("cannot add synapse with missing endpoint")
            existing = network.synapses.setdefault(delta.source_id, [])
            if any(item.target_id == delta.target_id for item in existing):
                raise RecoveryError("duplicate synapse add delta")
            existing.append(
                _SynapseState(
                    target_id=delta.target_id,
                    weight=delta.weight,
                    delay=delta.delay,
                    eligibility=delta.eligibility,
                    last_pre_spike=delta.last_pre_spike,
                )
            )
            existing.sort(key=lambda item: item.target_id)
            return True

        if entry.delta_type is DeltaType.SYNAPSE_REMOVE:
            delta = decode_synapse_remove(entry.payload)
            outgoing = network.synapses.get(delta.source_id, [])
            remaining = [item for item in outgoing if item.target_id != delta.target_id]
            if len(remaining) == len(outgoing):
                raise RecoveryError("synapse remove delta targets missing synapse")
            network.synapses[delta.source_id] = remaining
            return True

        if entry.delta_type is DeltaType.NEURON_ADD:
            delta = decode_neuron_add(entry.payload)
            if delta.neuron_id in network.neurons:
                raise RecoveryError("duplicate neuron add delta")
            network.neurons[delta.neuron_id] = _NeuronState(
                a=delta.a,
                b=delta.b,
                c=delta.c,
                d=delta.d,
                spike_cost=delta.spike_cost,
                spike_counter=delta.spike_counter,
                last_spike_tick=delta.last_spike_tick,
                v=delta.optical.membrane_v,
                u=delta.optical.recovery_u,
                energy=delta.optical.energy,
                threshold_adaptation=delta.optical.threshold_adaptation,
            )
            optical_states[delta.neuron_id] = delta.optical
            return True

        if entry.delta_type is DeltaType.NEURON_REMOVE:
            delta = decode_neuron_remove(entry.payload)
            if delta.neuron_id not in network.neurons:
                raise RecoveryError("neuron remove delta targets missing neuron")
            network.neurons.pop(delta.neuron_id)
            optical_states.pop(delta.neuron_id, None)
            network.synapses.pop(delta.neuron_id, None)
            for source_id, outgoing in tuple(network.synapses.items()):
                network.synapses[source_id] = [
                    item for item in outgoing if item.target_id != delta.neuron_id
                ]
            return True

        if entry.delta_type is DeltaType.SPIKE_EVENT:
            decode_spike_event(entry.payload)
            return False

        if entry.delta_type is DeltaType.PARAMETER:
            raise RecoveryError(
                "PARAMETER replay is reserved for the homeostasis phase"
            )

        raise RecoveryError(f"unsupported delta type: {entry.delta_type.name}")

    @staticmethod
    def _write_atomic(
        destination: Path,
        network: _RecoveredNetwork,
        optical_states: dict[int, OpticalPointState],
        metadata: dict[str, JSONValue],
    ) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            prefix=destination.name + ".",
            suffix=".tmp",
            dir=destination.parent,
            delete=False,
        ) as temp_handle:
            temporary = Path(temp_handle.name)
        try:
            writer = B5DSnapshotWriter(restart_capable=True)
            updated_metadata = dict(metadata)
            updated_metadata["recovered"] = True
            updated_metadata["recovered_tick"] = network.current_tick
            snapshot_view = _SnapshotView(
                dimensions=network.dimensions,
                current_tick=network.current_tick,
                neurons=network.neurons,
                synapses=network.synapses,
            )
            writer.write(
                temporary,
                snapshot_view,
                optical_states=optical_states,
                metadata=updated_metadata,
            )
            with B5DReader(temporary) as validation_reader:
                validation_reader.validate_invariants()
            with temporary.open("r+b") as handle:
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, destination)
        finally:
            if temporary.exists():
                temporary.unlink()
