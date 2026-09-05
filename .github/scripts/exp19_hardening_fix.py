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
text = text.replace(
    "        found = _find_named_code(value, name)\n        if found is not None:\n            return found\n",
    "        if not isinstance(value, CodeType):\n            continue\n        found = _find_named_code(value, name)\n        if found is not None:\n            return found\n",
    1,
)
text = text.replace(
    "def _code_digest(code: object) -> str:\n",
    "def _code_digest(code: CodeType) -> str:\n",
)
workflow.write_text(text, encoding="utf-8")
