"""Read-only verification of the cognition supplement and its source boundaries."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote

EDITION = "2026-09-07_ki-die-geliehene-intelligenz_v1.2"
ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\]\(([^\s)]+)")
EXTERNAL = re.compile(r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*:|/)")


def verify(root: Path) -> dict[str, int]:
    """Verify immutable inherited chapters, inventory, links and claim boundaries."""
    folder = root / "research/publications" / EDITION
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    expected = [f"section-{i:03d}.md" for i in range(56)]
    if manifest["section_order"] != expected or manifest["section_count"] != 56:
        raise ValueError("Incomplete cognition edition")
    if (
        manifest["authority"] != "interpretation_only"
        or manifest["automatic_evidence_promotion"] is not False
        or manifest["new_empirical_consciousness_findings"] is not False
    ):
        raise ValueError("Publication cannot award consciousness evidence")
    names = {p.name for p in folder.iterdir() if p.is_file()} - {"manifest.json"}
    if names != set(manifest["files"]):
        raise ValueError("Edition file inventory mismatch")
    inherited = (folder / manifest["inherited_edition"]).resolve()
    if not inherited.is_relative_to((root / "research/publications").resolve()):
        raise ValueError("Unsafe inherited path")
    changed = set(manifest["revised_sections"]) | set(manifest["added_sections"])
    for name, record in manifest["files"].items():
        path = (folder / name).resolve()
        if path.parent != folder.resolve() or not path.is_file():
            raise ValueError("Unsafe inventory path")
        data = path.read_bytes()
        if (
            len(data) != record["size"]
            or hashlib.sha256(data).hexdigest() != record["sha256"]
        ):
            raise ValueError(f"Edition checksum mismatch: {name}")
        if name in expected:
            if not data or len(data) >= 240 * 1024:
                raise ValueError(f"Empty or oversized section: {name}")
            if name not in changed and data != (inherited / name).read_bytes():
                raise ValueError(f"Inherited section changed: {name}")
    pages = list(folder.glob("*.md")) + [root / "research/publications/README.md"]
    pages += list((root / "research/critique").glob("*.md"))
    pages += list((root / "research/ethics").glob("*.md"))
    pages += [
        root / "research/protocols/COGNITION_CONSCIOUSNESS.md",
        root / "research/literature/COGNITION_SOURCES.md",
        root / "docs/06-research/CONSCIOUSNESS_AND_WELFARE.md",
    ]
    checked = 0
    for page in pages:
        for match in LINK.finditer(page.read_text(encoding="utf-8")):
            target = match.group(1)
            if EXTERNAL.match(target):
                continue
            relative, _, anchor = target.partition("#")
            destination = (
                (page.parent / unquote(relative)).resolve() if relative else page
            )
            if (
                not destination.is_relative_to(root.resolve())
                or not destination.exists()
            ):
                raise ValueError(f"Broken or unsafe link {page.name}: {target}")
            if anchor and destination.suffix == ".md":
                content = destination.read_text(encoding="utf-8")
                if f'id="{unquote(anchor)}"' not in content:
                    raise ValueError(f"Broken anchor {page.name}: {target}")
            checked += 1
    for name in ("README.md", "section-004.md"):
        text = (folder / name).read_text(encoding="utf-8")
        if any(f"]({section})" not in text for section in expected):
            raise ValueError("Incomplete edition navigation")
    program = json.loads(
        (root / "research/protocols/COGNITION_CONSCIOUSNESS_V1.json").read_text(
            encoding="utf-8"
        )
    )
    protocols = program["protocols"]
    if len(protocols) != 22 or len({p["id"] for p in protocols}) != 22:
        raise ValueError("Incomplete protocol family")
    for protocol in protocols:
        draft = json.loads(
            (root / "research" / protocol["preregistration_draft"]).read_text(
                encoding="utf-8"
            )
        )
        if (
            draft["status"] != "DRAFT_NOT_PREREGISTERED"
            or draft["protocol_id"] != protocol["id"]
        ):
            raise ValueError("Preregistration falsely promoted or mismatched")
        if (
            protocol["consciousness_inference"] != "not_established"
            or protocol["native_adapter_validated"] is not False
        ):
            raise ValueError("Unvalidated adapter promoted")
    return {
        "sections": len(expected),
        "links": checked,
        "protocols": len(protocols),
        "critique_topics": 38,
    }


if __name__ == "__main__":
    print("VERIFIED cognition supplement: " + json.dumps(verify(ROOT), sort_keys=True))
