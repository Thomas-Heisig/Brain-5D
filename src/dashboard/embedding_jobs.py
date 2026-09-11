"""Versioned, provenance-bound embedding and cluster analysis jobs."""

from __future__ import annotations

import csv
import hashlib
import importlib
import importlib.metadata
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

import numpy as np

from src.core.spatial_index import unpack_coords
from src.dashboard.verification import compute_source_tree_digest, current_git_head


class EmbeddingJobError(ValueError):
    """Raised when an analysis job cannot be validated or executed."""


METHODS = {"tsne", "umap", "cluster_export"}
MAX_POINTS = 2000


def _package_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "unavailable"


def _features(network: Any, max_points: int) -> tuple[list[int], np.ndarray]:
    items = sorted(network.neurons.items())
    if not items:
        raise EmbeddingJobError("The live network contains no neurons.")
    if len(items) > max_points:
        indices = np.linspace(0, len(items) - 1, max_points, dtype=int)
        items = [items[int(index)] for index in indices]
    neuron_ids: list[int] = []
    rows: list[list[float]] = []
    for neuron_id, neuron in items:
        coordinates = unpack_coords(int(neuron_id))
        neuron_ids.append(int(neuron_id))
        rows.append(
            [
                *[float(value) for value in coordinates],
                float(getattr(neuron, "v", 0.0)),
                float(getattr(neuron, "u", 0.0)),
                float(getattr(neuron, "energy", 0.0)),
                float(getattr(neuron, "spike_counter", 0)),
            ]
        )
    return neuron_ids, np.asarray(rows, dtype=np.float64)


