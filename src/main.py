"""Brain-5D command-line simulation entry point."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import random
import statistics
from typing import Any, cast

from src.config.loader import load_config
from src.core.network import NeuralNetwork
from src.core.spatial_index import (
    coords_to_linear,
    linear_to_5d,
    make_boundary_coord,
    unpack_coords,
)
from src.diagnostics.propagation import PropagationAnalyzer
from src.diagnostics.stimulus import StimulusEngine, StimulusResult
from src.diagnostics.topology_health import TopologyHealth
from src.homeostasis import HomeostasisEngine
from src.learning.learning_engine import LearningEngine
from src.telemetry.history import History
from src.telemetry.probes import ProbeManager
from src.telemetry.spike_history import SpikeHistory
from src.utils.run_artifacts import RunArtifacts


def sample_positions_excluding_poc(
    total: int,
    reserved: set[int],
    n: int,
    rng: random.Random,
) -> list[int]:
    """Sample free linear positions while preserving reserved PoC cells."""
    available = [index for index in range(total) if index not in reserved]
    if n > len(available):
        raise ValueError("Not enough unreserved positions")
    return rng.sample(available, n)


def build_network(config: dict[str, Any]) -> tuple[NeuralNetwork, random.Random]:
    """Build the deterministic sparse PoC network from configuration."""
    rng = random.Random(int(config["seed"]))
    network = NeuralNetwork(config, rng)  # type: ignore[arg-type]
    dims = tuple(config["dimensions"])
    total = 1
    for dimension in dims:
        total *= dimension
    topology = config["topology"]
    input_coord = make_boundary_coord(
        dims,
        topology["input"]["dimension"],
        topology["input"]["coordinate"],
    )
    output_coord = make_boundary_coord(
        dims,
        topology["output"]["dimension"],
        topology["output"]["coordinate"],
    )
    diag_coord = tuple(config["diagnostics"]["target_coord"])
    reserved_coords = {input_coord, output_coord, diag_coord}
    reserved_indices = {coords_to_linear(coord, dims) for coord in reserved_coords}
    chosen = sample_positions_excluding_poc(
        total,
        reserved_indices,
        int(config["initial_neurons"]) - len(reserved_coords),
        rng,
    )
    for index in chosen:
        network.add_neuron(linear_to_5d(index, dims))
    for coord in sorted(reserved_coords):
        network.add_neuron(coord)
    network.set_input_output_cells(
        topology["input"]["dimension"],
        topology["input"]["coordinate"],
        topology["output"]["dimension"],
        topology["output"]["coordinate"],
    )
    network.initialize_random_connections(
        int(config["network"]["initial_connections_per_neuron"]),
        float(config["network"]["neighbour_radius"]),
    )
    return network, rng


def main() -> int:
    """Run the configured Brain-5D simulation."""
    parser = argparse.ArgumentParser(
        description="Brain 5D v0.5 - homeostatic self-regulation"
    )
    parser.add_argument("--config", default="configs/poc_config.yaml")
    parser.add_argument("--observe", action="store_true")
    parser.add_argument("--benchmark", action="store_true")
    args = parser.parse_args()
    # Load config and treat as generic dict to simplify typing
    config = cast(dict[str, Any], load_config(args.config))
    if args.observe:
        config["visualization"]["enabled"] = True

    network, rng = build_network(config)
    learning = LearningEngine(network, config)  # type: ignore[arg-type]
    if learning.enabled:
        learning.attach()
    homeostasis = HomeostasisEngine(network, config)  # type: ignore[arg-type]
    if homeostasis.enabled:
        homeostasis.attach()

    # TopologyHealth.analyze() returns dict[str, Any]; cast for clarity.
    health: dict[str, Any] = cast(dict[str, Any], TopologyHealth(network).analyze())  # type: ignore[arg-type]
    stimulus = StimulusEngine(config, rng)
    history = History(int(config["telemetry"]["history_ticks"]))
    spike_history = SpikeHistory(int(config["telemetry"]["spike_history_ticks"]))
    probes = ProbeManager(network, config)
    propagation = PropagationAnalyzer(network.output_cells)
    diag_target = tuple(config["diagnostics"]["target_coord"])
    diag_id = next(
        (nid for nid in network.neurons if unpack_coords(nid) == diag_target),
        None,
    )
    if diag_id is not None:
        probes.add_probe(diag_id)

    observatory = None
    if config["visualization"].get("enabled"):
        from src.visualization.observatory import Observatory

        observatory = Observatory(network, config, spike_history, history, probes)

    core_times: list[float] = []
    warmup = 100
    print("Brain 5D - v0.5.0-alpha.1 homeostasis")
    print(
        f"Neurons={len(network.neurons)} Synapses={network.synapse_count} "
        f"Input={len(network.input_cells)} Output={len(network.output_cells)} "
        f"Learning={'on' if learning.enabled else 'off'} "
        f"Homeostasis={'on' if homeostasis.enabled else 'off'}"
    )

    with RunArtifacts(config) as artifacts:  # type: ignore[arg-type]
        artifacts.save_topology(health)  # type: ignore[arg-type]
        for _ in range(int(config["simulation"]["ticks"])):
            stim: StimulusResult = stimulus.apply(network, network.current_tick)  # type: ignore[arg-type]
            result = network.step()
            reward_cfg = config.get("reward", {})
            if (
                learning.params.reward_enabled
                and reward_cfg.get("reward_source", "external") == "output_spike"
                and result.output_spike_ids
            ):
                learning.set_reward(
                    float(reward_cfg.get("output_spike_value", 1.0)),
                    result.tick,
                )
            history.append_from_stepresult(result)  # type: ignore[arg-type]
            spike_history.append(result.tick, result.spike_ids)
            propagation.observe(stim, result)
            metric: dict[str, Any] = history.get_all()[-1]  # type: ignore[assignment]
            artifacts.log_metrics(metric)  # type: ignore[arg-type]
            artifacts.log_spikes(result.tick, result.spike_ids)
            artifacts.log_stimulus(stim)
            if args.benchmark and result.tick >= warmup:
                core_times.append(result.core_step_ms)
            if (
                observatory
                and (result.tick + 1)
                % int(config["visualization"]["refresh_interval_ticks"])
                == 0
            ):
                observatory.draw()
            if (result.tick + 1) % int(config["logging"]["interval_ticks"]) == 0:
                print(
                    f"Tick {result.tick + 1:4d} | spikes={result.spikes_this_tick:4d} "
                    f"| total={result.total_spikes:6d} "
                    f"| queue={result.queued_events:5d} "
                    f"| {result.core_step_ms:.3f} ms"
                )

        report = propagation.get_report()
        summary: dict[str, Any] = {
            "seed": config["seed"],
            "ticks": config["simulation"]["ticks"],
            "final_neurons": len(network.neurons),
            "final_synapses": network.synapse_count,
            "total_spikes": network.total_spikes,
            "topology": health,
            "propagation": asdict(report),
        }
        if learning.enabled:
            summary["learning"] = asdict(learning.stats)
        if homeostasis.enabled:
            summary["homeostasis"] = asdict(homeostasis.stats)
        if core_times:
            ordered = sorted(core_times)
            p95 = ordered[max(0, int(len(ordered) * 0.95) - 1)]
            summary["benchmark"] = {
                "mean_ms": statistics.mean(core_times),
                "median_ms": statistics.median(core_times),
                "p95_ms": p95,
            }
            print("Benchmark:", summary["benchmark"])
        artifacts.save_summary(summary)  # type: ignore[arg-type]

    print("Propagation:", report)
    if learning.enabled:
        print("Learning:", learning.stats)
    if homeostasis.enabled:
        print("Homeostasis:", homeostasis.stats)
    if observatory:
        observatory.block_until_closed()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
