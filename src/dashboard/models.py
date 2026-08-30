"""Typed data models used by the Brain-5D operator dashboard."""

from __future__ import annotations

from dataclasses import dataclass, field
from dataclasses import fields as dataclass_fields
from typing import Any

from src.embodiment.models import EmbodimentMetrics

JSONScalar = str | int | float | bool | None
JSONValue = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]


# ============================================================================
# Core Metrics
# ============================================================================


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
    """Persistence metrics exposed by storage telemetry.

    All numeric fields default to ``None`` to distinguish
    "not available / not connected" from "measured and zero".
    The dashboard should display ``—`` for ``None`` fields.
    """

    available: bool = False
    queue_depth: int | None = None
    queue_capacity: int | None = None
    batches_enqueued: int | None = None
    batches_written: int | None = None
    deltas_written: int | None = None
    bytes_written: int | None = None
    dropped_batches: int | None = None
    write_latency_ms: float | None = None
    commit_latency_ms: float | None = None
    journal_size_bytes: int | None = None
    worker_failed: bool | None = None

    def to_json(self) -> dict[str, JSONValue]:
        """Return a JSON-serializable representation."""
        return {
            "available": self.available,
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
    """Structural self-organization counters.

    All numeric fields default to ``None`` to distinguish
    "not configured / not connected" from "measured and zero".
    """

    available: bool = False
    neurons_created: int | None = None
    neurons_removed: int | None = None
    synapses_created: int | None = None
    synapses_pruned: int | None = None

    def to_json(self) -> dict[str, JSONValue]:
        """Return a JSON-serializable representation."""
        return {
            "available": self.available,
            "neurons_created": self.neurons_created,
            "neurons_removed": self.neurons_removed,
            "synapses_created": self.synapses_created,
            "synapses_pruned": self.synapses_pruned,
        }


# ============================================================================
# Homeostasis Metrics
# ============================================================================


@dataclass(frozen=True, slots=True)
class HomeostasisMetrics:
    """Backward-compatible homeostasis metrics for dashboard consumers.

    ``actual_rate_hz`` / ``rate_error_hz`` are the alpha.6 names.  The
    ``mean_*`` fields are the v0.5 regulator names.  Both contracts remain
    available during the v0.5 transition so older dashboard tests, scripts,
    and saved API consumers do not break.
    """

    enabled: bool = False
    target_rate_hz: float = 0.0
    actual_rate_hz: float = 0.0
    rate_error_hz: float = 0.0
    mean_rate_hz: float = 0.0
    mean_rate_error_hz: float = 0.0
    mean_threshold_adaptation: float = 0.0
    target_energy: float = 0.0
    mean_energy: float = 0.0
    mean_energy_error: float = 0.0
    active_neurons: int = 0
    updates: int = 0

    def _resolved_rate(self) -> float:
        """Resolve the canonical rate while honoring the legacy alias."""
        if self.mean_rate_hz != 0.0 or self.actual_rate_hz == 0.0:
            return self.mean_rate_hz
        return self.actual_rate_hz

    def _resolved_error(self) -> float:
        """Resolve the canonical rate error while honoring the legacy alias."""
        if self.mean_rate_error_hz != 0.0 or self.rate_error_hz == 0.0:
            return self.mean_rate_error_hz
        return self.rate_error_hz

    def to_json(self) -> dict[str, JSONValue]:
        """Return both the legacy and canonical JSON field names."""
        rate = self._resolved_rate()
        error = self._resolved_error()
        return {
            "enabled": self.enabled,
            "target_rate_hz": self.target_rate_hz,
            "actual_rate_hz": rate,
            "rate_error_hz": error,
            "mean_rate_hz": rate,
            "mean_rate_error_hz": error,
            "mean_threshold_adaptation": self.mean_threshold_adaptation,
            "target_energy": self.target_energy,
            "mean_energy": self.mean_energy,
            "mean_energy_error": self.mean_energy_error,
            "active_neurons": self.active_neurons,
            "updates": self.updates,
        }


# ============================================================================
# Structural Metrics (for adapters.py)
# ============================================================================


@dataclass(frozen=True, slots=True)
class StructuralMetrics:
    """Structural plasticity metrics for dashboard display.

    These metrics are consumed by the structural_metrics() adapter
    and provide insight into network growth and pruning dynamics.
    """

    neuron_count: int = 0
    synapse_count: int = 0
    new_neurons: int = 0
    pruned_neurons: int = 0
    new_synapses: int = 0
    pruned_synapses: int = 0
    growth_budget: float = 0.0
    used_budget: float = 0.0
    structural_changes: int = 0

    def to_json(self) -> dict[str, JSONValue]:
        """Return a JSON-serializable representation."""
        return {
            "neuron_count": self.neuron_count,
            "synapse_count": self.synapse_count,
            "new_neurons": self.new_neurons,
            "pruned_neurons": self.pruned_neurons,
            "new_synapses": self.new_synapses,
            "pruned_synapses": self.pruned_synapses,
            "growth_budget": self.growth_budget,
            "used_budget": self.used_budget,
            "structural_changes": self.structural_changes,
        }


# ============================================================================
# Spike Metrics (for adapters.py)
# ============================================================================


@dataclass(frozen=True, slots=True)
class SpikeMetrics:
    """Spike recording metrics for dashboard display.

    These metrics are consumed by the spike_metrics() adapter
    and provide insight into network activity patterns.
    """

    total_spikes: int = 0
    active_neurons: int = 0
    mean_firing_rate_hz: float = 0.0
    burst_index: float = 0.0
    synchrony: float = 0.0
    spike_count_last_tick: int = 0

    def to_json(self) -> dict[str, JSONValue]:
        """Return a JSON-serializable representation."""
        return {
            "total_spikes": self.total_spikes,
            "active_neurons": self.active_neurons,
            "mean_firing_rate_hz": self.mean_firing_rate_hz,
            "burst_index": self.burst_index,
            "synchrony": self.synchrony,
            "spike_count_last_tick": self.spike_count_last_tick,
        }


# ============================================================================
# Network Metrics
# ============================================================================


@dataclass(frozen=True, slots=True)
class NetworkMetrics:
    """Comprehensive network metrics for dashboard display.

    Provides a holistic view of the network state including
    activity, structure, and energy consumption.
    """

    tick: int = 0
    neuron_count: int = 0
    synapse_count: int = 0
    active_neurons: int = 0
    silent_neurons: int = 0
    mean_firing_rate_hz: float = 0.0
    burst_index: float = 0.0
    synchrony: float = 0.0
    mean_energy: float = 0.0
    mean_threshold_adaptation: float = 0.0
    e_i_ratio: float = 0.0
    clustering_coefficient: float = 0.0
    mean_path_length: float = 0.0

    def to_json(self) -> dict[str, JSONValue]:
        """Return a JSON-serializable representation."""
        return {
            "tick": self.tick,
            "neuron_count": self.neuron_count,
            "synapse_count": self.synapse_count,
            "active_neurons": self.active_neurons,
            "silent_neurons": self.silent_neurons,
            "mean_firing_rate_hz": self.mean_firing_rate_hz,
            "burst_index": self.burst_index,
            "synchrony": self.synchrony,
            "mean_energy": self.mean_energy,
            "mean_threshold_adaptation": self.mean_threshold_adaptation,
            "e_i_ratio": self.e_i_ratio,
            "clustering_coefficient": self.clustering_coefficient,
            "mean_path_length": self.mean_path_length,
        }


# ============================================================================
# Language Organ Metrics
# ============================================================================


@dataclass(frozen=True, slots=True)
class LanguageOrganMetrics:
    """Metrics for the Language Organ (LLM integration).

    Tracks the status and performance of the optional LLM component
    as it translates between symbolic and subsymbolic representations.
    """

    enabled: bool = False
    active: bool = False
    backend_type: str = "null"
    model_name: str = ""
    inference_count: int = 0
    inference_time_ms: float = 0.0
    avg_inference_time_ms: float = 0.0
    errors: int = 0
    last_error: str | None = None
    queue_depth: int = 0
    max_queue_depth: int = 0

    def to_json(self) -> dict[str, JSONValue]:
        """Return a JSON-serializable representation."""
        result: dict[str, JSONValue] = {
            "enabled": self.enabled,
            "active": self.active,
            "backend_type": self.backend_type,
            "model_name": self.model_name,
            "inference_count": self.inference_count,
            "inference_time_ms": self.inference_time_ms,
            "avg_inference_time_ms": self.avg_inference_time_ms,
            "errors": self.errors,
            "queue_depth": self.queue_depth,
            "max_queue_depth": self.max_queue_depth,
        }
        if self.last_error is not None:
            result["last_error"] = self.last_error
        return result


# ============================================================================
# Knowledge Intake Metrics
# ============================================================================


@dataclass(frozen=True, slots=True)
class KnowledgeIntakeMetrics:
    """Metrics for the Knowledge Intake Engine.

    Tracks external knowledge ingestion and provenance for
    controlled learning experiments.
    """

    items_ingested: int = 0
    items_processed: int = 0
    items_failed: int = 0
    learning_stimuli_created: int = 0
    sources_cached: int = 0
    deduplication_hits: int = 0
    trust_failures: int = 0
    intake_queue_depth: int = 0
    intake_queue_capacity: int = 0
    last_ingestion_time: str | None = None
    active_sources: int = 0

    def to_json(self) -> dict[str, JSONValue]:
        """Return a JSON-serializable representation."""
        result: dict[str, JSONValue] = {
            "items_ingested": self.items_ingested,
            "items_processed": self.items_processed,
            "items_failed": self.items_failed,
            "learning_stimuli_created": self.learning_stimuli_created,
            "sources_cached": self.sources_cached,
            "deduplication_hits": self.deduplication_hits,
            "trust_failures": self.trust_failures,
            "intake_queue_depth": self.intake_queue_depth,
            "intake_queue_capacity": self.intake_queue_capacity,
            "active_sources": self.active_sources,
        }
        if self.last_ingestion_time is not None:
            result["last_ingestion_time"] = self.last_ingestion_time
        return result


# ============================================================================
# Signal Metrics (for Signal Bridge)
# ============================================================================


@dataclass(frozen=True, slots=True)
class SignalMetrics:
    """Metrics for the Signal Bridge layer.

    Tracks the transformation between spike events and SignalFrames,
    as well as the interpretation pipeline.
    """

    frames_processed: int = 0
    frames_generated: int = 0
    avg_frame_size: int = 0
    interpretation_count: int = 0
    interpretation_time_ms: float = 0.0
    active_regions: int = 0
    spike_events_processed: int = 0
    burst_detections: int = 0
    synchrony_events: int = 0

    def to_json(self) -> dict[str, JSONValue]:
        """Return a JSON-serializable representation."""
        return {
            "frames_processed": self.frames_processed,
            "frames_generated": self.frames_generated,
            "avg_frame_size": self.avg_frame_size,
            "interpretation_count": self.interpretation_count,
            "interpretation_time_ms": self.interpretation_time_ms,
            "active_regions": self.active_regions,
            "spike_events_processed": self.spike_events_processed,
            "burst_detections": self.burst_detections,
            "synchrony_events": self.synchrony_events,
        }


# ============================================================================
# Experiment Metrics
# ============================================================================


@dataclass(frozen=True, slots=True)
class ExperimentMetrics:
    """Metrics for controlled learning experiments.

    Tracks the progress and outcomes of knowledge learning experiments
    where external information is presented to the SNN.
    """

    experiment_id: str = ""
    episode_count: int = 0
    learning_episodes: int = 0
    evaluation_episodes: int = 0
    recall_accuracy: float = 0.0
    retention_score: float = 0.0
    generalization_score: float = 0.0
    contradiction_detections: int = 0
    source_switches: int = 0
    last_evaluation_tick: int = 0
    active: bool = False

    def to_json(self) -> dict[str, JSONValue]:
        """Return a JSON-serializable representation."""
        return {
            "experiment_id": self.experiment_id,
            "episode_count": self.episode_count,
            "learning_episodes": self.learning_episodes,
            "evaluation_episodes": self.evaluation_episodes,
            "recall_accuracy": self.recall_accuracy,
            "retention_score": self.retention_score,
            "generalization_score": self.generalization_score,
            "contradiction_detections": self.contradiction_detections,
            "source_switches": self.source_switches,
            "last_evaluation_tick": self.last_evaluation_tick,
            "active": self.active,
        }


# ============================================================================
# Component Status Model (Operator Workbench)
# ============================================================================


VALID_COMPONENT_STATUS = {
    "enabled",
    "active",
    "degraded",
    "unavailable",
    "error",
    "stale",
    "disabled",
}

VALID_MATURITY = {
    "implemented",
    "integrated",
    "verified",
    "evidenced",
}


@dataclass(frozen=True, slots=True)
class ComponentStatus:
    """Standardized status for any dashboard-relevant component.

    Attributes:
        component: Logical component identifier (e.g. "runtime", "storage").
        status: One of the VALID_COMPONENT_STATUS values.
        reason: Human-readable explanation of the status.
        last_update: ISO timestamp of the last update.
        source: Origin of the status (e.g. "OperatorBridge", "GateStatusBuilder").
        last_error: Optional last error message.
        maturity: Maturity level from VALID_MATURITY.
    """

    component: str
    status: str = "unavailable"
    reason: str = ""
    last_update: str | None = None
    source: str = ""
    last_error: str | None = None
    maturity: str = "implemented"

    def __post_init__(self) -> None:
        if self.status not in VALID_COMPONENT_STATUS:
            raise ValueError(f"invalid component status: {self.status!r}")
        if self.maturity not in VALID_MATURITY:
            raise ValueError(f"invalid maturity: {self.maturity!r}")

    def to_json(self) -> dict[str, JSONValue]:
        """Return a JSON-serializable representation."""
        result: dict[str, JSONValue] = {
            "component": self.component,
            "status": self.status,
            "reason": self.reason,
            "last_update": self.last_update,
            "source": self.source,
            "maturity": self.maturity,
        }
        if self.last_error is not None:
            result["last_error"] = self.last_error
        return result


# ============================================================================
# Parameter Schema Model (Operator Workbench)
# ============================================================================


@dataclass(frozen=True, slots=True)
class ParameterSchema:
    """Metadata for a single runtime or configuration parameter.

    Attributes:
        name: Parameter identifier.
        value: Current value.
        default: Factory/default value.
        min: Optional minimum value.
        max: Optional maximum value.
        unit: Optional unit suffix.
        description: Human-readable description.
        source: Where the value originates (e.g. "config", "runtime").
        runtime_mutable: Whether the parameter can be changed at runtime.
        requires_restart: Whether a restart is required after change.
        scientific_sensitive: Whether the parameter is scientifically sensitive.
    """

    name: str
    value: JSONScalar | list[JSONValue] | dict[str, JSONValue]
    default: JSONScalar | list[JSONValue] | dict[str, JSONValue] | None = None
    min: JSONScalar | None = None
    max: JSONScalar | None = None
    unit: str | None = None
    description: str = ""
    source: str = ""
    runtime_mutable: bool = False
    requires_restart: bool = False
    scientific_sensitive: bool = False

    def to_json(self) -> dict[str, JSONValue]:
        """Return a JSON-serializable representation."""
        return {
            "name": self.name,
            "value": self.value,
            "default": self.default,
            "min": self.min,
            "max": self.max,
            "unit": self.unit,
            "description": self.description,
            "source": self.source,
            "runtime_mutable": self.runtime_mutable,
            "requires_restart": self.requires_restart,
            "scientific_sensitive": self.scientific_sensitive,
        }


@dataclass(frozen=True, slots=True)
class PendingParameterChange:
    """One pending parameter change waiting for operator confirmation.

    Attributes:
        name: Parameter identifier.
        current_value: Value currently in effect.
        proposed_value: Value proposed by the operator.
        default_value: Factory/default value.
        timestamp: ISO timestamp when the change was proposed.
        requires_restart: Whether applying this change needs a restart.
        scientific_sensitive: Whether the parameter is scientifically sensitive.
        applied: Whether this change has already been applied.
    """

    name: str
    current_value: JSONScalar | list[JSONValue] | dict[str, JSONValue] | None = None
    proposed_value: JSONScalar | list[JSONValue] | dict[str, JSONValue] | None = None
    default_value: JSONScalar | list[JSONValue] | dict[str, JSONValue] | None = None
    timestamp: str | None = None
    requires_restart: bool = False
    scientific_sensitive: bool = False
    applied: bool = False

    def to_json(self) -> dict[str, JSONValue]:
        """Return a JSON-serializable representation."""
        return {
            "name": self.name,
            "current_value": self.current_value,
            "proposed_value": self.proposed_value,
            "default_value": self.default_value,
            "timestamp": self.timestamp,
            "requires_restart": self.requires_restart,
            "scientific_sensitive": self.scientific_sensitive,
            "applied": self.applied,
        }


@dataclass(frozen=True, slots=True)
class ParameterChangeRecord:
    """Immutable record of one applied or cancelled parameter change.

    Attributes:
        name: Parameter identifier.
        action: One of 'applied' or 'cancelled'.
        old_value: Value before the action.
        new_value: Value after the action (for applied changes).
        timestamp: ISO timestamp of the action.
        saved_profile: Whether the change was also saved as a profile.
    """

    name: str
    action: str
    old_value: JSONScalar | list[JSONValue] | dict[str, JSONValue] | None = None
    new_value: JSONScalar | list[JSONValue] | dict[str, JSONValue] | None = None
    timestamp: str | None = None
    saved_profile: bool = False

    def __post_init__(self) -> None:
        if self.action not in {"applied", "cancelled"}:
            raise ValueError(f"invalid change action: {self.action!r}")

    def to_json(self) -> dict[str, JSONValue]:
        """Return a JSON-serializable representation."""
        return {
            "name": self.name,
            "action": self.action,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "timestamp": self.timestamp,
            "saved_profile": self.saved_profile,
        }


# ============================================================================
# Health Snapshot Model (Operator Workbench)
# ============================================================================


@dataclass(frozen=True, slots=True)
class HealthSnapshot:
    """Aggregated health/problems view for the operator workbench.

    Attributes:
        overall: Overall health status.
        problems: List of problems/warnings/errors/unavailable/stale items.
        errors: Count of error-level items.
        warnings: Count of warning-level items.
        stale: Count of stale items.
        unavailable: Count of unavailable items.
    """

    overall: str = "unknown"
    problems: tuple[ComponentStatus, ...] = ()
    errors: int = 0
    warnings: int = 0
    stale: int = 0
    unavailable: int = 0

    def to_json(self) -> dict[str, JSONValue]:
        """Return a JSON-serializable representation."""
        return {
            "overall": self.overall,
            "problems": [p.to_json() for p in self.problems],
            "errors": self.errors,
            "warnings": self.warnings,
            "stale": self.stale,
            "unavailable": self.unavailable,
        }


# ============================================================================
# Experiment Mode Model (Operator Workbench)
# ============================================================================

VALID_EXPERIMENT_MODES = {"operator", "experiment", "debug"}


@dataclass(frozen=True, slots=True)
class ExperimentSession:
    """One recorded experiment or debug session.

    Attributes:
        session_id: Unique session identifier.
        mode: One of 'operator', 'experiment', 'debug'.
        hypothesis: Optional hypothesis or goal for the session.
        notes: Free-text notes recorded during the session.
        start_tick: Simulation tick at session start.
        end_tick: Simulation tick at session end (None if active).
        start_time: ISO timestamp of session start.
        end_time: ISO timestamp of session end (None if active).
        config_snapshot: Optional copy of relevant parameters at start.
        active: Whether the session is currently running.
    """

    session_id: str
    mode: str = "operator"
    hypothesis: str = ""
    notes: tuple[str, ...] = ()
    start_tick: int = 0
    end_tick: int | None = None
    start_time: str | None = None
    end_time: str | None = None
    config_snapshot: dict[str, JSONValue] | None = None
    active: bool = True

    def __post_init__(self) -> None:
        if self.mode not in VALID_EXPERIMENT_MODES:
            raise ValueError(f"invalid experiment mode: {self.mode!r}")

    def to_json(self) -> dict[str, JSONValue]:
        """Return a JSON-serializable representation."""
        return {
            "session_id": self.session_id,
            "mode": self.mode,
            "hypothesis": self.hypothesis,
            "notes": list(self.notes),
            "start_tick": self.start_tick,
            "end_tick": self.end_tick,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "config_snapshot": self.config_snapshot,
            "active": self.active,
        }


@dataclass(frozen=True, slots=True)
class ExperimentState:
    """Current experiment mode and active session metadata.

    Attributes:
        current_mode: One of 'operator', 'experiment', 'debug'.
        active_session: The currently active session, if any.
        sessions: Immutable history of all sessions.
    """

    current_mode: str = "operator"
    active_session: ExperimentSession | None = None
    sessions: tuple[ExperimentSession, ...] = ()

    def __post_init__(self) -> None:
        if self.current_mode not in VALID_EXPERIMENT_MODES:
            raise ValueError(f"invalid experiment mode: {self.current_mode!r}")

    def to_json(self) -> dict[str, JSONValue]:
        """Return a JSON-serializable representation."""
        return {
            "current_mode": self.current_mode,
            "active_session": (
                self.active_session.to_json() if self.active_session else None
            ),
            "sessions": [s.to_json() for s in self.sessions],
        }


# ============================================================================
# Dashboard Snapshot (Enhanced)
# ============================================================================


@dataclass(frozen=True, slots=True)
class DashboardSnapshot:
    """One immutable dashboard state publication."""

    system: SystemMetrics = SystemMetrics()
    learning: LearningMetrics = LearningMetrics()
    storage: StorageMetrics = StorageMetrics()
    self_organization: SelfOrganizationMetrics = SelfOrganizationMetrics()
    homeostasis: HomeostasisMetrics = HomeostasisMetrics()
    structural: StructuralMetrics = StructuralMetrics()
    spikes: SpikeMetrics = SpikeMetrics()
    network: NetworkMetrics = NetworkMetrics()
    language_organ: LanguageOrganMetrics = LanguageOrganMetrics()
    knowledge_intake: KnowledgeIntakeMetrics = KnowledgeIntakeMetrics()
    signal_metrics: SignalMetrics = SignalMetrics()
    experiment: ExperimentMetrics = ExperimentMetrics()
    embodiment: EmbodimentMetrics = EmbodimentMetrics()
    components: dict[str, ComponentStatus] = field(default_factory=dict[str, ComponentStatus])
    parameters: dict[str, ParameterSchema] = field(default_factory=dict[str, ParameterSchema])
    pending_changes: dict[str, PendingParameterChange] = field(default_factory=dict[str, PendingParameterChange])
    change_history: tuple[ParameterChangeRecord, ...] = ()
    experiment_state: ExperimentState = ExperimentState()
    health: HealthSnapshot = HealthSnapshot()
    status: str = "idle"
    version: str = "0.5.0-alpha.2"

    def to_json(self) -> dict[str, JSONValue]:
        """Return the complete snapshot as a JSON object."""
        components = self.components
        parameters = self.parameters
        return {
            "status": self.status,
            "version": self.version,
            "system": self.system.to_json(),
            "learning": self.learning.to_json(),
            "storage": self.storage.to_json(),
            "self_organization": self.self_organization.to_json(),
            "homeostasis": self.homeostasis.to_json(),
            "structural": self.structural.to_json(),
            "spikes": self.spikes.to_json(),
            "network": self.network.to_json(),
            "language_organ": self.language_organ.to_json(),
            "knowledge_intake": self.knowledge_intake.to_json(),
            "signal_metrics": self.signal_metrics.to_json(),
            "experiment": self.experiment.to_json(),
            "embodiment": self.embodiment.to_json(),
            "components": {k: v.to_json() for k, v in components.items()},
            "parameters": {k: v.to_json() for k, v in parameters.items()},
            "pending_changes": {
                k: v.to_json() for k, v in (self.pending_changes or {}).items()
            },
            "change_history": [r.to_json() for r in self.change_history],
            "experiment_state": self.experiment_state.to_json(),
            "health": self.health.to_json(),
        }


# ============================================================================
# Utility Functions
# ============================================================================


def to_json_serializable(obj: Any) -> JSONValue:
    """Convert any object to a JSON-serializable value.

    Recursively handles dataclasses, lists, and dictionaries.
    """
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, (list, tuple)):
        # Use type: ignore to suppress Pylance warnings about unknown item types
        return [to_json_serializable(item) for item in obj]  # type: ignore[reportUnknownVariableType, reportUnknownArgumentType]
    if isinstance(obj, dict):
        # Use type: ignore to suppress Pylance warnings about unknown key/value types
        return {str(k): to_json_serializable(v) for k, v in obj.items()}  # type: ignore[reportUnknownVariableType, reportUnknownArgumentType]
    if hasattr(obj, "to_json"):
        # The object has a to_json method; call it
        result = obj.to_json()
        # Recursively convert the result if needed
        return to_json_serializable(result)
    if hasattr(obj, "__dataclass_fields__"):
        # Fallback for dataclasses without to_json
        field_dict = {
            field.name: getattr(obj, field.name) for field in dataclass_fields(obj)
        }
        return to_json_serializable(field_dict)
    # For anything else, convert to string
    return str(obj)


