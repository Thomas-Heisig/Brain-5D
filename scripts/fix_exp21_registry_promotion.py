"""One-time cleanup after promoting EXP-GEN-0021 proposals to canonical registries."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPLACEMENTS = {
    "RQ-LEARN-INTERF-001": "RQ-LIFE-001",
    "H-LEARN-INTERF-001-A": "H-LIFE-001-A",
    "PREREG-LEARN-INTERF-001": "PREREG-LIFE-001",
}

PATHS = (
    ROOT / "research/registry/questions.yaml",
    ROOT / "research/registry/hypotheses.yaml",
    ROOT / "research/protocols/EXP_GEN_0021_OPERATIONAL_PROTOCOLS.json",
    ROOT / "research/preregistrations/PREREG-LEARN-INTERF-001.json",
    ROOT / "src/research/experiment_summary.py",
    ROOT / "tests/test_exp21_operational_protocols.py",
    ROOT / "scripts/apply_exp21_operationalization.py",
)


def main() -> None:
    for path in PATHS:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for old, new in REPLACEMENTS.items():
            text = text.replace(old, new)
        path.write_text(text, encoding="utf-8")

    old_prereg = ROOT / "research/preregistrations/PREREG-LEARN-INTERF-001.json"
    new_prereg = ROOT / "research/preregistrations/PREREG-LIFE-001.json"
    if old_prereg.exists() and not new_prereg.exists():
        old_prereg.rename(new_prereg)


if __name__ == "__main__":
    main()
