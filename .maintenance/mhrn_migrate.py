"""One-shot naming migration on an isolated review branch.

Keep historical science immutable. Emit a per-file byte inventory so the review
can distinguish renamed active surfaces from retained provenance/compatibility.
No global replacement of scientific dimensions, IDs or serialized formats.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = json.loads((ROOT / "project_identity.json").read_text(encoding="utf-8"))
PUB = ROOT / "research/publications"
OLD = PUB / "2026-09-07_ki-die-geliehene-intelligenz_v1.2"
NEW = ROOT / IDENTITY["publication"]["path"]
MARKER = ROOT / ".maintenance/mhrn-migration-complete.json"
PLATFORM = ROOT / "docs/05-quality/mhrn-platform-migration.json"
BRAND = re.compile(r"(?<![\w])Brain(?:-|\u2011|\u2013|\u2010| )5D(?![\w])")
URL = re.compile(r"https?://[^\s<>)\]\"']+")
HISTORICAL_PREFIXES = (
    "research/experiments/", "research/preregistrations/", "research/registry/",
    "research/generated/", "research/publications/", "research/literature/",
    "docs/99-archive/", "docs/09-archive/", "docs/10-releases/", "docs/11-readme/",
    "releases/", "artifacts/", "patches/", "tests/fixtures/", "tests/data/",
)
FROZEN_ROOT = {"CHANGELOG.md", "LICENSE", "tests/test_baseline.json"}
# Historical reference fixtures are rebuilt by their own unchanged validators.
FROZEN_SCRIPTS = {"scripts/publication_bundle.py", "scripts/publication_revision.py",
                  "scripts/publication_cognition.py", "tests/test_publication_revision.py",
                  "tests/test_publication_integration.py"}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tracked() -> list[Path]:
    data = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [ROOT / name.decode() for name in data.split(b"\0") if name]


def frozen(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith(HISTORICAL_PREFIXES) or rel in FROZEN_ROOT | FROZEN_SCRIPTS:
        return True
    # Versioned/datestamped reports stay historical, even outside archive folders.
    if rel.startswith("docs/") and re.search(r"(?:20\d{2}[-_]\d{2}[-_]\d{2}|v\d|V\d|ALPHA|SPRINT|RELEASE_)", path.name):
        return True
    return False


def rename_text(text: str, github_actual: str, hf_model: str, hf_space: str) -> str:
    """Preserve all cited URLs except active unpinned project/platform links."""
    urls: list[str] = []
    def mask(match: re.Match) -> str:
        url = match.group()
        # A commit/tag pinned reference continues to identify the same record.
        if not re.search(r"/(?:blob|tree)/[0-9a-f]{7,40}(?:/|$)", url):
            url = url.replace("github.com/Thomas-Heisig/Brain-5D", "github.com/" + github_actual)
            url = url.replace("huggingface.co/spaces/superdigger/Brain-5D-Space", "huggingface.co/spaces/" + hf_space)
            url = url.replace("huggingface.co/superdigger/Brain-5D", "huggingface.co/" + hf_model)
        urls.append(url)
        return f"__MHRN_URL_{len(urls)-1}__"
    masked = URL.sub(mask, text)
    masked = BRAND.sub("MHRN", masked)
    for i, url in enumerate(urls):
        masked = masked.replace(f"__MHRN_URL_{i}__", url)
    return masked


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def build_publication(gh: str, model: str, space: str) -> None:
    if NEW.exists():
        raise ValueError("Current edition path already exists; refusing to overwrite")
    shutil.copytree(OLD, NEW)
    old_manifest = json.loads((OLD / "manifest.json").read_text(encoding="utf-8"))
    order = old_manifest["section_order"] + ["section-056.md"]
    pub = IDENTITY["publication"]
    project = IDENTITY["project"]
    for page in NEW.glob("section-*.md"):
        if page.name in {"section-044.md", "section-045.md", "section-049.md"}:
            continue  # source titles and earlier source-use declarations are not rewritten
        text = rename_text(page.read_text(encoding="utf-8"), gh, model, space)
        write(page, text)
    write(NEW / "section-000.md", f'''[Inhaltsübersicht](README.md) | [Weiter](section-001.md)

<a id="b5d-ki---die-geliehene-intelligenz"></a>
# {pub['title_en']}

## {pub['subtitle_de']}

**Thomas Heisig · Scientific Treatise / Wissenschaftliche Abhandlung · Edition 1.3 · 8 September 2026**

**Technical framework: {project['short_name']} — {project['title_en']}**

*{project['subtitle_de']}*

{project['description_en']} / {project['description_de']}.

Diese Edition führt die vollständige bisherige Abhandlung unter einer deskriptiven Benennung fort. Die Kapitelsprachen bleiben erhalten; der englische Haupttitel und seine deutsche Übersetzung sind keine Behauptung, der gesamte Text sei ins Englische übersetzt worden. Der Ausdruck „Dissertation“ in historischen Quelldateinamen ist keine akademische Anerkennungsbehauptung.

**Wissenschaftlicher Status:** theoretisch-methodische Untersuchung mit quellengebundener Sekundärauswertung und ausdrücklich ausgewiesenen Prüfentwürfen. Die Umbenennung erzeugt keine neue empirische Evidenz, keinen Nachweis phänomenalen Bewusstseins und keine automatische Ethikfreigabe.

**Herkunft:** Fortführung der Fassung 1.2. Die historischen Projekt- und Werktitel bleiben in Zitaten, Quellenangaben, alten Ausgaben und technischen Kompatibilitätsbezeichnern nachvollziehbar. Die zugrunde liegende Architektur und ihre offenen Hypothesen werden nicht nachträglich verändert.

[Benennung und begriffliche Abgrenzung](section-056.md) · [Quellen und frühere Fassungen](../README.md)
''')
    write(NEW / "section-003.md", '''[Inhaltsübersicht](README.md) | [Zurück](section-002.md) | [Weiter](section-004.md)

<a id="b5d-leseweg-und-orientierung"></a>
# Leseweg und Orientierung

Die Edition 1.3 ist die aktuelle redaktionelle Quelle. Sie enthält sämtliche 56 Abschnitte der Edition 1.2, mit aktualisierter Benennung und zusätzlichem Anhang P. Die ursprünglichen Fassungen bleiben mit ihren Dateien und Prüfsummen erhalten. Ein vollständiger Export ist eine abgeleitete Darstellung, keine zweite Bearbeitungsquelle.

Die Kapitel 1–12 behandeln philosophische und institutionelle Fragen, 13–21 das technische Modell, 22–25 historische technische Befunde und 26–36 die Verbindung von Embodiment, Daten, Versuchsplanung, Kritik und Schlussposition. Anhänge A–J dokumentieren Register, Quellen, Begriffe und formale Argumente. Anhänge K–O ergänzen Bewusstseinskritik, Testverträge, Wohlfahrt, unabhängige Evidenz und Forschungsstatus. Anhang P präzisiert die neue Benennung und ihre Grenzen.

**Leseregel:** Ein aktualisierter Name verändert weder den Quellenstichtag eines übernommenen Befunds noch seinen Evidenzstatus. Frühere Registerauszüge bleiben datierte Momentaufnahmen. Vorhandene Modellgleichungen sind nicht allein durch ihre Aufnahme in diese Edition implementiert oder validiert. Die besonders deutlichen Einschränkungen und Kritikprüfungen aus den Editionen 1.1 und 1.2 bleiben sachlich wirksam.

**Terminologie:** MHRN ist der aktuelle Projektname. „Rekursive Epistemik“ ist der kurze deutsche Werktitel. Epistemische Herkunft, funktionale Abhängigkeit, bewusste Delegation und kausale Leistungszuordnung werden weiterhin unterschieden. Die technische fünfkoordinatige Adressierung ist keine Behauptung eines nur fünfdimensionalen vollständigen Systemzustands.
''')
    naming = (ROOT / "NAMING.md").read_text(encoding="utf-8")
    write(NEW / "section-056.md", '''[Inhaltsübersicht](README.md) | [Zurück](section-055.md)

<a id="mhrn-naming-and-scope"></a>
# Anhang P — Benennung, Übersetzung und wissenschaftlicher Geltungsbereich

## P.1 Aktuelle Titel

''' + f"**{project['title_en']} (MHRN)**\n\n*{project['subtitle_de']}*\n\n**{pub['title_en']}**\n\n*{pub['subtitle_de']}*\n\n" + '''## P.2 Deskriptiver Name ist kein Erkenntnisnachweis

Die Umbenennung beantwortet den Wunsch nach einer mechanismusorientierten Darstellung. Sie bestätigt weder, dass sämtliche im Titel angesprochenen Mechanismen bereits funktional validiert sind, noch dass ein bestimmter Publikationsort oder akademischer Grad erreicht werden würde. „Multi-Scale“, „Homeostatic“ und „Recurrence“ benennen Untersuchungsgegenstände und Architekturmerkmale, deren jeweiliger Implementierungs- und Evidenzstand weiterhin separat nachzuweisen ist.

Auch die Behauptung, ein früherer Titel sei wissenschaftlich „toxisch“ oder ein neuer Titel schütze vor berechtigter Kritik, wäre eine unbelegte Pauschalisierung. Beurteilt werden Fragestellung, Methodik, logische Tragfähigkeit, Ergebnisse und unabhängige Nachprüfbarkeit. Der vorgeschlagene Begriff „Autopoiesis“ wird nicht als Name gewählt, weil damit zusätzliche theoretische Verpflichtungen verbunden wären, die diese Revision nicht einlöst.

## P.3 Keine mathematische Umdeutung

Fünf Koordinaten adressieren im vorhandenen Kern Neuronen. Der Gesamtzustand enthält darüber hinaus Membran- und Erholungsvariablen, synaptische Gewichte, Verzögerungspuffer, Zufallszustände, Ressourcen und weitere Komponenten. Die Länge des Adresstupels ist daher nicht die Dimension des gesamten dynamischen Zustandsraums. Eine Projektion müsste ausdrücklich definiert und geprüft werden; die reine Umbenennung erzeugt keine solche Projektion. Ebenso ist „Tensor“ eine mathematische beziehungsweise implementierungsbezogene Eigenschaft und kein austauschbares Wort für jeden mehrdimensionalen Adressraum.

## P.4 Herkunft und Delegation bleiben verschieden

Der frühere Ausdruck „geliehene Intelligenz“ bleibt als historischer Arbeitsbegriff dort erhalten, wo die Argumentation ihn erläutert oder kritisiert. Er wird nicht mechanisch durch „Delegation“ ersetzt. Ein Modell kann von fremden Trainingsdaten abhängig sein, ohne dass deren Urheber ihm eine Aufgabe delegiert haben. Umgekehrt kann eine ausdrücklich delegierte Aufgabe lokal und ohne externes Abrufen gelöst werden. Die wissenschaftlich relevanten Relationen sind deshalb weiterhin quellen- und aufgabenspezifisch zu untersuchen.

## P.5 Provenienz und technische Kontinuität

Publizierte Ausgaben, ursprüngliche DOCX-Manuskripte, Quellenmetadaten, präregistrierte Protokolle, DATA und EVID behalten ihre historischen Identitäten. Die aktuelle Edition wird als Fortführung zitiert. Alte Sprungmarken, Dateiformate, IDs und kompatible Einstiegspunkte bleiben absichtlich bestehen, damit eine Namenskorrektur keine Quellen zerstört oder Versuche verändert. Ein neuer Dateiname ist nicht schon eine neue wissenschaftliche Untersuchung.

Die gemeinsame maschinenlesbare Benennung steht in `project_identity.json` im Repository-Hauptverzeichnis. Neue Exporte beziehen ihre Titel aus dieser Quelle. Änderungen an fremden Kopien, früher versandten Anhängen oder lokalen Arbeitsverzeichnissen außerhalb des Repository-Zugriffs werden nicht als ausgeführt behauptet.
''')
    # All existing anchors must remain valid; title replacement may remove old cover anchors.
    for name in order[:-1]:
        inherited_text = (OLD / name).read_text(encoding="utf-8")
        current_text = (NEW / name).read_text(encoding="utf-8")
        old_anchors = re.findall(r'<a id="([^"]+)"></a>', inherited_text)
        missing = [a for a in old_anchors if f'id="{a}"' not in current_text]
        if missing:
            write(NEW / name, "\n".join(f'<a id="{a}"></a>' for a in missing) + "\n\n" + current_text)
    labels = []
    for name in order:
        match = re.search(r"^# (.+)$", (NEW / name).read_text(encoding="utf-8"), re.MULTILINE)
        labels.append((name, match.group(1) if match else name))
    labels[4] = ("section-004.md", "Inhaltsverzeichnis")
    toc = "\n".join(f"- [{title}]({name})" for name, title in labels)
    write(NEW / "section-004.md", '<a id="b5d-inhaltsverzeichnis"></a>\n# Inhaltsverzeichnis\n\n' + toc)
    write(NEW / "README.md", f'''# {pub['title_en']}

## {pub['subtitle_de']}

**Thomas Heisig · MHRN · Edition 1.3 · 8 September 2026**

Current editorial source / Aktuelle redaktionelle Quelle. English main title with German subtitle; the German chapter text is retained. Naming does not promote scientific evidence. Historical editions and their citations remain unchanged.

[Publikationsübersicht](../README.md) · [Benennung und Grenzen](section-056.md) · [Editionsmanifest](manifest.json)

## Vollständiger Leseweg

{toc}

## Export and verification

The complete Markdown export is generated by `python scripts/publication_naming.py --export <outside-repository-path>` from these canonical sections. Existing Word files belong to earlier editions and are not relabelled as current. No updated DOCX is claimed by this naming-only edition.
''')
    write(NEW / "CITATION.cff", f'''cff-version: 1.2.0
message: "Cite this edition separately from the MHRN software and historical manuscripts."
title: "{pub['title_en']}"
type: book
version: "1.3"
date-released: "2026-09-08"
authors:
  - family-names: Heisig
    given-names: Thomas
repository-code: "https://github.com/{gh}"
abstract: "{pub['subtitle_de']}"
''')
    files = {p.name: {"sha256": digest(p.read_bytes()), "size": p.stat().st_size}
             for p in sorted(NEW.iterdir()) if p.is_file() and p.name != "manifest.json"}
    manifest = {"schema_version": "1.0", "edition": "1.3", "date": "2026-09-08",
                "title_en": pub["title_en"], "subtitle_de": pub["subtitle_de"],
                "section_order": order, "section_count": len(order),
                "inherited_edition": "../" + OLD.name, "authority": "interpretation_only",
                "automatic_evidence_promotion": False, "new_empirical_findings": False,
                "revision_scope": "naming_translation_and_scope_clarification",
                "files": files}
    write(NEW / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    old_index = (PUB / "README.md").read_text(encoding="utf-8")
    write(PUB / "README.md", f'''# {pub['short_title_en']}

## {pub['short_title_de']}

**{pub['title_en']}**

*{pub['subtitle_de']}*

Thomas Heisig · MHRN · Edition 1.3 · 8 September 2026.

[Die vollständige aktuelle wissenschaftliche Abhandlung lesen]({NEW.name}/README.md)

Die kapitelweise Edition 1.3 ist die redaktionelle Single Source of Truth. Sie führt alle Kapitel der Fassung 1.2 unter der neuen Benennung fort. Umfang, empirische Grenzen und Ethikregeln bleiben erhalten. Die Titeländerung ist kein neuer Funktions- oder Bewusstseinsnachweis. Die unveränderten Word-Dateien früherer Ausgaben bleiben historische Artefakte; ein aktueller DOCX-Export wird hier nicht behauptet.

[Benennung und Kontinuität](../../NAMING.md) · [Kognitionsprüfungen](../protocols/COGNITION_CONSCIOUSNESS.md) · [Wohlfahrt und Abschaltdilemma](../ethics/AI_WELFARE_POLICY.md) · [Kritikregister](../critique/CONSCIOUSNESS_CRITIQUE.md)

## Historical editions / Historische Ausgaben

[Fassung 1.2]({OLD.name}/README.md) · [Fassung 1.1](2026-09-07_ki-die-geliehene-intelligenz_v1.1/README.md) · [Lesefassung 1.0](reader/README.md) · [Word-Datei 1.0](2026-09-07_ki-die-geliehene-intelligenz/wissenschaftliche_abhandlung.docx) · [Originalpaket](archives/Brain5D_Wissenschaftliche_Abhandlung_2026-09-07.zip).

Alte Titel und Dateinamen bleiben absichtlich zitierbar. Kanonische Forschungsregister, präregistrierte Protokolle und DATA/EVID werden durch eine Publikationsrevision nicht umgeschrieben. [Katalog](catalog.json).

## Verification / Prüfung

```bash
python scripts/publication_bundle.py
python scripts/publication_revision.py
python scripts/publication_cognition.py
python scripts/publication_naming.py
```
''')
    catalog_path = PUB / "catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    item = {"id": "PUB-RECURSIVE-EPISTEMICS-20260908", "title": pub["title_en"],
            "subtitle": pub["subtitle_de"], "type": "wissenschaftliche_abhandlung",
            "author": "Thomas Heisig", "date": "2026-09-08", "version": "1.3",
            "entrypoint": "publications/README.md", "reader": f"publications/{NEW.name}/README.md",
            "snapshot": f"publications/{NEW.name}", "read_only": True,
            "authority": "interpretation_only", "automatic_evidence_promotion": False,
            "registry_role": "historical_snapshot_not_canonical_registry"}
    catalog["publications"].insert(0, item)
    catalog["current_publication"] = item["id"]
    write(catalog_path, json.dumps(catalog, ensure_ascii=False, indent=2))


def main() -> None:
    if MARKER.exists():
        print("Naming migration already applied; no sources rewritten.")
        return
    if not PLATFORM.exists():
        raise ValueError("Run the platform identity attempt before materializing URLs")
    platform = json.loads(PLATFORM.read_text(encoding="utf-8"))
    gh = platform["github"]["actual"]
    model = platform["huggingface_model"]["actual"]
    space = platform["huggingface_space"]["actual"]
    paths = tracked()
    before = {p.relative_to(ROOT).as_posix(): digest(p.read_bytes()) for p in paths if p.is_file()}
    protected = {p.relative_to(ROOT).as_posix(): digest(p.read_bytes()) for p in paths if p.is_file() and frozen(p)}
    changed = []
    for path in paths:
        rel = path.relative_to(ROOT).as_posix()
        if not path.is_file() or frozen(path) or rel.startswith(".maintenance/"):
            continue
        allowed = path.suffix in {".md", ".py", ".js", ".html", ".css", ".ps1", ".cmd", ".bat"}
        if rel.startswith(".github/workflows/"):
            allowed = True
        if not allowed or rel in {"NAMING.md", "src/identity.py", "scripts/publication_naming.py", "tests/test_mhrn_naming.py"}:
            continue
        try:
            text = path.read_bytes().decode("utf-8")
        except UnicodeDecodeError:
            continue
        after = rename_text(text, gh, model, space)
        if after != text:
            path.write_bytes(after.encode("utf-8"))
            changed.append(rel)
    # Package metadata changes; don't touch immutable tag names or data magic.
    path = ROOT / "pyproject.toml"
    text = path.read_text(encoding="utf-8").replace('name = "brain5d-core"', 'name = "mhrn-core"')
    text = text.replace('description = "Sparse 5D spiking-neural simulation with observable plasticity."',
                        'description = "Multi-scale homeostatic recurrent spiking-neural research architecture."')
    text = text.replace('  "5D",', '  "recurrent-networks",')
    text = text.replace("github.com/Thomas-Heisig/Brain-5D", "github.com/" + gh)
    write(path, text)
    path = ROOT / "src/version.py"
    text = path.read_text(encoding="utf-8").replace('_pkg_version("brain5d-core")', '_pkg_version("mhrn-core")')
    text += '\n# Public MHRN names; historical imports remain supported.\nMHRN_VERSION: str = BRAIN5D_VERSION\nMHRN_VERSION_DISPLAY: str = BRAIN5D_VERSION_DISPLAY\n'
    write(path, text)
    write(ROOT / "src/__init__.py", '''"""MHRN package with backwards-compatible process configuration."""

import os

from .identity import legacy_environment_aliases

os.environ.update(legacy_environment_aliases(dict(os.environ)))
''')
    for rel in ("start.ps1", "start.cmd", "stop.ps1", "stop.cmd"):
        path = ROOT / rel
        if path.exists():
            text = path.read_bytes().decode("utf-8").replace("scripts\\brain5d_launcher.py", "scripts\\mhrn_launcher.py").replace('"brain5d_launcher.py"', '"mhrn_launcher.py"')
            path.write_bytes(text.encode("utf-8"))
    # Documentation wrapper, not a claim of a changed observation/state schema.
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    prefix = f'''# {IDENTITY['project']['title_en']} (MHRN)

## {IDENTITY['project']['subtitle_de']}

**{IDENTITY['project']['description_en']}**

*{IDENTITY['project']['description_de']}*

[Scientific treatise / Wissenschaftliche Abhandlung](research/publications/README.md) · [Naming and compatibility / Benennung und Kompatibilität](NAMING.md).

MHRN is the current project name. Historical publications, scientific coordinates, evidence identifiers and compatible `.b5d` files retain their original meaning. The name does not establish consciousness or a performance advantage. The observed platform migration results are in [the status record](docs/05-quality/mhrn-platform-migration.json).

'''
    write(path, prefix + text)
    path = ROOT / "HF_README.md"
    text = path.read_text(encoding="utf-8")
    text = text.replace("title: MHRN", "title: MHRN").replace("library_name: brain5d-core", "library_name: mhrn-core")
    text = text.replace("short_description: Sparse 5D spiking-neural research dashboard", "short_description: Multi-scale homeostatic recurrent spiking research")
    text = text.replace("  - 5D\n", "  - recurrence\n")
    text = text.replace("language:\n  - en", "language:\n  - en\n  - de")
    text = text.replace("# MHRN\n", f"# {IDENTITY['project']['title_en']} (MHRN)\n\n## {IDENTITY['project']['subtitle_de']}\n", 1)
    # Never present an old snapshot as the HEAD after the rename.
    text = re.sub(r"## Current baseline[^\n]*\n.*?(?=\n## )", "## Status and provenance\n\nThe package version describes software, not validated cognition. GitHub main is canonical; this mirror is derived. Current verification must be checked against its exact source hashes in the repository. Historical reports remain dated records.\n", text, flags=re.S)
    write(path, text)
    path = ROOT / "src/dashboard/static/index.html"
    text = path.read_text(encoding="utf-8")
    text = text.replace('<p class="eyebrow">MHRN</p>', '<p class="eyebrow">MHRN</p>\n      <p class="project-title">Multi-Scale Homeostatic Recurrence Network</p>\n      <p class="project-subtitle">Mehrskaliges homöostatisches Rekurrenznetzwerk</p>')
    write(path, text)
    path = ROOT / "src/dashboard/static/styles.css"
    with path.open("a", encoding="utf-8") as f:
        f.write('\n/* Bilingual identity; wrap naturally on narrow dashboards. */\n.project-title, .project-subtitle { margin: 0.15rem 0; max-width: 36rem; overflow-wrap: anywhere; }\n.project-title { font-size: 0.9rem; font-weight: 600; }\n.project-subtitle { font-size: 0.8rem; opacity: 0.8; }\n')
    path = ROOT / "src/dashboard/static/file-viewer.js"
    text = path.read_text(encoding="utf-8").replace("publications/reader/README.md", "publications/README.md")
    write(path, text)
    # Versioned current publication with historical evidence untouched.
    build_publication(gh, model, space)
    write(ROOT / "CITATION.cff", f'''cff-version: 1.2.0
message: "Cite the MHRN software and the Recursive Epistemics publication separately."
title: "Multi-Scale Homeostatic Recurrence Network (MHRN)"
abstract: "Mehrskaliges homöostatisches Rekurrenznetzwerk. A Spiking Neural Architecture with Topological Plasticity."
type: software
version: "0.5.0a7"
authors:
  - family-names: Heisig
    given-names: Thomas
repository-code: "https://github.com/{gh}"
license: MIT
''')
    write(ROOT / "docs/06-research/RECURSIVE_EPISTEMICS.md", '''# Recursive Epistemics

## Rekursive Epistemik

Die [aktuelle vollständige wissenschaftliche Abhandlung](../../research/publications/README.md) ist die einzige redaktionelle Quelle. Ihre Titel werden aus [project_identity.json](../../project_identity.json) übernommen. Frühere Dissertation-Dateinamen und Ausgaben sind historische Quellen, keine aktuellen Exportfassungen und keine Qualifikationsbehauptungen.

[Benennung und Migration](../../NAMING.md).
''')
    for rel in ("research/README.md", "docs/08-roadmap/TODO.md"):
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        link = "../NAMING.md" if rel == "research/README.md" else "../../NAMING.md"
        text = f"## Naming update — 2026-09-08\n\nMHRN / Multi-Scale Homeostatic Recurrence Network. Publication: Recursive Epistemics / Rekursive Epistemik. [Migration and compatibility]({link}). Historical scientific artifacts remain unchanged. Platform completion is recorded separately from requested names.\n\n" + text
        write(path, text)
    # The two mutable publication indexes are the only exceptions within public history.
    protected.pop("research/publications/README.md", None)
    protected.pop("research/publications/catalog.json", None)
    mismatches = [name for name, sha in protected.items() if digest((ROOT / name).read_bytes()) != sha]
    if mismatches:
        raise ValueError("Historical bytes changed: " + ", ".join(mismatches))
    changed = [{"path": name, "before_sha256": sha, "after_sha256": digest((ROOT / name).read_bytes())}
               for name, sha in before.items() if (ROOT / name).is_file() and digest((ROOT / name).read_bytes()) != sha]
    retained = []
    for path in tracked():
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError:
            continue
        if re.search(r"Brain.?5D|BRAIN5D|brain5d|geliehene", text):
            rel = path.relative_to(ROOT).as_posix()
            retained.append({"path": rel, "reason": "historical_source" if frozen(path) else "compatibility_identifier_or_citation_or_platform_pending"})
    report = {"scope": "active_names_not_scientific_history", "project": "MHRN", "edition": "1.3",
              "changed_files": changed, "preserved_sha256": protected,
              "retained_legacy_references": retained, "external_unreachable_copies_modified": False,
              "new_empirical_evidence": False}
    write(ROOT / "docs/05-quality/mhrn-naming-audit.json", json.dumps(report, ensure_ascii=False, indent=2))
    write(MARKER, json.dumps({"applied": True, "edition": NEW.name, "changed_files": len(changed)}, indent=2))
    print(f"MHRN migration: {len(changed)} active files changed; {len(protected)} historical files preserved.")


if __name__ == "__main__":
    main()
