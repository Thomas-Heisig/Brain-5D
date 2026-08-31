"""
Experiment Recorder — Captures experiment manifests during Brain-5D runs.

Every scientifically relevant run produces a manifest.json with full metadata
for reproducibility: git state, software versions, simulation parameters,
and links to research questions / hypotheses.
"""

from __future__ import annotations

import json
import platform
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, cast

from .registry import REPO_ROOT

EXPERIMENTS_DIR = REPO_ROOT / "research" / "experiments"


def get_git_info() -> dict[str, Any]:
    """Capture current git commit hash and dirty state."""
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=REPO_ROOT
        ).stdout.strip()
        dirty = (
            subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
            ).stdout.strip()
            != ""
        )
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        ).stdout.strip()
        return {"commit": commit, "dirty": dirty, "branch": branch}
    except Exception:
        return {"commit": "unknown", "dirty": True, "branch": "unknown"}


def get_software_info() -> dict[str, Any]:
    """Capture Python and OS version info."""
    info = {
        "python": platform.python_version(),
        "os": f"{platform.system()} {platform.release()}",
    }
    try:
        import brain5d  # type: ignore[import-not-found]

        info["brain5d_version"] = getattr(brain5d, "__version__", "unknown")
    except ImportError:
        info["brain5d_version"] = "unknown"
    return info


def get_hardware_info() -> dict[str, Any]:
    """Basic hardware information."""
    info: dict[str, Any] = {"cpu": platform.processor() or "unknown"}
    try:
        import psutil  # type: ignore[import-untyped]

        info["ram_gb"] = round(psutil.virtual_memory().total / (1024**3), 1)
    except ImportError:
        pass
    return info


