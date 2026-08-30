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

## Sicherheit

Alpha.5 ist standardmaessig nur auf `127.0.0.1` gedacht. Es gibt noch keine
Authentifizierung. Der Server ist read-only und darf deshalb in dieser Phase
keine Manipulator-, Reward- oder Self-Organization-Schreiboperationen anbieten.
Vor einer extern erreichbaren API muessen Authentifizierung, Rechte und Audit-Log
implementiert werden.
