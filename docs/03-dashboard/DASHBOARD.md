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

Binäre Dateien werden als solche markiert und bei bekannten Medientypen mit dem
passenden Player geöffnet. Unbekannte Textdateien werden als Plaintext angezeigt.

## Sicherheit

Alpha.5 ist standardmaessig nur auf `127.0.0.1` gedacht. Es gibt noch keine
Authentifizierung. Der Server ist read-only und darf deshalb in dieser Phase
keine Manipulator-, Reward- oder Self-Organization-Schreiboperationen anbieten.
Vor einer extern erreichbaren API muessen Authentifizierung, Rechte und Audit-Log
implementiert werden.
