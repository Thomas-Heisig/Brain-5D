"""One-time additive publication integration; never change scientific registries."""
from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding='utf-8')
    if new in text:
        return
    if old not in text:
        raise ValueError('Expected integration anchor not found: ' + path)
    target.write_text(text.replace(old, new, 1), encoding='utf-8')


replace_once('src/dashboard/research_source.py', '        "literature",\n', '        "literature",\n        "publications",\n')
replace_once('src/dashboard/file_rendering.py', '        "experiments",\n', '        "experiments",\n        "publications",\n')
replace_once('.pre-commit-config.yaml', '\nrepos:\n', '\n# Frozen publication bytes are checked by Publication Integrity CI, not reformatted.\nexclude: ^research/publications/2026-09-07_ki-die-geliehene-intelligenz/\n\nrepos:\n')
for name, link in [('README.md', 'research/publications/README.md'), ('research/README.md', 'publications/README.md')]:
    path = Path(name)
    text = path.read_text(encoding='utf-8')
    if '## Wissenschaftliche Abhandlung und Publikationsarchiv' not in text:
        text = text.rstrip() + '\n\n## Wissenschaftliche Abhandlung und Publikationsarchiv\n\n'
        text += '[KI - Die geliehene Intelligenz: vollstaendige wissenschaftliche Abhandlung](' + link + ')\n\n'
        text += 'Die Research-Kategorie `publications` enthaelt die Word- und Markdown-Fassung, die komplette Literaturdatenbank, Forschungsfragen, Hypothesen, Ergebnisdarstellungen, Originalmanuskripte und alle Begleitdateien. Eine kapitelweise Lesefassung ist im zentralen File Viewer vollstaendig zugaenglich. Datierte Originale bleiben unveraendert und schreibgeschuetzt; kanonische Register und Evidenzfreigaben werden nicht ersetzt.\n'
        path.write_text(text, encoding='utf-8')
print('STATIC FILES', '\n'.join(p.name for p in Path('src/dashboard/static').iterdir() if p.is_file()))
for name in ['index.html', 'app.js', 'file-viewer.js']:
    path = Path('src/dashboard/static') / name
    if path.exists():
        lines = path.read_text(encoding='utf-8').splitlines()
        matches = [i for i, line in enumerate(lines) if any(x in line for x in ['research-tree', 'researchPanel', 'fileViewer.open', 'openFile(', 'research-docs', 'research-tab', 'Research & Docs'])]
        for i in matches[:12]:
            print('UI_ANCHOR', name, i+1, '\n'.join(lines[max(0,i-2):i+4]))
