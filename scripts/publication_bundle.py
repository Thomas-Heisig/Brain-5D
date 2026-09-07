"""Verify the frozen scientific publication and build its bounded reader views."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path
from urllib.parse import quote

PACKAGE = "2026-09-07_ki-die-geliehene-intelligenz"
PUBLICATIONS = Path("research/publications")
MASTER = "wissenschaftliche_abhandlung.md"
MAX_SECTION_BYTES = 240 * 1024
ANCHOR = re.compile(r'<a id="([^"]+)"></a>')
LINK = re.compile(r"(?P<prefix>\]\()(?P<target>[^\s)]+)")


def digest(data: bytes) -> str:
    """Return the content identity used by both import and reader manifests."""
    return hashlib.sha256(data).hexdigest()


def safe_path(root: Path, relative: str) -> Path:
    """Resolve a manifest path without accepting traversal or symlink escapes."""
    candidate = root / relative
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise ValueError(f"Unsafe manifest path: {relative}")
    if not candidate.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Manifest path escapes root: {relative}")
    return candidate


def split_sections(text: str) -> list[tuple[str, int, int, str]]:
    """Split at top-level headings, keeping each preceding explicit anchor."""
    lines = text.splitlines(keepends=True)
    starts = [0]
    fence: str | None = None
    for index, line in enumerate(lines):
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence or not line.startswith("# "):
            continue
        start = index
        while start and not lines[start - 1].strip():
            start -= 1
        if start and ANCHOR.fullmatch(lines[start - 1].strip()):
            start -= 1
        if start > starts[-1] and any(
            line.strip() for line in lines[starts[-1] : start]
        ):
            starts.append(start)
    result = []
    for start, end in zip(starts, starts[1:] + [len(lines)]):
        content = "".join(lines[start:end])
        heading = re.search(r"^# (.+)$", content, re.MULTILINE)
        title = heading.group(1) if heading else "Titel und Einordnung"
        result.append((title, start + 1, end, content))
    if "".join(item[3] for item in result) != text:
        raise ValueError("Section splitting did not preserve the complete source")
    return result


def clean_reader_text(text: str) -> str:
    """Normalize derived views only; preserve Markdown hard breaks."""
    output: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            output.append(line.rstrip())
            continue
        hard_break = fence is None and line.endswith("  ") and bool(line.strip())
        output.append(line.rstrip() + ("<br>" if hard_break else ""))
    return "\n".join(output)


def reader_files(source: bytes) -> dict[str, bytes]:
    """Return deterministic reader files, preserving all source sections."""
    text = source.decode("utf-8")
    sections = split_sections(text)
    names = [f"section-{index:03d}.md" for index in range(len(sections))]
    anchors = {
        match.group(1): name
        for name, (_, _, _, content) in zip(names, sections)
        for match in ANCHOR.finditer(content)
    }
    outputs: dict[str, bytes] = {}
    entries = []
    for index, (name, (title, first, last, content)) in enumerate(zip(names, sections)):

        def rewrite(match: re.Match[str]) -> str:
            target = match.group("target")
            if target.startswith("#") and target[1:] in anchors:
                target = anchors[target[1:]] + target
            elif not re.match(r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*:|/|#)", target):
                target = f"../{PACKAGE}/" + target
            return match.group("prefix") + target

        navigation = ["[Inhaltsuebersicht](README.md)"]
        if index:
            navigation.append(f"[Zurueck]({names[index - 1]})")
        if index + 1 < len(names):
            navigation.append(f"[Weiter]({names[index + 1]})")
        nav = " | ".join(navigation)
        rendered = (
            nav
            + "\n\n"
            + clean_reader_text(LINK.sub(rewrite, content)).rstrip()
            + "\n\n"
            + nav
            + "\n"
        ).encode()
        if len(rendered) >= MAX_SECTION_BYTES:
            raise ValueError(
                f"Reader section is too large for a complete preview: {title}"
            )
        outputs[name] = rendered
        entries.append(
            {
                "path": name,
                "title": title,
                "first_line": first,
                "last_line": last,
                "source_sha256": digest(content.encode()),
                "rendered_sha256": digest(rendered),
                "rendered_bytes": len(rendered),
            }
        )
    index_lines = [
        "# Wissenschaftliche Abhandlung: vollstaendige Lesefassung",
        "",
        "## KI - Die geliehene Intelligenz",
        "",
        "Thomas Heisig. Fassung vom 7. September 2026. Theoretische Synthese und "
        "artefaktbasierte Sekundaerauswertung; keine automatische Evidenzfreigabe.",
        "",
        "Die folgenden Abschnitte enthalten den gesamten Haupttext einschliesslich "
        "Anhaengen und Literaturverzeichnis. Die Unterteilung vermeidet das "
        "Vorschau-Limit des zentralen File Viewers. Originale bleiben unveraendert.",
        "",
        f"[Publikation und alle Begleitdateien](../README.md) | "
        f"[Original-Markdown](../{PACKAGE}/{MASTER}) | "
        f"[Word-Fassung](../{PACKAGE}/wissenschaftliche_abhandlung.docx)",
        "",
    ]
    for entry in entries:
        index_lines.append(f"- [{entry['title']}]({entry['path']})")
    index_lines += [
        "",
        "Generierte Leseansicht; Herkunft und Abschnittspruefsummen: "
        "[manifest.json](manifest.json).",
        "",
    ]
    outputs["README.md"] = "\n".join(index_lines).encode()
    manifest = {
        "schema_version": "1.0",
        "source": f"../{PACKAGE}/{MASTER}",
        "source_sha256": digest(source),
        "source_bytes": len(source),
        "authority": "interpretation_only",
        "section_count": len(entries),
        "sections": entries,
    }
    outputs["manifest.json"] = (
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    ).encode()
    return outputs


def build_reader(root: Path, *, check: bool = False) -> int:
    """Write the reader, or fail if any existing generated file is stale."""
    publication_root = root / PUBLICATIONS
    source = (publication_root / PACKAGE / MASTER).read_bytes()
    expected = reader_files(source)
    target = publication_root / "reader"
    existing = {p.name for p in target.glob("*") if p.is_file()}
    if check and existing != set(expected):
        raise ValueError("Reader inventory differs from the complete generated view")
    if not check:
        target.mkdir(parents=True, exist_ok=True)
        if existing - set(expected):
            raise ValueError(
                "Unexpected reader files; refusing to silently delete content"
            )
    for name, data in expected.items():
        path = target / name
        if check:
            if path.read_bytes() != data:
                raise ValueError(f"Stale or modified reader file: {name}")
        else:
            path.write_bytes(data)
    return len(expected) - 2


def verify_bundle(root: Path) -> int:
    """Require full bytes (not LFS pointers) and verify inventory plus archive."""
    publication_root = root / PUBLICATIONS
    manifest = json.loads(
        (publication_root / "integrity.json").read_text(encoding="utf-8")
    )
    snapshot = safe_path(publication_root, manifest["package"])
    entries = manifest["files"]
    names = [entry["path"] for entry in entries]
    if len(names) != 41 or len(set(names)) != 41 or manifest["file_count"] != 41:
        raise ValueError("Expected exactly 41 distinct frozen publication files")
    actual = {
        p.relative_to(snapshot).as_posix() for p in snapshot.rglob("*") if p.is_file()
    }
    if actual != set(names):
        raise ValueError("Frozen publication inventory changed")
    for entry in entries:
        data = safe_path(snapshot, entry["path"]).read_bytes()
        if len(data) != entry["size"] or digest(data) != entry["sha256"]:
            raise ValueError(
                f"Checksum mismatch or unmaterialized LFS: {entry['path']}"
            )
    archive = manifest["archive"]
    archive_path = safe_path(publication_root, archive["path"])
    archive_bytes = archive_path.read_bytes()
    if (
        len(archive_bytes) != archive["size"]
        or digest(archive_bytes) != archive["sha256"]
    ):
        raise ValueError("Original ZIP checksum mismatch or unmaterialized LFS")
    with zipfile.ZipFile(archive_path) as bundle:
        members = bundle.infolist()
        zipped = {item.filename.split("/", 1)[1]: item for item in members}
        if len(members) != 41 or set(zipped) != set(names):
            raise ValueError("Archive inventory does not match frozen publication")
        for entry in entries:
            if digest(bundle.read(zipped[entry["path"]])) != entry["sha256"]:
                raise ValueError(f"Archive member mismatch: {entry['path']}")
    return len(entries)


def check_reader_links(root: Path) -> None:
    """Validate local reader links and explicit cross-chapter anchors."""
    reader = root / PUBLICATIONS / "reader"
    for page in reader.glob("*.md"):
        for match in LINK.finditer(page.read_text(encoding="utf-8")):
            target = match.group("target")
            if re.match(r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*:|/)", target):
                continue
            path, _, anchor = target.partition("#")
            destination = page.parent / path if path else page
            if not destination.is_file():
                raise ValueError(f"Broken reader link in {page.name}: {target}")
            if anchor and destination.suffix == ".md":
                contents = destination.read_text(encoding="utf-8")
                if f'id="{anchor}"' not in contents and quote(anchor) not in contents:
                    raise ValueError(f"Broken reader anchor in {page.name}: {target}")


def main() -> None:
    """Provide deterministic build and strict verification entry points."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--build-reader", action="store_true")
    args = parser.parse_args()
    if args.build_reader:
        print(f"Reader generated: {build_reader(args.root)} complete sections")
    else:
        count = verify_bundle(args.root)
        sections = build_reader(args.root, check=True)
        check_reader_links(args.root)
        print(
            f"VERIFIED: {count} frozen files, original ZIP, {sections} complete reader sections"
        )


if __name__ == "__main__":
    main()
