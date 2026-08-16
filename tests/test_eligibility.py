import math

import pytest

from src.learning.eligibility import EligibilityTrace


def test_trace_add_and_lazy_decay() -> None:
    trace = EligibilityTrace(tau_ticks=20.0)
    assert trace.add(1.0, tick=0) == pytest.approx(1.0)
    assert trace.read(10) == pytest.approx(math.exp(-10 / 20.0))


def test_trace_accumulates_after_decay() -> None:
    trace = EligibilityTrace(tau_ticks=10.0)
    trace.add(1.0, 0)
    value = trace.add(0.5, 10)
    assert value == pytest.approx(math.exp(-1.0) + 0.5)


def test_trace_rejects_time_travel() -> None:
    trace = EligibilityTrace(tau_ticks=10.0)
    trace.add(1.0, 5)
    with pytest.raises(ValueError):
        trace.read(4)


def test_trace_reset() -> None:
    trace = EligibilityTrace(tau_ticks=10.0)
    trace.add(1.0, 3)
    trace.reset()
    assert trace.value == 0.0
    assert trace.last_tick is None


def test_invalid_tau_fails_fast() -> None:
    with pytest.raises(ValueError):
        EligibilityTrace(tau_ticks=0.0)
