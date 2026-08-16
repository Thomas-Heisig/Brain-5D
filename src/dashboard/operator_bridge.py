"""Typed bridge used by HTTP handlers to control Brain-5D safely."""

from __future__ import annotations

from dataclasses import replace
from typing import TypeAlias, cast

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

from .structural_api import StructuralCommandResult

JSONValue: TypeAlias = (
    str | int | float | bool | None | list["JSONValue"] | dict[str, "JSONValue"]
)
JSONMapping: TypeAlias = dict[str, JSONValue]


class OperatorBridge:
    """Translate dashboard requests into typed controller operations."""

    def __init__(
        self,
        controller: RuntimeController,
        coordinator: SelfOrganizationCoordinator | None = None,
        plasticity: StructuralPlasticityEngine | None = None,
        approval_policy: ProposalApprovalPolicy | None = None,
        structural_heatmaps: StructuralHeatmapSource | None = None,
    ) -> None:
        self.controller = controller
        self.coordinator = coordinator
        self.plasticity = plasticity
        self.approval_policy = approval_policy
        self.structural_heatmaps = structural_heatmaps

    def status(self) -> JSONMapping:
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
        report = self.coordinator.latest() if self.coordinator is not None else None
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
        if self.plasticity is not None:
            history_values: list[JSONValue] = []
            history_values.extend(self.structural_history(100))
            payload["structural_history"] = history_values
        return payload

    def structural_status(self) -> JSONMapping:
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

    def structural_proposals(self) -> list[JSONMapping]:
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

    def structural_history(self, limit: int) -> list[JSONMapping]:
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

    def structural_heatmap(self, kind: str) -> JSONMapping:
        source = self.structural_heatmaps
        if source is None or self.plasticity is None:
            raise RuntimeError("structural heatmap is not configured")
        allowed = {
            "neuron_additions",
            "neuron_removals",
            "synapse_additions",
            "synapse_removals",
            "total_structural_activity",
        }
        if kind not in allowed:
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

    def structural_config(self) -> JSONMapping:
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

    def command(self, command: str, *, ticks: int | None = None) -> JSONMapping:
        try:
            cmd = ControllerCommand(command)
        except ValueError:
            return {"ok": False, "error": f"unknown command: {command}"}
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
        return {"ok": True, "status": self.status()}

    def apply_proposal(self, proposal_id: str, *, approved: bool) -> JSONMapping:
        if self.coordinator is None or self.plasticity is None:
            return {"ok": False, "error": "structural plasticity not configured"}
        proposal = self.coordinator.find(proposal_id)
        if proposal is None:
            return {"ok": False, "error": "proposal not found"}
        decision_recorded = (
            self.coordinator.approve(proposal_id)
            if approved
            else self.coordinator.reject(proposal_id)
        )
        if not decision_recorded:
            return {"ok": False, "error": "proposal not found"}
        change = self.plasticity.apply_proposal(
            self.controller.telemetry.tick,
            proposal,
            approved=approved,
        )
        return {
            "ok": change is not None,
            "change": (
                None
                if change is None
                else {
                    "tick": change.tick,
                    "proposal_id": change.proposal_id,
                    "kind": change.kind.value,
                    "description": change.description,
                }
            ),
        }

    def undo(self) -> JSONMapping:
        result = self.undo_structural()
        return {"ok": result.ok, "message": result.message}

    def approve_structural(self, proposal_id: str) -> StructuralCommandResult:
        result = self.apply_proposal(proposal_id, approved=True)
        return StructuralCommandResult(
            bool(result.get("ok", False)),
            (
                "proposal applied"
                if result.get("ok")
                else str(result.get("error", "proposal rejected"))
            ),
        )

    def reject_structural(self, proposal_id: str) -> StructuralCommandResult:
        coordinator = self.coordinator
        if coordinator is None:
            return StructuralCommandResult(
                False, "structural coordinator not configured"
            )
        if not coordinator.reject(proposal_id):
            return StructuralCommandResult(False, "proposal not found")
        return StructuralCommandResult(True, "proposal rejected")

    def undo_structural(self) -> StructuralCommandResult:
        if self.plasticity is None:
            return StructuralCommandResult(
                False, "structural plasticity not configured"
            )
        undone = self.plasticity.undo_last_change(tick=self.controller.telemetry.tick)
        return StructuralCommandResult(
            undone, "change undone" if undone else "nothing to undo"
        )

    def set_auto_approval(self, enabled: bool) -> StructuralCommandResult:
        policy = self.approval_policy
        if policy is None:
            policy = ProposalApprovalPolicy(StructuralPlasticityConfig())
        self.approval_policy = ProposalApprovalPolicy(
            replace(policy.config, auto_approval=enabled)
        )
        return StructuralCommandResult(True, "auto-approval configuration updated")

    def run_ticks(self, count: int) -> StructuralCommandResult:
        self.controller.run_ticks(count)
        return StructuralCommandResult(True, f"executed {count} ticks")

    def single_step(self) -> StructuralCommandResult:
        self.controller.single_step()
        return StructuralCommandResult(True, "executed one tick")

    def request_snapshot(self) -> StructuralCommandResult:
        self.controller.request_snapshot()
        return StructuralCommandResult(True, "snapshot requested")
