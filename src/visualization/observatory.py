"""Interactive Brain 5D observatory with optional X-Y heatmap."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from src.core.spatial_index import unpack_coords
from src.visualization.heatmap import HeatmapKind, HeatmapProjector, HeatmapView


def build_raster_points(frames: Any, sample_ids: list[int]) -> list[tuple[int, int]]:
    """Convert spike-history frames to raster plot points."""
    id_to_row = {neuron_id: row for row, neuron_id in enumerate(sample_ids)}
    points: list[tuple[int, int]] = []
    for frame in frames:
        for neuron_id in frame.neuron_ids:
            row = id_to_row.get(neuron_id)
            if row is not None:
                points.append((frame.tick, row))
    return points


class Observatory:
    """Interactive visual observer for sparse Brain 5D simulations."""

    def __init__(
        self,
        network: Any,
        config: dict[str, Any],
        spike_history: Any,
        history: Any,
        probes: Any | None = None,
    ) -> None:
        self.net = network
        self.config = config
        self.spike_history = spike_history
        self.history = history
        self.probes = probes
        self.dims = tuple(config["dimensions"])
        visualization = config["visualization"]
        self.raster_n = int(visualization["spike_raster_neurons"])
        self.proj_dim = str(visualization.get("projection_4d", "d4"))
        self.tau = float(visualization.get("activity_tau_ticks", 50.0))
        self.show_heatmap = bool(visualization.get("show_heatmap", True))
        self.heatmap_kind: HeatmapKind = self._parse_heatmap_kind(
            visualization.get("heatmap_type", "activity")
        )

        plt.ion()
        self.fig = plt.figure(figsize=(16, 10))
        grid = self.fig.add_gridspec(2, 3)
        self.ax1 = self.fig.add_subplot(grid[0, 0], projection="3d")
        self.ax2 = self.fig.add_subplot(grid[0, 1])
        self.ax_heat = self.fig.add_subplot(grid[0, 2])
        self.ax3 = self.fig.add_subplot(grid[1, 0])
        self.ax4 = self.fig.add_subplot(grid[1, 1:])

        self.scatter_xyz = self.ax1.scatter(
            [], [], [], c=[], cmap="hot", vmin=0, vmax=1, s=10, alpha=0.7
        )
        self.scatter_xd = self.ax2.scatter(
            [], [], c=[], cmap="plasma", vmin=0, vmax=1, s=8, alpha=0.7
        )
        self.raster_scatter = self.ax3.scatter([], [], s=8, marker="|")
        (self.line_spikes,) = self.ax4.plot([], [], label="Spikes/tick")
        (self.line_v,) = self.ax4.plot([], [], label="Mean V")
        (self.line_queue,) = self.ax4.plot([], [], label="Queue")
        self.ax4.legend(fontsize=8)
        self.ax1.set_title("XYZ Activity")
        self.ax2.set_title(f"X vs {self.proj_dim.upper()}")
        self.ax3.set_title("Real Spike Raster")
        self.ax4.set_title("Time Series")

        self.heatmap_projector = HeatmapProjector(self.net, self.tau)
        self.heatmap_view = HeatmapView(self.ax_heat)
        if not self.show_heatmap:
            self.ax_heat.set_visible(False)

        self.status_text = self.fig.text(
            0.02, 0.02, "", family="monospace", fontsize=9
        )
        self.probe_text = self.fig.text(
            0.72, 0.02, "", family="monospace", fontsize=9
        )
        self.snapshot_dir = Path("artifacts/snapshots")
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        self.fig.canvas.mpl_connect("key_press_event", self._on_key)
        plt.show(block=False)

    @staticmethod
    def _parse_heatmap_kind(value: object) -> HeatmapKind:
        kind = str(value).lower()
        if kind not in {"activity", "weights", "energy"}:
            raise ValueError(
                "visualization.heatmap_type must be activity, weights or energy"
            )
        return kind  # type: ignore[return-value]

    def _on_key(self, event: Any) -> None:
        if event.key and str(event.key).lower() == "s":
            self.save_snapshot()

    def _activity(self, neuron: Any) -> float:
        if neuron.last_spike_tick < 0:
            return 0.0
        age = max(0, self.net.current_tick - neuron.last_spike_tick)
        return float(np.exp(-age / self.tau))

    def draw(self) -> None:
        """Refresh all Observatory panels from the current network state."""
        sample = list(self.net.neurons.items())[:2000]
        x_values: list[int] = []
        y_values: list[int] = []
        z_values: list[int] = []
        activity: list[float] = []
        xd_values: list[int] = []
        yd_values: list[int] = []
        activity_2d: list[float] = []

        for neuron_id, neuron in sample:
            x_coord, y_coord, z_coord, d4_coord, d5_coord = unpack_coords(
                neuron_id
            )
            value = self._activity(neuron)
            x_values.append(x_coord)
            y_values.append(y_coord)
            z_values.append(z_coord)
            activity.append(value)
            xd_values.append(x_coord)
            yd_values.append(d4_coord if self.proj_dim == "d4" else d5_coord)
            activity_2d.append(value)

        self.scatter_xyz._offsets3d = (x_values, y_values, z_values)
        self.scatter_xyz.set_array(np.asarray(activity))
        points_2d = (
            np.column_stack((xd_values, yd_values))
            if xd_values
            else np.empty((0, 2))
        )
        self.scatter_xd.set_offsets(points_2d)
        self.scatter_xd.set_array(np.asarray(activity_2d))
        self.ax1.set(
            xlim=(0, self.dims[0] - 1),
            ylim=(0, self.dims[1] - 1),
            zlim=(0, self.dims[2] - 1),
        )
        projection_size = (
            self.dims[3] if self.proj_dim == "d4" else self.dims[4]
        )
        self.ax2.set(
            xlim=(0, self.dims[0] - 1),
            ylim=(0, projection_size - 1),
        )

        frames = self.spike_history.get_frames()[-100:]
        sample_ids = list(self.net.neurons)[: self.raster_n]
        raster_points = build_raster_points(frames, sample_ids)
        self.raster_scatter.set_offsets(
            np.asarray(raster_points) if raster_points else np.empty((0, 2))
        )
        if frames:
            self.ax3.set_xlim(
                frames[0].tick,
                max(frames[0].tick + 1, frames[-1].tick + 1),
            )
        self.ax3.set_ylim(0, max(1, len(sample_ids)))

        history = self.history.get_all()
        if history:
            ticks = [item["tick"] for item in history]
            self.line_spikes.set_data(
                ticks, [item["spikes_this_tick"] for item in history]
            )
            self.line_v.set_data(ticks, [item["mean_v"] for item in history])
            self.line_queue.set_data(
                ticks, [item["queued_events"] for item in history]
            )
            self.ax4.relim()
            self.ax4.autoscale_view()

        if self.show_heatmap:
            self.heatmap_view.render(self.heatmap_projector.build(self.heatmap_kind))

        self.status_text.set_text(
            f"Tick {self.net.current_tick} | neurons {len(self.net.neurons)} | "
            f"synapses {self.net.synapse_count} | queue {self.net.queued_event_count} | "
            f"spikes {self.net.total_spikes}"
        )
        if self.probes and self.probes.probes:
            rows: list[str] = []
            for probe_id in self.probes.probes[:3]:
                data = self.probes.get_probe_data(probe_id)
                rows.append(
                    f"{probe_id}: v={data.get('v', 0):.1f} "
                    f"spk={data.get('spike_counter', 0)}"
                )
            self.probe_text.set_text("Probes\n" + "\n".join(rows))

        self.fig.canvas.draw_idle()
        plt.pause(0.001)

    def save_snapshot(self) -> Path:
        """Save the current Observatory figure and return its path."""
        path = self.snapshot_dir / f"brain5d_tick_{self.net.current_tick:06d}.png"
        self.fig.savefig(path, dpi=150, bbox_inches="tight")
        return path

    @staticmethod
    def block_until_closed() -> None:
        """Switch Matplotlib to blocking mode until the window is closed."""
        plt.ioff()
        plt.show(block=True)
