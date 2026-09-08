"""Repair the actual browser failures without weakening guards or assertions."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    subprocess.run([sys.executable, ".maintenance/mhrn_final_polish.py"], cwd=ROOT, check=True)
    path = ROOT / "scripts/browser_server.py"
    text = path.read_text(encoding="utf-8")
    if '            "ethics",' not in text:
        needle = '            "publications",\n'
        if needle not in text:
            raise ValueError("Browser fixture inventory changed; manual inspection required")
        text = text.replace(needle, needle + '            "ethics",\n')
        path.write_text(text, encoding="utf-8")
    path = ROOT / "src/dashboard/static/styles.css"
    text = path.read_text(encoding="utf-8")
    if "MHRN contextual navigation clearance" not in text:
        text += '''
/* MHRN contextual navigation clearance: keep controls below the taller title
 * and primary navigation, including when the page was opened from the footer. */
#tab-gate > .workspace-view-tabs {
  position: sticky;
  top: var(--mhrn-sticky-offset, 200px);
  z-index: 12;
  background: var(--shell-surface-strong, var(--panel)) !important;
}
'''
        path.write_text(text, encoding="utf-8")
    path = ROOT / ".maintenance/mhrn_prepare.py"
    text = path.read_text(encoding="utf-8").replace('if "workflow files are committed through" not in text:', 'if "Workflow files are committed through" not in text:')
    path.write_text(text, encoding="utf-8")
    # The recorded old IDs are intentional until an owner confirms the rename.
    path = ROOT / "huggin.ps1"
    text = path.read_text(encoding="utf-8")
    text = text.replace('https://github.com/Thomas-Heisig/MHRN', 'https://github.com/Thomas-Heisig/Brain-5D')
    path.write_text(text, encoding="utf-8")
    print("Copied the real ethics state into the isolated fixture and corrected contextual navigation stacking.")


if __name__ == "__main__":
    main()
