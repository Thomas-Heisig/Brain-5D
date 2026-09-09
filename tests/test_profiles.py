from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import pytest

from src.profiles import (
    ProfileError,
    ProfileService,
    ProfileValidationError,
)


def test_create_digest_revision_lineage_and_snapshot_binding(tmp_path: Path) -> None:
    service = ProfileService(tmp_path / "profiles")
    profile = service.create(name="Wesen Alpha")
    assert profile["profile_id"] == "WESEN-0001"
    assert profile["provenance"]["profile_digest"]
    assert profile["gateway"]["productive_gateway_lock"] is True
    assert profile["provenance"]["autonomous_profile_mutation"]["enabled"] is False

    updated = service.update(
        "WESEN-0001",
        {"name": "Wesen Alpha v2", "resources": {"max_neurons": 5000}},
        reason="test_update",
    )
    assert updated["revision"] == 2
    assert (
        updated["provenance"]["profile_digest"]
        != profile["provenance"]["profile_digest"]
    )
    assert len(updated["provenance"]["history"]) == 1

    clone = service.clone("WESEN-0001", name="Wesen Beta")
    assert clone["profile_id"] == "WESEN-0002"
    assert clone["parent_profile_id"] == "WESEN-0001"
    assert clone["snapshot_binding"] is None

    snapshot = tmp_path / "latest.b5d"
    snapshot.write_bytes(b"snapshot")
    bound = service.save_state("WESEN-0001", snapshot)
    assert bound["snapshot_binding"]["digest"]
    assert service.history("WESEN-0001")["current_revision"] == 3
    loaded = service.load("WESEN-0001", with_state=True)
    assert loaded["mode"] == "profile_with_state"

    service.update("WESEN-0001", {"learning": {"stdp": {"enabled": True}}})
    with pytest.raises(ProfileError, match="compatible snapshot"):
        service.load("WESEN-0001", with_state=True)


def test_profile_load_modes_and_safe_archive_delete(tmp_path: Path) -> None:
    service = ProfileService(tmp_path / "profiles")
    service.create(name="Disposable")
    assert service.load("WESEN-0001")["mode"] == "profile_only"
    with pytest.raises(ProfileError, match="no compatible snapshot"):
        service.load("WESEN-0001", with_state=True)
    archived = service.archive("WESEN-0001")
    assert archived["status"] == "archived"
    with pytest.raises(ProfileError, match="archived"):
        service.load("WESEN-0001")

    service.create(name="With provenance")
    snapshot = tmp_path / "state.b5d"
    snapshot.write_bytes(b"state")
    service.save_state("WESEN-0002", snapshot)
    with pytest.raises(ProfileError, match="provenance"):
        service.delete("WESEN-0002")


def test_profile_schema_and_security_boundaries(tmp_path: Path) -> None:
    service = ProfileService(tmp_path / "profiles")
    profile = service.create()
    invalid = json.loads(json.dumps(profile))
    invalid["gateway"]["productive_gateway_lock"] = False
    with pytest.raises(ProfileValidationError):
        service.update("WESEN-0001", {"gateway": invalid["gateway"]})

    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as zipped:
        zipped.writestr("manifest.json", "{}")
        zipped.writestr("../escape.json", "bad")
    with pytest.raises(ProfileValidationError, match="unsafe"):
        service.import_zip(archive.getvalue(), profile_id="WESEN-0002")


def test_profile_export_import_roundtrip(tmp_path: Path) -> None:
    source = ProfileService(tmp_path / "source")
    source.create(name="Exported")
    exported = source.export_zip("WESEN-0001")
    target = ProfileService(tmp_path / "target")
    imported = target.import_zip(exported, profile_id="WESEN-0007")
    assert imported["profile_id"] == "WESEN-0007"
    assert target.get("WESEN-0007")["name"] == "Exported"
