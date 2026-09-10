"""Engineering contracts only; development seeds do not become study outcomes."""

from pathlib import Path

import pytest
import yaml

from src.research.empirical_evaluation import (
    dimensional_edges,
    holm_adjust,
    paired_summary,
    run_association_generalization,
    run_dimensional_ablation,
)
from src.research.protocol_registry import protocol_catalog

ROOT = Path(__file__).resolve().parents[1]


def test_pair_statistics_and_degenerate_effect() -> None:
    value = paired_summary([1.0] * 4, [0.0] * 4)
    assert value["mean_difference"] == 1.0
    assert value["exact_two_sided_sign_flip_p"] == 0.125
    assert value["paired_standardized_effect_dz"] is None
    assert paired_summary([1.0, 1.0], [1.0, 1.0])["exact_two_sided_sign_flip_p"] == 1.0
    with pytest.raises(ValueError):
        paired_summary([1.0], [0.0])
    with pytest.raises(ValueError):
        paired_summary([float("inf"), 1.0], [0.0, 0.0])
    assert holm_adjust([0.01, 0.03, 0.04]) == [0.03, 0.06, 0.06]


def test_dimension_changes_edges_not_budget() -> None:
    a, b = dimensional_edges(7, 2), dimensional_edges(7, 5)
    assert a != b
    assert len(a) == len(b) == 1024
    assert sorted((s, w, d) for s, _, w, d in a) == sorted(
        (s, w, d) for s, _, w, d in b
    )
    assert all(source != target for source, target, _, _ in a + b)


def test_identical_graph_control_is_invariant() -> None:
    config = yaml.safe_load((ROOT / "configs/learning_experiment.yaml").read_text())
    runs = run_dimensional_ablation(config, (7,), ticks=32)
    controls = [r for r in runs if r.condition.startswith("fixed_graph")]
    assert len(controls) == 6
    assert len({r.metrics["response_digest"] for r in controls}) == 1
    assert all(r.metrics["ticks_executed"] == 32 for r in runs)


def test_association_probes_are_frozen_and_share_inputs() -> None:
    config = yaml.safe_load((ROOT / "configs/learning_experiment.yaml").read_text())
    runs = run_association_generalization(config, (7,))
    assert len(runs) == 5
    assert len({r.metrics["test_input_digest"] for r in runs}) == 1
    for run in runs:
        assert (
            run.metrics["weight_digest_before_test"]
            == run.metrics["weight_digest_after_test"]
        )
        assert run.metrics["actual_test_episodes"] == 40
        assert run.metrics["test_teacher_present"] is False
        assert run.metrics["test_learning_engine_attached"] is False
    off = next(r for r in runs if r.condition == "learning_off")
    assert off.metrics["acquisition_reward_weight_updates"] == 0
    # No required accuracy direction: negative experimental outcomes are valid.


def test_frozen_seed_lists_are_not_replaced_by_ui_defaults() -> None:
    catalog = {p["id"]: p for p in protocol_catalog(ROOT / "research")}
    assert catalog["sustained_activity_stability_v1"][
        "default_seed_expression"
    ] == ",".join(map(str, range(42, 52)))
    assert catalog["native_association_holdout_v1"][
        "default_seed_expression"
    ] == ",".join(map(str, range(20001, 20011)))
