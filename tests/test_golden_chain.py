"""
Configuration loader for Brain‑5D experiments.

This module provides validation and loading of YAML configuration files,
ensuring all parameters meet the constraints required by the reference core.
"""

from pathlib import Path
from typing import TypedDict

import yaml


# ---------- TypedDict definitions for all configuration sections ----------
class SimulationConfig(TypedDict, total=False):
    dt_ms: float
    max_delay: int
    ticks: int  # for tests / experiments
    debug_invariants: bool  # for tests / experiments


class NeuronConfig(TypedDict, total=False):
    a: float
    b: float
    c: float
    d: float


class EnergyConfig(TypedDict, total=False):
    initial: float
    spike_cost: float
    affects_firing: bool


class TopologyConfig(TypedDict, total=False):
    input: dict[str, str | int]
    output: dict[str, str | int]
    allow_self_connections: bool
    allow_parallel_connections: bool


class NetworkConfig(TypedDict, total=False):
    initial_connections_per_neuron: int
    neighbour_radius: float
    weight_min: float
    weight_max: float


class DiagnosticsConfig(TypedDict, total=False):
    mode: str
    start_tick: int
    duration_ticks: int
    amplitude: float
    target_coord: list[int]
    input_plane_dim: str
    poisson_rate_hz: float
    poisson_amplitude: float


class TelemetryConfig(TypedDict, total=False):
    enabled: bool
    history_ticks: int
    spike_history_ticks: int


class VisualizationConfig(TypedDict, total=False):
    enabled: bool
    refresh_interval_ticks: int
    spike_raster_neurons: int
    projection_4d: str
    activity_tau_ticks: float


class LoggingConfig(TypedDict, total=False):
    interval_ticks: int


class ConfigDict(TypedDict, total=False):
    seed: int
    dimensions: list[int]
    initial_neurons: int
    max_neurons: int
    simulation: SimulationConfig
    neuron: NeuronConfig
    energy: EnergyConfig
    topology: TopologyConfig
    network: NetworkConfig
    diagnostics: DiagnosticsConfig
    telemetry: TelemetryConfig
    visualization: VisualizationConfig
    logging: LoggingConfig


# --------------------------------------------------------------------------


def load_config(path: str | Path) -> ConfigDict:
    """
    Load and validate the experiment configuration from a YAML file.

    The function performs the following checks:
        - The YAML root must be a mapping (dictionary).
        - The 'dimensions' key must provide exactly five integers in [1, 256].
        - The total number of positions is computed from the dimensions.
        - The 'initial_neurons' value must be positive and not exceed total positions.
        - The 'simulation' section must be a dictionary.
        - 'dt_ms' must be exactly 1.0 (Sprint 1 requirement).
        - 'max_delay' must be >= 1.

    Returns:
        ConfigDict: The fully validated configuration dictionary.

    Raises:
        ValueError: If any validation constraint is violated.
        FileNotFoundError: If the configuration file does not exist.
        yaml.YAMLError: If the file cannot be parsed as YAML.
    """
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    # Ensure root is a dictionary (yaml.safe_load may return None)
    if not isinstance(raw, dict):
        raise ValueError("Configuration file must contain a YAML dictionary")

    # Inform type checker about the expected structure
    cfg: ConfigDict = raw  # type: ignore[assignment]  # raw is Any, but we know it's a dict

    # Validate dimensions
    dims_raw = cfg.get("dimensions")
    if not isinstance(dims_raw, (list, tuple)):
        raise ValueError("dimensions must be a list or tuple of five integers")
    dims = tuple(dims_raw)
    if len(dims) != 5 or any(int(d) <= 0 or int(d) > 256 for d in dims):
        raise ValueError("dimensions must contain five values in 1..256")

    total_positions = 1
    for d in dims:
        total_positions *= int(d)

    # Validate initial neuron count
    initial_raw = cfg.get("initial_neurons")
    if not isinstance(initial_raw, (int, float)):
        raise ValueError("initial_neurons must be numeric")
    initial = int(initial_raw)
    if initial <= 0 or initial > total_positions:
        raise ValueError("initial_neurons outside available positions")

    # Validate simulation section
    sim_raw = cfg.get("simulation")
    if not isinstance(sim_raw, dict):
        raise ValueError("simulation section must be a dictionary")

    # Validate dt_ms
    dt_raw = sim_raw.get("dt_ms")
    if not isinstance(dt_raw, (int, float)):
        raise ValueError("dt_ms must be numeric")
    if float(dt_raw) != 1.0:
        raise ValueError("Sprint 1 reference core requires dt_ms=1.0")

    # Validate max_delay
    delay_raw = sim_raw.get("max_delay")
    if not isinstance(delay_raw, (int, float)):
        raise ValueError("max_delay must be numeric")
    if int(delay_raw) < 1:
        raise ValueError("max_delay must be >=1")

    return cfg
