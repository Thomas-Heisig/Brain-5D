"""Learning components for Brain 5D."""

from .eligibility import EligibilityTrace
from .learning_engine import LearningEngine, LearningParameters, LearningStats
from .reward import RewardSignal
from .stdp_plugin import STDPSynapse

__all__ = [
    "EligibilityTrace",
    "LearningEngine",
    "LearningParameters",
    "LearningStats",
    "RewardSignal",
    "STDPSynapse",
]
