"""Safe read/write façade for Brain-5D.

All topology mutations go through the existing NeuralNetwork API. Extended
optical and graph properties are sidecars so Sprint-1/2 core determinism and
binary compatibility remain intact.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Iterable

from src.core.spatial_index import (
    Coord5D,
    iter_neighbour_coords,
    pack_coords,
    unpack_coords,
)
from src.storage.optical_codec import OpticalPointState, state_from_neuron


@dataclass(slots=True)
class SynapseMetadata:
    synapse_type: str = "chemical"
    excitatory: bool = True
    transmitter: str = "glutamate"
    receptor: str = "AMPA"
    plasticity: float = 0.0
    ltp: float = 0.0
    ltd: float = 0.0
    chemical_state: float = 0.0
    electrical_state: float = 0.0
    phase_relation: float = 0.0
    coherence: float = 0.0
    created_tick: int = 0
    modified_tick: int = 0
    flags: int = 0


@dataclass(slots=True)
class Mutation:
    operation: str
    payload: dict[str, Any]


@dataclass(slots=True)
class Transaction:
    name: str
    inverse: list[Mutation] = field(default_factory=list)


class Brain5DManipulator:
    """Instrument for inspection, mutation, journaling and rollback."""

    _NEURON_WRITABLE = {
        "a",
        "b",
        "c",
        "d",
        "v",
        "u",
        "energy",
        "spike_cost",
        "spike_counter",
        "last_spike_tick",
        "threshold_adaptation",
        "last_external_current",
        "last_synaptic_current",
    }
    _SYNAPSE_WRITABLE = {"weight", "delay", "eligibility", "last_pre_spike"}

    def __init__(self, network: Any):
        self.network = network
        self.optical: dict[int, OpticalPointState] = {}
        self.synapse_metadata: dict[tuple[int, int], SynapseMetadata] = {}
        self.audit_log: list[dict[str, Any]] = []
        self._transaction: Transaction | None = None

    def _audit(self, operation: str, **payload: Any) -> None:
        self.audit_log.append(
            {"tick": int(self.network.current_tick), "operation": operation, **payload}
        )

    def _record_inverse(self, operation: str, **payload: Any) -> None:
        if self._transaction is not None:
            self._transaction.inverse.append(Mutation(operation, payload))

    def begin(self, name: str = "manual") -> None:
        if self._transaction is not None:
            raise RuntimeError("transaction already active")
        self._transaction = Transaction(name=name)

    def commit(self) -> None:
        if self._transaction is None:
            raise RuntimeError("no active transaction")
        self._audit(
            "COMMIT",
            name=self._transaction.name,
            operations=len(self._transaction.inverse),
        )
        self._transaction = None

    def rollback(self) -> None:
        tx = self._transaction
        if tx is None:
            raise RuntimeError("no active transaction")
        self._transaction = None
        for mutation in reversed(tx.inverse):
            self._apply_inverse(mutation)
        self._audit("ROLLBACK", name=tx.name, operations=len(tx.inverse))

    def _apply_inverse(self, mutation: Mutation) -> None:
        p = mutation.payload
        if mutation.operation == "set_neuron":
            self.set_neuron(p["neuron_id"], **p["values"])
        elif mutation.operation == "delete_neuron":
            self.delete_neuron(p["neuron_id"])
        elif mutation.operation == "restore_neuron":
            nid = self.create_neuron(tuple(p["coord"]))
            self.set_neuron(nid, **p["values"])
            self.optical[nid] = p["optical"]
            for target_id, weight, delay, metadata in p["outgoing"]:
                if target_id in self.network.neurons:
                    self.create_synapse(nid, target_id, weight, delay, metadata)
            for source_id, weight, delay, metadata in p["incoming"]:
                if source_id in self.network.neurons:
                    self.create_synapse(source_id, nid, weight, delay, metadata)
        elif mutation.operation == "delete_synapse":
            self.delete_synapse(p["source_id"], p["target_id"])
        elif mutation.operation == "restore_synapse":
            self.create_synapse(
                p["source_id"], p["target_id"], p["weight"], p["delay"], p["metadata"]
            )
        elif mutation.operation == "set_synapse":
            self.update_synapse(p["source_id"], p["target_id"], **p["values"])

    def get_neuron(self, neuron_id: int) -> dict[str, Any]:
        neuron = self.network.neurons[neuron_id]
        optical = self.optical.get(neuron_id) or state_from_neuron(neuron)
        return {
            "neuron_id": neuron_id,
            "coord": unpack_coords(neuron_id),
            "core": {name: getattr(neuron, name) for name in self._NEURON_WRITABLE},
            "optical": asdict(optical),
            "in_degree": int(self.network.in_degree.get(neuron_id, 0)),
            "out_degree": len(self.network.synapses.get(neuron_id, ())),
        }

    def set_neuron(self, neuron_id: int, **values: Any) -> None:
        neuron = self.network.neurons[neuron_id]
        unknown = set(values) - self._NEURON_WRITABLE
        if unknown:
            raise ValueError(f"non-writable neuron fields: {sorted(unknown)}")
        old = {key: getattr(neuron, key) for key in values}
        self._record_inverse("set_neuron", neuron_id=neuron_id, values=old)
        for key, value in values.items():
            setattr(neuron, key, value)
        self._audit("SET_NEURON", neuron_id=neuron_id, values=values)

    def set_optical(self, neuron_id: int, **values: Any) -> OpticalPointState:
        if neuron_id not in self.network.neurons:
            raise KeyError(neuron_id)
        state = self.optical.get(neuron_id) or state_from_neuron(
            self.network.neurons[neuron_id]
        )
        old = {key: getattr(state, key) for key in values}
        for key, value in values.items():
            if not hasattr(state, key):
                raise ValueError(f"unknown optical field: {key}")
            setattr(state, key, value)
        state.validate()
        self.optical[neuron_id] = state
        self._audit("SET_OPTICAL", neuron_id=neuron_id, values=values, previous=old)
        return state

    def create_neuron(
        self, coord: Coord5D, optical: OpticalPointState | None = None
    ) -> int:
        nid = int(self.network.add_neuron(coord))
        self.optical[nid] = optical or state_from_neuron(self.network.neurons[nid])
        self._record_inverse("delete_neuron", neuron_id=nid)
        self._audit("CREATE_NEURON", neuron_id=nid, coord=coord)
        return nid

    def delete_neuron(self, neuron_id: int) -> None:
        if neuron_id not in self.network.neurons:
            return
        n = self.network.neurons[neuron_id]
        values = {name: getattr(n, name) for name in self._NEURON_WRITABLE}
        outgoing = []
        for syn in self.network.synapses.get(neuron_id, ()):
            outgoing.append(
                (
                    syn.target_id,
                    syn.weight,
                    syn.delay,
                    self.synapse_metadata.get((neuron_id, syn.target_id)),
                )
            )
        incoming = []
        for source_id, synapses in self.network.synapses.items():
            for syn in synapses:
                if syn.target_id == neuron_id:
                    incoming.append(
                        (
                            source_id,
                            syn.weight,
                            syn.delay,
                            self.synapse_metadata.get((source_id, neuron_id)),
                        )
                    )
        self._record_inverse(
            "restore_neuron",
            neuron_id=neuron_id,
            coord=unpack_coords(neuron_id),
            values=values,
            optical=self.optical.get(neuron_id) or state_from_neuron(n),
            outgoing=outgoing,
            incoming=incoming,
        )
        self.network.remove_neuron(neuron_id)
        self.optical.pop(neuron_id, None)
        for key in [k for k in self.synapse_metadata if neuron_id in k]:
            self.synapse_metadata.pop(key, None)
        self._audit("DELETE_NEURON", neuron_id=neuron_id)

    def _find_synapse(self, source_id: int, target_id: int) -> Any:
        for syn in self.network.synapses.get(source_id, ()):
            if syn.target_id == target_id:
                return syn
        raise KeyError((source_id, target_id))

    def create_synapse(
        self,
        source_id: int,
        target_id: int,
        weight: float,
        delay: int,
        metadata: SynapseMetadata | None = None,
    ) -> None:
        self.network.connect(source_id, target_id, weight, delay)
        meta = metadata or SynapseMetadata(
            created_tick=int(self.network.current_tick),
            modified_tick=int(self.network.current_tick),
        )
        self.synapse_metadata[(source_id, target_id)] = meta
        self._record_inverse("delete_synapse", source_id=source_id, target_id=target_id)
        self._audit(
            "CREATE_SYNAPSE",
            source_id=source_id,
            target_id=target_id,
            weight=weight,
            delay=delay,
        )

    def update_synapse(self, source_id: int, target_id: int, **values: Any) -> None:
        syn = self._find_synapse(source_id, target_id)
        unknown = set(values) - self._SYNAPSE_WRITABLE
        if unknown:
            raise ValueError(f"non-writable synapse fields: {sorted(unknown)}")
        old = {key: getattr(syn, key) for key in values}
        self._record_inverse(
            "set_synapse", source_id=source_id, target_id=target_id, values=old
        )
        for key, value in values.items():
            if key == "delay" and not 1 <= int(value) <= int(self.network.max_delay):
                raise ValueError(f"delay must be 1..{self.network.max_delay}")
            setattr(syn, key, value)
        meta = self.synapse_metadata.get((source_id, target_id))
        if meta is not None:
            meta.modified_tick = int(self.network.current_tick)
        self._audit(
            "UPDATE_SYNAPSE", source_id=source_id, target_id=target_id, values=values
        )

    def set_synapse_metadata(
        self, source_id: int, target_id: int, **values: Any
    ) -> SynapseMetadata:
        self._find_synapse(source_id, target_id)
        meta = self.synapse_metadata.setdefault(
            (source_id, target_id),
            SynapseMetadata(created_tick=int(self.network.current_tick)),
        )
        for key, value in values.items():
            if not hasattr(meta, key):
                raise ValueError(f"unknown synapse metadata field: {key}")
            setattr(meta, key, value)
        meta.modified_tick = int(self.network.current_tick)
        self._audit(
            "SET_SYNAPSE_METADATA",
            source_id=source_id,
            target_id=target_id,
            values=values,
        )
        return meta

    def delete_synapse(self, source_id: int, target_id: int) -> None:
        try:
            syn = self._find_synapse(source_id, target_id)
        except KeyError:
            return
        meta = self.synapse_metadata.get((source_id, target_id))
        self._record_inverse(
            "restore_synapse",
            source_id=source_id,
            target_id=target_id,
            weight=syn.weight,
            delay=syn.delay,
            metadata=meta,
        )
        self.network.disconnect(source_id, target_id)
        self.synapse_metadata.pop((source_id, target_id), None)
        self._audit("DELETE_SYNAPSE", source_id=source_id, target_id=target_id)

    def neighbours(
        self, neuron_id: int, radius: float = 1.0, existing_only: bool = True
    ) -> list[int]:
        coord = unpack_coords(neuron_id)
        result = []
        for candidate in iter_neighbour_coords(coord, self.network.dimensions, radius):
            nid = pack_coords(*candidate)
            if not existing_only or nid in self.network.neurons:
                result.append(nid)
        return result

    def query(
        self,
        *,
        min_activation_v: float | None = None,
        min_energy: float | None = None,
        coord_center: Coord5D | None = None,
        radius: float | None = None,
        limit: int | None = None,
    ) -> list[int]:
        candidates: Iterable[int]
        if coord_center is not None and radius is not None:
            ids = []
            center_id = pack_coords(*coord_center)
            if center_id in self.network.neurons:
                ids.append(center_id)
            for c in iter_neighbour_coords(
                coord_center, self.network.dimensions, radius
            ):
                nid = pack_coords(*c)
                if nid in self.network.neurons:
                    ids.append(nid)
            candidates = ids
        else:
            candidates = self.network.neurons.keys()
        out = []
        for nid in candidates:
            n = self.network.neurons[nid]
            if min_activation_v is not None and float(n.v) < min_activation_v:
                continue
            if min_energy is not None and float(n.energy) < min_energy:
                continue
            out.append(nid)
            if limit is not None and len(out) >= limit:
                break
        return out
