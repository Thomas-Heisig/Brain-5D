"""Versioned technical Wesen identity profiles."""

from .behavior import BEHAVIOR_SCHEMA_VERSION, BehaviorProfile
from .service import (
    PROFILE_SCHEMA_VERSION,
    ProfileCompatibilityError,
    ProfileError,
    ProfileNotFoundError,
    ProfileService,
    ProfileValidationError,
)

__all__ = [
    "PROFILE_SCHEMA_VERSION",
    "BEHAVIOR_SCHEMA_VERSION",
    "BehaviorProfile",
    "ProfileCompatibilityError",
    "ProfileError",
    "ProfileNotFoundError",
    "ProfileService",
    "ProfileValidationError",
]
