"""Check exact float state at K before and after restore."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config.loader import ConfigDict
from src.homeostasis.engine import HomeostasisEngine
from src.learning.learning_engine import LearningEngine
from src.storage.checkpoint import capture_runtime_checkpoint, write_runtime_checkpoint
from src.storage.core_restore import restore_full
from src.storage.runtime import StorageRuntimeConfig, StorageSession
from tests._restore_helpers import (
    K,
    build_absolute_schedule,
    create_network,
    make_config,
    run_absolute_schedule,
)


def main():
    config = make_config()
    schedule = build_absolute_schedule(config, 1000)

    net = create_network(config)
    homeo = HomeostasisEngine(net, config)
    homeo.attach()
    learn = LearningEngine(net, config)
    learn.attach()
    run_absolute_schedule(net, schedule, K)

    print("ORIGINAL at K:")
    print(f"  neuron 0 threshold_adaptation = {net.neurons[0].threshold_adaptation!r}")
    print(f"  neuron 0 v = {net.neurons[0].v!r}")
    print(f"  homeo rate 0 = {homeo._rates_hz.get(0, 0.0)!r}")

    tmp_path = Path("F:/Brain-5D/tmp/trace_diag/path_b")
    tmp_path.mkdir(parents=True, exist_ok=True)
    rt = StorageRuntimeConfig(
        snapshot_path=tmp_path / "base.b5d",
        journal_path=tmp_path / "base.b5d.journal",
        commit_interval_ticks=1,
    )
    with StorageSession(net, rt):
        pass
    from tests._restore_helpers import capture_learning_state

    learn_state = capture_learning_state(learn)
    checkpoint = capture_runtime_checkpoint(
        net,
        homeostasis_rates=homeo._rates_hz,
        learning_states=learn_state["states"] if learn_state else None,
        pending_rewards=learn_state["pending_rewards"] if learn_state else None,
    )
    cp_path = tmp_path / "runtime.json"
    write_runtime_checkpoint(cp_path, checkpoint)

    bundle = restore_full(
        snapshot_path=rt.snapshot_path,
        journal_path=rt.journal_path,
        checkpoint_path=cp_path,
        config=ConfigDict(config),
        recovered_path=tmp_path / "recovered.b5d",
        create_homeostasis_engine=True,
        create_learning_engine=True,
    )

    print("\nRESTORED at K:")
    print(
        f"  neuron 0 threshold_adaptation = {bundle.network.neurons[0].threshold_adaptation!r}"
    )
    print(f"  neuron 0 v = {bundle.network.neurons[0].v!r}")
    print(f"  homeo rate 0 = {bundle.homeostasis_engine._rates_hz.get(0, 0.0)!r}")

    print("\nDIFFERENCES:")
    print(
        f"  threshold_adaptation: {net.neurons[0].threshold_adaptation - bundle.network.neurons[0].threshold_adaptation!r}"
    )
    print(f"  v: {net.neurons[0].v - bundle.network.neurons[0].v!r}")
    print(
        f"  homeo rate: {homeo._rates_hz.get(0, 0.0) - bundle.homeostasis_engine._rates_hz.get(0, 0.0)!r}"
    )


if __name__ == "__main__":
    main()
