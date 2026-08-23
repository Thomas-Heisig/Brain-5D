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
# Canonical Runtime Controller
# ================================================================
from src.controller.runtime import RuntimeController as _RuntimeController

# ================================================================
# Snapshot Writer
# ================================================================
from src.storage import B5DSnapshotWriter

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
    # Canonical RuntimeController Setup
    # ================================================================
    dashboard_stop_event = threading.Event()
    operator_bridge = None
    state_store = None
    controller = None

    # Telemetry and logging state (shared via closure)
    core_times: list[float] = []
    warmup = 100

    # Snapshot path
    _snapshot_dir = Path("artifacts")
    _snapshot_dir.mkdir(parents=True, exist_ok=True)
    _snapshot_path = _snapshot_dir / "latest.b5d"
    _snapshot_temp = _snapshot_dir / "latest.b5d.tmp"

    # Snapshot writer
    _snapshot_writer = B5DSnapshotWriter(restart_capable=True)

    def _write_snapshot() -> None:
        """Write a .b5d snapshot atomically (temp file → validate → rename)."""
        try:
            # Collect metadata
            git_commit = "unknown"
            git_dirty = True
            try:
                import subprocess
                result = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    capture_output=True, text=True, timeout=5,
                    cwd=Path(__file__).resolve().parents[1],
                )
                if result.returncode == 0:
                    git_commit = result.stdout.strip()
                dirty_result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    capture_output=True, text=True, timeout=5,
                    cwd=Path(__file__).resolve().parents[1],
                )
                git_dirty = bool(dirty_result.stdout.strip())
            except Exception:
                pass

            metadata: dict[str, object] = {
                "type": "brain5d-snapshot",
                "version": "0.5.0-alpha.5",
                "tick": network.current_tick,
                "neuron_count": len(network.neurons),
                "synapse_count": network.synapse_count,
                "dimensions": list(network.dimensions),
                "seed": config_dict.get("seed", 42),
                "git_commit": git_commit,
                "git_dirty": git_dirty,
                "config": str(args.config),
            }

            # Write to temp file
            _snapshot_writer.write(
                str(_snapshot_temp),
                network,
                metadata=metadata,
            )

            # Validate written file (reader must be closed before rename on Windows)
            from src.storage.b5d import B5DReader
            reader = B5DReader(str(_snapshot_temp))
            try:
                reader.validate_invariants(full_scan=False)
            finally:
                reader.close()

            # Atomic rename
            _snapshot_temp.replace(_snapshot_path)

            # Preserve immutable historical snapshot with timestamp
            import time as _time
            tick = network.current_tick
            ts = _time.strftime("%Y%m%d_%H%M%S")
            historical = _snapshot_dir / f"snapshot_t{tick}_{ts}.b5d"
            try:
                import shutil
                shutil.copy2(_snapshot_path, historical)
            except Exception:
                pass

        except Exception as exc:
            print(f"⚠️ Snapshot write failed: {type(exc).__name__}: {exc}")
            # Clean up temp file on failure
            try:
                _snapshot_temp.unlink(missing_ok=True)
            except Exception:
                pass

    try:
        controller = _RuntimeController(
            network=network,
            homeostasis=None,  # Homeostasis is attached as post-step hook
            batch_size=10,
            loop_delay_ms=0.0,
            telemetry_interval_ticks=10,
            snapshot_callback=_write_snapshot,
        )
        print("✅ Canonical RuntimeController created (idle)")

        # Shared state for stimulus result (set by pre-hook, read by post-hook)
        _last_stim: list[StimulusResult | None] = [None]

        # Register pre-tick hook for stimulus
        def _pre_tick(tick: int) -> None:
            if dashboard_stop_event.is_set():
                return
            _last_stim[0] = stimulus.apply(network, tick)  # type: ignore[reportUnknownMemberType]

        controller.add_pre_hook(_pre_tick)

        # Register post-tick hook for telemetry, artifacts, logging, dashboard
        def _on_tick(tick: int, result: Any) -> None:
            if dashboard_stop_event.is_set():
                return
            stim_result = _last_stim[0]

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
            if stim_result is not None:
                propagation.observe(stim_result, result)

            # Artifacts
            metric = history.get_all()[-1]  # type: ignore[reportUnknownVariableType]
            artifacts.log_metrics(metric)  # type: ignore[reportUnknownArgumentType]
            artifacts.log_spikes(result.tick, result.spike_ids)
            if stim_result is not None:
                artifacts.log_stimulus(stim_result)

            # Benchmark
            if args.benchmark and result.tick >= warmup:
                core_times.append(result.core_step_ms)

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

            # Dashboard state publishing (every tick for live updates)
            if state_store is not None:
                try:
                    from src.dashboard.models import (
                        DashboardSnapshot,
                        HomeostasisMetrics,
                        LearningMetrics,
                        NetworkMetrics,
                        SelfOrganizationMetrics,
                        SpikeMetrics,
                        StorageMetrics,
                        SystemMetrics,
                    )

                    learning_stats = learning.stats if learning is not None else None
                    homeo_stats = homeostasis.stats if homeostasis is not None else None

                    snapshot = DashboardSnapshot(
                        status="running",
                        version="0.5.0-alpha.5",
                        system=SystemMetrics(
                            tick=result.tick,
                            neurons=len(network.neurons),
                            synapses=result.total_synapses,
                            spikes_total=result.total_spikes,
                            spikes_last_tick=result.spikes_this_tick,
                            core_step_ms=result.core_step_ms,
                            mean_energy=result.mean_energy,
                        ),
                        learning=LearningMetrics(
                            stdp_updates=getattr(learning_stats, "stdp_weight_updates", 0),
                            reward_updates=getattr(learning_stats, "reward_weight_updates", 0),
                            rewards_received=getattr(learning_stats, "rewards_received", 0),
                            rewards_applied=getattr(learning_stats, "rewards_applied", 0),
                            pending_rewards=getattr(learning_stats, "pending_rewards", 0),
                            update_ms=getattr(learning_stats, "last_update_ms", 0.0),
                        ),
                        storage=StorageMetrics(
                            queue_depth=result.queued_events,
                            queue_capacity=0,
                            deltas_written=0,
                            bytes_written=0,
                            write_latency_ms=0.0,
                            commit_latency_ms=0.0,
                            journal_size_bytes=0,
                            dropped_batches=0,
                        ),
                        self_organization=SelfOrganizationMetrics(
                            neurons_created=0,
                            neurons_removed=0,
                            synapses_created=0,
                            synapses_pruned=0,
                        ),
                        homeostasis=HomeostasisMetrics(
                            enabled=getattr(homeo_stats, "enabled", False),
                            target_rate_hz=getattr(homeo_stats, "target_rate_hz", 0.0),
                            actual_rate_hz=getattr(homeo_stats, "mean_rate_hz", 0.0),
                            rate_error_hz=getattr(homeo_stats, "mean_rate_error_hz", 0.0),
                            mean_rate_hz=getattr(homeo_stats, "mean_rate_hz", 0.0),
                            mean_rate_error_hz=getattr(homeo_stats, "mean_rate_error_hz", 0.0),
                            mean_threshold_adaptation=getattr(homeo_stats, "mean_threshold_adaptation", 0.0),
                            target_energy=getattr(homeo_stats, "target_energy", 0.0),
                            mean_energy=getattr(homeo_stats, "mean_energy", 0.0),
                            mean_energy_error=getattr(homeo_stats, "mean_energy_error", 0.0),
                            active_neurons=getattr(homeo_stats, "active_neurons", 0),
                            updates=getattr(homeo_stats, "updates", 0),
                        ),
                        spikes=SpikeMetrics(
                            total_spikes=result.total_spikes,
                            active_neurons=len(result.spike_ids),
                            mean_firing_rate_hz=0.0,
                            burst_index=0.0,
                            synchrony=0.0,
                            spike_count_last_tick=result.spikes_this_tick,
                        ),
                        network=NetworkMetrics(
                            tick=result.tick,
                            neuron_count=len(network.neurons),
                            synapse_count=result.total_synapses,
                            active_neurons=len(result.spike_ids),
                            silent_neurons=len(network.neurons) - len(result.spike_ids),
                            mean_firing_rate_hz=0.0,
                            burst_index=0.0,
                            synchrony=0.0,
                            mean_energy=result.mean_energy,
                            mean_threshold_adaptation=0.0,
                            e_i_ratio=0.0,
                            clustering_coefficient=0.0,
                            mean_path_length=0.0,
                        ),
                    )
                    state_store.publish(snapshot)
                except Exception:
                    pass  # Dashboard publishing must never break simulation

        controller.add_hook(_on_tick)

        # --- Observatory ---
        vis_cfg = config_dict.get("visualization", {})
        refresh_interval = vis_cfg.get("refresh_interval_ticks", 100)
        if observatory:
            controller.add_hook(lambda t, r=None: observatory.draw() if (t + 1) % refresh_interval == 0 else None)

    except Exception as e:
        print(f"⚠️ RuntimeController setup failed: {e}")
        controller = None

    # ================================================================
    # OperatorBridge & Dashboard Setup
    # ================================================================
    if not args.no_dashboard and _dashboard_available and controller is not None:
        try:
            operator_bridge = _OperatorBridge(
                controller=controller,
                coordinator=None,
                plasticity=None,
            )
            print("✅ OperatorBridge created with canonical RuntimeController")

            state_store = _DashboardStateStore()

        except Exception as e:
            print(f"⚠️ Dashboard setup failed: {e}")
            operator_bridge = None
            state_store = None

    # ================================================================
    # Artifacts (shared by hooks)
    # ================================================================
    artifacts_ctx = RunArtifacts(config_dict)
    artifacts = artifacts_ctx.__enter__()
    artifacts.save_topology(health)

    print(
        f"🧠 Neurons={len(network.neurons)} Synapses={network.synapse_count} "
        f"Input={len(network.input_cells)} Output={len(network.output_cells)} "
        f"Learning={'on' if learning and learning.enabled else 'off'} "
        f"Homeostasis={'on' if homeostasis and homeostasis.enabled else 'off'}"
        f"Controller={'idle' if controller else 'none'}"
    )

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
            # Write initial snapshot so the heatmap source has real data
            print("💾 Writing initial .b5d snapshot...")
            _write_snapshot()

            docs_root = Path("docs") if Path("docs").exists() else None
            research_root = Path("research") if Path("research").exists() else None

            print("🧠 Starting Brain-5D dashboard on http://127.0.0.1:8765")
            print("⏸️  Simulation starts in idle state. Use dashboard controls to run.")

            _serve_dashboard(host="127.0.0.1", port=8765, state=state_store, snapshot_path=_snapshot_path, structural_bridge=operator_bridge, docs_root=docs_root, research_root=research_root)  # type: ignore[reportOptionalCall, call-arg, operator]

        except KeyboardInterrupt:
            print("\n⏹️ Dashboard interrupted, stopping simulation...")
        finally:
            if controller is not None:
                controller.stop()
    else:
        # Kein Dashboard – starte Simulation mit konfigurierten Ticks
        total_ticks = int(config_dict.get("ticks", 1000))
        print(f"▶️  Running {total_ticks} ticks (no dashboard)...")
        controller.run_ticks(total_ticks)
        # Write final snapshot
        print("💾 Writing final .b5d snapshot...")
        _write_snapshot()

    # ================================================================
    # Final summary
    # ================================================================
    report = propagation.get_report()
    summary: dict[str, Any] = {
        "seed": config_dict.get("seed", 42),
        "ticks": network.current_tick,
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
    artifacts_ctx.__exit__(None, None, None)

    # Final dashboard state publication
    if state_store is not None:
        try:
            from src.dashboard.models import (
                DashboardSnapshot,
                HomeostasisMetrics,
                LearningMetrics,
                NetworkMetrics,
                SpikeMetrics,
                SystemMetrics,
            )

            learning_stats = learning.stats if learning is not None else None
            homeo_stats = homeostasis.stats if homeostasis is not None else None

            final_snapshot = DashboardSnapshot(
                status="completed",
                version="0.5.0-alpha.5",
                system=SystemMetrics(
                    tick=network.current_tick,
                    neurons=len(network.neurons),
                    synapses=network.synapse_count,
                    spikes_total=network.total_spikes,
                ),
                learning=LearningMetrics(
                    stdp_updates=getattr(learning_stats, "stdp_weight_updates", 0),
                    reward_updates=getattr(learning_stats, "reward_weight_updates", 0),
                    rewards_received=getattr(learning_stats, "rewards_received", 0),
                    rewards_applied=getattr(learning_stats, "rewards_applied", 0),
                    pending_rewards=getattr(learning_stats, "pending_rewards", 0),
                ),
                homeostasis=HomeostasisMetrics(
                    enabled=getattr(homeo_stats, "enabled", False),
                    target_rate_hz=getattr(homeo_stats, "target_rate_hz", 0.0),
                    actual_rate_hz=getattr(homeo_stats, "mean_rate_hz", 0.0),
                    rate_error_hz=getattr(homeo_stats, "mean_rate_error_hz", 0.0),
                    mean_rate_hz=getattr(homeo_stats, "mean_rate_hz", 0.0),
                    mean_rate_error_hz=getattr(homeo_stats, "mean_rate_error_hz", 0.0),
                    mean_threshold_adaptation=getattr(homeo_stats, "mean_threshold_adaptation", 0.0),
                    target_energy=getattr(homeo_stats, "target_energy", 0.0),
                    mean_energy=getattr(homeo_stats, "mean_energy", 0.0),
                    mean_energy_error=getattr(homeo_stats, "mean_energy_error", 0.0),
                    active_neurons=getattr(homeo_stats, "active_neurons", 0),
                    updates=getattr(homeo_stats, "updates", 0),
                ),
                spikes=SpikeMetrics(
                    total_spikes=network.total_spikes,
                    spike_count_last_tick=0,
                ),
                network=NetworkMetrics(
                    tick=network.current_tick,
                    neuron_count=len(network.neurons),
                    synapse_count=network.synapse_count,
                ),
            )
            state_store.publish(final_snapshot)
        except Exception:
            pass

    print("\n📈 Propagation:", report)
    if learning and learning.enabled:
        print("📚 Learning:", learning.stats)
    if homeostasis and homeostasis.enabled:
        print("⚖️ Homeostasis:", homeostasis.stats)

    if observatory:
        print("🔭 Observatory running — close window to exit")
        observatory.block_until_closed()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
