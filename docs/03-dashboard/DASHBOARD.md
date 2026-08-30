# Brain-5D Operator Dashboard

## Ziel

Das Dashboard ist eine lokale, read-only Operator-Konsole fuer Brain-5D. Es soll
nicht die Simulationslogik ersetzen, sondern deren Zustand nachvollziehbar machen.
Die erste Version ist absichtlich ohne zusaetzliche Web-Framework-Abhaengigkeit
implementiert und verwendet nur die Python-Standardbibliothek plus die bereits
vorhandene `.b5d`-Storage-Schicht.

## Ansichten

- Core: Tick, Neuronen, Synapsen, Spikes, Core-Latenz, mittlere Energie
- Learning: STDP-Updates, Reward-Updates, Rewards, Pending Rewards
- Storage: Queue-Tiefe, Bytes, Deltas, Write-/Commit-Latenz, Drops
- Self-Organization: erzeugte/entfernte Neuronen und Synapsen
- Heatmap: Activity, Weights und Energy direkt aus einem `.b5d` Snapshot
- Roadmap: sichtbarer Entwicklungsstatus von Persistenz bis nutzbarer KI

## Start

```powershell
python -m src.dashboard --snapshot artifacts/brain5d_snapshot.b5d
```

Danach:

```text
http://127.0.0.1:8765
```

Ohne `--snapshot` funktioniert die Operator-Oberflaeche weiterhin; lediglich die
Lazy-Heatmap ist dann nicht verfuegbar.

## API

### `GET /healthz`

Healthcheck des lokalen Dashboard-Servers.

### `GET /api/status`

Liefert den zuletzt publizierten `DashboardSnapshot` als JSON.

### `GET /api/heatmap?kind=activity`

Unterstuetzte Werte:

- `activity`
- `weights`
- `energy`

Die Projektion wird per `B5DLazyProjector` direkt aus der mmap-basierten
Snapshot-Datei erzeugt.

## Architektur

```text
Simulation / Storage / Learning
            |
            | immutable telemetry snapshots
            v
    DashboardStateStore
            |
            +---- /api/status
            |
.b5d -------+---- SnapshotHeatmapSource ---- /api/heatmap
            |
            v
       Browser UI
```

Der HTTP-Worker liest niemals direkt aus einem mutierenden `NeuralNetwork`.
Damit bleibt die Synchronisationsgrenze explizit.

## BibTeX-Viewer

Der Dashboard-Viewer erkennt `.bib`-Dateien automatisch und öffnet sie im
dedizierten BibTeX-Viewer (`bibtex-viewer.js`). Dieser bietet:

- **Tabellarische Ansicht**: Sortierbare Tabelle mit Key, Autor, Titel, Jahr, Typ, Status
- **Code-Ansicht**: Raw-BibTeX mit Syntax-Highlighting
- **Zitierfunktion**: Kopieren als `(Autor, Jahr)` oder als BibTeX-Snippet
- **Export**: Alle Einträge als BibTeX kopieren oder als `.bib`-Datei herunterladen
- **DOI-Link**: Öffnet `doi.org/…` in neuem Tab
- **Validierung**: Prüft Pflichtfelder, Jahreszahl und DOI-Format
- **Footer-Statistiken**: Anzahl Entries, Artikel, Bücher, Inproceedings, mit DOI

Die BibTeX-Dateien liegen unter `research/literature/`.

## Dateiformat-Unterstützung

Der integrierte Datei-Manager erkennt die gängigen Formate in `research/` und
`docs/` und rendert sie direkt im Browser:

| Format | Erweiterungen | Darstellung |
|--------|---------------|-------------|
| Markdown | `.md`, `.markdown` | Gerenderte HTML-Ansicht |
| Bilder | `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.svg`, `.bmp` | Inline-Bild |
| Videos | `.mp4`, `.webm`, `.ogg`, `.mov`, `.avi` | HTML5-Video-Player |
| Audio | `.mp3`, `.wav`, `.flac`, `.aac`, `.m4a`, `.opus` | HTML5-Audio-Player |
| PDF | `.pdf` | Eingebetteter PDF-Viewer (`<iframe>`) |
| Tabellen | `.xlsx`, `.xls`, `.xlsm`, `.ods` | Interaktive Tabelle mit Sheet-Tabs (SheetJS) |
| Word | `.docx`, `.doc` | HTML-Vorschau (mammoth.js) |
| CSV | `.csv` | Tabelle mit sortierbarem Header |
| JSON | `.json`, `.schema.json`, `.ipynb` | Syntax-highlightete Baumansicht |
| Code | `.py`, `.js`, `.ts`, `.css`, `.html`, `.sh`, `.bat`, `.ps1`, `.toml`, `.xml`, `.cfg`, `.conf`, `.ini`, `.tex`, `.rst`, `.dockerfile` | Syntax-Highlighting |
| BibTeX | `.bib` | Strukturierter BibTeX-Viewer |
| Patches | `.patch`, `.diff` | Farblich markierte Diff-Ansicht |
| Jupyter Notebook | `.ipynb` | Gerenderte Zellen-Ansicht mit Code, Markdown und Outputs |
| Log-Dateien | `.log` | Level-basierte farbliche Hervorhebung |
| Diagramme | `.dot`, `.gv`, `.puml`, `.plantuml` | Interaktive Graphviz/PlantUML-Darstellung |

