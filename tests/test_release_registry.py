"""Release registry consistency and historical boundary tests."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[1]


def _release(name: str) -> dict[str, Any]:
    return cast(
        dict[str, Any],
        json.loads((ROOT / "releases" / name).read_text(encoding="utf-8")),
    )


def test_current_release_matches_canonical_alpha7_version() -> None:
    with (ROOT / "pyproject.toml").open("rb") as stream:
        project = tomllib.load(stream)["project"]
    current = _release("current.json")

    assert project["version"] == "0.5.0a7"
    assert current["version"] == "0.5.0-alpha.7"
    assert current["pep440"] == project["version"]
    assert current["status"] == "development"
    assert current["parent"] == "v0.5.0-alpha.6"


def test_alpha6_release_preserves_verified_historical_boundary() -> None:
    release = _release("v0.5.0-alpha.6.json")

    assert release["status"] == "released"
    assert release["tag"] == "v0.5.0-alpha.6"
    assert release["source_freeze"] == ("3025e681a5f46bfd8dc2e5dbb8e1474fa5132cd1")
    assert release["evidence_commit"] == ("70a4ee253a5fc30716d0ffe0058f146a1ad59cde")
    assert release["closure_commit"] == ("8fac75da723b4b9d28383dd4ec49497771f4572f")
    assert release["baseline"] == {
        "python": "3.13.14",
        "passed": 489,
        "failed": 0,
        "skipped": 5,
        "collection_errors": 0,
        "command": "python -m pytest tests/ -q --tb=short",
        "artifact": "tests/test_baseline.json",
    }
    assert [run["run"] for run in release["continuous_integration"]] == [
        145,
        147,
        148,
    ]
    assert release["gate_summary"]["scientific_gate"] == "passed"
    assert release["gate_summary"]["release_readiness"] == "ready"
