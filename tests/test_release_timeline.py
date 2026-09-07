"""Tests for the documentation-backed release timeline."""

from pathlib import Path

from src.dashboard.release_timeline import build_release_timeline


ROOT = Path(__file__).resolve().parents[1]


def test_release_timeline_reads_all_canonical_sources() -> None:
    payload = build_release_timeline(ROOT)

    assert [source["name"] for source in payload["sources"]] == [
        "TODO",
        "ROADMAP",
        "CHANGELOG",
        "RELEASE",
    ]
    assert all(source["available"] for source in payload["sources"])
    assert payload["entries"]
    assert {entry["phase"] for entry in payload["entries"]} == {
        "past",
        "current",
        "future",
    }
    assert any(entry["title"] == "0.1.0 · Historical tagged release" for entry in payload["entries"])


def test_release_timeline_merges_same_milestone_and_keeps_checklist_state() -> None:
    payload = build_release_timeline(ROOT)
    matching = [
        entry
        for entry in payload["entries"]
        if entry["title"] == "Full-stack dashboard E2E verification"
    ]

    assert len(matching) == 1
    entry = matching[0]
    assert entry["date"] == "2026-09-07"
    assert entry["sources"] == ["ROADMAP", "CHANGELOG"]
    assert any(
        any(item["done"] is True for item in timeline_entry["items"])
        for timeline_entry in payload["entries"]
    )