"""Read-only research assistant orchestration."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

import yaml

from .models import AIAnalysisRecord, ResearchPacket

AnalysisBackend = Callable[[str], tuple[dict[str, Any], dict[str, str | float]]]


class ResearchAssistant:
    """Build packets and persist interpretations without scientific authority."""

    def __init__(self, research_root: Path) -> None:
        self._root = research_root.resolve()

    def build_packet(self, experiment_id: str) -> ResearchPacket:
        manifest = self._read_json(f"experiments/{experiment_id}/manifest.json")
        questions = self._read_yaml("registry/questions.yaml")
        hypotheses = self._read_yaml("registry/hypotheses.yaml")
        claims = self._read_yaml("registry/claims.yaml")
        question_id = _one_str(manifest, "research_questions")
        question = _by_id(questions, question_id)
        hypothesis_ids = _string_list(manifest, "hypotheses")
        data = self._data_for_manifest(experiment_id, manifest)
        statistics_path = (
            self._root / "experiments" / experiment_id / "analysis" / "statistics.json"
        )
        if data is not None and statistics_path.is_file():
            data = dict(data)
            data["statistics"] = self._read_json(
                str(statistics_path.relative_to(self._root))
            )
        evidence = self._evidence_for_experiment(experiment_id)
        protocol = self._protocol_for_manifest(experiment_id, manifest)
        previous_analyses = self._previous_analyses(experiment_id)
        manifest_path = self._root / "experiments" / experiment_id / "manifest.json"
        manifest_digest = _file_digest(manifest_path)
        config_path = str(
            cast(dict[str, Any], manifest.get("config", {})).get(
                "path", "NOT_AVAILABLE"
            )
        )
        config_file = _config_path(self._root, config_path)
        data_path = _artifact_path(self._root, manifest, "data", experiment_id)
        return ResearchPacket(
            experiment_id=experiment_id,
            research_question=question,
            hypotheses=[
                item for item in hypotheses if item.get("id") in hypothesis_ids
            ],
            claims=[
                item for item in claims if item.get("research_question") == question_id
            ],
            manifest=manifest,
            data=data,
            evidence=evidence,
            literature_sources=self._literature_for_question(question),
            protocol=protocol,
            known_limitations=self._limitations(manifest, evidence),
            previous_analyses=previous_analyses,
            provenance={
                "git_commit": str(
                    cast(dict[str, Any], manifest.get("git", {})).get(
                        "commit", "unknown"
                    )
                ),
                "experiment_status": str(manifest.get("experiment_status", "unknown")),
                "evidence_mode": str(manifest.get("evidence_mode", "not_reported")),
                "git_dirty": str(
                    cast(dict[str, Any], manifest.get("git", {})).get(
                        "dirty", "NOT_AVAILABLE"
                    )
                ),
                "source_freeze_sha": str(
                    manifest.get("source_freeze_sha", "NOT_AVAILABLE")
                ),
                "configuration_path": config_path,
                "configuration_sha256": (
                    _file_digest(config_file) if config_file else "NOT_AVAILABLE"
                ),
                "experiment_manifest_digest": manifest_digest,
                "data_ids": str(manifest.get("data_ids", "NOT_AVAILABLE")),
                "evid_ids": str(manifest.get("evid_ids", "NOT_AVAILABLE")),
                "protocol_id": str(manifest.get("protocol_id", "NOT_AVAILABLE")),
                "protocol_digest": _json_digest(protocol),
                "data_digest": _file_digest(data_path),
                "evid_digests": str(
                    [_file_digest(path) for path in self._evidence_paths(experiment_id)]
                ),
            },
        )

    def analyze(
        self, experiment_id: str, role: str, backend: AnalysisBackend
    ) -> AIAnalysisRecord:
        if role not in {
            "research_planner",
            "scientific_analyst",
            "critical_reviewer",
            "scientific_writer",
        }:
            raise ValueError(f"Unsupported assistant role: {role}")
        packet = self.build_packet(experiment_id)
        prompt = self._prompt(role, packet)
        output, model = backend(prompt)
        record = AIAnalysisRecord.create(
            role=role, model=model, packet=packet, output=output, prompt=prompt
        )
        directory = self._root / "experiments" / experiment_id / "analysis"
        directory.mkdir(exist_ok=True)
        path = directory / f"{record.analysis_id}.json"
        if path.exists():
            raise FileExistsError(
                f"Analysis record already exists: {record.analysis_id}"
            )
        path.write_text(
            json.dumps(record.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return record

    def _data_for_manifest(
        self, experiment_id: str, manifest: dict[str, Any]
    ) -> dict[str, Any] | None:
        path = _artifact_path(self._root, manifest, "data", experiment_id)
        if path is None or not path.is_file():
            return None
        raw_data: Any = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw_data, list):
            return {"runs": raw_data}
        return cast(dict[str, Any], raw_data) if isinstance(raw_data, dict) else None

    def _protocol_for_manifest(
        self, experiment_id: str, manifest: dict[str, Any]
    ) -> dict[str, Any] | None:
        path = _artifact_path(self._root, manifest, "workflow", experiment_id)
        if path is None or not path.is_file():
            return None
        try:
            raw_protocol: Any = json.loads(path.read_text(encoding="utf-8"))
            return (
                cast(dict[str, Any], raw_protocol)
                if isinstance(raw_protocol, dict)
                else None
            )
        except (FileNotFoundError, ValueError, json.JSONDecodeError):
            return None

    def _evidence_for_experiment(self, experiment_id: str) -> list[dict[str, Any]]:
        directory = self._root / "registry" / "evidence"
        if not directory.is_dir():
            return []
        records: list[dict[str, Any]] = []
        for path in sorted(directory.glob("EVID-*.json")):
            record = self._read_json(str(path.relative_to(self._root)))
            if record.get("experiment_id") == experiment_id:
                records.append(record)
        return records

    def _evidence_paths(self, experiment_id: str) -> list[Path]:
        directory = self._root / "registry" / "evidence"
        if not directory.is_dir():
            return []
        return [
            path
            for path in sorted(directory.glob("EVID-*.json"))
            if self._read_json(str(path.relative_to(self._root))).get("experiment_id")
            == experiment_id
        ]

    def _literature_for_question(
        self, question: dict[str, Any]
    ) -> list[dict[str, Any]]:
        source_ids = _string_list(question, "literature")
        try:
            sources = self._read_yaml("registry/sources.yaml")
        except FileNotFoundError:
            return []
        return [source for source in sources if source.get("source_id") in source_ids]

    def _previous_analyses(self, experiment_id: str) -> list[dict[str, Any]]:
        directory = self._root / "experiments" / experiment_id / "analysis"
        if not directory.is_dir():
            return []
        return [
            record
            for path in sorted(directory.glob("AIAR-*.json"))
            for record in [self._read_json(str(path.relative_to(self._root)))]
            if cast(dict[str, Any], record.get("inputs", {})).get("experiment_id")
            == experiment_id
        ]

    @staticmethod
    def _limitations(
        manifest: dict[str, Any], evidence: list[dict[str, Any]]
    ) -> list[str]:
        limitations: list[str] = []
        git = manifest.get("git", {})
        if (
            not isinstance(git, dict)
            or cast(dict[str, Any], git).get("dirty") is not False
        ):
            limitations.append("Git provenance is dirty or unavailable.")
        if manifest.get("experiment_status") != "completed":
            limitations.append("Experiment is not a completed valid scientific run.")
        if not evidence:
            limitations.append(
                "No registered scientific evidence is linked to this experiment."
            )
        return limitations

    def _read_json(self, relative_path: str) -> dict[str, Any]:
        raw_data: Any = json.loads(
            self._safe_path(relative_path).read_text(encoding="utf-8")
        )
        if not isinstance(raw_data, dict):
            raise ValueError(
                f"Research artifact must be a JSON object: {relative_path}"
            )
        return cast(dict[str, Any], raw_data)

    def _read_yaml(self, relative_path: str) -> list[dict[str, Any]]:
        raw_data: Any = yaml.safe_load(
            self._safe_path(relative_path).read_text(encoding="utf-8")
        )
        if not isinstance(raw_data, list):
            return []
        entries = cast(list[object], raw_data)
        return [
            cast(dict[str, Any], item) for item in entries if isinstance(item, dict)
        ]

    def _safe_path(self, relative_path: str) -> Path:
        if Path(relative_path).parts and Path(relative_path).parts[0] == "benchmarks":
            raise PermissionError("Research assistants cannot access benchmark labels.")
        path = (self._root / relative_path).resolve()
        if (
            ".." in Path(relative_path).parts
            or not path.is_file()
            or self._root not in path.parents
        ):
            raise FileNotFoundError(f"Research artifact not found: {relative_path}")
        return path

    @staticmethod
    def _prompt(role: str, packet: ResearchPacket) -> str:
        common = (
            "Interpret only the supplied ResearchPacket. Separate direct observation, derived quantity, statistical inference and interpretation. "
            "Never call an effect significant, statistically robust, causal, confirmed or disproven unless the packet contains an explicit statistical test or a design that supports that exact claim. "
            "Before interpretation, verify semantic consistency between research question, hypothesis, protocol, conditions and measured metrics. If they do not match, state this as the primary methodological finding and do not pretend the experiment answers the registered question. "
            "Do not infer biological meaning from engineering metrics unless their operational definition is supplied. Distinguish deterministic replication from statistically independent samples. "
            "Report exact numerical results whenever available, including n, seeds, ticks, condition-wise values, absolute differences, ratios and timing. Include equations in plain LaTeX strings for every derived metric and define each symbol. "
            "State missing definitions, missing controls, missing variance/statistics, provenance limitations and alternative explanations explicitly. "
            "Do not issue commands, decide evidence, approve claims, or answer a research question with scientific authority."
        )
        writer = (
            " For role scientific_writer, produce a detailed publication-style synthesis rather than a short abstract. The assessment must cover: objective; registered RQ and hypothesis; design; data basis; operational definitions; formulas; exact quantitative results; seed-by-seed reproducibility; effect sizes or descriptive ratios only when mathematically justified; spike timing/ISI where present; state-digest interpretation limits; methodological critique; competing explanations; what the run does and does not show; and concrete follow-up experiments. "
            "Use cautious language. A repeated identical deterministic sequence across seeds is reproducibility of the observed output, not evidence of independent replication. If RQ/H and protocol mismatch, label the report as semantically mismatched and explain the correct scope of the experiment."
            if role == "scientific_writer"
            else ""
        )
        reviewer = (
            " For role critical_reviewer, actively search for RQ/hypothesis/protocol mismatches, pseudo-replication, undefined metrics, unjustified causal language, missing statistical tests, impossible effect claims and inconsistencies between raw metrics and narrative."
            if role == "critical_reviewer"
            else ""
        )
        return (
            f"Role: {role}\n{common}{writer}{reviewer}\n"
            "Return JSON only with assessment, observations, methodological_concerns, alternative_explanations, recommended_experiments, confidence, requested_evidence. "
            "Observations should contain exact values and formulas where possible.\n"
            f"Packet: {packet.to_json()}"
        )


def _file_digest(path: Path | None) -> str:
    if path is None or not path.is_file():
        return "NOT_AVAILABLE"
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact_path(
    root: Path, manifest: dict[str, Any], name: str, experiment_id: str
) -> Path | None:
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        return None
    artifact_map = cast(dict[str, Any], artifacts)
    value = artifact_map.get(name)
    if not isinstance(value, str):
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    if value.startswith("research/"):
        return root / value.removeprefix("research/")
    return root / "experiments" / experiment_id / value


def _config_path(root: Path, value: str) -> Path | None:
    if not value or value == "NOT_AVAILABLE":
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    if value.startswith("research/"):
        return root / value.removeprefix("research/")
    return root.parent / value


def _json_digest(value: dict[str, Any] | None) -> str:
    if value is None:
        return "NOT_AVAILABLE"
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def _one_str(data: dict[str, Any], key: str) -> str:
    values = _string_list(data, key)
    if len(values) != 1:
        raise ValueError(f"Expected exactly one {key} link.")
    return values[0]


def _string_list(data: dict[str, Any], key: str) -> list[str]:
    value = data.get(key, [])
    if not isinstance(value, list):
        return []
    values = cast(list[object], value)
    return [item for item in values if isinstance(item, str)]


def _by_id(items: list[dict[str, Any]], item_id: str) -> dict[str, Any]:
    for item in items:
        if item.get("id") == item_id:
            return item
    raise ValueError(f"Research registry entry not found: {item_id}")
