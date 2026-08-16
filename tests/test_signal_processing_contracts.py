from src.signal_processing.interpreter import SignalInterpreter
from src.signal_processing.models import SpikeSample


def test_signal_frame_is_deterministic_and_bounded() -> None:
    frame = SignalInterpreter().build_frame(
        tick_from=10,
        tick_to=19,
        dt_ms=1.0,
        neuron_ids=(1, 2),
        spikes=(SpikeSample(10, 1), SpikeSample(10, 2)),
        energies={1: 1.0, 2: 0.8},
        threshold_adaptations={1: 0.2, 2: -0.2},
    )
    assert frame.spike_count == 2
    assert 0.0 <= frame.burst_index <= 1.0
    assert 0.0 <= frame.synchrony <= 1.0
    assert frame.neuron_ids == (1, 2)
