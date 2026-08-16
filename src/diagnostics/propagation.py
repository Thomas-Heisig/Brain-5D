from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Set, Tuple

from ..core.network import StepResult
from .stimulus import StimulusResult


@dataclass(slots=True)
class PropagationReport:
    stimulus_tick: int
    stimulus_mode: str
    directly_stimulated_cells: Tuple[int, ...]
    direct_spike_cells_count: int
    direct_spike_total: int
    secondary_recruited_cells: Tuple[int, ...]
    secondary_recruited_count: int
    first_secondary_tick: Optional[int]
    peak_tick: Optional[int]
    peak_spikes_per_tick: int
    output_reached: bool
    first_output_tick: Optional[int]
    output_spikes_total: int


class PropagationAnalyzer:
    """Classifies directly stimulated vs secondary-recruited cells.

    This is experimental classification, not a proof of causal propagation in
    arbitrary networks. Causal attribution requires event tracing (future work).
    """
    def __init__(self, output_cells: Set[int]):
        self.output_cells = set(output_cells)
        self.stimulated_ids: Set[int] = set()
        self.direct_spike_cells: Set[int] = set()
        self.direct_spike_total = 0
        self.secondary_ids: Set[int] = set()
        self.first_secondary_tick = None
        self.first_output_tick = None
        self.peak_tick = None
        self.peak_spikes = 0
        self.output_spikes_total = 0
        self._stimulus_tick = -1
        self._stimulus_mode = ""

    def observe(self, stimulus_result: StimulusResult, step_result: StepResult) -> None:
        if stimulus_result.target_ids:
            if self._stimulus_tick < 0:
                self._stimulus_tick = stimulus_result.tick
                self._stimulus_mode = stimulus_result.mode
            self.stimulated_ids.update(stimulus_result.target_ids)
        spikes = set(step_result.spike_ids)
        direct = spikes & self.stimulated_ids
        self.direct_spike_cells.update(direct)
        self.direct_spike_total += len(direct)
        secondary = spikes - self.stimulated_ids
        new_secondary = secondary - self.secondary_ids
        if new_secondary and self.first_secondary_tick is None:
            self.first_secondary_tick = step_result.tick
        self.secondary_ids.update(secondary)
        output = spikes & self.output_cells
        if output:
            self.output_spikes_total += len(output)
            if self.first_output_tick is None:
                self.first_output_tick = step_result.tick
        if step_result.spikes_this_tick > self.peak_spikes:
            self.peak_spikes = step_result.spikes_this_tick
            self.peak_tick = step_result.tick

    def get_report(self) -> PropagationReport:
        return PropagationReport(
            stimulus_tick=self._stimulus_tick,
            stimulus_mode=self._stimulus_mode,
            directly_stimulated_cells=tuple(sorted(self.stimulated_ids)),
            direct_spike_cells_count=len(self.direct_spike_cells),
            direct_spike_total=self.direct_spike_total,
            secondary_recruited_cells=tuple(sorted(self.secondary_ids)),
            secondary_recruited_count=len(self.secondary_ids),
            first_secondary_tick=self.first_secondary_tick,
            peak_tick=self.peak_tick,
            peak_spikes_per_tick=self.peak_spikes,
            output_reached=self.first_output_tick is not None,
            first_output_tick=self.first_output_tick,
            output_spikes_total=self.output_spikes_total,
        )