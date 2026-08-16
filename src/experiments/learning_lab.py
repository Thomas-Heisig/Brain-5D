"""Deterministic end-to-end learning experiment for Brain 5D.

The experiment demonstrates a complete causal chain:

PRE spikes -> POST spike -> eligibility -> reward -> weight update -> changed response.

It intentionally lives outside the reference core and uses only public network and
learning APIs. The trained weights are evaluated in a fresh network so the reported
response change cannot be explained by residual neuron state.
"""

from __future__ import annotations

import argparse
import itertools
import random
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence, cast

import yaml

from src.core.network import NeuralNetwork
from src.learning.learning_engine import LearningEngine

Config = Mapping[str, Any]
Coord5D = tuple[int, int, int, int, int]


@dataclass(frozen=True, slots=True)
class LearningExperimentResult:
    """Summary of one deterministic system-level learning experiment."""

    training_trials: int
    presynaptic_neurons: int
    initial_mean_weight: float
    final_mean_weight: float
    mean_weight_delta: float
    rewards_received: int
    rewards_applied: int
    reward_weight_updates: int
    baseline_target_spiked: bool
    trained_target_spiked: bool
    baseline_target_peak_v: float
    trained_target_peak_v: float
    baseline_target_spike_tick: int | None
    trained_target_spike_tick: int | None

    @property
    def learned(self) -> bool:
        """Return whether training strengthened weights and changed target response."""
        return (
            self.final_mean_weight > self.initial_mean_weight
            and not self.baseline_target_spiked
            and self.trained_target_spiked
        )


def _experiment_config(config: Config) -> Mapping[str, Any]:
    section = config.get("learning_experiment", {})
    if not isinstance(section, Mapping):
        raise TypeError("learning_experiment config must be a mapping")
    return section


def _validated_dimensions(config: Config) -> Coord5D:
    raw = config.get("dimensions")
    if not isinstance(raw, Sequence) or len(raw) != 5:
        raise ValueError("dimensions must contain exactly five entries")
    dims = cast(Coord5D, tuple(int(value) for value in raw))
    if any(value <= 0 for value in dims):
        raise ValueError("all dimensions must be > 0")
    return dims


def _candidate_coords(dims: Coord5D) -> Iterable[Coord5D]:
    product = itertools.product(*(range(size) for size in dims))
    return (cast(Coord5D, coord) for coord in product)


def _build_convergent_network(
    config: Config,
    weight: float,
) -> tuple[NeuralNetwork, tuple[int, ...], int]:
    exp = _experiment_config(config)
    pre_count = int(exp.get("presynaptic_neurons", 48))
    if pre_count <= 0:
        raise ValueError("learning_experiment.presynaptic_neurons must be > 0")

    dims = _validated_dimensions(config)
    target_coord = cast(Coord5D, tuple(size - 1 for size in dims))
    available = [coord for coord in _candidate_coords(dims) if coord != target_coord]
    if pre_count > len(available):
        raise ValueError("not enough coordinates for requested presynaptic neurons")

    network = NeuralNetwork(dict(config), random.Random(int(config.get("seed", 42))))
    pre_ids = tuple(network.add_neuron(coord) for coord in available[:pre_count])
    target_id = network.add_neuron(target_coord)
    delay = int(exp.get("connection_delay_ticks", 1))
    for pre_id in pre_ids:
        network.connect(pre_id, target_id, float(weight), delay)
    network.output_cells.add(target_id)
    return network, pre_ids, target_id


def _advance_to_tick(network: NeuralNetwork, tick: int) -> None:
    if tick < network.current_tick:
        raise ValueError("cannot move network backwards in time")
    while network.current_tick < tick:
        network.step()


