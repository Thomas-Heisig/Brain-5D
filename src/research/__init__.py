"""MHRN Scientific Evidence Framework (B5D-SEF).

The package keeps execution, DATA, interpretation and EVID authority separated.
Operational cognition runners are attached to the canonical experiment-suite
module so the existing workflow resolver can execute them without a generic
PING/runtime fallback.
"""

from __future__ import annotations

from . import cognition_experiments, experiment_suite
from .network_probe import NetworkImpulseProbe, NetworkResponseSignature
from .temporal import (
    TemporalComparator,
    TemporalComparison,
    TemporalStateFrame,
    TemporalStateMemory,
)

__version__ = "0.1.0"

# Explicit extension registration. The dashboard resolves operational runner
# names against ``src.research.experiment_suite``. Keep this list derived from
# the cognition module's public contract rather than duplicating implementation.
for _name in cognition_experiments.RUNNER_NAMES:
    if _name.startswith("run_"):
        setattr(experiment_suite, _name, getattr(cognition_experiments, _name))

__all__ = [
    "NetworkImpulseProbe",
    "NetworkResponseSignature",
    "TemporalComparator",
    "TemporalComparison",
    "TemporalStateFrame",
    "TemporalStateMemory",
    "cognition_experiments",
    "experiment_suite",
]
