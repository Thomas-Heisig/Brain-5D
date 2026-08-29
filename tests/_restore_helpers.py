"""Shared helpers for restore determinism A/B/C protocol (Alpha.5).

Provides deterministic state capture and schedule building that both the
pytest test and the C2 restore worker use, ensuring a single canonical
digest implementation across all paths.
"""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path
from typing import Any

from src.core.network import Brain5DConfig, NeuralNetwork
from src.core.spatial_index import linear_to_5d
from src.homeostasis.engine import HomeostasisEngine
from src.learning.learning_engine import LearningEngine
from src.research.canonical_state import canonical_state_digest


# ============================================================================
# Configuration
# ============================================================================


SEED: int = 42
K: int = 500
N: int = 1000


def make_config() -> dict[str, Any]:
    return {
        "seed": SEED,
        "dimensions": [5, 5, 1, 1, 1],
        "initial_neurons": 25,
        "simulation": {"dt_ms": 1.0, "max_delay": 5, "debug_invariants": True},
        "network": {
            "initial_connections_per_neuron": 3,
            "neighbour_radius": 2.0,
            "weight_min": 0.0,
            "weight_max": 0.5,
        },
        "neuron": {"a": 0.02, "b": 0.2, "c": -65.0, "d": 8.0},
        "energy": {"initial": 1.0, "spike_cost": 0.001},
        "topology": {
            "input": {"dimension": "x", "coordinate": 0},
            "output": {"dimension": "x", "coordinate": 4},
        },
        "homeostasis": {
            "enabled": True,
            "target_rate_hz": 5.0,
            "rate_tau_ticks": 200.0,
        },
        "stdp": {
            "enabled": True, "a_plus": 0.1, "a_minus": 0.12,
            "tau_plus": 20.0, "tau_minus": 20.0,
        },
        "eligibility": {"enabled": True, "tau_ticks": 200.0},
        "reward": {"enabled": True, "learning_rate": 0.01, "delay_ticks": 5},
    }


def config_sha256(config: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(config, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()


# ============================================================================
# Network creation and schedule
# ============================================================================


def create_network(config: dict[str, Any]) -> NeuralNetwork:
    rng = random.Random(config["seed"])
    b5d_config = Brain5DConfig.from_dict(config)
    net = NeuralNetwork(b5d_config, rng)
    dims = config["dimensions"]
    for i in range(config.get("initial_neurons", 30)):
        net.add_neuron(linear_to_5d(i, tuple(dims)))
    net.set_input_output_cells("x", 0, "x", dims[0] - 1)
    net.initialize_random_connections(3, 2.0)
    return net


def build_absolute_schedule(config: dict[str, Any], total_ticks: int) -> list[dict[str, Any]]:
    network = create_network(config)
    stim_ids = tuple(sorted(network.neurons))[:3]
    schedule: list[dict[str, Any]] = []
    for tick in range(total_ticks):
        if tick % 50 == 0:
            schedule.append({
                "tick": tick,
                "neuron_ids": list(stim_ids),
                "current": 30.0,
            })
    return schedule


def run_absolute_schedule(network: NeuralNetwork, schedule: list[dict[str, Any]], end_tick: int) -> None:
    stim_map: dict[int, list[tuple[int, float]]] = {}
    for entry in schedule:
        t = int(entry["tick"])
        if t < end_tick:
            stim_map[t] = [(nid, float(entry["current"])) for nid in entry["neuron_ids"]]
    while network.current_tick < end_tick:
        tick = network.current_tick
        if tick in stim_map:
            for nid, curr in stim_map[tick]:
                network.inject_current(nid, curr)
        network.step()


# ============================================================================
# Canonical digest adapter — single implementation for A, B, C
# ============================================================================


def capture_learning_state(learn: LearningEngine) -> dict[str, Any]:
    """Capture learning engine state in the format expected by canonical_state_digest."""
    states_list: list[dict[str, Any]] = []
    for key in sorted(learn._states.keys()):
        state = learn._states[key]
        states_list.append({
            "pre_id": key[0],
            "target_id": key[1],
            "last_pre_tick": state.last_pre_tick,
            "last_post_tick": state.last_post_tick,
            "eligibility_value": state.eligibility.value,
            "eligibility_last_tick": state.eligibility.last_tick,
        })
    pending = [
        {"value": r.value, "tick": r.tick}
        for r in learn._pending_rewards
    ]
    return {
        "states": states_list,
        "pending_rewards": pending,
    }


def compute_digest(
    network: NeuralNetwork,
    homeostasis: HomeostasisEngine | None = None,
    learning: LearningEngine | None = None,
    *,
    config_sha256_str: str = "",
    brain5d_version: str = "",
) -> str:
    """Compute the canonical full-state digest using the production implementation.

    This is the SINGLE digest function for all A/B/C paths.
    """
    homeo_rates: dict[int, float] | None = None
    if homeostasis is not None and hasattr(homeostasis, "_rates_hz"):
        homeo_rates = dict(homeostasis._rates_hz)

    learn_state: dict[str, Any] | None = None
    if learning is not None:
        learn_state = capture_learning_state(learning)

    return canonical_state_digest(
        network,
        config_sha256=config_sha256_str,
        brain5d_version=brain5d_version,
        homeostasis_rates=homeo_rates,
        learning_state=learn_state,
    )
