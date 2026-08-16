# Entwicklungsverfahren

## Leitprinzip

Neue Funktionalität wird erst in den Core übernommen, wenn sie isoliert testbar, beobachtbar und über einen Feature-Flag deaktivierbar ist.

## Arbeitsfolge

1. Issue bzw. technische Hypothese formulieren.
2. Referenztest schreiben oder erweitern.
3. kleinste Core-Änderung implementieren.
4. `python -m pytest -v` ausführen.
5. Golden Chain ausführen.
6. Headless-PoC ausführen.
7. Run-Artefakte prüfen.
8. Observatory nur als Beobachter verwenden.
9. Benchmark gegen Referenzstand vergleichen.
10. Commit mit eindeutiger Nachricht erzeugen.

## Definition of Done

Eine Änderung ist fertig, wenn:

- alle Tests grün sind;
- keine vorhandene Invariante abgeschwächt wurde;
- keine Beispielzahlen als Messergebnisse ausgegeben werden;
- neue Messwerte eine eindeutige Quelle besitzen;
- der Core weiterhin ohne Observatory startet;
- Dokumentation und Konfiguration aktualisiert sind.

## Debug-Invarianten

`simulation.debug_invariants: true` aktiviert teurere interne Konsistenzprüfungen. Diese Option ist für Tests und Fehlersuche vorgesehen, nicht für Performance-Messungen.
