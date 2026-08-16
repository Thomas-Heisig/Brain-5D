from collections import deque


class TopologyHealth:
    def __init__(self, network):
        self.net = network

    def analyze(self) -> dict:
        n = self.net
        neurons = set(n.neurons)
        in_vals_map = {nid: n.in_degree.get(nid, 0) for nid in neurons}
        out_vals_map = {nid: len(n.synapses.get(nid, [])) for nid in neurons}
        in_vals = list(in_vals_map.values()); out_vals = list(out_vals_map.values())
        reachable = False; shortest = None
        if n.input_cells and n.output_cells:
            q = deque((nid, 0) for nid in n.input_cells)
            visited = set(n.input_cells)
            while q:
                node, depth = q.popleft()
                if node in n.output_cells:
                    reachable = True; shortest = depth; break
                for syn in n.synapses.get(node, []):
                    if syn.target_id not in visited:
                        visited.add(syn.target_id); q.append((syn.target_id, depth + 1))
        return {
            "neurons": len(neurons), "synapses": n.synapse_count,
            "mean_in_degree": sum(in_vals) / len(in_vals) if in_vals else 0,
            "min_in_degree": min(in_vals) if in_vals else 0, "max_in_degree": max(in_vals) if in_vals else 0,
            "mean_out_degree": sum(out_vals) / len(out_vals) if out_vals else 0,
            "min_out_degree": min(out_vals) if out_vals else 0, "max_out_degree": max(out_vals) if out_vals else 0,
            "zero_incoming": sum(v == 0 for v in in_vals), "zero_outgoing": sum(v == 0 for v in out_vals),
            "isolated": sum(in_vals_map[nid] == 0 and out_vals_map[nid] == 0 for nid in neurons),
            "input_cells": len(n.input_cells), "output_cells": len(n.output_cells),
            "input_output_reachable": reachable, "shortest_path_length": shortest,
        }
