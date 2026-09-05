"""Idempotently promote EXP-GEN-0021 follow-ups into the runtime research system."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

QUESTION_APPEND = r"""

- id: RQ-REC-001
  domain: Recurrent Dynamics
  question: Unter welchen Rekurrenzgewichten und Delays wechselt Brain-5D zwischen sofortigem Erlöschen, transienter rekurrenter Aktivität und bis zum Beobachtungsende persistierender Aktivität?
  relevance: EXP-GEN-0021 zeigte einen klaren rekurrenzabhängigen Dynamikunterschied, aber noch keine Parametergrenze.
  literature: []
  hypotheses:
  - H-REC-001-A
  evidence: []
  status: open
  answer:
    current: null
    confidence: none
    limitations: Abgeleitet aus EXP-GEN-0021; persistente Aktivität ist nicht gleichbedeutend mit Gedächtnis oder Kognition.
  created: '2026-09-05'
  updated: '2026-09-05'
- id: RQ-GEN-001
  domain: Learning Generalization
  question: Verbessert reward-moduliertes lokales Lernen die Leistung auf Holdout- und Perturbationsbedingungen, die nicht zur Anpassung verwendet wurden?
  relevance: EXP-GEN-0021 zeigte funktionelle Änderung unter Learning-on, aber keine Generalisierung.
  literature: []
  hypotheses:
  - H-GEN-001-A
  evidence: []
  status: open
  answer:
    current: null
    confidence: none
    limitations: Generalisierung muss gegenüber Learning-off und Sham-Replay getrennt werden.
  created: '2026-09-05'
  updated: '2026-09-05'
- id: RQ-REPL-001
  domain: Replication
  question: Bleiben die in EXP-GEN-0021 beobachteten Rekurrenz- und Learning-Effekte unter unabhängigen Initialisierungen und sauberem Prozess erhalten?
  relevance: Identische Seedsignaturen zeigen Determinismus, aber keine statistisch unabhängige Replikation.
  literature: []
  hypotheses:
  - H-REPL-001-A
  evidence: []
  status: open
  answer:
    current: null
    confidence: none
    limitations: Replikation erfordert echte Variation der Initialisierung und einen Clean Freeze.
  created: '2026-09-05'
  updated: '2026-09-05'
- id: RQ-5D-005
  domain: 5D Topology
  question: Verändert 5D-Geometrie Propagation, Robustheit oder Dynamik, wenn Neuronenzahl, Synapsenzahl, Grad- und Gewichtsmuster sowie Stimulusplan kontrolliert gleich bleiben?
  relevance: Der kleine 5D-Test in EXP-GEN-0021 isolierte keinen dimensionsspezifischen Effekt.
  literature: []
  hypotheses:
  - H-5D-005-A
  evidence: []
  status: open
  answer:
    current: null
    confidence: none
    limitations: Der erste operationalisierte Test hält die Graphstruktur bewusst klein und identisch.
  created: '2026-09-05'
  updated: '2026-09-05'
- id: RQ-REG-002
  domain: Closed-loop Regulation
  question: Verbessert aktive Regulation Stabilität und Recovery eines laufenden SNN unter identischen Ressourcen- oder Sensorperturbationen gegenüber deaktivierter Regulation?
  relevance: EXP-GEN-0021 validierte Regulationszustände, aber noch keinen funktionalen Closed-loop-Nutzen.
  literature: []
  hypotheses:
  - H-REG-002-A
  evidence: []
  status: open
  answer:
    current: null
    confidence: none
    limitations: Der Feedbackpfad muss als technische Intervention und nicht als Emotion interpretiert werden.
  created: '2026-09-05'
  updated: '2026-09-05'
- id: RQ-TEMP-002
  domain: Temporal Learning
  question: Reagiert Brain-5D auf spike-tragende zeitliche Reihenfolge anders als auf umgekehrte oder simultane Kontrollfolgen?
  relevance: EXP-GEN-0021 zeigte Temporal-State-Diskrepanzen ohne Spike-Aktivität.
  literature: []
  hypotheses:
  - H-TEMP-002-A
  evidence: []
  status: open
  answer:
    current: null
    confidence: none
    limitations: Eine Reihenfolgenabhängigkeit ist zunächst nur eine dynamische Differenz, kein Gedächtnisnachweis.
  created: '2026-09-05'
  updated: '2026-09-05'
