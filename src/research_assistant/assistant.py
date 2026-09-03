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
        data = self._data_for_manifest(manifest)
        statistics_path = (
            self._root / "experiments" / experiment_id / "analysis" / "statistics.json"
        )
        if data is not None and statistics_path.is_file():
            data = dict(data)
            data["statistics"] = self._read_json(
                str(statistics_path.relative_to(self._root))
            )
        evidence = self._evidence_for_experiment(experiment_id)
        protocol = self._protocol_for_manifest(manifest)
        previous_analyses = self._previous_analyses(experiment_id)
        manifest_path = self._root / "experiments" / experiment_id / "manifest.json"
        manifest_digest = _file_digest(manifest_path)
        config_path = str(
            cast(dict[str, Any], manifest.get("config", {})).get(
                "path", "NOT_AVAILABLE"
            )
        )
        config_file = (
            self._root.parent / config_path
            if config_path.startswith("research/")
            else None
        )
        data_path = _artifact_path(self._root.parent, manifest, "data")
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
        directory = self._root / "analysis"
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

    def _data_for_manifest(self, manifest: dict[str, Any]) -> dict[str, Any] | None:
        artifacts_raw = manifest.get("artifacts", {})
        if not isinstance(artifacts_raw, dict):
            return None
        artifacts = cast(dict[str, Any], artifacts_raw)
        path = artifacts.get("data")
        if not isinstance(path, str) or not path.startswith("research/"):
            return None
        return self._read_json(path.removeprefix("research/"))

    def _protocol_for_manifest(self, manifest: dict[str, Any]) -> dict[str, Any] | None:
        config = manifest.get("config", {})
        if not isinstance(config, dict):
            return None
        path = cast(dict[str, Any], config).get("path")
        if not isinstance(path, str) or not path.startswith("research/"):
            return None
        try:
            return self._read_json(path.removeprefix("research/"))
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
        directory = self._root / "analysis"
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
        return (
            f"Role: {role}\nInterpret this ResearchPacket. Separate observation from interpretation. "
            "Do not issue commands, decide evidence, claims, or research-question answers. "
            "Return JSON only with assessment, observations, methodological_concerns, "
            "alternative_explanations, recommended_experiments, confidence, requested_evidence.\n"
            f"Packet: {packet.to_json()}"
        )


def _file_digest(path: Path | None) -> str:
    if path is None or not path.is_file():
        return "NOT_AVAILABLE"
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact_path(root: Path, manifest: dict[str, Any], name: str) -> Path | None:
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        return None
    artifact_map = cast(dict[str, Any], artifacts)
    value = artifact_map.get(name)
    if not isinstance(value, str) or not value.startswith("research/"):
        return None
    return root / value


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
