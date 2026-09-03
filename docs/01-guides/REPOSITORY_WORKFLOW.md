# Brain-5D Repository Workflow

> Verbindliche Projektkonvention ab 2026-09-03

## Kanonischer Entwicklungsstand

Der verbindliche, gemeinsame Projektstand von Brain-5D ist:

```text
origin/main
```

Alle abgeschlossenen Arbeiten, Dokumentationsänderungen, Forschungsregistrierungen und freigegebenen Implementierungen müssen in `origin/main` integriert werden.

Lokale Branches oder Feature-Branches dürfen für isolierte Änderungen, Review, CI oder sichere Vorbereitung verwendet werden. Sie gelten jedoch nicht als offizieller Projektstand.

## Arbeitsregel

1. Vor Beginn neuer Arbeit `origin/main` als Referenzstand prüfen.
2. Änderungen dürfen temporär in einem Feature-Branch vorbereitet werden.
3. Nach Prüfung und Freigabe wird die Änderung nach `main` gemerged.
4. Der resultierende `main`-Stand wird nach `origin/main` geschrieben.
5. Dokumentation, TODO, Research Registry und Changelog müssen sich auf den in `origin/main` vorhandenen Stand beziehen.
6. Wissenschaftliche Experimente dürfen nur einen eindeutig dokumentierten Commit aus `origin/main` bzw. einen davon erzeugten Clean Freeze verwenden.

## Wichtige Klarstellung

„Immer in origin/main schreiben“ bedeutet für Brain-5D:

> `origin/main` ist der einzige dauerhafte kanonische Zielstand.

Es bedeutet nicht, dass Sicherheits-, Review- oder CI-Schritte übersprungen werden sollen. Temporäre Branches sind zulässig und erwünscht, wenn sie helfen, `main` sauber, reproduzierbar und wissenschaftlich nachvollziehbar zu halten.

## Keine parallelen Wahrheiten

Es sollen keine dauerhaft voneinander abweichenden Entwicklungsstände als gleichwertig behandelt werden.

- `origin/main` = kanonischer Projektstand
- Feature-Branch = temporäre Arbeitsfläche
- Release Tag = eingefrorene Referenz eines bestimmten `main`-Commits
- Experiment Freeze = wissenschaftlich dokumentierte Referenz eines bestimmten `origin/main`-Commits

Damit bleibt für Code, Dokumentation und Forschung eindeutig nachvollziehbar, auf welchem Systemstand eine Aussage beruht.
