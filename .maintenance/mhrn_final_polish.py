"""Finalize citation metadata, compatible public aliases and bounded audit files."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "research/publications/2026-09-08_recursive-epistemics_v1.3"
MARKER = ROOT / ".maintenance/mhrn-final-polish.json"


def write(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def partition_lines(lines: list[str], stem: str, suffix: str) -> list[dict]:
    chunks: list[list[str]] = []
    current: list[str] = []
    size = 0
    for line in lines:
        length = len((line + "\n").encode("utf-8"))
        if current and size + length > 300 * 1024:
            chunks.append(current)
            current, size = [], 0
        current.append(line)
        size += length
    if current:
        chunks.append(current)
    output = []
    for i, chunk in enumerate(chunks, 1):
        name = f"{stem}-{i:03d}.{suffix}"
        path = ROOT / "docs/05-quality" / name
        write(path, "\n".join(chunk))
        output.append({"path": name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "entries": len(chunk)})
    return output


def main() -> None:
    if MARKER.exists():
        return
    identity = json.loads((ROOT / "project_identity.json").read_text(encoding="utf-8"))
    platform = json.loads((ROOT / "docs/05-quality/mhrn-platform-migration.json").read_text(encoding="utf-8"))
    publication = identity["publication"]
    # Top-level CFF types describe software/data; the treatise is the preferred report citation.
    record = {
        "cff-version": "1.2.0",
        "message": "For the scientific treatise use preferred-citation; the top-level record identifies its reproducible publication package.",
        "type": "software", "title": "Recursive Epistemics: reproducible publication package",
        "version": "1.3", "date-released": "2026-09-08",
        "authors": [{"family-names": "Heisig", "given-names": "Thomas"}],
        "repository-code": "https://github.com/" + platform["github"]["actual"],
        "preferred-citation": {
            "type": "report", "title": publication["title_en"],
            "authors": [{"family-names": "Heisig", "given-names": "Thomas"}],
            "year": 2026, "month": 9, "version": "1.3",
            "abstract": publication["subtitle_de"],
            "url": "https://github.com/" + platform["github"]["actual"] + "/tree/main/" + publication["path"],
        },
    }
    # JSON is a YAML 1.2 subset accepted by CFF; this avoids ambiguous quoting.
    write(FOLDER / "CITATION.cff", json.dumps(record, ensure_ascii=False, indent=2))
    bib = "@techreport{Heisig2026RecursiveEpistemics,\n  author = {Heisig, Thomas},\n  title = {" + publication["title_en"] + "},\n  year = {2026},\n  number = {Edition 1.3},\n  note = {" + publication["subtitle_de"] + "; scientific treatise, no peer-review or degree claim},\n  url = {" + record["preferred-citation"]["url"] + "}\n}\n"
    write(FOLDER / "CITATION.bib", bib)
    path = ROOT / "src/core/network.py"
    text = path.read_text(encoding="utf-8")
    if "MHRNConfig = Brain5DConfig" not in text:
        text += "\n# Preferred public name; preserve class identity for old configurations.\nMHRNConfig = Brain5DConfig\n"
        write(path, text)
    path = ROOT / "src/dashboard/static/assets/brain5d-being.svg"
    text = path.read_text(encoding="utf-8").replace("Brain-5D symmetrical living system organism", "MHRN symmetrical system visualization")
    write(path, text)
    path = ROOT / "tests/test_mhrn_naming.py"
    text = path.read_text(encoding="utf-8")
    text += '''

def test_configuration_alias_preserves_existing_class_identity() -> None:
    from src.core.network import Brain5DConfig, MHRNConfig

    assert MHRNConfig is Brain5DConfig
    assert MHRNConfig(dimensions=(2, 2, 2, 2, 2)).dimensions == (2, 2, 2, 2, 2)


def test_publication_citation_distinguishes_package_from_treatise() -> None:
    folder = ROOT / "research/publications/2026-09-08_recursive-epistemics_v1.3"
    citation = json.loads((folder / "CITATION.cff").read_text(encoding="utf-8"))
    identity = json.loads((ROOT / "project_identity.json").read_text(encoding="utf-8"))
    assert citation["type"] == "software"
    assert citation["preferred-citation"]["type"] == "report"
    assert citation["preferred-citation"]["title"] == identity["publication"]["title_en"]
    assert citation["preferred-citation"]["abstract"] == identity["publication"]["subtitle_de"]
'''
    write(path, text)
    # Preserve the complete dated audit without a megabyte-sized monolith.
    path = ROOT / "docs/05-quality/mhrn-naming-audit.json"
    audit = json.loads(path.read_text(encoding="utf-8"))
    all_hashes = audit["preserved_sha256"]
    audit["preserved_at_migration_count"] = len(all_hashes)
    audit["preservation_inventory_files"] = partition_lines([f"{sha}  {name}" for name, sha in sorted(all_hashes.items())], "mhrn-preserved-sources", "sha256")
    roots = (
        "research/publications/2026-09-07_ki-die-geliehene-intelligenz/",
        "research/publications/2026-09-07_ki-die-geliehene-intelligenz_v1.1/",
        "research/publications/2026-09-07_ki-die-geliehene-intelligenz_v1.2/",
        "research/publications/reader/", "research/publications/archives/",
    )
    audit["preserved_sha256"] = {name: sha for name, sha in all_hashes.items() if name.startswith(roots)}
    legacy = audit.pop("retained_legacy_references", [])
    audit["retained_legacy_reference_count"] = len(legacy)
    audit["legacy_reference_inventory_files"] = partition_lines([json.dumps(item, ensure_ascii=False) for item in legacy], "mhrn-legacy-references", "jsonl")
    audit["persistent_check_scope"] = "frozen_publication_history_only; other inventories document preservation during naming migration, not a ban on future research updates"
    write(path, json.dumps(audit, ensure_ascii=False, indent=2))
    naming = ROOT / "NAMING.md"
    text = naming.read_text(encoding="utf-8")
    text += "\nPreferred configuration import: `from src.core.network import MHRNConfig`. The historical `Brain5DConfig` name refers to the identical class. The current publication package includes a CFF record with a report-type preferred citation and a matching BibTeX citation. Audit inventories are split into bounded files; they preserve the full migration record.\n"
    write(naming, text)
    manifest_path = FOLDER / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["files"] = {p.name: {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "size": p.stat().st_size} for p in sorted(FOLDER.iterdir()) if p.is_file() and p.name != "manifest.json"}
    write(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2))
    write(MARKER, '{"applied":true,"historical_scientific_data_changed":false}')


if __name__ == "__main__":
    main()
