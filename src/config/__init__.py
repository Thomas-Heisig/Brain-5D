"""
Brain-5D configuration management.

This package provides loading, validation, and management of
Brain-5D configuration files in YAML format.
"""

from .loader import (
    ConfigDict,
    DEFAULT_CONFIG,
    EnergyConfig,
    LoggingConfig,
    NetworkConfig,
    NeuronConfig,
    RewardConfig,
    STDPConfig,
    SimulationConfig,
    TelemetryConfig,
    TopologyConfig,
    VisualizationConfig,
    config_to_dict,
    load_config,
    save_config,
    validate_config,
)

__all__ = [
    # Types
    "ConfigDict",
    "SimulationConfig",
    "TopologyConfig",
    "NetworkConfig",
    "NeuronConfig",
    "EnergyConfig",
    "STDPConfig",
    "RewardConfig",
    "VisualizationConfig",
    "TelemetryConfig",
    "LoggingConfig",
    # Functions
    "load_config",
    "validate_config",
    "save_config",
    "config_to_dict",
    # Constants
    "DEFAULT_CONFIG",
]
