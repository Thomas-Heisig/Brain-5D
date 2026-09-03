"""Canonical filesystem layout for operator, experiment, and dev artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


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

    def ensure_directories(self) -> None:
        """Create only controlled roots, never experiment data."""
        for directory in (
            self.operator_journal,
            self.operator_checkpoints,
            self.dev_disposable,
        ):
            directory.mkdir(parents=True, exist_ok=True)
