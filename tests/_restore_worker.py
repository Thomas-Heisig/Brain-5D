"""Restore worker subprocess for Path C (Alpha.5).

This is C2: a fresh Python process that receives only filesystem paths
and scalar arguments. It calls the production restore_full() and
computes digests using the canonical production digest.

No in-memory network/engine/state object crosses the subprocess boundary.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def main() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--journal", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--schedule", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--end-tick", type=int, required=True)
    parser.add_argument("--digest-k", required=True, help="Path to write digest at K (before continuation)")
    args = parser.parse_args()

    from src.storage.core_restore import restore_full

    # ── Restore from filesystem artifacts only ───────────────────────────
    bundle = restore_full(
        snapshot_path=Path(args.snapshot),
        journal_path=Path(args.journal),
        checkpoint_path=Path(args.checkpoint),
        config=json.loads(Path(args.config).read_text()),
        recovered_path=Path(args.output).parent / "recovered.b5d",
        create_homeostasis_engine=True,
        create_learning_engine=True,
    )

    # ── Compute digest at K (before continuing) ──────────────────────────
    from tests._restore_helpers import compute_digest, config_sha256, make_config, run_absolute_schedule

    config = make_config()
    digest_K = compute_digest(
        bundle.network,
        bundle.homeostasis_engine,
        bundle.learning_engine,
        config_sha256_str=config_sha256(config),
    )

    digest_K_path = Path(args.digest_k)
    digest_K_path.write_text(json.dumps({"digest_K": digest_K, "pid": os.getpid()}), encoding="utf-8")

    # ── Continue K -> N ──────────────────────────────────────────────────
    schedule = json.loads(Path(args.schedule).read_text())
    run_absolute_schedule(bundle.network, schedule, args.end_tick)

    # ── Compute digest at N ──────────────────────────────────────────────
    digest_N = compute_digest(
        bundle.network,
        bundle.homeostasis_engine,
        bundle.learning_engine,
        config_sha256_str=config_sha256(config),
    )

    result = {
        "digest": digest_N,
        "digest_K": digest_K,
        "pid": os.getpid(),
        "start_tick": 0,
        "end_tick": args.end_tick,
        "restore_full_used": True,
    }

    Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"C2 worker done: digest_K={digest_K}, digest_N={digest_N}, pid={os.getpid()}")


if __name__ == "__main__":
    main()
