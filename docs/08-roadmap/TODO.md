# Brain-5D — Consolidated TODO

> Last updated: 2026-08-30
>
> Infrastructure: Hugging Face Repository vorbereitet (HF_README.md,
> .gitattributes LFS, .huggingface/ metadata, Space-Konfiguration,
> GitHub→HF Sync Workflow).
> Verification basis:
>   Current verification → tests/test_baseline.json (tree-digest authority)
>   All 5 verification artifacts share the same tested_tree_digest ✅

## Priorität 1 — Alpha.5 Closure (aktuelle Sprint-Arbeiten)

- [ ] EXP-DET-0001: Determinism A/B/C experiment durchführen
- [ ] EXP-STOR-0001: Storage persistence experiment durchführen
- [ ] Erste DATA-* / EVID-* Artefakte generieren
- [ ] Research Catalog aus echten Evidenzen neu aufbauen
- [ ] Dashboard: IO-Fluss Visualisierung finalisieren
- [ ] Dashboard: Populationen-Übersicht finalisieren
- [ ] Dashboard: 5D Isometrische Projektion verbessern

## Priorität 2 — Code-Qualität

- [x] Research-Registry Tests verstärken (Duplikate, Referenzen, Pflichtfelder)
- [ ] Pylance/Pyright clean: alle Typfehler beseitigen
- [ ] type:ignore-Kommentare auf Minimum reduzieren
- [ ] Testabdeckung für neue Module erhöhen
- [ ] Dokumentation zu den neuen API-Endpunkten schreiben

## Priorität 3 — Infrastruktur

- [ ] Hugging Face Space Deployment testen
- [ ] CI/CD Pipeline für automatische Tests
- [ ] Benchmark-Ladder für 5k-1M Neuronen vorbereiten

## Erledigt

- [x] Viewer als eigenständiges Overlay-Element (Close-Button, expandiert bei Bedarf)
- [x] Fehlende Dateitypen ergänzt: `.bib`, `.patch`, `.rst`, `.tex`, `.sh`, `.bat`, `.ps1`, `.dockerfile`, `.cmake`, `.makefile`, `.txt`
- [x] JSON-Erkennung jetzt über `ext.endsWith('.json')` — fängt auch `.schema.json` ab
- [x] YAML Syntax-Highlighting (renderFMYaml mit farblichen Token-Klassen)
- [x] Research-Registry Validierung verstärkt: Duplikate, ID-Formate, Referenzen, Pflichtfelder
- [x] Fehlende Quellen `SRC-WATTS-STROGATZ-1998` und `SRC-BARABASI-1999` in `research/registry/sources.yaml` ergänzt
- [x] Multi-Language Code Syntax-Highlighting (renderFMCode für 17 Sprachen)

## Bekannte Probleme

- Dashboard State Publishing darf niemals die Simulation blockieren (bereits gelöst)
- Self-Organization nur über canonical Coordinator->Approval->PlasticityEngine Pfad
- Storage ist per Konfiguration deaktiviert (poc_config.yaml)
