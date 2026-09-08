"""Perform only the owner's explicitly requested, identity-preserving renames.

No token values, permissions, visibility, billing or secrets are modified.
A denied administrator operation remains BLOCKED, never silently substituted
with a duplicate repository. The result distinguishes requested and actual IDs.
"""
from __future__ import annotations

import importlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = json.loads((ROOT / "project_identity.json").read_text(encoding="utf-8"))
PLATFORMS = IDENTITY["platforms"]


def github_request(path: str, method: str = "GET", body: dict | None = None) -> dict:
    token = os.environ.get("GITHUB_TOKEN", "")
    data = json.dumps(body).encode() if body is not None else None
    request = Request("https://api.github.com" + path, data=data, method=method,
                      headers={"Accept": "application/vnd.github+json",
                               "Authorization": "Bearer " + token,
                               "Content-Type": "application/json"})
    with urlopen(request, timeout=45) as response:
        return json.load(response)


def rename_github() -> dict:
    desired = PLATFORMS["github_requested"]
    current = PLATFORMS["github_legacy"]
    result = {"requested": desired, "actual": current, "status": "BLOCKED"}
    try:
        info = github_request("/repositories/" + str(PLATFORMS["github_repository_id"]))
        current = info["full_name"]
        result["actual"] = current
        result["repository_id"] = info["id"]
        if current == desired:
            return {**result, "status": "ALREADY_RENAMED"}
        if current != PLATFORMS["github_legacy"]:
            return {**result, "reason": "unexpected_repository_identity"}
        try:
            existing = github_request("/repos/" + desired)
        except HTTPError as exc:
            if exc.code != 404:
                raise
        else:
            if existing["id"] != info["id"]:
                return {**result, "reason": "destination_is_another_repository"}
        changed = github_request("/repos/" + current, "PATCH", {
            "name": "MHRN",
            "description": IDENTITY["project"]["title_en"] + " | " + IDENTITY["project"]["subtitle_de"],
        })
        if changed["id"] != info["id"] or changed["full_name"] != desired:
            return {**result, "reason": "rename_response_not_verified"}
        return {**result, "actual": desired, "status": "RENAMED"}
    except HTTPError as exc:
        return {**result, "http_status": exc.code,
                "reason": "admin_permission_required" if exc.code in (401, 403) else "api_request_failed"}
    except Exception as exc:
        return {**result, "reason": type(exc).__name__}


def rename_hf(repo_type: str) -> dict:
    key = "model" if repo_type == "model" else "space"
    old = PLATFORMS[f"huggingface_{key}_legacy"]
    desired = PLATFORMS[f"huggingface_{key}_requested"]
    result = {"repo_type": repo_type, "requested": desired, "actual": old, "status": "BLOCKED"}
    token = os.environ.get("HF_TOKEN", "")
    namespace = os.environ.get("HF_USERNAME", "")
    if not token or not namespace:
        return {**result, "reason": "configured_huggingface_credentials_unavailable"}
    if namespace != PLATFORMS["huggingface_namespace"]:
        return {**result, "reason": "configured_namespace_does_not_match_authorized_namespace"}
    try:
        api = importlib.import_module("huggingface_hub").HfApi(token=token)
        info = api.repo_info(old, repo_type=repo_type)
        result["actual"] = info.id
        result["source_head"] = info.sha
        if info.id == desired:
            return {**result, "status": "ALREADY_RENAMED"}
        if info.id != old:
            return {**result, "reason": "unexpected_source_identity"}
        try:
            destination = api.repo_info(desired, repo_type=repo_type)
        except Exception as exc:
            if getattr(getattr(exc, "response", None), "status_code", None) != 404:
                raise
        else:
            return {**result, "reason": "destination_exists_no_overwrite", "destination_id": destination.id}
        api.move_repo(from_id=old, to_id=desired, repo_type=repo_type)
        after = api.repo_info(desired, repo_type=repo_type)
        if after.id != desired or after.sha != info.sha:
            return {**result, "actual": after.id, "reason": "post_rename_head_or_identity_changed"}
        return {**result, "actual": after.id, "status": "RENAMED", "head_preserved": True}
    except Exception as exc:
        return {**result, "reason": type(exc).__name__,
                "http_status": getattr(getattr(exc, "response", None), "status_code", None)}


def main() -> None:
    report = {"checked_at": datetime.now(timezone.utc).isoformat(),
              "github": rename_github(),
              "huggingface_model": rename_hf("model"),
              "huggingface_space": rename_hf("space")}
    target = ROOT / "docs/05-quality/mhrn-platform-migration.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
