# Wissenschaftliche Publikationen

## KI - Die geliehene Intelligenz

**Wissenschaftliche Abhandlung von Thomas Heisig, Fassung vom 7. September 2026.**

[Abhandlung kapitelweise im File Viewer lesen](reader/README.md)

Die vollstaendige Publikation verbindet die drei Originalmanuskripte, technische und philosophische Betrachtungen, Forschungsfragen, Hypothesen, Berichtsauswertungen, Literatur und Reproduktionsmaterialien. Der datierte Ordner ist ein unveraenderter Publikationsstand mit genau 41 Originaldateien. Die zusaetzliche Lesefassung enthaelt den gesamten Haupttext in begrenzten Abschnitten, damit keine Vorschau stillschweigend am Groessenlimit endet.

| Inhalt | Einstieg |
| --- | --- |
| Word-Dokument | [Wissenschaftliche Abhandlung](2026-09-07_ki-die-geliehene-intelligenz/wissenschaftliche_abhandlung.docx) |
| Vollstaendiges Markdown | [Originalfassung](2026-09-07_ki-die-geliehene-intelligenz/wissenschaftliche_abhandlung.md) |
| Literatur | [BibTeX](2026-09-07_ki-die-geliehene-intelligenz/literatur.bib), [annotiertes Verzeichnis](2026-09-07_ki-die-geliehene-intelligenz/literatur_annotiert.md), [CSL-JSON](2026-09-07_ki-die-geliehene-intelligenz/literatur.csl.json) |
| Fragen und Hypothesen | [Publikationsregister](2026-09-07_ki-die-geliehene-intelligenz/forschungsfragen_hypothesen.json) |
| Ergebnisse und Grenzen | [Ergebnisatlas](2026-09-07_ki-die-geliehene-intelligenz/ergebnisatlas.md), [Evidenzdarstellung](2026-09-07_ki-die-geliehene-intelligenz/evidenzregister.json) |
| Herkunft und Redaktion | [Quellenmanifest](2026-09-07_ki-die-geliehene-intelligenz/quellenmanifest.json), [Entscheidungen](2026-09-07_ki-die-geliehene-intelligenz/redaktionelle_entscheidungen.md) |
| Alle Materialien | [Paketbeschreibung](2026-09-07_ki-die-geliehene-intelligenz/README.md), [Katalog](catalog.json) |
| Gesamtes Originalpaket | [ZIP mit allen 41 Dateien](archives/Brain5D_Wissenschaftliche_Abhandlung_2026-09-07.zip) |
| Technische Integritaet | [Dateiinventar und SHA-256](integrity.json), [Lesefassungsmanifest](reader/manifest.json) |

## Einbindung in das Forschungssystem

Der Research-Dokumentbaum und die Research-Dokumentliste enthalten die Kategorie `publications`. Alle Darstellungen laufen durch den bestehenden zentralen File Viewer, einschliesslich Markdown, DOCX, BibTeX, JSON, Formeln, Abbildungen und ZIP-Inhaltsverzeichnis. Die Publikation und ihre Lesefassung sind ueber die Dateiverwaltungs-API schreibgeschuetzt.

Im zentralen File Viewer und in aufgeklappten Chat-Dateikarten steht ausserdem der gemeinsame natuerliche Vorlesemodus mit deutscher Stimme, Pause, Fortsetzen und Stopp zur Verfuegung. Die datierte Publikation selbst bleibt ein unveraenderter, schreibgeschuetzter Publikationsstand.

Das Publikationsregister ist eine zitierbare Momentaufnahme, **kein zweites kanonisches Forschungsregister**. Massgeblich bleiben [questions.yaml](../registry/questions.yaml) und seine Fragmente, [hypotheses.yaml](../registry/hypotheses.yaml) und seine Fragmente sowie die registrierten Experiment- und Evidenzartefakte. Die Einbindung veraendert keine Messdaten, Hypothesenstatus oder Review-Entscheidungen. Neue Synthesehypothesen werden hier nicht automatisch zu bestaetigten oder ausfuehrbaren Forschungsfragen erklaert.

## Pruefung und Aktualisierung

```bash
git lfs pull --include='research/publications/**' --exclude=''
python scripts/publication_bundle.py
```

Die Pruefung verlangt echte Dateien statt LFS-Zeigern, verifiziert alle 41 SHA-256-Pruefsummen, den gesamten ZIP-Hash, jedes Archivmitglied und die vollstaendige deterministische Lesefassung. Eine neue wissenschaftliche Fassung erhaelt einen neuen datierten Ordner; dieser Stand wird nicht nachtraeglich ueberschrieben.

```bash
python scripts/publication_bundle.py --build-reader
```

Dieser zweite Befehl regeneriert ausschliesslich die abgeleitete Lesefassung. Historische Originaldateien und deren eingebettete Pruefsummen bleiben unveraendert.
