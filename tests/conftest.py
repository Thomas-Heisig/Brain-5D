import random


def base_config():
    return {
        "seed": 42,
        "dimensions": [5,5,5,5,5],
        "initial_neurons": 3,
        "max_neurons": 3125,
        "simulation": {"dt_ms": 1.0, "ticks": 20, "max_delay": 10, "debug_invariants": True},
        "neuron": {"a": .02, "b": .2, "c": -65.0, "d": 8.0},
        "network": {"initial_connections_per_neuron": 2, "neighbour_radius": 2.0, "weight_min": 0.0, "weight_max": .5},
        "energy": {"initial": 1.0, "spike_cost": .001, "affects_firing": False},
        "topology": {"input": {"dimension": "x", "coordinate": 0}, "output": {"dimension": "x", "coordinate": 4}, "allow_self_connections": False, "allow_parallel_connections": False},
        "diagnostics": {"mode": "single_pulse", "start_tick": 0, "duration_ticks": 1, "amplitude": 100.0, "target_coord": [1,1,1,1,1], "input_plane_dim": "x", "poisson_rate_hz": .5, "poisson_amplitude": 5.0},
        "telemetry": {"enabled": True, "history_ticks": 100, "spike_history_ticks": 100},
        "visualization": {"enabled": False, "refresh_interval_ticks": 20, "spike_raster_neurons": 250, "projection_4d": "d4", "activity_tau_ticks": 50.0},
        "logging": {"interval_ticks": 100},
    }
