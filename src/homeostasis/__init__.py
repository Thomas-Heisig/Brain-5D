"""Homeostatic self-regulation for Brain-5D.

This package provides firing-rate and energy homeostasis through a post-step
observer that continuously adjusts neuron thresholds and energy levels.
"""

from .engine import HomeostasisEngine, HomeostasisParameters, HomeostasisStats
from .signals import HomeostasisSignal

__all__ = [
    "HomeostasisEngine",
    "HomeostasisParameters",
    "HomeostasisStats",
    "HomeostasisSignal",
]
