"""Runtime adapter that connects HomeostasisSignal to the structural coordinator.

This adapter is the bridge between live runtime measurements and the
canonical structural mutation path. It runs as a post-tick hook and:

1. Captures the real HomeostasisSignal from HomeostasisEngine
2. Feeds it through SelfOrganizationPolicy.analyze()
3. Publishes the resulting PolicyReport to the SelfOrganizationCoordinator

It does NOT mutate the network. Mutation remains exclusively in:
    Proposal -> Approval -> StructuralPlasticityEngine -> Manipulator

This is the missing link that closes Gate A for the production path.

Config-authoritative:
    The adapter reads its interval from config and passes the policy config
    from the YAML ``self_organization`` section. Hardcoded defaults are
    never used when production config exists.

Error visibility:
    The adapter captures structured RuntimeErrorEvent on failure. The error
    is observable through the error buffer and dashboard — never silently
    swallowed.
"""

from __future__ import annotations

import traceback
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from src.homeostasis.engine import HomeostasisEngine
from src.self_organization.coordinator import SelfOrganizationCoordinator
from src.self_organization.policy import (
    SelfOrganizationPolicy,
    SelfOrganizationPolicyConfig,
)

# ============================================================================
# Structured error event for scientific integrity
# ============================================================================


@dataclass(frozen=True, slots=True)
class RuntimeErrorEvent:
    """Canonical structured error event for the runtime adapter.

    Attributes:
        timestamp: Monotonic time (time.monotonic_ns()) when the error occurred.
        tick: Simulation tick when the error occurred.
        component: Component name (e.g. "SelfOrganizationRuntimeAdapter").
        phase: Phase within the component (e.g. "build_signal", "analyze", "publish").
        exception_type: Fully qualified exception type name.
        message: Human-readable error message.
        fatal: If True, the simulation should stop. If False, the error is
               isolated and the simulation can continue.
        traceback_hash: SHA-256 of the traceback text, for deduplication.
    """

    timestamp: int
    tick: int
    component: str
    phase: str
    exception_type: str
    message: str
    fatal: bool = False
    traceback_hash: str = ""


# ============================================================================
# Bounded error buffer
# ============================================================================


class ErrorBuffer:
    """Thread-safe bounded buffer for RuntimeErrorEvents.

    The buffer holds the most recent N events and exposes them for
    dashboard/API visibility. All public methods are protected by
    ``threading.RLock`` for genuine thread safety.
    """

    def __init__(self, max_size: int = 100) -> None:
        import threading

        self._lock = threading.RLock()
        self._max_size = max_size
        self._events: list[RuntimeErrorEvent] = []

    def push(self, event: RuntimeErrorEvent) -> None:
        with self._lock:
            self._events.append(event)
            if len(self._events) > self._max_size:
                self._events.pop(0)

    @property
    def events(self) -> Sequence[RuntimeErrorEvent]:
        with self._lock:
            return tuple(self._events)

    @property
    def latest(self) -> RuntimeErrorEvent | None:
        with self._lock:
            return self._events[-1] if self._events else None

    @property
    def count(self) -> int:
        with self._lock:
            return len(self._events)

    def clear(self) -> None:
        with self._lock:
            self._events.clear()


# ============================================================================
# Shared global error buffer (canonical owner)
# ============================================================================

# The canonical error buffer for the runtime adapter. Accessed by the
# adapter, the OperatorBridge, and the dashboard integration status.
_runtime_error_buffer: ErrorBuffer = ErrorBuffer()


def get_error_buffer() -> ErrorBuffer:
    """Return the canonical shared error buffer."""
    return _runtime_error_buffer


# ============================================================================
# Runtime Adapter
# ============================================================================


class SelfOrganizationRuntimeAdapter:
    """Post-tick hook that feeds real HomeostasisSignals into the structural coordinator.

    The adapter is attached to the RuntimeController and runs after every
    tick. It builds a HomeostasisSignal from the live network, passes it
    through the SelfOrganizationPolicy, and publishes the resulting
    PolicyReport to the coordinator.

    Config-authoritative:
        ``interval_ticks`` and ``policy_config`` come from the YAML
        ``self_organization`` section. Hardcoded defaults are only used
        when no config is provided (e.g. in tests).

    Error visibility:
        Exceptions are captured as structured RuntimeErrorEvent and pushed
        to the canonical error buffer. They are observable through the
        dashboard and integration status. The simulation continues unless
        the error is marked fatal.
    """

    def __init__(
        self,
        homeostasis_engine: HomeostasisEngine,
        coordinator: SelfOrganizationCoordinator,
        *,
        interval_ticks: int = 10,
        policy_config: SelfOrganizationPolicyConfig | None = None,
        error_buffer: ErrorBuffer | None = None,
    ) -> None:
        self.homeostasis_engine = homeostasis_engine
        self.coordinator = coordinator
        self.interval_ticks = interval_ticks
        self.policy = SelfOrganizationPolicy(
            policy_config or SelfOrganizationPolicyConfig(enabled=True, dry_run=True)
        )
        self._last_tick: int = 0
        self._error_buffer = error_buffer or _runtime_error_buffer

    def __call__(self, tick: int, _result: Any) -> None:  # noqa: ARG001
        """Post-tick hook: build signal, run policy, publish to coordinator.

        Runs every ``interval_ticks`` ticks to avoid excessive overhead.

        Errors are captured as structured RuntimeErrorEvent and pushed to
        the error buffer. The simulation continues — a hook error must
        never break the simulation.
        """
        if tick - self._last_tick < self.interval_ticks:
            return
        self._last_tick = tick

        # --- Phase: build_signal ---
        try:
            signal = self.homeostasis_engine.build_signal(tick=tick)
        except Exception as exc:
            self._capture_error(tick, "build_signal", exc)
            return

        # --- Phase: analyze ---
        try:
            report = self.policy.analyze(signal)
        except Exception as exc:
            self._capture_error(tick, "analyze", exc)
            return

        # --- Phase: publish ---
        if report.proposals:
            try:
                self.coordinator.publish(report)
            except Exception as exc:
                self._capture_error(tick, "publish", exc)
                return

    def _capture_error(self, tick: int, phase: str, exc: Exception) -> None:
        """Capture a structured error event."""
        import hashlib
        import time

        tb_text = traceback.format_exc()
        tb_hash = hashlib.sha256(tb_text.encode("utf-8")).hexdigest()[:16]

        event = RuntimeErrorEvent(
            timestamp=time.monotonic_ns(),
            tick=tick,
            component="SelfOrganizationRuntimeAdapter",
            phase=phase,
            exception_type=f"{type(exc).__module__}.{type(exc).__qualname__}",
            message=str(exc),
            fatal=False,
            traceback_hash=tb_hash,
        )
        self._error_buffer.push(event)