- id: RQ-PERF-001
  domain: Runtime Performance
  question: Welche Subsysteme dominieren die Wall-Time wissenschaftlicher Läufe und welche Optimierungen erhöhen den Durchsatz bei erhaltener deterministischer Äquivalenz?
  relevance: EXP-GEN-0021 zeigte eine große Differenz zwischen isoliertem Tick-Durchsatz und Suite-Laufzeit.
  literature: []
  hypotheses:
  - H-PERF-001-A
  evidence: []
  status: open
  answer:
    current: null
    confidence: none
    limitations: Performanceänderungen mit veränderter numerischer oder zeitlicher Semantik gelten als Protokolländerung.
  created: '2026-09-05'
  updated: '2026-09-05'
- id: RQ-REC-002
  domain: Recurrent Dynamics
  question: Wie verändern Loop-Delay und skalierte Rekurrenzstruktur Persistenzdauer, Inter-Spike-Dynamik und Extinktionsverhalten?
  relevance: Der Drei-Neuronen-Loop aus EXP-GEN-0021 reicht nicht für Skalierungsaussagen.
  literature: []
  hypotheses:
  - H-REC-002-A
  evidence: []
  status: open
  answer:
    current: null
    confidence: none
    limitations: Version 1 operationalisiert zunächst Loop-Delay als kontrollierten Skalierungsparameter.
  created: '2026-09-05'
  updated: '2026-09-05'
- id: RQ-LIFE-001
  domain: Lifelong Learning
  question: Bleibt zuvor erworbene Lernleistung bei sequenziellen Aufgaben erhalten oder entstehen messbare Interferenzeffekte?
  relevance: Das positive Single-Task-Learningsignal aus EXP-GEN-0021 motiviert Retentionstests.
  literature: []
  hypotheses:
  - H-LIFE-001-A
  evidence: []
  status: open
  answer:
    current: null
    confidence: none
    limitations: Der erste Runner ist ein Vorläufer-Screen; echte Catastrophic-Forgetting-Evidenz erfordert ein gemeinsames fortlaufend trainiertes Netzwerk.
  created: '2026-09-05'
  updated: '2026-09-05'
"""

HYPOTHESIS_APPEND = r"""

- id: H-REC-001-A
  research_question: RQ-REC-001
  hypothesis: Rekurrenzgewicht und Delay erzeugen reproduzierbare Übergänge zwischen sofortigem Erlöschen, transienter Aktivität und Aktivität bis zum Ende des registrierten Beobachtungsfensters.
  status: untested
  evidence: []
  created: '2026-09-05'
  updated: '2026-09-05'
- id: H-GEN-001-A
  research_question: RQ-GEN-001
  hypothesis: Learning-on verbessert die Erfolgsrate auf vorab registrierten Perturbationsproben gegenüber Learning-off und Sham-Replay.
  status: untested
  evidence: []
  created: '2026-09-05'
  updated: '2026-09-05'
- id: H-REPL-001-A
  research_question: RQ-REPL-001
  hypothesis: Der Rekurrenzbehandlungseffekt bleibt über mindestens 20 vorab registrierte Initialisierungsseeds in Richtung und Größenordnung konsistent.
  status: untested
  evidence: []
  created: '2026-09-05'
  updated: '2026-09-05'
- id: H-5D-005-A
  research_question: RQ-5D-005
  hypothesis: Mindestens eine registrierte Propagationsmetrik unterscheidet sich in 5D von topology-matched niedrigdimensionalen Einbettungen.
  status: untested
  evidence: []
  created: '2026-09-05'
  updated: '2026-09-05'
- id: H-REG-002-A
  research_question: RQ-REG-002
  hypothesis: Der registrierte Regulationsfeedbackpfad verbessert die Recovery-Metrik nach einer identischen Druckphase gegenüber Regulation-off.
  status: untested
  evidence: []
  created: '2026-09-05'
  updated: '2026-09-05'
- id: H-TEMP-002-A
  research_question: RQ-TEMP-002
  hypothesis: Forward-, Reverse- und Simultanfolgen erzeugen bei gleicher Ereignisanzahl unterscheidbare spike-basierte Antwortsignaturen.
  status: untested
  evidence: []
  created: '2026-09-05'
  updated: '2026-09-05'
- id: H-PERF-001-A
  research_question: RQ-PERF-001
  hypothesis: Der Core-Tick-Loop ist nicht der einzige dominante Kostenblock vollständiger Science-Läufe; mindestens ein zusätzlicher gemessener Subsystemanteil ist relevant.
  status: untested
  evidence: []
  created: '2026-09-05'
  updated: '2026-09-05'
