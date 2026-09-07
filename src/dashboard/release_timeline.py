"""Build the operator-facing release timeline from canonical project docs."""

from __future__ import annotations

import json
import re
from pathlib import Path

_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")
_DATED_TITLE_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})(?:\s+[\u2014-]\s*|\s+)(?P<title>.+)$"
)
_BULLET_RE = re.compile(r"^-\s+(?:(?:\[(?P<checked>[ xX])\])\s+)?(?P<text>.+)$")
_SOURCE_SPECS = (
    ("TODO", "docs/08-roadmap/TODO.md"),
    ("ROADMAP", "docs/08-roadmap/ROADMAP.md"),
    ("CHANGELOG", "docs/07-changelog/CHANGELOG.md"),
)


def _parse_document(path: Path, source: str) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    current: dict[str, object] | None = None

    def flush() -> None:
        if current is not None:
            entries.append(current.copy())

    for line in path.read_text(encoding="utf-8").splitlines():
        heading = _HEADING_RE.match(line)
        if heading:
            flush()
            heading_text = heading.group(1).strip()
            dated = _DATED_TITLE_RE.match(heading_text)
            current = {
                "date": dated.group("date") if dated else None,
                "title": dated.group("title").strip() if dated else heading_text,
                "source": source,
                "items": [],
            }
            continue

        if current is None:
            continue
        bullet = _BULLET_RE.match(line.strip())
        if not bullet:
            continue
        items = current["items"]
        if not isinstance(items, list):
            continue
        checked = bullet.group("checked")
        items.append(
            {
                "text": bullet.group("text").strip(),
                "done": None if checked is None else checked.lower() == "x",
            }
        )

    flush()
    return entries


def _release_entries(repo_root: Path) -> list[dict[str, object]]:
    releases_dir = repo_root / "releases"
    if not releases_dir.is_dir():
        return []

    entries: list[dict[str, object]] = []
    for path in sorted(releases_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(data, dict):
            continue

        version = str(data.get("version") or path.stem)
        title = str(data.get("title") or "Release")
        status = str(data.get("status") or "unknown")
        items: list[dict[str, object]] = []
        scope = data.get("scope")
        if isinstance(scope, list):
            items.extend({"text": str(item), "done": status == "released"} for item in scope)
        for field in ("subtitle", "note"):
            value = data.get(field)
            if isinstance(value, str) and value:
                items.append({"text": value, "done": status == "released"})

        entries.append(
            {
                "date": data.get("date") if isinstance(data.get("date"), str) else None,
                "title": f"{version} · {title}",
                "sources": ["RELEASE"],
                "items": items,
                "phase": "current" if status == "development" else "past",
            }
        )
    return entries


def _entry_phase(entry: dict[str, object], as_of: str) -> str:
    explicit_phase = entry.get("phase")
    if explicit_phase in {"past", "current", "future"}:
        return str(explicit_phase)

    date = entry.get("date")
    if not isinstance(date, str) or not date:
        title = str(entry.get("title") or "")
        return "current" if title == "Current engineering baseline" else "future"
    if date > as_of:
        return "future"
    if date < as_of:
        return "past"

    sources = entry.get("sources")
    source_names = set(sources) if isinstance(sources, list) else set()
    if "TODO" not in source_names:
        return "past"

    items = entry.get("items")
    checks = (
        [item for item in items if isinstance(item, dict) and isinstance(item.get("done"), bool)]
        if isinstance(items, list)
        else []
    )
    return "current" if any(item.get("done") is False for item in checks) else "past"


def build_release_timeline(repo_root: Path) -> dict[str, object]:
    """Return merged timeline entries and their document provenance.

    Matching date/title sections are merged so the same release milestone
    documented in ROADMAP and CHANGELOG appears once with both sources.
    """

    sources: list[dict[str, object]] = []
    merged: dict[tuple[str, str], dict[str, object]] = {}

    for source, relative_path in _SOURCE_SPECS:
        path = repo_root / relative_path
        available = path.is_file()
        sources.append({"name": source, "path": relative_path, "available": available})
        if not available:
            continue

        for entry in _parse_document(path, source):
            date = str(entry["date"] or "")
            title = str(entry["title"])
            key = (date, re.sub(r"\s+", " ", title).casefold())
            existing = merged.get(key)
            if existing is None:
                existing = {
                    "date": entry["date"],
                    "title": title,
                    "sources": [source],
                    "items": [],
                }
                merged[key] = existing
            else:
                existing_sources = existing["sources"]
                if isinstance(existing_sources, list) and source not in existing_sources:
                    existing_sources.append(source)

            existing_items = existing["items"]
            entry_items = entry["items"]
            if not isinstance(existing_items, list) or not isinstance(entry_items, list):
                continue
            for item in entry_items:
                if not isinstance(item, dict):
                    continue
                item_text = str(item.get("text", ""))
                matching = next(
                    (
                        candidate
                        for candidate in existing_items
                        if isinstance(candidate, dict) and candidate.get("text") == item_text
                    ),
                    None,
                )
                if matching is None:
                    existing_items.append(dict(item))
                elif item.get("done") is True:
                    matching["done"] = True

    release_source = repo_root / "releases"
    sources.append({"name": "RELEASE", "path": "releases/", "available": release_source.is_dir()})
    for entry in _release_entries(repo_root):
        key = (str(entry.get("date") or ""), str(entry.get("title") or "").casefold())
        merged[key] = entry

    dated_entries = [
        str(entry["date"])
        for entry in merged.values()
        if isinstance(entry.get("date"), str) and entry["date"]
    ]
    as_of = max(dated_entries) if dated_entries else ""
    for entry in merged.values():
        entry["phase"] = _entry_phase(entry, as_of)

    entries = sorted(
        merged.values(),
        key=lambda entry: (str(entry.get("date") or ""), str(entry.get("title") or "")),
        reverse=True,
    )
    return {"entries": entries, "sources": sources, "as_of": as_of}