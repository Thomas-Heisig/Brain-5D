from src.telemetry.spike_history import SpikeFrame
from src.visualization.observatory import build_raster_points


def test_raster_points_are_real_spikes():
    frames = [SpikeFrame(0, (10,)), SpikeFrame(1, ()), SpikeFrame(2, (20,))]
    assert build_raster_points(frames, [10, 20]) == [(0, 0), (2, 1)]
