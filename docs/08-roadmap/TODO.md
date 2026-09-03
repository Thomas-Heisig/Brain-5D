# Brain-5D — Consolidated TODO

> Last updated: 2026-09-03
> Die TODO ist nach Verantwortung getrennt: ENGINEERING, SCIENCE und OPERATION.
> Wissenschaftliche Aussagen benötigen ein registriertes Experiment und
> reproduzierbare EVID-Artefakte; technische Implementierung allein genügt nicht.
> Verifiziert am 2026-09-03: `main` / `67d91dd`, lokale Vollsuite `618 passed, 5 skipped`.
> Externe CI und wissenschaftliche EVID sind damit nicht vorweggenommen.

## ENGINEERING

### P0 — Scientific AI Boundary & Provenance

- [x] Erste Contract-Layer-Basis mit `AIExposure`, `CausalTaint` und digest-only `AIInteractionRecord` in Research Assistant und Chat-UI integrieren
- [x] Gemeinsamen AI-Contract-Layer für `Observation`, `Interpretation`, `Proposal`, `Intervention` und `Evidence` definieren
- [x] Scientific AI Firewall als read-only Chat-Grenze implementieren: mutierende und unbekannte Aktionen werden abgewiesen
- [x] Scientific AI Firewall auf Netzwerk, Synapsen, Struktur, Rewards, Memory und Experimentzustand ausweiten
- [x] Scientific-Authority-Matrix für SNN, Statistics Engine, Language Organ, Research Assistant, Cognitive Advisor, Action Gateway, Evidence Engine und Human Reviewer dokumentieren und validieren
- [x] Contract-Test ergänzen, der direkte Core-Imports aus Research-Assistant- und Language-Organ-Backends verhindert
- [x] `AIExposure` in Experimentmanifesten und Laufmetadaten einführen (`none`, `observer_only`, `semantic_interface`, `advisor`, `bounded_controller`, `adaptive_controller`)
- [x] Gemeinsames `AIInteractionRecord` mit Rolle, Experiment, Tick, Input-/Prompt-/Output-Digest, Modell-Provenienz, Autorität und `causal_effect` im Experimentmanifest speichern
- [x] AI-Causal-Taint-Tracking von `PURE` über beobachtend/vorschlagend bis `AI_INFLUENCED` implementieren
- [x] Causal Card je Experiment erzeugen: AI-Beobachtung, externer Input, AI-Reward, AI-Aktorentscheidung und wissenschaftliche Klassifikation
- [x] Evidence-Gate verschärfen: AI-beeinflusste Läufe benötigen ein passendes Treatment-Protokoll und dürfen nicht als reine SNN-Evidenz erscheinen

### P0 — Vollständige AI-Provenienz

- [x] Ollama-Baseline-Provenienz mit Samplingparametern, Stop-Sequenzen, Timeout und Response-Digest integrieren
- [x] Ollama-Request-/Response-Digest, Modell-ID, Completion-Grund und Tokenmetriken ergänzen
- [x] Ollama-Provenienz vollständig erfassen: Modell-ID, Modell-Digest, Artefakt-/Quantisierungsdaten, Ollama-/Engine-Version, Hardware, Präzision, Seed und alle Samplingparameter (fehlende Providerdaten bleiben `not_reported`)
- [x] `top_k`, `num_ctx`, Stop-Sequenzen, Timeout, Retry-Anzahl, Input-/Output-Tokens und Raw-Response-Digest protokollieren
- [x] Tokenizer-Digest, Prompt-Template-Digest, System-/Übergabeprompt-Digest, Toolset-Digest und Retrieval-Snapshot-Digest ergänzen
- [x] Provider-Revision, Request-Zeitpunkt, Response-Fingerprint und `knowledge_origin` für API-/Webwissen speichern
- [x] AI-Fehler als `AIInferenceFailureEvent` mit Request-ID, Backend, Latenz und Retry-Status auditieren
- [x] Automatische Retries in wissenschaftlichen Runs deaktivieren und als reproduzierbaren Treatment-Faktor protokollieren
- [x] Modellwechsel, Promptwechsel und Statistikcodeänderungen mit Versions-/Protocol-Bump registrieren und validieren

### P0 — Shadow, Replay und kontrollierte Kausalität

