"""Bounded, versioned and reproducible technical Wesen profiles.

Profiles describe configuration and identity. Large mutable neural state stays
in the existing snapshot/checkpoint formats and is referenced by digest only.
This module never activates sensors, actuators, gateways or autonomous profile
mutation.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import zipfile
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, cast

PROFILE_SCHEMA_VERSION = 1
MAX_PROFILE_BYTES = 256 * 1024
MAX_IMPORT_BYTES = 8 * 1024 * 1024
MAX_IMPORT_FILES = 64
PROFILE_ID_PREFIX = "WESEN-"


class ProfileError(ValueError):
    """Base error for profile operations."""


class ProfileValidationError(ProfileError):
    """Raised when profile data violates the canonical schema."""


class ProfileCompatibilityError(ProfileError):
    """Raised when a profile cannot be used by the current runtime."""


class ProfileNotFoundError(ProfileError):
    """Raised when a profile identifier is not registered."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def _digest(profile: Mapping[str, Any]) -> str:
    value = json.loads(json.dumps(profile))
    provenance = value.get("provenance")
    if isinstance(provenance, dict):
        provenance.pop("profile_digest", None)
    return hashlib.sha256(_canonical(cast(dict[str, Any], value))).hexdigest()


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _safe_id(value: object) -> str:
    if not isinstance(value, str) or not value.startswith(PROFILE_ID_PREFIX):
        raise ProfileValidationError("profile_id must use the WESEN-* convention")
    suffix = value[len(PROFILE_ID_PREFIX) :]
    if not suffix.isdigit() or len(suffix) != 4:
        raise ProfileValidationError("profile_id must look like WESEN-0001")
    return value


