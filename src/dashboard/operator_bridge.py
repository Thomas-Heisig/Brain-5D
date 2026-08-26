"""Typed bridge used by HTTP handlers to control Brain-5D safely.

This module provides the OperatorBridge class, which translates dashboard
HTTP requests into typed controller operations with proper error handling
and consistent response formatting.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any, TypeAlias, cast

from src.controller.runtime import ControllerCommand, RuntimeController
from src.self_organization.approval import (
    ProposalApprovalPolicy,
    StructuralPlasticityConfig,
)
from src.self_organization.coordinator import SelfOrganizationCoordinator
from src.self_organization.plasticity import StructuralPlasticityEngine
from src.visualization.structural_heatmap import (
    StructuralHeatmapKind,
    StructuralHeatmapSource,
)

from .models import (
    JSONValue,
    StructuralMetrics,
    SystemMetrics,
    to_json_serializable,
)
from .structural_api import StructuralCommandResult
from src.self_organization.runtime_adapter import get_error_buffer

# Type aliases for JSON responses
JSONMapping: TypeAlias = dict[str, JSONValue]

# Allowed heatmap kinds
HEATMAP_KINDS = {
    "neuron_additions",
    "neuron_removals",
    "synapse_additions",
    "synapse_removals",
    "total_structural_activity",
}


class OperatorBridge:
    """Translate dashboard requests into typed controller operations.

    This bridge provides a clean, type-safe interface between the HTTP
    dashboard endpoints and the Brain-5D runtime controller. It handles
    structural plasticity coordination, heatmap generation, and all
    controller commands.

    All methods that return JSONMapping are guaranteed to produce
    JSON-serializable responses with consistent error handling.
    """

    def __init__(
        self,
        controller: RuntimeController,
        coordinator: SelfOrganizationCoordinator | None = None,
        plasticity: StructuralPlasticityEngine | None = None,
        approval_policy: ProposalApprovalPolicy | None = None,
        structural_heatmaps: StructuralHeatmapSource | None = None,
    ) -> None:
        """Initialize the operator bridge.

        Args:
            controller: The runtime controller instance (required).
            coordinator: Optional self-organization coordinator.
            plasticity: Optional structural plasticity engine.
            approval_policy: Optional proposal approval policy.
            structural_heatmaps: Optional heatmap source for visualizations.
        """
        # controller is required by type annotation, so no None check needed
        self.controller = controller
        self.coordinator = coordinator
        self.plasticity = plasticity
        self.approval_policy = approval_policy
        self.structural_heatmaps = structural_heatmaps

    # =========================================================================
    # Status and Telemetry
    # =========================================================================

    def status(self) -> JSONMapping:
        """Get the current system status as a JSON-serializable dictionary.

        Returns:
            Complete system status including telemetry, self-organization
            reports, and structural history.
        """
        telemetry = self.controller.telemetry

        payload: JSONMapping = {
            "state": telemetry.controller_state.value,
            "tick": telemetry.tick,
            "ticks_per_second": telemetry.ticks_per_second,
            "batch_duration_ms": telemetry.batch_duration_ms,
            "spikes_this_batch": telemetry.spikes_this_batch,
            "neurons": telemetry.neurons,
            "synapses": telemetry.synapses,
            "queue_depth": telemetry.queue_depth,
            "requested_ticks": telemetry.requested_ticks,
            "completed_ticks": telemetry.completed_ticks,
            "last_error": telemetry.last_error,
        }

        # Add self-organization report if available
        if self.coordinator is not None:
            report = self.coordinator.latest()
            if report is not None:
                payload["self_organization"] = {
                    "tick": report.tick,
                    "neurogenesis_pressure": report.neurogenesis_pressure,
                    "pruning_pressure": report.pruning_pressure,
                    "synapse_sprouting_pressure": report.synapse_sprouting_pressure,
                    "synapse_pruning_pressure": report.synapse_pruning_pressure,
                    "proposals": [
                        {
                            "proposal_id": p.proposal_id,
                            "kind": p.kind.value,
                            "neuron_id": p.neuron_id,
                            "target_id": p.target_id,
                            "reason": p.reason,
                            "confidence": p.confidence,
                        }
                        for p in report.proposals
                    ],
                }

        # Add structural history if available - cast to JSONValue to satisfy type checker
        if self.plasticity is not None:
            payload["structural_history"] = cast(
                list[JSONValue], self.structural_history(100)
            )

        return payload

    def structural_status(self) -> JSONMapping:
        """Get structural plasticity subsystem status.

        Returns:
            Dictionary with configuration and proposal statistics.
        """
        report = self.coordinator.latest() if self.coordinator is not None else None

        return {
            "configured": self.coordinator is not None and self.plasticity is not None,
            "proposal_tick": report.tick if report is not None else None,
            "proposal_count": len(report.proposals) if report is not None else 0,
            "decision_count": (
                len(self.coordinator.decisions()) if self.coordinator is not None else 0
            ),
            "history_count": (
                len(self.plasticity.history()) if self.plasticity is not None else 0
            ),
        }

    def structural_config(self) -> JSONMapping:
        """Get the current structural plasticity configuration.

        Returns:
            Dictionary with all configuration parameters, or a minimal
            response if not configured.
        """
        policy = self.approval_policy
        if policy is None:
            return {"configured": False}

        config = policy.config
        return {
            "configured": True,
            "enabled": config.enabled,
            "dry_run": config.dry_run,
            "auto_approval": config.auto_approval,
            "auto_approval_threshold": config.auto_approval_threshold,
            "max_changes_per_tick": config.max_changes_per_tick,
            "max_neuron_additions_per_tick": config.max_neuron_additions_per_tick,
            "max_neuron_removals_per_tick": config.max_neuron_removals_per_tick,
            "max_synapse_additions_per_tick": config.max_synapse_additions_per_tick,
            "max_synapse_removals_per_tick": config.max_synapse_removals_per_tick,
            "min_neurons": config.min_neurons,
            "max_neurons": config.max_neurons,
            "allow_neuron_pruning": config.allow_neuron_pruning,
            "allow_synapse_pruning": config.allow_synapse_pruning,
            "cooldown_ticks": config.cooldown_ticks,
        }

    # =========================================================================
    # Self-Organization Proposals
    # =========================================================================

    def structural_proposals(self) -> list[JSONMapping]:
        """Get all pending structural plasticity proposals.

        Returns:
            List of proposal dictionaries, each with ID, kind, and metadata.
        """
        report = self.coordinator.latest() if self.coordinator is not None else None
        if report is None:
            return []

        return [
            {
                "proposal_id": proposal.proposal_id,
                "kind": proposal.kind.value,
                "neuron_id": proposal.neuron_id,
                "target_id": proposal.target_id,
                "reason": proposal.reason,
                "confidence": proposal.confidence,
            }
            for proposal in report.proposals
        ]

    def structural_history(self, limit: int = 100) -> list[JSONMapping]:
        """Get structural plasticity history records.

        Args:
            limit: Maximum number of records to return.

        Returns:
            List of history record dictionaries.
        """
        if self.plasticity is None:
            return []

        return [
            {
                "sequence": record.sequence,
                "tick": record.tick,
                "kind": record.kind.value,
                "proposal_id": record.proposal_id,
                "neuron_id": record.neuron_id,
                "source_id": record.source_id,
                "target_id": record.target_id,
                "reason": record.reason,
                "approved_by": record.approved_by,
                "automatic": record.automatic,
                "undo_of_sequence": record.undo_of_sequence,
            }
            for record in self.plasticity.history(limit)
        ]

    # =========================================================================
    # Heatmap Generation
    # =========================================================================

    def structural_heatmap(self, kind: str) -> JSONMapping:
        """Generate a structural plasticity heatmap.

        Args:
            kind: Heatmap type (neuron_additions, neuron_removals,
                 synapse_additions, synapse_removals,
                 total_structural_activity).

        Returns:
            Heatmap data including values, range, and metadata.

        Raises:
            RuntimeError: If heatmap source or plasticity engine is not configured.
            ValueError: If the heatmap kind is unknown.
        """
        source = self.structural_heatmaps
        if source is None:
            raise RuntimeError("structural heatmap source is not configured")

        if self.plasticity is None:
            raise RuntimeError("structural plasticity engine is not configured")

        if kind not in HEATMAP_KINDS:
            raise ValueError(f"unknown structural heatmap kind: {kind}")

        result = source.build(
            self.plasticity.history(),
            cast(StructuralHeatmapKind, kind),
        )

        return {
            "kind": result.kind,
            "values": result.values.tolist(),
            "min_value": result.min_value,
            "max_value": result.max_value,
            "populated_cells": result.populated_cells,
            "sequence_from": result.sequence_from,
            "sequence_to": result.sequence_to,
        }

    # =========================================================================
    # Controller Commands
    # =========================================================================

    def command(self, command: str, *, ticks: int | None = None) -> JSONMapping:
        """Execute a controller command.

        Args:
            command: Command name (start, pause, resume, stop, step, run_ticks, snapshot).
            ticks: Number of ticks to run (for run_ticks command).

        Returns:
            JSON response with success status and current status.
        """
        try:
            cmd = ControllerCommand(command)
        except ValueError:
            return {"ok": False, "error": f"unknown command: {command}"}

        try:
            if cmd == ControllerCommand.START:
                self.controller.start()
            elif cmd == ControllerCommand.PAUSE:
                self.controller.pause()
            elif cmd == ControllerCommand.RESUME:
                self.controller.resume()
            elif cmd == ControllerCommand.STOP:
                self.controller.stop()
            elif cmd == ControllerCommand.STEP:
                self.controller.step_once()
            elif cmd == ControllerCommand.RUN_TICKS:
                self.controller.run_ticks(ticks or 1)
            elif cmd == ControllerCommand.SNAPSHOT:
                self.controller.request_snapshot()
        except Exception as e:
            return {"ok": False, "error": str(e)}

        return {"ok": True, "status": self.status()}

    # =========================================================================
    # Proposal Management
    # =========================================================================

    def apply_proposal(self, proposal_id: str, *, approved: bool) -> JSONMapping:
        """Apply or reject a structural proposal.

        Args:
            proposal_id: ID of the proposal to process.
            approved: Whether to approve (True) or reject (False).

        Returns:
            JSON response with success status and change details.
        """
        if self.coordinator is None:
            return {"ok": False, "error": "structural coordinator not configured"}

        if self.plasticity is None:
            return {"ok": False, "error": "structural plasticity not configured"}

        proposal = self.coordinator.find(proposal_id)
        if proposal is None:
            return {"ok": False, "error": f"proposal not found: {proposal_id}"}

        # Record the decision
        decision_recorded = (
            self.coordinator.approve(proposal_id)
            if approved
            else self.coordinator.reject(proposal_id)
        )

        if not decision_recorded:
            return {
                "ok": False,
                "error": f"failed to record decision for: {proposal_id}",
            }

        # Apply the change if approved
        if approved:
            change = self.plasticity.apply_proposal(
                self.controller.telemetry.tick,
                proposal,
                approved=True,
            )

            if change is None:
                return {"ok": False, "error": "failed to apply approved proposal"}

            return {
                "ok": True,
                "change": {
                    "tick": change.tick,
                    "proposal_id": change.proposal_id,
                    "kind": change.kind.value,
                    "description": change.description,
                },
            }

        return {"ok": True, "change": None}

    def approve_structural(self, proposal_id: str) -> StructuralCommandResult:
        """Approve a structural plasticity proposal.

        Args:
            proposal_id: ID of the proposal to approve.

        Returns:
            StructuralCommandResult with success status and message.
        """
        if self.coordinator is None:
            return StructuralCommandResult(
                False, "structural coordinator not configured"
            )

        if self.plasticity is None:
            return StructuralCommandResult(
                False, "structural plasticity not configured"
            )

        proposal = self.coordinator.find(proposal_id)
        if proposal is None:
            return StructuralCommandResult(False, f"proposal not found: {proposal_id}")

        if not self.coordinator.approve(proposal_id):
            return StructuralCommandResult(False, "failed to approve proposal")

        change = self.plasticity.apply_proposal(
            self.controller.telemetry.tick,
            proposal,
            approved=True,
        )

        if change is None:
            return StructuralCommandResult(False, "failed to apply approved proposal")

        return StructuralCommandResult(
            True, f"proposal {proposal_id} approved and applied"
        )

    def reject_structural(self, proposal_id: str) -> StructuralCommandResult:
        """Reject a structural plasticity proposal.

        Args:
            proposal_id: ID of the proposal to reject.

        Returns:
            StructuralCommandResult with success status and message.
        """
        coordinator = self.coordinator
        if coordinator is None:
            return StructuralCommandResult(
                False, "structural coordinator not configured"
            )

        if not coordinator.reject(proposal_id):
            return StructuralCommandResult(False, f"proposal not found: {proposal_id}")

        return StructuralCommandResult(True, f"proposal {proposal_id} rejected")

    def undo_structural(self) -> StructuralCommandResult:
        """Undo the last structural plasticity change.

        Returns:
            StructuralCommandResult with success status and message.
        """
        if self.plasticity is None:
            return StructuralCommandResult(
                False, "structural plasticity not configured"
            )

        undone = self.plasticity.undo_last_change(tick=self.controller.telemetry.tick)

        if undone:
            return StructuralCommandResult(True, "last change undone")
        return StructuralCommandResult(False, "no changes to undo")

    # =========================================================================
    # Configuration Management
    # =========================================================================

    def set_auto_approval(self, enabled: bool) -> StructuralCommandResult:
        """Enable or disable automatic approval of proposals.

        Args:
            enabled: Whether to enable auto-approval.

        Returns:
            StructuralCommandResult with success status and message.
        """
        if self.approval_policy is None:
            # Create a new policy with default config
            self.approval_policy = ProposalApprovalPolicy(
                StructuralPlasticityConfig(auto_approval=enabled)
            )
        else:
            # Update existing policy
            self.approval_policy = ProposalApprovalPolicy(
                replace(self.approval_policy.config, auto_approval=enabled)
            )

        return StructuralCommandResult(
            True, f"auto-approval {'enabled' if enabled else 'disabled'}"
        )

    def update_structural_config(self, **kwargs: Any) -> StructuralCommandResult:
        """Update structural plasticity configuration parameters.

        Args:
            **kwargs: Configuration parameters to update.

        Returns:
            StructuralCommandResult with success status and message.
        """
        if self.approval_policy is None:
            return StructuralCommandResult(
                False, "structural plasticity not configured"
            )

        # Get current config and update with new values
        current = self.approval_policy.config
        config_dict = {
            k: v for k, v in current.__dict__.items() if not k.startswith("_")
        }

        for key, value in kwargs.items():
            if key in config_dict:
                config_dict[key] = value
            else:
                return StructuralCommandResult(
                    False, f"unknown config parameter: {key}"
                )

        # Create new config and policy
        new_config = StructuralPlasticityConfig(**config_dict)
        self.approval_policy = ProposalApprovalPolicy(new_config)

        return StructuralCommandResult(True, "configuration updated")

    # =========================================================================
    # Convenience Methods
    # =========================================================================

    def run_ticks(self, count: int) -> StructuralCommandResult:
        """Run a specified number of ticks.

        Args:
            count: Number of ticks to execute.

        Returns:
            StructuralCommandResult with success status and message.
        """
        if count <= 0:
            return StructuralCommandResult(False, "tick count must be positive")

        try:
            self.controller.run_ticks(count)
            return StructuralCommandResult(True, f"executed {count} ticks")
        except Exception as e:
            return StructuralCommandResult(False, f"failed to run ticks: {e}")

    def single_step(self) -> StructuralCommandResult:
        """Execute a single tick.

        Returns:
            StructuralCommandResult with success status and message.
        """
        try:
            self.controller.step_once()
            return StructuralCommandResult(True, "executed one tick")
        except Exception as e:
            return StructuralCommandResult(False, f"failed to execute tick: {e}")

    def request_snapshot(self) -> StructuralCommandResult:
        """Request a snapshot of the current system state.

        Returns:
            StructuralCommandResult with success status and message.
        """
        try:
            self.controller.request_snapshot()
            return StructuralCommandResult(True, "snapshot requested")
        except Exception as e:
            return StructuralCommandResult(False, f"failed to request snapshot: {e}")

    # =========================================================================
    # Metrics Extraction
    # =========================================================================

    def get_system_metrics(self) -> SystemMetrics:
        """Extract system metrics from the current telemetry.

        Returns:
            SystemMetrics object with current values.
        """
        telemetry = self.controller.telemetry
        return SystemMetrics(
            tick=telemetry.tick,
            neurons=telemetry.neurons,
            synapses=telemetry.synapses,
            spikes_total=0,  # Not available in telemetry; use spikes_this_batch instead
            spikes_last_tick=telemetry.spikes_this_batch,
            core_step_ms=telemetry.batch_duration_ms,
            mean_energy=0.0,  # Not available in telemetry; placeholder
        )

    def get_structural_metrics(self) -> StructuralMetrics:
        """Extract structural metrics from the current state.

        Returns:
            StructuralMetrics object with current values.
        """
        if self.coordinator is None or self.plasticity is None:
            return StructuralMetrics()

        report = self.coordinator.latest()
        if report is None:
            return StructuralMetrics()

        return StructuralMetrics(
            neuron_count=self.controller.telemetry.neurons,
            synapse_count=self.controller.telemetry.synapses,
            # Convert float pressures to int for the model
            new_neurons=int(report.neurogenesis_pressure),
            pruned_neurons=int(report.pruning_pressure),
            new_synapses=int(report.synapse_sprouting_pressure),
            pruned_synapses=int(report.synapse_pruning_pressure),
            growth_budget=1.0,  # Placeholder - actual value from config
            used_budget=0.0,  # Placeholder - actual value from engine
            structural_changes=len(report.proposals),
        )

    def runtime_errors(self) -> list[dict[str, JSONValue]]:
        """Return structured runtime error events for dashboard visibility.

        Returns:
            List of error event dictionaries with timestamp, tick, component,
            phase, exception_type, message, fatal, and traceback_hash.
        """
        buffer = get_error_buffer()
        return [
            {
                "timestamp": e.timestamp,
                "tick": e.tick,
                "component": e.component,
                "phase": e.phase,
                "exception_type": e.exception_type,
                "message": e.message,
                "fatal": e.fatal,
                "traceback_hash": e.traceback_hash,
            }
            for e in buffer.events
        ]

    def to_json(self, obj: Any) -> JSONValue:
        """Convert any object to a JSON-serializable value.

        Delegates to the global to_json_serializable function.
        """
        return to_json_serializable(obj)