- [x] Shadow Mode implementieren: AI darf beobachten, interpretieren und Vorschläge erzeugen; Vorschläge werden markiert, aber nicht ausgeführt
- [x] Shadow-Proposals quantitativ evaluieren: Precision, Recall, False Positives, Prediction Accuracy, Calibration und Utility
- [x] `observation_stream.jsonl` für reproduzierbare Offline-Replays erzeugen und validieren
- [x] `FrozenAIReplayBackend` mit Request-/Response-Digest und fehlendem Live-Fallback implementieren
- [x] Reproduzierbarkeitsstufen R0 bis R3 für AI-Beteiligung in Experimenten registrieren
- [x] Counterfactual Twin Runs aus identischem Snapshot mit AI-off/AI-on und identischem Seed, Input, Reward und Tickplan ermöglichen (statistischer Vergleich bleibt Forschungsauswertung)
- [x] Kontrollgruppen für SNN-only, Language Organ, Knowledge Intake, Language+Knowledge, LLM-only und Full System als Experimentvorlagen registrieren
- [x] `NullLanguageOrgan`, `RandomLanguageOrgan` und `ReplayLanguageOrgan` als Sham-Kontrollen ergänzen

### P1 — Prompt-, Daten- und Netzwerkdisziplin

- [x] Versionierte Prompt Registry unter `research/prompts/` mit eingefrorenen Prompt-Dateien und Protocol-Digests einführen
- [x] Preregistration Lock für Forschungsfrage, Hypothesen, Metriken, Stichprobe, Seeds, Stopping Rule, Analyse und Ausschlussregeln implementieren
- [x] Exploratory und Confirmatory AI-Modus technisch und im Dashboard trennen
- [x] Confirmatory Runs gegen nachträgliche Hypothesen-, Prompt- und Analyseänderungen sperren
- [x] Development-, Validation- und Scientific-Holdout-Daten strikt trennen und AI-/Gold-Label-Leakage testen
- [x] AI-Selbstvertrauen als `model_self_confidence` kennzeichnen und von empirischer Kalibrierung, Brier Score und ECE trennen
- [x] Quantitative Statistik ausschließlich durch die deterministische Statistics Engine erzeugen; LLM darf Zahlen nur interpretieren
- [x] Netzwerkmodi `OFFLINE`, `FROZEN_CORPUS` und `LIVE_NETWORK` implementieren; wissenschaftliche Runs standardmäßig offline/frozen erzwingen
- [x] Für Sensor-, Internet- und Knowledge-Intake-Daten Observation-, Capture-, Processing-Zeit, Quelle, Version und Digest speichern
- [x] Knowledge-Intake-Pipeline mit URL, Rohdaten-Digest, MIME, Trust-Klassifikation, Extraktionsmethode und Provenienz vervollständigen
- [x] Unsichtbares RAG verhindern: Retrieval muss explizit aktiviert, versioniert und im Antwort-/Laufprotokoll sichtbar sein

### P1 — AI-Rollen und semantische Schnittstellen

- [x] Cognitive Advisor als Proposal-only-Komponente mit typisiertem `ActionProposal`-Contract implementieren
- [x] Deterministisches Intervention Gateway mit Capability Check, Rate Limit, Safety Envelope, Experiment Policy, Audit Journal und Human Override ergänzen
- [x] Memory Write Gateway für alle zukünftigen AI-generierten Memory-Proposals einführen
- [x] Language Organ in `LINGUISTIC_TRANSPORT` und `SEMANTIC_AUGMENTATION` trennen und beide Treatments messbar machen
- [x] AI-0 Research AI, AI-1 Language Organ, AI-2 Cognitive Advisor und AI-3 Experimental Cognitive Controller als formale Rollen dokumentieren
- [x] Logical-Time- und Wall-Clock-Modus für asynchrone AI-Interaktionen unterscheiden und Response-Anwendungstics protokollieren
- [x] Replay-, Live-Frozen-Model- und Live-External-API-Betrieb im Dashboard sichtbar klassifizieren

### P1 — Vergleich, Bias und AI-Forschungsobjekt

