"""Brain-5D core neural network components.

This package provides the fundamental building blocks of the Brain-5D
spiking neural network, including:
- 5D spatial indexing and coordinate transformations
- Izhikevich neuron model with multiple types, homeostasis, and energy
- Synaptic connections with STDP, reward-modulated plasticity, and metaplasticity
- Sparse spiking neural network with event-driven spike propagation

All components are fully typed and support serialization.
"""

from __future__ import annotations

# ============================================================================
# Network
# ============================================================================
from .network import (
    Brain5DConfig,
    NetworkConfig,
    NeuralNetwork,
    PostStepHook,
    SimulationConfig,
    SpikeEvent,
    StepResult,
    TopologyConfig,
    create_network,
)

# ============================================================================
# Neuron
# ============================================================================
from .neuron import (
    Neuron,
    NeuronConfig,
    NeuronType,
    create_neuron,
    create_random_neuron,
)

# ============================================================================
# Spatial Index
# ============================================================================
from .spatial_index import (
    BITS_PER_DIM,
    DIM_INDICES,
    DIM_NAMES,
    MASK,
    MAX_COORD,
    SHIFTS,
    Coord5D,
    Dim5D,
    chebyshev_distance_5d,
    coords_to_linear,
    coords_to_linear_batch,
    distance_5d,
    euclidean_distance_5d,
    get_dimension_index,
    get_dimension_name,
    is_valid_coord,
    is_valid_coord_in_dims,
    iter_linear_neighbours,
    iter_neighbour_coords,
    linear_to_5d,
    linear_to_coord,
    linear_to_coords_batch,
    make_boundary_coord,
    manhattan_distance_5d,
    neighbour_count,
    neighbour_offsets,
    pack_coords,
    total_cells,
    unpack_coords,
    validate_coord,
    validate_coord_in_dims,
    validate_dims,
    weighted_distance_5d,
)

# ============================================================================
# Synapse
# ============================================================================
from .synapse import (
    A_MINUS,
    A_PLUS,
    ELIGIBILITY_DECAY,
    TAU_MINUS,
    TAU_PLUS,
    W_MAX,
    W_MIN,
    Synapse,
    SynapseConfig,
    create_random_synapse,
    create_synapse,
)

# ============================================================================
# Public API
# ============================================================================

__all__ = [
    # Spatial index
    "BITS_PER_DIM",
    "Coord5D",
    "DIM_INDICES",
    "DIM_NAMES",
    "Dim5D",
    "MASK",
    "MAX_COORD",
    "SHIFTS",
    "chebyshev_distance_5d",
    "coords_to_linear",
    "coords_to_linear_batch",
    "distance_5d",
    "euclidean_distance_5d",
    "get_dimension_index",
    "get_dimension_name",
    "is_valid_coord",
    "is_valid_coord_in_dims",
    "iter_linear_neighbours",
    "iter_neighbour_coords",
    "linear_to_5d",
    "linear_to_coord",
    "linear_to_coords_batch",
    "make_boundary_coord",
    "manhattan_distance_5d",
    "neighbour_count",
    "neighbour_offsets",
    "pack_coords",
    "total_cells",
    "unpack_coords",
    "validate_coord",
    "validate_coord_in_dims",
    "validate_dims",
    "weighted_distance_5d",
    # Neuron
    "Neuron",
    "NeuronConfig",
    "NeuronType",
    "create_neuron",
    "create_random_neuron",
    # Synapse
    "A_MINUS",
    "A_PLUS",
    "ELIGIBILITY_DECAY",
    "TAU_MINUS",
    "TAU_PLUS",
    "W_MAX",
    "W_MIN",
    "Synapse",
    "SynapseConfig",
    "create_random_synapse",
    "create_synapse",
    # Network
    "Brain5DConfig",
    "NetworkConfig",
    "NeuralNetwork",
    "PostStepHook",
    "SimulationConfig",
    "SpikeEvent",
    "StepResult",
    "TopologyConfig",
    "create_network",
]
