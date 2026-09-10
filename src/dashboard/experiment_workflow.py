"""Controlled experiment execution and report publication for the dashboard."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from types import CodeType, ModuleType
from typing import Any, Callable, Protocol, Sequence, cast

from src.experiments.msba_lab import (
    MSBA_RUNNERS,
    persist_gateway_state_sidecar,
)
from src.profiles import ProfileService
from src.research.catalog_status import (
    CATALOG_FACET_FIELDS,
    question_facet_options,
    question_facets,
)
from src.research.cognition_governance import (
    CognitionGovernanceError,
    cognition_catalog,
    guard_cognition_launch,
)
from src.research.connectome_embodiment import (
    RUNNERS as CONNECTOME_RUNNERS,
)
from src.research.connectome_embodiment import (
    persist_boundary_state,
)
from src.research.connectome_governance import (
    ConnectomeGovernanceError,
    connectome_catalog,
    guard_connectome_launch,
)
from src.research.data_v2 import prepare_research_data_v2
from src.research.experiment_recorder import ExperimentRecorder
from src.research.experiment_summary import (
    write_detailed_experiment_summary,
    write_statistics_artifact,
)
from src.research.protocol_registry import (
    OPERATIONAL_RUNNERS,
    PreregistrationError,
    protocol_by_id,
    protocol_catalog,
    validate_operational_protocol,
)
from src.research.registry import ResearchRegistry
from src.research_assistant.airr import AIRRPipeline
from src.research_assistant.assistant import AnalysisBackend

from .models import JSONValue


class WorkflowValidationError(ValueError):
    """Raised when a workflow submission is not scientifically traceable."""


EPISTEMIC_LAYERS: dict[str, JSONValue] = {
    "ui_state": "operator/dashboard progress only; not a scientific result",
    "data": "DATA artifacts and deterministic statistics are authoritative run outputs",
    "evid": "not_created; requires semantic validation, clean freeze and human review",
    "interpretation": "post-hoc AI or human interpretation; never execution input",
}


class _ScientificRunLike(Protocol):
    """Typed read boundary used only for post-run execution validation."""

    seed: int
    condition: str
    metrics: dict[str, Any]


def write_experiment_summary(
    research_root: Path,
    experiment_id: str,
    ai_report: dict[str, object],
) -> str:
    """Write the canonical detailed, data-first experiment summary."""
    return write_detailed_experiment_summary(research_root, experiment_id, ai_report)


@dataclass(frozen=True, slots=True)
class ExperimentWorkflow:
    """Validated, reproducible input for one controlled experiment run."""

    experiment_id: str
    question_id: str
    hypothesis_id: str
    title: str
    conditions: str
    ticks: int
    notes: str
    protocol: str
    seeds: tuple[int, ...]


class ExperimentWorkflowService:
    """Run a fixed controller action and publish its research artifacts.

    The service deliberately accepts a controller callback, never commands or
    model-generated code. This keeps language-model assistance outside the
    causal path of the experiment.
    """

    def __init__(
        self,
        research_root: Path,
        ai_backend: AnalysisBackend | None = None,
    ) -> None:
        self._research_root = research_root
        self._ai_backend = ai_backend

    def catalog(self) -> dict[str, JSONValue]:
        """Return registry entries suitable for workflow selection."""
        registry = ResearchRegistry(self._research_root / "registry").load_all()
        questions = question_facets(self._research_root, registry)
        return {
            "questions": cast(JSONValue, questions),
            "facets": cast(JSONValue, question_facet_options(questions)),
            "facet_fields": cast(JSONValue, list(CATALOG_FACET_FIELDS)),
            "hypotheses": cast(
                JSONValue,
                [
                    {
                        "id": hypothesis.id,
                        "question_id": hypothesis.research_question,
                        "label": hypothesis.hypothesis,
                    }
                    for hypothesis in registry.hypotheses.values()
                ],
            ),
            "protocols": cast(
                JSONValue,
                [
                    {
                        "id": "science_suite_v1",
                        "label": "Science Suite v1 (RQ-gesteuerter Runner + DATA + Manifest)",
                    },
                    {
                        "id": "science_all_v1",
                        "label": "Science ALL v1 (alle Science-Suite-Protokolle)",
                    },
                    {
                        "id": "science_time_v1",
                        "label": "Science TIME v1 (DATA + Manifest)",
                    },
                    {"id": "science_5d_v1", "label": "Science 5D v1 (DATA + Manifest)"},
                    {
                        "id": "learning_operator_v1",
                        "label": "Operator Learning v1 (DATA + Manifest + Report)",
                    },
                    {
                        "id": "runtime_ticks_v1",
                        "label": "Runtime-Ticks (Laufprotokoll)",
                    },
                    {
                        "id": "stdp_pair_timing_v1",
                        "label": "STDP Pair-Timing v1 (registriert)",
                    },
                    *protocol_catalog(self._research_root),
                ],
            ),
            "connectome_protocols": cast(
                JSONValue, connectome_catalog(self._research_root)
            ),
            "cognition_protocols": cast(
                JSONValue, cognition_catalog(self._research_root)
            ),
            "next_experiment_id": self._next_experiment_id(),
        }

    def run_batch(
        self,
        body: dict[str, object],
        *,
        run_ticks: Callable[[int], object] | None = None,
        before: Callable[[], dict[str, int]] | None = None,
        after: Callable[[], dict[str, int]] | None = None,
    ) -> dict[str, object]:
        """Run selected registered protocols and publish one aggregate report."""
        protocol_ids_value = body.get("protocols")
        if not isinstance(protocol_ids_value, list) or not protocol_ids_value:
            raise WorkflowValidationError(
                "protocols must contain at least one protocol id"
            )
        selections = cast(list[object], protocol_ids_value)
        if not all(isinstance(item, str) and item for item in selections):
            raise WorkflowValidationError(
                "protocols must contain only non-empty strings"
            )
        protocol_ids = cast(list[str], selections)
        if not protocol_ids:
            raise WorkflowValidationError(
                "protocols must contain valid protocol selections"
            )
        catalog = {
            str(item["id"]): item
            for item in protocol_catalog(self._research_root)
            if isinstance(item.get("id"), str)
        }
        exploratory: dict[str, tuple[str, str]] = {}
        known_protocols: list[str] = []
        for protocol_id in protocol_ids:
            if protocol_id.startswith("exploratory:"):
                parts = protocol_id.split(":", 2)
                if len(parts) != 3 or not parts[1] or not parts[2]:
                    raise WorkflowValidationError(
                        f"Invalid exploratory selection: {protocol_id}"
                    )
                exploratory[protocol_id] = (parts[1], parts[2])
            else:
                known_protocols.append(protocol_id)
        unknown = [
            protocol_id for protocol_id in known_protocols if protocol_id not in catalog
        ]
        if unknown:
            raise WorkflowValidationError(
                f"Unknown operational protocols: {', '.join(unknown)}"
            )
        batch_id_value = body.get("batch_id")
        batch_id = (
            str(batch_id_value).strip() if isinstance(batch_id_value, str) else ""
        )
        if not batch_id:
            stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
            batch_id = f"EXP-BATCH-{stamp}"
        if not batch_id.startswith("EXP-"):
            raise WorkflowValidationError("batch_id must use the EXP-* convention")
        ticks = body.get("ticks", 1000)
        if not isinstance(ticks, int) or isinstance(ticks, bool) or ticks < 1:
            raise WorkflowValidationError("ticks must be a positive integer")
        seeds = body.get("seeds", "42-44")
        options_value = body.get("protocol_options", {})
        protocol_options = (
            cast(dict[str, object], options_value)
            if isinstance(options_value, dict)
            else {}
        )
        title_prefix = str(body.get("title_prefix") or "Experiment workflow").strip()
        conditions = str(
            body.get("conditions") or "Registered protocol conditions"
        ).strip()
        notes = str(body.get("notes") or "").strip()
        results: list[dict[str, object]] = []
        for index, protocol_id in enumerate(protocol_ids, start=1):
            option_value = protocol_options.get(protocol_id)
            option = (
                cast(dict[str, object], option_value)
                if isinstance(option_value, dict)
                else {}
            )
            child_ticks = option.get("ticks", ticks)
            child_seeds = option.get("seeds", seeds)
            if (
                not isinstance(child_ticks, int)
                or isinstance(child_ticks, bool)
                or child_ticks < 1
            ):
                raise WorkflowValidationError(f"Invalid ticks for {protocol_id}")
            if protocol_id in exploratory:
                question_id, hypothesis_id = exploratory[protocol_id]
                protocol = "runtime_ticks_v1"
                title = f"{title_prefix}: exploratory {question_id}"
            else:
                contract = catalog[protocol_id]
                question_id = str(contract["research_question"])
                hypothesis_id = str(contract["hypothesis"])
                protocol = protocol_id
                title = f"{title_prefix}: {protocol_id}"
            experiment_id = f"{batch_id}-{index:02d}"
            child: dict[str, object] = {
                "experiment_id": experiment_id,
                "question_id": question_id,
                "hypothesis_id": hypothesis_id,
                "title": title,
                "conditions": conditions,
                "ticks": child_ticks,
                "seeds": child_seeds,
                "notes": notes,
                "protocol": protocol,
                "exploratory": protocol_id in exploratory,
            }
            try:
                if protocol_id in exploratory:
                    if run_ticks is None or before is None or after is None:
                        raise WorkflowValidationError(
                            "Exploratory batch runs require an attached runtime controller."
                        )
                    result = self.run(child, run_ticks, before(), after)
                    summary = write_experiment_summary(
                        self._research_root,
                        experiment_id,
                        {
                            "status": "unavailable",
                            "reason": "Exploratory runtime run; AI post-hoc analysis not required.",
                            "scientific_evidence": False,
                        },
                    )
                    result["summary"] = summary
                    result["research_run_mode"] = "EXPLORATORY"
                    result["test_run"] = True
                else:
                    result = self.run_science(child)
                results.append(
                    {
                        "protocol": protocol_id,
                        "ticks": child_ticks,
                        "seeds": child_seeds,
                        "status": "completed",
                        **result,
                    }
                )
            except WorkflowValidationError as exc:
                message = str(exc)
                intentionally_blocked = message.startswith(
                    (
                        "COGNITION_ADAPTER_NOT_VALIDATED:",
                        "CONNECTOME_ADAPTER_NOT_VALIDATED:",
                    )
                )
                results.append(
                    {
                        "protocol": protocol_id,
                        "ticks": child_ticks,
                        "seeds": child_seeds,
                        "experiment_id": experiment_id,
                        "status": "blocked" if intentionally_blocked else "failed",
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )
            except Exception as exc:
                results.append(
                    {
                        "protocol": protocol_id,
                        "ticks": child_ticks,
                        "seeds": child_seeds,
                        "experiment_id": experiment_id,
                        "status": "failed",
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )
        workflow_root = self._research_root / "workflows"
        workflow_root.mkdir(parents=True, exist_ok=True)
        report_path = workflow_root / f"{batch_id}.json"
        completed = sum(item["status"] == "completed" for item in results)
        blocked = sum(item["status"] == "blocked" for item in results)
        failed = sum(item["status"] == "failed" for item in results)
        report = {
            "workflow_id": batch_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "protocols": protocol_ids,
            "requested_ticks": ticks,
            "seeds": seeds,
            "completed": completed,
            "blocked": blocked,
            "failed": failed,
            "results": results,
        }
        report_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=True, default=str) + "\n",
            encoding="utf-8",
        )
        markdown_path = report_path.with_suffix(".md")
        markdown_path.write_text(
            "\n".join(
                [
                    f"# {batch_id}: Experiment workflow",
                    "",
                    f"- Requested ticks: `{ticks}`",
                    f"- Seeds: `{seeds}`",
                    f"- Completed: `{completed}`",
                    f"- Blocked by design: `{blocked}`",
                    f"- Failed: `{failed}`",
                    "",
                    "## Protocol results",
                    *[
                        f"- `{item['protocol']}`: **{item['status']}**"
                        + (f" — {item['error']}" if item.get("error") else "")
                        for item in results
                    ],
                    "",
                    "The workflow report is an aggregate index; each completed protocol keeps its own manifest, raw data, statistics and report.",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        return {
            "workflow_id": batch_id,
            "report": f"workflows/{batch_id}.json",
            "report_markdown": f"workflows/{batch_id}.md",
            "completed": completed,
            "blocked": blocked,
            "failed": failed,
            "results": results,
        }

    def run_science(
        self, body: dict[str, object], *, seeds: tuple[int, ...] | None = None
    ) -> dict[str, object]:
        """Execute the RQ-compatible science runner and persist complete artifacts."""
        science_body = dict(body)
        science_body.setdefault("protocol", "science_suite_v1")
        workflow = self._validate(science_body)
        profile_subject: dict[str, Any] | None = None
        profile_service = ProfileService(self._research_root.parent / "profiles")
        profile_id_value = science_body.get("profile_id")
        if isinstance(profile_id_value, str) and profile_id_value.strip():
            profile = profile_service.get(profile_id_value.strip())
            binding = profile.get("snapshot_binding")
            profile_subject = {
                "profile_id": profile["profile_id"],
                "profile_revision": profile["revision"],
                "profile_digest": profile["provenance"]["profile_digest"],
                "snapshot_digest": (
                    cast(dict[str, Any], binding).get("digest")
                    if isinstance(binding, dict)
                    else None
                ),
            }
        runner_name = self._science_runner(science_body, workflow)
        effective_seeds = seeds if seeds is not None else workflow.seeds
        workflow = replace(workflow, seeds=effective_seeds)
        output_dir = self._research_root / "experiments" / workflow.experiment_id
        if (output_dir / "manifest.json").exists():
            raise WorkflowValidationError(
                f"Experiment '{workflow.experiment_id}' already exists."
            )

        from src.research import experiment_suite

        config_path = (
            self._research_root.parent / "configs" / "learning_experiment.yaml"
        )
        if not config_path.exists():
            config_path = Path("configs/learning_experiment.yaml")
        config_path = config_path.resolve()
        config = _load_yaml(config_path)
        config_digest = _sha256_file(config_path)
        started = perf_counter()
        if hasattr(experiment_suite, runner_name):
            runner_module: ModuleType = experiment_suite
        else:
            from src.research import followup_experiments

            runner_module = followup_experiments
        runner = getattr(runner_module, runner_name)
        runner_source_value = getattr(runner_module, "__file__", None)
        if not isinstance(runner_source_value, str):
            raise WorkflowValidationError(
                f"Cannot resolve source path for runner module {runner_module.__name__}."
            )
        runner_source = runner_source_value
        runtime_runner_digest, source_runner_digest = (
            _assert_loaded_callable_matches_source(
                runner, Path(runner_source).resolve(), runner_name
            )
        )
        summary_runtime_digest, summary_source_digest = (
            _assert_loaded_callable_matches_source(
                write_detailed_experiment_summary,
                Path(write_detailed_experiment_summary.__code__.co_filename).resolve(),
                "write_detailed_experiment_summary",
            )
        )
        connectome_sources: dict[str, object] = {}
        if runner_name in CONNECTOME_RUNNERS.values():
            from src.embodiment import joint_world
            from src.research import connectome_embodiment, connectome_reference

            specifications = (
                (connectome_embodiment, ("_network", "_simulate", "run_protocol")),
                (connectome_reference, ("synthetic_graph", "transform_graph")),
                (joint_world, ()),
            )
            for module, names in specifications:
                source_path = Path(str(module.__file__)).resolve()
                matches = {
                    name: _assert_loaded_callable_matches_source(
                        getattr(module, name), source_path, name
                    )
                    for name in names
                }
                if module is joint_world:
                    matches["advance"] = _assert_loaded_callable_matches_source(
                        joint_world.JointWorld.advance, source_path, "advance"
                    )
                connectome_sources[str(source_path)] = {
                    "sha256": _sha256_file(source_path),
                    "callables": matches,
                }
        tick_aware_runners = {
            "run_embodied_closed_loop",
            "run_embodied_proprioception",
            "run_embodied_perturbation",
            "run_connectome_topology",
            "run_embodied_controller",
            "run_embodied_timing",
            "run_all",
            "run_ping",
            "run_ping_v2",
            "run_5d",
            "run_time",
            "run_temporal",
            "run_recurrence_map",
            "run_replication",
            "run_5d_matched",
            "run_regulation_recovery",
            "run_temporal_order",
            "run_performance_profile",
            "run_recurrence_scale",
            "run_sustained_stability",
        }
        if runner_name in tick_aware_runners:
            runs = runner(config, seeds=effective_seeds, ticks=workflow.ticks)
        else:
            runs = runner(config, seeds=effective_seeds)
        for path, observation in connectome_sources.items():
            if (
                _sha256_file(Path(path))
                != cast(dict[str, object], observation)["sha256"]
            ):
                raise WorkflowValidationError(
                    "Connectome source changed during execution"
                )
        runs = [replace(run, experiment_id=workflow.experiment_id) for run in runs]
        duration = perf_counter() - started

        tick_validation: dict[str, object]
        try:
            tick_validation = self._validate_tick_execution(
                runner_name,
                workflow.ticks,
                effective_seeds,
                cast(Sequence[_ScientificRunLike], runs),
            )
        except WorkflowValidationError as exc:
            if runner_name not in CONNECTOME_RUNNERS.values():
                raise
            # Preserve incomplete native trajectories as failed observations.
            # They must not disappear simply because the tick gate failed.
            tick_validation = {
                "status": "VIOLATED",
                "requested_ticks": workflow.ticks,
                "reason": str(exc),
                "retained_failed_observations": True,
            }
        recorder = ExperimentRecorder(workflow.experiment_id, output_dir=output_dir)
        if profile_subject is not None:
            recorder.manifest["subject"] = profile_subject
        data_path = output_dir / "DATA" / "runs.json"
        data_path.parent.mkdir(parents=True, exist_ok=True)
        serialized_runs = [asdict(run) for run in runs]
        gateway_state_path: Path | None = None
        if runner_name in MSBA_RUNNERS:
            gateway_state_path = persist_gateway_state_sidecar(
                output_dir, serialized_runs
            )
        if runner_name in CONNECTOME_RUNNERS.values():
            contract = protocol_by_id(self._research_root, workflow.protocol)
            if contract is None:
                raise WorkflowValidationError("Missing connectome execution contract")
            expected_hash = _sha256_file(
                self._research_root / contract["preregistration"]
            )
            if any(
                run.metrics.get("preregistration_sha256") != expected_hash
                for run in runs
            ):
                raise WorkflowValidationError(
                    "Runner/workflow preregistration bytes differ"
                )
            gateway_state_path = persist_boundary_state(output_dir, serialized_runs)
        # Compute statistics from the complete in-memory observations first. Large
        # per-tick traces are then moved to compressed sidecars so runs.json remains
        # reviewable without discarding raw observations.
        statistics_path = write_statistics_artifact(output_dir, serialized_runs)
        statistics_payload = json.loads(statistics_path.read_text(encoding="utf-8"))
        data_v2 = prepare_research_data_v2(
            output_dir, serialized_runs, statistics_payload
        )
        trace_paths = list(data_v2.raw_paths)
        data_path.write_text(
            json.dumps(serialized_runs, indent=2, sort_keys=True, default=list) + "\n",
            encoding="utf-8",
        )

        recorder.record_research_links([workflow.question_id], [workflow.hypothesis_id])
        operational_protocol = protocol_by_id(self._research_root, workflow.protocol)
        if operational_protocol is not None:
            preregistration = validate_operational_protocol(
                self._research_root,
                question_id=workflow.question_id,
                hypothesis_id=workflow.hypothesis_id,
                protocol_id=workflow.protocol,
                seed_count=len(effective_seeds),
            )
            recorder.record_research_run_mode(
                str(preregistration.get("mode", "EXPLORATORY")).upper()
            )
            execution_kind = operational_protocol.get("execution_kind")
            if execution_kind in {"conceptual_audit", "functional_experiment"}:
                recorder.manifest["execution_semantics"] = {
                    "kind": execution_kind,
                    "snn_involved": False,
                    "human_assessment": "not_recorded",
                    "claim_scope": (
                        "method_template_only"
                        if execution_kind == "conceptual_audit"
                        else "component_engineering_screen_not_snn_learning"
                    ),
                    "external_review": "external_review/INTEGRATION.md",
                }

        recorder.record_config(str(config_path), config_digest)
        recorder.record_simulation_params(
            seed=effective_seeds[0],
            ticks=workflow.ticks,
            seeds=list(effective_seeds),
            protocol=workflow.protocol,
        )
        recorder.record_artifact("data", "DATA/runs.json")
        if gateway_state_path is not None:
            recorder.record_artifact("gateway_state", "DATA/gateway_state.json")
        recorder.record_artifact("data_index", "DATA/runs_index.json")
        recorder.record_artifact("ai_packet", "analysis/ai_packet.json")
        recorder.record_artifact("ai_packet_digest", "analysis/ai_packet_digest.json")
        recorder.record_artifact("statistics", "analysis/statistics.json")
        recorder.record_artifact("workflow", "workflow.json")
        recorder.record_artifact("report", "report.md")
        recorder.record_results(
            run_count=len(runs),
            protocol=workflow.protocol,
            runner=runner_name,
            ticks_requested=workflow.ticks,
            tick_contract=tick_validation,
        )

        report_path = output_dir / "report.md"
        report_path.write_text(
            self._render_science_report(
                workflow, len(runs), duration, runner_name, tick_validation
            ),
            encoding="utf-8",
        )
        workflow_path = output_dir / "workflow.json"
        workflow_path.write_text(
            json.dumps(
                {
                    "experiment_id": workflow.experiment_id,
                    "research_question": workflow.question_id,
                    "hypothesis": workflow.hypothesis_id,
                    "title": workflow.title,
                    "conditions": workflow.conditions,
                    "ticks": workflow.ticks,
                    "ticks_contract": "minimum requested observation window",
                    "seeds": list(effective_seeds),
                    "protocol": workflow.protocol,
                    "resolved_runner": runner_name,
                    "tick_validation": tick_validation,
                    "notes": workflow.notes,
                    "execution": "registered experiment_suite runner",
                    "assistant_policy": "AI is post-hoc interpretation only.",
                    **(
                        {"subject": profile_subject}
                        if profile_subject is not None
                        else {}
                    ),
                    "epistemic_layers": EPISTEMIC_LAYERS,
                },
                indent=2,
                ensure_ascii=True,
            )
            + "\n",
            encoding="utf-8",
        )
        recorder.record_provenance_digests(
            code_digest=_sha256_file(Path(experiment_suite.__file__)),
            config_digest=config_digest,
            prompt_digest=hashlib.sha256(b"NO_PROMPT").hexdigest(),
            data_digest=_sha256_files(
                [
                    data_path,
                    data_v2.raw_index_path,
                    data_v2.ai_packet_path,
                    data_v2.ai_packet_digest_path,
                    *trace_paths,
                    *([gateway_state_path] if gateway_state_path is not None else []),
                ],
                output_dir,
            ),
        )
        recorder.record_runtime(duration)
        failed_native = runner_name in CONNECTOME_RUNNERS.values() and (
            tick_validation.get("status") != "SATISFIED"
            or any(run.runtime_error for run in runs)
        )
        if failed_native:
            recorder.mark_failed().save()
        else:
            recorder.mark_completed().save()

        ai_report = self._append_ai_report(workflow.experiment_id)
        manifest_path = output_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        artifacts = manifest.setdefault("artifacts", {})
        artifacts["statistics"] = str(statistics_path.relative_to(output_dir)).replace(
            "\\", "/"
        )
        manifest["execution_contract"] = {
            "resolved_runner": runner_name,
            "ticks_requested": workflow.ticks,
            "tick_validation": tick_validation,
            "question_id": workflow.question_id,
            "hypothesis_id": workflow.hypothesis_id,
            "protocol": workflow.protocol,
            "runtime_runner_bytecode_sha256": runtime_runner_digest,
            "source_runner_bytecode_sha256": source_runner_digest,
            "runtime_summary_bytecode_sha256": summary_runtime_digest,
            "source_summary_bytecode_sha256": summary_source_digest,
            "source_runtime_consistency": "MATCH",
        }
        if connectome_sources:
            manifest["execution_contract"]["connectome_sources"] = {
                Path(path)
                .relative_to(Path(__file__).resolve().parents[2])
                .as_posix(): value
                for path, value in connectome_sources.items()
            }
            manifest["execution_contract"]["data_kind"] = "SYNTHETIC"
            manifest["execution_contract"]["learning_enabled"] = False
            manifest["execution_contract"]["automatic_evidence_promotion"] = False
        manifest["epistemic_layers"] = EPISTEMIC_LAYERS
        artifacts["raw_run_index"] = "DATA/runs_index.json"
        artifacts["current_run"] = "DATA/current_run.json"
        if gateway_state_path is not None:
            artifacts["gateway_state"] = "DATA/gateway_state.json"
        artifacts["ai_packet"] = "analysis/ai_packet.json"
        artifacts["ai_packet_digest"] = "analysis/ai_packet_digest.json"
        if operational_protocol is not None:
            artifacts["preregistration"] = str(operational_protocol["preregistration"])
        if ai_report.get("status") == "generated":
            artifacts["ai_report_json"] = str(ai_report["json"])
            artifacts["ai_report_markdown"] = str(ai_report["markdown"])
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

        summary_path = write_experiment_summary(
            self._research_root, workflow.experiment_id, ai_report
        )
        return {
            "experiment_id": workflow.experiment_id,
            "manifest": f"experiments/{workflow.experiment_id}/manifest.json",
            "report": f"experiments/{workflow.experiment_id}/report.md",
            "workflow": f"experiments/{workflow.experiment_id}/workflow.json",
            "statistics": f"experiments/{workflow.experiment_id}/analysis/statistics.json",
            "ai_packet": f"experiments/{workflow.experiment_id}/analysis/ai_packet.json",
            "raw_run_index": f"experiments/{workflow.experiment_id}/DATA/runs_index.json",
            "data_id": f"DATA-{workflow.experiment_id}",
            "ai_report": ai_report,
            "summary": summary_path,
            "result": {
                "run_count": len(runs),
                "duration_seconds": duration,
                "runner": runner_name,
                "ticks_requested": workflow.ticks,
                "seeds_executed": list(effective_seeds),
                "tick_validation": tick_validation,
            },
            "epistemic_layers": EPISTEMIC_LAYERS,
        }

    @staticmethod
    def _science_runner(body: dict[str, object], workflow: ExperimentWorkflow) -> str:
        """Resolve execution from protocol and registered research question.

        Generated experiment IDs are labels only. They must never silently select
        a scientific runner, because that previously allowed TEMP questions to be
        executed as PING recurrence experiments.
        """
        protocol = str(body.get("protocol") or workflow.protocol)
        question_id = workflow.question_id
        operational_runner = OPERATIONAL_RUNNERS.get(protocol)
        if operational_runner is not None:
            return operational_runner
        if protocol == "science_all_v1":
            return "run_all"
        if protocol == "science_time_v1":
            if not question_id.startswith("RQ-TIME-"):
                raise WorkflowValidationError(
                    "science_time_v1 requires a RQ-TIME-* research question."
                )
            return "run_time"
        if protocol == "science_5d_v1":
            if not question_id.startswith("RQ-5D-"):
                raise WorkflowValidationError(
                    "science_5d_v1 requires a RQ-5D-* research question."
                )
            return "run_5d"
        if protocol != "science_suite_v1":
            raise WorkflowValidationError(
                f"Protocol '{protocol}' is not a Science Suite runner protocol."
            )

        rq_runners = (
            ("RQ-PING-", "run_ping"),
            ("RQ-TEMP-", "run_temporal"),
            ("RQ-TIME-", "run_time"),
            ("RQ-5D-", "run_5d"),
            ("RQ-STDP-", "run_stdp"),
            ("RQ-REG-", "run_regulation"),
        )
        for prefix, runner_name in rq_runners:
            if question_id.startswith(prefix):
                return runner_name
        if question_id == "RQ-SNN-001":
            # Keep the UI workflow executable, but never relabel an impulse-response
            # PING run as primary evidence for long-term stability. The complete
            # suite is diagnostic only; _semantic_status deliberately keeps this RQ
            # at MISMATCH until a dedicated sustained-activity protocol exists.
            return "run_all"
        if question_id == "RQ-SNN-002":
            return "run_ping"
        if question_id == "RQ-SNN-005":
            return "run_learning_repeat"
        raise WorkflowValidationError(
            f"No science runner is registered for research question '{question_id}'. "
            "Select a compatible registered protocol instead of falling back to PING."
        )

    @staticmethod
    def _validate_tick_execution(
        runner_name: str,
        requested_ticks: int,
        seeds: tuple[int, ...],
        runs: Sequence[_ScientificRunLike],
    ) -> dict[str, object]:
        """Verify that tick-aware runners really respected the requested window."""
        exact_window_runners = {
            "run_embodied_closed_loop",
            "run_embodied_proprioception",
            "run_embodied_perturbation",
            "run_connectome_topology",
            "run_embodied_controller",
            "run_embodied_timing",
            "run_ping",
            "run_ping_v2",
            "run_5d",
            "run_temporal",
            "run_recurrence_map",
            "run_replication",
            "run_5d_matched",
            "run_regulation_recovery",
            "run_temporal_order",
            "run_performance_profile",
            "run_recurrence_scale",
        }
        if runner_name in exact_window_runners:
            observed_ints: list[int] = []
            for run in runs:
                value = run.metrics.get("ticks_executed")
                if (
                    isinstance(value, bool)
                    or not isinstance(value, int)
                    or value < requested_ticks
                ):
                    raise WorkflowValidationError(
                        f"Tick contract violated: runner {runner_name} did not execute at least {requested_ticks} ticks in every run."
                    )
                observed_ints.append(value)
            if not observed_ints:
                raise WorkflowValidationError(
                    f"Tick contract violated: runner {runner_name} produced no runs."
                )
            return {
                "status": "SATISFIED",
                "mode": "minimum_per_run",
                "requested_ticks": requested_ticks,
                "observed_min": min(observed_ints),
                "observed_max": max(observed_ints),
            }

        if runner_name == "run_sustained_stability":
            observed_ints = [
                value
                for run in runs
                if isinstance((value := run.metrics.get("ticks_executed")), int)
                and not isinstance(value, bool)
            ]
            if len(observed_ints) != len(runs) or not observed_ints:
                raise WorkflowValidationError(
                    "Sustained stability runner produced incomplete tick observations."
                )
            if min(observed_ints) < requested_ticks:
                raise WorkflowValidationError(
                    "Sustained stability runner did not execute the requested tick budget in every run."
                )
            if len(runs) != len(seeds) * 2:
                raise WorkflowValidationError(
                    "Sustained stability runner must produce control and treatment runs for every seed."
                )
            return {
                "status": "SATISFIED",
                "mode": "minimum_per_run_with_control_and_treatment",
                "requested_ticks": requested_ticks,
                "observed_min": min(observed_ints),
                "observed_max": max(observed_ints),
                "run_count": len(runs),
            }

        if runner_name == "run_time":
            missing_seeds: list[int] = []
            for seed in seeds:
                if not any(
                    run.seed == seed and run.metrics.get("ticks") == requested_ticks
                    for run in runs
                ):
                    missing_seeds.append(seed)
            if missing_seeds:
                raise WorkflowValidationError(
                    "TIME tick ladder does not contain the requested terminal tick count "
                    f"for seeds: {missing_seeds}."
                )
            return {
                "status": "SATISFIED",
                "mode": "terminal_tick_per_seed",
                "requested_ticks": requested_ticks,
            }

        if runner_name == "run_all":
            tick_groups = ("ping:", "temporal:", "5d:")
            relevant = [
                run
                for run in runs
                if any(str(run.condition).startswith(prefix) for prefix in tick_groups)
            ]
            if not relevant or any(
                not isinstance(run.metrics.get("ticks_executed"), int)
                or run.metrics["ticks_executed"] < requested_ticks
                for run in relevant
            ):
                raise WorkflowValidationError(
                    "Science ALL tick contract violated in a tick-aware subgroup."
                )
            for seed in seeds:
                if not any(
                    run.seed == seed
                    and str(run.condition).startswith("time:")
                    and run.metrics.get("ticks") == requested_ticks
                    for run in runs
                ):
                    raise WorkflowValidationError(
                        f"Science ALL TIME subgroup lacks requested tick terminal for seed {seed}."
                    )
            return {
                "status": "SATISFIED",
                "mode": "mixed_protocol_tick_contract",
                "requested_ticks": requested_ticks,
            }

        return {
            "status": "NOT_APPLICABLE",
            "mode": "protocol_defined_internal_trials",
            "requested_ticks": requested_ticks,
        }

    def _append_ai_report(self, experiment_id: str) -> dict[str, object]:
        """Generate AIRR only after completion, or expose unavailable explicitly."""
        if self._ai_backend is None:
            return {"status": "unavailable", "reason": "AI backend not configured"}
        try:
            report = AIRRPipeline(self._research_root).analyze(
                experiment_id, self._ai_backend
            )
        except Exception as exc:
            return {
                "status": "failed",
                "error": type(exc).__name__,
                "message": str(exc),
            }
        return {
            "status": "generated",
            "report_id": report.report_id,
            "json": f"experiments/{experiment_id}/reports/{report.report_id}.json",
            "markdown": f"experiments/{experiment_id}/reports/{report.report_id}.md",
            "human_review": "PENDING",
            "scientific_evidence": False,
        }

    def run(
        self,
        body: dict[str, object],
        run_ticks: Callable[[int], object],
        before: dict[str, int],
        after: Callable[[], dict[str, int]],
    ) -> dict[str, object]:
        """Execute a bounded tick run and write manifest, plan, and report."""
        workflow = self._validate(body)
        output_dir = self._research_root / "experiments" / workflow.experiment_id
        manifest_path = output_dir / "manifest.json"
        if manifest_path.exists():
            raise WorkflowValidationError(
                f"Experiment '{workflow.experiment_id}' already exists."
            )

        output_dir.mkdir(parents=True, exist_ok=False)
        relative_root = Path("experiments") / workflow.experiment_id
        plan_path = output_dir / "workflow.json"
        plan_path.write_text(
            json.dumps(
                {
                    "title": workflow.title,
                    "research_question": workflow.question_id,
                    "hypothesis": workflow.hypothesis_id,
                    "conditions": workflow.conditions,
                    "ticks": workflow.ticks,
                    "protocol": workflow.protocol,
                    "seeds": list(workflow.seeds),
                    "notes": workflow.notes,
                    "execution": "controller.step",
                    "assistant_policy": "No AI-generated input is executed or used as evidence.",
                    "epistemic_layers": EPISTEMIC_LAYERS,
                },
                indent=2,
                ensure_ascii=True,
            )
            + "\n",
            encoding="utf-8",
        )

        recorder = ExperimentRecorder(workflow.experiment_id, output_dir=output_dir)
        recorder.record_research_links(
            [workflow.question_id], [workflow.hypothesis_id]
        ).record_simulation_params(
            ticks=workflow.ticks,
            seed=workflow.seeds[0],
            seeds=list(workflow.seeds),
            protocol=workflow.protocol,
        ).record_artifact(
            "workflow", str(relative_root / plan_path.name).replace("\\", "/")
        )
        data_path = output_dir / "DATA" / "runs.json"
        data_path.parent.mkdir(parents=True, exist_ok=True)

        started = perf_counter()
        try:
            run_ticks(workflow.ticks)
        except Exception as exc:
            recorder.record_runtime_error(
                tick=before["tick"],
                phase="controller.step",
                exception_type=type(exc).__name__,
                message=str(exc),
                fatal=True,
            ).mark_failed()
            recorder.record_runtime(perf_counter() - started).save()
            raise

        runtime = after()
        duration = perf_counter() - started
        observed_ticks = runtime["tick"] - before["tick"]
        if observed_ticks < workflow.ticks:
            recorder.record_runtime_error(
                tick=runtime["tick"],
                phase="tick_contract",
                exception_type="TickContractViolation",
                message=f"Requested {workflow.ticks}, observed {observed_ticks} ticks.",
                fatal=True,
            ).mark_failed()
            recorder.record_runtime(duration).save()
            raise WorkflowValidationError(
                f"Runtime tick contract violated: requested {workflow.ticks}, observed {observed_ticks}."
            )
        recorder.record_results(
            passed=True,
            start=before,
            end=runtime,
            observed_ticks=observed_ticks,
            ticks_requested=workflow.ticks,
            tick_contract="SATISFIED",
        ).record_artifact("data", "DATA/runs.json").record_runtime(
            duration
        ).mark_completed().save()

        data_path.write_text(
            json.dumps(
                [
                    {
                        "experiment_id": workflow.experiment_id,
                        "condition": "exploratory_runtime_ticks",
                        "seed": workflow.seeds[0],
                        "metrics": {
                            "ticks_requested": workflow.ticks,
                            "ticks_executed": observed_ticks,
                            "start_tick": before["tick"],
                            "end_tick": runtime["tick"],
                            "neurons": runtime["neurons"],
                            "synapses": runtime["synapses"],
                        },
                        "runtime_error": None,
                    }
                ],
                indent=2,
                ensure_ascii=True,
            )
            + "\n",
            encoding="utf-8",
        )

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["epistemic_layers"] = EPISTEMIC_LAYERS
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

        report_path = output_dir / "report.md"
        report_path.write_text(
            self._render_report(workflow, before, runtime, duration), encoding="utf-8"
        )
        return {
            "experiment_id": workflow.experiment_id,
            "manifest": str(relative_root / manifest_path.name).replace("\\", "/"),
            "report": str(relative_root / report_path.name).replace("\\", "/"),
            "result": {"start": before, "end": runtime, "duration_seconds": duration},
            "epistemic_layers": EPISTEMIC_LAYERS,
        }

    def _validate(self, body: dict[str, object]) -> ExperimentWorkflow:
        def required(name: str) -> str:
            value = body.get(name)
            if not isinstance(value, str) or not value.strip():
                raise WorkflowValidationError(f"Missing '{name}'.")
            return value.strip()

        experiment_id_value = body.get("experiment_id", "")
        if not isinstance(experiment_id_value, str):
            raise WorkflowValidationError("Experiment ID must be text.")
        experiment_id = experiment_id_value.strip() or self._next_experiment_id()
        if not experiment_id.startswith("EXP-") or len(experiment_id) > 64:
            raise WorkflowValidationError(
                "Experiment ID must use the EXP-* convention."
            )
        ticks = body.get("ticks")
        protocol = str(body.get("protocol") or "runtime_ticks_v1")
        tick_limit = 1_000_000 if protocol == "science_time_v1" else 100_000
        if (
            not isinstance(ticks, int)
            or isinstance(ticks, bool)
            or not 1 <= ticks <= tick_limit
        ):
            raise WorkflowValidationError(
                f"Ticks must be an integer between 1 and {tick_limit}."
            )

        if protocol in CONNECTOME_RUNNERS and not 60 <= ticks <= 10000:
            raise WorkflowValidationError(
                "Connectome engineering screens require 60..10000 ticks"
            )
        seeds = self._parse_seeds(body.get("seeds"))
        question_id = required("question_id")
        hypothesis_id = required("hypothesis_id")
        try:
            guard_cognition_launch(self._research_root, question_id, protocol)
            guard_connectome_launch(
                self._research_root, question_id, hypothesis_id, protocol
            )
        except (CognitionGovernanceError, ConnectomeGovernanceError) as exc:
            raise WorkflowValidationError(str(exc)) from exc
        registry = ResearchRegistry(self._research_root / "registry").load_all()
        question = registry.questions.get(question_id)
        hypothesis = registry.hypotheses.get(hypothesis_id)
        if question is None:
            raise WorkflowValidationError(f"Unknown research question '{question_id}'.")
        exploratory_runtime = (
            protocol == "runtime_ticks_v1" and body.get("exploratory") is True
        )
        if exploratory_runtime and hypothesis_id == "EXPLORATORY-UNSPECIFIED":
            hypothesis = None
        elif hypothesis is None or hypothesis.research_question != question.id:
            raise WorkflowValidationError(
                "The selected hypothesis does not belong to the research question."
            )
        if protocol_by_id(self._research_root, protocol) is not None:
            try:
                validate_operational_protocol(
                    self._research_root,
                    question_id=question_id,
                    hypothesis_id=hypothesis_id,
                    protocol_id=protocol,
                    seed_count=len(seeds),
                )
            except PreregistrationError as exc:
                raise WorkflowValidationError(str(exc)) from exc

        return ExperimentWorkflow(
            experiment_id=experiment_id,
            question_id=question_id,
            hypothesis_id=hypothesis_id,
            title=required("title"),
            conditions=required("conditions"),
            ticks=ticks,
            notes=str(body.get("notes", "")).strip(),
            protocol=protocol,
            seeds=seeds,
        )

    @staticmethod
    def _parse_seeds(value: object) -> tuple[int, ...]:
        """Parse comma-separated seeds and compact ranges from the runner UI."""
        if value is None or value == "":
            return (42, 43, 44)
        if isinstance(value, str):
            tokens: list[object] = [
                token.strip() for token in value.split(",") if token.strip()
            ]
        elif isinstance(value, (list, tuple)):
            tokens = list(cast(list[object] | tuple[object, ...], value))
        else:
            raise WorkflowValidationError("Seeds must be comma-separated integers.")

        parsed: list[int] = []
        for token in tokens:
            if isinstance(token, bool):
                raise WorkflowValidationError("Seeds must be non-negative integers.")
            text = str(token).strip()
            if "-" in text and text.count("-") == 1:
                start_text, end_text = (part.strip() for part in text.split("-"))
                if start_text.isdigit() and end_text.isdigit():
                    start, end = int(start_text), int(end_text)
                    if end < start or end - start > 63:
                        raise WorkflowValidationError(
                            "Seed ranges must contain 64 values or fewer."
                        )
                    parsed.extend(range(start, end + 1))
                    continue
            if not text.isdigit():
                raise WorkflowValidationError("Seeds must be non-negative integers.")
            parsed.append(int(text))

        unique = tuple(dict.fromkeys(parsed))
        if not unique or len(unique) > 64:
            raise WorkflowValidationError("Provide between 1 and 64 unique seeds.")
        return unique

    def _next_experiment_id(self) -> str:
        """Return the first available generated experiment identifier."""
        experiments_dir = self._research_root / "experiments"
        for number in range(1, 10_000):
            experiment_id = f"EXP-GEN-{number:04d}"
            if not (experiments_dir / experiment_id).exists():
                return experiment_id
        raise WorkflowValidationError("No generated experiment IDs are available.")

    @staticmethod
    def _render_science_report(
        workflow: ExperimentWorkflow,
        run_count: int,
        duration: float,
        runner_name: str,
        tick_validation: dict[str, object],
    ) -> str:
        return "\n".join(
            [
                f"# {workflow.experiment_id}: {workflow.title}",
                "",
                "## Forschungszuordnung",
                f"Forschungsfrage: `{workflow.question_id}`",
                f"Hypothese: `{workflow.hypothesis_id}`",
                f"Aufgeloester Runner: `{runner_name}`",
                "",
                "## Protokoll und Einstellungen",
                f"Protokoll: `{workflow.protocol}`",
                f"Angeforderte Mindest-Ticks: `{workflow.ticks}`",
                f"Seeds: `{', '.join(str(seed) for seed in workflow.seeds)}`",
                f"Tick-Vertrag: `{json.dumps(tick_validation, ensure_ascii=False, sort_keys=True)}`",
                "",
                "## Bedingungen",
                workflow.conditions,
                f"Runs: {run_count}; Dauer: {duration:.6f} s",
                "",
                "## Daten und Statistik",
                "Kompakte Run-Projektion: `DATA/runs.json`",
                "Unveränderlicher Rohdatenindex: `DATA/runs_index.json`",
                "KI-Eingabepaket: `analysis/ai_packet.json` (hart begrenzt)",
                "Deterministische deskriptive Statistik: `analysis/statistics.json`",
                "Die Summary verbindet Rohdaten, Formeln, Einzelruns, Bedingungen, Reproduzierbarkeit und AIRR ohne KI-generierte Statistik.",
                "",
                "## Epistemische Ebenen",
                "UI-Zustand: Dashboard-Steuerung und Fortschritt; kein wissenschaftliches Ergebnis.",
                "DATA: Rohdaten, Run-Index und deterministische Statistik.",
                "EVID: nicht erzeugt; Clean Freeze, semantische Zuordnung und Human Review erforderlich.",
                "Interpretation: nachgelagerte KI-/Human-Interpretation; keine Ausfuehrungseingabe.",
                "",
                "## Evidenzstatus",
                "DATA, Manifest, Workflow und deterministische Statistik sind erzeugt. Wissenschaftliche EVID entsteht erst nach passender semantischer Zuordnung, Clean Freeze und Human Review.",
                "",
                "## Hinweise",
                workflow.notes or "Keine.",
                "",
            ]
        )

    @staticmethod
    def _render_report(
        workflow: ExperimentWorkflow,
        before: dict[str, int],
        after: dict[str, int],
        duration: float,
    ) -> str:
        observed_ticks = after["tick"] - before["tick"]
        return "\n".join(
            [
                f"# {workflow.experiment_id}: {workflow.title}",
                "",
                "## Forschungsfrage",
                workflow.question_id,
                "",
                "## Hypothese",
                workflow.hypothesis_id,
                "",
                "## Bedingungen",
                workflow.conditions,
                "",
                "## Ausfuehrung",
                f"Controller: `step({workflow.ticks})`",
                "Ausfuehrungsmodus: kontrollierter Runtime-Lauf",
                f"Dauer: {duration:.6f} s",
                "",
                "## Ergebnis",
                f"Tick: {before['tick']} -> {after['tick']}",
                f"Neuronen: {before['neurons']} -> {after['neurons']}",
                f"Synapsen: {before['synapses']} -> {after['synapses']}",
                f"Angeforderte Ticks: {workflow.ticks}",
                f"Beobachtete Ticks: {observed_ticks}",
                f"Tick-Vertrag: {'SATISFIED' if observed_ticks >= workflow.ticks else 'VIOLATED'}",
                "",
                "## Epistemische Ebenen",
                "UI-Zustand ist nur Dashboard-Steuerung und Fortschritt.",
                "DATA sind Manifest, Workflow und gemessene Laufwerte.",
                "EVID wurde nicht erzeugt.",
                "Interpretation bleibt nachgelagert und hat keine Ausfuehrungsautoritaet.",
                "",
                "## Reproduzierbarkeit",
                "Git-Commit, Laufzeitumgebung und Runtime-Parameter stehen im Manifest.",
                "",
                "## Evidenzstatus",
                "Keine EVID erzeugt. Fuer wissenschaftliche Evidenz sind ein sauberer Source-Freeze, ein registriertes Protokoll, kontrollierte unabhaengige Variablen und definierte Messgroessen erforderlich.",
                "",
                "## Hinweise",
                workflow.notes or "Keine.",
                "",
                "KI-Ausgaben sind weder Ausfuehrungseingabe noch Evidenz. Eine finale Antwort auf die Forschungsfrage bleibt einer menschlichen wissenschaftlichen Bewertung vorbehalten.",
                "",
            ]
        )


def _find_named_code(code: CodeType, name: str) -> CodeType | None:
    if code.co_name == name:
        return code
    for value in code.co_consts:
        if not isinstance(value, CodeType):
            continue
        found = _find_named_code(value, name)
        if found is not None:
            return found
    return None


def _code_digest(code: CodeType) -> str:
    """Hash executable code semantics while ignoring path/debug metadata.

    Raw marshal bytes include interpreter- and compilation-specific metadata that
    can differ between an imported function and the same freshly compiled source.
    The source-freeze gate needs semantic identity instead: bytecode, exception
    tables, signature/flags, referenced names and recursively hashed constants.
    """
    digest = hashlib.sha256()

    def update_value(value: object) -> None:
        if isinstance(value, CodeType):
            digest.update(b"code\0")
            update_code(value)
            return
        if isinstance(value, tuple):
            digest.update(b"tuple\0")
            tuple_items = cast(tuple[object, ...], value)
            for item in tuple_items:
                update_value(item)
                digest.update(b"\0")
            return
        if isinstance(value, frozenset):
            digest.update(b"frozenset\0")
            set_items = cast(frozenset[object], value)
            encoded_items = sorted(
                f"{type(item).__qualname__}:{item!r}".encode(
                    "utf-8", errors="backslashreplace"
                )
                for item in set_items
            )
            for item in encoded_items:
                digest.update(item)
                digest.update(b"\0")
            return
        if isinstance(value, bytes):
            digest.update(b"bytes\0")
            digest.update(value)
            return
        digest.update(type(value).__qualname__.encode("utf-8"))
        digest.update(b":")
        digest.update(repr(value).encode("utf-8", errors="backslashreplace"))

    def update_code(item: CodeType) -> None:
        for number in (
            item.co_argcount,
            item.co_posonlyargcount,
            item.co_kwonlyargcount,
            item.co_nlocals,
            item.co_stacksize,
            item.co_flags,
        ):
            digest.update(str(number).encode("ascii"))
            digest.update(b"\0")
        digest.update(item.co_code)
        digest.update(b"\0")
        digest.update(item.co_exceptiontable)
        digest.update(b"\0")
        for values in (
            item.co_names,
            item.co_varnames,
            item.co_freevars,
            item.co_cellvars,
        ):
            update_value(tuple(values))
            digest.update(b"\0")
        update_value(tuple(item.co_consts))

    update_code(code)
    return digest.hexdigest()


def _assert_loaded_callable_matches_source(
    function: Callable[..., object], source_path: Path, function_name: str
) -> tuple[str, str]:
    """Block scientific runs when a long-lived process still holds stale code."""
    runtime_digest = _code_digest(function.__code__)
    compiled = compile(
        source_path.read_text(encoding="utf-8"), str(source_path), "exec"
    )
    source_code = _find_named_code(compiled, function_name)
    if source_code is None:
        raise WorkflowValidationError(
            f"Cannot verify runtime/source consistency for {function_name}."
        )
    source_digest = _code_digest(source_code)
    if runtime_digest != source_digest:
        raise WorkflowValidationError(
            f"Running process contains stale code for {function_name}. Restart the MHRN "
            "dashboard/runtime before creating a scientific experiment."
        )
    return runtime_digest, source_digest


def _sha256_files(paths: Sequence[Path], root: Path) -> str:
    """Hash a set of artifacts using experiment-relative names for portability."""
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.relative_to(root).as_posix()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _load_yaml(path: Path) -> dict[str, Any]:
    import yaml

    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise WorkflowValidationError("Science configuration must be a mapping.")
    return cast(dict[str, Any], loaded)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
