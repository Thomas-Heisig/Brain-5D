# KI - Die geliehene Intelligenz
## Wissenschaftliche Abhandlung | Gesamtpaket 1.0

Thomas Heisig / Brain-5D. Redaktions- und Recherchestichtag: 7. September 2026.

## Einstieg

Die Hauptdatei `wissenschaftliche_abhandlung.docx` enthält die integrierte Lesefassung mit 36 Kapiteln, fünf Anhängen, 38 Tabellen, acht konzeptionellen Originalabbildungen, einem verlinkten Inhaltsverzeichnis und bearbeitbaren mathematischen Formeln. Der geprüfte Referenzumbruch umfasst 165 Seiten. Der Gesamttext umfasst ungefähr 48.000 Wörter einschließlich Anhängen und Literatur; mathematische Ausdrücke werden bei dieser Näherung nicht als Wörter gezählt. Word-Version, Schriftverfügbarkeit und Druckereinstellungen können die Seitenzahl beim erneuten Umbruch verändern.

Die Arbeit verbindet die drei bereitgestellten Manuskripte mit ausgewählten Projektquellen, Ergebnissen und gezielten Literaturaktualisierungen. Sie untersucht Genealogie, Erkenntnistheorie, Agency, Embodiment, Ethik, Recht, Kontrolle, SNN-Dynamik, Plastizität, Geometrie, Gedächtnis, Persistenz, multimodale Ressourcenverteilung und wissenschaftliche Reproduzierbarkeit.

## Dateien und Verwendung

| Datei oder Ordner | Inhalt |
|---|---|
| `wissenschaftliche_abhandlung.docx` | Vollständige formatierte Lesefassung. |
| `wissenschaftliche_abhandlung.md` | Bearbeitbare Markdown-Vollfassung; GFM, TeX-Mathematik und explizite HTML-Sprungmarken. |
| `literatur.bib` | 311 Literaturdatensätze als UTF-8-BibTeX; konservativer Austauschtyp `@misc`, bibliografische Vollangabe im Feld `note`. |
| `literatur_annotiert.md` | Literaturverzeichnis mit thematischer Einordnung, Herkunft und Prüfstatus je Eintrag. |
| `literatur.json`, `literatur.csl.json` | Literaturdaten und CSL-Austauschformat; teilweise literale Autorenfelder, siehe Grenzen unten. |
| `forschungsfragen_hypothesen.json` | 48 erfasste kanonische Fragen, die Framework-Fragen, F1-F24, H1-H12, Gegenhypothesen und acht neue Synthesevorschläge. |
| `evidenzregister.json`, `ergebnisatlas.md` | Getrennte Ergebnislinien mit Reichweite, Status und Einschränkungen. |
| `repository_quellen.json`, `quellenmanifest.json` | 15 gezielt gelesene Projektquellen am fixierten Commit sowie SHA-256 der drei Originaldateien. |
| `rechercheprotokoll.md` | Tatsächlich verwendete Recherchewege und elf gezielt aktualisierte externe Primär-/Amtsquellen. |
| `redaktionelle_entscheidungen.md` | Zusammenführung, Formelergänzungen, begriffliche Abgrenzungen und offene Nachprüfungen. |
| `reproduktion/` | Transkribierte Berichtswerte, standardbibliotheksbasiertes Python-Skript und nachgerechnete deskriptive Kennzahlen. |
| `materialien/` | Integrationsmatrix, Paketmetadaten, Qualitätsprüfung, MSBA-Transkript und Formelauszug als JSON/TeX. |
| `originale/` | Drei unveränderte bereitgestellte DOCX-Dateien. Historische Dateinamen bleiben aus Provenienzgründen erhalten. |
| `abbildungen/` | Originaldiagramme; acht sind in der Lesefassung eingebunden, vier weitere bleiben als Quellenmaterial verfügbar. |
| `CITATION.cff` | Zitiermetadaten dieses Pakets ohne behaupteten DOI, Peer Review oder akademische Anerkennung. |
| `SHA256SUMS.txt`, `pruefsummen_pruefen.py` | Dateiintegrität des ausgelieferten Pakets. |

## Wissenschaftlicher Status

