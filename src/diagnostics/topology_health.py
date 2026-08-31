from __future__ import annotations

from collections import deque
from typing import Any

from src.core.network import NeuralNetwork


class TopologyHealth:
    """Analyze the topological health of a NeuralNetwork."""

    def __init__(self, network: NeuralNetwork) -> None:
        self.net = network

    def analyze(self) -> dict[str, Any]:
        n = self.net
        neuron_ids: set[int] = set(n.neurons.keys())
        in_vals_map: dict[int, int] = {
            nid: n.in_degree.get(nid, 0) for nid in neuron_ids
        }
        out_vals_map: dict[int, int] = {
            nid: len(n.synapses.get(nid, [])) for nid in neuron_ids
        }
        in_vals: list[int] = list(in_vals_map.values())
        out_vals: list[int] = list(out_vals_map.values())
        reachable = False
        shortest: int | None = None
        if n.input_cells and n.output_cells:
            q: deque[tuple[int, int]] = deque((nid, 0) for nid in n.input_cells)
            visited: set[int] = set(n.input_cells)
            while q:
                node, depth = q.popleft()
                if node in n.output_cells:
                    reachable = True
                    shortest = depth
                    break
                for syn in n.synapses.get(node, []):
                    syn_cast = syn  # already Synapse from type inference
                    if syn_cast.target_id not in visited:
                        visited.add(syn_cast.target_id)
                        q.append((syn_cast.target_id, depth + 1))
        return {
            "neurons": len(neuron_ids),
            "synapses": n.synapse_count,
            "mean_in_degree": sum(in_vals) / len(in_vals) if in_vals else 0,
            "min_in_degree": min(in_vals) if in_vals else 0,
            "max_in_degree": max(in_vals) if in_vals else 0,
            "mean_out_degree": sum(out_vals) / len(out_vals) if out_vals else 0,
            "min_out_degree": min(out_vals) if out_vals else 0,
            "max_out_degree": max(out_vals) if out_vals else 0,
            "zero_incoming": sum(v == 0 for v in in_vals),
            "zero_outgoing": sum(v == 0 for v in out_vals),
            "isolated": sum(
                in_vals_map[nid] == 0 and out_vals_map[nid] == 0 for nid in neuron_ids
            ),
            "input_cells": len(n.input_cells),
            "output_cells": len(n.output_cells),
            "input_output_reachable": reachable,
            "shortest_path_length": shortest,
        }
