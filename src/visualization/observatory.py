from __future__ import annotations

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from src.core.spatial_index import unpack_coords


def build_raster_points(frames, sample_ids):
    id_to_row = {nid: i for i, nid in enumerate(sample_ids)}
    points = []
    for frame in frames:
        for nid in frame.neuron_ids:
            row = id_to_row.get(nid)
            if row is not None:
                points.append((frame.tick, row))
    return points


class Observatory:
    def __init__(self, network, config, spike_history, history, probes=None):
        self.net = network; self.config = config; self.spike_history = spike_history; self.history = history; self.probes = probes
        self.dims = tuple(config["dimensions"]); self.raster_n = int(config["visualization"]["spike_raster_neurons"])
        self.proj_dim = config["visualization"].get("projection_4d", "d4")
        self.tau = float(config["visualization"].get("activity_tau_ticks", 50.0))
        plt.ion(); self.fig = plt.figure(figsize=(14, 10))
        self.ax1 = self.fig.add_subplot(2, 2, 1, projection="3d"); self.ax2 = self.fig.add_subplot(2, 2, 2)
        self.ax3 = self.fig.add_subplot(2, 2, 3); self.ax4 = self.fig.add_subplot(2, 2, 4)
        self.scatter_xyz = self.ax1.scatter([], [], [], c=[], cmap="hot", vmin=0, vmax=1, s=10, alpha=.7)
        self.scatter_xd = self.ax2.scatter([], [], c=[], cmap="plasma", vmin=0, vmax=1, s=8, alpha=.7)
        self.raster_scatter = self.ax3.scatter([], [], s=8, marker="|")
        self.line_spikes, = self.ax4.plot([], [], label="Spikes/tick")
        self.line_v, = self.ax4.plot([], [], label="Mean V")
        self.line_queue, = self.ax4.plot([], [], label="Queue")
        self.ax4.legend(fontsize=8); self.ax1.set_title("XYZ Activity"); self.ax2.set_title(f"X vs {self.proj_dim.upper()}")
        self.ax3.set_title("Real Spike Raster"); self.ax4.set_title("Time Series")
        self.status_text = self.fig.text(.02, .02, "", family="monospace", fontsize=9)
        self.probe_text = self.fig.text(.72, .02, "", family="monospace", fontsize=9)
        self.snapshot_dir = Path("artifacts/snapshots"); self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        self.fig.canvas.mpl_connect("key_press_event", self._on_key); plt.show(block=False)

    def _on_key(self, event):
        if event.key and event.key.lower() == "s": self.save_snapshot()

    def _activity(self, neuron):
        if neuron.last_spike_tick < 0: return 0.0
        age = max(0, self.net.current_tick - neuron.last_spike_tick)
        return float(np.exp(-age / self.tau))

    def draw(self):
        sample = list(self.net.neurons.items())[:2000]
        xs=[]; ys=[]; zs=[]; act=[]; xd=[]; yd=[]; act2=[]
        for nid, neuron in sample:
            x,y,z,d4,d5 = unpack_coords(nid); a=self._activity(neuron)
            xs.append(x); ys.append(y); zs.append(z); act.append(a)
            xd.append(x); yd.append(d4 if self.proj_dim=="d4" else d5); act2.append(a)
        self.scatter_xyz._offsets3d = (xs,ys,zs); self.scatter_xyz.set_array(np.asarray(act))
        pts2 = np.column_stack((xd,yd)) if xd else np.empty((0,2)); self.scatter_xd.set_offsets(pts2); self.scatter_xd.set_array(np.asarray(act2))
        self.ax1.set(xlim=(0,self.dims[0]-1), ylim=(0,self.dims[1]-1), zlim=(0,self.dims[2]-1))
        self.ax2.set(xlim=(0,self.dims[0]-1), ylim=(0,(self.dims[3] if self.proj_dim=="d4" else self.dims[4])-1))
        frames = self.spike_history.get_frames()[-100:]; sample_ids = list(self.net.neurons)[:self.raster_n]
        rp = build_raster_points(frames, sample_ids); self.raster_scatter.set_offsets(np.asarray(rp) if rp else np.empty((0,2)))
        if frames: self.ax3.set_xlim(frames[0].tick, max(frames[0].tick+1, frames[-1].tick+1))
        self.ax3.set_ylim(0, max(1,len(sample_ids)))
        h = self.history.get_all()
        if h:
            ticks=[d["tick"] for d in h]; self.line_spikes.set_data(ticks,[d["spikes_this_tick"] for d in h])
            self.line_v.set_data(ticks,[d["mean_v"] for d in h]); self.line_queue.set_data(ticks,[d["queued_events"] for d in h])
            self.ax4.relim(); self.ax4.autoscale_view()
        self.status_text.set_text(f"Tick {self.net.current_tick} | neurons {len(self.net.neurons)} | synapses {self.net.synapse_count} | queue {self.net.queued_event_count} | spikes {self.net.total_spikes}")
        if self.probes and self.probes.probes:
            rows=[]
            for pid in self.probes.probes[:3]:
                d=self.probes.get_probe_data(pid); rows.append(f"{pid}: v={d.get('v',0):.1f} spk={d.get('spike_counter',0)}")
            self.probe_text.set_text("Probes\n"+"\n".join(rows))
        self.fig.canvas.draw_idle(); plt.pause(.001)

    def save_snapshot(self):
        path=self.snapshot_dir/f"brain5d_tick_{self.net.current_tick:06d}.png"; self.fig.savefig(path,dpi=150,bbox_inches="tight")
        return path

    def block_until_closed(self):
        plt.ioff(); plt.show(block=True)
