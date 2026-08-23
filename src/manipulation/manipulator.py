"""Safe read/write façade for Brain-5D.

All topology mutations go through the existing NeuralNetwork API. Extended
optical and graph properties are sidecars so Sprint-1/2 core determinism and
binary compatibility remain intact.

The Brain5DManipulator provides:
- Inspection: Read neuron and synapse state with optical metadata
- Mutation: Modify neurons, synapses, and optical properties
- Transactions: Group operations for atomic commit or rollback
- Audit Logging: Track all operations for reproducibility
- Rollback: Undo mutations with inverse operations

This manipulator is designed for:
1. Interactive exploration and debugging
2. Structural plasticity experiments
3. Dashboard and operator console integration
4. Journaling and replay for reproducibility

Example:
    >>> from src.manipulation import Brain5DManipulator
    >>> manipulator = Brain5DManipulator(network)
    >>> manipulator.begin("my_transaction")
    >>> nid = manipulator.create_neuron((1, 2, 3, 4, 5))
    >>> manipulator.set_neuron(nid, v=-60.0, energy=0.8)
    >>> manipulator.commit()
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from src.core.spatial_index import (
    Coord5D,
    iter_neighbour_coords,
    pack_coords,
    unpack_coords,
)
from src.storage.optical_codec import OpticalPointState, state_from_neuron

# ============================================================================
# Synapse Metadata
# ============================================================================


@dataclass(slots=True)
class SynapseMetadata:
    """Extended metadata for synapses beyond the core model.

    This metadata is stored as a sidecar to maintain core determinism and
    binary compatibility. It provides additional properties for advanced
    plasticity and visualization.

    Attributes:
        synapse_type: Type of synapse ('chemical', 'electrical').
        excitatory: Whether the synapse is excitatory (True) or inhibitory (False).
        transmitter: Neurotransmitter type (e.g., 'glutamate', 'GABA').
        receptor: Receptor type (e.g., 'AMPA', 'NMDA').
        plasticity: General plasticity state/coefficient.
        ltp: Long-term potentiation state.
        ltd: Long-term depression state.
        chemical_state: Chemical state value.
        electrical_state: Electrical state value.
        phase_relation: Phase relation between pre and post.
        coherence: Synaptic coherence (0.0 - 1.0).
        created_tick: Tick when the synapse was created.
        modified_tick: Tick when the synapse was last modified.
        flags: Bitmask for additional flags.
    """

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

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "synapse_type": self.synapse_type,
            "excitatory": self.excitatory,
            "transmitter": self.transmitter,
            "receptor": self.receptor,
            "plasticity": self.plasticity,
            "ltp": self.ltp,
            "ltd": self.ltd,
            "chemical_state": self.chemical_state,
            "electrical_state": self.electrical_state,
            "phase_relation": self.phase_relation,
            "coherence": self.coherence,
            "created_tick": self.created_tick,
            "modified_tick": self.modified_tick,
            "flags": self.flags,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SynapseMetadata:
        """Deserialize from a dictionary."""
        return cls(
            synapse_type=data.get("synapse_type", "chemical"),
            excitatory=data.get("excitatory", True),
            transmitter=data.get("transmitter", "glutamate"),
            receptor=data.get("receptor", "AMPA"),
            plasticity=data.get("plasticity", 0.0),
            ltp=data.get("ltp", 0.0),
            ltd=data.get("ltd", 0.0),
            chemical_state=data.get("chemical_state", 0.0),
            electrical_state=data.get("electrical_state", 0.0),
            phase_relation=data.get("phase_relation", 0.0),
            coherence=data.get("coherence", 0.0),
            created_tick=data.get("created_tick", 0),
            modified_tick=data.get("modified_tick", 0),
            flags=data.get("flags", 0),
        )


# ============================================================================
# Mutation and Transaction Types
# ============================================================================


@dataclass(slots=True)
class Mutation:
    """A single operation for transaction rollback.

    Attributes:
        operation: The operation name ('set_neuron', 'delete_synapse', etc.).
        payload: The operation parameters for inverse application.
    """

    operation: str
    payload: dict[str, Any]


@dataclass(slots=True)
class Transaction:
    """A transaction with a name and a list of inverse mutations.

    Attributes:
        name: The transaction name (for auditing).
        inverse: List of inverse mutations for rollback.
    """

    name: str
    inverse: list[Mutation] = field(default_factory=list)  # type: ignore


# ============================================================================
# Manipulator
# ============================================================================


class Brain5DManipulator:
    """Instrument for inspection, mutation, journaling and rollback.

    The manipulator provides a safe, audited interface for modifying the
    Brain-5D network state. All operations are logged and can be rolled back
    using transactions.

    Design Principles:
    1. Safety – All mutations go through the public NeuralNetwork API.
    2. Auditability – Every operation is logged with tick and metadata.
    3. Reversibility – Transactions support atomic rollback.
    4. Sidecar Metadata – Optical and metadata properties are stored separately
       from core network state for compatibility.

    Attributes:
        network: The NeuralNetwork instance to manipulate.
        optical: Dictionary mapping neuron_id to OpticalPointState.
        synapse_metadata: Dictionary mapping (source_id, target_id) to SynapseMetadata.
        audit_log: List of audit entries for all operations.
    """

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
    """Neuron fields that can be modified via set_neuron()."""

    _SYNAPSE_WRITABLE = {"weight", "delay", "eligibility", "last_pre_spike"}
    """Synapse fields that can be modified via update_synapse()."""

    def __init__(self, network: Any) -> None:
        """Initialize the manipulator.

        Args:
            network: The NeuralNetwork instance to manipulate.
        """
        self.network = network
        self.optical: dict[int, OpticalPointState] = {}
        self.synapse_metadata: dict[tuple[int, int], SynapseMetadata] = {}
        self.audit_log: list[dict[str, Any]] = []
        self._transaction: Transaction | None = None

    # ========================================================================
    # Internal Helpers
    # ========================================================================

    def _audit(self, operation: str, **payload: Any) -> None:
        """Log an operation to the audit log."""
        self.audit_log.append(
            {
                "tick": int(self.network.current_tick),
                "operation": operation,
                **payload,
            }
        )

    def _record_inverse(self, operation: str, **payload: Any) -> None:
        """Record an inverse operation for the current transaction."""
        if self._transaction is not None:
            self._transaction.inverse.append(Mutation(operation, payload))

    def _find_synapse(self, source_id: int, target_id: int) -> Any:
        """Find a synapse by source and target IDs.

        Returns:
            The Synapse object.

        Raises:
            KeyError: If the synapse does not exist.
        """
        for syn in self.network.synapses.get(source_id, ()):
            if syn.target_id == target_id:
                return syn
        raise KeyError((source_id, target_id))

    # ========================================================================
    # Transaction Management
    # ========================================================================

    def begin(self, name: str = "manual") -> None:
        """Begin a transaction for atomic operations.

        Args:
            name: The transaction name (for auditing).

        Raises:
            RuntimeError: If a transaction is already active.
        """
        if self._transaction is not None:
            raise RuntimeError("transaction already active")
        self._transaction = Transaction(name=name)

    def commit(self) -> None:
        """Commit the current transaction.

        Raises:
            RuntimeError: If no transaction is active.
        """
        if self._transaction is None:
            raise RuntimeError("no active transaction")
        self._audit(
            "COMMIT",
            name=self._transaction.name,
            operations=len(self._transaction.inverse),
        )
        self._transaction = None

    def rollback(self) -> None:
        """Rollback the current transaction by applying inverse operations.

        Raises:
            RuntimeError: If no transaction is active.
        """
        tx = self._transaction
        if tx is None:
            raise RuntimeError("no active transaction")
        self._transaction = None

        for mutation in reversed(tx.inverse):
            self._apply_inverse(mutation)

        self._audit("ROLLBACK", name=tx.name, operations=len(tx.inverse))

    def _apply_inverse(self, mutation: Mutation) -> None:
        """Apply an inverse mutation.

        This method handles all inverse operation types to restore state
        during rollback.

        Args:
            mutation: The mutation with operation and payload.
        """
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
                p["source_id"],
                p["target_id"],
                p["weight"],
                p["delay"],
                p["metadata"],
            )

        elif mutation.operation == "set_synapse":
            self.update_synapse(p["source_id"], p["target_id"], **p["values"])

    # ========================================================================
    # Neuron Inspection
    # ========================================================================

    def get_neuron(self, neuron_id: int) -> dict[str, Any]:
        """Get detailed neuron information.

        Args:
            neuron_id: The ID of the neuron.

        Returns:
            A dictionary with core state, optical state, coordinates, and degree.

        Raises:
            KeyError: If the neuron does not exist.
        """
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

    def get_neuron_by_coord(self, coord: Coord5D) -> dict[str, Any] | None:
        """Get neuron information by coordinate.

        Args:
            coord: The 5D coordinate.

        Returns:
            Neuron information dictionary, or None if no neuron exists.
        """
        nid = pack_coords(*coord)
        if nid not in self.network.neurons:
            return None
        return self.get_neuron(nid)

    # ========================================================================
    # Neuron Mutation
    # ========================================================================

    def set_neuron(self, neuron_id: int, **values: Any) -> None:
        """Modify writable neuron fields.

        Args:
            neuron_id: The ID of the neuron.
            **values: The fields to modify (must be in _NEURON_WRITABLE).

        Raises:
            ValueError: If any field is not writable.
            KeyError: If the neuron does not exist.
        """
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
        """Set optical state for a neuron.

        Args:
            neuron_id: The ID of the neuron.
            **values: The optical fields to set.

        Returns:
            The updated OpticalPointState.

        Raises:
            KeyError: If the neuron does not exist.
            ValueError: If any field is unknown or invalid.
        """
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
        self,
        coord: Coord5D,
        optical: OpticalPointState | None = None,
    ) -> int:
        """Create a new neuron at the given coordinate.

        Args:
            coord: The 5D coordinate for the new neuron.
            optical: Optional optical state (default: derived from neuron).

        Returns:
            The ID of the created neuron.
        """
        nid = int(self.network.add_neuron(coord))
        self.optical[nid] = optical or state_from_neuron(self.network.neurons[nid])

        self._record_inverse("delete_neuron", neuron_id=nid)
        self._audit("CREATE_NEURON", neuron_id=nid, coord=coord)

        return nid

    def delete_neuron(self, neuron_id: int) -> None:
        """Delete a neuron and all its connections.

        Args:
            neuron_id: The ID of the neuron to delete.
        """
        if neuron_id not in self.network.neurons:
            return

        neuron = self.network.neurons[neuron_id]
        values = {name: getattr(neuron, name) for name in self._NEURON_WRITABLE}

        # Save outgoing synapses
        outgoing: list[tuple[int, float, int, SynapseMetadata | None]] = []
        for syn in self.network.synapses.get(neuron_id, ()):
            outgoing.append(
                (
                    syn.target_id,
                    syn.weight,
                    syn.delay,
                    self.synapse_metadata.get((neuron_id, syn.target_id)),
                )
            )

        # Save incoming synapses
        incoming: list[tuple[int, float, int, SynapseMetadata | None]] = []
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
            optical=self.optical.get(neuron_id) or state_from_neuron(neuron),
            outgoing=outgoing,
            incoming=incoming,
        )

        self.network.remove_neuron(neuron_id)
        self.optical.pop(neuron_id, None)

        # Clean up synapse metadata
        for key in [k for k in self.synapse_metadata if neuron_id in k]:
            self.synapse_metadata.pop(key, None)

        self._audit("DELETE_NEURON", neuron_id=neuron_id)

    # ========================================================================
    # Synapse Mutation
    # ========================================================================

    def create_synapse(
        self,
        source_id: int,
        target_id: int,
        weight: float,
        delay: int,
        metadata: SynapseMetadata | None = None,
    ) -> None:
        """Create a synapse between two neurons.

        Args:
            source_id: The presynaptic neuron ID.
            target_id: The postsynaptic neuron ID.
            weight: The synaptic weight.
            delay: The transmission delay in ticks.
            metadata: Optional synapse metadata.
        """
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
        """Update writable synapse fields.

        Args:
            source_id: The presynaptic neuron ID.
            target_id: The postsynaptic neuron ID.
            **values: The fields to modify (must be in _SYNAPSE_WRITABLE).

        Raises:
            ValueError: If any field is not writable or delay is out of bounds.
            KeyError: If the synapse does not exist.
        """
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
        self,
        source_id: int,
        target_id: int,
        **values: Any,
    ) -> SynapseMetadata:
        """Set synapse metadata.

        Args:
            source_id: The presynaptic neuron ID.
            target_id: The postsynaptic neuron ID.
            **values: The metadata fields to set.

        Returns:
            The updated SynapseMetadata.

        Raises:
            ValueError: If any field is unknown.
            KeyError: If the synapse does not exist.
        """
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
        """Delete a synapse.

        Args:
            source_id: The presynaptic neuron ID.
            target_id: The postsynaptic neuron ID.
        """
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

    # ========================================================================
    # Synapse Query Methods
    # ========================================================================

    def get_synapse_metadata(
        self,
        source_id: int,
        target_id: int,
    ) -> SynapseMetadata | None:
        """Get metadata for a synapse.

        Args:
            source_id: The presynaptic neuron ID.
            target_id: The postsynaptic neuron ID.

        Returns:
            The SynapseMetadata, or None if no metadata exists.
        """
        return self.synapse_metadata.get((source_id, target_id))

    def get_outgoing_synapses(self, neuron_id: int) -> list[tuple[int, float, int]]:
        """Get all outgoing synapses from a neuron.

        Args:
            neuron_id: The neuron ID.

        Returns:
            A list of (target_id, weight, delay) tuples.
        """
        result: list[tuple[int, float, int]] = []
        for syn in self.network.synapses.get(neuron_id, ()):
            result.append((syn.target_id, syn.weight, syn.delay))
        return result

    def get_incoming_synapses(self, neuron_id: int) -> list[tuple[int, float, int]]:
        """Get all incoming synapses to a neuron.

        Args:
            neuron_id: The neuron ID.

        Returns:
            A list of (source_id, weight, delay) tuples.
        """
        result: list[tuple[int, float, int]] = []
        for source_id, synapses in self.network.synapses.items():
            for syn in synapses:
                if syn.target_id == neuron_id:
                    result.append((source_id, syn.weight, syn.delay))
        return result

    # ========================================================================
    # Spatial Queries
    # ========================================================================

    def neighbours(
        self,
        neuron_id: int,
        radius: float = 1.0,
        existing_only: bool = True,
    ) -> list[int]:
        """Find neighboring neurons within a radius.

        Args:
            neuron_id: The center neuron ID.
            radius: The search radius in 5D space.
            existing_only: If True, only return existing neurons.

        Returns:
            A list of neuron IDs within the radius.
        """
        coord = unpack_coords(neuron_id)
        result: list[int] = []

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
        """Query neurons with filters.

        Args:
            min_activation_v: Minimum membrane potential.
            min_energy: Minimum energy level.
            coord_center: Optional center coordinate for spatial filter.
            radius: Optional radius for spatial filter.
            limit: Maximum number of results.

        Returns:
            A list of matching neuron IDs.
        """
        if coord_center is not None and radius is not None:
            # Spatial query
            ids: list[int] = []
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
            candidates = list(self.network.neurons.keys())

        out: list[int] = []

        for nid in candidates:
            neuron = self.network.neurons[nid]

            if min_activation_v is not None and float(neuron.v) < min_activation_v:
                continue
            if min_energy is not None and float(neuron.energy) < min_energy:
                continue

            out.append(nid)

            if limit is not None and len(out) >= limit:
                break

        return out

    # ========================================================================
    # StructuralManipulator Protocol Implementation
    # ========================================================================

    def create_neuron_near(self, neuron_id: int | None = None) -> int:
        """Create a new neuron near an existing one (StructuralManipulator protocol).

        Args:
            neuron_id: Optional reference neuron ID. If None, creates at origin.

        Returns:
            The ID of the created neuron.
        """
        if neuron_id is not None and neuron_id in self.network.neurons:
            coord = unpack_coords(neuron_id)
            # Try neighbours first
            for c in iter_neighbour_coords(coord, self.network.dimensions, 1.0):
                nid = pack_coords(*c)
                if nid not in self.network.neurons:
                    return self.create_neuron(c)
        # Fallback: create at origin
        return self.create_neuron((0, 0, 0, 0, 0))

    def remove_neuron(self, neuron_id: int) -> bool:
        """Remove a neuron (StructuralManipulator protocol).

        Args:
            neuron_id: The ID of the neuron to remove.

        Returns:
            True if the neuron was removed, False if it did not exist.
        """
        if neuron_id not in self.network.neurons:
            return False
        self.delete_neuron(neuron_id)
        return True

    def sprout_synapse(
        self, source_id: int | None = None, target_id: int | None = None
    ) -> tuple[int, int]:
        """Create a synapse between two neurons (StructuralManipulator protocol).

        Args:
            source_id: Optional presynaptic neuron ID.
            target_id: Optional postsynaptic neuron ID.

        Returns:
            Tuple of (source_id, target_id) of the created synapse.
        """
        src: int = (
            source_id
            if source_id is not None
            else next(iter(self.network.neurons), 0)
        )
        tgt: int = target_id if target_id is not None else src
        if target_id is None:
            # Find a different neuron
            for nid in self.network.neurons:
                if nid != src:
                    tgt = nid
                    break
        self.create_synapse(src, tgt, weight=1.0, delay=1)
        return (src, tgt)

    def prune_synapse(
        self, source_id: int | None = None, target_id: int | None = None
    ) -> tuple[int, int]:
        """Remove a synapse between two neurons (StructuralManipulator protocol).

        Args:
            source_id: Optional presynaptic neuron ID.
            target_id: Optional postsynaptic neuron ID.

        Returns:
            Tuple of (source_id, target_id) of the pruned synapse.
        """
        src: int = (
            source_id
            if source_id is not None
            else (next(iter(self.network.synapses), 0) if self.network.synapses else 0)
        )
        tgt: int = target_id if target_id is not None else 0
        if target_id is None and src in self.network.synapses:
            synapses = list(self.network.synapses[src])
            if synapses:
                tgt = synapses[0].target_id
        self.delete_synapse(src, tgt)
        return (src, tgt)

    def undo(self) -> bool:
        """Undo the last transaction (StructuralManipulator protocol).

        Returns:
            True if undo was performed, False if no transaction was active.
        """
        if self._transaction is None:
            return False
        self.rollback()
        return True

    # ========================================================================
    # String Representation
    # ========================================================================

    def __repr__(self) -> str:
        """Return a string representation of the manipulator."""
        return (
            f"Brain5DManipulator(neurons={len(self.network.neurons)}, "
            f"synapses={self.network.synapse_count}, "
            f"optical={len(self.optical)}, "
            f"audit={len(self.audit_log)})"
        )


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "Brain5DManipulator",
    "Mutation",
    "SynapseMetadata",
    "Transaction",
]