def _input_digest(neuron_ids: list[int], features: np.ndarray) -> str:
    payload = json.dumps(
        {"neuron_ids": neuron_ids, "features": features.tolist()},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _write_csv(path: Path, rows: list[dict[str, Any]], method: str) -> None:
    fields = [
        "neuron_id",
        "method",
        "x",
        "y",
        "cluster",
        "d1",
        "d2",
        "d3",
        "d4",
        "d5",
        "v",
        "u",
        "energy",
        "spike_counter",
        "io_role",
    ]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def run_embedding_job(
    repo_root: Path,
    network: Any,
    *,
    method: str,
    random_state: int = 42,
    max_points: int = MAX_POINTS,
    perplexity: float = 30.0,
    n_neighbors: int = 15,
    n_clusters: int = 5,
) -> dict[str, Any]:
    """Execute one bounded analysis job and persist its provenance-bound output."""
    if method not in METHODS:
        raise EmbeddingJobError(f"Unknown analysis method: {method}")
    if not 2 <= max_points <= MAX_POINTS:
        raise EmbeddingJobError(f"max_points must be between 2 and {MAX_POINTS}")
    if random_state < 0:
        raise EmbeddingJobError("random_state must be non-negative")

    neuron_ids, features = _features(network, max_points)
    if len(neuron_ids) < 3:
        raise EmbeddingJobError("At least three neurons are required for analysis.")
    input_digest = _input_digest(neuron_ids, features)
    parameters: dict[str, Any] = {
        "method": method,
        "random_state": random_state,
        "max_points": max_points,
        "perplexity": perplexity,
        "n_neighbors": n_neighbors,
        "n_clusters": n_clusters,
    }
    started = datetime.now(timezone.utc)
    clusters: list[int | None]
    if method == "tsne":
        if perplexity <= 0 or perplexity >= len(neuron_ids):
            raise EmbeddingJobError(
                "perplexity must be greater than 0 and below the point count"
            )
        try:
            tsne_class = importlib.import_module("sklearn.manifold").TSNE
        except ImportError as exc:
            raise EmbeddingJobError(
                "t-SNE requires the optional analysis dependencies"
            ) from exc
        transformed = np.asarray(
            tsne_class(
                n_components=2,
                perplexity=perplexity,
                init="pca",
                learning_rate="auto",
                random_state=random_state,
                max_iter=750,
            ).fit_transform(features),
            dtype=np.float64,
        )
        clusters = [None] * len(neuron_ids)
        algorithm_version = _package_version("scikit-learn")
    elif method == "umap":
        if n_neighbors < 2 or n_neighbors >= len(neuron_ids):
            raise EmbeddingJobError("n_neighbors must be between 2 and the point count")
        try:
            umap_class = importlib.import_module("umap").UMAP
        except ImportError as exc:
            raise EmbeddingJobError(
                "UMAP requires the optional analysis dependencies"
            ) from exc
        transformed = np.asarray(
            umap_class(
                n_components=2,
                n_neighbors=n_neighbors,
                random_state=random_state,
                transform_seed=random_state,
            ).fit_transform(features),
            dtype=np.float64,
        )
        clusters = [None] * len(neuron_ids)
        algorithm_version = _package_version("umap-learn")
    else:
        if n_clusters < 2 or n_clusters > len(neuron_ids):
            raise EmbeddingJobError("n_clusters must be between 2 and the point count")
        try:
            kmeans_class = importlib.import_module("sklearn.cluster").KMeans
        except ImportError as exc:
            raise EmbeddingJobError(
                "Cluster export requires the optional analysis dependencies"
            ) from exc
        model = kmeans_class(
            n_clusters=n_clusters, n_init=10, random_state=random_state
        )
        clusters = [int(value) for value in model.fit_predict(features)]
        transformed = features[:, :2]
        algorithm_version = _package_version("scikit-learn")

    input_cells = set(getattr(network, "input_cells", set()))
    output_cells = set(getattr(network, "output_cells", set()))
    rows: list[dict[str, Any]] = []
    for index, neuron_id in enumerate(neuron_ids):
        feature = features[index]
        is_input = neuron_id in input_cells
        is_output = neuron_id in output_cells
        if is_input and is_output:
            io_role = "input_output"
        elif is_input:
            io_role = "input"
        elif is_output:
            io_role = "output"
        else:
            io_role = "internal"
        rows.append(
            {
                "neuron_id": neuron_id,
                "method": method,
                "x": float(transformed[index, 0]),
                "y": float(transformed[index, 1]),
                "cluster": clusters[index],
                "d1": float(feature[0]),
                "d2": float(feature[1]),
                "d3": float(feature[2]),
                "d4": float(feature[3]),
                "d5": float(feature[4]),
                "v": float(feature[5]),
                "u": float(feature[6]),
                "energy": float(feature[7]),
                "spike_counter": int(feature[8]),
                "io_role": io_role,
            }
        )
    output_root = repo_root / "research" / "generated" / "analysis_jobs"
    output_root.mkdir(parents=True, exist_ok=True)
    job_id = f"{started.strftime('%Y%m%dT%H%M%S%fZ')}-{method}"
    json_path = output_root / f"{job_id}.json"
    csv_path = output_root / f"{job_id}.csv"
    job = {
        "schema_version": "1.0",
        "job_id": job_id,
        "status": "completed",
        "created_at": started.isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "method": method,
        "algorithm": {"name": method, "version": algorithm_version},
        "parameters": parameters,
        "input": {
            "source": "live_runtime",
            "neuron_count": len(neuron_ids),
            "input_digest": input_digest,
            "network_tick": int(getattr(network, "current_tick", 0)),
            "feature_columns": [
                "D1",
                "D2",
                "D3",
                "D4",
                "D5",
                "v",
                "u",
                "energy",
                "spike_counter",
            ],
            "input_neuron_count": sum(
                1 for neuron_id in neuron_ids if neuron_id in input_cells
            ),
            "output_neuron_count": sum(
                1 for neuron_id in neuron_ids if neuron_id in output_cells
            ),
        },
        "provenance": {
            "git_commit": current_git_head(repo_root),
            "source_tree_digest": compute_source_tree_digest(repo_root),
            "binary_values_byte_exact": True,
            "scientific_evidence": False,
            "human_review_required": True,
        },
        "artifacts": {
            "json": f"generated/analysis_jobs/{json_path.name}",
            "csv": f"generated/analysis_jobs/{csv_path.name}",
        },
        "rows": rows,
    }
    json_path.write_text(
        json.dumps(job, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    _write_csv(csv_path, rows, method)
    return job


def list_embedding_jobs(repo_root: Path) -> list[dict[str, Any]]:
    """List persisted analysis jobs newest first without loading row payloads."""
    directory = repo_root / "research" / "generated" / "analysis_jobs"
    if not directory.is_dir():
        return []
    jobs: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json"), reverse=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict):
            typed_data = cast(dict[str, Any], data)
            jobs.append(
                {key: value for key, value in typed_data.items() if key != "rows"}
            )
    return jobs
