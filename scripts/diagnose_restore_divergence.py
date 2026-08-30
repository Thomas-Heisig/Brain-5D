"""Diagnose A/B/C divergence by dumping canonical state for comparison."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config.loader import ConfigDict
from src.core.network import NeuralNetwork
from src.homeostasis.engine import HomeostasisEngine
from src.learning.learning_engine import LearningEngine
from src.storage.checkpoint import capture_runtime_checkpoint, write_runtime_checkpoint
from src.storage.core_restore import restore_full
from src.storage.runtime import StorageRuntimeConfig, StorageSession
from tests._restore_helpers import (
    K,
    N,
    build_absolute_schedule,
    config_sha256,
    create_network,
    make_config,
    run_absolute_schedule,
)

OUT_DIR = Path(__file__).resolve().parent.parent / "tmp" / "restore_diag"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def _write_artifacts(network, homeo, learn, tmp_path, schedule, config):
    rt = StorageRuntimeConfig(
        snapshot_path=tmp_path / "base.b5d",
        journal_path=tmp_path / "base.b5d.journal",
        commit_interval_ticks=1,
    )
    with StorageSession(network, rt):
        pass
    from tests._restore_helpers import capture_learning_state
    learn_state = capture_learning_state(learn)
    checkpoint = capture_runtime_checkpoint(
        network,
        homeostasis_rates=homeo._rates_hz,
        learning_states=learn_state["states"] if learn_state else None,
        pending_rewards=learn_state["pending_rewards"] if learn_state else None,
    )
    cp_path = tmp_path / "runtime.json"
    write_runtime_checkpoint(cp_path, checkpoint)
    cfg_path = tmp_path / "config.json"
    cfg_path.write_text(json.dumps(config, sort_keys=True), encoding="utf-8")
    sched_path = tmp_path / "schedule.json"
    sched_path.write_text(json.dumps(schedule, sort_keys=True), encoding="utf-8")
    return {
        "snapshot": rt.snapshot_path,
        "journal": rt.journal_path,
        "checkpoint": cp_path,
        "config": cfg_path,
        "schedule": sched_path,
    }


def _dump_state(network, homeo, learn, label):
    from src.research.canonical_state import capture_canonical_state
    from tests._restore_helpers import capture_learning_state

    homeo_rates = dict(homeo._rates_hz) if homeo is not None else None
    learn_state = capture_learning_state(learn) if learn is not None else None
    state = capture_canonical_state(
        network,
        config_sha256=config_sha256(make_config()),
        homeostasis_rates=homeo_rates,
        learning_state=learn_state,
    )
    path = OUT_DIR / f"state_{label}.json"
    path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    return path


def main():
    config = make_config()
    schedule = build_absolute_schedule(config, N)

    # Path B: run to K, capture original state at K, then restore, capture state at K after restore
    net_b = create_network(config)
    homeo_b = HomeostasisEngine(net_b, config)
    homeo_b.attach()
    learn_b = LearningEngine(net_b, config)
    learn_b.attach()
    run_absolute_schedule(net_b, schedule, K)
    path_bk_orig = _dump_state(net_b, homeo_b, learn_b, "B_K_original")

    tmp_path = OUT_DIR / "path_b"
    tmp_path.mkdir(exist_ok=True)
    artifacts = _write_artifacts(net_b, homeo_b, learn_b, tmp_path, schedule, config)
    bundle = restore_full(
        snapshot_path=artifacts["snapshot"],
        journal_path=artifacts["journal"],
        checkpoint_path=artifacts["checkpoint"],
        config=ConfigDict(config),
        recovered_path=tmp_path / "recovered.b5d",
        create_homeostasis_engine=True,
        create_learning_engine=True,
    )
    path_bk_restored = _dump_state(bundle.network, bundle.homeostasis_engine, bundle.learning_engine, "B_K_restored")

    print(f"State B_K original: {path_bk_orig}")
    print(f"State B_K restored: {path_bk_restored}")

    # Compare top-level keys at K
    state_orig = json.loads(path_bk_orig.read_text(encoding="utf-8"))
    state_restored = json.loads(path_bk_restored.read_text(encoding="utf-8"))
    for key in state_orig:
        if state_orig[key] != state_restored[key]:
            print(f"DIFFERS at K: {key}")
            detail = OUT_DIR / f"diff_at_K_{key}.json"
            detail.write_text(
                json.dumps({"original": state_orig[key], "restored": state_restored[key]}, indent=2, sort_keys=True),
                encoding="utf-8",
            )
            print(f"  detail: {detail}")

    # Continue to N and compare A vs B


    print(f"State A_N: {path_a}")
    print(f"State B_N: {path_b}")

    state_a = json.loads(path_a.read_text(encoding="utf-8"))
    state_b = json.loads(path_b.read_text(encoding="utf-8"))
    differing_keys = []
    for key in state_a:
        if state_a[key] != state_b[key]:
            differing_keys.append(key)
            print(f"DIFFERS at N: {key}")
            detail = OUT_DIR / f"diff_N_{key}.json"
            detail.write_text(
                json.dumps({"A": state_a[key], "B": state_b[key]}, indent=2, sort_keys=True),
                encoding="utf-8",
            )
            print(f"  detail: {detail}")

    if "neurons" in differing_keys:
        a_neurons = {n["neuron_id"]: n for n in state_a["neurons"]}
        b_neurons = {n["neuron_id"]: n for n in state_b["neurons"]}
        first_diff = None
        for nid in sorted(a_neurons):
            if a_neurons[nid] != b_neurons.get(nid):
                first_diff = nid
                break
        if first_diff is not None:
            detail = OUT_DIR / "diff_N_first_neuron.json"
            detail.write_text(
                json.dumps({"A": a_neurons[first_diff], "B": b_neurons.get(first_diff)}, indent=2, sort_keys=True),
                encoding="utf-8",
            )
            print(f"First diverging neuron at N: {first_diff} -> {detail}")


if __name__ == "__main__":
    main()
