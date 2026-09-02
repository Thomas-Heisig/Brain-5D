"""Controlled experiment execution and report publication for the dashboard."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any, Callable

from src.research.experiment_recorder import ExperimentRecorder
from src.research.registry import ResearchRegistry


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

    def catalog(self) -> dict[str, list[dict[str, str]]]:
        """Return registry entries suitable for workflow selection."""
        registry = ResearchRegistry(self._research_root / "registry").load_all()
        return {
            "questions": [
                {"id": question.id, "label": question.question}
                for question in registry.questions.values()
            ],
            "hypotheses": [
                {
                    "id": hypothesis.id,
                    "question_id": hypothesis.research_question,
                    "label": hypothesis.hypothesis,
                }
                for hypothesis in registry.hypotheses.values()
            ],
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
            raise WorkflowValidationError("Experiment ID must use the EXP-* convention.")
        ticks = body.get("ticks")
        if not isinstance(ticks, int) or isinstance(ticks, bool) or not 1 <= ticks <= 100_000:
            raise WorkflowValidationError("Ticks must be an integer between 1 and 100000.")

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
                f"Dauer: {duration:.6f} s",
                "",
                "## Ergebnis",
                f"Tick: {before['tick']} -> {after['tick']}",
                f"Neuronen: {before['neurons']} -> {after['neurons']}",
                f"Synapsen: {before['synapses']} -> {after['synapses']}",
                "",
                "## Hinweise",
                workflow.notes or "Keine.",
                "",
                "Der Bericht ist ein Laufprotokoll. Die wissenschaftliche Bewertung"
                " erfolgt erst durch registrierte Evidenzregeln; KI-Ausgaben sind"
                " weder Ausfuehrungseingabe noch Evidenz.",
                "",
            ]
        )