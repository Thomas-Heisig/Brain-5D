import math

import pytest

from src.learning.stdp_plugin import STDPParameters, STDPSynapse


def test_ltp_pre_before_post() -> None:
    """PRE before POST -> potentiation."""
    syn = STDPSynapse(weight=0.5, a_plus=0.1, tau_plus=20.0)

    assert syn.pre_spike(0) == 0.0
    delta = syn.post_spike(10)

    expected_delta = 0.1 * math.exp(-10 / 20)
    assert delta == pytest.approx(expected_delta)
    assert syn.weight == pytest.approx(0.5 + expected_delta)


def test_ltd_post_before_pre() -> None:
    """POST before PRE -> depression."""
    syn = STDPSynapse(weight=0.5, a_minus=0.12, tau_minus=20.0)

    assert syn.post_spike(0) == 0.0
    delta = syn.pre_spike(10)

    expected_delta = -0.12 * math.exp(-10 / 20)
    assert delta == pytest.approx(expected_delta)
    assert syn.weight == pytest.approx(0.5 + expected_delta)


def test_simultaneous_spikes_do_not_change_weight() -> None:
    syn = STDPSynapse(weight=0.5)

    syn.pre_spike(10)
    delta = syn.post_spike(10)

    assert delta == 0.0
    assert syn.weight == 0.5


def test_large_delta_approaches_zero() -> None:
    syn = STDPSynapse(weight=0.5, a_plus=0.1, tau_plus=20.0)
    syn.pre_spike(0)

    delta = syn.post_spike(200)

    assert delta == pytest.approx(0.1 * math.exp(-10.0))
    assert abs(delta) < 0.00001


def test_weight_clamping_reports_applied_delta() -> None:
    high = STDPSynapse(weight=0.95, a_plus=0.1, tau_plus=20.0, max_weight=1.0)
    high.pre_spike(0)
    high_delta = high.post_spike(1)

    assert high.weight == 1.0
    assert high_delta == pytest.approx(0.05)

    low = STDPSynapse(weight=0.05, a_minus=0.12, tau_minus=20.0, min_weight=0.0)
    low.post_spike(0)
    low_delta = low.pre_spike(1)

    assert low.weight == 0.0
    assert low_delta == pytest.approx(-0.05)


@pytest.mark.parametrize("delay", [1, 5, 10, 20, 50])
def test_ltp_timing_curve(delay: int) -> None:
    syn = STDPSynapse(weight=0.5, a_plus=0.1, tau_plus=20.0)
    syn.pre_spike(0)

    delta = syn.post_spike(delay)

    assert delta == pytest.approx(0.1 * math.exp(-delay / 20.0))


@pytest.mark.parametrize("delay", [1, 5, 10, 20, 50])
def test_ltd_timing_curve(delay: int) -> None:
    syn = STDPSynapse(weight=0.5, a_minus=0.12, tau_minus=20.0)
    syn.post_spike(0)

    delta = syn.pre_spike(delay)

    assert delta == pytest.approx(-0.12 * math.exp(-delay / 20.0))


def test_independent_repeated_pairs() -> None:
    """Repeated laboratory pairs are separated by an explicit timing reset."""
    syn = STDPSynapse(weight=0.5, a_plus=0.1, tau_plus=20.0)
    expected_delta = 0.1 * math.exp(-10 / 20.0)

    syn.pre_spike(0)
    first = syn.post_spike(10)
    syn.reset_timing()

    syn.pre_spike(20)
    second = syn.post_spike(30)

    assert first == pytest.approx(expected_delta)
    assert second == pytest.approx(expected_delta)
    assert syn.weight == pytest.approx(0.5 + 2 * expected_delta)


def test_continuous_sequence_exposes_nearest_neighbour_pairing() -> None:
    """Document the actual online rule: PRE after an earlier POST causes LTD."""
    syn = STDPSynapse(weight=0.5, a_plus=0.1, a_minus=0.12, tau_plus=20.0, tau_minus=20.0)

    syn.pre_spike(0)
    ltp_1 = syn.post_spike(10)
    ltd_1 = syn.pre_spike(20)
    ltp_2 = syn.post_spike(30)

    assert ltp_1 > 0.0
    assert ltd_1 < 0.0
    assert ltp_2 > 0.0


def test_parameter_bundle_factory() -> None:
    params = STDPParameters(
        a_plus=0.05,
        a_minus=0.07,
        tau_plus=15.0,
        tau_minus=25.0,
        min_weight=0.1,
        max_weight=0.9,
    )

    syn = STDPSynapse.from_parameters(0.4, params)

    assert syn.a_plus == 0.05
    assert syn.a_minus == 0.07
    assert syn.tau_plus == 15.0
    assert syn.tau_minus == 25.0
    assert syn.min_weight == 0.1
    assert syn.max_weight == 0.9


@pytest.mark.parametrize(
    "kwargs",
    [
        {"tau_plus": 0.0},
        {"tau_minus": 0.0},
        {"a_plus": -0.1},
        {"a_minus": -0.1},
        {"min_weight": 1.0, "max_weight": 0.0},
    ],
)
def test_invalid_parameters_fail_fast(kwargs: dict[str, float]) -> None:
    # Der Type‑Checker kann den **kwargs‑Aufruf nicht korrekt analysieren;
    # für den Test ist die Laufzeit‑Struktur entscheidend, daher ignorieren
    # wir den Argument‑Typ an dieser Stelle.
    with pytest.raises(ValueError):
        STDPSynapse(weight=0.5, **kwargs)  # type: ignore[arg-type]