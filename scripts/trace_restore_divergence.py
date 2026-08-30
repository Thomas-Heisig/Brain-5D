"""Trace A/B divergence tick-by-tick between K and N."""

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

OUT_DIR = Path(__file__).resolve().parent.parent / "tmp" / "trace_diag"
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


def _neuron_0_state(network, homeo):
    n = network.neurons[0]
    return {
        "tick": network.current_tick,
        "v": n.v,
        "u": n.u,
        "threshold_adaptation": n.threshold_adaptation,
        "last_spike_tick": n.last_spike_tick,
        "homeo_rate": homeo._rates_hz.get(0, 0.0) if homeo else None,
    }


def main():
    config = make_config()
    schedule = build_absolute_schedule(config, N)

    # Path A: run to N, recording neuron 0 each tick after K
    net_a = create_network(config)
    homeo_a = HomeostasisEngine(net_a, config)
    homeo_a.attach()
    learn_a = LearningEngine(net_a, config)
    learn_a.attach()
    run_absolute_schedule(net_a, schedule, K)
    trace_a = []
    while net_a.current_tick < N:
        net_a.step()
        trace_a.append(_neuron_0_state(net_a, homeo_a))

    # Path B: run to K, restore, then step-by-step to N
    net_b = create_network(config)
    homeo_b = HomeostasisEngine(net_b, config)
    homeo_b.attach()
    learn_b = LearningEngine(net_b, config)
    learn_b.attach()
    run_absolute_schedule(net_b, schedule, K)

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
    trace_b = []
    while bundle.network.current_tick < N:
        bundle.network.step()
        trace_b.append(_neuron_0_state(bundle.network, bundle.homeostasis_engine))

    # Compare tick-by-tick
    diff_tick = None
    for i, (sa, sb) in enumerate(zip(trace_a, trace_b)):
        if sa != sb:
            diff_tick = i
            break

    out = OUT_DIR / "trace_comparison.json"
    out.write_text(
        json.dumps({"diff_tick_index": diff_tick, "A": trace_a, "B": trace_b}, indent=2),
        encoding="utf-8",
    )
    print(f"Trace written to {out}")
    if diff_tick is not None:
        tick = trace_a[diff_tick]["tick"]
        print(f"First divergence at tick {tick}")
        print(f"  A: {trace_a[diff_tick]}")
        print(f"  B: {trace_b[diff_tick]}")
    else:
        print("No divergence found between K and N")


if __name__ == "__main__":
    main()
