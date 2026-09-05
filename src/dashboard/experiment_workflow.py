"""Controlled experiment execution and report publication for the dashboard."""

from __future__ import annotations

import gzip
import hashlib
import json
import marshal
import re
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from time import perf_counter
from types import CodeType
from typing import Any, Callable, Protocol, Sequence, cast

from src.research.experiment_recorder import ExperimentRecorder
from src.research.experiment_summary import (
    write_detailed_experiment_summary,
    write_statistics_artifact,
)
from src.research.registry import ResearchRegistry
from src.research_assistant.airr import AIRRPipeline
from src.research_assistant.assistant import AnalysisBackend

from .models import JSONValue


class WorkflowValidationError(ValueError):
    """Raised when a workflow submission is not scientifically traceable."""


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
        return {
            "questions": cast(
                JSONValue,
                [
                    {"id": question.id, "label": question.question}
                    for question in registry.questions.values()
                ],
            ),
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
                ],
            ),
            "next_experiment_id": self._next_experiment_id(),
        }

    def run_science(
        self, body: dict[str, object], *, seeds: tuple[int, ...] | None = None
    ) -> dict[str, object]:
        """Execute the RQ-compatible science runner and persist complete artifacts."""
        science_body = dict(body)
        science_body.setdefault("protocol", "science_suite_v1")
        workflow = self._validate(science_body)
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
        runner = getattr(experiment_suite, runner_name)
        runtime_runner_digest, source_runner_digest = (
            _assert_loaded_callable_matches_source(
                runner, Path(experiment_suite.__file__).resolve(), runner_name
            )
        )
        summary_runtime_digest, summary_source_digest = (
            _assert_loaded_callable_matches_source(
                write_detailed_experiment_summary,
                Path(write_detailed_experiment_summary.__code__.co_filename).resolve(),
                "write_detailed_experiment_summary",
            )
        )
        tick_aware_runners = {
            "run_all",
            "run_ping",
            "run_ping_v2",
            "run_5d",
            "run_time",
            "run_temporal",
        }
        if runner_name in tick_aware_runners:
            runs = runner(config, seeds=effective_seeds, ticks=workflow.ticks)
        else:
            runs = runner(config, seeds=effective_seeds)
        runs = [replace(run, experiment_id=workflow.experiment_id) for run in runs]
        duration = perf_counter() - started

        tick_validation = self._validate_tick_execution(
            runner_name,
            workflow.ticks,
            effective_seeds,
            cast(Sequence[_ScientificRunLike], runs),
        )
        output_dir.mkdir(parents=True, exist_ok=False)
        data_path = output_dir / "DATA" / "runs.json"
        data_path.parent.mkdir(parents=True, exist_ok=True)
        serialized_runs = [asdict(run) for run in runs]
        # Compute statistics from the complete in-memory observations first. Large
        # per-tick traces are then moved to compressed sidecars so runs.json remains
        # reviewable without discarding raw observations.
        statistics_path = write_statistics_artifact(output_dir, serialized_runs)
        trace_paths = _externalize_large_traces(output_dir, serialized_runs)
        data_path.write_text(
            json.dumps(serialized_runs, indent=2, sort_keys=True, default=list) + "\n",
            encoding="utf-8",
        )

        recorder = ExperimentRecorder(workflow.experiment_id, output_dir=output_dir)
        recorder.record_research_links([workflow.question_id], [workflow.hypothesis_id])
        recorder.record_config(str(config_path), config_digest)
        recorder.record_simulation_params(
            seed=effective_seeds[0],
            ticks=workflow.ticks,
            seeds=list(effective_seeds),
            protocol=workflow.protocol,
        )
        recorder.record_artifact("data", "DATA/runs.json")
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
            data_digest=_sha256_files([data_path, *trace_paths], output_dir),
        )
        recorder.record_runtime(duration).mark_completed().save()

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
        if trace_paths:
            artifacts["raw_trace_index"] = "DATA/traces/index.json"
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
            "data_id": f"DATA-{workflow.experiment_id}",
            "ai_report": ai_report,
            "summary": summary_path,
            "result": {
                "run_count": len(runs),
                "duration_seconds": duration,
                "runner": runner_name,
                "ticks_requested": workflow.ticks,
                "tick_validation": tick_validation,
            },
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
            raise WorkflowValidationError(
                "RQ-SNN-001 requires a dedicated long-term stability protocol with sustained activity; "
                "run_ping is not valid primary evidence for this research question."
            )
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
        exact_window_runners = {"run_ping", "run_ping_v2", "run_5d", "run_temporal"}
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
        ).record_runtime(duration).mark_completed().save()

        report_path = output_dir / "report.md"
        report_path.write_text(
            self._render_report(workflow, before, runtime, duration), encoding="utf-8"
        )
        return {
            "experiment_id": workflow.experiment_id,
            "manifest": str(relative_root / manifest_path.name).replace("\\", "/"),
            "report": str(relative_root / report_path.name).replace("\\", "/"),
            "result": {"start": before, "end": runtime, "duration_seconds": duration},
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

        seeds = self._parse_seeds(body.get("seeds"))
        question_id = required("question_id")
        hypothesis_id = required("hypothesis_id")
        registry = ResearchRegistry(self._research_root / "registry").load_all()
        question = registry.questions.get(question_id)
        hypothesis = registry.hypotheses.get(hypothesis_id)
        if question is None:
            raise WorkflowValidationError(f"Unknown research question '{question_id}'.")
        if hypothesis is None or hypothesis.research_question != question.id:
            raise WorkflowValidationError(
                "The selected hypothesis does not belong to the research question."
            )

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
                "Rohdaten: `DATA/runs.json`",
                "Deterministische deskriptive Statistik: `analysis/statistics.json`",
                "Die Summary verbindet Rohdaten, Formeln, Einzelruns, Bedingungen, Reproduzierbarkeit und AIRR ohne KI-generierte Statistik.",
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
    return hashlib.sha256(marshal.dumps(code)).hexdigest()


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
            f"Running process contains stale code for {function_name}. Restart the Brain-5D "
            "dashboard/runtime before creating a scientific experiment."
        )
    return runtime_digest, source_digest


