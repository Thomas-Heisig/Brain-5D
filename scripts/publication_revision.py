"""Validate the current publication and export from its canonical chapters."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote, unquote

EDITION = "2026-09-07_ki-die-geliehene-intelligenz_v1.1"
PUBLICATIONS = Path("research/publications")
LINK = re.compile(r"\]\((?P<target>[^\s)]+)")
EXTERNAL = re.compile(r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*:|/)")
SECTION = re.compile(r"section-\d{3}\.md\Z")
MAX_BYTES = 240 * 1024


def contained(root: Path, path: Path) -> Path:
    """Reject resolved paths outside the repository, including symlinks."""
    resolved = path.resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError(f"Unsafe publication path: {path}")
    return resolved


def check_links(root: Path, pages: list[Path]) -> int:
    """Check relative file targets and explicit Markdown fragment anchors."""
    checked = 0
    for page in pages:
        for match in LINK.finditer(page.read_text(encoding="utf-8")):
            target = match.group("target")
            if EXTERNAL.match(target):
                continue
            path, _, anchor = target.partition("#")
            destination = contained(root, page.parent / unquote(path)) if path else page
            if not destination.exists():
                raise ValueError(f"Broken link in {page.name}: {target}")
            if anchor and destination.suffix == ".md":
                text = destination.read_text(encoding="utf-8")
                decoded = unquote(anchor)
                if f'id="{decoded}"' not in text and f"id='{decoded}'" not in text:
                    raise ValueError(f"Broken anchor in {page.name}: {target}")
            checked += 1
    return checked


def verify_edition(root: Path) -> dict[str, int]:
    """Require all chapters, exact inherited text, valid links and witnesses."""
    folder = root / PUBLICATIONS / EDITION
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    order = manifest["section_order"]
    expected = [f"section-{i:03d}.md" for i in range(51)]
    if order != expected or manifest["section_count"] != len(expected):
        raise ValueError("Incomplete or reordered publication chapters")
    revised = set(manifest["revised_sections"])
    added = set(manifest["added_sections"])
    original = set(expected[:46])
    if not revised <= original or added != set(expected[46:]):
        raise ValueError("Invalid chapter provenance")
    if len(revised) != 8 or revised & added:
        raise ValueError("Expected eight revised historical chapters")
    if manifest["automatic_evidence_promotion"] is not False:
        raise ValueError("Publication must not promote scientific evidence")
    if manifest["empirical_brain5d_experiments_executed_in_revision"] is not False:
        raise ValueError("Methodological witnesses are not Brain-5D experiments")
    supporting = manifest["supporting_files"]
    names = set(expected) | {"README.md", "manifest.json"} | set(supporting)
    actual = {path.name for path in folder.iterdir() if path.is_file()}
    if actual != names:
        raise ValueError("Edition inventory differs from its manifest")
    inherited = contained(root, folder / manifest["inherited_reader"])
    for name in order:
        if not SECTION.fullmatch(name):
            raise ValueError(f"Unsafe chapter name: {name}")
        data = (folder / name).read_bytes()
        if not data or len(data) > MAX_BYTES:
            raise ValueError(f"Empty or oversized chapter: {name}")
        if name not in revised | added and data != (inherited / name).read_bytes():
            raise ValueError(f"Modified inherited chapter: {name}")
    for name in supporting:
        contained(root, folder / name)
    pages = [folder / "README.md"] + [folder / name for name in order]
    for index in (folder / "README.md", folder / "section-004.md"):
        text = index.read_text(encoding="utf-8")
        if any(f"]({name})" not in text for name in order):
            raise ValueError(f"Incomplete table of contents: {index.name}")
    links = check_links(root, pages)
    report = json.loads((folder / "methodenpruefung.json").read_text(encoding="utf-8"))
    if report["brain5d_runtime_executed"] is not False or report["checks_passed"] != 28:
        raise ValueError("Invalid methodological witness report")
    script = folder / "methodenpruefung.py"
    if hashlib.sha256(script.read_bytes()).hexdigest() != report["script_sha256"]:
        raise ValueError("Witness script and recorded hash differ")
    subprocess.run(
        [sys.executable, str(script), "--check", str(folder / "methodenpruefung.json")],
        check=True,
    )
    return {"sections": len(order), "inherited": 38, "links": links, "witnesses": 28}


def build_export(root: Path, revision: str) -> str:
    """Combine chapters and pin non-chapter links to a verified Git commit."""
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("An exact Git commit is required for exported asset links")
    folder = root / PUBLICATIONS / EDITION
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    order = manifest["section_order"]
    output = [
        '<a id="edition-index"></a>\n# Brain-5D: Abhandlung 1.1\n',
        f"Derived export from canonical chapters at commit `{revision}`.\n",
        "Do not edit this export as an independent source.\n",
    ]
    for name in order:
        page = folder / name
        text = "\n".join(
            line
            for line in page.read_text(encoding="utf-8").splitlines()
            if not line.startswith("[Inhalts")
        )

        def rewrite(match: re.Match[str]) -> str:
            target = match.group("target")
            if EXTERNAL.match(target) or target.startswith("#"):
                return match.group(0)
            path, _, anchor = target.partition("#")
            if path in order:
                return "](#" + (anchor or "edition-" + Path(path).stem)
            if path == "README.md":
                return "](#edition-index"
            destination = contained(root, page.parent / unquote(path))
            relative = quote(destination.relative_to(root.resolve()).as_posix())
            base = f"https://github.com/Thomas-Heisig/Brain-5D/blob/{revision}/"
            if destination.suffix.lower() in {".png", ".jpg", ".jpeg", ".svg"}:
                base = (
                    "https://raw.githubusercontent.com/Thomas-Heisig/Brain-5D/"
                    f"{revision}/"
                )
            return "](" + base + relative + ("#" + anchor if anchor else "")

        text = LINK.sub(rewrite, text)
        output.append(f'<a id="edition-{Path(name).stem}"></a>\n\n{text.strip()}\n')
    return "\n\n".join(output) + "\n"


def main() -> None:
    """Validate without writes; optionally export outside the canonical tree."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--export", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    result = verify_edition(root)
    print("VERIFIED publication revision: " + json.dumps(result, sort_keys=True))
    if args.export:
        target = args.export.resolve()
        if target.is_relative_to((root / PUBLICATIONS).resolve()):
            raise ValueError("Export must not overwrite canonical publication files")
        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout.strip()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(build_export(root, revision), encoding="utf-8")
        print(f"Derived export written: {target}")


if __name__ == "__main__":
    main()
