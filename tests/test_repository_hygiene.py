"""Regression coverage for immutable publications and reproducible installs."""

import hashlib
import json
import re
import tomllib
from pathlib import Path
from typing import Any, cast

import yaml

from src.dashboard.file_rendering import file_is_read_only
from src.dashboard.research_source import ResearchSource
from src.dashboard.verification import compute_source_tree_digest

ROOT = Path(__file__).resolve().parents[1]


def test_install_metadata_does_not_change_source_identity(tmp_path: Path) -> None:
    source = tmp_path / "src"
    source.mkdir()
    module = source / "example.py"
    module.write_text("value = 1\n")
    before = compute_source_tree_digest(tmp_path)
    assert before is not None
    metadata = source / "brain5d_core.egg-info"
    metadata.mkdir()
    (metadata / "PKG-INFO").write_text("generated install metadata")
    assert compute_source_tree_digest(tmp_path) == before
    module.write_text("value = 2\n")
    assert compute_source_tree_digest(tmp_path) != before


def test_frozen_records_are_not_reformatted() -> None:
    config = cast(
        dict[str, Any], yaml.safe_load((ROOT / ".pre-commit-config.yaml").read_text())
    )
    hooks = {hook["id"]: hook for repo in config["repos"] for hook in repo["hooks"]}
    for name in ("trailing-whitespace", "end-of-file-fixer"):
        pattern = hooks[name]["exclude"]
        assert re.search(pattern, "research/preregistrations/PREREG-SNN-001.json")
        assert re.search(pattern, "research/publications/integrity.json")
        assert not re.search(pattern, "src/dashboard/file_rendering.py")


def test_wheel_preserves_import_namespace_and_assets() -> None:
    config = tomllib.loads((ROOT / "pyproject.toml").read_text())
    discovery = config["tool"]["setuptools"]["packages"]["find"]
    assert discovery["where"] == ["."]
    assert discovery["include"] == ["src", "src.*"]
    assets = config["tool"]["setuptools"]["package-data"]["src.dashboard"]
    assert "static/*" in assets and "static/**/*" in assets


def test_complete_publication_is_byte_exact_and_discoverable() -> None:
    root = ROOT / "research/publications"
    manifest = json.loads((root / "integrity.json").read_text())
    package = root / manifest["package"]
    assert len(manifest["files"]) == manifest["file_count"] == 41
    for item in manifest["files"]:
        data = (package / item["path"]).read_bytes()
        assert len(data) == item["size"], item["path"]
        assert hashlib.sha256(data).hexdigest() == item["sha256"], item["path"]
    item = manifest["archive"]
    data = (root / item["path"]).read_bytes()
    assert len(data) == item["size"]
    assert hashlib.sha256(data).hexdigest() == item["sha256"]
    docs = ResearchSource(ROOT / "research").list_documents()
    assert any(d.path.endswith("wissenschaftliche_abhandlung.md") for d in docs)
    assert file_is_read_only(
        "research", "publications/" + manifest["package"] + "/literatur.bib"
    )
    assert manifest["automatic_evidence_promotion"] is False
