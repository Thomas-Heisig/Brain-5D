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

## Browser-Checks

Die Dashboard-UI wird mit Playwright und Chromium geprüft. Ein vollständiger
lokaler Check installiert die optionale Browser-Abhängigkeit und startet den
Dashboard-Server automatisch auf einem freien Port:

```powershell
python -m pip install -e ".[browser]"
python -m playwright install chromium
python scripts/browser_check.py
```

Für einen bereits laufenden Dashboard-Server kann die URL direkt übergeben
werden: `python scripts/browser_check.py --url http://127.0.0.1:8765/`.

Die vollständige Browser-Suite läuft unabhängig mit `npm ci` und
`npm run test:e2e`; sie prüft Batch-Optionen, Footer-Status, Routing,
Box-Zustände sowie responsive Viewports.

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
