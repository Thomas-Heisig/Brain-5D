from __future__ import annotations

import argparse
import random
import statistics
from dataclasses import asdict
from pathlib import Path

from src.config.loader import load_config
from src.core.network import NeuralNetwork
from src.core.spatial_index import coords_to_linear, linear_to_5d, make_boundary_coord, unpack_coords
from src.diagnostics.propagation import PropagationAnalyzer
from src.diagnostics.stimulus import StimulusEngine
from src.diagnostics.topology_health import TopologyHealth
from src.telemetry.history import History
from src.telemetry.probes import ProbeManager
from src.telemetry.spike_history import SpikeHistory
from src.utils.run_artifacts import RunArtifacts


def sample_positions_excluding_poc(total: int, reserved: set[int], n: int, rng: random.Random) -> list[int]:
    available = [i for i in range(total) if i not in reserved]
    if n > len(available):
        raise ValueError("Not enough unreserved positions")
    return rng.sample(available, n)


def build_network(config: dict) -> tuple[NeuralNetwork, random.Random]:
    rng = random.Random(int(config["seed"]))
    network = NeuralNetwork(config, rng)
    dims = tuple(config["dimensions"])
    total = 1
    for d in dims: total *= d
    topology = config["topology"]
    input_coord = make_boundary_coord(dims, topology["input"]["dimension"], topology["input"]["coordinate"])
    output_coord = make_boundary_coord(dims, topology["output"]["dimension"], topology["output"]["coordinate"])
    diag_coord = tuple(config["diagnostics"]["target_coord"])
    reserved_coords = {input_coord, output_coord, diag_coord}
    reserved_indices = {coords_to_linear(c, dims) for c in reserved_coords}
    chosen = sample_positions_excluding_poc(total, reserved_indices, int(config["initial_neurons"]) - len(reserved_coords), rng)
    for idx in chosen:
        network.add_neuron(linear_to_5d(idx, dims))
    for coord in sorted(reserved_coords):
        network.add_neuron(coord)
    network.set_input_output_cells(
        topology["input"]["dimension"], topology["input"]["coordinate"],
        topology["output"]["dimension"], topology["output"]["coordinate"],
    )
    network.initialize_random_connections(int(config["network"]["initial_connections_per_neuron"]), float(config["network"]["neighbour_radius"]))
    return network, rng


def main() -> int:
    parser = argparse.ArgumentParser(description="Brain 5D Sprint 1C verified observable core")
    parser.add_argument("--config", default="configs/poc_config.yaml")
    parser.add_argument("--observe", action="store_true")
    parser.add_argument("--benchmark", action="store_true")
    args = parser.parse_args()
    config = load_config(args.config)
    if args.observe: config["visualization"]["enabled"] = True
    network, rng = build_network(config)
    health = TopologyHealth(network).analyze()
    stimulus = StimulusEngine(config, rng)
    history = History(int(config["telemetry"]["history_ticks"]))
    spike_history = SpikeHistory(int(config["telemetry"]["spike_history_ticks"]))
    probes = ProbeManager(network, config)
    propagation = PropagationAnalyzer(network.output_cells)
    diag_target = tuple(config["diagnostics"]["target_coord"])
    diag_id = next((nid for nid in network.neurons if unpack_coords(nid) == diag_target), None)
    if diag_id is not None: probes.add_probe(diag_id)
    obs = None
    if config["visualization"].get("enabled"):
        from src.visualization.observatory import Observatory
        obs = Observatory(network, config, spike_history, history, probes)
    core_times = []
    warmup = 100
    print("Brain 5D - Sprint 1C reference core")
    print(f"Neurons={len(network.neurons)} Synapses={network.synapse_count} Input={len(network.input_cells)} Output={len(network.output_cells)}")
    with RunArtifacts(config) as artifacts:
        artifacts.save_topology(health)
        for _ in range(int(config["simulation"]["ticks"])):
            stim = stimulus.apply(network, network.current_tick)
            result = network.step()
            history.append_from_stepresult(result)
            spike_history.append(result.tick, result.spike_ids)
            propagation.observe(stim, result)
            metric = history.get_all()[-1]
            artifacts.log_metrics(metric); artifacts.log_spikes(result.tick, result.spike_ids); artifacts.log_stimulus(stim)
            if args.benchmark and result.tick >= warmup: core_times.append(result.core_step_ms)
            if obs and (result.tick + 1) % int(config["visualization"]["refresh_interval_ticks"]) == 0: obs.draw()
            if (result.tick + 1) % int(config["logging"]["interval_ticks"]) == 0:
                print(f"Tick {result.tick+1:4d} | spikes={result.spikes_this_tick:4d} | total={result.total_spikes:6d} | queue={result.queued_events:5d} | {result.core_step_ms:.3f} ms")
        report = propagation.get_report()
        summary = {
            "seed": config["seed"], "ticks": config["simulation"]["ticks"],
            "final_neurons": len(network.neurons), "final_synapses": network.synapse_count,
            "total_spikes": network.total_spikes, "topology": health, "propagation": asdict(report),
        }
        if core_times:
            ordered = sorted(core_times); p95 = ordered[max(0, int(len(ordered)*0.95)-1)]
            summary["benchmark"] = {"mean_ms": statistics.mean(core_times), "median_ms": statistics.median(core_times), "p95_ms": p95}
            print("Benchmark:", summary["benchmark"])
        artifacts.save_summary(summary)
    print("Propagation:", report)
    if obs: obs.block_until_closed()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