# ============================================================================
# Metric Aggregator
# ============================================================================


class MetricAggregator:
    """Helper for collecting and aggregating metrics from multiple sources.

    This class provides a convenient way to collect metrics from various
    subsystems and produce a single DashboardSnapshot.
    """

    def __init__(self) -> None:
        self._system = SystemMetrics()
        self._learning = LearningMetrics()
        self._storage = StorageMetrics()
        self._self_org = SelfOrganizationMetrics()
        self._homeostasis = HomeostasisMetrics()
        self._structural = StructuralMetrics()
        self._spikes = SpikeMetrics()
        self._network = NetworkMetrics()
        self._language_organ = LanguageOrganMetrics()
        self._knowledge_intake = KnowledgeIntakeMetrics()
        self._signal_metrics = SignalMetrics()
        self._experiment = ExperimentMetrics()
        self._embodiment = EmbodimentMetrics()
        self._status: str = "idle"
        self._version: str = "0.5.0-alpha.2"

    def update_system(self, **kwargs: Any) -> MetricAggregator:
        """Update SystemMetrics fields."""
        fields = {k: v for k, v in kwargs.items() if hasattr(self._system, k)}
        self._system = SystemMetrics(**{**self._system.__dict__, **fields})
        return self

    def update_learning(self, **kwargs: Any) -> MetricAggregator:
        """Update LearningMetrics fields."""
        fields = {k: v for k, v in kwargs.items() if hasattr(self._learning, k)}
        self._learning = LearningMetrics(**{**self._learning.__dict__, **fields})
        return self

    def update_homeostasis(self, **kwargs: Any) -> MetricAggregator:
        """Update HomeostasisMetrics fields."""
        fields = {k: v for k, v in kwargs.items() if hasattr(self._homeostasis, k)}
        self._homeostasis = HomeostasisMetrics(
            **{**self._homeostasis.__dict__, **fields}
        )
        return self

    def update_structural(self, **kwargs: Any) -> MetricAggregator:
        """Update StructuralMetrics fields."""
        fields = {k: v for k, v in kwargs.items() if hasattr(self._structural, k)}
        self._structural = StructuralMetrics(**{**self._structural.__dict__, **fields})
        return self

    def update_spikes(self, **kwargs: Any) -> MetricAggregator:
        """Update SpikeMetrics fields."""
        fields = {k: v for k, v in kwargs.items() if hasattr(self._spikes, k)}
        self._spikes = SpikeMetrics(**{**self._spikes.__dict__, **fields})
        return self

    def update_network(self, **kwargs: Any) -> MetricAggregator:
        """Update NetworkMetrics fields."""
        fields = {k: v for k, v in kwargs.items() if hasattr(self._network, k)}
        self._network = NetworkMetrics(**{**self._network.__dict__, **fields})
        return self

    def set_status(self, status: str) -> MetricAggregator:
        """Set the dashboard status."""
        self._status = status
        return self

    def set_version(self, version: str) -> MetricAggregator:
        """Set the system version."""
        self._version = version
        return self

    def snapshot(self) -> DashboardSnapshot:
        """Build the complete dashboard snapshot."""
        return DashboardSnapshot(
            system=self._system,
            learning=self._learning,
            storage=self._storage,
            self_organization=self._self_org,
            homeostasis=self._homeostasis,
            structural=self._structural,
            spikes=self._spikes,
            network=self._network,
            language_organ=self._language_organ,
            knowledge_intake=self._knowledge_intake,
            signal_metrics=self._signal_metrics,
            experiment=self._experiment,
            embodiment=self._embodiment,
            status=self._status,
            version=self._version,
        )
