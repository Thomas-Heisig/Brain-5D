"""Shared fixtures and automatic test marker assignment for Brain-5D tests."""

from __future__ import annotations

from typing import TypedDict

import pytest


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
    input: dict[str, str | int]
    output: dict[str, str | int]
    allow_self_connections: bool
    allow_parallel_connections: bool


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


class TestConfig(TypedDict, total=False):
    seed: int
    dimensions: list[int]
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


# ============================================================================
# Automatic test marker assignment
# ============================================================================

_CATEGORY_MAP: dict[str, str] = {
    "test_artifacts": "core",
    "test_async_storage": "storage",
    "test_auto_approval": "plasticity",
    "test_b5d_storage": "storage",
    "test_brain5d_launcher": "core",
    "test_checkpoint": "storage",
    "test_compaction": "storage",
    "test_crc": "storage",
    "test_dashboard": "dashboard",
    "test_dashboard_alpha6": "dashboard",
    "test_dashboard_alpha7": "dashboard",
    "test_dashboard_compatibility_v050a2": "dashboard",
    "test_dashboard_control_service": "dashboard",
    "test_dashboard_homeostasis": "dashboard",
    "test_dashboard_single_instance": "dashboard",
    "test_delta_journal": "storage",
    "test_eligibility": "learning",
    "test_embodiment": "embodiment",
    "test_golden_chain": "integration",
    "test_heatmap": "dashboard",
    "test_homeostasis_engine": "homeostasis",
    "test_knowledge_contracts": "core",
    "test_language_organ_contracts": "core",
    "test_lazy_storage_view": "storage",
    "test_learning_experiment": "learning",
    "test_manipulator": "core",
    "test_network": "core",
    "test_network_hooks": "core",
    "test_neuron": "core",
    "test_observatory_data": "dashboard",
    "test_optical_codec": "storage",
    "test_recovery": "storage",
    "test_research_dashboard_routes": "dashboard",
    "test_restore_continue": "storage",
    "test_reward": "learning",
    "test_runtime_control": "core",
    "test_runtime_controller_alpha4": "core",
    "test_self_organization": "plasticity",
    "test_self_organization_alpha4": "plasticity",
    "test_self_organization_policy_alpha3": "plasticity",
    "test_signal_processing_contracts": "core",
    "test_spatial_index": "core",
    "test_stdp_integration": "plasticity",
    "test_stdp_isolated": "plasticity",
    "test_storage_runtime": "storage",
    "test_structural_coordinator_alpha5": "plasticity",
    "test_structural_dashboard_routes": "dashboard",
    "test_structural_heatmap": "dashboard",
    "test_structural_journal": "storage",
    "test_structural_operator_bridge": "dashboard",
    "test_structural_plasticity_journal": "plasticity",
    "test_structural_recovery": "storage",
    "test_structural_undo": "plasticity",
}

_SLOW: set[str] = {
    "test_b5d_storage",
    "test_delta_journal",
    "test_golden_chain",
    "test_restore_continue",
    "test_learning_experiment",
}


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Automatically assign markers to tests based on module filename."""
    for item in items:
        node_id = item.nodeid
        module_name = node_id.split("::")[0].split("/")[-1].replace(".py", "")

        # Category marker
        cat = _CATEGORY_MAP.get(module_name)
        if cat:
            item.add_marker(getattr(pytest.mark, cat))

        # Slow marker
        if module_name in _SLOW:
            item.add_marker(pytest.mark.slow)
