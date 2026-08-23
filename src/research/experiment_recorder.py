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
from typing import Any, Dict, List, Optional

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
    info = {"cpu": platform.processor() or "unknown"}
    try:
        import psutil  # type: ignore[import-untyped]

        info["ram_gb"] = round(psutil.virtual_memory().total / (1024**3), 1)
    except ImportError:
        pass
    return info


class ExperimentRecorder:
    """Records experiment manifests for scientific reproducibility."""

    def __init__(self, experiment_id: str, output_dir: Optional[Path] = None):
        self.experiment_id = experiment_id
        self.output_dir = output_dir or (EXPERIMENTS_DIR / experiment_id)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._manifest: Dict[str, Any] = {
            "experiment_id": experiment_id,
            "timestamp": datetime.now().isoformat(),
            "git": get_git_info(),
            "software": get_software_info(),
            "simulation": {},
            "artifacts": {},
            "research_questions": [],
            "hypotheses": [],
        }

    def record_simulation_params(self: ExperimentRecorder, **kwargs: Any) -> ExperimentRecorder:
        """Record simulation parameters (seed, ticks, dimensions, etc.)."""
        self._manifest["simulation"].update(kwargs)
        return self

    def record_research_links(
        self,
        research_questions: Optional[List[str]] = None,
        hypotheses: Optional[List[str]] = None,
    ) -> "ExperimentRecorder":
        """Link this experiment to research questions and hypotheses."""
        if research_questions:
            self._manifest["research_questions"] = research_questions
        if hypotheses:
            self._manifest["hypotheses"] = hypotheses
        return self

    def record_artifact(self, key: str, path: str) -> "ExperimentRecorder":
        """Record a produced artifact path."""
        self._manifest["artifacts"][key] = str(path)
        return self

    def record_results(self: ExperimentRecorder, **kwargs: Any) -> ExperimentRecorder:
        """Record result metrics."""
        self._manifest.setdefault("results", {}).update(kwargs)
        return self

    def record_runtime(
        self, duration_seconds: float, ram_peak_mb: Optional[float] = None
    ) -> "ExperimentRecorder":
        """Record runtime information."""
        self._manifest["runtime"] = {"duration_seconds": duration_seconds}
        if ram_peak_mb is not None:
            self._manifest["runtime"]["ram_peak_mb"] = ram_peak_mb
        return self

    def save(self) -> Path:
        """Write the manifest to disk as JSON."""
        manifest_path = self.output_dir / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(self._manifest, f, indent=2, ensure_ascii=False)
        return manifest_path

    @property
    @property
    def manifest(self) -> dict[str, Any]:
        return self._manifest

    @staticmethod
    def load(experiment_id: str) -> dict[str, Any] | None:
        """Load an existing experiment manifest."""
        path = EXPERIMENTS_DIR / experiment_id / "manifest.json"
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else None
