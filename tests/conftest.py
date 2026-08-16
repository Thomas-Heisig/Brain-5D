from typing import TypedDict, List, Dict, Union


# Lokale Typdefinition für die Testkonfiguration
class SimulationConfig(TypedDict, total=False):
    dt_ms: float
    ticks: int
    max_delay: int
    debug_invariants: bool


class NeuronConfig(TypedDict, total=False):
    a: float
    b: float
    c: float
    d: float


class NetworkConfig(TypedDict, total=False):
    initial_connections_per_neuron: int
    neighbour_radius: float
    weight_min: float
    weight_max: float


class EnergyConfig(TypedDict, total=False):
    initial: float
    spike_cost: float
    affects_firing: bool


class TopologyConfig(TypedDict, total=False):
    input: Dict[str, Union[str, int]]
    output: Dict[str, Union[str, int]]
    allow_self_connections: bool
    allow_parallel_connections: bool


class DiagnosticsConfig(TypedDict, total=False):
    mode: str
    start_tick: int
    duration_ticks: int
    amplitude: float
    target_coord: List[int]
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


class TestConfig(TypedDict, total=False):
    seed: int
    dimensions: List[int]
    initial_neurons: int
    max_neurons: int
    simulation: SimulationConfig
    neuron: NeuronConfig
    network: NetworkConfig
    energy: EnergyConfig
    topology: TopologyConfig
    diagnostics: DiagnosticsConfig
    telemetry: TelemetryConfig
    visualization: VisualizationConfig
    logging: LoggingConfig


def base_config() -> TestConfig:
    return {
        "seed": 42,
        "dimensions": [5, 5, 5, 5, 5],
        "initial_neurons": 3,
        "max_neurons": 3125,
        "simulation": {
            "dt_ms": 1.0,
            "ticks": 20,
            "max_delay": 10,
            "debug_invariants": True,
        },
        "neuron": {"a": 0.02, "b": 0.2, "c": -65.0, "d": 8.0},
        "network": {
            "initial_connections_per_neuron": 2,
            "neighbour_radius": 2.0,
            "weight_min": 0.0,
            "weight_max": 0.5,
        },
        "energy": {"initial": 1.0, "spike_cost": 0.001, "affects_firing": False},
        "topology": {
            "input": {"dimension": "x", "coordinate": 0},
            "output": {"dimension": "x", "coordinate": 4},
            "allow_self_connections": False,
            "allow_parallel_connections": False,
        },
        "diagnostics": {
            "mode": "single_pulse",
            "start_tick": 0,
            "duration_ticks": 1,
            "amplitude": 100.0,
            "target_coord": [1, 1, 1, 1, 1],
            "input_plane_dim": "x",
            "poisson_rate_hz": 0.5,
            "poisson_amplitude": 5.0,
        },
        "telemetry": {
            "enabled": True,
            "history_ticks": 100,
            "spike_history_ticks": 100,
        },
        "visualization": {
            "enabled": False,
            "refresh_interval_ticks": 20,
            "spike_raster_neurons": 250,
            "projection_4d": "d4",
            "activity_tau_ticks": 50.0,
        },
        "logging": {"interval_ticks": 100},
    }
