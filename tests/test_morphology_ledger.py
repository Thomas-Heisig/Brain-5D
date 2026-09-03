from __future__ import annotations

import pytest

from src.self_organization import MorphologyBudget, MorphologyLedger


def test_morphology_ledger_tracks_ages_and_first_birth_tick() -> None:
    ledger = MorphologyLedger(budget=MorphologyBudget(growth=3.0, pruning=2.0))
    ledger = ledger.register_neuron(4, 10).register_neuron(4, 12)
    ledger = ledger.register_synapse(4, 5, 11)

    assert ledger.neuron_age(4, 15) == 5
    assert ledger.synapse_age(4, 5, 15) == 4
    assert ledger.neuron_age(99, 15) is None


def test_morphology_ledger_keeps_growth_and_pruning_budgets_separate() -> None:
    ledger = MorphologyLedger(budget=MorphologyBudget(growth=2.0, pruning=1.0))

    assert ledger.can_afford_growth(neurons=1, synapses=2)
    ledger = ledger.consume_growth(neurons=1, synapses=2)
    assert ledger.growth_spent == pytest.approx(1.5)
    assert ledger.can_afford_pruning(synapses=4)
    ledger = ledger.consume_pruning(synapses=4)
    assert ledger.pruning_spent == pytest.approx(1.0)
    assert not ledger.can_afford_pruning(synapses=1)


def test_morphology_ledger_rejects_budget_overrun_and_invalid_age() -> None:
    ledger = MorphologyLedger(budget=MorphologyBudget(growth=1.0, pruning=1.0))

    with pytest.raises(ValueError, match="growth budget"):
        ledger.consume_growth(neurons=2)
    with pytest.raises(ValueError, match="precede"):
        ledger.register_neuron(1, 10).neuron_age(1, 9)
    with pytest.raises(ValueError, match="budgets"):
        MorphologyBudget(growth=-1.0, pruning=1.0)
