"""Headless-testable 5D-to-2D heatmap projection for Brain 5D."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

import numpy as np
import numpy.typing as npt
from matplotlib.axes import Axes
from matplotlib.colorbar import Colorbar
from matplotlib.image import AxesImage

from src.core.spatial_index import unpack_coords

if TYPE_CHECKING:
    from src.core.network import NeuralNetwork

HeatmapKind = Literal["activity", "weights", "energy"]


@dataclass(frozen=True, slots=True)
class HeatmapData:
    """Numerical heatmap payload independent of Matplotlib rendering."""

    values: npt.NDArray[np.float64]
    kind: HeatmapKind
    label: str
    title: str


class HeatmapProjector:
    """Project sparse 5D network state onto the X-Y plane."""

    def __init__(self, network: "NeuralNetwork", activity_tau_ticks: float = 50.0):
        if activity_tau_ticks <= 0.0:
            raise ValueError("activity_tau_ticks must be > 0")
        self.network = network
        self.activity_tau_ticks = float(activity_tau_ticks)
        self._shape = (int(network.dimensions[0]), int(network.dimensions[1]))

    def build(self, kind: HeatmapKind) -> HeatmapData:
        """Build one finite X-Y projection for the requested metric."""
        if kind == "activity":
            return HeatmapData(
                values=self.activity(),
                kind=kind,
                label="Recent activity",
                title="Activity heatmap (X-Y projection)",
            )
        if kind == "weights":
            return HeatmapData(
                values=self.weights(),
                kind=kind,
                label="Mean incoming weight",
                title="Weight heatmap (X-Y projection)",
            )
        if kind == "energy":
            return HeatmapData(
                values=self.energy(),
                kind=kind,
                label="Mean energy",
                title="Energy heatmap (X-Y projection)",
            )
        raise ValueError(f"Unsupported heatmap kind: {kind}")

    def activity(self) -> npt.NDArray[np.float64]:
        """Return recent spike activity projected onto X-Y."""
        sums, counts = self._empty_accumulators()
        current_tick = self.network.current_tick
        for neuron_id, neuron in self.network.neurons.items():
            x_coord, y_coord, _, _, _ = unpack_coords(neuron_id)
            if neuron.last_spike_tick < 0:
                value = 0.0
            else:
                age = max(0, current_tick - neuron.last_spike_tick)
                value = float(np.exp(-age / self.activity_tau_ticks))
            sums[x_coord, y_coord] += value
            counts[x_coord, y_coord] += 1.0
        return self._mean(sums, counts)

    def weights(self) -> npt.NDArray[np.float64]:
        """Return mean incoming synaptic weight per target, projected onto X-Y."""
        per_neuron_sum: dict[int, float] = {}
        per_neuron_count: dict[int, int] = {}
        for synapses in self.network.synapses.values():
            for synapse in synapses:
                per_neuron_sum[synapse.target_id] = (
                    per_neuron_sum.get(synapse.target_id, 0.0) + synapse.weight
                )
                per_neuron_count[synapse.target_id] = (
                    per_neuron_count.get(synapse.target_id, 0) + 1
                )

        sums, counts = self._empty_accumulators()
        for neuron_id in self.network.neurons:
            x_coord, y_coord, _, _, _ = unpack_coords(neuron_id)
            incoming_count = per_neuron_count.get(neuron_id, 0)
            value = (
                per_neuron_sum[neuron_id] / incoming_count
                if incoming_count
                else 0.0
            )
            sums[x_coord, y_coord] += value
            counts[x_coord, y_coord] += 1.0
        return self._mean(sums, counts)

    def energy(self) -> npt.NDArray[np.float64]:
        """Return mean neuron energy projected onto X-Y."""
        sums, counts = self._empty_accumulators()
        for neuron_id, neuron in self.network.neurons.items():
            x_coord, y_coord, _, _, _ = unpack_coords(neuron_id)
            sums[x_coord, y_coord] += neuron.energy
            counts[x_coord, y_coord] += 1.0
        return self._mean(sums, counts)

    def _empty_accumulators(
        self,
    ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        return np.zeros(self._shape, dtype=float), np.zeros(self._shape, dtype=float)

    @staticmethod
    def _mean(
        sums: npt.NDArray[np.float64],
        counts: npt.NDArray[np.float64],
    ) -> npt.NDArray[np.float64]:
        result = np.zeros_like(sums)
        np.divide(sums, counts, out=result, where=counts > 0.0)
        return result


class HeatmapView:
    """Render projected heatmap data into an existing Matplotlib axis."""

    def __init__(self, axis: Axes):
        self.axis = axis
        self._image: AxesImage | None = None
        self._colorbar: Colorbar | None = None

    def render(self, data: HeatmapData) -> None:
        """Render or update a heatmap without creating duplicate colorbars."""
        display_values = data.values.T
        if self._image is None:
            self._image = self.axis.imshow(
                display_values,
                origin="lower",
                interpolation="nearest",
                cmap="hot",
                aspect="auto",
            )
            self._colorbar = self.axis.figure.colorbar(self._image, ax=self.axis)
        else:
            self._image.set_data(display_values)

        finite = display_values[np.isfinite(display_values)]
        if finite.size:
            value_min = float(np.min(finite))
            value_max = float(np.max(finite))
            if value_min == value_max:
                value_max = value_min + 1.0
            self._image.set_clim(value_min, value_max)

        self.axis.set_title(data.title)
        self.axis.set_xlabel("X")
        self.axis.set_ylabel("Y")
        if self._colorbar is not None:
            self._colorbar.set_label(data.label)
