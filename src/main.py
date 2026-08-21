"""Brain-5D command-line simulation entry point with dashboard integration."""

from __future__ import annotations

import argparse
import random
import statistics
import threading
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, cast

from src.config.loader import load_config
from src.core.network import NeuralNetwork
from src.core.spatial_index import (
    coords_to_linear,
    linear_to_5d,
    make_boundary_coord,
    unpack_coords,
)
from src.diagnostics.propagation import PropagationAnalyzer
from src.diagnostics.stimulus import StimulusEngine, StimulusResult
from src.diagnostics.topology_health import TopologyHealth
from src.homeostasis import HomeostasisEngine
from src.learning.learning_engine import LearningEngine
from src.telemetry.history import History
from src.telemetry.probes import ProbeManager
from src.telemetry.spike_history import SpikeHistory
from src.utils.run_artifacts import RunArtifacts

# ================================================================
# Dashboard Integration
# ================================================================
try:
    from src.controller.runtime import RuntimeController
    from src.dashboard.operator_bridge import OperatorBridge
    from src.dashboard.server import serve_dashboard
    from src.dashboard.state import DashboardStateStore
    from src.dashboard.models import DashboardSnapshot

    DASHBOARD_AVAILABLE = True
except ImportError as e:
    DASHBOARD_AVAILABLE = False
    print(f"⚠️ Dashboard not available: {e}")


# ================================================================
# SimpleController (Fallback)
# ================================================================

@dataclass
class TelemetryStub:
    controller_state: str = "idle"
    tick: int = 0
    ticks_per_second: float = 0.0
    batch_duration_ms: float = 0.0
    spikes_this_batch: int = 0
    neurons: int = 0
    synapses: int = 0
    queue_depth: int = 0
    requested_ticks: int = 0
    completed_ticks: int = 0
    last_error: str | None = None
    mean_energy: float = 0.0
    spikes_total: int = 0


class SimpleController:
    """Simple controller for OperatorBridge."""

    def __init__(self, network: NeuralNetwork) -> None:
        self.network = network
        self._state = "idle"
        self._telemetry = TelemetryStub()

    @property
    def telemetry(self) -> TelemetryStub:
        self._telemetry.tick = self.network.current_tick
        self._telemetry.neurons = len(self.network.neurons)
        self._telemetry.synapses = self.network.synapse_count
        self._telemetry.spikes_total = self.network.total_spikes
        return self._telemetry

    def start(self) -> None:
        self._state = "running"
        self._telemetry.controller_state = "running"

    def pause(self) -> None:
        self._state = "paused"
        self._telemetry.controller_state = "paused"

    def resume(self) -> None:
        self._state = "running"
        self._telemetry.controller_state = "running"

    def stop(self) -> None:
        self._state = "stopped"
        self._telemetry.controller_state = "stopped"

    def step_once(self) -> None:
        self.network.step()

    def step(self, ticks: int = 1) -> None:
        for _ in range(ticks):
            self.network.step()

    def run_ticks(self, ticks: int) -> None:
        self.start()
        for _ in range(ticks):
            self.network.step()
        self.pause()

    def request_snapshot(self) -> None:
        pass

    def configure(self, **kwargs: Any) -> None:
        pass

    def snapshot(self) -> dict[str, Any]:
        return {"tick": self.network.current_tick}


# ================================================================
# Helper Functions
# ================================================================

def sample_positions_excluding_poc(total: int, reserved: set[int], n: int, rng: random.Random) -> list[int]:
    available = [idx for idx in range(total) if idx not in reserved]
    if n > len(available):
        raise ValueError(f"Not enough unreserved positions: need {n}, have {len(available)}")
    return rng.sample(available, n)


def build_network(config: dict[str, Any]) -> tuple[NeuralNetwork, random.Random]:
    rng = random.Random(int(config["seed"]))
    network = NeuralNetwork(config, rng)

    dims = tuple(config["dimensions"])
    total = 1
    for dim in dims:
        total *= dim

    topology = config["topology"]
    input_coord = make_boundary_coord(dims, topology["input"]["dimension"], topology["input"]["coordinate"])
    output_coord = make_boundary_coord(dims, topology["output"]["dimension"], topology["output"]["coordinate"])
    diag_coord = tuple(config["diagnostics"]["target_coord"])

    reserved_coords = {input_coord, output_coord, diag_coord}
    reserved_indices = {coords_to_linear(coord, dims) for coord in reserved_coords}

    chosen = sample_positions_excluding_poc(
        total, reserved_indices, int(config["initial_neurons"]) - len(reserved_coords), rng
    )

    for idx in chosen:
        network.add_neuron(linear_to_5d(idx, dims))
    for coord in sorted(reserved_coords):
        network.add_neuron(coord)

    network.set_input_output_cells(
        topology["input"]["dimension"],
        topology["input"]["coordinate"],
        topology["output"]["dimension"],
        topology["output"]["coordinate"],
    )

    network.initialize_random_connections(
        int(config["network"]["initial_connections_per_neuron"]),
        float(config["network"]["neighbour_radius"]),
    )

    return network, rng