- [x] Multi-Model-Vergleich mit identischem ResearchPacket, Modellmetadaten und Disagreement Map implementieren
- [x] LLM-Konsens ausdrücklich nicht als Evidence behandeln; Agreement nur als Messgröße speichern
- [x] Blind Analysis mit anonymisierten Gruppenlabels vor der Aufdeckung ermöglichen
- [x] Analyst und unabhängigen Reviewer mit getrennten Artefakten und ohne Chain-of-Thought-Leakage evaluieren
- [x] Reviewer Correction Rate, False Criticism Rate und Missed Error Rate messen
- [x] AIR-Forschungsfragen RQ-AIR1 bis RQ-AIR5 als Benchmark-/Experimentstruktur registrieren
- [x] Modellabhängige Interpretationsdistanz `D(I_A, I_B)` und Fingerprints identischer SNN-Zustände messen
- [x] Borrowed Intelligence Ratio über Ablationen definieren, deterministisch berechnen und als keine wissenschaftliche Einzelmetrik ohne Protokoll markieren

### P2 — Wissenschaftliche Integritätsautomatisierung

- [x] Scientific Integrity Gate in CI für Determinismus, Restore, Canonical State, Golden Chain, Schema, AI-Leakage und AI-Authority ausführen
- [x] CI-Regeln für Prompt-, Modell-, Treatment- und Statistikversionsänderungen erzwingen
- [x] Epistemic Provenance Graph für Claims, Sensoren, Memory, Experimente, Webquellen und Derived Values modellieren
- [x] `knowledge_origin` mit `SNN_LEARNED`, `LLM_PRIOR`, `EXTERNAL_RETRIEVAL`, `HUMAN_INPUT`, `SENSOR_OBSERVATION`, `SYSTEM_STATE`, `SIMULATED_ENVIRONMENT`, `DERIVED` und `UNKNOWN` standardisieren
- [x] Causal-Attribution-Report für jede AI-Exposure-Stufe und jeden Twin-/Ablation-Run generieren
- [x] Dashboard-Betriebsstatus für `PURE EXPERIMENT`, `AI OBSERVING`, `AI PROPOSING` und `AI CAUSALLY ACTIVE` anzeigen

### Chat UX und Providersteuerung

- [x] Editierbare Chat-Einstellungen inklusive System-Prompt, Sampling, Tokenbudget und Kontextlimit
- [x] Persistente Räume und Unterchats mit festem Header und Composer
- [x] Live-Health-Probe für den konfigurierten Provider
- [x] Räume einklappen, archivieren, wiederherstellen und löschen
- [x] Hierarchischen Kontext für Unterchats übertragen
- [x] Provider-/Modellauswahl mit klarer OAuth-Grenze für Microsoft Copilot
- [x] Bearbeitbarer Übergabeprompt und wiederherstellbare Standardwerte
- [x] Ollama-Vision mit begrenzten Bildanhängen
- [x] Microsoft Entra OAuth PKCE Start/Callback-Grundlage
- [x] Antwortmodi mit wissenschaftlicher Quellen- und Runtime-Trennung
- [x] Größeres Chatfenster mit horizontaler Room-Aktionsleiste
- [x] Drag-and-drop für Bildanhänge sowie lokale Sprach-Ein-/Ausgabe
- [x] Ollama-Vision-Requestpfad und sichtbarer Verarbeitungsstatus

### Alpha.7 — Controlled Experience & Learning Loop

- [x] Produktiven Lernpfad instrumentieren: Input, Pre/Post, LearningEngine, reale Synapse
- [x] Gewicht `weight_before` / `weight_after` und Lernstatistiken pro Lauf erfassen
- [x] Deterministisches Environment für wiederholbare Wahrnehmungs-Handlungs-Zyklen verwenden
- [x] Audio/Vision nicht als Alpha.7-Kernabhängigkeit behandeln

### Alpha.7.1 — Performance & Persistent Operator

- [x] Storage unter `operator/state.b5d`, `operator/journal/`, `operator/checkpoints/` kapseln
- [x] Experimente unter `experiment/EXP-*/state/`, `DATA/` und `EVID/` kapseln
- [x] Dev-Artefakte ausschließlich unter `dev/disposable/` ablegen
- [x] Harte Grenzen erzwingen: DEV -> OPERATOR verboten, EXPERIMENT -> OPERATOR kein Merge, OPERATOR -> EXPERIMENT nur Snapshot/Fork
- [x] `full_change_scan` und `dirty_tracking` mit identischem Seed, Input und Tickzahl vergleichen
- [ ] Digest, Gewichte, Neuronen-, Strukturzustand und Journal-Restore auf Gleichheit prüfen
- [ ] Laufzeitprofil für 1k / 10k / 100k / 1M Ticks erfassen: ticks/s, ms/tick, Storage, Telemetrie, Bytes, Dirty-Counts, RAM

### Release-Freeze vor Alpha.8

