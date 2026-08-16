"""Lazy mmap heatmap projection tests."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from src.core.spatial_index import pack_coords
from src.storage.b5d import B5DReader, B5DSnapshotWriter
from src.storage.lazy_view import B5DLazyProjector, StorageHeatmapKind


@dataclass(slots=True)
class FakeNeuron:
    a: float = 0.02
    b: float = 0.2
    c: float = -65.0
    d: float = 8.0
    v: float = -60.0
    u: float = -12.0
    energy: float = 0.5
    spike_cost: float = 0.001
    spike_counter: int = 0
    last_spike_tick: int = -1
    threshold_adaptation: float = 0.0


@dataclass(slots=True)
class FakeSynapse:
    target_id: int
    weight: float
    delay: int = 1
    eligibility: float = 0.0
    last_pre_spike: int = -1


@dataclass(slots=True)
class FakeNetwork:
    dimensions: tuple[int, int, int, int, int]
    current_tick: int
    neurons: dict[int, FakeNeuron]
    synapses: dict[int, list[FakeSynapse]]


def _write(path: Path) -> None:
    a = pack_coords(1, 2, 0, 0, 0)
    b = pack_coords(3, 1, 0, 0, 0)
    net = FakeNetwork(
        dimensions=(5, 5, 2, 2, 2),
        current_tick=10,
        neurons={
            a: FakeNeuron(energy=0.25, last_spike_tick=9),
            b: FakeNeuron(energy=0.75, last_spike_tick=5),
        },
        synapses={a: [FakeSynapse(b, 0.8)], b: []},
    )
    B5DSnapshotWriter().write(path, net)


def test_lazy_projector_shapes_and_finite_values(tmp_path: Path) -> None:
    path = tmp_path / "lazy.b5d"
    _write(path)
    with B5DReader(path) as reader:
        projector = B5DLazyProjector(reader, activity_tau_ticks=10.0)
        for kind in StorageHeatmapKind:
            heatmap = projector.build(kind)
            assert heatmap.values.shape == (5, 5)
            assert np.isfinite(heatmap.values).all()


def test_lazy_energy_projection_uses_xy_coordinates(tmp_path: Path) -> None:
    path = tmp_path / "energy.b5d"
    _write(path)
    with B5DReader(path) as reader:
        heatmap = B5DLazyProjector(reader).build(StorageHeatmapKind.ENERGY)
    assert heatmap.values[2, 1] > 0.0
    assert heatmap.values[1, 3] > heatmap.values[2, 1]
