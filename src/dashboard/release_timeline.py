"""Build the operator-facing release timeline from canonical project docs."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any, NotRequired, TypedDict, cast

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


class TimelineItem(TypedDict):
    """A documented milestone, not an inferred scientific finding."""

    text: str
    done: bool | None


class TimelineEntry(TypedDict):
    """A release milestone with explicit document provenance."""

    date: str | None
    title: str
    sources: list[str]
    items: list[TimelineItem]
    phase: NotRequired[str]


class TimelineSource(TypedDict):
    """Availability of a canonical timeline document."""

    name: str
    path: str
    available: bool


class ReleaseTimeline(TypedDict):
    """JSON-serializable release timeline API response."""

    entries: list[TimelineEntry]
    sources: list[TimelineSource]
    as_of: str


def _parse_document(path: Path, source: str) -> list[TimelineEntry]:
    entries: list[TimelineEntry] = []
    current: TimelineEntry | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        heading = _HEADING_RE.match(line)
        if heading:
            if current is not None:
                entries.append(current)
            heading_text = heading.group(1).strip()
            dated = _DATED_TITLE_RE.match(heading_text)
            current = {
                "date": dated.group("date") if dated else None,
                "title": dated.group("title").strip() if dated else heading_text,
                "sources": [source],
                "items": [],
            }
        elif current is not None and (bullet := _BULLET_RE.match(line.strip())):
            checked = bullet.group("checked")
            current["items"].append(
                {
                    "text": bullet.group("text").strip(),
                    "done": None if checked is None else checked.lower() == "x",
                }
            )
    if current is not None:
        entries.append(current)
    return entries


def _release_entries(repo_root: Path) -> list[TimelineEntry]:
    releases_dir = repo_root / "releases"
    if not releases_dir.is_dir():
        return []
    entries: list[TimelineEntry] = []
    known_versions: set[str] = set()
    for path in sorted(releases_dir.glob("*.json")):
        try:
            raw: object = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(raw, dict):
            continue
        data = cast(dict[str, Any], raw)
        version = str(data.get("version") or path.stem)
        known_versions.add(version)
        title = str(data.get("title") or "Release")
        status = str(data.get("status") or "unknown")
        items: list[TimelineItem] = []
        scope: object = data.get("scope")
        if isinstance(scope, list):
            items.extend(
                {"text": str(item), "done": status == "released"}
                for item in cast(list[object], scope)
            )
        for field in ("subtitle", "note"):
            value: object = data.get(field)
            if isinstance(value, str) and value:
                items.append({"text": value, "done": status == "released"})
        date: object = data.get("date")
        entries.append(
            {
                "date": date if isinstance(date, str) else None,
                "title": f"{version} \u00b7 {title}",
                "sources": ["RELEASE"],
                "items": items,
                "phase": "current" if status == "development" else "past",
            }
        )
    try:
        tags = subprocess.run(
            [
                "git",
                "for-each-ref",
                "refs/tags",
                "--format=%(refname:short)|%(objectname:short)|%(creatordate:short)",
            ],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        tags = None
    if tags is not None and tags.returncode == 0:
        for line in tags.stdout.splitlines():
            tag, commit, date = (line.split("|", 2) + ["", "", ""])[:3]
            version = tag.removeprefix("brain5d-core-").removeprefix("v")
            if version in known_versions or not version.startswith("0."):
                continue
            entries.append(
                {
                    "date": date or None,
                    "title": f"{version} \u00b7 Historical tagged release",
                    "sources": ["RELEASE"],
                    "items": [
                        {"text": f"Tag {tag} \u00b7 commit {commit}", "done": True}
                    ],
                    "phase": "past",
                }
            )
            known_versions.add(version)
    return entries


def _entry_phase(entry: TimelineEntry, as_of: str) -> str:
    explicit_phase = entry.get("phase")
    if explicit_phase in {"past", "current", "future"}:
        return str(explicit_phase)
    date = entry["date"]
    if not date:
        return (
            "current" if entry["title"] == "Current engineering baseline" else "future"
        )
    if date > as_of:
        return "future"
    if date < as_of or "TODO" not in entry["sources"]:
        return "past"
    return (
        "current" if any(item["done"] is False for item in entry["items"]) else "past"
    )


def build_release_timeline(repo_root: Path) -> ReleaseTimeline:
    """Merge matching date/title sections without losing source provenance."""
    sources: list[TimelineSource] = []
    merged: dict[tuple[str, str], TimelineEntry] = {}
    for source, relative_path in _SOURCE_SPECS:
        path = repo_root / relative_path
        sources.append(
            {"name": source, "path": relative_path, "available": path.is_file()}
        )
        if not path.is_file():
            continue
        for entry in _parse_document(path, source):
            key = (entry["date"] or "", re.sub(r"\s+", " ", entry["title"]).casefold())
            existing = merged.get(key)
            if existing is None:
                merged[key] = entry
                continue
            if source not in existing["sources"]:
                existing["sources"].append(source)
            for item in entry["items"]:
                matching = next(
                    (
                        candidate
                        for candidate in existing["items"]
                        if candidate["text"] == item["text"]
                    ),
                    None,
                )
                if matching is None:
                    existing["items"].append(item.copy())
                elif item["done"] is True:
                    matching["done"] = True
    sources.append(
        {
            "name": "RELEASE",
            "path": "releases/",
            "available": (repo_root / "releases").is_dir(),
        }
    )
    for entry in _release_entries(repo_root):
        merged[(entry["date"] or "", entry["title"].casefold())] = entry
    as_of = max((entry["date"] or "" for entry in merged.values()), default="")
    for entry in merged.values():
        entry["phase"] = _entry_phase(entry, as_of)
    entries = sorted(
        merged.values(),
        key=lambda entry: (entry["date"] or "", entry["title"]),
        reverse=True,
    )
    return {"entries": entries, "sources": sources, "as_of": as_of}
