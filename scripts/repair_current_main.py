"""Repair verified CI and experiment-observability defects on the current main tree."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"Target block not found in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def patch_server() -> None:
    replace_once(
        Path("src/dashboard/server.py"),
        """            experiment_id = body.get("experiment_id")
            if not isinstance(experiment_id, str) or not experiment_id.strip():
                experiment_id = ExperimentWorkflowService(source.root()).catalog()[
                    "next_experiment_id"
                ]
            protocol_result = execute_stdp_pair_experiment(
                experiment_id=experiment_id.strip(), research_root=source.root()
            )""",
        """            experiment_id_value = body.get("experiment_id")
            if isinstance(experiment_id_value, str) and experiment_id_value.strip():
                experiment_id = experiment_id_value.strip()
            else:
                next_experiment_id = ExperimentWorkflowService(source.root()).catalog().get(
                    "next_experiment_id"
                )
                if not isinstance(next_experiment_id, str) or not next_experiment_id.strip():
                    raise InvalidRequestError("No generated experiment ID is available.")
                experiment_id = next_experiment_id.strip()
            protocol_result = execute_stdp_pair_experiment(
                experiment_id=experiment_id, research_root=source.root()
            )""",
    )


def patch_probe() -> None:
    path = Path("src/research/network_probe.py")
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "    network_state_digest_after: str | None = None\n",
        "    network_state_digest_after: str | None = None\n"
        "    ticks_executed: int = 0\n"
        "    delivered_synaptic_events: int = 0\n"
        "    synaptic_activity_ticks: int = 0\n"
        "    max_synaptic_current_targets: int = 0\n"
        "    total_synapses: int = 0\n",
        1,
    )
    text = text.replace(
        '            "network_state_digest_after": self.network_state_digest_after,\n',
        '            "network_state_digest_after": self.network_state_digest_after,\n'
        '            "ticks_executed": self.ticks_executed,\n'
        '            "delivered_synaptic_events": self.delivered_synaptic_events,\n'
        '            "synaptic_activity_ticks": self.synaptic_activity_ticks,\n'
        '            "max_synaptic_current_targets": self.max_synaptic_current_targets,\n'
        '            "total_synapses": self.total_synapses,\n',
        1,
    )
    old = """        spike_sequence: list[tuple[int, int]] = []

        for tick in range(self.max_ticks):
            result = runtime.step()
            raw_ids = result.get("output_spike_ids", ())
            spike_ids = tuple(int(value) for value in raw_ids)
            if spike_ids:
                spike_sequence.extend((tick, neuron_id) for neuron_id in spike_ids)
                response_ticks.append(tick)
                response_neurons.update(spike_ids)
                total_spikes += len(spike_ids)
                peak_rate = max(peak_rate, float(len(spike_ids)))
                if (
                    self.source_neuron in spike_ids
                    and return_latency is None
                    and tick > 0
                ):
                    return_latency = tick
                if tick > 0 and self.source_neuron in spike_ids:
                    recurrent_events += 1
"""
    new = """        spike_sequence: list[tuple[int, int]] = []
        ticks_executed = 0
        delivered_synaptic_events = 0
        synaptic_activity_ticks = 0
        max_synaptic_current_targets = 0
        total_synapses = 0

        for tick in range(self.max_ticks):
            result = runtime.step()
            ticks_executed = tick + 1
            raw_ids = result.get("spike_ids")
            if raw_ids is None:
                raw_ids = result.get("output_spike_ids", ())
            spike_ids = tuple(int(value) for value in raw_ids)
            output_ids = tuple(
                int(value) for value in result.get("output_spike_ids", spike_ids)
            )
            delivered = int(result.get("delivered_events", 0) or 0)
            synaptic_targets = int(result.get("synaptic_current_targets", 0) or 0)
            delivered_synaptic_events += delivered
            if delivered > 0 or synaptic_targets > 0:
                synaptic_activity_ticks += 1
            max_synaptic_current_targets = max(
                max_synaptic_current_targets, synaptic_targets
            )
            total_synapses = max(
                total_synapses, int(result.get("total_synapses", 0) or 0)
            )
            if spike_ids:
                spike_sequence.extend((tick, neuron_id) for neuron_id in spike_ids)
                response_neurons.update(spike_ids)
                total_spikes += len(spike_ids)
                peak_rate = max(peak_rate, float(len(spike_ids)))
                if (
                    self.source_neuron in spike_ids
                    and return_latency is None
                    and tick > 0
                ):
                    return_latency = tick
                if tick > 0 and self.source_neuron in spike_ids:
                    recurrent_events += 1
            if output_ids:
                response_ticks.append(tick)
"""
    if old not in text:
        raise RuntimeError("Network probe target block not found")
    text = text.replace(old, new, 1)
    target = "            network_state_digest_after=after,\n        )\n"
    replacement = (
        "            network_state_digest_after=after,\n"
        "            ticks_executed=ticks_executed,\n"
        "            delivered_synaptic_events=delivered_synaptic_events,\n"
        "            synaptic_activity_ticks=synaptic_activity_ticks,\n"
        "            max_synaptic_current_targets=max_synaptic_current_targets,\n"
        "            total_synapses=total_synapses,\n"
        "        )\n"
    )
    if target not in text:
        raise RuntimeError("Network probe result block not found")
    path.write_text(text.replace(target, replacement, 1), encoding="utf-8")


def patch_recurrence() -> None:
    replace_once(
        Path("src/research/experiment_suite.py"),
        """    if recurrence:
        network.connect(
            neurons[2], neurons[1], impulse_weight, 1, config=impulse_synapse_config
        )""",
        """    if recurrence:
        network.connect(
            neurons[2], neurons[0], impulse_weight, 1, config=impulse_synapse_config
        )""",
    )


def synchronize_test_count() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        capture_output=True,
        text=True,
        check=False,
    )
    output = f"{result.stdout}\n{result.stderr}"
    match = re.search(r"(\d+) tests collected", output)
    if match is None:
        raise RuntimeError("pytest did not report a collected-test count")
    count = match.group(1)
    path = Path("docs/08-roadmap/TODO.md")
    text = path.read_text(encoding="utf-8")
    text, changed = re.subn(
        r"- \[x\] Current test collection is \d+ tests[^\n]*",
        f"- [x] {count} tests collected on the current main tree.",
        text,
        count=1,
    )
    if changed != 1:
        text, changed = re.subn(
            r"- \[x\] \d+ tests collected[^\n]*",
            f"- [x] {count} tests collected on the current main tree.",
            text,
            count=1,
        )
    if changed != 1:
        raise RuntimeError("TODO test-count claim not found")
    path.write_text(text, encoding="utf-8")


def main() -> int:
    patch_server()
    patch_probe()
    patch_recurrence()
    synchronize_test_count()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
