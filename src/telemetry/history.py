from collections import deque


class History:
    def __init__(self, maxlen: int):
        self.data = deque(maxlen=maxlen)

    def append_from_stepresult(self, result) -> None:
        self.data.append({
            "tick": result.tick,
            "spikes_this_tick": result.spikes_this_tick,
            "total_spikes": result.total_spikes,
            "mean_v": result.mean_v,
            "min_v": result.min_v,
            "max_v": result.max_v,
            "mean_energy": result.mean_energy,
            "queued_events": result.queued_events,
            "delivered_events": result.delivered_events,
            "external_targets": result.external_injection_count,
            "external_total_current": result.external_total_current,
            "synaptic_targets": result.synaptic_current_targets,
            "core_step_ms": result.core_step_ms,
        })

    def get_all(self):
        return list(self.data)
