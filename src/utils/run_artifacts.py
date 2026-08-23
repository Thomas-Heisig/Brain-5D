from __future__ import annotations

import csv
import hashlib
import json
import platform
import sys
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, cast

import yaml


class RunArtifacts:
    def __init__(
        self,
        config: dict[str, Any],
        run_id: str | None = None,
        root: str | Path = "artifacts/runs",
    ):
        if run_id is None:
            run_id = datetime.now().strftime("%Y%m%d_%H%M%S") + f"_seed{config['seed']}"
        self.run_dir = Path(root) / run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.config = config
        self.run_id = run_id
        canonical = json.dumps(config, sort_keys=True, separators=(",", ":"))
        self.config_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
        self._metrics_handle = self._spike_handle = self._stimulus_handle = None
        self._metrics_writer = None
        self.summary: dict[str, Any] = {}
        self._topology_data = None
        with (self.run_dir / "environment.json").open("w", encoding="utf-8") as f:
            json.dump(
                {
                    "python_version": sys.version,
                    "platform": platform.platform(),
                    "machine": platform.machine(),
                    "processor": platform.processor(),
                    "run_id": run_id,
                    "seed": config["seed"],
                    "timestamp": datetime.now().isoformat(),
                    "config_hash": self.config_hash,
                },
                f,
                indent=2,
            )
        with (self.run_dir / "effective_config.yaml").open("w", encoding="utf-8") as f:
            yaml.safe_dump(config, f, sort_keys=False)
        (self.run_dir / "config_hash.txt").write_text(
            self.config_hash, encoding="utf-8"
        )

    def __enter__(self):
        self._metrics_handle = (self.run_dir / "metrics.csv").open(
            "w", newline="", encoding="utf-8"
        )
        self._spike_handle = (self.run_dir / "spikes.jsonl").open("w", encoding="utf-8")
        self._stimulus_handle = (self.run_dir / "stimulus.jsonl").open(
            "w", encoding="utf-8"
        )
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        for handle in (self._metrics_handle, self._spike_handle, self._stimulus_handle):
            if handle:
                handle.close()
        if self._topology_data is not None:
            (self.run_dir / "topology.json").write_text(
                json.dumps(self._topology_data, indent=2), encoding="utf-8"
            )
        (self.run_dir / "run_summary.json").write_text(
            json.dumps(self.summary, indent=2), encoding="utf-8"
        )

    def log_metrics(self, metric_dict: dict[str, Any]) -> None:
        if self._metrics_writer is None:
            self._metrics_writer = csv.DictWriter(
                self._metrics_handle, fieldnames=list(metric_dict.keys())  # type: ignore[reportArgumentType]
            )
            self._metrics_writer.writeheader()
        self._metrics_writer.writerow(metric_dict)

    def log_spikes(self, tick: int, spike_ids: tuple[int, ...]) -> None:
        self._spike_handle.write(  # type: ignore[reportOptionalMemberAccess]
            json.dumps({"tick": tick, "spikes": list(spike_ids)}) + "\n"
        )

    def log_stimulus(self, stimulus_result: Any) -> None:
        if is_dataclass(stimulus_result):
            data: dict[str, Any] = asdict(stimulus_result)  # type: ignore[reportArgumentType]
        else:
            data = cast("dict[str, Any]", vars(stimulus_result))
        self._stimulus_handle.write(json.dumps(data) + "\n")  # type: ignore[reportOptionalMemberAccess]

    def save_topology(self, topology_data: dict[str, Any]) -> None:
        self._topology_data = topology_data

    def save_summary(self, summary: dict[str, Any]) -> None:
        self.summary.update(summary)
