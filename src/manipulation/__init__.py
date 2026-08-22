"""Safe read/write manipulation and inspection for Brain-5D.

This package provides a safe, audited façade for modifying the Brain-5D
network state with transaction support and rollback capabilities.
"""

from .manipulator import (
    Brain5DManipulator,
    Mutation,
    SynapseMetadata,
    Transaction,
)

__all__ = [
    "Brain5DManipulator",
    "SynapseMetadata",
    "Mutation",
    "Transaction",
]