- [ ] Black-Formatierung und alle sechs aktuellen mypy-Befunde beheben
- [ ] Lokale Vollsuite und Scientific Integrity Gate nach den Qualitätsfixes erneut ausführen
- [ ] Externe GitHub-CI vollständig grün abwarten; Hugging-Face-Sync erst danach freigeben
- [ ] README-, Embodiment-Foundation-, Roadmap- und Changelog-Versionen auf denselben Commit-/Release-Stand synchronisieren
- [ ] Clean-Freeze-Artefakt mit Tree-Digest, Teststatus und Dirty-Tree-Prüfung erzeugen

### Alpha.8 — Adaptive Self-Regulation & Morphology

- [x] Typisierten Digital-Interoception-Vertrag mit VitalSignal, Signalqualität,
  Sicherheitsbereichen und explizitem UNKNOWN-Status einführen
- [ ] Vital Signals um Lüfter-RPM/-Status, CPU/GPU-Temperatur, Temperaturgradient,
  Thermal Throttling, GPU/VRAM, RAM-Reserve, Storage, Disk-I/O/SMART,
  Strom/USV/Akku, Netzwerkqualität, Sensoralter und Sensorfehler erweitern
- [ ] Fehlende oder veraltete Sensorsignale fail-closed behandeln und niemals als sicher interpretieren
- [ ] Interne Regelgrößen für Thermal Margin, Energy Reserve, Continuity Risk,
  Sensory Integrity, Resource Pressure und Task Progress definieren
- [x] Erste Drives deterministisch aus Interoception ableiten: thermal_threat,
  resource_pressure und continuity_risk; nicht beobachtbare Drives bleiben
  explizit `None` mit Unsicherheit
- [ ] Drives vollständig aus Regelgrößen ableiten: thermal_threat,
  resource_pressure, sensory_integrity, continuity_risk, task_progress,
  novelty und actuator_confidence
- [ ] Valence, Activation, Safety und Uncertainty als abgeleitete Zustände
  modellieren; menschliche Emotionsbegriffe ausschließlich als nachgelagerte Interpretation zulassen
- [ ] Neuron-/Synapsenalter, Growth-/Pruning-Kosten und Neurogenese-Budgets ergänzen
- [ ] Regional Pressure, Hysterese und Anti-Oszillation integrieren
- [ ] Langhorizont-Stabilität unter chronischem Druck verifizieren
- [ ] Wetter-/Umweltrelevanz nur über nachgewiesene Kausalketten zur Systemkontinuität zulassen
- [ ] `BodySchemaManager` über dem `ConnectionManager` mit Integrations- und
  Kausalvertrauen, Verifikationstic, Abhängigkeiten und Fallbacks ergänzen
- [ ] `ActuatorHub`/`ActionRouter` für mehrere autorisierte Aktoren mit getrennten
  Capabilities, Safety Envelopes, Rate Limits und Auditpfaden implementieren
- [ ] `ActionReceipt` mit command_id, accepted, started, completed, failed,
  latency, error, safety_clamp und effect_observed einführen
- [ ] Befehlsannahme strikt von beobachtetem Handlungserfolg trennen
- [ ] Hashverkettetes Aktionsjournal dauerhaft in Operator-/Experiment-Storage persistieren
- [ ] Deterministischen `TaskOutcomeVerifier` als einzige Quelle für Task-Erfolg/Reward anbinden

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
- [ ] `EXP-BODY-0001` um Wetter-/Umwelt-Kontrollbedingung, Sensorqualität,
  Kausalpfad, Body-Schema-Übergänge und unabhängige Effect-Observation erweitern
- [ ] `EXP-MEM-0001`: Retention, Interferenz, Relearning, Transfer und Recall messen
- [ ] `EXP-AIR-0001`: Scientific Research Assistant erst nach Clean Freeze, Push und externer CI ausführen

### Forschungsprotokoll für jeden Lauf

- [x] Forschungsfrage, Hypothesen, Bedingungen, Kontrollen und Wiederholungszahl registrieren
- [x] Effektive Inputs, Outputs, Rewards, Audit-Status und Laufmetriken für EXP-EMB-0001 speichern
- [ ] DATA/EVID-Provenienz, Limitationen und unabhängige Wiederholungen prüfen
- [ ] Claims erst nach menschlicher Review aktualisieren als option

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
- [ ] AIRR gegen menschliche Referenzauswertung und mehrere Modelle evaluieren als option

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