- id: H-REC-002-A
  research_question: RQ-REC-002
  hypothesis: Größere rekurrente Delays verändern Persistenzdauer oder Propagation Depth gegenüber dem Delay-1-Kontrollarm.
  status: untested
  evidence: []
  created: '2026-09-05'
  updated: '2026-09-05'
- id: H-LIFE-001-A
  research_question: RQ-LIFE-001
  hypothesis: Sequenzielle Lernaufgaben zeigen eine messbare Veränderung der Retentions- oder Gewichtssignatur gegenüber einer Single-Task-Baseline.
  status: untested
  evidence: []
  created: '2026-09-05'
  updated: '2026-09-05'
"""


def append_once(path: Path, marker: str, payload: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker not in text:
        path.write_text(text.rstrip() + payload + "\n", encoding="utf-8")


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"Patch anchor not found in {path}: {old[:80]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def patch_assistant() -> None:
    path = ROOT / "src/research_assistant/assistant.py"
    old = """    def _data_for_manifest(\n        self, experiment_id: str, manifest: dict[str, Any]\n    ) -> dict[str, Any] | None:\n        path = _artifact_path(self._root, manifest, "data", experiment_id)\n        if path is None or not path.is_file():\n            return None\n        raw_data: Any = json.loads(path.read_text(encoding="utf-8"))\n        if isinstance(raw_data, list):\n            return {"runs": _compact_for_analysis(raw_data)}\n        if isinstance(raw_data, dict):\n            return cast(dict[str, Any], _compact_for_analysis(raw_data))\n        return None\n"""
    new = """    def _data_for_manifest(\n        self, experiment_id: str, manifest: dict[str, Any]\n    ) -> dict[str, Any] | None:\n        # DATA v2: never parse the potentially large raw run archive for normal AI\n        # interpretation. The deterministic writer produces a bounded packet first.\n        ai_packet = (\n            self._root / "experiments" / experiment_id / "analysis" / "ai_packet.json"\n        )\n        if ai_packet.is_file():\n            if ai_packet.stat().st_size > 1_000_000:\n                raise ValueError("AI packet exceeds the 1 MB research-assistant limit.")\n            raw_packet: Any = json.loads(ai_packet.read_text(encoding="utf-8"))\n            if not isinstance(raw_packet, dict):\n                raise ValueError("AI packet must be a JSON object.")\n            return cast(dict[str, Any], raw_packet)\n\n        # Legacy experiments retain the bounded fallback. New experiments must use\n        # analysis/ai_packet.json and therefore avoid loading 100+ MB runs.json.\n        path = _artifact_path(self._root, manifest, "data", experiment_id)\n        if path is None or not path.is_file():\n            return None\n        raw_data: Any = json.loads(path.read_text(encoding="utf-8"))\n        if isinstance(raw_data, list):\n            return {"runs": _compact_for_analysis(raw_data)}\n        if isinstance(raw_data, dict):\n            return cast(dict[str, Any], _compact_for_analysis(raw_data))\n        return None\n"""
    replace_once(path, old, new)


