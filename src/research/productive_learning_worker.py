"""Single clean-process worker for the productive-learning protocol."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any, cast

import yaml

from src.experiments.learning_lab import run_learning_experiment


def _load_config(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise TypeError("configuration root must be a mapping")
    return cast(dict[str, Any], loaded)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--condition", required=True)
    args = parser.parse_args()

    config = _load_config(args.config)
    config["seed"] = args.seed
    result = run_learning_experiment(config, condition=args.condition)
    print(
        json.dumps(
            {"process_id": os.getpid(), "result": asdict(result)},
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
