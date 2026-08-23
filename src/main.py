"""Brain-5D command-line simulation entry point with dashboard integration.

This module runs the simulation and optionally starts the dashboard in the
main thread (to handle signals). The simulation runs in a daemon thread
so that the dashboard can control it via the OperatorBridge.

Usage:
    python -m src.main --config configs/poc_config.yaml
    python -m src.main --config configs/poc_config.yaml --no-dashboard
    python -m src.main --config configs/poc_config.yaml --observe --benchmark
"""

from __future__ import annotations

import argparse
import random
import statistics
import threading
from dataclasses import asdict
from pathlib import Path
from typing import Any, cast

from src.config.loader import load_config
from src.core import Brain5DConfig, NeuralNetwork
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
# Dashboard Integration – with None‑fallback
# ================================================================
_dashboard_available = False
_OperatorBridge = None
_serve_dashboard = None
_DashboardStateStore = None

try:
    from src.dashboard.operator_bridge import OperatorBridge as _OperatorBridge
    from src.dashboard.server import serve_dashboard as _serve_dashboard
    from src.dashboard.state import DashboardStateStore as _DashboardStateStore

    _dashboard_available = True
except ImportError as e:
    print(f"⚠️ Dashboard not available: {e}")


# ================================================================
# Simple Controller (Ersatz für RuntimeController)
# ================================================================


class SimpleController:
    """Einfacher Controller für das Dashboard – vermeidet Protokollkonflikte.

    Dieser Controller erfüllt die minimalen Anforderungen, die OperatorBridge
    an ein Controller-Objekt stellt. Er ist ein Ersatz für den eigentlichen
    RuntimeController, der aufgrund von Protokollkonflikten nicht verwendet wird.
    """

    def __init__(self, network: NeuralNetwork) -> None:
        self.network = network
        self._state = "idle"

    @property
    def telemetry(self) -> object:
        """Telemetrie-Stub, der die vom Dashboard erwarteten Attribute bereitstellt."""
        # Verwende ein einfaches Objekt mit Attributen statt einer dataclass
        return type(
            "TelemetryStub",
            (),
            {
                "controller_state": self._state,
                "tick": self.network.current_tick,
                "neurons": len(self.network.neurons),
                "synapses": self.network.synapse_count,
                "queue_depth": getattr(self.network, "queued_event_count", 0),
                "spikes_total": self.network.total_spikes,
                "spikes_this_batch": 0,
                "ticks_per_second": 0.0,
                "batch_duration_ms": 0.0,
                "requested_ticks": 0,
                "completed_ticks": 0,
                "last_error": None,
                "mean_energy": 0.0,
            },
        )()

    def start(self) -> None:
        self._state = "running"

    def pause(self) -> None:
        self._state = "paused"

    def resume(self) -> None:
        self._state = "running"

    def stop(self) -> None:
        self._state = "stopped"

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

    def configure(self, **_kwargs: Any) -> None:
        pass

    def snapshot(self) -> "ControlSnapshot":
        """Return a snapshot object with to_json() for the dashboard."""
        return ControlSnapshot(
            tick=self.network.current_tick,
            mode=self._state,
        )


class ControlSnapshot:
    """Lightweight snapshot for dashboard compatibility.

    The dashboard's DashboardControlService calls .to_json() on the
    object returned by controller.snapshot(). This class provides that
    contract without requiring the full runtime RuntimeController.
    """

    __slots__ = ("tick", "mode")

    def __init__(self, tick: int = 0, mode: str = "idle") -> None:
        self.tick = tick
        self.mode = mode

    def to_json(self) -> dict[str, object]:
        return {
            "tick": self.tick,
            "mode": self.mode,
            "queued_ticks": 0,
            "loop_size": 100,
            "delay_ms": 0.0,
            "last_batch_ticks": 0,
            "last_batch_ms": 0.0,
            "total_runtime_ms": 0.0,
            "fault": None,
            "can_snapshot": False,
        }


