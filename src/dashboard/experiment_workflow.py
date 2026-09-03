"""Controlled experiment execution and report publication for the dashboard."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter
from typing import Any, Callable, cast

from src.research.experiment_recorder import ExperimentRecorder
from src.research.registry import ResearchRegistry

from .models import JSONValue


class WorkflowValidationError(ValueError):
    """Raised when a workflow submission is not scientifically traceable."""


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


class ExperimentWorkflowService:
    """Run a fixed controller action and publish its research artifacts.

    The service deliberately accepts a controller callback, never commands or
    model-generated code. This keeps language-model assistance outside the
    causal path of the experiment.
    """

    def __init__(self, research_root: Path) -> None:
        self._research_root = research_root

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
                    {"id": "science_suite_v1", "label": "Science Suite v1 (DATA + Manifest)"},
                    {"id": "science_time_v1", "label": "Science TIME v1 (DATA + Manifest)"},
                    {"id": "science_5d_v1", "label": "Science 5D v1 (DATA + Manifest)"},
                    {"id": "runtime_ticks_v1", "label": "Runtime-Ticks (Laufprotokoll)"},
                    {"id": "stdp_pair_timing_v1", "label": "STDP Pair-Timing v1 (registriert)"},
                ],
            ),
            "next_experiment_id": self._next_experiment_id(),
        }

    def run_science(
        self, body: dict[str, object], *, seeds: tuple[int, ...] = (42, 43, 44)
    ) -> dict[str, object]:
        """Execute a registered suite and persist DATA, manifest, and report."""
        workflow = self._validate(body)
        runners = {
            "EXP-PING-0001": "run_ping",
            "EXP-TEMP-0001": "run_temporal",
            "EXP-STDP-0002": "run_stdp",
            "EXP-EMB-0001": "run_learning_repeat",
            "EXP-TIME-0001": "run_time",
            "EXP-5D-0001": "run_5d",
        }
        runner_name = runners.get(workflow.experiment_id)
        if runner_name is None:
            raise WorkflowValidationError(
                "Science Suite supports EXP-PING-0001, EXP-TEMP-0001, "
                "EXP-STDP-0002, EXP-TIME-0001, and EXP-5D-0001."
            )
        output_dir = self._research_root / "experiments" / workflow.experiment_id
        if (output_dir / "manifest.json").exists():
            raise WorkflowValidationError(
                f"Experiment '{workflow.experiment_id}' already exists."
            )
        from src.research import experiment_suite

        config_path = self._research_root.parent / "configs" / "learning_experiment.yaml"
        if not config_path.exists():
            config_path = Path("configs/learning_experiment.yaml")
        config = _load_yaml(config_path)
        started = perf_counter()
        runs = getattr(experiment_suite, runner_name)(config, seeds=seeds)
        duration = perf_counter() - started
        output_dir.mkdir(parents=True, exist_ok=False)
        data_path = output_dir / "DATA" / "runs.json"
        data_path.parent.mkdir(parents=True, exist_ok=True)
        data_path.write_text(
            json.dumps([asdict(run) for run in runs], indent=2, sort_keys=True, default=list)
            + "\n",
            encoding="utf-8",
        )
        recorder = ExperimentRecorder(workflow.experiment_id, output_dir=output_dir)
        recorder.record_research_links([workflow.question_id], [workflow.hypothesis_id])
        recorder.record_config(str(config_path), "")
        recorder.record_simulation_params(seed=seeds[0], ticks=workflow.ticks, seeds=list(seeds))
        recorder.record_artifact("data", "DATA/runs.json")
        recorder.record_results(run_count=len(runs), protocol="science_suite_v1")
        recorder.record_runtime(duration).mark_completed().save()
        report_path = output_dir / "report.md"
        report_path.write_text(
            self._render_science_report(workflow, len(runs), duration), encoding="utf-8"
        )
        return {
            "experiment_id": workflow.experiment_id,
            "manifest": f"experiments/{workflow.experiment_id}/manifest.json",
            "report": f"experiments/{workflow.experiment_id}/report.md",
            "data_id": f"DATA-{workflow.experiment_id}",
            "result": {"run_count": len(runs), "duration_seconds": duration},
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
        ).record_simulation_params(ticks=workflow.ticks).record_artifact(
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
        recorder.record_results(
            passed=True,
            start=before,
            end=runtime,
            observed_ticks=runtime["tick"] - before["tick"],
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
        tick_limit = 1_000_000 if body.get("protocol") == "science_time_v1" else 100_000
        if (
            not isinstance(ticks, int)
            or isinstance(ticks, bool)
            or not 1 <= ticks <= tick_limit
        ):
            raise WorkflowValidationError(
                f"Ticks must be an integer between 1 and {tick_limit}."
            )

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
        )

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
        workflow: ExperimentWorkflow, run_count: int, duration: float
    ) -> str:
        return "\n".join(
            [
                f"# {workflow.experiment_id}: {workflow.title}",
                "",
                "## Protokoll",
                "science_suite_v1",
                f"Runs: {run_count}; Dauer: {duration:.6f} s",
                "",
                "## Evidenzstatus",
                "DATA und Manifest erzeugt. EVID wird erst nach Clean Freeze und Review erzeugt.",
                "",
                "## Hinweise",
                "Prediction Error, Memory, TIME, 5D, Regulation und Sensorverlust sind in diesem Lauf nicht behauptet.",
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
                f"Beobachtete Ticks: {after['tick'] - before['tick']}",
                "",
                "## Reproduzierbarkeit",
                "Git-Commit, Laufzeitumgebung und Runtime-Parameter stehen im Manifest.",
                "Dieser allgemeine Runner schreibt keinen kontrollierten Seed oder eingefrorenen Konfigurations-Snapshot; daher ist der Lauf ein Betriebsprotokoll, keine evidenzfaehige Messstudie.",
                "",
                "## Evidenzstatus",
                "Keine EVID erzeugt. Fuer wissenschaftliche Evidenz sind ein sauberer Source-Freeze, ein registriertes Protokoll, kontrollierte unabhängige Variablen und definierte Messgroessen erforderlich.",
                "",
                "## Hinweise",
                workflow.notes or "Keine.",
                "",
                "KI-Ausgaben sind weder Ausfuehrungseingabe noch Evidenz. Eine finale Antwort auf die Forschungsfrage bleibt einer menschlichen wissenschaftlichen Bewertung vorbehalten.",
                "",
            ]
        )


def _load_yaml(path: Path) -> dict[str, Any]:
    import yaml

    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise WorkflowValidationError("Science configuration must be a mapping.")
    return cast(dict[str, Any], loaded)
