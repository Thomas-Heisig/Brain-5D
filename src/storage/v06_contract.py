"""Frozen v0.6 persistence compatibility contract.

v0.6 intentionally retains the already frozen B5D snapshot V1 and delta
journal V1 formats.  Therefore the v0.6 migration for persisted network state
is an explicitly verified no-op: validation may inspect bytes but may not
rewrite them.  Future format changes must add a new migration path rather than
silently mutating this contract.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .b5d import B5DReader, FORMAT_VERSION
from .delta_journal import JOURNAL_VERSION


class V06CompatibilityError(ValueError):
    """Raised when persisted state is incompatible with the v0.6 contract."""


@dataclass(frozen=True, slots=True)
class V06PersistenceContract:
    schema_version: int = 1
    snapshot_format_version: int = FORMAT_VERSION
    journal_format_version: int = JOURNAL_VERSION
    snapshot_restart_capable_required: bool = True
    migration_policy: str = "NOOP_FROZEN_FORMAT"
    rollback_policy: str = "BYTE_IDENTITY"

    def to_json(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "snapshot_format_version": self.snapshot_format_version,
            "journal_format_version": self.journal_format_version,
            "snapshot_restart_capable_required": self.snapshot_restart_capable_required,
            "migration_policy": self.migration_policy,
            "rollback_policy": self.rollback_policy,
        }


V06_CONTRACT = V06PersistenceContract()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_v06_snapshot(path: Path) -> dict[str, Any]:
    """Validate a snapshot without changing bytes and return a compatibility receipt."""
    before = sha256_file(path)
    with B5DReader(path) as reader:
        header = reader.header
        if header.version != V06_CONTRACT.snapshot_format_version:
            raise V06CompatibilityError(
                f"snapshot version {header.version} != {V06_CONTRACT.snapshot_format_version}"
            )
        if V06_CONTRACT.snapshot_restart_capable_required and not header.restart_capable:
            raise V06CompatibilityError("v0.6 resumable snapshot must be restart-capable")
        tick = int(header.snapshot_tick)
        neurons = int(header.neuron_count)
        synapses = int(header.synapse_count)
    after = sha256_file(path)
    if before != after:
        raise V06CompatibilityError("compatibility validation modified snapshot bytes")
    return {
        "compatible": True,
        "migration": V06_CONTRACT.migration_policy,
        "rollback": V06_CONTRACT.rollback_policy,
        "sha256_before": before,
        "sha256_after": after,
        "snapshot_tick": tick,
        "neurons": neurons,
        "synapses": synapses,
    }


def migration_plan(snapshot_version: int, journal_version: int) -> str:
    """Return the only allowed migration plan for the frozen v0.6 formats."""
    if snapshot_version != V06_CONTRACT.snapshot_format_version:
        raise V06CompatibilityError(
            f"no implicit snapshot migration from version {snapshot_version}"
        )
    if journal_version != V06_CONTRACT.journal_format_version:
        raise V06CompatibilityError(
            f"no implicit journal migration from version {journal_version}"
        )
    return V06_CONTRACT.migration_policy