def _safe_trace_name(condition: object, seed: object) -> str:
    label = re.sub(r"[^A-Za-z0-9_.-]+", "-", str(condition)).strip("-") or "trace"
    return f"{label}-seed-{seed}.jsonl.gz"


def _externalize_large_traces(
    output_dir: Path, serialized_runs: list[dict[str, Any]], threshold: int = 10_000
) -> list[Path]:
    """Keep complete large traces compressed and references inside compact DATA."""
    trace_dir = output_dir / "DATA" / "traces"
    trace_entries: list[dict[str, object]] = []
    written: list[Path] = []
    for run in serialized_runs:
        metrics_raw: object = run.get("metrics")
        if not isinstance(metrics_raw, dict):
            continue
        metrics = cast(dict[str, object], metrics_raw)
        comparison_value: object = metrics.get("comparisons")
        if not isinstance(comparison_value, list):
            continue
        comparisons = cast(list[object], comparison_value)
        if len(comparisons) <= threshold:
            continue
        trace_dir.mkdir(parents=True, exist_ok=True)
        path = trace_dir / _safe_trace_name(run.get("condition"), run.get("seed"))
        with gzip.open(
            path, "wt", encoding="utf-8", newline="\n", compresslevel=9
        ) as handle:
            for item in comparisons:
                handle.write(
                    json.dumps(
                        item,
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    )
                )
                handle.write("\n")
        digest = _sha256_file(path)
        count = len(comparisons)
        metrics["comparisons_artifact"] = {
            "path": path.relative_to(output_dir).as_posix(),
            "format": "jsonl.gz",
            "count": count,
            "sha256": digest,
        }
        metrics["comparisons_preview"] = comparisons[:8] + comparisons[-8:]
        del metrics["comparisons"]
        trace_entries.append(
            {
                "condition": run.get("condition"),
                "seed": run.get("seed"),
                "path": path.relative_to(output_dir).as_posix(),
                "count": count,
                "sha256": digest,
                "size_bytes": path.stat().st_size,
            }
        )
        written.append(path)
    if trace_entries:
        index_path = trace_dir / "index.json"
        index_path.write_text(
            json.dumps(
                {"schema_version": "1.0", "traces": trace_entries},
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        written.append(index_path)
    return written


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
