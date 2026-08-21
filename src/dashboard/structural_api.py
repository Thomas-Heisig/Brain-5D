"""Typed bridge contracts for structural dashboard endpoints.

This module defines the protocol and data types for the structural operator
bridge, which provides a clean interface between the dashboard HTTP layer
and the Brain-5D structural plasticity subsystem.

The StructuralOperatorBridge protocol defines all operations that can be
performed on the structural plasticity system, including:
- Querying status, proposals, history, configuration
- Approving/rejecting proposals
- Undoing changes
- Controlling auto-approval
- Runtime control (ticks, steps, snapshots)

This contract ensures consistency between the dashboard server and the
operator bridge implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable

from .models import JSONValue

# ============================================================================
# Type Aliases
# ============================================================================

JSONMapping = dict[str, JSONValue]
"""Type alias for a JSON-serializable dictionary."""


# ============================================================================
# Command Result
# ============================================================================

@dataclass(frozen=True, slots=True)
class StructuralCommandResult:
    """Result of a structural operator command.

    This immutable data class represents the outcome of a command executed
    through the StructuralOperatorBridge. It contains a success flag and
    a human-readable message describing the result.

    Attributes:
        ok: True if the command succeeded, False otherwise.
        message: A human-readable message describing the result.
            For successful commands, this typically describes what was done.
            For failed commands, this describes the error that occurred.
    """

    ok: bool
    message: str

    def to_json(self) -> JSONMapping:
        """Convert to a JSON-serializable dictionary."""
        return {"ok": self.ok, "message": self.message}

    @classmethod
    def success(cls, message: str) -> StructuralCommandResult:
        """Create a successful result.

        Args:
            message: Description of the successful operation.

        Returns:
            StructuralCommandResult with ok=True.
        """
        return cls(ok=True, message=message)

    @classmethod
    def failure(cls, message: str) -> StructuralCommandResult:
        """Create a failed result.

        Args:
            message: Description of the failure.

        Returns:
            StructuralCommandResult with ok=False.
        """
        return cls(ok=False, message=message)

    @property
    def is_success(self) -> bool:
        """Return True if the command succeeded."""
        return self.ok

    @property
    def is_failure(self) -> bool:
        """Return True if the command failed."""
        return not self.ok


# ============================================================================
# Operator Bridge Protocol
# ============================================================================

@runtime_checkable
class StructuralOperatorBridge(Protocol):
    """Protocol defining the structural operator bridge interface.

    This protocol defines the contract between the dashboard HTTP handlers
    and the structural plasticity operator bridge implementation. All methods
    are synchronous and return either JSON-serializable data or
    StructuralCommandResult objects.

    The bridge provides:
    1. Status queries (current state of the structural plasticity system)
    2. Proposal management (listing, approving, rejecting)
    3. History access (past structural changes)
    4. Heatmap generation (visualization data)
    5. Configuration access (current settings)
    6. Runtime control (ticks, steps, snapshots)

    All methods should handle errors gracefully and return meaningful
    error messages in the command results.
    """

    # -------------------------------------------------------------------------
    # Status Queries
    # -------------------------------------------------------------------------

    def structural_status(self) -> JSONMapping:
        """Get the current status of the structural plasticity system.

        Returns:
            A dictionary containing:
            - configured: bool - whether the system is configured
            - proposal_tick: int | None - last tick when proposals were generated
            - proposal_count: int - number of pending proposals
            - decision_count: int - total decisions made
            - history_count: int - total history records

        Raises:
            RuntimeError: If the bridge is not properly initialized.
        """
        ...

    def structural_proposals(self) -> list[JSONMapping]:
        """Get all pending structural plasticity proposals.

        Returns:
            A list of proposal dictionaries, each containing:
            - proposal_id: str - unique identifier
            - kind: str - type of proposal (e.g., 'neuron_add', 'synapse_prune')
            - neuron_id: int | None - affected neuron
            - target_id: int | None - target neuron for synapses
            - reason: str - why the proposal was generated
            - confidence: float - confidence score (0-1)

        Raises:
            RuntimeError: If the bridge is not properly initialized.
        """
        ...

    def structural_history(self, limit: int) -> list[JSONMapping]:
        """Get the history of structural plasticity changes.

        Args:
            limit: Maximum number of records to return. Should be positive.

        Returns:
            A list of history record dictionaries, each containing:
            - sequence: int - sequence number
            - tick: int - simulation tick when the change occurred
            - kind: str - type of change
            - proposal_id: str - ID of the proposal that caused the change
            - neuron_id: int | None - affected neuron
            - source_id: int | None - source neuron (for synapses)
            - target_id: int | None - target neuron (for synapses)
            - reason: str - reason for the change
            - approved_by: str - who approved the change
            - automatic: bool - whether the change was automatic
            - undo_of_sequence: int | None - sequence number if this is an undo

        Raises:
            ValueError: If limit is negative or zero.
            RuntimeError: If the bridge is not properly initialized.
        """
        ...

    def structural_heatmap(self, kind: str) -> JSONMapping:
        """Generate a structural plasticity heatmap.

        Args:
            kind: The type of heatmap to generate.
                Valid values: 'neuron_additions', 'neuron_removals',
                'synapse_additions', 'synapse_removals',
                'total_structural_activity'.

        Returns:
            A dictionary containing:
            - kind: str - the heatmap kind
            - values: list[list[float]] - 2D array of heatmap values
            - min_value: float - minimum value in the heatmap
            - max_value: float - maximum value in the heatmap
            - populated_cells: int - number of non-zero cells
            - sequence_from: int - starting sequence number
            - sequence_to: int - ending sequence number

        Raises:
            ValueError: If the heatmap kind is unknown.
            RuntimeError: If the bridge is not properly initialized.
        """
        ...

    def structural_config(self) -> JSONMapping:
        """Get the current structural plasticity configuration.

        Returns:
            A dictionary containing:
            - configured: bool - whether the system is configured
            - enabled: bool - whether structural plasticity is enabled
            - dry_run: bool - whether changes are applied (dry run mode)
            - auto_approval: bool - whether proposals are auto-approved
            - auto_approval_threshold: float - confidence threshold for auto-approval
            - max_changes_per_tick: int - maximum changes per tick
            - max_neuron_additions_per_tick: int - max neuron additions per tick
            - max_neuron_removals_per_tick: int - max neuron removals per tick
            - max_synapse_additions_per_tick: int - max synapse additions per tick
            - max_synapse_removals_per_tick: int - max synapse removals per tick
            - min_neurons: int - minimum neuron count
            - max_neurons: int - maximum neuron count
            - allow_neuron_pruning: bool - whether neurons can be pruned
            - allow_synapse_pruning: bool - whether synapses can be pruned
            - cooldown_ticks: int - cooldown period between changes

        Raises:
            RuntimeError: If the bridge is not properly initialized.
        """
        ...

    # -------------------------------------------------------------------------
    # Proposal Management
    # -------------------------------------------------------------------------

    def approve_structural(self, proposal_id: str) -> StructuralCommandResult:
        """Approve a structural plasticity proposal.

        This method records the approval decision and applies the proposed
        change to the network.

        Args:
            proposal_id: ID of the proposal to approve.

        Returns:
            StructuralCommandResult with success status and message.

        Raises:
            ValueError: If proposal_id is empty or invalid.
            RuntimeError: If the bridge is not properly initialized.
        """
        ...

    def reject_structural(self, proposal_id: str) -> StructuralCommandResult:
        """Reject a structural plasticity proposal.

        This method records the rejection decision without applying any changes.

        Args:
            proposal_id: ID of the proposal to reject.

        Returns:
            StructuralCommandResult with success status and message.

        Raises:
            ValueError: If proposal_id is empty or invalid.
            RuntimeError: If the bridge is not properly initialized.
        """
        ...

    def undo_structural(self) -> StructuralCommandResult:
        """Undo the last structural plasticity change.

        This method reverts the most recent structural change that was applied.

        Returns:
            StructuralCommandResult with success status and message.
            The message indicates whether a change was undone or if there
            was nothing to undo.

        Raises:
            RuntimeError: If the bridge is not properly initialized.
        """
        ...

    # -------------------------------------------------------------------------
    # Configuration Management
    # -------------------------------------------------------------------------

    def set_auto_approval(self, enabled: bool) -> StructuralCommandResult:
        """Enable or disable automatic approval of proposals.

        When auto-approval is enabled, proposals that meet the confidence
        threshold are automatically approved without user intervention.

        Args:
            enabled: Whether to enable auto-approval.

        Returns:
            StructuralCommandResult with success status and message.

        Raises:
            RuntimeError: If the bridge is not properly initialized.
        """
        ...

    # -------------------------------------------------------------------------
    # Runtime Control
    # -------------------------------------------------------------------------

    def run_ticks(self, count: int) -> StructuralCommandResult:
        """Run a specified number of simulation ticks.

        Args:
            count: Number of ticks to execute. Must be positive.

        Returns:
            StructuralCommandResult with success status and message.

        Raises:
            ValueError: If count is negative or zero.
            RuntimeError: If the bridge is not properly initialized.
        """
        ...

    def single_step(self) -> StructuralCommandResult:
        """Execute a single simulation tick.

        This is a convenience method that runs exactly one tick.

        Returns:
            StructuralCommandResult with success status and message.

        Raises:
            RuntimeError: If the bridge is not properly initialized.
        """
        ...

    def request_snapshot(self) -> StructuralCommandResult:
        """Request a snapshot of the current system state.

        This triggers the creation of a persistent snapshot that can be
        used for later analysis or visualization.

        Returns:
            StructuralCommandResult with success status and message.

        Raises:
            RuntimeError: If the bridge is not properly initialized.
        """
        ...


# ============================================================================
# Utility Functions
# ============================================================================

def is_command_success(result: StructuralCommandResult) -> bool:
    """Check if a StructuralCommandResult indicates success.

    Args:
        result: The command result to check.

    Returns:
        True if the command succeeded, False otherwise.
    """
    return result.ok


def is_command_failure(result: StructuralCommandResult) -> bool:
    """Check if a StructuralCommandResult indicates failure.

    Args:
        result: The command result to check.

    Returns:
        True if the command failed, False otherwise.
    """
    return not result.ok


def command_result_to_json(result: StructuralCommandResult) -> JSONMapping:
    """Convert a StructuralCommandResult to a JSON-serializable dictionary.

    Args:
        result: The command result to convert.

    Returns:
        A dictionary with 'ok' and 'message' keys.
    """
    return {"ok": result.ok, "message": result.message}


# ============================================================================
# Error Codes
# ============================================================================

class StructuralErrorCode:
    """Common error codes for structural operator operations.

    These can be used to provide more structured error information
    in command results.
    """

    SUCCESS = "success"
    NOT_FOUND = "not_found"
    CONFIGURATION_ERROR = "configuration_error"
    ENGINE_NOT_READY = "engine_not_ready"
    INVALID_PROPOSAL = "invalid_proposal"
    INVALID_KIND = "invalid_kind"
    LIMIT_EXCEEDED = "limit_exceeded"
    UNDO_FAILED = "undo_failed"
    TICK_FAILED = "tick_failed"
    SNAPSHOT_FAILED = "snapshot_failed"
    AUTO_APPROVAL_ERROR = "auto_approval_error"


# ============================================================================
# Extended Command Result
# ============================================================================

@dataclass(frozen=True, slots=True)
class ExtendedStructuralCommandResult:
    """Extended command result with additional metadata.

    This extends the basic StructuralCommandResult with optional
    error codes, details, and timestamps. It can be used for
    more detailed error reporting and debugging.

    Attributes:
        ok: True if the command succeeded, False otherwise.
        message: A human-readable message describing the result.
        code: Optional error code for categorized error handling.
        details: Optional additional structured data.
        timestamp: Optional ISO format timestamp of the result.
    """

    ok: bool
    message: str
    code: str | None = None
    details: dict[str, JSONValue] | None = None
    timestamp: str | None = None

    def to_json(self) -> JSONMapping:
        """Convert to a JSON-serializable dictionary."""
        result: JSONMapping = {"ok": self.ok, "message": self.message}
        if self.code is not None:
            result["code"] = self.code
        if self.details is not None:
            result["details"] = self.details
        if self.timestamp is not None:
            result["timestamp"] = self.timestamp
        return result

    @classmethod
    def success(
        cls,
        message: str,
        code: str = StructuralErrorCode.SUCCESS,
        details: dict[str, JSONValue] | None = None,
    ) -> ExtendedStructuralCommandResult:
        """Create a successful extended result."""
        return cls(
            ok=True,
            message=message,
            code=code,
            details=details,
            timestamp=datetime.now().isoformat(),
        )

    @classmethod
    def failure(
        cls,
        message: str,
        code: str = StructuralErrorCode.CONFIGURATION_ERROR,
        details: dict[str, JSONValue] | None = None,
    ) -> ExtendedStructuralCommandResult:
        """Create a failed extended result."""
        return cls(
            ok=False,
            message=message,
            code=code,
            details=details,
            timestamp=datetime.now().isoformat(),
        )

    def to_basic(self) -> StructuralCommandResult:
        """Convert to a basic StructuralCommandResult."""
        return StructuralCommandResult(ok=self.ok, message=self.message)


# ============================================================================
# Protocol Implementation Helper
# ============================================================================

# ... (restliche Datei bleibt unverändert) ...

def validate_bridge(bridge: StructuralOperatorBridge | None) -> StructuralOperatorBridge:
    """Validate that a bridge is properly configured.

    Args:
        bridge: The bridge instance to validate.

    Returns:
        The validated bridge instance.

    Raises:
        TypeError: If bridge is not a StructuralOperatorBridge.
        RuntimeError: If bridge is None.
    """
    if bridge is None:
        raise RuntimeError("Structural operator bridge is not configured")
    # The type annotation guarantees bridge is a StructuralOperatorBridge when not None.
    # No runtime isinstance check needed.
    return bridge