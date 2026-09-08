"""Materialize and refine naming without retrying denied platform operations."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    if not (ROOT / ".maintenance/mhrn-migration-complete.json").exists():
        subprocess.run([sys.executable, ".maintenance/mhrn_migrate.py"], cwd=ROOT, check=True)
    marker = ROOT / ".maintenance/mhrn-refinement-complete.json"
    if not marker.exists():
        subprocess.run([sys.executable, ".maintenance/mhrn_refine.py"], cwd=ROOT, check=True)
        marker.write_text('{"applied":true,"scope":"names_and_layout"}\n', encoding="utf-8")
    path = ROOT / ".maintenance/mhrn_ci.py"
    text = path.read_text(encoding="utf-8")
    needle = '    run("format", [sys.executable, "-m", "black", "src", "tests", "scripts"])'
    if "Workflow files are committed through" not in text:
        text = text.replace(needle, '    # Workflow files are committed through the authorized connector, not the runner token.\n    subprocess.run(["git", "restore", "--source=HEAD", "--staged", "--worktree", "--", ".github/workflows"], check=True)\n' + needle)
    path.write_text(text, encoding="utf-8")
    # Prevent the expanded bilingual header from covering sticky navigation.
    path = ROOT / "src/dashboard/static/frontend-architecture.js"
    text = path.read_text(encoding="utf-8")
    if "mhrnStickyInsets" not in text:
        needle = '  topbar.insertAdjacentElement("afterend", nav);'
        insertion = '''
  const mhrnStickyInsets = () => {
    const headerHeight = Math.ceil(topbar.getBoundingClientRect().height);
    const navHeight = Math.ceil(nav.getBoundingClientRect().height);
    document.documentElement.style.setProperty('--dashboard-topbar-height', `${headerHeight}px`);
    document.documentElement.style.setProperty('--mhrn-sticky-offset', `${headerHeight + navHeight + 12}px`);
  };
  mhrnStickyInsets();
  if (typeof ResizeObserver === 'function') {
    const observer = new ResizeObserver(mhrnStickyInsets);
    observer.observe(topbar);
    observer.observe(nav);
  } else {
    window.addEventListener('resize', mhrnStickyInsets);
  }
'''
        if needle not in text:
            raise ValueError("Primary navigation insertion point changed")
        text = text.replace(needle, needle + insertion)
        path.write_text(text, encoding="utf-8")
    path = ROOT / "src/dashboard/static/styles.css"
    text = path.read_text(encoding="utf-8")
    if "MHRN sticky navigation clearance" not in text:
        text += '''
/* MHRN sticky navigation clearance uses the measured bilingual header height. */
.brain5d-primary-nav { top: var(--dashboard-topbar-height, 0px) !important; }
html { scroll-padding-top: var(--mhrn-sticky-offset, 180px); }
[data-workspace-view], .tab-content button, .tab-content a { scroll-margin-top: var(--mhrn-sticky-offset, 180px); }
'''
        path.write_text(text, encoding="utf-8")
    # Keep the original assertion; expose the backend reason rather than hiding it.
    path = ROOT / "tests/browser/fullstack.spec.js"
    text = path.read_text(encoding="utf-8").replace('expect(result.failed).toBe(0);', 'expect(result.failed, JSON.stringify(result)).toBe(0);')
    path.write_text(text, encoding="utf-8")
    # Count what the persistent check actually protects, not the whole dated audit.
    path = ROOT / "scripts/publication_naming.py"
    text = path.read_text(encoding="utf-8")
    if "history_checked = 0" not in text:
        text = text.replace('    # A whole-tree migration record', '    history_checked = 0\n    # A whole-tree migration record')
        text = text.replace('        path = (root / name).resolve()', '        history_checked += 1\n        path = (root / name).resolve()')
        text = text.replace('"historical_files": len(audit["preserved_sha256"])', '"historical_files": history_checked')
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
