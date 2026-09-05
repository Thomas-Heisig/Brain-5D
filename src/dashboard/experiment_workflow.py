"""Controlled experiment execution and report publication for the dashboard."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from time import perf_counter
from typing import Any, Callable, cast

from src.research.experiment_recorder import ExperimentRecorder
from src.research.registry import ResearchRegistry
from src.research_assistant.airr import AIRRPipeline
from src.research_assistant.assistant import AnalysisBackend

from .models import JSONValue


class WorkflowValidationError(ValueError):
    """Raised when a workflow submission is not scientifically traceable."""


def _summary_items(value: object) -> list[str]:
    """Return non-empty textual items from an AIRR list field."""
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _airr_observation_fallback(content: dict[str, object]) -> list[str]:
    """Extract explicit limitation observations when AIRR request lists are empty."""
    interpretation = content.get("interpretation")
    observations: list[object] = []
    if isinstance(interpretation, dict):
        observations.extend(
            interpretation.get("observations", [])
            if isinstance(interpretation.get("observations"), list)
            else []
        )
    observations.extend(
        content.get("observations", [])
        if isinstance(content.get("observations"), list)
        else []
    )
    return [
        str(item["value"]).strip()
        for item in observations
        if isinstance(item, dict)
        and str(item.get("type", "")).lower() in {"limitation", "limitations"}
        and str(item.get("value", "")).strip()
    ]


def write_experiment_summary(
    research_root: Path,
    experiment_id: str,
    ai_report: dict[str, object],
) -> str:
    """Write the post-hoc assistant summary beside one experiment's artifacts."""
    experiment_dir = research_root / "experiments" / experiment_id
    report_dir = experiment_dir / "reports"
    manifest: dict[str, Any] = {}
    manifest_path = experiment_dir / "manifest.json"
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            manifest = {}
    lines = [
        f"# {experiment_id}: Zusammenfassung",
        "",
        "Diese Zusammenfassung wurde nach Abschluss des Laufs durch den internen "
        "Research Assistant aus den Experimentartefakten und dem AIRR erstellt. "
        "Sie beschreibt die Daten, die Berichte und deren wissenschaftliche Grenzen.",
        "",
        "## Versuchsuebersicht",
        "",
        f"- Status: `{manifest.get('experiment_status', 'unbekannt')}`",
        f"- Forschungsfragen: {', '.join(map(str, manifest.get('research_questions', []))) or 'nicht angegeben'}",
        f"- Hypothesen: {', '.join(map(str, manifest.get('hypotheses', []))) or 'nicht angegeben'}",
        f"- Durchlaeufe: `{manifest.get('results', {}).get('run_count', 'unbekannt') if isinstance(manifest.get('results'), dict) else 'unbekannt'}`",
        f"- Laufmodus: `{manifest.get('research_run_mode', 'unbekannt')}`",
        f"- Netzwerkmodus: `{manifest.get('network_mode', 'unbekannt')}`",
        "",
        "## Artefakte",
        "",
    ]
    for path in sorted(experiment_dir.rglob("*")):
        if path.is_file() and path.name != "summary.md":
            relative = path.relative_to(experiment_dir).as_posix()
            lines.append(f"- [{relative}]({relative})")
    lines.extend(["", "## AI-Bericht", ""])
    status = str(ai_report.get("status", "unknown"))
    lines.append(f"- AIRR-Status: `{status}`")
    if status == "generated":
        lines.extend(
            [
                f"- AIRR: [{ai_report['report_id']}.md](reports/{ai_report['report_id']}.md)",
                f"- AIRR JSON: [{ai_report['report_id']}.json](reports/{ai_report['report_id']}.json)",
                "- Wissenschaftliche Evidenz: `false`",
                "- Human Review: `PENDING`",
            ]
        )
        report_path = report_dir / f"{ai_report['report_id']}.json"
        if report_path.is_file():
            content = json.loads(report_path.read_text(encoding="utf-8"))["content"]
            interpretation = content.get("interpretation", {})
            interpretation = interpretation if isinstance(interpretation, dict) else {}
            requested_evidence = _summary_items(content.get("missing_evidence"))
            if not requested_evidence:
                requested_evidence = _summary_items(
                    interpretation.get("requested_evidence")
                )
            if not requested_evidence:
                requested_evidence = [
                    f"AIRR-Limitation dokumentieren: {item}"
                    for item in _airr_observation_fallback(content)
                ]
            if not requested_evidence:
                requested_evidence = [
                    "Keine expliziten zusätzlichen Nachweise im AIRR angegeben."
                ]
            recommended_follow_up = _summary_items(content.get("recommended_follow_up"))
            if not recommended_follow_up:
                recommended_follow_up = _summary_items(
                    interpretation.get("recommended_experiments")
                )
            if not recommended_follow_up:
                recommended_follow_up = [
                    "Keine expliziten Folgeexperimente im AIRR angegeben."
                ]
            lines.extend(
                [
                    "",
                    "### KI-Einschaetzung",
                    "",
                    "Die KI bewertet den vorliegenden Datensatz wie folgt:",
                    "",
                    str(
                        content.get(
                            "executive_summary",
                            content.get("conclusion", "Keine Einschaetzung vorhanden."),
                        )
                    ),
                    "",
                    f"KI-Konfidenz: `{content.get('ai_confidence', 0.0)}`",
                    "",
                    "Angeforderte zusaetzliche Nachweise:",
                    "",
                ]
            )
            for item in requested_evidence:
                lines.append(f"- {item}")
            lines.extend(["", "Empfohlene Folgeexperimente:", ""])
            for item in recommended_follow_up:
                lines.append(f"- {item}")
    else:
        lines.append(
            f"- Hinweis: `{ai_report.get('reason', ai_report.get('message', ''))}`"
        )
    lines.extend(
        [
            "",
            "## Wissenschaftliche Grenze",
            "",
            "Die KI-Auswertung ist post-hoc, steuert den Lauf nicht und ersetzt keine "
            "menschliche wissenschaftliche Pruefung oder Evidenzfreigabe.",
            "",
        ]
    )
    summary_path = experiment_dir / "summary.md"
    summary_path.write_text("\n".join(lines), encoding="utf-8")
    return f"experiments/{experiment_id}/summary.md"


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
                        "label": "Science Suite v1 (DATA + Manifest)",
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
        """Execute a registered suite and persist DATA, manifest, and report."""
        science_body = dict(body)
        science_body.setdefault("protocol", "science_suite_v1")
        workflow = self._validate(science_body)
        runner_name = self._science_runner(science_body, workflow.experiment_id)
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
        if runner_name in {"run_ping", "run_ping_v2", "run_5d", "run_time"}:
            runs = runner(config, seeds=effective_seeds, ticks=workflow.ticks)
        else:
            runs = runner(config, seeds=effective_seeds)
        runs = [replace(run, experiment_id=workflow.experiment_id) for run in runs]
        duration = perf_counter() - started
        output_dir.mkdir(parents=True, exist_ok=False)
        data_path = output_dir / "DATA" / "runs.json"
        data_path.parent.mkdir(parents=True, exist_ok=True)
        data_path.write_text(
            json.dumps(
                [asdict(run) for run in runs], indent=2, sort_keys=True, default=list
            )
            + "\n",
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
        recorder.record_artifact("workflow", "workflow.json")
        recorder.record_artifact("report", "report.md")
        recorder.record_results(run_count=len(runs), protocol=workflow.protocol)
        report_path = output_dir / "report.md"
        report_path.write_text(
            self._render_science_report(workflow, len(runs), duration), encoding="utf-8"
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
                    "seeds": list(effective_seeds),
                    "protocol": workflow.protocol,
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
            code_digest=_sha256_file(Path(cast(str, experiment_suite.__file__))),
            config_digest=config_digest,
            prompt_digest=hashlib.sha256(b"NO_PROMPT").hexdigest(),
            data_digest=_sha256_file(data_path),
        )
        recorder.record_runtime(duration).mark_completed().save()
        ai_report = self._append_ai_report(workflow.experiment_id)
        if ai_report.get("status") == "generated":
            manifest = json.loads(
                (output_dir / "manifest.json").read_text(encoding="utf-8")
            )
            artifacts = manifest.setdefault("artifacts", {})
            artifacts["ai_report_json"] = str(ai_report["json"])
            artifacts["ai_report_markdown"] = str(ai_report["markdown"])
            (output_dir / "manifest.json").write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        summary_path = write_experiment_summary(
            self._research_root, workflow.experiment_id, ai_report
        )
        return {
            "experiment_id": workflow.experiment_id,
            "manifest": f"experiments/{workflow.experiment_id}/manifest.json",
            "report": f"experiments/{workflow.experiment_id}/report.md",
            "workflow": f"experiments/{workflow.experiment_id}/workflow.json",
            "data_id": f"DATA-{workflow.experiment_id}",
            "ai_report": ai_report,
            "summary": summary_path,
            "result": {"run_count": len(runs), "duration_seconds": duration},
        }

    @staticmethod
    def _science_runner(body: dict[str, object], experiment_id: str) -> str:
        """Resolve execution from the protocol, while keeping IDs traceable labels."""
        protocol_runners = {
            "science_time_v1": "run_time",
            "science_5d_v1": "run_5d",
        }
        runner_name = protocol_runners.get(str(body.get("protocol")))
        if runner_name is not None:
            return runner_name

        if experiment_id.startswith("EXP-PING-0001-v"):
            return "run_ping_v2"
        if experiment_id.startswith("EXP-PING-"):
            return "run_ping"
        if experiment_id.startswith("EXP-TEMP-"):
            return "run_temporal"
        if experiment_id.startswith("EXP-STDP-"):
            return "run_stdp"
        if experiment_id.startswith("EXP-EMB-"):
            return "run_learning_repeat"
        if experiment_id.startswith("EXP-REG-"):
            return "run_regulation"
        if experiment_id.startswith("EXP-LEARN-"):
            return "run_learning"
        return "run_ping"

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
            tokens = list(value)
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
        workflow: ExperimentWorkflow, run_count: int, duration: float
    ) -> str:
        return "\n".join(
            [
                f"# {workflow.experiment_id}: {workflow.title}",
                "",
                "## Protokoll",
                workflow.protocol,
                f"Ticks: {workflow.ticks}; Seeds: {', '.join(map(str, workflow.seeds))}",
                "",
                "## Bedingungen",
                workflow.conditions,
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


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
