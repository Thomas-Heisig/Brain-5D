"""Update repository metadata and roadmap markers for v0.4.0-alpha.6."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def update_version() -> None:
    """Advance package metadata from alpha.5 to alpha.6 when present."""

    path = ROOT / "pyproject.toml"
    text = path.read_text(encoding="utf-8")
    text = text.replace('version = "0.4.0a5"', 'version = "0.4.0a6"')
    text = text.replace('version = "0.4.0a4"', 'version = "0.4.0a6"')
    path.write_text(text, encoding="utf-8")


def append_once(path: Path, marker: str, section: str) -> None:
    """Append a documentation section once."""

    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if marker in text:
        return
    separator = "\n" if text.endswith("\n") or not text else "\n\n"
    path.write_text(text + separator + section.rstrip() + "\n", encoding="utf-8")


def update_docs() -> None:
    """Link the research alignment and deterministic restore contract."""

    append_once(
        ROOT / "README.md",
        "<!-- alpha6-strategy -->",
        """<!-- alpha6-strategy -->\n"
        "## Strategy and deterministic restore\n\n"
        "The persistence quality gate now distinguishes compact `.b5d` snapshots "
        "from deterministic checkpoints. See `docs/DETERMINISTIC_RESTORE.md`. "
        "Research and roadmap alignment is documented in "
        "`docs/RESEARCH_ALIGNMENT.md`.""",
    )
    append_once(
        ROOT / "docs" / "ROADMAP_TO_USABLE_AI.md",
        "<!-- research-alignment-alpha6 -->",
        """<!-- research-alignment-alpha6 -->\n"
        "## Research alignment update\n\n"
        "The roadmap now treats embodiment, continual-learning retention, causal "
        "evaluation and neuro-symbolic composition as explicit later-stage "
        "benchmarks. See `docs/RESEARCH_ALIGNMENT.md` for the mapping from "
        "`Analyse_Deepseek.md`, `Der_weg_zur_KI.md` and `Research.md`.""",
    )


def main() -> None:
    """Apply alpha.6 repository metadata updates."""

    update_version()
    update_docs()
    print("alpha.6 metadata updated")


if __name__ == "__main__":
    main()
