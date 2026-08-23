"""Optional runtime bridge between a live network and Brain-5D persistence."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from .b5d import (
    B5DSnapshotWriter,
    NetworkSnapshotLike,
    NeuronSnapshotLike,
    SynapseSnapshotLike,
)
from .delta_codec import (
    NeuronAddDelta,
    NeuronRemoveDelta,
    NeuronStateDelta,
    SpikeEventDelta,
    SynapseAddDelta,
    SynapseRemoveDelta,
    SynapseWeightDelta,
    encode_neuron_add,
    encode_neuron_remove,
    encode_neuron_state,
    encode_spike_event,
    encode_synapse_add,
    encode_synapse_remove,
    encode_synapse_weight,
)
from .delta_journal import DeltaJournal, DeltaRecord
from .optical_codec import state_from_neuron


class RuntimeNeuronLike(NeuronSnapshotLike, Protocol):
    """Neuron attributes required for runtime persistence."""

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


class RuntimeSynapseLike(SynapseSnapshotLike, Protocol):
    """Synapse attributes required for runtime persistence."""

    target_id: int
    weight: float
    delay: int
    eligibility: float
    last_pre_spike: int


class StepResultLike(Protocol):
    """Minimal completed-step result consumed by the storage hook."""

    tick: int
    spike_ids: Sequence[int]


PostStepHook = Callable[[StepResultLike], None]


class RuntimeNetworkLike(NetworkSnapshotLike, Protocol):
    """Network surface required by :class:`StorageSession`.

    The attribute types are refined to RuntimeNeuronLike and RuntimeSynapseLike,
    which are compatible with the base types. The type checker warnings are
    suppressed because the refined types satisfy the base protocol contracts.
    """

    # Refined types: these are compatible with the base types but more specific.
    neurons: Mapping[int, RuntimeNeuronLike]  # type: ignore[reportIncompatibleVariableOverride]
    synapses: Mapping[int, Sequence[RuntimeSynapseLike]]  # type: ignore[reportIncompatibleVariableOverride]

    def add_post_step_hook(self, hook: PostStepHook) -> None:
        """Register a callback after a completed network step."""

    def remove_post_step_hook(self, hook: PostStepHook) -> None:
        """Remove a previously registered callback."""


@dataclass(frozen=True, slots=True)
class StorageRuntimeConfig:
    """Explicit runtime persistence policy for alpha.3."""

    snapshot_path: Path
    journal_path: Path
    commit_interval_ticks: int = 10
    capture_spike_events: bool = True
    restart_capable: bool = True

    def __post_init__(self) -> None:
        if self.commit_interval_ticks <= 0:
            raise ValueError("commit_interval_ticks must be positive")


@dataclass(frozen=True, slots=True)
class StorageRuntimeStats:
    """Counters for one attached storage session."""

    captured_ticks: int
    neuron_deltas: int
    synapse_deltas: int
    topology_deltas: int
    spike_events: int
    commits: int


@dataclass(frozen=True, slots=True)
class _NeuronFingerprint:
    v: float
    u: float
    energy: float
    spike_counter: int
    last_spike_tick: int


@dataclass(frozen=True, slots=True)
class _SynapseFingerprint:
    weight: float
    eligibility: float
    delay: int
    last_pre_spike: int


class StorageSession:
    """Capture changed network state into a `.b5d.journal` post-step hook.

    Alpha.3 intentionally uses an O(N+E) change detector while persistence is
    enabled.  The feature is disabled by default and provides a correctness
    baseline before v0.6 chunked/parallel dirty tracking.
    """

    def __init__(
        self, network: RuntimeNetworkLike, config: StorageRuntimeConfig
    ) -> None:
        self.network = network
        self.config = config
        self._journal: DeltaJournal | None = None
        self._attached = False
        self._neurons: dict[int, _NeuronFingerprint] = {}
        self._synapses: dict[tuple[int, int], _SynapseFingerprint] = {}
        self._captured_ticks = 0
        self._neuron_deltas = 0
        self._synapse_deltas = 0
        self._topology_deltas = 0
        self._spike_events = 0
        self._commits = 0

    def __enter__(self) -> StorageSession:
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
        """Return whether the session is registered as a network hook."""
        return self._attached

    @property
    def stats(self) -> StorageRuntimeStats:
        """Return immutable runtime persistence counters."""
        return StorageRuntimeStats(
            captured_ticks=self._captured_ticks,
            neuron_deltas=self._neuron_deltas,
            synapse_deltas=self._synapse_deltas,
            topology_deltas=self._topology_deltas,
            spike_events=self._spike_events,
            commits=self._commits,
        )

    def prepare_snapshot(self) -> None:
        """Create the base snapshot once, without opening the journal."""
        if self.config.snapshot_path.exists():
            return
        writer = B5DSnapshotWriter(restart_capable=self.config.restart_capable)
        writer.write(
            self.config.snapshot_path,
            self.network,
            metadata={
                "storage_runtime": "alpha.4",
                "capture_policy": "full_change_scan",
            },
        )

    def prime(self) -> None:
        """Capture the current network fingerprints without performing I/O."""
        self._prime_fingerprints()

    def start(self) -> None:
        """Create a base snapshot if needed, open its journal, and attach."""
        if self._attached:
            return
        self.prepare_snapshot()
        self._journal = DeltaJournal(
            self.config.journal_path,
            base_tick=self.network.current_tick,
        )
        self._journal.open()
        scan = self._journal.validate()
        if scan.has_uncommitted_tail:
            self._journal.truncate_uncommitted_tail()
        self.prime()
        self.network.add_post_step_hook(self.capture)
        self._attached = True

    def close(self) -> None:
        """Commit pending data, detach the hook, and close the journal."""
        if self._journal is not None and self._journal.dirty_entry_count:
            if self._journal.commit() is not None:
                self._commits += 1
        if self._attached:
            self.network.remove_post_step_hook(self.capture)
            self._attached = False
        if self._journal is not None:
            self._journal.close()
            self._journal = None

    def _require_journal(self) -> DeltaJournal:
        if self._journal is None:
            raise RuntimeError("storage session is not started")
        return self._journal

    @staticmethod
    def _neuron_fingerprint(neuron: RuntimeNeuronLike) -> _NeuronFingerprint:
        return _NeuronFingerprint(
            v=float(neuron.v),
            u=float(neuron.u),
            energy=float(neuron.energy),
            spike_counter=int(neuron.spike_counter),
            last_spike_tick=int(neuron.last_spike_tick),
        )

    @staticmethod
    def _synapse_fingerprint(synapse: RuntimeSynapseLike) -> _SynapseFingerprint:
        return _SynapseFingerprint(
            weight=float(synapse.weight),
            eligibility=float(synapse.eligibility),
            delay=int(synapse.delay),
            last_pre_spike=int(synapse.last_pre_spike),
        )

    def _prime_fingerprints(self) -> None:
        self._neurons = {
            int(neuron_id): self._neuron_fingerprint(neuron)
            for neuron_id, neuron in self.network.neurons.items()
        }
        self._synapses = {
            (int(source_id), int(synapse.target_id)): self._synapse_fingerprint(synapse)
            for source_id, outgoing in self.network.synapses.items()
            for synapse in outgoing
        }

    def collect_deltas(self, result: StepResultLike) -> tuple[DeltaRecord, ...]:
        """Collect typed deltas for one completed tick without performing I/O."""
        deltas: list[DeltaRecord] = []
        tick = int(result.tick)
        current_neuron_ids = {int(value) for value in self.network.neurons}
        previous_neuron_ids = set(self._neurons)

        for removed_id in sorted(previous_neuron_ids - current_neuron_ids):
            deltas.append(encode_neuron_remove(tick, NeuronRemoveDelta(removed_id)))
            self._neurons.pop(removed_id, None)
            self._topology_deltas += 1

        for added_id in sorted(current_neuron_ids - previous_neuron_ids):
            neuron = self.network.neurons[added_id]
            optical = state_from_neuron(neuron)
            deltas.append(
                encode_neuron_add(
                    tick,
                    NeuronAddDelta(
                        neuron_id=added_id,
                        tick=tick,
                        optical=optical,
                        a=float(neuron.a),
                        b=float(neuron.b),
                        c=float(neuron.c),
                        d=float(neuron.d),
                        spike_cost=float(neuron.spike_cost),
                        spike_counter=int(neuron.spike_counter),
                        last_spike_tick=int(neuron.last_spike_tick),
                    ),
                )
            )
            self._topology_deltas += 1

        for neuron_id, neuron in self.network.neurons.items():
            numeric_id = int(neuron_id)
            neuron_fingerprint = self._neuron_fingerprint(neuron)
            previous_neuron = self._neurons.get(numeric_id)
            if previous_neuron is not None and neuron_fingerprint != previous_neuron:
                deltas.append(
                    encode_neuron_state(
                        tick,
                        NeuronStateDelta(
                            neuron_id=numeric_id,
                            membrane_v=neuron_fingerprint.v,
                            recovery_u=neuron_fingerprint.u,
                            energy=neuron_fingerprint.energy,
                            spike_counter=neuron_fingerprint.spike_counter,
                            last_spike_tick=neuron_fingerprint.last_spike_tick,
                        ),
                    )
                )
                self._neuron_deltas += 1
            self._neurons[numeric_id] = neuron_fingerprint

        current_synapses: dict[
            tuple[int, int], tuple[RuntimeSynapseLike, _SynapseFingerprint]
        ] = {}
        for source_id, outgoing in self.network.synapses.items():
            for synapse in outgoing:
                key = (int(source_id), int(synapse.target_id))
                current_synapses[key] = (synapse, self._synapse_fingerprint(synapse))

        previous_synapse_keys = set(self._synapses)
        current_synapse_keys = set(current_synapses)
        for source_id, target_id in sorted(
            previous_synapse_keys - current_synapse_keys
        ):
            deltas.append(
                encode_synapse_remove(
                    tick, SynapseRemoveDelta(source_id=source_id, target_id=target_id)
                )
            )
            self._synapses.pop((source_id, target_id), None)
            self._topology_deltas += 1

        for source_id, target_id in sorted(
            current_synapse_keys - previous_synapse_keys
        ):
            synapse, synapse_fingerprint = current_synapses[(source_id, target_id)]
            deltas.append(
                encode_synapse_add(
                    tick,
                    SynapseAddDelta(
                        source_id=source_id,
                        target_id=target_id,
                        weight=synapse_fingerprint.weight,
                        eligibility=synapse_fingerprint.eligibility,
                        delay=synapse_fingerprint.delay,
                        last_pre_spike=synapse_fingerprint.last_pre_spike,
                    ),
                )
            )
            self._synapses[(source_id, target_id)] = synapse_fingerprint
            self._topology_deltas += 1

        for key in sorted(current_synapse_keys & previous_synapse_keys):
            _, synapse_fingerprint = current_synapses[key]
            previous_synapse = self._synapses[key]
            if synapse_fingerprint != previous_synapse:
                source_id, target_id = key
                deltas.append(
                    encode_synapse_weight(
                        tick,
                        SynapseWeightDelta(
                            source_id=source_id,
                            target_id=target_id,
                            weight=synapse_fingerprint.weight,
                            eligibility=synapse_fingerprint.eligibility,
                            last_pre_spike=synapse_fingerprint.last_pre_spike,
                        ),
                    )
                )
                self._synapse_deltas += 1
            self._synapses[key] = synapse_fingerprint

        if self.config.capture_spike_events:
            for neuron_id in result.spike_ids:
                deltas.append(
                    encode_spike_event(tick, SpikeEventDelta(neuron_id=int(neuron_id)))
                )
                self._spike_events += 1

        return tuple(deltas)

    def capture(self, result: StepResultLike) -> None:
        """Capture one completed tick and synchronously persist its deltas."""
        journal = self._require_journal()
        deltas = self.collect_deltas(result)
        for delta in deltas:
            journal.append(delta)
        self._captured_ticks += 1
        if (
            int(result.tick) % self.config.commit_interval_ticks == 0
            and journal.dirty_entry_count
        ):
            if journal.commit() is not None:
                self._commits += 1