def _train(config: Config) -> tuple[tuple[float, ...], LearningEngine]:
    exp = _experiment_config(config)
    trials = int(exp.get("training_trials", 20))
    spacing = int(exp.get("trial_spacing_ticks", 25))
    pair_delay = int(exp.get("pair_delay_ticks", 5))
    drive = float(exp.get("drive_current", 100.0))
    reward_value = float(exp.get("reward_value", 1.0))
    initial_weight = float(exp.get("initial_weight", 0.05))

    if trials <= 0:
        raise ValueError("learning_experiment.training_trials must be > 0")
    if pair_delay <= 0:
        raise ValueError("learning_experiment.pair_delay_ticks must be > 0")
    if spacing <= pair_delay:
        raise ValueError("trial_spacing_ticks must be greater than pair_delay_ticks")

    network, pre_ids, target_id = _build_convergent_network(config, initial_weight)
    learning = LearningEngine(network, config)
    if not learning.params.reward_enabled:
        raise ValueError("learning experiment requires reward.enabled=true")
    learning.attach()

    for trial in range(trials):
        pre_tick = trial * spacing
        post_tick = pre_tick + pair_delay
        _advance_to_tick(network, pre_tick)
        for pre_id in pre_ids:
            network.inject_current(pre_id, drive)
        pre_result = network.step()
        if not set(pre_ids).issubset(pre_result.spike_ids):
            raise RuntimeError("training drive failed to spike all presynaptic neurons")

        _advance_to_tick(network, post_tick)
        network.inject_current(target_id, drive)
        post_result = network.step()
        if target_id not in post_result.spike_ids:
            raise RuntimeError("training drive failed to spike target neuron")

        learning.set_reward(reward_value, post_result.tick)
        # Each trial is an independent timing episode. Weight changes persist,
        # while timing/eligibility state is cleared to avoid cross-trial pairing.
        learning.reset_state()

    weights = tuple(
        synapse.weight for pre_id in pre_ids for synapse in network.synapses[pre_id]
    )
    return weights, learning


def _probe_response(
    config: Config,
    weights: Sequence[float],
) -> tuple[bool, float, int | None]:
    exp = _experiment_config(config)
    drive = float(exp.get("drive_current", 100.0))
    probe_ticks = int(exp.get("probe_ticks", 5))
    if probe_ticks < 2:
        raise ValueError("learning_experiment.probe_ticks must be >= 2")

    network, pre_ids, target_id = _build_convergent_network(config, 0.0)
    if len(weights) != len(pre_ids):
        raise ValueError("weight vector does not match experiment topology")
    for pre_id, weight in zip(pre_ids, weights):
        network.synapses[pre_id][0].weight = float(weight)

    for pre_id in pre_ids:
        network.inject_current(pre_id, drive)

    peak_v = network.neurons[target_id].v
    spike_tick: int | None = None
    for _ in range(probe_ticks):
        result = network.step()
        peak_v = max(peak_v, network.neurons[target_id].v)
        if target_id in result.spike_ids and spike_tick is None:
            spike_tick = result.tick
    return spike_tick is not None, peak_v, spike_tick


def run_learning_experiment(config: Config) -> LearningExperimentResult:
    """Run training and compare fresh baseline/trained network responses."""
    exp = _experiment_config(config)
    initial_weight = float(exp.get("initial_weight", 0.05))
    pre_count = int(exp.get("presynaptic_neurons", 48))
    initial_weights = tuple(initial_weight for _ in range(pre_count))

    baseline_spiked, baseline_peak_v, baseline_tick = _probe_response(
        config, initial_weights
    )
    trained_weights, learning = _train(config)
    trained_spiked, trained_peak_v, trained_tick = _probe_response(
        config, trained_weights
    )

    initial_mean = statistics.mean(initial_weights)
    final_mean = statistics.mean(trained_weights)
    return LearningExperimentResult(
        training_trials=int(exp.get("training_trials", 20)),
        presynaptic_neurons=pre_count,
        initial_mean_weight=initial_mean,
        final_mean_weight=final_mean,
        mean_weight_delta=final_mean - initial_mean,
        rewards_received=learning.stats.rewards_received,
        rewards_applied=learning.stats.rewards_applied,
        reward_weight_updates=learning.stats.reward_weight_updates,
        baseline_target_spiked=baseline_spiked,
        trained_target_spiked=trained_spiked,
        baseline_target_peak_v=baseline_peak_v,
        trained_target_peak_v=trained_peak_v,
        baseline_target_spike_tick=baseline_tick,
        trained_target_spike_tick=trained_tick,
    )


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)
    if not isinstance(loaded, dict):
        raise TypeError("experiment config root must be a mapping")
    return loaded


def main() -> int:
    """CLI entry point for the deterministic learning experiment."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/learning_experiment.yaml")
    args = parser.parse_args()
    result = run_learning_experiment(_load_yaml(Path(args.config)))
    for key, value in asdict(result).items():
        print(f"{key}: {value}")
    print(f"learned: {result.learned}")
    return 0 if result.learned else 1


if __name__ == "__main__":
    raise SystemExit(main())