class ExperimentRecorder:
    """Records experiment manifests for scientific reproducibility.

    The recorder enforces experiment validity semantics:

    - ``experiment_status`` tracks the lifecycle: template -> not_started ->
      running -> completed | failed | invalid
    - ``validity`` captures whether the run is scientifically usable
    - ``runtime_errors`` captures structured RuntimeErrorEvents that
      occurred during execution
    - ``fail_fast`` mode stops the experiment on first runtime error

    Validity distinction (Phase 1):
        completed + negative result = VALID scientific result
        failed = execution failure (e.g. crash)
        invalid = scientifically unusable (runtime errors during execution)

    The EvidenceEngine MUST reject template, not_started, running, failed,
    and invalid experiments as scientific evidence.
    """

    def __init__(
        self,
        experiment_id: str,
        output_dir: Path | None = None,
        fail_fast: bool = False,
    ):
        self.experiment_id = experiment_id
        self.output_dir = output_dir or (EXPERIMENTS_DIR / experiment_id)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.fail_fast = fail_fast
        self._runtime_errors: list[dict[str, Any]] = []
        self._manifest: dict[str, Any] = {
            "experiment_id": experiment_id,
            "experiment_status": "not_started",
            "timestamp": datetime.now().isoformat(),
            "git": get_git_info(),
            "software": get_software_info(),
            "simulation": {},
            "artifacts": {},
            "research_questions": [],
            "hypotheses": [],
            "config": {},
            "validity": {
                "valid": True,
                "reason": None,
                "runtime_error_count": 0,
                "fatal_error_count": 0,
            },
            "runtime_errors": [],
        }

    def record_config(self, config_path: str, sha256: str = "") -> ExperimentRecorder:
        """Record the configuration file path and its SHA-256 hash."""
        self._manifest["config"] = {"path": config_path, "sha256": sha256}
        return self

    def record_software_version(self, key: str, value: str) -> ExperimentRecorder:
        """Record or override a software version entry (e.g. brain5d_version)."""
        self._manifest["software"][key] = value
        return self

    def record_simulation_params(
        self: ExperimentRecorder, **kwargs: Any
    ) -> ExperimentRecorder:
        """Record simulation parameters (seed, ticks, dimensions, etc.)."""
        self._manifest["simulation"].update(kwargs)
        return self

    def record_research_links(
        self,
        research_questions: list[str] | None = None,
        hypotheses: list[str] | None = None,
    ) -> ExperimentRecorder:
        """Link this experiment to research questions and hypotheses."""
        if research_questions:
            self._manifest["research_questions"] = research_questions
        if hypotheses:
            self._manifest["hypotheses"] = hypotheses
        return self

    def record_artifact(self, key: str, path: str) -> ExperimentRecorder:
        """Record a produced artifact path."""
        self._manifest["artifacts"][key] = str(path)
        return self

    def record_results(self: ExperimentRecorder, **kwargs: Any) -> ExperimentRecorder:
        """Record result metrics."""
        self._manifest.setdefault("results", {}).update(kwargs)
        return self

    def record_runtime(
        self, duration_seconds: float, ram_peak_mb: float | None = None
    ) -> ExperimentRecorder:
        """Record runtime information."""
        self._manifest["runtime"] = {"duration_seconds": duration_seconds}
        if ram_peak_mb is not None:
            self._manifest["runtime"]["ram_peak_mb"] = ram_peak_mb
        return self

    def record_runtime_error(
        self,
        tick: int,
        phase: str,
        exception_type: str,
        message: str,
        fatal: bool = False,
        traceback_hash: str = "",
    ) -> ExperimentRecorder:
        """Record a runtime error event in the experiment manifest.

        When ``fail_fast`` is True, the first error automatically sets
        the experiment status to ``invalid`` and marks the run as
        scientifically unusable.

        Args:
            tick: The simulation tick when the error occurred.
            phase: The phase where the error occurred (e.g. "step", "hook").
            exception_type: The type name of the exception.
            message: The exception message.
            fatal: Whether this error is fatal to the experiment.
            traceback_hash: Optional hash of the traceback for deduplication.

        Returns:
            Self for chaining.
        """
        error_entry: dict[str, Any] = {
            "tick": tick,
            "phase": phase,
            "exception_type": exception_type,
            "message": message,
            "fatal": fatal,
            "traceback_hash": traceback_hash,
        }
        self._runtime_errors.append(error_entry)
        self._manifest["runtime_errors"] = list(self._runtime_errors)

        # Update validity
        error_count = len(self._runtime_errors)
        fatal_count = sum(1 for e in self._runtime_errors if e.get("fatal"))
        self._manifest["validity"] = {
            "valid": False,
            "reason": f"{error_count} runtime error(s), {fatal_count} fatal",
            "runtime_error_count": error_count,
            "fatal_error_count": fatal_count,
        }

        # Fail-fast: mark experiment as invalid
        if self.fail_fast:
            self._manifest["experiment_status"] = "invalid"

        return self

    def mark_completed(self) -> ExperimentRecorder:
        """Mark the experiment as completed if no fatal errors occurred.

        If runtime errors exist, the experiment is marked ``invalid``
        instead of ``completed``. This enforces the distinction between
        a failed hypothesis (valid science) and a failed execution
        (invalid science).
        """
        if self._runtime_errors:
            self._manifest["experiment_status"] = "invalid"
        elif self._manifest.get("experiment_status") not in ("invalid", "failed"):
            self._manifest["experiment_status"] = "completed"
        return self

    def mark_failed(self) -> ExperimentRecorder:
        """Mark the experiment as failed (execution failure, not invalid)."""
        self._manifest["experiment_status"] = "failed"
        return self

    def save(self) -> Path:
        """Write the manifest to disk as JSON."""
        manifest_path = self.output_dir / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(self._manifest, f, indent=2, ensure_ascii=False)
        return manifest_path

    @property
    def manifest(self) -> dict[str, Any]:
        return self._manifest

    @staticmethod
    def load(experiment_id: str) -> dict[str, Any] | None:
        """Load an existing experiment manifest."""
        path = EXPERIMENTS_DIR / experiment_id / "manifest.json"
        if not path.exists():
            return None
        with open(path, encoding="utf-8") as f:
            data: Any = json.load(f)
            return cast("dict[str, Any]", data) if isinstance(data, dict) else None
