# EXP-5D-0001-v2: Zusammenfassung

## Kurzfassung

Das Experiment untersucht, ob eine fuenfdimensionale Anordnung eine messbar andere Netzwerkdynamik als niedrigere Dimensionen erzeugt.

**Ergebnis:** Der Lauf wurde technisch erfolgreich abgeschlossen. In allen 15 Messungen wurden jedoch keine aktivierten Neuronen und keine Spikes beobachtet. Eine belastbare Aussage ueber einen Effekt der Dimensionalitaet ist deshalb nicht moeglich.

## Zuordnung

| Feld | Wert |
|---|---|
| Experiment | `EXP-5D-0001-v2` |
| Titel | Dimensionalitaet und Netzwerkdynamik v2 |
| Forschungsfrage | `RQ-5D-001` |
| Hypothese | `H-5D-001-A` |
| Protokoll | `science_suite_v1` |
| Laufmodus | EXPLORATORY |
| Netzwerkmodus | OFFLINE |
| Seeds | 42, 43, 44 |
| Messungen | 15 (3 Seeds x 5 Bedingungen) |
| Laufzeit | 0.003842 s |
| Technischer Status | completed |
| Gueltigkeitsstatus | valid, 0 Laufzeitfehler |

## Bedingungen und Daten

| Bedingung | Dimensionen | Laeufe | Aktivierte Neuronen | Gesamt-Spikes | Propagationstiefe | Latenz |
|---|---:|---:|---:|---:|---:|---|
| 1d | `[3, 1, 1, 1, 1]` | 3 | 0 | 0 | 0 | nicht bestimmt |
| 2d | `[2, 2, 1, 1, 1]` | 3 | 0 | 0 | 0 | nicht bestimmt |
| 3d | `[2, 2, 2, 1, 1]` | 3 | 0 | 0 | 0 | nicht bestimmt |
| 5d | `[2, 2, 2, 2, 2]` | 3 | 0 | 0 | 0 | nicht bestimmt |
| random_graph | `[2, 2, 2, 2, 2]` | 3 | 0 | 0 | 0 | nicht bestimmt |

Die Rohdaten enthalten fuer jeden Lauf die Vorher-/Nachher-State-Digests. Die Probe meldete in allen Bedingungen keine Netzwerkantwort; deshalb sind `first_response_latency`, `last_response_latency` und `return_latency` null.

## Berichtslage

### Technischer Experimentbericht

[report.md](report.md) dokumentiert Protokoll, Laufanzahl und den Evidenzvorbehalt.

### DATA

[runs.json](DATA/runs.json) enthaelt alle 15 Einzelmessungen.

### Manifest und Workflow

- [manifest.json](manifest.json) beschreibt Status, Seeds, Konfiguration, Artefakte und Validitaet.
- [workflow.json](workflow.json) beschreibt die registrierte Forschungsfrage, Hypothese, Bedingungen und KI-Grenzen.

### AIRR

[AIRR-2026-0001.json](reports/AIRR-2026-0001.json) und [AIRR-2026-0001.md](reports/AIRR-2026-0001.md) wurden post-hoc erzeugt.

- Status: `review_pending`
- KI-Konfidenz: `0.1`
- Menschliche Pruefung: `PENDING`
- Wissenschaftliche Evidenz: `false`
- Interpretation bleibt von der Ausfuehrung getrennt.

Der AIRR fordert fuer eine belastbare Bewertung insbesondere Rohdaten mit auswertbaren Netzwerkmetriken, eine detailliertere reproduzierbare Protokollbeschreibung und statistische Vergleiche zwischen 2D, 3D und 5D.

### AIAR

Im Ordner [analysis](analysis) liegen die AIAR-Ausgaben der Rollen `scientific_analyst`, `critical_reviewer` und `scientific_writer`.

Vorhandene AIAR-Dateien:

- [AIAR-scientific_analyst-20260903205623921935-d11507fa.json](analysis/AIAR-scientific_analyst-20260903205623921935-d11507fa.json)
- [AIAR-critical_reviewer-20260903205642547131-d11507fa.json](analysis/AIAR-critical_reviewer-20260903205642547131-d11507fa.json)
- [AIAR-scientific_analyst-20260903205715084095-664b8e2f.json](analysis/AIAR-scientific_analyst-20260903205715084095-664b8e2f.json)
- [AIAR-critical_reviewer-20260903205732047321-664b8e2f.json](analysis/AIAR-critical_reviewer-20260903205732047321-664b8e2f.json)
- [AIAR-scientific_writer-20260903205748858380-664b8e2f.json](analysis/AIAR-scientific_writer-20260903205748858380-664b8e2f.json)

Die Rollen kommen uebereinstimmend zu dem Schluss, dass aus dem vorliegenden Lauf keine wissenschaftliche Aussage ueber einen Dimensionalitaetseffekt abgeleitet werden kann. Die kritische Hauptursache ist die fehlende Netzwerkaktivitaet, nicht ein bestaetigter negativer Effekt der 5D-Anordnung.

## Wissenschaftliche Einordnung

Die Hypothese ist mit diesem Lauf **weder bestaetigt noch widerlegt**. Der beobachtete Nullbefund kann auf die Stimulations- oder Modellkonfiguration zurueckgehen. Fuer einen aussagekraeftigen Folgelauf sollten die Ursache der ausbleibenden Spikes geprueft, eine messbare Kontrollreaktion hergestellt und anschliessend die Dimensionen unter ansonsten identischen Parametern statistisch verglichen werden.

Es wurde keine `EVID` erzeugt. Human Review bleibt erforderlich; die KI-Berichte sind keine wissenschaftliche Evidenz.

## Reproduzierbarkeit

- Python: 3.13.14
- Betriebssystem: Windows 11
- Git-Commit zum Lauf: `254b3574af41364619e297a5c399cb29249e9270`
- Konfiguration: `configs/learning_experiment.yaml`
- Git-Status beim Lauf: dirty

