"""Read-only research assistant orchestration."""

from __future__ import annotations

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

    def _read_json(self, relative_path: str) -> dict[str, Any]:
        raw_data: Any = json.loads(
            self._safe_path(relative_path).read_text(encoding="utf-8")
        )
        if not isinstance(raw_data, dict):
            raise ValueError(f"Research artifact must be a JSON object: {relative_path}")
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
