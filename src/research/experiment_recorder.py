"""
Experiment Recorder — Captures experiment manifests during Brain-5D runs.

Every scientifically relevant run produces a manifest.json with full metadata
for reproducibility: git state, software versions, simulation parameters,
and links to research questions / hypotheses.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Protocol, cast

from src.research_assistant.contracts import (
    AIExposure,
    AIInteractionRecord,
    AIReproducibility,
    CausalTaint,
)
from src.research_assistant.governance import (
    ConfirmatoryRunLock,
    DataPartition,
    NetworkMode,
    ResearchRunMode,
    RetrievalRecord,
)

from .registry import REPO_ROOT

EXPERIMENTS_DIR = REPO_ROOT / "research" / "experiments"
CONTROL_GROUP_TEMPLATES = (
    "SNN_ONLY",
    "LANGUAGE_ORGAN",
    "KNOWLEDGE_INTAKE",
    "LANGUAGE_KNOWLEDGE",
    "LLM_ONLY",
    "FULL_SYSTEM",
)


def _digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class _VirtualMemoryLike(Protocol):
    total: int


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
        import psutil

        mem = cast(_VirtualMemoryLike, psutil.virtual_memory())
        info["ram_gb"] = round(mem.total / (1024**3), 1)
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
            "ai_exposure": AIExposure.NONE.value,
            "ai_reproducibility": AIReproducibility.R0.value,
            "ai_protocol": {"version": 1, "bump_reason": "initial registration"},
            "causal_taint": CausalTaint.PURE.value,
            "ai_interactions": [],
            "causal_card": {
                "classification": CausalTaint.PURE.value,
                "interaction_ids": [],
                "roles": [],
            },
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
            "research_run_mode": ResearchRunMode.EXPLORATORY.value,
            "data_partitions": [],
            "network_mode": NetworkMode.OFFLINE.value,
        }

    def record_config(self, config_path: str, sha256: str = "") -> ExperimentRecorder:
        """Record the configuration file path and its SHA-256 hash."""
        self._manifest["config"] = {"path": config_path, "sha256": sha256}
        return self

    def record_software_version(self, key: str, value: str) -> ExperimentRecorder:
        """Record or override a software version entry (e.g. brain5d_version)."""
        self._manifest["software"][key] = value
        return self

    def record_ai_protocol(self, version: int, bump_reason: str) -> ExperimentRecorder:
        """Register the version and reason for the AI protocol used by a run."""
        if version < 1:
            raise ValueError("AI protocol version must be positive")
        if not bump_reason.strip():
            raise ValueError("AI protocol bump_reason must not be empty")
        self._manifest["ai_protocol"] = {
            "version": version,
            "bump_reason": bump_reason.strip(),
        }
        return self

    def record_simulation_params(
        self: ExperimentRecorder, **kwargs: Any
    ) -> ExperimentRecorder:
        """Record simulation parameters (seed, ticks, dimensions, etc.)."""
        self._manifest["simulation"].update(kwargs)
        return self

    def record_ai_exposure(self, exposure: AIExposure | str) -> ExperimentRecorder:
        """Record the declared AI exposure level for this experiment."""
        try:
            normalized = AIExposure(exposure)
        except ValueError as exc:
            raise ValueError(f"Unsupported AI exposure: {exposure}") from exc
        self._manifest["ai_exposure"] = normalized.value
        return self

    def record_ai_reproducibility(
        self, level: AIReproducibility | str
    ) -> ExperimentRecorder:
        """Register the reproducibility level claimed for AI participation."""
        try:
            normalized = AIReproducibility(level)
        except ValueError as exc:
            raise ValueError(f"Unsupported AI reproducibility level: {level}") from exc
        self._manifest["ai_reproducibility"] = normalized.value
        return self

    def record_ai_interaction(
        self, interaction: AIInteractionRecord
    ) -> ExperimentRecorder:
        """Append one interaction and monotonically update the run's causal taint."""
        if interaction.experiment_id not in (None, self.experiment_id):
            raise ValueError(
                "AI interaction experiment_id does not match this recorder."
            )
        interactions = cast(list[dict[str, Any]], self._manifest["ai_interactions"])
        interactions.append(interaction.to_dict())
        card = cast(dict[str, Any], self._manifest["causal_card"])
        card["interaction_ids"].append(interaction.interaction_id)
        if interaction.role not in card["roles"]:
            card["roles"].append(interaction.role)
        taint_order = {
            CausalTaint.PURE: 0,
            CausalTaint.OBSERVED: 1,
            CausalTaint.PROPOSED: 2,
            CausalTaint.AI_INFLUENCED: 3,
        }
        current = CausalTaint(cast(str, self._manifest["causal_taint"]))
        if taint_order[interaction.causal_effect] > taint_order[current]:
            self._manifest["causal_taint"] = interaction.causal_effect.value
            card["classification"] = interaction.causal_effect.value
        return self

    def record_ai_treatment(
        self, protocol_id: str, *, registered: bool = True, mode: str = "confirmatory"
    ) -> ExperimentRecorder:
        """Register the treatment required to interpret AI-influenced runs."""
        if not protocol_id.strip():
            raise ValueError("AI treatment protocol_id must not be empty")
        if mode not in {"exploratory", "confirmatory"}:
            raise ValueError("AI treatment mode must be exploratory or confirmatory")
        self._manifest["ai_treatment"] = {
            "protocol_id": protocol_id,
            "registered": registered,
            "mode": mode,
        }
        return self

    def record_research_run_mode(self, mode: ResearchRunMode | str) -> ExperimentRecorder:
        """Declare exploratory or confirmatory protocol handling."""
        self._manifest["research_run_mode"] = ResearchRunMode(mode).value
        return self

    def record_network_mode(
        self, mode: NetworkMode | str, *, scientific_run: bool = True
    ) -> ExperimentRecorder:
        """Register network policy and reject live access for scientific runs."""
        normalized = NetworkMode(mode)
        if scientific_run and normalized is NetworkMode.LIVE_NETWORK:
            raise ValueError("Scientific runs require OFFLINE or FROZEN_CORPUS network mode")
        self._manifest["network_mode"] = normalized.value
        return self

    def record_data_partition(self, partition: DataPartition | str) -> ExperimentRecorder:
        """Record a data partition used by this run."""
        normalized = DataPartition(partition).value
        partitions = cast(list[str], self._manifest["data_partitions"])
        if normalized not in partitions:
            partitions.append(normalized)
        return self

    def record_retrieval(self, retrieval: RetrievalRecord) -> ExperimentRecorder:
        """Record explicit retrieval state so knowledge use is never implicit."""
        self._manifest["retrieval"] = retrieval.to_dict()
        return self

    def lock_confirmatory_run(
        self,
        *,
        protocol: dict[str, object],
        prompt_digest: str,
        analysis_digest: str,
    ) -> ExperimentRecorder:
        """Attach an immutable lock and switch this manifest to confirmatory mode."""
        lock = ConfirmatoryRunLock.create(
            protocol=protocol,
            prompt_digest=prompt_digest,
            analysis_digest=analysis_digest,
        )
        self._manifest["research_run_mode"] = ResearchRunMode.CONFIRMATORY.value
        self._manifest["confirmatory_lock"] = {
            "protocol_digest": lock.protocol_digest,
            "prompt_digest": lock.prompt_digest,
            "analysis_digest": lock.analysis_digest,
            "locked": lock.locked,
        }
        return self

    def record_twin_run(
        self,
        *,
        snapshot_digest: str,
        seed: int,
        inputs: object,
        reward: object,
        tick_plan: list[int],
        ai_off_experiment_id: str,
        ai_on_experiment_id: str,
    ) -> ExperimentRecorder:
        """Register matching AI-off/AI-on inputs without executing either run."""
        if not snapshot_digest.strip():
            raise ValueError("Twin-run snapshot_digest must not be empty")
        if not ai_off_experiment_id.strip() or not ai_on_experiment_id.strip():
            raise ValueError("Twin-run experiment IDs must not be empty")
        if ai_off_experiment_id == ai_on_experiment_id:
            raise ValueError("Twin-run experiment IDs must be distinct")
        if not tick_plan or any(tick < 0 for tick in tick_plan):
            raise ValueError("Twin-run tick_plan must contain non-negative ticks")
        self._manifest["twin_run"] = {
            "snapshot_digest": snapshot_digest,
            "seed": seed,
            "input_digest": _digest(inputs),
            "reward_digest": _digest(reward),
            "tick_plan_digest": _digest(tick_plan),
            "tick_count": len(tick_plan),
            "ai_off_experiment_id": ai_off_experiment_id,
            "ai_on_experiment_id": ai_on_experiment_id,
            "executed": False,
        }
        return self

    def record_twin_results(
        self, *, ai_off_result: object, ai_on_result: object
    ) -> ExperimentRecorder:
        """Attach digests from completed AI-off/AI-on runs to a twin manifest."""
        twin_run = self._manifest.get("twin_run")
        if not isinstance(twin_run, dict):
            raise ValueError("Twin-run inputs must be registered before results")
        twin_run["ai_off_result_digest"] = _digest(ai_off_result)
        twin_run["ai_on_result_digest"] = _digest(ai_on_result)
        twin_run["results_recorded"] = True
        twin_run["executed"] = True
        return self

    def execute_twin_run(
        self,
        runner: Callable[..., object],
        *,
        snapshot_digest: str,
        seed: int,
        inputs: object,
        reward: object,
        tick_plan: list[int],
        ai_off_experiment_id: str,
        ai_on_experiment_id: str,
    ) -> tuple[object, object]:
        """Run the same protocol once with AI disabled and once enabled."""
        self.record_twin_run(
            snapshot_digest=snapshot_digest,
            seed=seed,
            inputs=inputs,
            reward=reward,
            tick_plan=tick_plan,
            ai_off_experiment_id=ai_off_experiment_id,
            ai_on_experiment_id=ai_on_experiment_id,
        )
        common = {
            "seed": seed,
            "inputs": inputs,
            "reward": reward,
            "tick_plan": list(tick_plan),
        }
        ai_off_result = runner(ai_enabled=False, **common)
        ai_on_result = runner(ai_enabled=True, **common)
        self.record_twin_results(
            ai_off_result=ai_off_result, ai_on_result=ai_on_result
        )
        return ai_off_result, ai_on_result

    def record_control_group(self, control_group: str) -> ExperimentRecorder:
        """Register one predefined control-group condition for this experiment."""
        normalized = control_group.strip().upper()
        if normalized not in CONTROL_GROUP_TEMPLATES:
            allowed = ", ".join(CONTROL_GROUP_TEMPLATES)
            raise ValueError(f"Unsupported control group {control_group!r}; use: {allowed}")
        self._manifest["control_group"] = {
            "template": normalized,
            "registered": True,
            "executed": False,
        }
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
