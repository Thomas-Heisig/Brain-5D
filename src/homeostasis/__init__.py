"""Homeostatic self-regulation for MHRN.

This package provides firing-rate and energy homeostasis through a post-step
observer that continuously adjusts neuron thresholds and energy levels.
"""

from .engine import HomeostasisEngine, HomeostasisParameters, HomeostasisStats
from .signals import HomeostasisSignal

__all__ = [
    "HomeostasisEngine",
    "HomeostasisParameters",
    "HomeostasisSignal",
    "HomeostasisStats",
]
