from pathlib import Path

path = Path("src/dashboard/review_inbox.py")
text = path.read_text(encoding="utf-8")
text = text.replace("from typing import Any\n", "from typing import Any, cast\n")
text = text.replace(
    "    return value if isinstance(value, dict) else None\n",
    "    return cast(dict[str, Any], value) if isinstance(value, dict) else None\n",
)
text = text.replace(
    '        content = report.get("content") if isinstance(report.get("content"), dict) else {}\n',
    '        content_value = report.get("content")\n        content = cast(dict[str, Any], content_value) if isinstance(content_value, dict) else {}\n',
)
text = text.replace(
    '                "summary": content.get("executive_summary") if isinstance(content, dict) else None,\n',
    '                "summary": content.get("executive_summary"),\n',
)
path.write_text(text, encoding="utf-8")
