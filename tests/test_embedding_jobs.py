"""Tests for provenance-bound embedding and cluster analysis jobs."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.dashboard.embedding_jobs import run_embedding_job


@pytest.fixture
def fake_network() -> SimpleNamespace:
    neurons = {
        index: SimpleNamespace(
            v=float(index),
            u=float(index) / 2,
            energy=1.0 + index,
            spike_counter=index,
        )
        for index in range(1, 9)
    }
    return SimpleNamespace(
        neurons=neurons,
        dimensions=(8, 1, 1, 1, 1),
        current_tick=12,
        input_cells={1},
        output_cells={8},
    )


@pytest.mark.parametrize("method", ["tsne", "umap", "cluster_export"])
def test_analysis_job_persists_method_and_provenance(
    tmp_path: Path, fake_network: SimpleNamespace, method: str
) -> None:
    if method == "umap":
        pytest.importorskip("umap")
    job = run_embedding_job(
        tmp_path,
        fake_network,
        method=method,
        max_points=8,
        perplexity=2,
        n_neighbors=2,
        n_clusters=2,
    )

    assert job["status"] == "completed"
    assert job["method"] == method
    assert job["input"]["neuron_count"] == 8
    assert job["provenance"]["scientific_evidence"] is False
    assert job["provenance"]["human_review_required"] is True
    assert job["input"]["feature_columns"] == [
        "D1", "D2", "D3", "D4", "D5", "v", "u", "energy", "spike_counter"
    ]
    assert job["rows"][0]["io_role"] == "input"
    assert job["rows"][-1]["io_role"] == "output"
    assert {"d1", "d2", "d3", "d4", "d5", "v", "u", "energy", "spike_counter"} <= set(job["rows"][0])
    json_path = tmp_path / "research" / job["artifacts"]["json"]
    csv_path = tmp_path / "research" / job["artifacts"]["csv"]
    assert json_path.is_file()
    assert csv_path.is_file()
    assert len(json.loads(json_path.read_text(encoding="utf-8"))["rows"]) == 8
