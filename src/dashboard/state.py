"""Thread-safe dashboard state publication and management.

This module provides a thread-safe state store for the dashboard that
supports atomic updates, partial state changes, and event notifications
for state subscribers.
"""

from __future__ import annotations

import datetime
import logging
from collections.abc import Callable
from dataclasses import replace
from threading import RLock
from typing import Any, Protocol

from .models import (
    ComponentStatus,
    DashboardSnapshot,
    ExperimentSession,
    ExperimentState,
    HealthSnapshot,
    ParameterChangeRecord,
    ParameterSchema,
    PendingParameterChange,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Type Definitions
# ============================================================================

StateChangeCallback = Callable[[DashboardSnapshot, DashboardSnapshot], None]
"""Callback function type for state change notifications.

Args:
    old_snapshot: The previous dashboard state.
    new_snapshot: The new dashboard state.
"""


# ============================================================================
# Protocols
# ============================================================================


class StateSource(Protocol):
    """Protocol for objects that can provide a dashboard snapshot."""

    def snapshot(self) -> DashboardSnapshot:
        """Return the current dashboard snapshot."""
        ...


# ============================================================================
# State Store
# ============================================================================


class DashboardStateStore:
    """Publish and retrieve immutable dashboard snapshots safely.

    This class provides thread-safe access to the current dashboard state
    with support for atomic updates, partial updates, and event notifications.

    Features:
        - Thread-safe with RLock
        - Atomic full-state updates
        - Partial updates using a builder pattern
        - Event callbacks for state changes
        - Optional state history for debugging
        - Compatible with the simple interface expected by server.py

    Example:
        >>> store = DashboardStateStore()
        >>> store.update(system=SystemMetrics(neurons=1000))
        >>> current = store.snapshot()
        >>> store.on_change(lambda old, new: print(f"State changed: {new.status}"))
    """

    def __init__(
        self,
        initial: DashboardSnapshot | None = None,
        *,
        max_history: int = 0,
        notify_on_update: bool = True,
    ) -> None:
        """Initialize the state store.

        Args:
            initial: Optional initial snapshot. If None, a default is used.
            max_history: Maximum number of historical states to keep.
                0 disables history tracking.
            notify_on_update: Whether to notify callbacks on updates.
        """
        self._lock = RLock()
        self._snapshot = initial or DashboardSnapshot()
        self._version = 0
        self._callbacks: list[StateChangeCallback] = []
        self._history: list[DashboardSnapshot] = []
        self._max_history = max_history
        self._notify_on_update = notify_on_update
        self._update_count = 0

        # Store the initial snapshot in history if enabled
        if max_history > 0:
            self._history.append(self._snapshot)

    # =========================================================================
    # Core Operations
    # =========================================================================

    def publish(self, snapshot: DashboardSnapshot) -> None:
        """Replace the currently visible snapshot atomically.

        Args:
            snapshot: The new dashboard snapshot.
        """
        with self._lock:
            old = self._snapshot
            self._snapshot = snapshot
            self._version += 1
            self._update_count += 1

            # Track history if enabled
            if self._max_history > 0:
                self._history.append(snapshot)
                if len(self._history) > self._max_history:
                    self._history = self._history[-self._max_history :]

            # Notify callbacks
            if self._notify_on_update:
                self._notify_callbacks(old, snapshot)

    def snapshot(self) -> DashboardSnapshot:
        """Return the latest immutable snapshot.

        Returns:
            The current dashboard snapshot.
        """
        with self._lock:
            return self._snapshot

    def update(self, **kwargs: Any) -> DashboardSnapshot:
        """Update specific fields of the dashboard state.

        This is a convenience method that creates a new snapshot with
        updated fields. It uses the dataclass replace() pattern.

        Args:
            **kwargs: Fields to update. Supported keys correspond to
                the fields of DashboardSnapshot.

        Returns:
            The new snapshot that was published.

        Example:
            >>> store.update(status="running", system=SystemMetrics(neurons=1000))
        """
        with self._lock:
            old = self._snapshot

            # Create a new snapshot with updated fields
            new_snapshot = self._update_snapshot(old, **kwargs)

            # Publish the new snapshot
            self._snapshot = new_snapshot
            self._version += 1
            self._update_count += 1

            # Track history if enabled
            if self._max_history > 0:
                self._history.append(new_snapshot)
                if len(self._history) > self._max_history:
                    self._history = self._history[-self._max_history :]

            # Notify callbacks
            if self._notify_on_update:
                self._notify_callbacks(old, new_snapshot)

            return new_snapshot

    def _update_snapshot(
        self, snapshot: DashboardSnapshot, **kwargs: Any
    ) -> DashboardSnapshot:
        """Create a new snapshot with updated fields."""
        # Get all fields of DashboardSnapshot
        field_names = [
            "system",
            "learning",
            "storage",
            "self_organization",
            "homeostasis",
            "structural",
            "spikes",
            "network",
            "language_organ",
            "knowledge_intake",
            "signal_metrics",
            "experiment",
            "embodiment",
            "components",
            "parameters",
            "pending_changes",
            "change_history",
            "experiment_state",
            "health",
            "status",
            "version",
        ]

        # Build replacement dict
        replacements: dict[str, Any] = {}
        for name in field_names:
            if name in kwargs:
                replacements[name] = kwargs[name]

        # Update the snapshot using dataclass replace
        return replace(snapshot, **replacements)

    def update_component(self, status: ComponentStatus) -> DashboardSnapshot:
        """Update or insert a single component status.

        Args:
            status: The new component status.

        Returns:
            The new snapshot.
        """
        with self._lock:
            current = self._snapshot
            components = dict(current.components or {})
            components[status.component] = status
            return self.update(components=components)

    def update_parameter(self, parameter: ParameterSchema) -> DashboardSnapshot:
        """Update or insert a single parameter schema entry.

        Args:
            parameter: The new parameter schema entry.

        Returns:
            The new snapshot.
        """
        with self._lock:
            current = self._snapshot
            parameters = dict(current.parameters or {})
            parameters[parameter.name] = parameter
            return self.update(parameters=parameters)

    def set_health(self, health: HealthSnapshot) -> DashboardSnapshot:
        """Set the aggregated health snapshot.

        Args:
            health: The new health snapshot.

        Returns:
            The new snapshot.
        """
        return self.update(health=health)

    def set_pending_change(
        self,
        change: PendingParameterChange,
    ) -> DashboardSnapshot:
        """Record or update a pending parameter change.

        Args:
            change: The pending change to store.

        Returns:
            The new snapshot.
        """
        with self._lock:
            current = self._snapshot
            pending = dict(current.pending_changes or {})
            pending[change.name] = change
            return self.update(pending_changes=pending)

    def remove_pending_change(self, name: str) -> DashboardSnapshot:
        """Remove a pending parameter change.

        Args:
            name: Parameter name whose pending change should be removed.

        Returns:
            The new snapshot.
        """
        with self._lock:
            current = self._snapshot
            pending = dict(current.pending_changes or {})
            pending.pop(name, None)
            return self.update(pending_changes=pending)

    def clear_pending_changes(self) -> DashboardSnapshot:
        """Clear all pending parameter changes.

        Returns:
            The new snapshot.
        """
        return self.update(pending_changes={})

    def append_change_history(
        self,
        record: ParameterChangeRecord,
    ) -> DashboardSnapshot:
        """Append a change record to the history.

        Args:
            record: The record to append.

        Returns:
            The new snapshot.
        """
        with self._lock:
            current = self._snapshot
            history = list(current.change_history)
            history.append(record)
            return self.update(change_history=tuple(history))

    def set_experiment_mode(
        self,
        mode: str,
    ) -> DashboardSnapshot:
        """Set the current experiment mode.

        Args:
            mode: One of 'operator', 'experiment', 'debug'.

        Returns:
            The new snapshot.
        """
        with self._lock:
            current = self._snapshot
            new_state = ExperimentState(
                current_mode=mode,
                active_session=current.experiment_state.active_session,
                sessions=current.experiment_state.sessions,
            )
            return self.update(experiment_state=new_state)

    def start_experiment_session(
        self,
        session: ExperimentSession,
    ) -> DashboardSnapshot:
        """Start a new experiment/debug session.

        Any currently active session is closed automatically.

        Args:
            session: The session to start.

        Returns:
            The new snapshot.
        """
        with self._lock:
            current = self._snapshot
            old_state = current.experiment_state
            sessions = list(old_state.sessions)

            # Close any active session first
            if old_state.active_session is not None:
                now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
                closed = ExperimentSession(
                    session_id=old_state.active_session.session_id,
                    mode=old_state.active_session.mode,
                    hypothesis=old_state.active_session.hypothesis,
                    notes=old_state.active_session.notes,
                    start_tick=old_state.active_session.start_tick,
                    end_tick=session.start_tick,
                    start_time=old_state.active_session.start_time,
                    end_time=now,
                    config_snapshot=old_state.active_session.config_snapshot,
                    active=False,
                )
                sessions.append(closed)

            sessions.append(session)
            new_state = ExperimentState(
                current_mode=session.mode,
                active_session=session,
                sessions=tuple(sessions),
            )
            return self.update(experiment_state=new_state)

    def stop_experiment_session(
        self,
        end_tick: int = 0,
    ) -> DashboardSnapshot:
        """Stop the active experiment/debug session.

        Args:
            end_tick: Simulation tick at session stop.

        Returns:
            The new snapshot.
        """
        with self._lock:
            current = self._snapshot
            old_state = current.experiment_state
            active = old_state.active_session

            if active is None:
                return current

            now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
            sessions = [s for s in old_state.sessions if not s.active]
            closed = ExperimentSession(
                session_id=active.session_id,
                mode=active.mode,
                hypothesis=active.hypothesis,
                notes=active.notes,
                start_tick=active.start_tick,
                end_tick=end_tick,
                start_time=active.start_time,
                end_time=now,
                config_snapshot=active.config_snapshot,
                active=False,
            )
            sessions.append(closed)

            new_state = ExperimentState(
                current_mode=old_state.current_mode,
                active_session=None,
                sessions=tuple(sessions),
            )
            return self.update(experiment_state=new_state)

    def add_experiment_note(
        self,
        note: str,
    ) -> DashboardSnapshot:
        """Append a note to the active experiment session.

        Args:
            note: Note text to append.

        Returns:
            The new snapshot.
        """
        with self._lock:
            current = self._snapshot
            old_state = current.experiment_state
            active = old_state.active_session

            if active is None:
                return current

            now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
            updated = ExperimentSession(
                session_id=active.session_id,
                mode=active.mode,
                hypothesis=active.hypothesis,
                notes=(*active.notes, f"[{now}] {note}"),
                start_tick=active.start_tick,
                end_tick=active.end_tick,
                start_time=active.start_time,
                end_time=active.end_time,
                config_snapshot=active.config_snapshot,
                active=active.active,
            )

            sessions = [
                s if s.session_id != active.session_id else updated
                for s in old_state.sessions
            ]
            # Ensure active session is present in sessions list
            if not any(s.session_id == active.session_id for s in sessions):
                sessions.append(updated)

            new_state = ExperimentState(
                current_mode=old_state.current_mode,
                active_session=updated,
                sessions=tuple(sessions),
            )
            return self.update(experiment_state=new_state)

    # =========================================================================
    # Event System
    # =========================================================================

    def on_change(self, callback: StateChangeCallback) -> None:
        """Register a callback for state changes.

        Args:
            callback: Function to call when the state changes.
                Receives old and new snapshots as arguments.

        Raises:
            ValueError: If the callback is already registered.
        """
        with self._lock:
            if callback in self._callbacks:
                raise ValueError("Callback already registered")
            self._callbacks.append(callback)

    def remove_callback(self, callback: StateChangeCallback) -> bool:
        """Remove a previously registered callback.

        Args:
            callback: The callback to remove.

        Returns:
            True if the callback was removed, False if not found.
        """
        with self._lock:
            try:
                self._callbacks.remove(callback)
                return True
            except ValueError:
                return False

    def clear_callbacks(self) -> None:
        """Remove all registered callbacks."""
        with self._lock:
            self._callbacks.clear()

    def _notify_callbacks(self, old: DashboardSnapshot, new: DashboardSnapshot) -> None:
        """Notify all registered callbacks of a state change."""
        # Make a copy of the callback list to avoid issues if callbacks
        # modify the list during iteration.
        with self._lock:
            callbacks = list(self._callbacks)

        for callback in callbacks:
            try:
                callback(old, new)
            except Exception as e:
                logger.warning(f"State change callback failed: {e}")

    # =========================================================================
    # Query Methods
    # =========================================================================

    def version(self) -> int:
        """Return the current state version number.

        The version increments on every state change.
        """
        with self._lock:
            return self._version

    def update_count(self) -> int:
        """Return the total number of state updates."""
        with self._lock:
            return self._update_count

    def get_history(self, limit: int | None = None) -> list[DashboardSnapshot]:
        """Return the state history.

        Args:
            limit: Maximum number of historical states to return.
                If None, returns all history.

        Returns:
            List of historical snapshots (newest first).
        """
        with self._lock:
            if limit is None or limit <= 0:
                return list(reversed(self._history))
            return list(reversed(self._history[-limit:]))

    def get_version_at(self, version: int) -> DashboardSnapshot | None:
        """Get the state at a specific version.

        Args:
            version: Version number to retrieve.

        Returns:
            The snapshot at that version, or None if not found.
        """
        with self._lock:
            if version < 0 or version >= len(self._history):
                return None
            return self._history[version]

    # =========================================================================
    # Convenience Methods
    # =========================================================================

    def set_status(self, status: str) -> DashboardSnapshot:
        """Update the dashboard status.

        Args:
            status: New status string (e.g., "idle", "running", "paused").

        Returns:
            The new snapshot.
        """
        return self.update(status=status)

    def set_version(self, version: str) -> DashboardSnapshot:
        """Update the system version.

        Args:
            version: New version string.

        Returns:
            The new snapshot.
        """
        return self.update(version=version)

    def update_metrics(
        self,
        system: Any = None,
        learning: Any = None,
        storage: Any = None,
        homeostasis: Any = None,
        structural: Any = None,
        spikes: Any = None,
        network: Any = None,
        language_organ: Any = None,
        knowledge_intake: Any = None,
        experiment: Any = None,
        embodiment: Any = None,
    ) -> DashboardSnapshot:
        """Update multiple metric fields at once.

        This is a convenience method for updating all metric-related
        fields in a single call.

        Args:
            system: SystemMetrics instance.
            learning: LearningMetrics instance.
            storage: StorageMetrics instance.
            homeostasis: HomeostasisMetrics instance.
            structural: StructuralMetrics instance.
            spikes: SpikeMetrics instance.
            network: NetworkMetrics instance.
            language_organ: LanguageOrganMetrics instance.
            knowledge_intake: KnowledgeIntakeMetrics instance.
            experiment: ExperimentMetrics instance.
            embodiment: EmbodimentMetrics instance.

        Returns:
            The new snapshot.
        """
        updates: dict[str, Any] = {}
        if system is not None:
            updates["system"] = system
        if learning is not None:
            updates["learning"] = learning
        if storage is not None:
            updates["storage"] = storage
        if homeostasis is not None:
            updates["homeostasis"] = homeostasis
        if structural is not None:
            updates["structural"] = structural
        if spikes is not None:
            updates["spikes"] = spikes
        if network is not None:
            updates["network"] = network
        if language_organ is not None:
            updates["language_organ"] = language_organ
        if knowledge_intake is not None:
            updates["knowledge_intake"] = knowledge_intake
        if experiment is not None:
            updates["experiment"] = experiment
        if embodiment is not None:
            updates["embodiment"] = embodiment

        return self.update(**updates)

    # =========================================================================
    # Testing Helpers
    # =========================================================================

    def reset(self, initial: DashboardSnapshot | None = None) -> None:
        """Reset the state store to a clean state.

        This is primarily useful for testing.

        Args:
            initial: Optional initial snapshot. If None, uses a default.
        """
        with self._lock:
            self._snapshot = initial or DashboardSnapshot()
            self._version = 0
            self._update_count = 0
            self._history = []
            self._callbacks.clear()
            if self._max_history > 0:
                self._history.append(self._snapshot)


# ============================================================================
# Factory Functions
# ============================================================================


def create_state_store(
    initial: DashboardSnapshot | None = None,
    *,
    with_history: bool = True,
    history_limit: int = 100,
    notify: bool = True,
) -> DashboardStateStore:
    """Create a configured DashboardStateStore.

    Args:
        initial: Optional initial snapshot.
        with_history: Whether to enable history tracking.
        history_limit: Maximum number of historical states to keep.
        notify: Whether to notify callbacks on updates.

    Returns:
        Configured DashboardStateStore instance.

    Example:
        >>> store = create_state_store(with_history=True, history_limit=50)
    """
    return DashboardStateStore(
        initial=initial,
        max_history=history_limit if with_history else 0,
        notify_on_update=notify,
    )


# ============================================================================
# Global State Manager (Optional)
# ============================================================================


class StateManager:
    """Global state manager for the dashboard.

    This is a singleton-like manager that provides access to the
    dashboard state store. It can be used as a central point for
    state management across different parts of the application.
    """

    _instance: StateManager | None = None
    _store: DashboardStateStore | None = None
    _config_dict: dict[str, Any] | None = None

    def __new__(cls) -> StateManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(
        self,
        initial: DashboardSnapshot | None = None,
        *,
        with_history: bool = True,
        history_limit: int = 100,
    ) -> None:
        """Initialize the global state store.

        Args:
            initial: Optional initial snapshot.
            with_history: Whether to enable history tracking.
            history_limit: Maximum number of historical states to keep.
        """
        if self._store is None:
            self._store = create_state_store(
                initial=initial,
                with_history=with_history,
                history_limit=history_limit,
            )

    def set_config(self, config_dict: dict[str, Any] | None) -> None:
        """Store the runtime configuration for health derivation."""
        self._config_dict = config_dict

    @property
    def store(self) -> DashboardStateStore:
        """Get the global state store."""
        if self._store is None:
            # Auto-initialize with default settings
            self._store = create_state_store()
        return self._store

    def publish(self, snapshot: DashboardSnapshot) -> None:
        """Publish a new snapshot."""
        self.store.publish(snapshot)

    def snapshot(self) -> DashboardSnapshot:
        """Get the current snapshot."""
        return self.store.snapshot()

    def update(self, **kwargs: Any) -> DashboardSnapshot:
        """Update the current state."""
        return self.store.update(**kwargs)


# ============================================================================
# Global Instance
# ============================================================================

# Convenience global instance for simple use cases
_state_manager = StateManager()


def get_state_store() -> DashboardStateStore:
    """Get the global state store instance.

    Returns:
        The global DashboardStateStore instance.
    """
    return _state_manager.store


def publish_state(snapshot: DashboardSnapshot) -> None:
    """Publish a state update to the global store.

    The snapshot is automatically enriched with derived components,
    parameters and health so that every consumer sees a complete view.
    """
    from .health_builder import enrich_snapshot

    _state_manager.publish(enrich_snapshot(snapshot, _state_manager._config_dict))  # pyright: ignore[reportPrivateUsage]


def set_dashboard_config(config_dict: dict[str, Any] | None) -> None:
    """Store the runtime configuration used for health derivation."""
    _state_manager.set_config(config_dict)


def get_current_state() -> DashboardSnapshot:
    """Get the current state from the global store."""
    return _state_manager.snapshot()


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Basic usage
    store = DashboardStateStore()

    # Register a callback
    def on_state_change(old: DashboardSnapshot, new: DashboardSnapshot) -> None:
        print(f"State changed: {old.status} -> {new.status}")

    store.on_change(on_state_change)

    # Update state
    store.set_status("running")
    store.set_version("0.6.0")

    # Get current state
    current = store.snapshot()
    print(f"Current status: {current.status}")
    print(f"Version: {current.version}")