Die drei Quellmanuskripte tragen K1-K3, Projektartefakte R1-R15 und gezielt extern aktualisierte Quellen W01-W11. Die Kennzeichnung S beziehungsweise „Synthese“ bezeichnet eigene redaktionelle Ableitungen oder Vorschläge. Die historische Bezeichnung einzelner Originaldateien als Dissertation ist keine Qualifikations- oder Anerkennungsbehauptung für das neue Gesamtwerk.

Es wurden keine neuen Brain-5D-Experimente ausgeführt, keine Rohereignisse unabhängig repliziert, keine menschlichen Versuchspersonen untersucht und keine Hypothesen automatisch zu akzeptierter Evidenz hochgestuft. Bereits registrierte technische `supported`-Einträge zu Restore und Speicherung werden berichtet, aber nicht als Nachweis von Gedächtnis, Bewusstsein oder allgemeiner Intelligenz ausgegeben. Dirty-Tree-Provenienz, semantische Freigabekonflikte, ausstehende Reviews und eingeschränkte Versuchsdesigns bleiben sichtbar.

Die acht H-SYN-Vorschläge wurden nicht in das Repository geschrieben. Der Repository-Zugriff war lesend und auf ausgewählte Quellen begrenzt. Referenzstand: `661681981458bc69fea5fce096e27f2b85b6c9d2`.

Das Literaturverzeichnis ist ein konsolidierter Quellenbestand, kein Nachweis, dass alle 311 Einträge unabhängig verifiziert wurden oder 311 eindeutig verschiedene Werke darstellen. 300 Einträge stammen aus dem Ausgangskorpus; elf wurden gezielt extern aktualisiert. Unterschiedliche Ausgaben, Varianten und uneindeutige Datensätze sind nicht durch Vermutungen vereinigt. Insbesondere die automatisch strukturierten BibTeX-/CSL-Metadaten sollten vor einer Zeitschrifteneinreichung bibliografisch nachgeprüft werden. Die vollständige übernommene Angabe bleibt erhalten. Es wird keine vollständige PRISMA-Review oder externe Fachbegutachtung behauptet.

Die Erstellung war KI-gestützt. Eine persönliche abschließende Freigabe durch Thomas Heisig wird nicht unterstellt. Rechtliche Abschnitte sind wissenschaftliche Einordnungen und keine individuelle Rechtsberatung; datierte Anwendungsfristen sind vor konkretem Einsatz erneut zu prüfen.

## Bearbeiten, rechnen und prüfen

Das Word-Inhaltsverzeichnis enthält interne Verweise und gespeicherte Referenzseitenzahlen. Nach umfangreichen Änderungen können in Word mit `Strg+A` und `F9` die Felder aktualisiert werden. Die Überschriften sind auch über den Navigationsbereich erreichbar. Es sind keine Schriftdateien beigefügt; bei Schrift-Ersetzung kann ein neuer Seitenumbruch entstehen.

Für Markdown-Abbildungen muss der relative Ordner `abbildungen/` neben der Markdown-Datei bleiben. Die mathematische Anzeige setzt einen Markdown-Viewer mit TeX-Unterstützung voraus. Der Formelauszug ist eine Sammlung von Schnipseln für einen LaTeX-Kontext mit `amsmath`, kein selbstständig gesetztes Buch und keine Sammlung bewiesener Sätze.

Zum Nachrechnen ausschließlich der transkribierten Berichtskennzahlen:

```bash
python reproduktion/auswertung.py
```

Das Skript benötigt keine externen Python-Bibliotheken. Es berechnet Differenzen, Verhältnisse und einen einzelnen berichteten Kompressionsfaktor. Es erzeugt weder neue SNN-Daten noch p-Werte oder Evidenzfreigaben. Wird die Ausgabedatei nach eigenen Änderungen neu geschrieben, weicht ihre Prüfsumme erwartungsgemäß vom ausgelieferten Stand ab.

Dateiintegrität vor einer Bearbeitung prüfen:

```bash
python pruefsummen_pruefen.py
```

Die Prüfsummen belegen Dateiidentität, nicht wissenschaftliche Wahrheit, Autorschaft oder die Echtheit eines externen Repository-Rohartefakts. Das Rohartefakt des Kompressionsbeispiels wurde hier nicht lokal verifiziert. Die Qualitätsprüfung beschreibt die tatsächlich vorgenommenen Dokument- und Dateiprüfungen.
