# Brain-5D v0.4.0-alpha.5 - Operator Dashboard & Quality Gate

## Rolle der Revision

Alpha.5 ist keine neue Lernmethode. Die Revision macht die bereits vorhandenen
Subsysteme operativ sichtbar und schliesst die Qualitaetsgrenze vor `v0.4.0`.

## Ziele

1. Black fuer das gesamte Repository ohne Diff.
2. `mypy src` ohne Fehler.
3. Pylint mindestens 9.0; echte Fehler E/F muessen 0 sein.
4. Operator Dashboard als lokale read-only Weboberflaeche.
5. Storage-Telemetrie und Lazy-Heatmaps sichtbar machen.
6. Dokumentationsquellen fuer den Weg zur KI konsolidieren.

## Dokumente

Folgende lokale Dokumente sollen als Design-Inputs beruecksichtigt werden:

- `docs/06-research/Analyse_Deepseek.md`
- `docs/06-research/Der_weg_zur_KI.md`
- `docs/08-roadmap/ROADMAP_TO_USABLE_AI.md`
- `docs/02-architecture/B5D_FORMAT.md`
- `docs/09-sprints/SPRINT_STORAGE_V4.md`

`Analyse_Deepseek.md` und `Der_weg_zur_KI.md` waren bei Erstellung dieses
Overlays nicht im Remote-Repository verfuegbar. Sie werden daher noch nicht
inhaltlich zusammengefasst. Nach dem Push muss ein Dokumentabgleich erfolgen.

## Exit-Kriterien

```text
pytest               PASS
black --check        PASS
mypy src             PASS
pylint src >= 9.0    PASS
Dashboard tests      PASS
Dashboard local UI   PASS
```

Danach ist `v0.4.0` als Persistenz-/Observability-Contract bereit.

## Naechste Ebene

`v0.5` startet erst danach und konzentriert sich auf Selbstregulation:

- HomeostasisEngine
- Ziel-Feuerungsraten
- adaptive Thresholds
- Energie-Homoeostase
- Neurogenese/Pruning unter stabilen Grenzen
- Dirty Tracking statt O(N+E) Persistence Scan

Das Dashboard wird in v0.5 um Homeostase-Kennwerte erweitert.
