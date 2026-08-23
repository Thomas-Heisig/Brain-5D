"""
Thread-safe runtime controller for interactive Brain-5D operation.

This package provides the RuntimeController, which owns the simulation clock
and exposes safe operator commands for interactive control.
"""

from .runtime import (
    ControllerCommand,
    ControllerState,
    ErrorCallback,
    HomeostasisLike,
    PostTickHook,
    RuntimeController,
    RuntimeNetworkLike,
    RuntimeTelemetry,
    SnapshotCallback,
    StepResultLike,
)

__all__ = [
    "ControllerCommand",
    "ControllerState",
    "ErrorCallback",
    "HomeostasisLike",
    "PostTickHook",
    "RuntimeController",
    "RuntimeNetworkLike",
    "RuntimeTelemetry",
    "SnapshotCallback",
    "StepResultLike",
]