def patch_workflow() -> None:
    path = ROOT / "src/dashboard/experiment_workflow.py"
    replace_once(
        path,
        """from src.research.experiment_recorder import ExperimentRecorder\n""",
        """from src.research.data_v2 import prepare_research_data_v2\nfrom src.research.experiment_recorder import ExperimentRecorder\n""",
    )
    replace_once(
        path,
        """from src.research.registry import ResearchRegistry\n""",
        """from src.research.protocol_registry import (\n    PreregistrationError,\n    protocol_by_id,\n    protocol_catalog,\n    validate_operational_protocol,\n)\nfrom src.research.registry import ResearchRegistry\n""",
    )
    replace_once(
        path,
        """                    {\n                        "id": "stdp_pair_timing_v1",\n                        "label": "STDP Pair-Timing v1 (registriert)",\n                    },\n                ],\n""",
        """                    {\n                        "id": "stdp_pair_timing_v1",\n                        "label": "STDP Pair-Timing v1 (registriert)",\n                    },\n                    *protocol_catalog(self._research_root),\n                ],\n""",
    )
    replace_once(
        path,
        """        runner = getattr(experiment_suite, runner_name)\n        runtime_runner_digest, source_runner_digest = (\n            _assert_loaded_callable_matches_source(\n                runner, Path(experiment_suite.__file__).resolve(), runner_name\n            )\n        )\n""",
        """        if hasattr(experiment_suite, runner_name):\n            runner_module = experiment_suite\n        else:\n            from src.research import followup_experiments\n\n            runner_module = followup_experiments\n        runner = getattr(runner_module, runner_name)\n        runtime_runner_digest, source_runner_digest = (\n            _assert_loaded_callable_matches_source(\n                runner, Path(runner_module.__file__).resolve(), runner_name\n            )\n        )\n""",
    )
    replace_once(
        path,
        """            "run_temporal",\n        }\n""",
        """            "run_temporal",\n            "run_recurrence_map",\n            "run_replication",\n            "run_5d_matched",\n            "run_regulation_recovery",\n            "run_temporal_order",\n            "run_performance_profile",\n            "run_recurrence_scale",\n        }\n""",
    )
    replace_once(
        path,
        """        statistics_path = write_statistics_artifact(output_dir, serialized_runs)\n        trace_paths = _externalize_large_traces(output_dir, serialized_runs)\n        data_path.write_text(\n""",
        """        statistics_path = write_statistics_artifact(output_dir, serialized_runs)\n        statistics_payload = json.loads(statistics_path.read_text(encoding="utf-8"))\n        data_v2 = prepare_research_data_v2(\n            output_dir, serialized_runs, statistics_payload\n        )\n        trace_paths = list(data_v2.raw_paths)\n        data_path.write_text(\n""",
    )
    replace_once(
        path,
        """        recorder.record_artifact("data", "DATA/runs.json")\n        recorder.record_artifact("statistics", "analysis/statistics.json")\n""",
        """        recorder.record_artifact("data", "DATA/runs.json")\n        recorder.record_artifact("data_index", "DATA/runs_index.json")\n        recorder.record_artifact("ai_packet", "analysis/ai_packet.json")\n        recorder.record_artifact("ai_packet_digest", "analysis/ai_packet_digest.json")\n        recorder.record_artifact("statistics", "analysis/statistics.json")\n""",
    )
    replace_once(
        path,
        """            data_digest=_sha256_files([data_path, *trace_paths], output_dir),\n""",
        """            data_digest=_sha256_files(\n                [\n                    data_path,\n                    data_v2.raw_index_path,\n                    data_v2.ai_packet_path,\n                    data_v2.ai_packet_digest_path,\n                    *trace_paths,\n                ],\n                output_dir,\n            ),\n""",
    )
    replace_once(
        path,
        """        if trace_paths:\n            artifacts["raw_trace_index"] = "DATA/traces/index.json"\n""",
        """        artifacts["raw_run_index"] = "DATA/runs_index.json"\n        artifacts["current_run"] = "DATA/current_run.json"\n        artifacts["ai_packet"] = "analysis/ai_packet.json"\n        artifacts["ai_packet_digest"] = "analysis/ai_packet_digest.json"\n        operational_protocol = protocol_by_id(self._research_root, workflow.protocol)\n        if operational_protocol is not None:\n            artifacts["preregistration"] = str(operational_protocol["preregistration"])\n""",
    )
    replace_once(
        path,
        """            "statistics": f"experiments/{workflow.experiment_id}/analysis/statistics.json",\n""",
        """            "statistics": f"experiments/{workflow.experiment_id}/analysis/statistics.json",\n            "ai_packet": f"experiments/{workflow.experiment_id}/analysis/ai_packet.json",\n            "raw_run_index": f"experiments/{workflow.experiment_id}/DATA/runs_index.json",\n""",
    )
    replace_once(
        path,
        """    @staticmethod\n    def _science_runner(body: dict[str, object], workflow: ExperimentWorkflow) -> str:\n""",
        """    def _science_runner(self, body: dict[str, object], workflow: ExperimentWorkflow) -> str:\n""",
    )
    replace_once(
        path,
        """        protocol = str(body.get("protocol") or workflow.protocol)\n        question_id = workflow.question_id\n        if protocol == "science_all_v1":\n""",
        """        protocol = str(body.get("protocol") or workflow.protocol)\n        question_id = workflow.question_id\n        operational = protocol_by_id(self._research_root, protocol)\n        if operational is not None:\n            return str(operational["runner"])\n        if protocol == "science_all_v1":\n""",
    )
    replace_once(
        path,
        """        exact_window_runners = {"run_ping", "run_ping_v2", "run_5d", "run_temporal"}\n""",
        """        exact_window_runners = {\n            "run_ping",\n            "run_ping_v2",\n            "run_5d",\n            "run_temporal",\n            "run_recurrence_map",\n            "run_replication",\n            "run_5d_matched",\n            "run_regulation_recovery",\n            "run_temporal_order",\n            "run_performance_profile",\n            "run_recurrence_scale",\n        }\n""",
    )
    replace_once(
        path,
        """        if hypothesis is None or hypothesis.research_question != question.id:\n            raise WorkflowValidationError(\n                "The selected hypothesis does not belong to the research question."\n            )\n\n        return ExperimentWorkflow(\n""",
        """        if hypothesis is None or hypothesis.research_question != question.id:\n            raise WorkflowValidationError(\n                "The selected hypothesis does not belong to the research question."\n            )\n        if protocol_by_id(self._research_root, protocol) is not None:\n            try:\n                validate_operational_protocol(\n                    self._research_root,\n                    question_id=question_id,\n                    hypothesis_id=hypothesis_id,\n                    protocol_id=protocol,\n                    seed_count=len(seeds),\n                )\n            except PreregistrationError as exc:\n                raise WorkflowValidationError(str(exc)) from exc\n\n        return ExperimentWorkflow(\n""",
    )
    replace_once(
        path,
        """                "Rohdaten: `DATA/runs.json`",\n                "Deterministische deskriptive Statistik: `analysis/statistics.json`",\n""",
        """                "Kompakte Run-Projektion: `DATA/runs.json`",\n                "Unveränderlicher Rohdatenindex: `DATA/runs_index.json`",\n                "KI-Eingabepaket: `analysis/ai_packet.json` (hart begrenzt)",\n                "Deterministische deskriptive Statistik: `analysis/statistics.json`",\n""",
    )


