"""Journal-backed structural activity heatmaps."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from numpy.typing import NDArray

from src.storage.structural_journal import StructuralChangeKind, StructuralChangeRecord

StructuralHeatmapKind = Literal[
    "neuron_additions",
    "neuron_removals",
    "synapse_additions",
    "synapse_removals",
    "total_structural_activity",
]


@dataclass(frozen=True, slots=True)
class StructuralHeatmapResult:
    kind: StructuralHeatmapKind
    values: NDArray[np.float64]
    min_value: float
    max_value: float
    populated_cells: int
    sequence_from: int
    sequence_to: int


class StructuralHeatmapSource:
    def __init__(self, dimensions: tuple[int, int, int, int, int]) -> None:
        self.dimensions = dimensions

    def build(
        self, records: tuple[StructuralChangeRecord, ...], kind: StructuralHeatmapKind
    ) -> StructuralHeatmapResult:
        values = np.zeros((self.dimensions[0], self.dimensions[1]), dtype=np.float64)
        wanted = {
            "neuron_additions": {StructuralChangeKind.NEURON_ADD},
            "neuron_removals": {StructuralChangeKind.NEURON_REMOVE},
            "synapse_additions": {StructuralChangeKind.SYNAPSE_ADD},
            "synapse_removals": {StructuralChangeKind.SYNAPSE_REMOVE},
            "total_structural_activity": set(StructuralChangeKind),
        }[kind]
        used_sequences: list[int] = []
        for record in records:
            if record.kind not in wanted or record.coord is None:
                continue
            x, y, _, _, _ = record.coord
            if 0 <= x < values.shape[0] and 0 <= y < values.shape[1]:
                values[x, y] += 1.0
                used_sequences.append(record.sequence)
        populated = int(np.count_nonzero(values))
        return StructuralHeatmapResult(
            kind=kind,
            values=values,
            min_value=float(np.min(values)) if values.size else 0.0,
            max_value=float(np.max(values)) if values.size else 0.0,
            populated_cells=populated,
            sequence_from=min(used_sequences) if used_sequences else 0,
            sequence_to=max(used_sequences) if used_sequences else 0,
        )
