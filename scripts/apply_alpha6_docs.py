"""Append alpha.6 roadmap/TODO markers without replacing existing documentation."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START = "<!-- BRAIN5D:ALPHA6-COGNITIVE-BRIDGE:START -->"
END = "<!-- BRAIN5D:ALPHA6-COGNITIVE-BRIDGE:END -->"
BLOCK = f"""\n{START}\n## v0.5.0-alpha.6 — Cognitive Bridge Contracts\n\n- [ ] chronic homeostasis signals\n- [ ] growth budgets and structural costs\n- [ ] anti-oscillation between neurogenesis and pruning\n- [ ] neuron/synapse age tracking\n- [x] SignalFrame contract\n- [x] SignalInterpreter foundation\n- [x] LanguageModelBackend protocol\n- [x] NullLanguageBackend, disabled by default\n- [x] provenance-bearing KnowledgeItem/SourceRecord contracts\n- [ ] local language model backend (alpha.7)\n- [ ] Wikipedia/web retrieval adapter (v0.6+)\n- [ ] deterministic knowledge-learning experiment (v0.7)\n\nHard rule: the Language Organ never owns the Brain-5D runtime loop and never mutates SNN\nweights, structural plasticity, or runtime execution directly.\n{END}\n"""

CANDIDATES = (
    ROOT / "docs" / "Roadmap" / "ROADMAP_V05_ONWARD.md",
    ROOT / "docs" / "ROADMAP_TO_USABLE_AI.md",
    ROOT / "TODO.md",
)


def update(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    if START in text and END in text:
        before = text.split(START, 1)[0].rstrip()
        after = text.split(END, 1)[1].lstrip("\r\n")
        text = before + BLOCK + ("\n" + after if after else "")
    else:
        text = text.rstrip() + "\n" + BLOCK
    path.write_text(text, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    updated = [str(path.relative_to(ROOT)) for path in CANDIDATES if update(path)]
    if not updated:
        print("No supported roadmap/TODO file found; no existing file was modified.")
        return 0
    print("Updated:")
    for path in updated:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