def patch_summary_semantics() -> None:
    path = ROOT / "src/research/experiment_summary.py"
    anchor = """    if question_id.startswith("RQ-PING-"):\n"""
    addition = """    if question_id == "RQ-REC-001":\n        return classify(\n            any(item.startswith("w0_") for item in plain)\n            and any(item.startswith("w100_") or item.startswith("w125_") for item in plain),\n            "REC-001 erwartet eine registrierte Rekurrenz-Gewicht/Delay-Karte mit Nullkontrolle.",\n        )\n    if question_id == "RQ-REC-002":\n        return classify(\n            {"loop_delay_1", "loop_delay_2", "loop_delay_4", "loop_delay_8"}.issubset(plain),\n            "REC-002 erwartet die registrierte Loop-Delay-Leiter.",\n        )\n    if question_id == "RQ-GEN-001":\n        return classify(\n            any(item.startswith("learning_on_drive_") for item in plain)\n            and any(item.startswith("learning_off_drive_") for item in plain)\n            and any(item.startswith("sham_replay_drive_") for item in plain),\n            "GEN-001 erwartet Learning-on, Learning-off und Sham-Replay über registrierte Perturbationsproben.",\n        )\n    if question_id == "RQ-REPL-001":\n        return classify(\n            {"recurrence_off", "recurrence_on"}.issubset(plain),\n            "REPL-001 erwartet beide Rekurrenzarme mit unabhängiger Seedstrategie.",\n        )\n    if question_id == "RQ-5D-005":\n        return classify(\n            {"1d", "2d", "3d", "5d"}.issubset(plain),\n            "5D-005 erwartet topology-matched 1D/2D/3D/5D-Einbettungen.",\n        )\n    if question_id == "RQ-REG-002":\n        return classify(\n            {"regulation_off", "regulation_on"}.issubset(plain),\n            "REG-002 erwartet Regulation-off und Regulation-on unter gleichem Perturbationsplan.",\n        )\n    if question_id == "RQ-TEMP-002":\n        return classify(\n            {"forward", "reverse", "simultaneous"}.issubset(plain),\n            "TEMP-002 erwartet Forward-, Reverse- und Simultankontrolle.",\n        )\n    if question_id == "RQ-PERF-001":\n        return classify(\n            "subsystem_profile" in plain,\n            "PERF-001 erwartet subsystemaufgelöste Runtime-Messungen.",\n        )\n    if question_id == "RQ-LIFE-001":\n        return classify(\n            "sequential_three_task_screen" in plain,\n            "LEARN-INTERF-001 v1 ist ein explizit als Vorläufer markierter Interferenz-Screen.",\n        )\n"""
    replace_once(path, anchor, addition + anchor)


def main() -> None:
    append_once(
        ROOT / "research/registry/questions.yaml", "- id: RQ-REC-001", QUESTION_APPEND
    )
    append_once(
        ROOT / "research/registry/hypotheses.yaml",
        "- id: H-REC-001-A",
        HYPOTHESIS_APPEND,
    )
    patch_assistant()
    patch_workflow()
    patch_summary_semantics()


if __name__ == "__main__":
    main()
