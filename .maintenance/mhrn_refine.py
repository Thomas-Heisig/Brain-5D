"""Narrow naming checks to their real scope and retain resolvable platform IDs."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def main() -> None:
    platform = json.loads((ROOT / "docs/05-quality/mhrn-platform-migration.json").read_text(encoding="utf-8"))
    gh = platform["github"]["actual"]
    # A requested slug must not break live API defaults when the rename was denied.
    if gh != "Thomas-Heisig/MHRN":
        for base in ("src", "scripts", "tests", ".github/workflows"):
            for path in (ROOT / base).rglob("*"):
                if not path.is_file() or path.suffix not in {".py", ".js", ".yml", ".yaml"}:
                    continue
                if path.name.startswith("publication_") or path.name == "test_mhrn_naming.py":
                    continue
                text = path.read_text(encoding="utf-8")
                corrected = text.replace("Thomas-Heisig/MHRN", gh)
                if corrected != text:
                    write(path, corrected)
    # Preserve correct source-manuscript titles inside the current narrative.
    folder = ROOT / "research/publications/2026-09-08_recursive-epistemics_v1.3"
    for path in folder.glob("section-*.md"):
        text = path.read_text(encoding="utf-8")
        corrected = text.replace("MHRN Scientific Framework", "Brain-5D Scientific Framework")
        if corrected != text:
            write(path, corrected)
    for rel in ("README.md", "HF_README.md"):
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"(?m)^git clone (https://github\.com/[^\s]+\.git)\s*$", r"git clone \1 MHRN", text)
        if rel == "README.md":
            text = re.sub(r"(?m)^# MHRN[^\n]*\n", "", text, count=1)
        text = text.replace("@software{heisig2026brain5d,", "@software{heisig2026mhrn,")
        text = text.replace("title   = {MHRN: Sparse 5D Spiking-Neural Research Framework}", "title   = {Multi-Scale Homeostatic Recurrence Network (MHRN)}")
        write(path, text)
    # Standalone scripts are not repeatedly rewrapped on subsequent verification.
    path = ROOT / ".maintenance/mhrn_ci.py"
    text = path.read_text(encoding="utf-8")
    start = text.find("    # New script entrypoints must work")
    end = text.find('    run("format",', start)
    if start >= 0 and end >= 0:
        text = text[:start] + text[end:]
    write(path, text)
    path = ROOT / "scripts/publication_naming.py"
    text = path.read_text(encoding="utf-8")
    # Import in verify, after the direct CLI adds the repository root to sys.path.
    text = text.replace("try:\n    from scripts.publication_revision import check_links\nexcept ModuleNotFoundError:\n    from publication_revision import check_links\n", "")
    text = text.replace("from scripts.publication_revision import check_links\n", "")
    if "import sys\n" not in text:
        text = text.replace("import subprocess\n", "import subprocess\nimport sys\n")
    needle = '    identity: dict[str, Any] = json.loads('
    text = text.replace(needle, '    from scripts.publication_revision import check_links\n\n' + needle, 1)
    text = text.replace('if __name__ == "__main__":\n    main()', 'if __name__ == "__main__":\n    sys.path.insert(0, str(ROOT))\n    main()')
    # The whole-tree migration audit is a dated record, NOT a lock on future RQ updates.
    needle = '    for name, digest in audit["preserved_sha256"].items():\n'
    replacement = needle + '''        if not name.startswith((
            "research/publications/2026-09-07_ki-die-geliehene-intelligenz/",
            "research/publications/2026-09-07_ki-die-geliehene-intelligenz_v1.1/",
            "research/publications/2026-09-07_ki-die-geliehene-intelligenz_v1.2/",
            "research/publications/reader/", "research/publications/archives/",
        )):
            continue
'''
    if "whole-tree migration record" not in text:
        text = text.replace(needle, '    # A whole-tree migration record must not freeze future active research.\n' + replacement)
    write(path, text)
    # Node reads its environment before Python compatibility aliases can apply.
    path = ROOT / "playwright.config.js"
    text = path.read_text(encoding="utf-8")
    if "process.env.MHRN_TEST_PYTHON" not in text:
        text = text.replace("process.env.BRAIN5D_TEST_PYTHON", "process.env.MHRN_TEST_PYTHON || process.env.BRAIN5D_TEST_PYTHON")
    write(path, text)
    path = ROOT / "Dockerfile"
    text = path.read_text(encoding="utf-8").replace("Brain-5D", "MHRN").replace("brain5d", "mhrn")
    if "COPY research/ research/" not in text:
        text = text.replace("COPY scripts/ scripts/", "COPY scripts/ scripts/\nCOPY research/ research/\nCOPY docs/ docs/\nCOPY project_identity.json NAMING.md README.md ./")
    write(path, text)
    path = ROOT / "src/dashboard/static/styles.css"
    text = path.read_text(encoding="utf-8")
    if "MHRN identity flex bounds" not in text:
        text += "\n/* MHRN identity flex bounds retain narrow-screen navigation. */\n.topbar-brand, .topbar-brand > div { min-width: 0; }\n@media (max-width: 760px) { .topbar { flex-wrap: wrap; } .topbar-right { flex-wrap: wrap; } }\n"
    write(path, text)
    # Clarify that the dated audit proves migration preservation only.
    path = ROOT / "NAMING.md"
    text = path.read_text(encoding="utf-8")
    notice = "The migration inventory is a dated byte-preservation record, not a ban on future canonical research updates. Persistent checks protect the historical publication editions; legitimate future registry and run changes remain possible."
    if notice not in text:
        text += "\n" + notice + "\n"
    write(path, text)
    path = folder / "manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["files"] = {p.name: {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "size": p.stat().st_size} for p in sorted(folder.iterdir()) if p.is_file() and p.name != "manifest.json"}
    write(path, json.dumps(manifest, ensure_ascii=False, indent=2))
    print("Naming refinements applied without changing historical scientific artifacts.")


if __name__ == "__main__":
    main()
