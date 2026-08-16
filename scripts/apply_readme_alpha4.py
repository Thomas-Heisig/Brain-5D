"""Insert/update the alpha.4 README section without overwriting the rest."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
BLOCK = (ROOT / "README_ALPHA4_BLOCK.md").read_text(encoding="utf-8")
START = "<!-- BRAIN5D:ALPHA4:START -->"
END = "<!-- BRAIN5D:ALPHA4:END -->"


def main() -> int:
    text = README.read_text(encoding="utf-8") if README.exists() else "# Brain-5D\n\n"
    if START in text and END in text:
        before = text.split(START, 1)[0]
        after = text.split(END, 1)[1]
        text = before + BLOCK + after
    else:
        text = text.rstrip() + "\n\n" + BLOCK + "\n"
    README.write_text(text, encoding="utf-8", newline="\n")
    print("README alpha.4 block updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
