"""Learning and plasticity for Brain-5D.

This package provides:
- Pair-based STDP (isolated and production variants)
- Reward-modulated plasticity
- Eligibility traces
- Learning engine for network integration
"""

from .eligibility import EligibilityTrace, create_eligibility_trace
from .learning_engine import LearningEngine, LearningParameters, LearningStats
from .reward import RewardSignal, create_reward
from .stdp_plugin import STDPParameters, STDPSynapse, create_stdp_synapse

__all__ = [
    # STDP
    "STDPParameters",
    "STDPSynapse",
    "create_stdp_synapse",
    # Reward
    "RewardSignal",
    "create_reward",
    # Learning Engine
    "LearningEngine",
    "LearningParameters",
    "LearningStats",
    # Eligibility
    "EligibilityTrace",
    "create_eligibility_trace",
]