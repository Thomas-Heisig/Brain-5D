# Brain 5D Heatmap Observatory

Sprint 2C projects sparse 5D state onto the X-Y plane while averaging neurons
that share the same X-Y coordinate across Z, D4 and D5.

Supported modes:

- `activity`: exponentially decayed recent spike activity using
  `visualization.activity_tau_ticks`.
- `weights`: mean incoming synaptic weight per neuron, then averaged per X-Y
  cell.
- `energy`: mean neuron energy per X-Y cell.

Configuration:

```yaml
visualization:
  show_heatmap: true
  heatmap_type: activity  # activity | weights | energy
```

`HeatmapProjector` contains the numerical projection and is independent of an
interactive Matplotlib window. `HeatmapView` owns one image and one colorbar and
updates them in place to avoid accumulating GUI objects on repeated refreshes.
