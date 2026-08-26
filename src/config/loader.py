"""
Configuration loader and validator for Brain‑5D experiments.

This module provides robust loading and validation of YAML configuration files,
ensuring all parameters meet the constraints required by the Brain-5D core.

Features:
- Full YAML configuration loading with comprehensive validation
- Support for all Brain-5D configuration sections (simulation, topology, network, neuron, energy, STDP)
- Clear error messages with context
- Default values for optional parameters
- Type-safe configuration return with TypedDict
- Backward compatibility with existing configuration files

Example:
    >>> from src.config import load_config
    >>> config = load_config("configs/poc_config.yaml")
    >>> print(config["dimensions"])
    (50, 50, 50, 50, 50)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, TypedDict, cast

import yaml

logger = logging.getLogger(__name__)


# ============================================================================
# Type Definitions
# ============================================================================


class SimulationConfig(TypedDict, total=False):
    """Configuration for simulation parameters."""

    dt_ms: float
    max_delay: int
    debug_invariants: bool


class TopologyConfig(TypedDict, total=False):
    """Configuration for network topology."""

    allow_self_connections: bool
    allow_parallel_connections: bool


class NetworkConfig(TypedDict, total=False):
    """Configuration for network parameters."""

    weight_min: float
    weight_max: float
    initial_connections_per_neuron: int
    neighbour_radius: float


class NeuronConfig(TypedDict, total=False):
    """Configuration for neuron parameters."""

    a: float
    b: float
    c: float
    d: float


class EnergyConfig(TypedDict, total=False):
    """Configuration for energy parameters."""

    initial: float
    spike_cost: float


class STDPConfig(TypedDict, total=False):
    """Configuration for STDP parameters."""

    a_plus: float
    a_minus: float
    tau_plus: float
    tau_minus: float
    enable_triplet: bool
    enable_metaplasticity: bool


class RewardConfig(TypedDict, total=False):
    """Configuration for reward-modulated plasticity."""

    reward_source: str
    output_spike_value: float


class VisualizationConfig(TypedDict, total=False):
    """Configuration for visualization."""

    enabled: bool
    refresh_interval_ticks: int


class TelemetryConfig(TypedDict, total=False):
    """Configuration for telemetry."""

    history_ticks: int
    spike_history_ticks: int


class LoggingConfig(TypedDict, total=False):
    """Configuration for logging."""

    interval_ticks: int


class ConfigDict(TypedDict, total=False):
    """Complete Brain-5D configuration dictionary.

    All fields are optional with defaults applied during validation.
    """

    # Required
    dimensions: tuple[int, int, int, int, int]
    initial_neurons: int

    # Optional sections
    seed: int
    simulation: SimulationConfig
    topology: TopologyConfig
    network: NetworkConfig
    neuron: NeuronConfig
    energy: EnergyConfig
    stdp: STDPConfig
    reward: RewardConfig
    visualization: VisualizationConfig
    telemetry: TelemetryConfig
    logging: LoggingConfig
    diagnostics: dict[str, Any]
    topology_input: dict[str, Any]  # Backward compatibility


# ============================================================================
# Default Configuration
# ============================================================================

DEFAULT_CONFIG: ConfigDict = {
    "simulation": {
        "dt_ms": 1.0,
        "max_delay": 5,
        "debug_invariants": False,
    },
    "topology": {
        "allow_self_connections": False,
        "allow_parallel_connections": False,
    },
    "network": {
        "weight_min": 0.0,
        "weight_max": 0.5,
        "initial_connections_per_neuron": 10,
        "neighbour_radius": 5.0,
    },
    "neuron": {
        "a": 0.02,
        "b": 0.2,
        "c": -65.0,
        "d": 8.0,
    },
    "energy": {
        "initial": 1.0,
        "spike_cost": 0.001,
    },
    "stdp": {
        "a_plus": 0.1,
        "a_minus": 0.12,
        "tau_plus": 20.0,
        "tau_minus": 20.0,
        "enable_triplet": False,
        "enable_metaplasticity": False,
    },
    "reward": {
        "reward_source": "external",
        "output_spike_value": 1.0,
    },
    "visualization": {
        "enabled": False,
        "refresh_interval_ticks": 100,
    },
    "telemetry": {
        "history_ticks": 10000,
        "spike_history_ticks": 1000,
    },
    "logging": {
        "interval_ticks": 100,
    },
    "seed": 42,
}


# ============================================================================
# Validation Functions
# ============================================================================


def _validate_dimensions(value: Any) -> tuple[int, int, int, int, int]:
    """Validate dimensions parameter."""
    if not isinstance(value, (list, tuple)):
        raise ValueError("dimensions must be a list or tuple")

    value_seq = cast("list[Any] | tuple[Any, ...]", value)
    if len(value_seq) != 5:
        raise ValueError(f"dimensions must have exactly 5 values, got {len(value_seq)}")

    dims: list[int] = []
    for i, d in enumerate(value_seq):
        if not isinstance(d, (int, float)):
            raise ValueError(f"dimension {i} must be numeric, got {type(d).__name__}")
        dim = int(d)
        if dim < 1 or dim > 256:
            raise ValueError(f"dimension {i} must be in 1..256, got {dim}")
        dims.append(dim)

    return (dims[0], dims[1], dims[2], dims[3], dims[4])


def _validate_initial_neurons(
    value: Any,
    dims: tuple[int, int, int, int, int],
) -> int:
    """Validate initial_neurons parameter."""
    if not isinstance(value, (int, float)):
        raise ValueError(f"initial_neurons must be numeric, got {type(value).__name__}")

    initial = int(value)
    if initial <= 0:
        raise ValueError(f"initial_neurons must be positive, got {initial}")

    total = 1
    for d in dims:
        total *= d

    if initial > total:
        raise ValueError(
            f"initial_neurons ({initial}) exceeds total positions ({total})"
        )

    return initial


def _validate_seed(value: Any) -> int:
    """Validate seed parameter."""
    if value is None:
        return 42
    if not isinstance(value, (int, float)):
        raise ValueError(f"seed must be numeric, got {type(value).__name__}")
    return int(value)


def _validate_simulation_config(
    raw: dict[str, Any],
    defaults: SimulationConfig,
) -> SimulationConfig:
    """Validate and merge simulation configuration."""
    result: SimulationConfig = {}

    # dt_ms
    dt_raw = raw.get("dt_ms", defaults.get("dt_ms", 1.0))
    if not isinstance(dt_raw, (int, float)):
        raise ValueError(f"dt_ms must be numeric, got {type(dt_raw).__name__}")
    dt = float(dt_raw)
    if dt != 1.0:
        raise ValueError(f"Sprint 1 reference core requires dt_ms=1.0, got {dt}")
    result["dt_ms"] = dt

    # max_delay
    delay_raw = raw.get("max_delay", defaults.get("max_delay", 5))
    if not isinstance(delay_raw, (int, float)):
        raise ValueError(f"max_delay must be numeric, got {type(delay_raw).__name__}")
    delay = int(delay_raw)
    if delay < 1:
        raise ValueError(f"max_delay must be >= 1, got {delay}")
    result["max_delay"] = delay

    # debug_invariants
    debug_raw = raw.get("debug_invariants", defaults.get("debug_invariants", False))
    result["debug_invariants"] = bool(debug_raw)

    return result


def _validate_topology_config(
    raw: dict[str, Any],
    defaults: TopologyConfig,
) -> TopologyConfig:
    """Validate and merge topology configuration."""
    result: TopologyConfig = {}

    result["allow_self_connections"] = bool(
        raw.get("allow_self_connections", defaults.get("allow_self_connections", False))
    )
    result["allow_parallel_connections"] = bool(
        raw.get(
            "allow_parallel_connections",
            defaults.get("allow_parallel_connections", False),
        )
    )

    return result


def _validate_network_config(
    raw: dict[str, Any],
    defaults: NetworkConfig,
) -> NetworkConfig:
    """Validate and merge network configuration."""
    result: NetworkConfig = {}

    # weight_min
    wmin_raw = raw.get("weight_min", defaults.get("weight_min", 0.0))
    if not isinstance(wmin_raw, (int, float)):
        raise ValueError(f"weight_min must be numeric, got {type(wmin_raw).__name__}")
    result["weight_min"] = float(wmin_raw)

    # weight_max
    wmax_raw = raw.get("weight_max", defaults.get("weight_max", 0.5))
    if not isinstance(wmax_raw, (int, float)):
        raise ValueError(f"weight_max must be numeric, got {type(wmax_raw).__name__}")
    result["weight_max"] = float(wmax_raw)

    if result["weight_min"] > result["weight_max"]:
        raise ValueError(
            f"weight_min ({result['weight_min']}) > weight_max ({result['weight_max']})"
        )

    # initial_connections_per_neuron
    conn_raw = raw.get(
        "initial_connections_per_neuron",
        defaults.get("initial_connections_per_neuron", 10),
    )
    if not isinstance(conn_raw, (int, float)):
        raise ValueError(
            f"initial_connections_per_neuron must be numeric, got {type(conn_raw).__name__}"
        )
    conn = int(conn_raw)
    if conn < 0:
        raise ValueError(f"initial_connections_per_neuron must be >= 0, got {conn}")
    result["initial_connections_per_neuron"] = conn

    # neighbour_radius
    radius_raw = raw.get("neighbour_radius", defaults.get("neighbour_radius", 5.0))
    if not isinstance(radius_raw, (int, float)):
        raise ValueError(
            f"neighbour_radius must be numeric, got {type(radius_raw).__name__}"
        )
    radius = float(radius_raw)
    if radius < 0:
        raise ValueError(f"neighbour_radius must be >= 0, got {radius}")
    result["neighbour_radius"] = radius

    return result


def _validate_neuron_config(
    raw: dict[str, Any],
    defaults: NeuronConfig,
) -> NeuronConfig:
    """Validate and merge neuron configuration."""
    result: NeuronConfig = {}

    for key in ["a", "b", "c", "d"]:
        value = raw.get(key, defaults.get(key))
        if value is None:
            continue
        if not isinstance(value, (int, float)):
            raise ValueError(
                f"neuron.{key} must be numeric, got {type(value).__name__}"
            )
        result[key] = float(value)  # type: ignore[literal-required]

    return result


def _validate_energy_config(
    raw: dict[str, Any],
    defaults: EnergyConfig,
) -> EnergyConfig:
    """Validate and merge energy configuration."""
    result: EnergyConfig = {}

    # initial
    init_raw = raw.get("initial", defaults.get("initial", 1.0))
    if not isinstance(init_raw, (int, float)):
        raise ValueError(
            f"energy.initial must be numeric, got {type(init_raw).__name__}"
        )
    result["initial"] = float(init_raw)

    # spike_cost
    cost_raw = raw.get("spike_cost", defaults.get("spike_cost", 0.001))
    if not isinstance(cost_raw, (int, float)):
        raise ValueError(
            f"energy.spike_cost must be numeric, got {type(cost_raw).__name__}"
        )
    result["spike_cost"] = float(cost_raw)

    return result


def _validate_stdp_config(
    raw: dict[str, Any],
    defaults: STDPConfig,
) -> STDPConfig:
    """Validate and merge STDP configuration."""
    result: STDPConfig = {}

    for key in ["a_plus", "a_minus", "tau_plus", "tau_minus"]:
        value = raw.get(key, defaults.get(key))
        if value is None:
            continue
        if not isinstance(value, (int, float)):
            raise ValueError(f"stdp.{key} must be numeric, got {type(value).__name__}")
        result[key] = float(value)  # type: ignore[literal-required]

    # Booleans
    result["enable_triplet"] = bool(
        raw.get("enable_triplet", defaults.get("enable_triplet", False))
    )
    result["enable_metaplasticity"] = bool(
        raw.get("enable_metaplasticity", defaults.get("enable_metaplasticity", False))
    )

    return result


def _validate_reward_config(
    raw: dict[str, Any],
    defaults: RewardConfig,
) -> RewardConfig:
    """Validate and merge reward configuration."""
    result: RewardConfig = {}

    # reward_source
    source = raw.get("reward_source", defaults.get("reward_source", "external"))
    if not isinstance(source, str):
        raise ValueError(f"reward_source must be a string, got {type(source).__name__}")
    if source not in {"external", "output_spike"}:
        raise ValueError(
            f"reward_source must be 'external' or 'output_spike', got {source}"
        )
    result["reward_source"] = source

    # output_spike_value
    val_raw = raw.get("output_spike_value", defaults.get("output_spike_value", 1.0))
    if not isinstance(val_raw, (int, float)):
        raise ValueError(
            f"output_spike_value must be numeric, got {type(val_raw).__name__}"
        )
    result["output_spike_value"] = float(val_raw)

    return result


def _validate_visualization_config(
    raw: dict[str, Any],
    defaults: VisualizationConfig,
) -> VisualizationConfig:
    """Validate and merge visualization configuration."""
    result: VisualizationConfig = {}

    result["enabled"] = bool(raw.get("enabled", defaults.get("enabled", False)))

    refresh_raw = raw.get(
        "refresh_interval_ticks", defaults.get("refresh_interval_ticks", 100)
    )
    if not isinstance(refresh_raw, (int, float)):
        raise ValueError(
            f"refresh_interval_ticks must be numeric, got {type(refresh_raw).__name__}"
        )
    refresh = int(refresh_raw)
    if refresh < 1:
        raise ValueError(f"refresh_interval_ticks must be >= 1, got {refresh}")
    result["refresh_interval_ticks"] = refresh

    return result


def _validate_telemetry_config(
    raw: dict[str, Any],
    defaults: TelemetryConfig,
) -> TelemetryConfig:
    """Validate and merge telemetry configuration."""
    result: TelemetryConfig = {}

    for key in ["history_ticks", "spike_history_ticks"]:
        value = raw.get(key, defaults.get(key))
        if value is None:
            continue
        if not isinstance(value, (int, float)):
            raise ValueError(
                f"telemetry.{key} must be numeric, got {type(value).__name__}"
            )
        val = int(value)
        if val < 1:
            raise ValueError(f"telemetry.{key} must be >= 1, got {val}")
        result[key] = val  # type: ignore[literal-required]

    return result


def _validate_logging_config(
    raw: dict[str, Any],
    defaults: LoggingConfig,
) -> LoggingConfig:
    """Validate and merge logging configuration."""
    result: LoggingConfig = {}

    interval_raw = raw.get("interval_ticks", defaults.get("interval_ticks", 100))
    if not isinstance(interval_raw, (int, float)):
        raise ValueError(
            f"interval_ticks must be numeric, got {type(interval_raw).__name__}"
        )
    interval = int(interval_raw)
    if interval < 1:
        raise ValueError(f"interval_ticks must be >= 1, got {interval}")
    result["interval_ticks"] = interval

    return result


# ============================================================================
# Main Loader
# ============================================================================


def load_config(
    path: str | Path,
    apply_defaults: bool = True,
) -> ConfigDict:
    """
    Load and validate the experiment configuration from a YAML file.

    Args:
        path: Path to the YAML configuration file.
        apply_defaults: Whether to fill missing values with defaults.

    Returns:
        ConfigDict: Fully validated and merged configuration.

    Raises:
        ValueError: On validation failure with detailed error message.
        FileNotFoundError: If the file does not exist.
        yaml.YAMLError: On YAML parse errors.

    Example:
        >>> config = load_config("configs/poc_config.yaml")
        >>> print(config["dimensions"])
        (50, 50, 50, 50, 50)
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        try:
            raw = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Failed to parse YAML file {path}: {e}") from e

    if raw is None:
        raw = {}
    elif not isinstance(raw, dict):
        raise ValueError("Configuration file must contain a YAML dictionary")

    raw_dict = cast("dict[str, Any]", raw)

    # ------------------------------------------------------------------------
    # Required fields
    # ------------------------------------------------------------------------

    dims = _validate_dimensions(raw_dict.get("dimensions"))
    initial_neurons = _validate_initial_neurons(raw_dict.get("initial_neurons"), dims)

    result: ConfigDict = {
        "dimensions": dims,
        "initial_neurons": initial_neurons,
    }

    # ------------------------------------------------------------------------
    # Optional fields with defaults
    # ------------------------------------------------------------------------

    defaults = cast("dict[str, Any]", DEFAULT_CONFIG)

    # Seed
    result["seed"] = _validate_seed(raw_dict.get("seed", defaults.get("seed", 42)))

    # Simulation
    sim_raw = raw_dict.get("simulation", {})
    if not isinstance(sim_raw, dict):
        raise ValueError("simulation section must be a dictionary")
    result["simulation"] = _validate_simulation_config(
        cast("dict[str, Any]", sim_raw), cast("SimulationConfig", defaults["simulation"])
    )

    # Topology
    topo_raw = raw_dict.get("topology", {})
    if not isinstance(topo_raw, dict):
        raise ValueError("topology section must be a dictionary")
    result["topology"] = _validate_topology_config(
        cast("dict[str, Any]", topo_raw), cast("TopologyConfig", defaults["topology"])
    )

    # Network
    net_raw = raw_dict.get("network", {})
    if not isinstance(net_raw, dict):
        raise ValueError("network section must be a dictionary")
    result["network"] = _validate_network_config(
        cast("dict[str, Any]", net_raw), cast("NetworkConfig", defaults["network"])
    )

    # Neuron
    neuron_raw = raw_dict.get("neuron", {})
    if not isinstance(neuron_raw, dict):
        raise ValueError("neuron section must be a dictionary")
    result["neuron"] = _validate_neuron_config(
        cast("dict[str, Any]", neuron_raw), cast("NeuronConfig", defaults["neuron"])
    )

    # Energy
    energy_raw = raw_dict.get("energy", {})
    if not isinstance(energy_raw, dict):
        raise ValueError("energy section must be a dictionary")
    result["energy"] = _validate_energy_config(
        cast("dict[str, Any]", energy_raw), cast("EnergyConfig", defaults["energy"])
    )

    # STDP
    stdp_raw = raw_dict.get("stdp", {})
    if not isinstance(stdp_raw, dict):
        raise ValueError("stdp section must be a dictionary")
    result["stdp"] = _validate_stdp_config(
        cast("dict[str, Any]", stdp_raw), cast("STDPConfig", defaults["stdp"])
    )

    # Reward
    reward_raw = raw_dict.get("reward", {})
    if not isinstance(reward_raw, dict):
        raise ValueError("reward section must be a dictionary")
    result["reward"] = _validate_reward_config(
        cast("dict[str, Any]", reward_raw), cast("RewardConfig", defaults["reward"])
    )

    # Visualization
    vis_raw = raw_dict.get("visualization", {})
    if not isinstance(vis_raw, dict):
        raise ValueError("visualization section must be a dictionary")
    result["visualization"] = _validate_visualization_config(
        cast("dict[str, Any]", vis_raw), cast("VisualizationConfig", defaults["visualization"])
    )

    # Telemetry
    tele_raw = raw_dict.get("telemetry", {})
    if not isinstance(tele_raw, dict):
        raise ValueError("telemetry section must be a dictionary")
    result["telemetry"] = _validate_telemetry_config(
        cast("dict[str, Any]", tele_raw), cast("TelemetryConfig", defaults["telemetry"])
    )

    # Logging
    log_raw = raw_dict.get("logging", {})
    if not isinstance(log_raw, dict):
        raise ValueError("logging section must be a dictionary")
    result["logging"] = _validate_logging_config(
        cast("dict[str, Any]", log_raw), cast("LoggingConfig", defaults["logging"])
    )

    # Diagnostics (passthrough, optional)
    if "diagnostics" in raw_dict:
        if not isinstance(raw_dict["diagnostics"], dict):
            raise ValueError("diagnostics section must be a dictionary")
        result["diagnostics"] = raw_dict["diagnostics"]

    # Homeostasis (passthrough, optional)
    if "homeostasis" in raw_dict:
        if not isinstance(raw_dict["homeostasis"], dict):
            raise ValueError("homeostasis section must be a dictionary")
        result["homeostasis"] = raw_dict["homeostasis"]

    # Self-organization (passthrough, optional)
    if "self_organization" in raw_dict:
        if not isinstance(raw_dict["self_organization"], dict):
            raise ValueError("self_organization section must be a dictionary")
        result["self_organization"] = raw_dict["self_organization"]

    # Eligibility (passthrough, optional)
    if "eligibility" in raw_dict:
        if not isinstance(raw_dict["eligibility"], dict):
            raise ValueError("eligibility section must be a dictionary")
        result["eligibility"] = raw_dict["eligibility"]

    # Storage (passthrough, optional)
    if "storage" in raw_dict:
        if not isinstance(raw_dict["storage"], dict):
            raise ValueError("storage section must be a dictionary")
        result["storage"] = raw_dict["storage"]

    # Topology input (backward compatibility)
    if "topology" in raw_dict and "input" in raw_dict["topology"]:
        result["topology_input"] = raw_dict["topology"]["input"]

    logger.info(f"Loaded configuration from {path}")
    logger.debug(f"Configuration: {result}")

    return result


