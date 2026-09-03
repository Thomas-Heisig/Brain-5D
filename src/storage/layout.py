"""Canonical filesystem layout for operator, experiment, and dev artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


def validate_scope_transition(source: str, target: str, operation: str) -> None:
    """Reject storage transitions that could merge uncontrolled state."""
    if source.upper() == "DEV" and target.upper() == "OPERATOR":
        raise ValueError("DEV to OPERATOR transitions are forbidden")
    if source.upper() == "EXPERIMENT" and target.upper() == "OPERATOR" and operation.lower() == "merge":
        raise ValueError("EXPERIMENT to OPERATOR merge is forbidden")
    if source.upper() == "OPERATOR" and target.upper() == "EXPERIMENT" and operation.lower() not in {"snapshot", "fork"}:
        raise ValueError("OPERATOR to EXPERIMENT requires snapshot or fork")
    if source.upper() not in {"DEV", "EXPERIMENT", "OPERATOR"} or target.upper() not in {"DEV", "EXPERIMENT", "OPERATOR"}:
        raise ValueError(f"Unknown storage scope transition: {source} -> {target}")


@dataclass(frozen=True, slots=True)
class StorageLayout:
    """Resolve controlled storage roots without crossing the workspace root."""

    root: Path

    def __post_init__(self) -> None:
        object.__setattr__(self, "root", self.root.resolve())

    @property
    def operator_state(self) -> Path:
        return self.root / "operator" / "state.b5d"

    @property
    def operator_journal(self) -> Path:
        return self.root / "operator" / "journal"

    @property
    def operator_action_journal(self) -> Path:
        """Durable hash-linked action audit path within operator storage."""
        return self.operator_journal / "actions.jsonl"

    @property
    def operator_checkpoints(self) -> Path:
        return self.root / "operator" / "checkpoints"

    @property
    def dev_disposable(self) -> Path:
        return self.root / "dev" / "disposable"

    def experiment(self, experiment_id: str) -> Path:
        if not experiment_id.startswith("EXP-") or "/" in experiment_id or "\\" in experiment_id:
            raise ValueError("Experiment ID must be a safe EXP-* name")
        candidate = self.root / "experiment" / experiment_id
        try:
            candidate.resolve().relative_to(self.root)
        except ValueError as exc:
            raise ValueError("Experiment path escapes storage root") from exc
        return candidate

    def experiment_state(self, experiment_id: str) -> Path:
        return self.experiment(experiment_id) / "state"

    def experiment_data(self, experiment_id: str) -> Path:
        return self.experiment(experiment_id) / "DATA"

    def experiment_evidence(self, experiment_id: str) -> Path:
        return self.experiment(experiment_id) / "EVID"

    def ensure_directories(self) -> None:
        """Create only controlled roots, never experiment data."""
        for directory in (
            self.operator_journal,
            self.operator_checkpoints,
            self.dev_disposable,
        ):
            directory.mkdir(parents=True, exist_ok=True)