def _mapping(value: object, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ProfileValidationError(f"{field} must be an object")
    return cast(dict[str, Any], value)


def _list(value: object, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise ProfileValidationError(f"{field} must be an array")
    return value


def _default_profile(profile_id: str, name: str) -> dict[str, Any]:
    timestamp = _now()
    profile: dict[str, Any] = {
        "schema_version": PROFILE_SCHEMA_VERSION,
        "profile_id": profile_id,
        "name": name,
        "created_at": timestamp,
        "updated_at": timestamp,
        "parent_profile_id": None,
        "revision": 1,
        "status": "inactive",
        "runtime": {
            "mode": "operator",
            "target_hz": None,
            "runtime_version": "0.6.0a1",
            "implementation_status": "implemented",
        },
        "neural_core": {
            "neuron_model": "Izhikevich",
            "neuron_count_target": None,
            "neuron_count_limit": None,
            "topology_rules": {},
            "spatial_dimensions": [5],
            "delays": {},
            "neuron_parameters": {},
            "connectivity_rules": {},
            "structural_plasticity": {"enabled": False},
            "initialization_strategy": "runtime_config",
        },
        "learning": {
            "stdp": {"enabled": False},
            "three_factor": {"enabled": False},
            "eligibility": {"enabled": False},
            "homeostasis": {"enabled": False},
            "structural_plasticity": {"enabled": False},
            "pruning": {"enabled": False},
            "growth": {"enabled": False},
            "reward_modulation": {"enabled": False},
            "learning_rates": {},
            "adaptation_limits": {},
            "consolidation": {"enabled": False},
        },
        "senses": {
            "items": [],
            "implementation_status": "declared_only",
            "interoceptive_signals": [
                "cpu_load",
                "gpu_load",
                "temperature",
                "memory_pressure",
                "queue_pressure",
                "storage_pressure",
                "network_connectivity",
            ],
        },
        "actuators": {"items": [], "implementation_status": "declared_only"},
        "morphology": {
            "type": "graph",
            "nodes": [],
            "joints": [],
            "segments": [],
            "sensors": [],
            "actuators": [],
            "fixed_endpoints": [],
            "constraints": [],
            "load_limits": {},
            "overload_signals": [],
            "implementation_status": "declared_only",
        },
        "gateway": {
            "registered_areas": [],
            "modality_mappings": [],
            "defaults": {},
            "allowed_pathways": [],
            "experiment_only": True,
            "productive_gateway_lock": True,
            "active_weights_in_profile": False,
        },
        "memory": {
            "episodic": {
                "enabled": False,
                "implementation_status": "implemented_optional",
            },
            "semantic": {"enabled": False, "implementation_status": "planned"},
            "working": {
                "enabled": True,
                "implementation_status": "implemented_optional",
            },
        },
        "self_model": {
            "enabled": False,
            "body_representation": {},
            "internal_state_sources": [],
            "action_attribution": {"enabled": False},
            "identity_persistence": {"enabled": True},
            "confidence_parameters": {},
            "scientific_boundary": "self_model_is_not_consciousness",
        },
        "resources": {
            "max_neurons": None,
            "max_synapses": None,
            "cpu_budget": None,
            "gpu_budget": None,
            "ram_budget_bytes": None,
            "storage_budget_bytes": None,
            "target_hz": None,
            "max_hz": None,
            "thermal_limits": {},
            "gateway_bandwidth": {},
            "telemetry_budget": {},
        },
        "safety": {
            "allowed_sensors": [],
            "allowed_actuators": [],
            "network_policy": "deny_by_default",
            "filesystem_policy": "read_only",
            "external_actions": False,
            "gateway_restrictions": {"experiment_only": True},
            "experiment_only_restrictions": True,
            "emergency_stop": True,
            "resource_ceilings": {},
        },
        "provenance": {
            "source": "profile_service",
            "runtime_version": "0.6.0a1",
            "profile_digest": None,
            "latest_snapshot": None,
            "history": [],
            "autonomous_profile_mutation": {"enabled": False, "status": "locked"},
        },
        "snapshot_binding": None,
        "compatibility": {
            "min_runtime": "0.6.0",
            "max_runtime": "0.x",
            "schema_version": PROFILE_SCHEMA_VERSION,
        },
    }
    profile["provenance"]["profile_digest"] = _digest(profile)
    return profile


def validate_profile(
    value: object, *, runtime_version: str = "0.6.0a1"
) -> dict[str, Any]:
    profile = _mapping(value, "profile")
    required = {
        "schema_version",
        "profile_id",
        "name",
        "created_at",
        "updated_at",
        "parent_profile_id",
        "revision",
        "status",
        "runtime",
        "neural_core",
        "learning",
        "senses",
        "actuators",
        "morphology",
        "gateway",
        "memory",
        "self_model",
        "resources",
        "safety",
        "provenance",
        "snapshot_binding",
        "compatibility",
    }
    missing = sorted(required - profile.keys())
    if missing:
        raise ProfileValidationError(f"profile is missing fields: {', '.join(missing)}")
    unknown = sorted(set(profile) - required)
    if unknown:
        raise ProfileValidationError(
            f"profile has unknown fields: {', '.join(unknown)}"
        )
    if profile["schema_version"] != PROFILE_SCHEMA_VERSION:
        raise ProfileValidationError("unsupported profile schema_version")
    _safe_id(profile["profile_id"])
    if not isinstance(profile["name"], str) or not profile["name"].strip():
        raise ProfileValidationError("name must be a non-empty string")
    if (
        isinstance(profile["revision"], bool)
        or not isinstance(profile["revision"], int)
        or profile["revision"] < 1
    ):
        raise ProfileValidationError("revision must be a positive integer")
    if profile["status"] not in {
        "active",
        "inactive",
        "archived",
        "incompatible",
        "corrupted",
    }:
        raise ProfileValidationError("invalid profile status")
    for section in required - {
        "schema_version",
        "profile_id",
        "name",
        "created_at",
        "updated_at",
        "parent_profile_id",
        "revision",
        "status",
        "snapshot_binding",
    }:
        _mapping(profile[section], section)
    gateway = _mapping(profile["gateway"], "gateway")
    if (
        gateway.get("productive_gateway_lock") is not True
        or gateway.get("experiment_only") is not True
    ):
        raise ProfileValidationError(
            "gateway productive lock and experiment-only boundary are required"
        )
    if gateway.get("active_weights_in_profile") is not False:
        raise ProfileValidationError(
            "active gateway weights must remain outside profile.json"
        )
    safety = _mapping(profile["safety"], "safety")
    if (
        safety.get("experiment_only_restrictions") is not True
        or safety.get("emergency_stop") is not True
    ):
        raise ProfileValidationError(
            "safety restrictions cannot be disabled by a profile"
        )
    mutation = _mapping(profile["provenance"], "provenance").get(
        "autonomous_profile_mutation"
    )
    if not isinstance(mutation, dict) or mutation.get("enabled") is not False:
        raise ProfileValidationError("autonomous profile mutation is locked")
    compatibility = _mapping(profile["compatibility"], "compatibility")
    if compatibility.get("schema_version") != PROFILE_SCHEMA_VERSION:
        raise ProfileValidationError("compatibility schema version mismatch")
    (
        _mapping(profile["snapshot_binding"], "snapshot_binding")
        if profile["snapshot_binding"] is not None
        else None
    )
    if _digest(profile) != _mapping(profile["provenance"], "provenance").get(
        "profile_digest"
    ):
        raise ProfileValidationError("profile digest mismatch")
    if str(compatibility.get("min_runtime", "0")) > runtime_version:
        raise ProfileCompatibilityError("profile requires a newer runtime")
    return profile


class ProfileService:
    """Manage bounded profile metadata under one controlled root."""

    def __init__(
        self, root: Path = Path("profiles"), *, runtime_version: str = "0.6.0a1"
    ) -> None:
        self.root = root.resolve()
        self.runtime_version = runtime_version
        self.index_path = self.root / "index.json"
        self._active_profile_id: str | None = None

    def _profile_dir(self, profile_id: str) -> Path:
        _safe_id(profile_id)
        candidate = (self.root / profile_id).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise ProfileError("profile path escapes root") from exc
        return candidate

    def _profile_path(self, profile_id: str) -> Path:
        return self._profile_dir(profile_id) / "profile.json"

    def _read_index(self) -> dict[str, Any]:
        if not self.index_path.is_file():
            return {"schema_version": 1, "profiles": []}
        try:
            value = json.loads(self.index_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ProfileError("profile registry is corrupted") from exc
        data = _mapping(value, "profile registry")
        if data.get("schema_version") != 1 or not isinstance(
            data.get("profiles"), list
        ):
            raise ProfileError("profile registry schema is invalid")
        return data

    def _write_index(self, entries: list[dict[str, Any]]) -> None:
        payload = {"schema_version": 1, "profiles": entries}
        _atomic_write(
            self.index_path,
            (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        )

    def _entry(self, profile: Mapping[str, Any]) -> dict[str, Any]:
        provenance = _mapping(profile["provenance"], "provenance")
        binding = profile.get("snapshot_binding")
        return {
            "profile_id": profile["profile_id"],
            "name": profile["name"],
            "version": profile["revision"],
            "created_at": profile["created_at"],
            "updated_at": profile["updated_at"],
            "parent": profile["parent_profile_id"],
            "status": profile["status"],
            "latest_snapshot": (
                binding.get("path") if isinstance(binding, dict) else None
            ),
            "compatibility": profile["compatibility"],
            "digest": provenance["profile_digest"],
        }

    def _next_id(self) -> str:
        used = {
            str(item.get("profile_id"))
            for item in self._read_index()["profiles"]
            if isinstance(item, dict)
        }
        number = 1
        while f"{PROFILE_ID_PREFIX}{number:04d}" in used:
            number += 1
        return f"{PROFILE_ID_PREFIX}{number:04d}"

    def list_profiles(self) -> dict[str, Any]:
        entries = self._read_index()["profiles"]
        active_profile_id = self._active_profile_id or next(
            (
                item.get("profile_id")
                for item in entries
                if isinstance(item, dict) and item.get("status") == "active"
            ),
            None,
        )
        return {
            "profiles": entries,
            "count": len(entries),
            "active_profile_id": active_profile_id,
            "maturity_level": self._maturity(entries),
            "scientific_boundary": "technical_identity_is_not_psychological_or_conscious_identity",
        }

    def current(self) -> dict[str, Any] | None:
        profile_id = self._active_profile_id
        if profile_id is None:
            active = next(
                (
                    item.get("profile_id")
                    for item in self._read_index()["profiles"]
                    if isinstance(item, dict) and item.get("status") == "active"
                ),
                None,
            )
            profile_id = active if isinstance(active, str) else None
        return self.get(profile_id) if profile_id is not None else None

    def _maturity(self, entries: list[Any]) -> int:
        """Derive maturity from persisted profile capabilities and lineage."""
        if not entries:
            return 0
        level = 1
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(
                entry.get("profile_id"), str
            ):
                continue
            try:
                profile = self.get(cast(str, entry["profile_id"]))
            except ProfileError:
                continue
            level = max(level, 2)
            if int(profile["revision"]) > 1:
                level = max(level, 4)
            if profile.get("snapshot_binding") is not None:
                level = max(level, 5)
            if all(
                profile.get(section) is not None
                for section in ("senses", "actuators", "morphology")
            ):
                level = max(level, 6)
            if all(
                profile.get(section) is not None
                for section in ("gateway", "memory", "self_model")
            ):
                level = max(level, 7)
            if profile.get("parent_profile_id") is not None:
                level = max(level, 8)
        return level

    def get(self, profile_id: str) -> dict[str, Any]:
        path = self._profile_path(profile_id)
        if not path.is_file():
            raise ProfileNotFoundError(f"profile not found: {profile_id}")
        if path.stat().st_size > MAX_PROFILE_BYTES:
            raise ProfileValidationError("profile exceeds bounded size")
        try:
            profile = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ProfileValidationError(f"profile is corrupted: {profile_id}") from exc
        return validate_profile(profile, runtime_version=self.runtime_version)

    def create(
        self,
        payload: Mapping[str, Any] | None = None,
        *,
        profile_id: str | None = None,
        name: str | None = None,
        parent_profile_id: str | None = None,
    ) -> dict[str, Any]:
        data = dict(payload or {})
        selected_id = (
            profile_id
            or cast(str | None, data.pop("profile_id", None))
            or self._next_id()
        )
        selected_name = (
            name
            or cast(str | None, data.pop("name", None))
            or f"MHRN Wesen {selected_id.removeprefix(PROFILE_ID_PREFIX)}"
        )
        if any(
            str(item.get("profile_id")) == selected_id
            for item in self._read_index()["profiles"]
            if isinstance(item, dict)
        ):
            raise ProfileError(f"profile already exists: {selected_id}")
        profile = _default_profile(_safe_id(selected_id), selected_name)
        if parent_profile_id is not None:
            self.get(parent_profile_id)
        profile["parent_profile_id"] = parent_profile_id
        for key, value in data.items():
            if key not in profile:
                raise ProfileValidationError(f"unknown profile field: {key}")
            profile[key] = value
        if parent_profile_id is not None:
            profile["parent_profile_id"] = parent_profile_id
        profile["updated_at"] = _now()
        profile["provenance"]["profile_digest"] = _digest(profile)
        profile = validate_profile(profile, runtime_version=self.runtime_version)
        self._write_profile(profile)
        return profile

    def update(
        self,
        profile_id: str,
        changes: Mapping[str, Any],
        *,
        reason: str = "profile_update",
    ) -> dict[str, Any]:
        profile = self.get(profile_id)
        if profile["status"] == "archived":
            raise ProfileError("archived profiles cannot be updated")
        if (
            changes.get("status") == "archived"
            and self._active_profile_id == profile_id
        ):
            raise ProfileError(
                "active profile cannot be archived; switch identity first"
            )
        revision = int(profile["revision"]) + 1
        previous_digest = cast(
            str, _mapping(profile["provenance"], "provenance")["profile_digest"]
        )
        for key, value in changes.items():
            if key in {"profile_id", "created_at", "revision", "provenance"}:
                raise ProfileValidationError(f"immutable profile field: {key}")
            if key not in profile:
                raise ProfileValidationError(f"unknown profile field: {key}")
            profile[key] = value
        profile["revision"] = revision
        profile["updated_at"] = _now()
        profile["provenance"].setdefault("history", []).append(
            {
                "revision": revision,
                "previous_digest": previous_digest,
                "reason": reason,
                "timestamp": profile["updated_at"],
            }
        )
        profile["provenance"]["profile_digest"] = _digest(profile)
        validated = validate_profile(profile, runtime_version=self.runtime_version)
        self._write_profile(validated)
        return validated

    def _write_profile(self, profile: Mapping[str, Any]) -> None:
        profile_id = cast(str, profile["profile_id"])
        path = self._profile_path(profile_id)
        revisions = path.parent / "revisions"
        revisions.mkdir(parents=True, exist_ok=True)
        revision_path = revisions / f"rev-{int(profile['revision']):04d}.json"
        encoded = (json.dumps(profile, indent=2, sort_keys=True) + "\n").encode("utf-8")
        if len(encoded) > MAX_PROFILE_BYTES:
            raise ProfileValidationError("profile exceeds bounded size")
        _atomic_write(revision_path, encoded)
        _atomic_write(path, encoded)
        entries = [
            item
            for item in self._read_index()["profiles"]
            if isinstance(item, dict) and item.get("profile_id") != profile_id
        ]
        entries.append(self._entry(profile))
        self._write_index(sorted(entries, key=lambda item: str(item["profile_id"])))

    def clone(
        self,
        profile_id: str,
        *,
        name: str | None = None,
        profile_id_new: str | None = None,
    ) -> dict[str, Any]:
        source = self.get(profile_id)
        cloned = json.loads(json.dumps(source))
        cloned.pop("profile_id", None)
        cloned.pop("created_at", None)
        cloned.pop("updated_at", None)
        cloned.pop("revision", None)
        cloned.pop("status", None)
        cloned["name"] = name or f"{source['name']} clone"
        cloned["status"] = "inactive"
        cloned["snapshot_binding"] = None
        cloned["gateway"]["active_weights_in_profile"] = False
        return self.create(
            cloned, profile_id=profile_id_new, parent_profile_id=profile_id
        )

    def load(self, profile_id: str, *, with_state: bool = False) -> dict[str, Any]:
        profile = self.get(profile_id)
        binding = profile.get("snapshot_binding")
        if with_state and (
            not isinstance(binding, dict)
            or binding.get("profile_id") != profile_id
            or binding.get("profile_revision") != profile["revision"]
        ):
            raise ProfileCompatibilityError(
                "profile has no compatible snapshot binding for this revision"
            )
        if profile["status"] == "archived":
            raise ProfileError("archived profile cannot be loaded")
        for entry in self._read_index()["profiles"]:
            if not isinstance(entry, dict):
                continue
            other_id = entry.get("profile_id")
            if (
                isinstance(other_id, str)
                and other_id != profile_id
                and entry.get("status") == "active"
            ):
                other = self.get(other_id)
                changes: dict[str, Any] = {"status": "inactive"}
                other_binding = other.get("snapshot_binding")
                if isinstance(other_binding, dict):
                    changes["snapshot_binding"] = {
                        **other_binding,
                        "profile_revision": int(other["revision"]) + 1,
                    }
                self.update(other_id, changes, reason="profile_switch")
        if profile.get("status") != "active":
            changes = {"status": "active"}
            if isinstance(binding, dict):
                changes["snapshot_binding"] = {
                    **binding,
                    "profile_revision": int(profile["revision"]) + 1,
                }
            profile = self.update(profile_id, changes, reason="profile_load")
        self._active_profile_id = profile_id
        return {
            "profile": profile,
            "mode": "profile_with_state" if with_state else "profile_only",
            "runtime_applied": False,
            "reason": "configuration boundary requires explicit runtime reinitialization",
            "active_profile_id": profile_id,
        }

    def save_state(self, profile_id: str, snapshot_path: Path) -> dict[str, Any]:
        profile = self.get(profile_id)
        if not snapshot_path.is_file():
            raise ProfileCompatibilityError("snapshot file does not exist")
        digest = hashlib.sha256(snapshot_path.read_bytes()).hexdigest()
        binding = {
            "path": str(snapshot_path),
            "digest": digest,
            "size_bytes": snapshot_path.stat().st_size,
            "bound_at": _now(),
            "profile_id": profile_id,
            "profile_revision": int(profile["revision"]) + 1,
            "runtime_version": self.runtime_version,
            "neuron_model": profile["neural_core"]["neuron_model"],
            "core_config_digest": _digest(profile["neural_core"]),
        }
        return self.update(
            profile_id, {"snapshot_binding": binding}, reason="snapshot_binding"
        )

    def history(self, profile_id: str) -> dict[str, Any]:
        profile = self.get(profile_id)
        directory = self._profile_dir(profile_id) / "revisions"
        revisions = []
        for path in sorted(directory.glob("rev-*.json")):
            revisions.append(
                {
                    "revision": int(path.stem.removeprefix("rev-")),
                    "path": str(path.relative_to(self.root)).replace("\\", "/"),
                    "digest": _digest(json.loads(path.read_text(encoding="utf-8"))),
                }
            )
        return {
            "profile_id": profile_id,
            "current_revision": profile["revision"],
            "revisions": revisions,
            "parent_profile_id": profile["parent_profile_id"],
        }

    def archive(self, profile_id: str) -> dict[str, Any]:
        was_active = self._active_profile_id == profile_id
        if was_active:
            self._active_profile_id = None
        return self.update(profile_id, {"status": "archived"}, reason="archive")

    def delete(self, profile_id: str) -> dict[str, Any]:
        profile = self.get(profile_id)
        if self._active_profile_id == profile_id or profile["status"] == "active":
            raise ProfileError("active profile cannot be deleted; archive it instead")
        binding = profile.get("snapshot_binding")
        if binding:
            raise ProfileError(
                "profile with snapshot provenance cannot be hard-deleted"
            )
        directory = self._profile_dir(profile_id)
        for path in sorted(directory.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
        directory.rmdir()
        self._write_index(
            [
                item
                for item in self._read_index()["profiles"]
                if item.get("profile_id") != profile_id
            ]
        )
        return {"deleted": profile_id}

    def export_zip(self, profile_id: str, *, include_snapshot: bool = False) -> bytes:
        profile = self.get(profile_id)
        payloads: dict[str, bytes] = {
            "manifest.json": b"",
            "profile.json": (
                json.dumps(profile, indent=2, sort_keys=True) + "\n"
            ).encode("utf-8"),
        }
        history = self.history(profile_id)
        payloads["revisions/metadata.json"] = (
            json.dumps(history, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        binding = profile.get("snapshot_binding")
        if (
            include_snapshot
            and isinstance(binding, dict)
            and Path(str(binding["path"])).is_file()
        ):
            snapshot = Path(str(binding["path"]))
            payloads["snapshot/" + snapshot.name] = snapshot.read_bytes()
        manifest = {
            "format": "mhrn-profile-zip-v1",
            "exported_at": _now(),
            "profile_id": profile_id,
            "profile_digest": profile["provenance"]["profile_digest"],
            "included_files": sorted(payloads),
            "snapshot_digest": (
                binding.get("digest") if isinstance(binding, dict) else None
            ),
            "scientific_boundary": "technical_identity_only",
        }
        payloads["manifest.json"] = (
            json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        import io

        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
            for name, content in payloads.items():
                archive.writestr(name, content)
        return output.getvalue()

    def import_zip(
        self, archive_bytes: bytes, *, profile_id: str | None = None
    ) -> dict[str, Any]:
        if len(archive_bytes) > MAX_IMPORT_BYTES:
            raise ProfileValidationError("profile import exceeds size limit")
        import io

        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
            infos = archive.infolist()
            if len(infos) > MAX_IMPORT_FILES:
                raise ProfileValidationError("profile import contains too many files")
            for info in infos:
                path = PurePosixPath(info.filename)
                if (
                    path.is_absolute()
                    or ".." in path.parts
                    or "\\" in info.filename
                    or info.is_dir()
                ):
                    raise ProfileValidationError("unsafe profile archive path")
                if info.file_size > MAX_IMPORT_BYTES:
                    raise ProfileValidationError(
                        "profile archive member exceeds size limit"
                    )
            if (
                "profile.json" not in archive.namelist()
                or "manifest.json" not in archive.namelist()
            ):
                raise ProfileValidationError(
                    "profile archive requires manifest.json and profile.json"
                )
            profile = validate_profile(
                json.loads(archive.read("profile.json")),
                runtime_version=self.runtime_version,
            )
            manifest = _mapping(json.loads(archive.read("manifest.json")), "manifest")
            if (
                manifest.get("profile_digest")
                != profile["provenance"]["profile_digest"]
            ):
                raise ProfileValidationError("profile archive digest mismatch")
            selected = profile_id or cast(str, profile["profile_id"])
            if any(
                item.get("profile_id") == selected
                for item in self._read_index()["profiles"]
            ):
                raise ProfileError(f"profile already exists: {selected}")
            profile["profile_id"] = _safe_id(selected)
            profile["parent_profile_id"] = None
            profile["created_at"] = _now()
            profile["updated_at"] = profile["created_at"]
            profile["revision"] = 1
            profile["status"] = "inactive"
            profile["provenance"]["profile_digest"] = _digest(profile)
            return self.create(
                profile, profile_id=selected, name=cast(str, profile["name"])
            )


__all__ = [
    "ProfileService",
    "validate_profile",
    "PROFILE_SCHEMA_VERSION",
    "ProfileError",
    "ProfileValidationError",
    "ProfileCompatibilityError",
    "ProfileNotFoundError",
]