# ================================================================
# Helper Functions
# ================================================================


def sample_positions_excluding_poc(
    total: int,
    reserved: set[int],
    n: int,
    rng: random.Random,
) -> list[int]:
    """Sample free linear positions while preserving reserved PoC cells."""
    available = [idx for idx in range(total) if idx not in reserved]
    if n > len(available):
        raise ValueError(
            f"Not enough unreserved positions: need {n}, have {len(available)}"
        )
    return rng.sample(available, n)


def build_network(config_dict: dict[str, Any]) -> tuple[NeuralNetwork, random.Random]:
    """Build the network from configuration using the new Brain5DConfig."""
    # Convert dict to Brain5DConfig
    config = Brain5DConfig.from_dict(config_dict)
    rng = random.Random(int(config_dict.get("seed", 42)))

    # Create network
    network = NeuralNetwork(config, rng)

    dims = config.dimensions

    # Extract topology information from the original config dict
    topology = config_dict.get("topology", {})
    input_dim = topology.get("input", {}).get("dimension", "x")
    input_coord = topology.get("input", {}).get("coordinate", 0)
    output_dim = topology.get("output", {}).get("dimension", "x")
    output_coord = topology.get("output", {}).get("coordinate", dims[0] - 1)

    # Add reserved neurons (input, output, diagnostic)
    input_coord_5d = make_boundary_coord(dims, input_dim, input_coord)
    output_coord_5d = make_boundary_coord(dims, output_dim, output_coord)
    diag_coord = tuple(
        config_dict.get("diagnostics", {}).get("target_coord", (0, 0, 0, 0, 0))
    )

    reserved_coords = {input_coord_5d, output_coord_5d, diag_coord}
    reserved_indices = {coords_to_linear(coord, dims) for coord in reserved_coords}

    total_positions = 1
    for d in dims:
        total_positions *= d

    initial_neurons = int(config_dict.get("initial_neurons", 5000))

    chosen = sample_positions_excluding_poc(
        total_positions,
        reserved_indices,
        initial_neurons - len(reserved_coords),
        rng,
    )

    for idx in chosen:
        network.add_neuron(linear_to_5d(idx, dims))

    for coord in sorted(reserved_coords):
        network.add_neuron(coord)

    # Set input/output cells
    network.set_input_output_cells(
        input_dim,
        input_coord,
        output_dim,
        output_coord,
    )

    # Initialize random connections
    conn_per_neuron = config.network.initial_connections_per_neuron
    radius = config.network.neighbour_radius
    network.initialize_random_connections(conn_per_neuron, radius)

    return network, rng


def setup_learning(
    network: NeuralNetwork,
    config_dict: dict[str, Any],
) -> LearningEngine | None:
    """Set up and attach the learning engine if enabled."""
    try:
        learning = LearningEngine(network, config_dict)
        if learning.enabled:
            learning.attach()
            print("✅ Learning engine attached")
        return learning
    except Exception as e:
        print(f"⚠️ Learning engine setup failed: {e}")
        return None


def setup_homeostasis(
    network: NeuralNetwork,
    config_dict: dict[str, Any],
) -> HomeostasisEngine | None:
    """Set up and attach the homeostasis engine if enabled."""
    try:
        homeostasis = HomeostasisEngine(network, config_dict)
        if homeostasis.enabled:
            homeostasis.attach()
            print("✅ Homeostasis engine attached")
        return homeostasis
    except Exception as e:
        print(f"⚠️ Homeostasis engine setup failed: {e}")
        return None


def setup_observatory(
    network: NeuralNetwork,
    config_dict: dict[str, Any],
    spike_history: SpikeHistory,
    history: History,
    probes: ProbeManager,
) -> Any | None:
    """Set up the observatory if visualization is enabled."""
    vis = config_dict.get("visualization", {})
    if not vis.get("enabled", False):
        return None

    try:
        from src.visualization.observatory import Observatory

        observatory = Observatory(network, config_dict, spike_history, history, probes)
        print("✅ Observatory ready")
        return observatory
    except Exception as e:
        print(f"⚠️ Observatory setup failed: {e}")
        return None


