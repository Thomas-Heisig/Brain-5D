from pathlib import Path

summary = Path("src/research/experiment_summary.py")
text = summary.read_text(encoding="utf-8")
text = text.replace(
    "            values: list[float] = []\n            for run in condition_runs:\n",
    "            nested_values: list[float] = []\n            for run in condition_runs:\n",
)
text = text.replace(
    "                    values.append(value)\n            if values:\n                metric_stats[name] = _stats(values)\n",
    "                    nested_values.append(value)\n            if nested_values:\n                metric_stats[name] = _stats(nested_values)\n",
)
summary.write_text(text, encoding="utf-8")

workflow = Path("src/dashboard/experiment_workflow.py")
text = workflow.read_text(encoding="utf-8")
if "from types import CodeType" not in text:
    text = text.replace(
        "from time import perf_counter\n",
        "from time import perf_counter\nfrom types import CodeType\n",
        1,
    )
text = text.replace(
    "def _find_named_code(code: object, name: str) -> object | None:\n    if not hasattr(code, \"co_consts\"):\n        return None\n    if getattr(code, \"co_name\", None) == name:\n        return code\n    for value in code.co_consts:\n",
    "def _find_named_code(code: CodeType, name: str) -> CodeType | None:\n    if code.co_name == name:\n        return code\n    for value in code.co_consts:\n",
)
raw_recursion = (
    "    for value in code.co_consts:\n"
    "        found = _find_named_code(value, name)\n"
    "        if found is not None:\n"
    "            return found\n"
)
typed_recursion = (
    "    for value in code.co_consts:\n"
    "        if not isinstance(value, CodeType):\n"
    "            continue\n"
    "        found = _find_named_code(value, name)\n"
    "        if found is not None:\n"
    "            return found\n"
)
if raw_recursion in text:
    text = text.replace(raw_recursion, typed_recursion, 1)
duplicate_recursion = (
    "    for value in code.co_consts:\n"
    "        if not isinstance(value, CodeType):\n"
    "            continue\n"
    "        if not isinstance(value, CodeType):\n"
    "            continue\n"
    "        found = _find_named_code(value, name)\n"
)
text = text.replace(
    duplicate_recursion,
    "    for value in code.co_consts:\n"
    "        if not isinstance(value, CodeType):\n"
    "            continue\n"
    "        found = _find_named_code(value, name)\n",
)
text = text.replace(
    "def _code_digest(code: object) -> str:\n",
    "def _code_digest(code: CodeType) -> str:\n",
)
old_variants = [
    "        comparisons = metrics.get(\"comparisons\")\n        if not isinstance(comparisons, list) or len(comparisons) <= threshold:\n            continue\n",
    "        comparison_value: object = metrics.get(\"comparisons\")\n        if not isinstance(comparison_value, list) or len(comparison_value) <= threshold:\n            continue\n        comparisons: list[object] = list(comparison_value)\n",
    "        metrics_raw: object = run.get(\"metrics\")\n        if not isinstance(metrics_raw, dict):\n            continue\n        metrics = cast(dict[str, object], metrics_raw)\n        comparison_value: object = metrics.get(\"comparisons\")\n        if not isinstance(comparison_value, list) or len(comparison_value) <= threshold:\n            continue\n        comparisons = cast(list[object], comparison_value)\n",
]
new = "        metrics_raw: object = run.get(\"metrics\")\n        if not isinstance(metrics_raw, dict):\n            continue\n        metrics = cast(dict[str, object], metrics_raw)\n        comparison_value: object = metrics.get(\"comparisons\")\n        if not isinstance(comparison_value, list):\n            continue\n        comparisons = cast(list[object], comparison_value)\n        if len(comparisons) <= threshold:\n            continue\n"
for old in old_variants:
    if old in text:
        text = text.replace(old, new, 1)
        break
text = text.replace(
    "        metrics = run.get(\"metrics\")\n        if not isinstance(metrics, dict):\n            continue\n        metrics_raw: object = run.get(\"metrics\")\n",
    "        metrics_raw: object = run.get(\"metrics\")\n",
)
text = text.replace(
    "data_digest=_sha256_files([data_path, *trace_paths]),",
    "data_digest=_sha256_files([data_path, *trace_paths], output_dir),",
)
old_digest = '''def _sha256_files(paths: Sequence[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.as_posix()):
        digest.update(
            path.relative_to(path.parent.parent.parent).as_posix().encode("utf-8")
        )
        digest.update(b"\\0")
        digest.update(path.read_bytes())
        digest.update(b"\\0")
    return digest.hexdigest()
'''
new_digest = '''def _sha256_files(paths: Sequence[Path], root: Path) -> str:
    """Hash a set of artifacts using experiment-relative names for portability."""
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.relative_to(root).as_posix()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\\0")
        digest.update(path.read_bytes())
        digest.update(b"\\0")
    return digest.hexdigest()
'''
if old_digest in text:
    text = text.replace(old_digest, new_digest, 1)
workflow.write_text(text, encoding="utf-8")
