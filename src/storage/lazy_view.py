"""Lazy mmap-backed projections for `.b5d` snapshots without a live network."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

import numpy as np
import numpy.typing as npt

from src.core.spatial_index import unpack_coords

from .b5d import B5DReader

FloatMatrix = npt.NDArray[np.float64]


class StorageHeatmapKind(StrEnum):
    """Heatmap projections available directly from persistent snapshots."""

    ACTIVITY = "activity"
    WEIGHTS = "weights"
    ENERGY = "energy"


@dataclass(frozen=True, slots=True)
class StorageHeatmap:
    """One X-Y projection calculated from a memory-mapped snapshot."""

    kind: StorageHeatmapKind
    values: FloatMatrix
    snapshot_tick: int
    samples: int


class B5DLazyProjector:
    """Build X-Y projections by streaming records from :class:`B5DReader`."""

    def __init__(self, reader: B5DReader, activity_tau_ticks: float = 50.0) -> None:
        if activity_tau_ticks <= 0:
            raise ValueError("activity_tau_ticks must be positive")
        self.reader = reader
        self.activity_tau_ticks = float(activity_tau_ticks)
        self._shape = (reader.header.dimensions[1], reader.header.dimensions[0])

    def build(self, kind: StorageHeatmapKind) -> StorageHeatmap:
        """Build one projection while keeping memory proportional to X*Y only."""
        if kind is StorageHeatmapKind.ACTIVITY:
            return self._activity()
        if kind is StorageHeatmapKind.WEIGHTS:
            return self._weights()
        if kind is StorageHeatmapKind.ENERGY:
            return self._energy()
        raise ValueError(f"unsupported storage heatmap kind: {kind}")

    def _activity(self) -> StorageHeatmap:
        sums = np.zeros(self._shape, dtype=np.float64)
        counts = np.zeros(self._shape, dtype=np.int64)
        tick = self.reader.header.snapshot_tick
        samples = 0
        for neuron in self.reader.iter_neurons():
            x_coord, y_coord, _, _, _ = unpack_coords(neuron.neuron_id)
            if neuron.last_spike_tick is None or neuron.last_spike_tick < 0:
                value = 0.0
            else:
                age = max(0, tick - neuron.last_spike_tick)
                value = float(np.exp(-age / self.activity_tau_ticks))
            sums[y_coord, x_coord] += value
            counts[y_coord, x_coord] += 1
            samples += 1
        return StorageHeatmap(
            StorageHeatmapKind.ACTIVITY,
            _safe_mean(sums, counts),
            tick,
            samples,
        )

    def _energy(self) -> StorageHeatmap:
        sums = np.zeros(self._shape, dtype=np.float64)
        counts = np.zeros(self._shape, dtype=np.int64)
        samples = 0
        for neuron in self.reader.iter_neurons():
            x_coord, y_coord, _, _, _ = unpack_coords(neuron.neuron_id)
            sums[y_coord, x_coord] += neuron.optical.energy
            counts[y_coord, x_coord] += 1
            samples += 1
        return StorageHeatmap(
            StorageHeatmapKind.ENERGY,
            _safe_mean(sums, counts),
            self.reader.header.snapshot_tick,
            samples,
        )

    def _weights(self) -> StorageHeatmap:
        sums = np.zeros(self._shape, dtype=np.float64)
        counts = np.zeros(self._shape, dtype=np.int64)
        coordinates: dict[int, tuple[int, int]] = {}
        for neuron in self.reader.iter_neurons():
            x_coord, y_coord, _, _, _ = unpack_coords(neuron.neuron_id)
            coordinates[neuron.neuron_id] = (x_coord, y_coord)
        samples = 0
        for synapse in self.reader.iter_synapses():
            coordinate = coordinates.get(synapse.target_id)
            if coordinate is None:
                continue
            x_coord, y_coord = coordinate
            sums[y_coord, x_coord] += synapse.weight
            counts[y_coord, x_coord] += 1
            samples += 1
        return StorageHeatmap(
            StorageHeatmapKind.WEIGHTS,
            _safe_mean(sums, counts),
            self.reader.header.snapshot_tick,
            samples,
        )


def _safe_mean(sums: FloatMatrix, counts: npt.NDArray[np.int64]) -> FloatMatrix:
    result = np.zeros_like(sums, dtype=np.float64)
    np.divide(sums, counts, out=result, where=counts > 0)
    return result
