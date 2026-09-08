"""Verify the MHRN naming edition and export its complete canonical chapters."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote

EDITION = "2026-09-08_recursive-epistemics_v1.3"
ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\]\(([^\s)]+)")
EXTERNAL = re.compile(r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*:|/)")


def verify(root: Path) -> dict[str, int]:
    """Validate names, provenance, all current chapters and immutable history."""
    from scripts.publication_revision import check_links

    identity: dict[str, Any] = json.loads(
        (root / "project_identity.json").read_text(encoding="utf-8")
    )
    folder = root / "research/publications" / EDITION
    manifest: dict[str, Any] = json.loads(
        (folder / "manifest.json").read_text(encoding="utf-8")
    )
    order = [f"section-{index:03d}.md" for index in range(57)]
    if manifest["section_order"] != order or manifest["section_count"] != 57:
        raise ValueError("Incomplete naming edition")
    if (
        manifest["title_en"] != identity["publication"]["title_en"]
        or manifest["subtitle_de"] != identity["publication"]["subtitle_de"]
    ):
        raise ValueError("Publication title differs from canonical identity")
    if (
        manifest["new_empirical_findings"] is not False
        or manifest["automatic_evidence_promotion"] is not False
    ):
        raise ValueError("Naming must not promote evidence")
    if manifest["authority"] != "interpretation_only":
        raise ValueError("Publication authority changed")
    records = manifest["files"]
    actual = {p.name for p in folder.iterdir() if p.is_file()} - {"manifest.json"}
    if actual != set(records):
        raise ValueError("Naming edition inventory mismatch")
    for name, record in records.items():
        path = (folder / name).resolve()
        if path.parent != folder.resolve():
            raise ValueError("Unsafe edition path")
        data = path.read_bytes()
        if (
            len(data) != record["size"]
            or hashlib.sha256(data).hexdigest() != record["sha256"]
        ):
            raise ValueError(f"Naming edition checksum mismatch: {name}")
        if name in order and (not data or len(data) >= 240 * 1024):
            raise ValueError("Empty or oversized chapter")
    for name in ("README.md", "section-004.md"):
        text = (folder / name).read_text(encoding="utf-8")
        if any(f"]({section})" not in text for section in order):
            raise ValueError("Missing current chapter navigation")
    old = folder.parent / "2026-09-07_ki-die-geliehene-intelligenz_v1.2"
    for name in order[:-1]:
        anchors = re.findall(
            r'<a id="([^"]+)"', (old / name).read_text(encoding="utf-8")
        )
        new_text = (folder / name).read_text(encoding="utf-8")
        if any(f'id="{anchor}"' not in new_text for anchor in anchors):
            raise ValueError(f"Legacy citation anchor lost: {name}")
    audit: dict[str, Any] = json.loads(
        (root / "docs/05-quality/mhrn-naming-audit.json").read_text(encoding="utf-8")
    )
    history_checked = 0
    # A whole-tree migration record must not freeze future active research.
    for name, digest in audit["preserved_sha256"].items():
        if not name.startswith(
            (
                "research/publications/2026-09-07_ki-die-geliehene-intelligenz/",
                "research/publications/2026-09-07_ki-die-geliehene-intelligenz_v1.1/",
                "research/publications/2026-09-07_ki-die-geliehene-intelligenz_v1.2/",
                "research/publications/reader/",
                "research/publications/archives/",
            )
        ):
            continue
        history_checked += 1
        path = (root / name).resolve()
        if (
            not path.is_relative_to(root.resolve())
            or hashlib.sha256(path.read_bytes()).hexdigest() != digest
        ):
            raise ValueError(f"Historical source modified: {name}")
    pages = list(folder.glob("*.md")) + [
        root / "research/publications/README.md",
        root / "NAMING.md",
    ]
    links = check_links(root, pages)
    return {"sections": 57, "links": links, "historical_files": history_checked}


def export_markdown(root: Path, revision: str) -> str:
    """Pin nonchapter references while retaining the entire chapter content."""
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Export requires an exact source commit")
    folder = root / "research/publications" / EDITION
    identity: dict[str, Any] = json.loads(
        (root / "project_identity.json").read_text(encoding="utf-8")
    )
    platform: dict[str, Any] = json.loads(
        (root / "docs/05-quality/mhrn-platform-migration.json").read_text(
            encoding="utf-8"
        )
    )
    repo = platform["github"]["actual"]
    order = [f"section-{index:03d}.md" for index in range(57)]
    title = identity["publication"]["title_en"]
    output = [
        f'<a id="edition-index"></a>\n# {title}\n\nDerived export from commit `{revision}`; do not edit as a second master.\n'
    ]
    for name in order:
        text = "\n".join(
            line
            for line in (folder / name).read_text(encoding="utf-8").splitlines()
            if not line.startswith("[Inhalts")
        )

        def rewrite(match: re.Match[str]) -> str:
            target = match.group(1)
            if EXTERNAL.match(target) or target.startswith("#"):
                return match.group(0)
            relative, _, anchor = target.partition("#")
            if relative in order:
                return "](#" + (anchor or "edition-" + Path(relative).stem)
            if relative == "README.md":
                return "](#edition-index"
            destination = (folder / unquote(relative)).resolve()
            if not destination.is_relative_to(root.resolve()):
                raise ValueError("Unsafe export link")
            path = quote(destination.relative_to(root.resolve()).as_posix())
            prefix = f"https://github.com/{repo}/blob/{revision}/"
            if destination.suffix.lower() in {".png", ".jpg", ".jpeg", ".svg"}:
                prefix = f"https://raw.githubusercontent.com/{repo}/{revision}/"
            return "](" + prefix + path + ("#" + anchor if anchor else "")

        output.append(
            f'<a id="edition-{Path(name).stem}"></a>\n\n'
            + LINK.sub(rewrite, text).strip()
        )
    return "\n\n".join(output) + "\n"


def main() -> None:
    """Verify read-only; exports are permitted outside the source checkout only."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--export", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    print("VERIFIED MHRN naming: " + json.dumps(verify(root), sort_keys=True))
    if args.export:
        target = args.export.resolve()
        if target.is_relative_to(root):
            raise ValueError("Export must be outside the source checkout")
        dirty = subprocess.check_output(
            [
                "git",
                "status",
                "--porcelain",
                "--",
                "project_identity.json",
                "research/publications",
                "docs/05-quality/mhrn-platform-migration.json",
            ],
            cwd=root,
            text=True,
        )
        if dirty.strip():
            raise ValueError(
                "Commit publication sources before exporting a source-bound edition"
            )
        revision = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True
        ).strip()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(export_markdown(root, revision), encoding="utf-8")
        print(f"Derived export: {target}")


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    main()
