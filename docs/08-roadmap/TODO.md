# Brain-5D — Consolidated TODO

> Last updated: 2026-09-03
> Die TODO ist nach Verantwortung getrennt: ENGINEERING, SCIENCE und OPERATION.
> Wissenschaftliche Aussagen benötigen ein registriertes Experiment und
> reproduzierbare EVID-Artefakte; technische Implementierung allein genügt nicht.

## ENGINEERING

### Chat UX und Providersteuerung

- [x] Editierbare Chat-Einstellungen inklusive System-Prompt, Sampling, Tokenbudget und Kontextlimit
- [x] Persistente Räume und Unterchats mit festem Header und Composer
- [x] Live-Health-Probe für den konfigurierten Provider

### Alpha.7 — Controlled Experience & Learning Loop

- [x] Produktiven Lernpfad instrumentieren: Input, Pre/Post, LearningEngine, reale Synapse
- [x] Gewicht `weight_before` / `weight_after` und Lernstatistiken pro Lauf erfassen
- [x] Deterministisches Environment für wiederholbare Wahrnehmungs-Handlungs-Zyklen verwenden
- [x] Audio/Vision nicht als Alpha.7-Kernabhängigkeit behandeln

### Alpha.7.1 — Performance & Persistent Operator

- [ ] Storage unter `operator/state.b5d`, `operator/journal/`, `operator/checkpoints/` kapseln
- [ ] Experimente unter `experiment/EXP-*/state/`, `DATA/` und `EVID/` kapseln
- [ ] Dev-Artefakte ausschließlich unter `dev/disposable/` ablegen
- [ ] Harte Grenzen erzwingen: DEV -> OPERATOR verboten, EXPERIMENT -> OPERATOR kein Merge, OPERATOR -> EXPERIMENT nur Snapshot/Fork
- [ ] `full_change_scan` und `dirty_tracking` mit identischem Seed, Input und Tickzahl vergleichen
- [ ] Digest, Gewichte, Neuronen-, Strukturzustand und Journal-Restore auf Gleichheit prüfen
- [ ] Laufzeitprofil für 1k / 10k / 100k / 1M Ticks erfassen: ticks/s, ms/tick, Storage, Telemetrie, Bytes, Dirty-Counts, RAM

### Alpha.8 — Adaptive Self-Regulation & Morphology

- [ ] Interne Regelgrößen und daraus abgeleitete Drives definieren
- [ ] Neuron-/Synapsenalter, Growth-/Pruning-Kosten und Neurogenese-Budgets ergänzen
- [ ] Regional Pressure, Hysterese und Anti-Oszillation integrieren
- [ ] Langhorizont-Stabilität unter chronischem Druck verifizieren

### Alpha.9 bis v1.0

- [ ] Memory-/World-Model-Schnittstellen implementieren
- [ ] Multimodale Audio-/Vision-Adapter als echte, opt-in Datenquellen anbinden
- [ ] Provenance-gebundenen Knowledge Intake implementieren
- [ ] Language Organ auf lesende Zustandsbeschreibung begrenzen
- [ ] Release- und Installationspfad für die integrierte Forschungsplattform härten

## SCIENCE

- [ ] `EXP-STDP-0002`: Productive STDP auf `NeuralNetwork -> LearningEngine -> Synapse` mit unabhängigen Runs
- [x] `EXP-EMB-0001` Protocol Run: 180 DATA-Runs mit autorisiertem, unauthorisiertem und Reproduzierbarkeits-Kontrollpfad
- [ ] `EXP-EMB-0001`: EVID-Artefakt nach Clean Freeze, unabhängiger Review und vollständiger Provenienz erzeugen
- [ ] Zweiten identischen Versuch nach dem Lernen ausführen und `P(success | after) > P(success | before)` prüfen
- [ ] `EXP-TIME-0001`: Learning Timescale Calibration bei 100 bis 1.000.000 Ticks
- [ ] `EXP-5D-0001`: 1D/2D/3D/5D/Random-Graph-Ablation mit mindestens 30 Seeds je Bedingung
- [ ] `EXP-REG-0001`: Homeostase, Drives und strukturelle Selbstregulation unter kontrolliertem Druck
- [ ] `EXP-BODY-0001`: Sensorverlust, Aktivitätsänderung, Rekonfiguration und Kompensation messen
- [ ] `EXP-MEM-0001`: Retention, Interferenz, Relearning, Transfer und Recall messen
- [ ] `EXP-AIR-0001`: Scientific Research Assistant erst nach Clean Freeze, Push und externer CI ausführen

### Forschungsprotokoll für jeden Lauf

- [x] Forschungsfrage, Hypothesen, Bedingungen, Kontrollen und Wiederholungszahl registrieren
- [x] Effektive Inputs, Outputs, Rewards, Audit-Status und Laufmetriken für EXP-EMB-0001 speichern
- [ ] DATA/EVID-Provenienz, Limitationen und unabhängige Wiederholungen prüfen
- [ ] Claims erst nach menschlicher Review aktualisieren

### AI Research Reports (AIRR)

- [x] `PROTOCOL-AIRR-001` und kanonisches AIRR-JSON-Schema registrieren
- [x] Analyst -> Critical Reviewer -> Scientific Writer als getrennte AIAR-Pipeline
- [x] Deterministisches JSON -> Markdown Rendering mit vollständiger Provenienz
- [x] DATA/EVID-Referenzen und ResearchPacket-Digest im Bericht speichern
- [x] Human Review als separates append-only `.review.json` speichern
- [x] AIRR im Research-Dashboard lesbar machen
- [x] Research Self-Knowledge Chat mit Research-/Docs-Kontext und fail-closed Backend
- [x] Chat-Ausführung strikt vom Freitext trennen; Experimente bleiben registrierte Workflows
- [x] Lokales Ollama-Backend, Markdown-Ausgabe und Chat-Einstellungen konfigurieren
- [ ] Azure-Backend explizit konfigurieren und `EXP-AIR-0001` ausführen
- [ ] AIRR gegen menschliche Referenzauswertung und mehrere Modelle evaluieren

## OPERATION

- [ ] Lokale Änderungen committen und pushen; vollständige GitHub-CI abwarten
- [ ] Kein wissenschaftliches Experiment auf Dirty Tree ausführen
- [ ] Hugging-Face-Sync erst nach geklärten `HF_USERNAME`-/`HF_TOKEN`-Secrets und CI-Grün aktivieren
- [ ] Release-Registry, Changelog und Roadmap nach jedem abgeschlossenen Meilenstein synchronisieren
- [ ] Dashboard-/Runtime-Verträge aktuell halten; `enabled`, `active`, `unavailable` und Evidenzstatus getrennt lassen
- [ ] Dokumentierte Benchmarks nicht als wissenschaftliche Claims ausgeben

## Bereits erledigt, bewusst nicht erneut auf der Arbeitsliste

Alpha.5/6-Integration, Operator/Experiment/Dev-Modi, Evidence Scopes,
Restore-Determinismus, Structural E2E, RuntimeController, Embodiment-Verträge,
Safety-Grenzen, deterministischer EnvironmentAdapter, Experience Engine v0,
dirty-state emitter, Dashboard-Workbench und die lokale Qualitätsbaseline sind
implementiert oder historisch abgeschlossen. Details bleiben in
`docs/07-changelog/CHANGELOG.md` und den historischen Release-Dokumenten.
