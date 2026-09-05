"""One-time type cleanup for the EXP-GEN-0021 operationalization branch."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"Patch anchor not found in {path}: {old!r}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def main() -> None:
    data_v2 = ROOT / "src/research/data_v2.py"
    replace(
        data_v2,
        "for index, run in enumerate(tuple(runs)):",
        "for run_index, run in enumerate(tuple(runs)):",
    )
    replace(
        data_v2,
        'f"run-{index:04d}-{condition}-seed-{seed}.json.gz"',
        'f"run-{run_index:04d}-{condition}-seed-{seed}.json.gz"',
    )
    replace(data_v2, '"run_index": index,', '"run_index": run_index,')
    replace(data_v2, '"last_archived_run": index,', '"last_archived_run": run_index,')

    followup = ROOT / "src/research/followup_experiments.py"
    replace(
        followup,
        "tuple(size - 1 for size in dimensions),  # type: ignore[arg-type]",
        "(dimensions[0] - 1, dimensions[1] - 1, dimensions[2] - 1, dimensions[3] - 1, dimensions[4] - 1),",
    )
    replace(followup, "    readings = {", "    readings: dict[str, dict[str, Any]] = {")

    workflow = ROOT / "src/dashboard/experiment_workflow.py"
    replace(workflow, "from types import CodeType", "from types import CodeType, ModuleType")
    replace(
        workflow,
        "            runner_module = experiment_suite",
        "            runner_module: ModuleType = experiment_suite",
    )
    replace(
        workflow,
        "        runner = getattr(runner_module, runner_name)\n        runtime_runner_digest, source_runner_digest = (\n            _assert_loaded_callable_matches_source(\n                runner, Path(runner_module.__file__).resolve(), runner_name\n            )\n        )",
        "        runner = getattr(runner_module, runner_name)\n        runner_source = runner_module.__file__\n        if runner_source is None:\n            raise WorkflowValidationError(\n                f\"Cannot resolve source path for runner module {runner_module.__name__}.\"\n            )\n        runtime_runner_digest, source_runner_digest = (\n            _assert_loaded_callable_matches_source(\n                runner, Path(runner_source).resolve(), runner_name\n            )\n        )",
    )


if __name__ == "__main__":
    main()
