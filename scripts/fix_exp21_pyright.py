"""One-time strict-Pyright cleanup for the EXP-GEN-0021 branch."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"Patch anchor not found in {path}: {old[:120]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def patch_learning_lab() -> None:
    path = ROOT / "src/experiments/learning_lab.py"
    anchor = "\ndef run_learning_experiment(\n"
    wrappers = '''\ndef train_learning_weights(\n    config: Config, condition: str\n) -> tuple[tuple[float, ...], LearningEngine, TrialPartitions]:\n    \"\"\"Public deterministic training boundary for registered research protocols.\"\"\"\n    return _train(config, condition)\n\n\ndef probe_learning_response(\n    config: Config, weights: Sequence[float]\n) -> tuple[bool, float, int | None]:\n    \"\"\"Public deterministic post-training probe boundary.\"\"\"\n    return _probe_response(config, weights)\n\n'''
    replace(path, anchor, wrappers + anchor)


def patch_followup() -> None:
    path = ROOT / "src/research/followup_experiments.py"
    replace(
        path,
        '''from src.experiments.learning_lab import (\n    _probe_response,\n    _train,\n    run_learning_experiment,\n)''',
        '''from src.experiments.learning_lab import (\n    probe_learning_response,\n    run_learning_experiment,\n    train_learning_weights,\n)''',
    )
    text = path.read_text(encoding="utf-8")
    text = text.replace("_train(values, condition)", "train_learning_weights(values, condition)")
    text = text.replace(
        "_probe_response(\n                    probe_config, initial_weights\n                )",
        "probe_learning_response(\n                    probe_config, initial_weights\n                )",
    )
    text = text.replace(
        "_probe_response(\n                    probe_config, trained_weights\n                )",
        "probe_learning_response(\n                    probe_config, trained_weights\n                )",
    )
    text = text.replace(
        '''                    if isinstance(uncertainty, (int, float)):\n                        current *= max(0.5, 1.0 - 0.25 * float(uncertainty))''',
        '''                    current *= max(0.5, 1.0 - 0.25 * float(uncertainty))''',
    )
    path.write_text(text, encoding="utf-8")


def patch_workflow() -> None:
    path = ROOT / "src/dashboard/experiment_workflow.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace("import gzip\n", "")
    text = text.replace("import re\n", "")
    text = text.replace(
        '''    PreregistrationError,\n    protocol_by_id,''',
        '''    OPERATIONAL_RUNNERS,\n    PreregistrationError,\n    protocol_by_id,''',
    )
    text = text.replace(
        '''        runner_source = runner_module.__file__\n        if runner_source is None:\n            raise WorkflowValidationError(\n                f"Cannot resolve source path for runner module {runner_module.__name__}."\n            )''',
        '''        runner_source_value = getattr(runner_module, "__file__", None)\n        if not isinstance(runner_source_value, str):\n            raise WorkflowValidationError(\n                f"Cannot resolve source path for runner module {runner_module.__name__}."\n            )\n        runner_source = runner_source_value''',
    )
    text = text.replace(
        '''    def _science_runner(\n        self, body: dict[str, object], workflow: ExperimentWorkflow\n    ) -> str:''',
        '''    @staticmethod\n    def _science_runner(\n        body: dict[str, object], workflow: ExperimentWorkflow\n    ) -> str:''',
    )
    text = text.replace(
        '''        operational = protocol_by_id(self._research_root, protocol)\n        if operational is not None:\n            return str(operational["runner"])''',
        '''        operational_runner = OPERATIONAL_RUNNERS.get(protocol)\n        if operational_runner is not None:\n            return operational_runner''',
    )
    start = text.find("\ndef _safe_trace_name(")
    end = text.find("\ndef _sha256_files(", start)
    if start == -1 or end == -1:
        raise RuntimeError("Could not find obsolete trace helper block")
    text = text[:start] + text[end:]
    path.write_text(text, encoding="utf-8")


def patch_tests() -> None:
    path = ROOT / "tests/test_exp21_followup_runners.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace("from typing import Any\n", "from typing import Any, cast\n")
    text = text.replace("    return loaded\n", "    return cast(dict[str, Any], loaded)\n")
    path.write_text(text, encoding="utf-8")

    path = ROOT / "tests/test_exp21_operational_protocols.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "from pathlib import Path\n", "from pathlib import Path\nfrom typing import Any, cast\n"
    )
    text = text.replace(
        '''    payload = yaml.safe_load(path.read_text(encoding="utf-8"))\n    assert isinstance(payload, list)\n    return {str(item["id"]) for item in payload if isinstance(item, dict)}''',
        '''    payload_value: object = yaml.safe_load(path.read_text(encoding="utf-8"))\n    assert isinstance(payload_value, list)\n    payload = cast(list[object], payload_value)\n    ids: set[str] = set()\n    for item_value in payload:\n        if not isinstance(item_value, dict):\n            continue\n        item = cast(dict[str, Any], item_value)\n        ids.add(str(item["id"]))\n    return ids''',
    )
    path.write_text(text, encoding="utf-8")

    path = ROOT / "tests/test_research_assistant.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace("from typing import", "from typing import cast,", 1) if "from typing import" in text and "cast" not in text.split("\n", 20)[0:20] else text
    old = '''    projected = packet.data["runs"] if packet.data is not None else None\n    assert isinstance(projected, dict)\n    assert projected["_analysis_projection"] == "truncated_sequence"\n    assert projected["item_count"] == 300\n    assert len(projected["head"]) == 8\n    assert len(projected["tail"]) == 8'''
    new = '''    projected_value: object = packet.data["runs"] if packet.data is not None else None\n    assert isinstance(projected_value, dict)\n    projected = cast(dict[str, object], projected_value)\n    assert projected["_analysis_projection"] == "truncated_sequence"\n    assert projected["item_count"] == 300\n    head_value = projected["head"]\n    tail_value = projected["tail"]\n    assert isinstance(head_value, list)\n    assert isinstance(tail_value, list)\n    head = cast(list[object], head_value)\n    tail = cast(list[object], tail_value)\n    assert len(head) == 8\n    assert len(tail) == 8'''
    if old not in text:
        raise RuntimeError("Research assistant test anchor not found")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> None:
    patch_learning_lab()
    patch_followup()
    patch_workflow()
    patch_tests()


if __name__ == "__main__":
    main()
