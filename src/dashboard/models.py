"""Typed data models used by the Brain-5D operator dashboard."""

from __future__ import annotations

from dataclasses import dataclass

JSONScalar = str | int | float | bool | None
JSONValue = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]


@dataclass(frozen=True, slots=True)
class SystemMetrics:
    """Core simulation metrics presented on the dashboard."""

    tick: int = 0
    neurons: int = 0
    synapses: int = 0
    spikes_total: int = 0
    spikes_last_tick: int = 0
    core_step_ms: float = 0.0
    mean_energy: float = 0.0

    def to_json(self) -> dict[str, JSONValue]:
        """Return a JSON-serializable representation."""
        return {
            "tick": self.tick,
            "neurons": self.neurons,
            "synapses": self.synapses,
            "spikes_total": self.spikes_total,
            "spikes_last_tick": self.spikes_last_tick,
            "core_step_ms": self.core_step_ms,
            "mean_energy": self.mean_energy,
        }


@dataclass(frozen=True, slots=True)
class LearningMetrics:
    """Learning counters exposed by the dashboard."""

    stdp_updates: int = 0
    reward_updates: int = 0
    rewards_received: int = 0
    rewards_applied: int = 0
    pending_rewards: int = 0
    update_ms: float = 0.0

    def to_json(self) -> dict[str, JSONValue]:
        """Return a JSON-serializable representation."""
        return {
            "stdp_updates": self.stdp_updates,
            "reward_updates": self.reward_updates,
            "rewards_received": self.rewards_received,
            "rewards_applied": self.rewards_applied,
            "pending_rewards": self.pending_rewards,
            "update_ms": self.update_ms,
        }


@dataclass(frozen=True, slots=True)
class StorageMetrics:
    """Persistence metrics exposed by storage telemetry."""

    queue_depth: int = 0
    queue_capacity: int = 0
    batches_enqueued: int = 0
    batches_written: int = 0
    deltas_written: int = 0
    bytes_written: int = 0
    dropped_batches: int = 0
    write_latency_ms: float = 0.0
    commit_latency_ms: float = 0.0
    journal_size_bytes: int = 0
    worker_failed: bool = False

    def to_json(self) -> dict[str, JSONValue]:
        """Return a JSON-serializable representation."""
        return {
            "queue_depth": self.queue_depth,
            "queue_capacity": self.queue_capacity,
            "batches_enqueued": self.batches_enqueued,
            "batches_written": self.batches_written,
            "deltas_written": self.deltas_written,
            "bytes_written": self.bytes_written,
            "dropped_batches": self.dropped_batches,
            "write_latency_ms": self.write_latency_ms,
            "commit_latency_ms": self.commit_latency_ms,
            "journal_size_bytes": self.journal_size_bytes,
            "worker_failed": self.worker_failed,
        }


@dataclass(frozen=True, slots=True)
class SelfOrganizationMetrics:
    """Structural self-organization counters."""

    neurons_created: int = 0
    neurons_removed: int = 0
    synapses_created: int = 0
    synapses_pruned: int = 0

    def to_json(self) -> dict[str, JSONValue]:
        """Return a JSON-serializable representation."""
        return {
            "neurons_created": self.neurons_created,
            "neurons_removed": self.neurons_removed,
            "synapses_created": self.synapses_created,
            "synapses_pruned": self.synapses_pruned,
        }


@dataclass(frozen=True, slots=True)
class HomeostasisMetrics:
    """Self-regulation metrics introduced with v0.5."""

    enabled: bool = False
    target_rate_hz: float = 0.0
    mean_rate_hz: float = 0.0
    mean_rate_error_hz: float = 0.0
    mean_threshold_adaptation: float = 0.0
    target_energy: float = 0.0
    mean_energy: float = 0.0
    mean_energy_error: float = 0.0
    active_neurons: int = 0
    updates: int = 0

    def to_json(self) -> dict[str, JSONValue]:
        """Return a JSON-serializable representation."""
        return {
            "enabled": self.enabled,
            "target_rate_hz": self.target_rate_hz,
            "mean_rate_hz": self.mean_rate_hz,
            "mean_rate_error_hz": self.mean_rate_error_hz,
            "mean_threshold_adaptation": self.mean_threshold_adaptation,
            "target_energy": self.target_energy,
            "mean_energy": self.mean_energy,
            "mean_energy_error": self.mean_energy_error,
            "active_neurons": self.active_neurons,
            "updates": self.updates,
        }


@dataclass(frozen=True, slots=True)
class DashboardSnapshot:
    """One immutable dashboard state publication."""

    system: SystemMetrics = SystemMetrics()
    learning: LearningMetrics = LearningMetrics()
    storage: StorageMetrics = StorageMetrics()
    self_organization: SelfOrganizationMetrics = SelfOrganizationMetrics()
    homeostasis: HomeostasisMetrics = HomeostasisMetrics()
    status: str = "idle"
    version: str = "0.5.0-alpha.1"

    def to_json(self) -> dict[str, JSONValue]:
        """Return the complete snapshot as a JSON object."""
        return {
            "status": self.status,
            "version": self.version,
            "system": self.system.to_json(),
            "learning": self.learning.to_json(),
            "storage": self.storage.to_json(),
            "self_organization": self.self_organization.to_json(),
            "homeostasis": self.homeostasis.to_json(),
        }
