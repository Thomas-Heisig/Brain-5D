"""
Configuration loader for Brain‑5D experiments.

This module provides validation and loading of YAML configuration files,
ensuring all parameters meet the constraints required by the reference core.
"""

from pathlib import Path
from typing import TypedDict, cast, List
import yaml


class SimulationConfig(TypedDict, total=False):
    """Expected structure of the 'simulation' section."""
    dt_ms: float
    max_delay: int


class ConfigDict(TypedDict, total=False):
    """Expected structure of the entire configuration dictionary."""
    dimensions: List[int]
    initial_neurons: int
    simulation: SimulationConfig


def load_config(path: str | Path) -> ConfigDict:
    """
    Load and validate the experiment configuration from a YAML file.

    Validation steps:
        - Root must be a YAML mapping.
        - 'dimensions': exactly five integers in [1, 256].
        - 'initial_neurons': positive integer not exceeding total positions.
        - 'simulation': must be a mapping.
        - 'dt_ms': must equal 1.0 (Sprint 1 requirement).
        - 'max_delay': must be >= 1.

    Returns:
        ConfigDict: Validated configuration.

    Raises:
        ValueError: On validation failure.
        FileNotFoundError: If the file does not exist.
        yaml.YAMLError: On YAML parse errors.
    """
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    # Ensure root is a dictionary (yaml.safe_load may return None)
    if not isinstance(raw, dict):
        raise ValueError("Configuration file must contain a YAML dictionary")

    # Inform type checker about the expected structure
    cfg = cast(ConfigDict, raw)

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