def setup_learning(network: NeuralNetwork, config: dict[str, Any]) -> LearningEngine | None:
    try:
        learning = LearningEngine(network, config)
        if learning.enabled:
            learning.attach()
            print("✅ Learning engine attached")
        return learning
    except Exception as e:
        print(f"⚠️ Learning engine setup failed: {e}")
        return None


def setup_homeostasis(network: NeuralNetwork, config: dict[str, Any]) -> HomeostasisEngine | None:
    try:
        homeostasis = HomeostasisEngine(network, config)
        if homeostasis.enabled:
            homeostasis.attach()
            print("✅ Homeostasis engine attached")
        return homeostasis
    except Exception as e:
        print(f"⚠️ Homeostasis engine setup failed: {e}")
        return None


def setup_observatory(network: NeuralNetwork, config: dict[str, Any], spike_history: SpikeHistory, history: History, probes: ProbeManager) -> Any | None:
    if not config["visualization"].get("enabled"):
        return None
    try:
        from src.visualization.observatory import Observatory
        observatory = Observatory(network, config, spike_history, history, probes)
        print("✅ Observatory ready")
        return observatory
    except Exception as e:
        print(f"⚠️ Observatory setup failed: {e}")
        return None


# ================================================================
# Main
# ================================================================

def main() -> int:
    parser = argparse.ArgumentParser(description="Brain 5D v0.5 - homeostatic self-regulation with dashboard")
    parser.add_argument("--config", default="configs/poc_config.yaml")
    parser.add_argument("--observe", action="store_true")
    parser.add_argument("--benchmark", action="store_true")
    parser.add_argument("--no-dashboard", action="store_true")
    parser.add_argument("--no-learning", action="store_true")
    parser.add_argument("--no-homeostasis", action="store_true")
    parser.add_argument("--ticks", type=int, default=None)
    args = parser.parse_args()

    config = cast(dict[str, Any], load_config(args.config))
    if args.observe:
        config["visualization"]["enabled"] = True
    if args.ticks is not None:
        config["simulation"]["ticks"] = args.ticks

    print("🚀 Brain 5D - v0.5.0-alpha.1 with dashboard")
    print(f"📄 Config: {args.config}")

    # Build network
    network, rng = build_network(config)

    # Setup engines
    learning = None if args.no_learning else setup_learning(network, config)
    homeostasis = None if args.no_homeostasis else setup_homeostasis(network, config)

    # Topology health
    health = cast(dict[str, Any], TopologyHealth(network).analyze())

    # Telemetry
    history = History(int(config["telemetry"]["history_ticks"]))
    spike_history = SpikeHistory(int(config["telemetry"]["spike_history_ticks"]))
    probes = ProbeManager(network, config)

    # Stimulus
    stimulus = StimulusEngine(config, rng)

    # Propagation
    propagation = PropagationAnalyzer(network.output_cells)

    # Diagnostic probe
    diag_target = tuple(config["diagnostics"]["target_coord"])
    diag_id = next((nid for nid in network.neurons if unpack_coords(nid) == diag_target), None)
    if diag_id is not None:
        probes.add_probe(diag_id)

    # Observatory
    observatory = setup_observatory(network, config, spike_history, history, probes)

    # ================================================================
    # Dashboard Setup - WIRD IM HAUPTTHREAD GESTARTET
    # ================================================================
    dashboard_stop_event = threading.Event()
    controller = None
    operator_bridge = None
    state_store = DashboardStateStore()

    if not args.no_dashboard and DASHBOARD_AVAILABLE:
        try:
            # Controller erstellen
            try:
                controller = RuntimeController(network=network)
                print("✅ Using RuntimeController")
            except Exception as e:
                print(f"⚠️ RuntimeController failed, using SimpleController: {e}")
                controller = SimpleController(network)
                print("✅ Using SimpleController")

            # OperatorBridge erstellen
            operator_bridge = OperatorBridge(
                controller=controller,
                coordinator=None,
                plasticity=None,
            )
            print("✅ OperatorBridge created")

            # Snapshot & Docs
            snapshot_path = Path("artifacts/latest.b5d") if Path("artifacts").exists() else None
            docs_root = Path("docs") if Path("docs").exists() else None

            # Dashboard im Hauptthread starten
            print("🧠 Starting Brain-5D dashboard on http://127.0.0.1:8765")
            serve_dashboard(
                host="127.0.0.1",
                port=8765,
                state=state_store,
                snapshot_path=snapshot_path,
                structural_bridge=operator_bridge,  # <-- HIER WIRD DIE BRIDGE ÜBERGEBEN!
                docs_root=docs_root,
            )
            # WICHTIG: serve_dashboard blockiert den Thread!
            # D.h. alles was danach kommt, läuft erst nach Beendigung des Dashboards.
            # Deshalb starten wir die Simulation in einem separaten Thread.
        except Exception as e:
            print(f"⚠️ Dashboard could not be started: {e}")

    # ================================================================
    # Simulation (in separatem Thread, wenn Dashboard läuft)
    # ================================================================

    def run_simulation() -> None:
        core_times: list[float] = []
        warmup = 100
        total_ticks = int(config["simulation"]["ticks"])

        print(
            f"🧠 Neurons={len(network.neurons)} Synapses={network.synapse_count} "
            f"Input={len(network.input_cells)} Output={len(network.output_cells)} "
            f"Learning={'on' if learning and learning.enabled else 'off'} "
            f"Homeostasis={'on' if homeostasis and homeostasis.enabled else 'off'}"
        )

        with RunArtifacts(config) as artifacts:
            artifacts.save_topology(health)

            for tick_idx in range(total_ticks):
                stim: StimulusResult = stimulus.apply(network, network.current_tick)
                result = network.step()

                # Reward
                reward_cfg = config.get("reward", {})
                if (
                    learning
                    and learning.params.reward_enabled
                    and reward_cfg.get("reward_source", "external") == "output_spike"
                    and result.output_spike_ids
                ):
                    learning.set_reward(float(reward_cfg.get("output_spike_value", 1.0)), result.tick)

                # Telemetry
                history.append_from_stepresult(result)
                spike_history.append(result.tick, result.spike_ids)
                propagation.observe(stim, result)

                # Artifacts
                metric: dict[str, Any] = history.get_all()[-1]
                artifacts.log_metrics(metric)
                artifacts.log_spikes(result.tick, result.spike_ids)
                artifacts.log_stimulus(stim)

                # Benchmark
                if args.benchmark and result.tick >= warmup:
                    core_times.append(result.core_step_ms)

                # Observatory
                if (
                    observatory
                    and (result.tick + 1) % int(config["visualization"]["refresh_interval_ticks"]) == 0
                ):
                    observatory.draw()

                # Console logging
                if (result.tick + 1) % int(config["logging"]["interval_ticks"]) == 0:
                    print(
                        f"Tick {result.tick + 1:4d} | spikes={result.spikes_this_tick:4d} "
                        f"| total={result.total_spikes:6d} "
                        f"| queue={result.queued_events:5d} "
                        f"| {result.core_step_ms:.3f} ms"
                    )

            # Reports
            report = propagation.get_report()
            summary: dict[str, Any] = {
                "seed": config["seed"],
                "ticks": total_ticks,
                "final_neurons": len(network.neurons),
                "final_synapses": network.synapse_count,
                "total_spikes": network.total_spikes,
                "topology": health,
                "propagation": asdict(report),
            }

            if learning and learning.enabled:
                summary["learning"] = asdict(learning.stats)
            if homeostasis and homeostasis.enabled:
                summary["homeostasis"] = asdict(homeostasis.stats)

            if core_times:
                ordered = sorted(core_times)
                p95 = ordered[max(0, int(len(ordered) * 0.95) - 1)]
                summary["benchmark"] = {
                    "mean_ms": statistics.mean(core_times),
                    "median_ms": statistics.median(core_times),
                    "p95_ms": p95,
                }
                print("📊 Benchmark:", summary["benchmark"])

            artifacts.save_summary(summary)

        print("\n📈 Propagation:", report)
        if learning and learning.enabled:
            print("📚 Learning:", learning.stats)
        if homeostasis and homeostasis.enabled:
            print("⚖️ Homeostasis:", homeostasis.stats)

        if observatory:
            print("🔭 Observatory running — close window to exit")
            observatory.block_until_closed()

        dashboard_stop_event.set()

    # Simulation starten
    sim_thread = threading.Thread(target=run_simulation, daemon=True)
    sim_thread.start()

    # Wenn Dashboard nicht läuft, wartet der Hauptthread auf die Simulation
    if args.no_dashboard or not DASHBOARD_AVAILABLE:
        sim_thread.join()

    # Wenn Dashboard läuft, wird der Hauptthread von serve_dashboard blockiert.
    # Die Simulation läuft parallel.

    return 0


if __name__ == "__main__":
    raise SystemExit(main())