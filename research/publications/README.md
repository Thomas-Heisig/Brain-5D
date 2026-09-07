# Wissenschaftliche Abhandlung – zentrale Publikationsquelle

## Aktuelle Fassung 1.1

**Thomas Heisig: KI – Die geliehene Intelligenz.** Epistemische Herkunft, kausale Leistungszuordnung und überprüfbare Kontrolle in einem neuronalen Forschungsframework. Überarbeitung vom 7. September 2026.

**[Die vollständige aktuelle Abhandlung lesen](2026-09-07_ki-die-geliehene-intelligenz_v1.1/README.md)**

Die kapitelweisen Markdown-Dateien der Fassung 1.1 sind die aktuelle redaktionelle Single Source of Truth. Sie enthalten die komplette bisherige Abhandlung mit acht ersetzten Abschnitten und fünf neuen Anhängen. Unveränderte Kapitel behalten ihren ausgewiesenen historischen Quellenstand; eine pauschale erneute Prüfung aller Aussagen wird nicht behauptet. Exporte werden aus der Kapitelreihenfolge erzeugt, nicht unabhängig weiterbearbeitet.

Die Revision bearbeitet die Kritik an 5D-Überlegenheitsbehauptungen, fehlendem Erkenntnisgewinn, Evidenzdeutung, Literaturmethodik und unklaren Begriffen. Sie ergänzt bedingte Beweise, Gegenbeispiele und ausführliche Operationalisierungen. **Neue Brain-5D-Lernversuche und ein empirischer 5D-Vorteil werden dadurch nicht behauptet.**

| Zugang | Inhalt |
| --- | --- |
| [Methodologie](2026-09-07_ki-die-geliehene-intelligenz_v1.1/section-006.md) | Tatsächlicher Arbeitsumfang und getrennte Nachweisformen |
| [5D-Architektur](2026-09-07_ki-die-geliehene-intelligenz_v1.1/section-019.md) | Adressierung, wirksame Geometrie und faire Vergleichsbedingungen |
| [Begriffskompendium](2026-09-07_ki-die-geliehene-intelligenz_v1.1/section-046.md) | Ausführliche Definitionen, Beispiele, Gegenbeispiele und Messvorschläge |
| [Formale Ergebnisse](2026-09-07_ki-die-geliehene-intelligenz_v1.1/section-047.md) | Drei Argumente mit Beweisen und ausführbaren endlichen Beispielen |
| [Prüfentwürfe](2026-09-07_ki-die-geliehene-intelligenz_v1.1/section-048.md) | Noch nicht durchgeführte Dimensions-, Lern-, Gedächtnis-, Attributions- und Kontrollprüfungen |
| [Quellennutzung](2026-09-07_ki-die-geliehene-intelligenz_v1.1/section-049.md) | Rechercheplan, tatsächliche Suche, Lektüreumfang und argumentative Nutzung |
| [Kritik und Bearbeitungsstand](2026-09-07_ki-die-geliehene-intelligenz_v1.1/section-050.md) | Änderungen und ausdrücklich verbleibende empirische Nachweispflichten |
| [Editionsmanifest](2026-09-07_ki-die-geliehene-intelligenz_v1.1/manifest.json) | Reihenfolge, Herkunft und geänderte Kapitel |

## Historische Fassung 1.0 – unverändert archiviert

Die folgenden Dateien dokumentieren die frühere Fassung und sind **nicht** als aktualisierte Ausgabe 1.1 zu bezeichnen:

[Ursprüngliche vollständige Lesefassung](reader/README.md) · [Original-Markdown](2026-09-07_ki-die-geliehene-intelligenz/wissenschaftliche_abhandlung.md) · [Word-Datei 1.0](2026-09-07_ki-die-geliehene-intelligenz/wissenschaftliche_abhandlung.docx) · [Originalpaket mit allen 41 Dateien](archives/Brain5D_Wissenschaftliche_Abhandlung_2026-09-07.zip) · [Paketbeschreibung](2026-09-07_ki-die-geliehene-intelligenz/README.md) · [Originalprüfsummen](integrity.json).

Die ursprünglichen Manuskripte, Abbildungen, BibTeX-Dateien und Begleitregister bleiben vollständig erhalten. Für die aktuelle Revision wurde keine neue DOCX-Datei erzeugt. Ein abgeleiteter Markdown-Export ist mit dem unten genannten Befehl reproduzierbar.

## Wissenschaftliche Zuständigkeit

Die Publikationen haben `authority=interpretation_only` und keine automatische Evidenzfreigabe. Kanonisch bleiben [Forschungsfragen](../registry/questions.yaml), [Hypothesen](../registry/hypotheses.yaml), [Evidenz](../registry/evidence/) und [Experimente](../experiments/). Die neuen Prüfentwürfe sind noch keine registrierten Runner-Protokolle. Technische Tests, mathematische Argumente, empirische Resultate und menschliches Review sind getrennt zu lesen. Katalog: [catalog.json](catalog.json).

## Integrität, Prüfung und Export

Vom Repository-Hauptverzeichnis:

```bash
git lfs pull --include='research/publications/**' --exclude=''
python scripts/publication_bundle.py
python scripts/publication_revision.py
python scripts/publication_revision.py --export /tmp/Brain5D_Abhandlung_v1.1.md
```

Der erste Python-Aufruf prüft die unveränderten 41 Originaldateien, das ZIP und die ursprüngliche Lesefassung. Der zweite prüft die neue Edition, ihre Verweise, die bytegleichen Übernahmen und die tatsächlich ausführbaren Methodenbeispiele. Der Export liegt außerhalb der kanonischen Quellen und darf nicht als unabhängig bearbeiteter Master zurückgeführt werden. Ein technischer Erfolg ersetzt kein unabhängiges wissenschaftliches Fachreview.
