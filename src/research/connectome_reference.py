"""Bounded, opt-in sparse graph import and explicit synthetic controls.

This adapter imports an already selected local JSON subset. It never downloads
large datasets, changes canonical SNN state, or infers anatomy from a layout.
Edge weights must have a declared model interpretation; contacts are not silently
converted to conductances. Biological source validation remains a separate task.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, cast


@dataclass(frozen=True)
class ReferenceEdge:
    source: str
    target: str
    weight: float
    delay_ticks: int


@dataclass(frozen=True)
class ReferenceGraph:
    node_ids: tuple[str, ...]
    edges: tuple[ReferenceEdge, ...]
    provenance: dict[str, Any]

    def digest(self) -> str:
        payload = json.dumps(asdict(self), sort_keys=True, allow_nan=False)
        return hashlib.sha256(payload.encode()).hexdigest()

    def degrees(self) -> dict[str, tuple[int, int]]:
        incoming = dict.fromkeys(self.node_ids, 0)
        outgoing = dict.fromkeys(self.node_ids, 0)
        for edge in self.edges:
            outgoing[edge.source] += 1
            incoming[edge.target] += 1
        return {node: (incoming[node], outgoing[node]) for node in self.node_ids}

    def fingerprint(self) -> dict[str, Any]:
        pairs = {(edge.source, edge.target) for edge in self.edges}
        reciprocal = sum((target, source) in pairs for source, target in pairs)
        return {
            "node_count": len(self.node_ids),
            "edge_count": len(self.edges),
            "degree_by_original_id": self.degrees(),
            "reciprocal_edge_fraction": reciprocal / len(pairs) if pairs else 0.0,
            "graph_sha256": self.digest(),
            "data_kind": self.provenance["data_kind"],
        }


def load_reference(
    path: Path,
    *,
    expected_sha256: str,
    max_bytes: int = 8_000_000,
    max_nodes: int = 10_000,
    max_edges: int = 100_000,
) -> ReferenceGraph:
    """Validate bytes and schema before returning an inert reference graph."""
    if min(max_bytes, max_nodes, max_edges) < 1:
        raise ValueError("Reference budgets must be positive")
    with path.open("rb") as stream:
        payload = stream.read(max_bytes + 1)
    if len(payload) > max_bytes:
        raise ValueError("Reference exceeds byte budget")
    if hashlib.sha256(payload).hexdigest() != expected_sha256:
        raise ValueError("Reference artifact hash mismatch")
    raw = json.loads(payload)
    if not isinstance(raw, dict):
        raise ValueError("Reference root must be an object")
    raw = cast(dict[str, Any], raw)
    if raw.get("schema_version") != "1.0":
        raise ValueError("Unsupported reference schema")
    provenance = raw.get("provenance")
    required = (
        "source_id",
        "source_url",
        "dataset_version",
        "license",
        "retrieved_on",
        "selection_rule",
        "transformations",
        "neuron_model",
        "weight_interpretation",
        "delay_interpretation",
        "transmitter_uncertainty",
        "adapter_version",
    )
    if not isinstance(provenance, dict):
        raise ValueError("Reference provenance must be an object")
    provenance = cast(dict[str, Any], provenance)
    if any(
        not isinstance(provenance.get(key), str) or not provenance[key].strip()
        for key in required
    ):
        raise ValueError("Reference provenance is incomplete")
    if provenance.get("data_kind") not in {"SYNTHETIC", "BIOLOGICAL_REFERENCE"}:
        raise ValueError("Reference data kind must be explicit")
    nodes = raw.get("node_ids")
    if not isinstance(nodes, list):
        raise ValueError("Node IDs must be a list")
    nodes = cast(list[Any], nodes)
    if (
        not 1 <= len(nodes) <= max_nodes
        or any(not isinstance(node, str) or not node for node in nodes)
        or len(set(nodes)) != len(nodes)
    ):
        raise ValueError("Invalid, duplicate or excessive original node IDs")
    edge_values = raw.get("edges")
    if not isinstance(edge_values, list):
        raise ValueError("Edge records must be a list")
    edge_values = cast(list[Any], edge_values)
    if len(edge_values) > max_edges:
        raise ValueError("Invalid or excessive edge list")
    edges: list[ReferenceEdge] = []
    pairs: set[tuple[str, str]] = set()
    node_set = set(nodes)
    for record in edge_values:
        if not isinstance(record, dict):
            raise ValueError("Malformed edge")
        record = cast(dict[str, Any], record)
        source, target = record.get("source"), record.get("target")
        weight, delay = record.get("weight"), record.get("delay_ticks")
        if not isinstance(source, str) or not isinstance(target, str):
            raise ValueError("Edge IDs must be strings")
        if source not in node_set or target not in node_set or source == target:
            raise ValueError("Unknown edge endpoint or self edge")
        if (source, target) in pairs:
            raise ValueError("Duplicate edge; aggregate only with declared provenance")
        if isinstance(weight, bool) or not isinstance(weight, (float, int)):
            raise ValueError("Weight must be numeric")
        if not math.isfinite(weight) or abs(weight) > 200:
            raise ValueError("Weight exceeds experimental model bounds")
        if (
            isinstance(delay, bool)
            or not isinstance(delay, int)
            or not 1 <= delay <= 20
        ):
            raise ValueError("Delay must be integer ticks in [1,20]")
        pairs.add((source, target))
        edges.append(ReferenceEdge(source, target, float(weight), delay))
    return ReferenceGraph(
        tuple(nodes), tuple(edges), dict(provenance, artifact_sha256=expected_sha256)
    )


def synthetic_graph(seed: int) -> ReferenceGraph:
    """Six-neuron test graph; NOT a Drosophila reconstruction or anatomical motif."""
    rng = random.Random(seed)
    pairs = (
        (0, 2, 100.0),
        (2, 4, 90.0),
        (4, 2, 10.0),
        (1, 3, 100.0),
        (3, 5, 90.0),
        (5, 3, 10.0),
    )
    edges = tuple(
        ReferenceEdge(str(source), str(target), weight + rng.uniform(-2, 2), 1)
        for source, target, weight in pairs
    )
    return ReferenceGraph(
        tuple(map(str, range(6))),
        edges,
        {
            "data_kind": "SYNTHETIC",
            "source_id": "MHRN-SYNTHETIC-JOINT-V1",
            "dataset_version": "1.0",
            "seed": seed,
            "neuron_model": "Izhikevich RS",
            "weight_interpretation": "model current, not anatomical contact count",
            "delay_interpretation": "integer neural ticks of 1 ms",
        },
    )


def transform_graph(graph: ReferenceGraph, condition: str, seed: int) -> ReferenceGraph:
    """Return a declared control with node/edge/weight/delay budgets preserved."""
    if condition == "structured":
        return graph
    rng = random.Random(seed ^ 0xC0AA)
    edges = list(graph.edges)
    swaps = 0
    if condition == "weight_shuffle":
        weights = [edge.weight for edge in edges]
        rng.shuffle(weights)
        edges = [
            ReferenceEdge(e.source, e.target, w, e.delay_ticks)
            for e, w in zip(edges, weights)
        ]
    elif condition == "random_edges":
        # Bounded rejection sampling; no dense N x N allocation.
        pairs: set[tuple[str, str]] = set()
        for _ in range(max(100, len(edges) * 100)):
            if len(pairs) == len(edges):
                break
            source, target = rng.sample(graph.node_ids, 2)
            pairs.add((source, target))
        if len(pairs) != len(edges):
            raise ValueError("Random edge sampler exhausted its bounded budget")
        edges = [
            ReferenceEdge(a, b, edge.weight, edge.delay_ticks)
            for (a, b), edge in zip(sorted(pairs), edges)
        ]
    elif condition == "degree_preserving":
        original_pairs = {(edge.source, edge.target) for edge in edges}
        pairs = set(original_pairs)
        for _ in range(max(100, len(edges) * 20)):
            if len(edges) < 2:
                break
            i, j = rng.sample(range(len(edges)), 2)
            a, b = edges[i], edges[j]
            proposed = {(a.source, b.target), (b.source, a.target)}
            old = {(a.source, a.target), (b.source, b.target)}
            if (
                len(proposed) != 2
                or proposed == old
                or any(x == y for x, y in proposed)
                or proposed & (pairs - old)
            ):
                continue
            pairs = (pairs - old) | proposed
            edges[i] = ReferenceEdge(a.source, b.target, a.weight, a.delay_ticks)
            edges[j] = ReferenceEdge(b.source, a.target, b.weight, b.delay_ticks)
            swaps += 1
            if swaps >= len(edges) and pairs != original_pairs:
                break
        if pairs == original_pairs:
            raise ValueError("No nontrivial degree-preserving control was produced")
    else:
        raise ValueError(f"Unknown graph treatment: {condition}")
    return ReferenceGraph(
        graph.node_ids,
        tuple(edges),
        dict(
            graph.provenance,
            treatment=condition,
            transformation_seed=seed,
            accepted_swaps=swaps,
            parent_graph_sha256=graph.digest(),
        ),
    )