def validate_config(config: ConfigDict) -> None:
    """
    Validate a configuration dictionary without loading from file.

    Useful for testing or for validating programmatically generated configs.

    Args:
        config: Configuration dictionary to validate.

    Raises:
        ValueError: On validation failure.
    """
    # Re-validate dimensions
    dims = _validate_dimensions(config.get("dimensions"))
    _validate_initial_neurons(config.get("initial_neurons"), dims)

    # Validate each section (will raise on errors)
    defaults = cast("dict[str, Any]", DEFAULT_CONFIG)

    sim = config.get("simulation")
    if sim:
        _validate_simulation_config(
            cast("dict[str, Any]", sim), cast("SimulationConfig", defaults["simulation"])
        )

    topo = config.get("topology")
    if topo:
        _validate_topology_config(
            cast("dict[str, Any]", topo), cast("TopologyConfig", defaults["topology"])
        )

    net = config.get("network")
    if net:
        _validate_network_config(
            cast("dict[str, Any]", net), cast("NetworkConfig", defaults["network"])
        )


# ============================================================================
# Helper Functions
# ============================================================================


def config_to_dict(config: ConfigDict) -> dict[str, Any]:
    """Convert ConfigDict to a plain dictionary (for serialization)."""
    return {k: v for k, v in config.items() if v is not None}


def save_config(config: ConfigDict, path: str | Path) -> None:
    """
    Save a configuration to a YAML file.

    Args:
        config: Configuration dictionary to save.
        path: Path where to save the configuration.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Convert tuples to lists for YAML compatibility
    data = config_to_dict(config)
    if "dimensions" in data:
        data["dimensions"] = list(data["dimensions"])

    with path.open("w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    logger.info(f"Saved configuration to {path}")


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "DEFAULT_CONFIG",
    "ConfigDict",
    "EnergyConfig",
    "LoggingConfig",
    "NetworkConfig",
    "NeuronConfig",
    "RewardConfig",
    "STDPConfig",
    "SimulationConfig",
    "TelemetryConfig",
    "TopologyConfig",
    "VisualizationConfig",
    "config_to_dict",
    "load_config",
    "save_config",
    "validate_config",
]
