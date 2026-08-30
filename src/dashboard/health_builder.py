"""Build component status and health snapshots for the operator workbench.

This module derives standardized ``ComponentStatus`` entries and an aggregated
``HealthSnapshot`` from a ``DashboardSnapshot``, the operator bridge and the
runtime configuration.  It is the single source of truth for the dashboard's
health / problems view.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .models import (
    ComponentStatus,
    DashboardSnapshot,
    HealthSnapshot,
    ParameterSchema,
)


# ============================================================================
# Helpers
# ============================================================================


def _utc_now() -> str:
    """Return an ISO timestamp in UTC."""
    return datetime.now(timezone.utc).isoformat()


def _is_enabled(cfg: dict[str, Any] | None, *path: str) -> bool:
    """Safely read a nested boolean config flag."""
    if cfg is None:
        return False
    node: Any = cfg
    for key in path:
        if not isinstance(node, dict) or key not in node:
            return False
        node = node[key]
    return bool(node)


def _nested_get(cfg: dict[str, Any] | None, *path: str, default: Any = None) -> Any:
    """Safely read a nested config value."""
    if cfg is None:
        return default
    node: Any = cfg
    for key in path:
        if not isinstance(node, dict) or key not in node:
            return default
        node = node[key]
    return node


# ============================================================================
# Component Status Builders
# ============================================================================


def _runtime_status(snapshot: DashboardSnapshot) -> ComponentStatus:
    """Derive runtime component status from the dashboard snapshot."""
    status = "active" if snapshot.status in ("running", "idle") else "unavailable"
    if snapshot.status == "error":
        status = "error"
    return ComponentStatus(
        component="runtime",
        status=status,
        reason=f"Dashboard status is '{snapshot.status}'",
        last_update=_utc_now(),
        source="DashboardStateStore",
        maturity="integrated",
    )


def _network_status(snapshot: DashboardSnapshot) -> ComponentStatus:
    """Derive network component status."""
    neurons = snapshot.system.neurons
    synapses = snapshot.system.synapses
    reason = f"{neurons} neurons, {synapses} synapses"
    status = "active" if neurons > 0 else "unavailable"
    return ComponentStatus(
        component="network",
        status=status,
        reason=reason,
        last_update=_utc_now(),
        source="DashboardStateStore",
        maturity="integrated",
    )


def _learning_status(
    snapshot: DashboardSnapshot,
    config_dict: dict[str, Any] | None,
) -> ComponentStatus:
    """Derive learning component status.

    ``enabled`` reflects configuration; ``active`` reflects runtime activity
    measured by STDP/reward update counters.
    """
    enabled = _is_enabled(config_dict, "stdp", "enabled") or _is_enabled(
        config_dict, "reward", "enabled"
    )
    active = snapshot.learning.stdp_updates > 0 or snapshot.learning.reward_updates > 0

    if not enabled:
        return ComponentStatus(
            component="learning",
            status="disabled",
            reason="Learning is disabled by config (stdp.enabled / reward.enabled)",
            last_update=_utc_now(),
            source="config",
            maturity="integrated",
        )
    if active:
        return ComponentStatus(
            component="learning",
            status="active",
            reason=(
                f"STDP updates: {snapshot.learning.stdp_updates}, "
                f"reward updates: {snapshot.learning.reward_updates}"
            ),
            last_update=_utc_now(),
            source="DashboardStateStore",
            maturity="integrated",
        )
    return ComponentStatus(
        component="learning",
        status="enabled",
        reason="Learning is enabled by config but has no updates yet",
        last_update=_utc_now(),
        source="DashboardStateStore",
        maturity="integrated",
    )


def _homeostasis_status(
    snapshot: DashboardSnapshot,
    config_dict: dict[str, Any] | None,
) -> ComponentStatus:
    """Derive homeostasis component status.

    ``enabled`` reflects configuration; ``active`` reflects runtime activity
    measured by regulator updates.
    """
    enabled = _is_enabled(config_dict, "homeostasis", "enabled")
    active = snapshot.homeostasis.updates > 0

    if not enabled:
        return ComponentStatus(
            component="homeostasis",
            status="disabled",
            reason="Homeostasis is disabled by config",
            last_update=_utc_now(),
            source="config",
            maturity="integrated",
        )
    if active:
        return ComponentStatus(
            component="homeostasis",
            status="active",
            reason=(
                f"Target rate {snapshot.homeostasis.target_rate_hz:.3f} Hz, "
                f"updates: {snapshot.homeostasis.updates}"
            ),
            last_update=_utc_now(),
            source="DashboardStateStore",
            maturity="integrated",
        )
    return ComponentStatus(
        component="homeostasis",
        status="enabled",
        reason="Homeostasis is enabled by config but has not updated yet",
        last_update=_utc_now(),
        source="DashboardStateStore",
        maturity="integrated",
    )


def _structural_status(
    snapshot: DashboardSnapshot,
    config_dict: dict[str, Any] | None,
) -> ComponentStatus:
    """Derive structural plasticity component status.

    ``enabled`` reflects configuration; ``active`` reflects runtime activity
    measured by self-organization counters.
    """
    enabled = _is_enabled(config_dict, "self_organization", "enabled")
    active = (
        (snapshot.self_organization.neurons_created or 0) > 0
        or (snapshot.self_organization.neurons_removed or 0) > 0
        or (snapshot.self_organization.synapses_created or 0) > 0
        or (snapshot.self_organization.synapses_pruned or 0) > 0
    )

    if not enabled:
        return ComponentStatus(
            component="structural",
            status="disabled",
            reason="Self-organization is disabled by config",
            last_update=_utc_now(),
            source="config",
            maturity="integrated",
        )
    if active:
        return ComponentStatus(
            component="structural",
            status="active",
            reason=(
                f"Created {snapshot.self_organization.neurons_created or 0} neurons, "
                f"pruned {snapshot.self_organization.synapses_pruned or 0} synapses"
            ),
            last_update=_utc_now(),
            source="DashboardStateStore",
            maturity="integrated",
        )
    return ComponentStatus(
        component="structural",
        status="enabled",
        reason="Self-organization is enabled by config but has not changed structure yet",
        last_update=_utc_now(),
        source="DashboardStateStore",
        maturity="integrated",
    )


def _storage_status(
    snapshot: DashboardSnapshot,
    config_dict: dict[str, Any] | None,
) -> ComponentStatus:
    """Derive storage component status.

    ``enabled`` reflects configuration; ``active`` reflects runtime activity
    measured by deltas written.
    """
    storage = snapshot.storage
    enabled = _is_enabled(config_dict, "storage", "enabled")

    if not enabled:
        return ComponentStatus(
            component="storage",
            status="disabled",
            reason="Storage is disabled by config",
            last_update=_utc_now(),
            source="config",
            maturity="integrated",
        )
    if storage.worker_failed:
        return ComponentStatus(
            component="storage",
            status="error",
            reason="Storage worker failed",
            last_update=_utc_now(),
            source="DashboardStateStore",
            last_error="worker_failed flag is set",
            maturity="integrated",
        )
    if storage.dropped_batches:
        return ComponentStatus(
            component="storage",
            status="degraded",
            reason=f"{storage.dropped_batches} dropped batches",
            last_update=_utc_now(),
            source="DashboardStateStore",
            maturity="integrated",
        )
    if storage.deltas_written:
        return ComponentStatus(
            component="storage",
            status="active",
            reason=f"{storage.deltas_written} deltas written",
            last_update=_utc_now(),
            source="DashboardStateStore",
            maturity="integrated",
        )
    return ComponentStatus(
        component="storage",
        status="enabled",
        reason="Storage is enabled by config but has not written deltas yet",
        last_update=_utc_now(),
        source="DashboardStateStore",
        maturity="integrated",
    )


def _telemetry_status(snapshot: DashboardSnapshot) -> ComponentStatus:
    """Derive telemetry component status."""
    return ComponentStatus(
        component="telemetry",
        status="active",
        reason=f"Tick {snapshot.system.tick} published",
        last_update=_utc_now(),
        source="DashboardStateStore",
        maturity="integrated",
    )


def _health_status(components: dict[str, ComponentStatus]) -> ComponentStatus:
    """Derive health subsystem status from the other components.

    The health component reflects the aggregate state of all other
    components.  It must not depend on the snapshot's own health field,
    because that would create a circular definition during enrichment.
    """
    errors = 0
    warnings = 0
    unavailable = 0
    stale_count = 0
    for comp in components.values():
        if comp.component == "health":
            continue
        if comp.status == "error":
            errors += 1
        elif comp.status == "degraded":
            warnings += 1
        elif comp.status == "unavailable":
            unavailable += 1
        elif comp.status == "stale":
            stale_count += 1

    if errors:
        status = "error"
        reason = f"{errors} component(s) reported error"
    elif warnings:
        status = "degraded"
        reason = f"{warnings} component(s) degraded"
    elif unavailable:
        status = "unavailable"
        reason = f"{unavailable} component(s) unavailable"
    elif stale_count:
        status = "stale"
        reason = f"{stale_count} component(s) stale"
    else:
        status = "active"
        reason = "All components healthy"

    return ComponentStatus(
        component="health",
        status=status,
        reason=reason,
        last_update=_utc_now(),
        source="HealthBuilder",
        maturity="integrated",
    )


def _verification_status(snapshot: DashboardSnapshot) -> ComponentStatus:
    """Derive verification component status."""
    return ComponentStatus(
        component="verification",
        status="active",
        reason="Verification endpoint available",
        last_update=_utc_now(),
        source="DashboardStateStore",
        maturity="implemented",
    )


# ============================================================================
# Health Aggregation
# ============================================================================


def _severity(status: str) -> str:
    """Map component status to problem severity."""
    return {
        "error": "error",
        "degraded": "warning",
        "stale": "stale",
        "unavailable": "unavailable",
    }.get(status, "info")


def _derive_problems(components: dict[str, ComponentStatus]) -> HealthSnapshot:
    """Build a HealthSnapshot from component statuses."""
    problems: list[ComponentStatus] = []
    errors = 0
    warnings = 0
    stale_count = 0
    unavailable_count = 0

    for comp in components.values():
        if comp.status in {"error", "degraded", "stale", "unavailable"}:
            problems.append(comp)
            sev = _severity(comp.status)
            if sev == "error":
                errors += 1
            elif sev == "warning":
                warnings += 1
            elif sev == "stale":
                stale_count += 1
            elif sev == "unavailable":
                unavailable_count += 1

    overall = "ok"
    if errors:
        overall = "error"
    elif warnings:
        overall = "degraded"
    elif unavailable_count:
        overall = "unavailable"
    elif stale_count:
        overall = "stale"

    return HealthSnapshot(
        overall=overall,
        problems=tuple(problems),
        errors=errors,
        warnings=warnings,
        stale=stale_count,
        unavailable=unavailable_count,
    )


# ============================================================================
# Parameter Schema Builders
# ============================================================================


def _param(
    name: str,
    value: Any,
    *,
    default: Any = None,
    min: Any = None,  # noqa: A002
    max: Any = None,  # noqa: A002
    unit: str | None = None,
    description: str = "",
    source: str = "config",
    runtime_mutable: bool = False,
    requires_restart: bool = False,
    scientific_sensitive: bool = False,
) -> ParameterSchema:
    """Convenience wrapper to create a ParameterSchema."""
    return ParameterSchema(
        name=name,
        value=value,
        default=default,
        min=min,
        max=max,
        unit=unit,
        description=description,
        source=source,
        runtime_mutable=runtime_mutable,
        requires_restart=requires_restart,
        scientific_sensitive=scientific_sensitive,
    )


def build_parameters(config_dict: dict[str, Any] | None) -> dict[str, ParameterSchema]:
    """Build parameter schema entries from the runtime configuration.

    Only a curated set of scientifically relevant parameters is exposed.
    """
    if config_dict is None:
        return {}

    params: dict[str, ParameterSchema] = {}

    # Simulation
    params["simulation.dt_ms"] = _param(
        "simulation.dt_ms",
        _nested_get(config_dict, "simulation", "dt_ms", default=1.0),
        default=1.0,
        min=0.0,
        max=1000.0,
        unit="ms",
        description="Simulation time step in milliseconds.",
        runtime_mutable=False,
        requires_restart=True,
        scientific_sensitive=True,
    )
    params["simulation.ticks"] = _param(
        "simulation.ticks",
        _nested_get(config_dict, "simulation", "ticks", default=0),
        default=0,
        min=0,
        unit="ticks",
        description="Total ticks to run in headless mode.",
        runtime_mutable=True,
    )

    # Network
    params["network.initial_connections_per_neuron"] = _param(
        "network.initial_connections_per_neuron",
        _nested_get(config_dict, "network", "initial_connections_per_neuron", default=10),
        default=10,
        min=0,
        max=10000,
        description="Initial synaptic connections per neuron.",
        requires_restart=True,
        scientific_sensitive=True,
    )
    params["network.neighbour_radius"] = _param(
        "network.neighbour_radius",
        _nested_get(config_dict, "network", "neighbour_radius", default=5.0),
        default=5.0,
        min=0.0,
        unit="coordinates",
        description="Radius for local connection initialization.",
        requires_restart=True,
        scientific_sensitive=True,
    )

    # Learning
    params["stdp.enabled"] = _param(
        "stdp.enabled",
        _nested_get(config_dict, "stdp", "enabled", default=False),
        default=False,
        description="Whether STDP learning is enabled.",
        runtime_mutable=False,
        requires_restart=True,
        scientific_sensitive=True,
    )
    params["reward.enabled"] = _param(
        "reward.enabled",
        _nested_get(config_dict, "reward", "enabled", default=False),
        default=False,
        description="Whether reward-modulated plasticity is enabled.",
        runtime_mutable=False,
        requires_restart=True,
        scientific_sensitive=True,
    )

    # Homeostasis
    params["homeostasis.enabled"] = _param(
        "homeostasis.enabled",
        _nested_get(config_dict, "homeostasis", "enabled", default=False),
        default=False,
        description="Whether homeostatic regulation is enabled.",
        runtime_mutable=False,
        requires_restart=True,
        scientific_sensitive=True,
    )
    params["homeostasis.target_rate_hz"] = _param(
        "homeostasis.target_rate_hz",
        _nested_get(config_dict, "homeostasis", "target_rate_hz", default=5.0),
        default=5.0,
        min=0.0,
        max=1000.0,
        unit="Hz",
        description="Target firing rate for homeostasis.",
        runtime_mutable=True,
        scientific_sensitive=True,
    )

    # Self-organization
    params["self_organization.enabled"] = _param(
        "self_organization.enabled",
        _nested_get(config_dict, "self_organization", "enabled", default=False),
        default=False,
        description="Whether structural self-organization is enabled.",
        runtime_mutable=False,
        requires_restart=True,
        scientific_sensitive=True,
    )

    # Storage
    params["storage.enabled"] = _param(
        "storage.enabled",
        _nested_get(config_dict, "storage", "enabled", default=False),
        default=False,
        description="Whether delta storage is enabled.",
        runtime_mutable=False,
        requires_restart=True,
    )

    return params


# ============================================================================
# Public API
# ============================================================================


def build_component_status(
    snapshot: DashboardSnapshot,
    config_dict: dict[str, Any] | None = None,
) -> dict[str, ComponentStatus]:
    """Build all component statuses for the operator workbench.

    Args:
        snapshot: Current dashboard snapshot.
        config_dict: Optional runtime configuration for additional context.

    Returns:
        Dictionary mapping component key to ComponentStatus.
    """
    components: dict[str, ComponentStatus] = {
        "runtime": _runtime_status(snapshot),
        "network": _network_status(snapshot),
        "learning": _learning_status(snapshot, config_dict),
        "homeostasis": _homeostasis_status(snapshot, config_dict),
        "structural": _structural_status(snapshot, config_dict),
        "storage": _storage_status(snapshot, config_dict),
        "telemetry": _telemetry_status(snapshot),
        "verification": _verification_status(snapshot),
    }
    components["health"] = _health_status(components)

    return components


def build_health(snapshot: DashboardSnapshot) -> HealthSnapshot:
    """Build the aggregated health snapshot from component statuses."""
    components = build_component_status(snapshot)
    return _derive_problems(components)


def enrich_snapshot(
    snapshot: DashboardSnapshot,
    config_dict: dict[str, Any] | None = None,
) -> DashboardSnapshot:
    """Return a new snapshot enriched with components, parameters and health.

    This is a pure function: the input snapshot is not mutated.
    """
    from dataclasses import replace

    components = build_component_status(snapshot, config_dict)
    parameters = build_parameters(config_dict)
    health = _derive_problems(components)

    return replace(
        snapshot,
        components=components,
        parameters=parameters,
        health=health,
    )