Binäre Dateien werden als solche markiert und bei bekannten Medientypen mit dem
passenden Player geöffnet. Unbekannte Textdateien werden als Plaintext angezeigt.

### Text- und Code-Editor

Für bearbeitbare Textformate (Markdown, Python, JSON, YAML, TOML, INI, Config,
BibTeX, Patch, Shell-Skripte, TypeScript, HTML, CSS, C/C++, Rust, Go, Java,
Kotlin und weitere) zeigt der Viewer einen **✏️ Edit**-Button an. Im
Editor-Modus kann der Inhalt direkt im Browser geändert, gespeichert oder
verworfen werden.

- Markdown-Dateien werden mit einer **Split-Ansicht** geöffnet: links der
  Quelltext, rechts die gerenderte Vorschau.
- Alle anderen Textdateien verwenden ein responsives `<textarea>` mit
  automatischer Höhenanpassung.
- Beim Speichern wird automatisch eine `.bak`-Sicherungskopie der
  Originaldatei erstellt.
- **Tastaturkürzel**: `Ctrl+S` speichert, `Esc` bricht ab.
- **Auto-Save**: Alle 30 Sekunden wird automatisch gespeichert, solange
  der Editor aktiv ist.
- **Diff-Ansicht**: Über den "Diff"-Button werden Änderungen gegenüber
  der ursprünglichen Datei als farbige Zeilenübersicht angezeigt.
- **Wiederherstellen**: Über "Restore" kann der Inhalt der letzten
  `.bak`-Sicherung zurückgeladen werden.
- **BibTeX-Formular-Editor**: `.bib`-Dateien bieten eine feldbasierte
  Bearbeitungsansicht mit Auswahl des Entry-Typs und direktem Speichern.
- Speicher-Endpunkt: `PUT /api/files/save/{path}?source={research|docs}`

## Erweiterte Viewer-Features

Jeder Text-/Code-Viewer bietet zusätzliche Werkzeuge über die
Datei-Header-Leiste:

| Feature | Button | Beschreibung |
|---------|--------|--------------|
| Suche im Dokument | 🔍 Search | In-Document-Suche mit Treffer-Navigation (`Ctrl+F`) |
| Git-History | 🕰️ History | Zeigt `git log --follow` für die Datei an |
| Notizen / Metadaten | 📝 Notes | Sidecar-Editor für `.meta.yaml`-Dateien pro Dokument |
| Dokumentenanalyse | 🤖 Analyze | Lokale Statistik, Keywords, Lesbarkeit, Sentiment, Zusammenfassung |
| Export | ⬇️ Export | Markdown → HTML/DOCX/MD Download |
| Vollbild | 🖥️ Full | Vollbildmodus für den Viewer |

### Research-Registry-Kartenansicht

YAML-Dateien unter `research/registry/` (Fragen, Hypothesen, Claims,
Quellen, Methoden) werden automatisch als strukturierte Karten gerendert.
Jede Karte zeigt ID, Status, Typ, Titel, Domain, Verlinkungen und
Zeitstempel übersichtlich an.

### API-Endpunkte des Datei-Managers

- `GET /api/files/tree?source={research|docs}` — Verzeichnisbaum
- `GET /api/files/content/{path}?source={research|docs}` — Datei-Inhalt
- `PUT /api/files/save/{path}?source={research|docs}` — Datei speichern
- `GET /api/files/history/{path}?source={research|docs}` — Git-History
- `GET /api/files/meta/{path}?source={research|docs}` — Metadaten laden
- `PUT /api/files/meta/{path}?source={research|docs}` — Metadaten speichern
- `GET /api/files/analyze/{path}?source={research|docs}` — Dokumentenanalyse
- `GET /api/files/export/{path}?source={research|docs}&format={html|docx|md}` — Export

## Sicherheit

Alpha.5 ist standardmaessig nur auf `127.0.0.1` gedacht. Es gibt noch keine
Authentifizierung. Der Server ist read-only und darf deshalb in dieser Phase
keine Manipulator-, Reward- oder Self-Organization-Schreiboperationen anbieten.
Vor einer extern erreichbaren API muessen Authentifizierung, Rechte und Audit-Log
implementiert werden.
