"""
Thread-safe runtime controller for interactive MHRN operation.

This package provides the RuntimeController, which owns the simulation clock
and exposes safe operator commands for interactive control.
"""

from .runtime import (
    PROFILE_PHASES,
    ControllerCommand,
    ControllerState,
    ErrorCallback,
    HomeostasisLike,
    PostTickHook,
    PreTickHook,
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
    "PROFILE_PHASES",
    "PreTickHook",
    "RuntimeController",
    "RuntimeNetworkLike",
    "RuntimeTelemetry",
    "SnapshotCallback",
    "StepResultLike",
]