# ================================================================
# Main
# ================================================================


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Brain 5D v0.5 - homeostatic self-regulation with dashboard"
    )
    parser.add_argument("--config", default="configs/poc_config.yaml")
    parser.add_argument("--observe", action="store_true")
    parser.add_argument("--benchmark", action="store_true")
    parser.add_argument("--no-dashboard", action="store_true")
    parser.add_argument("--no-learning", action="store_true")
    parser.add_argument("--no-homeostasis", action="store_true")
    parser.add_argument("--ticks", type=int, default=None)
    args = parser.parse_args()

    # Load configuration
    config_dict: dict[str, Any] = cast(dict[str, Any], load_config(args.config))
    if args.observe:
        config_dict["visualization"] = config_dict.get("visualization", {})
        config_dict["visualization"]["enabled"] = True
    if args.ticks is not None:
        config_dict["ticks"] = args.ticks

    print("🚀 Brain 5D - v0.5.0-alpha.1 with dashboard")
    print(f"📄 Config: {args.config}")

    # --- Build network ---
    network, rng = build_network(config_dict)

    # --- Setup engines ---
    learning = None if args.no_learning else setup_learning(network, config_dict)
    homeostasis = (
        None if args.no_homeostasis else setup_homeostasis(network, config_dict)
    )

    # --- Topology health ---
    health = cast(dict[str, Any], TopologyHealth(network).analyze())  # type: ignore[reportUnknownMemberType]

    # --- Telemetry ---
    telemetry_cfg = config_dict.get("telemetry", {})
    history = History(int(telemetry_cfg.get("history_ticks", 10000)))
    spike_history = SpikeHistory(int(telemetry_cfg.get("spike_history_ticks", 1000)))
    probes = ProbeManager(network, config_dict)

    # --- Stimulus ---
    stimulus = StimulusEngine(config_dict, rng)

    # --- Propagation ---
    propagation = PropagationAnalyzer(network.output_cells)

    # --- Diagnostic probe ---
    diag_target = tuple(
        config_dict.get("diagnostics", {}).get("target_coord", (0, 0, 0, 0, 0))
    )
    diag_id = next(
        (nid for nid in network.neurons if unpack_coords(nid) == diag_target),
        None,
    )
    if diag_id is not None:
        probes.add_probe(diag_id)

    # --- Observatory ---
    observatory = setup_observatory(
        network, config_dict, spike_history, history, probes
    )

    # ================================================================
    # Dashboard Setup – mit SimpleController
    # ================================================================
    dashboard_stop_event = threading.Event()
    operator_bridge = None
    state_store = None

    if not args.no_dashboard and _dashboard_available:
        try:
            # Controller erstellen
            controller = SimpleController(network)
            print("✅ SimpleController created")

            # OperatorBridge erstellen – Typkonflikt wird ignoriert
            operator_bridge = _OperatorBridge(  # type: ignore[reportArgumentType]
                controller=controller,  # type: ignore[reportUnknownVariableType]
                coordinator=None,
                plasticity=None,
            )
            print("✅ OperatorBridge created")

            # StateStore
            state_store = _DashboardStateStore()  # type: ignore[reportUnknownVariableType]

        except Exception as e:
            print(f"⚠️ Dashboard setup failed: {e}")
            operator_bridge = None
            state_store = None

    # ================================================================
    # Simulation in separatem Thread (einmal definiert)
    # ================================================================

    def run_simulation(stop_event: threading.Event) -> None:
        core_times: list[float] = []
        warmup = 100
        total_ticks = int(config_dict.get("ticks", 1000))

        print(
            f"🧠 Neurons={len(network.neurons)} Synapses={network.synapse_count} "
            f"Input={len(network.input_cells)} Output={len(network.output_cells)} "
            f"Learning={'on' if learning and learning.enabled else 'off'} "
            f"Homeostasis={'on' if homeostasis and homeostasis.enabled else 'off'}"
        )

        with RunArtifacts(config_dict) as artifacts:
            artifacts.save_topology(health)

            for _ in range(total_ticks):
                if stop_event.is_set():
                    print("⏹️ Simulation stopped by event")
                    break

                stim: StimulusResult = stimulus.apply(network, network.current_tick)  # type: ignore[reportUnknownMemberType]
                result = network.step()

                # Reward
                reward_cfg = config_dict.get("reward", {})
                if (
                    learning
                    and learning.params.reward_enabled
                    and reward_cfg.get("reward_source", "external") == "output_spike"
                    and result.output_spike_ids
                ):
                    learning.set_reward(
                        float(reward_cfg.get("output_spike_value", 1.0)),
                        result.tick,
                    )

                # Telemetry
                history.append_from_stepresult(result)  # type: ignore[reportUnknownMemberType]
                spike_history.append(result.tick, result.spike_ids)
                propagation.observe(stim, result)

                # Artifacts
                metric = history.get_all()[-1]  # type: ignore[reportUnknownVariableType]
                artifacts.log_metrics(metric)  # type: ignore[reportUnknownArgumentType]
                artifacts.log_spikes(result.tick, result.spike_ids)
                artifacts.log_stimulus(stim)

                # Benchmark
                if args.benchmark and result.tick >= warmup:
                    core_times.append(result.core_step_ms)

                # Observatory
                vis_cfg = config_dict.get("visualization", {})
                refresh_interval = vis_cfg.get("refresh_interval_ticks", 100)
                if observatory and (result.tick + 1) % refresh_interval == 0:
                    observatory.draw()

                # Console logging
                log_cfg = config_dict.get("logging", {})
                log_interval = log_cfg.get("interval_ticks", 100)
                if (result.tick + 1) % log_interval == 0:
                    print(
                        f"Tick {result.tick + 1:4d} | spikes={result.spikes_this_tick:4d} "
                        f"| total={result.total_spikes:6d} "
                        f"| queue={result.queued_events:5d} "
                        f"| {result.core_step_ms:.3f} ms"
                    )

            # Reports
            report = propagation.get_report()
            summary: dict[str, Any] = {
                "seed": config_dict.get("seed", 42),
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

    # ================================================================
    # Start simulation thread
    # ================================================================
    sim_thread = threading.Thread(
        target=run_simulation,
        args=(dashboard_stop_event,),
        daemon=True,
    )
    sim_thread.start()

    # ================================================================
    # Dashboard im Hauptthread starten (falls aktiviert)
    # ================================================================
    if (
        not args.no_dashboard
        and _dashboard_available
        and operator_bridge is not None
        and state_store is not None
    ):
        try:
            snapshot_path = (
                Path("artifacts/latest.b5d") if Path("artifacts").exists() else None
            )
            docs_root = Path("docs") if Path("docs").exists() else None
            research_root = Path("research") if Path("research").exists() else None

            print("🧠 Starting Brain-5D dashboard on http://127.0.0.1:8765")

            # Die `type: ignore` muss auf derselben Zeile wie der Aufruf stehen
            _serve_dashboard(host="127.0.0.1", port=8765, state=state_store, snapshot_path=snapshot_path, structural_bridge=operator_bridge, docs_root=docs_root, research_root=research_root)  # type: ignore[reportOptionalCall, call-arg, operator]

        except KeyboardInterrupt:
            print("\n⏹️ Dashboard interrupted, stopping simulation...")
        finally:
            dashboard_stop_event.set()
            sim_thread.join(timeout=2)
    else:
        # Kein Dashboard – warte auf Simulation
        sim_thread.join()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
