# Brain-5D Roadmap

> Last updated: 2026-09-04
> Operative task list: [TODO.md](TODO.md)
> Research questions and experiment sequence: [RESEARCH_ROADMAP.md](RESEARCH_ROADMAP.md)

Die Infrastruktur ist weitgehend gebaut. Die Roadmap trennt deshalb bewusst
zwischen technischer Produktreife, wissenschaftlichem Nachweis und Betrieb.
Ein abgeschlossenes Engineering-Item ist kein wissenschaftlicher Claim.

## Verifizierter Repository-Stand

`main` ist lokal mit `origin/main` synchron. Die deterministische
Task-Outcome-Verifikation ist implementiert und fokussiert getestet. Die lokale
Vollsuite meldet **682 passed, 5 skipped**. Black ist lokal bereinigt; Pyright
meldet noch Befunde. GitHub CI #307 scheitert deshalb in Black und Pyright.
Die zuletzt abgeschlossene
Engineering-Etappe trennt nun Operator-, Experiment- und Dev-Artefakte über
`StorageLayout`; Scientific Integrity, AI-Provenienz und kausale
AI-Betriebsstatus sind ebenfalls technisch abgedeckt. Die Dashboard-Navigation
behandelt nun statische und dynamische Arbeitsbereiche konsistent. Externe CI und
wissenschaftliche EVID bleiben separate offene Nachweise.
Experimentzusammenfassungen enthalten die zentralen Laufmetadaten in deutscher
Sprache; relative Artefakt-Links bleiben innerhalb des Datei-Viewers.

Die Runtime besitzt nun eine getrennte Clock-Ebene: `dt = 1 ms` bleibt konstant,
während `target_hz` beziehungsweise `MAX` nur die reale Tick-Abarbeitung steuern.
Achieved Hz, Realtime-Verhältnis, Latenz, Jitter, Sättigung und ein grobes
Phasenprofil werden im Operator- und Embodiment-Status veröffentlicht.

Das Release-Gate zeigt nun Live-Profil sowie alle Kriterien aus Gate A, B und C
gleichzeitig in einer responsiven Ansicht. Manuelle Re-Checks laufen über den
zentralen State Store; `pending`, `stale` und `unknown` bleiben sichtbar und
werden nicht als erfolgreich dargestellt. Jede Kriterienzeile öffnet per Klick
oder Tastatur einen Detaildialog mit dem konkreten backendseitigen Grund,
Quelle, Live-Status und vorhandener Evidence.

## v0.5.0-alpha.7 — Controlled Experience & Learning Loop (implemented, evidence open)

- [x] Learning-Preparation-Formular für Lernziel, Erfolgskriterium,
  Provenienz und Kontrollen mit proposal-only KI-Vorbereitung und vollständigem Reset
- [x] Expliziten Operator-Lernstart über einen getrennten, validierten
	LearningEngine-Workflow mit DATA/Manifest/Report und sichtbarem Ergebnis ergänzen
- [x] Begrenzte KI-Kontextlänge im Learning Studio bis zum Chat-Backend durchreichen
- [x] Nach jedem erfolgreich abgeschlossenen Dashboard-Experiment einen post-hoc
	AIRR-Bericht anhängen; fehlendes Backend bleibt sichtbar `unavailable`
- [x] Science-suite Läufe veröffentlichen DATA, Workflow, technischen Report und
	bei konfiguriertem Backend den post-hoc AIRR-Bericht gemeinsam im Manifest
- [x] Productive STDP und ein versionierter Before/After-Lernwiederholungslauf
	über den Dashboard-Workflow als DATA/Manifest/Report veröffentlichen

Alpha.7 schliesst, wenn ein deterministisches Environment experimentell die
vollständige Kette zeigt:

```text
Wahrnehmung -> Handlung -> Konsequenz -> Lernen -> verändertes Verhalten
```

- [ ] Lokale Änderungen committen, pushen und vollständige GitHub-CI grün bekommen
- [x] Type-, Build-, Lint- und Runtime-Fehler des aktuellen Stands beheben und lokal verifizieren
- [ ] Operator-, Experiment- und Dev-Storage physisch trennen und Zugriffsmatrix prüfen
- [x] `EXP-STDP-0002`: NeuralNetwork -> LearningEngine -> reale Synapse, drei unabhängige Dashboard-DATA-Runs
- [x] Versionierter Before/After-Lernwiederholungslauf `EXP-LEARN-20260903-2300` mit drei unabhängigen Dashboard-DATA-Runs
- [x] Zehn-Seed-Replikation der geschlossenen Lernschleife `EXP-LEARN-20260903-2330` mit 0/10 Baseline- und 10/10 After-Zielspikes
- [x] Deterministischer Suite-Runner für PING, TEMP, produktives STDP und Before/After-Lernvergleich ergänzt; wissenschaftliche DATA-Ausführung bleibt separat
- [x] PING und TEMP über den Dashboard-Workflow ausgeführt und als Manifest/Report/DATA publiziert; EVID bleibt Clean-Freeze-gated
- [x] `EXP-PING-0001-v2` versioniert ausgeführt: sechs identische Replikatpaare
	bestätigen pro Seed und Rekurrenzbedingung denselben Vorher-Digest und dieselbe
	Response-Signatur; EVID bleibt Clean-Freeze-gated
- [x] TIME und 5D über den Dashboard-Workflow ausgeführt und als Manifest/Report/DATA publiziert; EVID bleibt Clean-Freeze-gated
- [x] `EXP-EMB-0001` Protocol Run: Sensor -> Encoder -> Network -> Decoder -> Action -> Environment -> Reward
- [ ] `EXP-EMB-0001` als wissenschaftliche Evidenz mit unabhängigen Clean-Freeze-Runs abschliessen
- [ ] Zweiten Durchlauf derselben Situation ausführen und verändertes Verhalten nachweisen
- [ ] Wissenschaftliche EVID für den operator-ausgelösten Learning-Studio-Lauf nach
	Clean Freeze und unabhängiger Review erzeugen
- [x] Persistente PreparedLearningPlans, typisierte Preparation-API und serverseitige
	Guard-/Freigabeprüfung ergänzen
- [x] `LearningSourceRef` aus validierter Knowledge-Provenienz und Environment-Capture
	ableiten; unvollständige Capture-Records werden fail-closed abgewiesen
- [x] Train-, Validation- und Holdout-Digests serverseitig auf Partition-Overlap
	prüfen und Label-Digests aus dem Holdout ausschließen
- [ ] Pre-/Post-Probes, TaskOutcomeVerifier und Holdout-Leakage im Learning-Lauf
	als DATA-Artefakte verknüpfen
- [ ] `EXP-LEARN-0001` als ON/OFF- und Holdout-Protokoll registrieren und ausführen
- [ ] Curriculum-Vergleich `EXP-CURR-0001` für deterministische, menschliche und
	KI-gestützte Vorbereitung registrieren
- [x] Audio/Vision aus dem Alpha.7-Kernnachweis herauslösen; Hardware bleibt opt-in

## v0.5.0-alpha.7.1 — Performance & Persistent Operator (current)

- [x] Runtime Clock mit Target-/Achieved-Rate, `MAX`, Realtime-Verhältnis,
  Latenz, Jitter und Compute-Limit-Status einführen; `dt` bleibt unverändert
- [x] Grobes Tick-Phasenprofil im Runtime-/Embodiment-Status veröffentlichen
- [x] Embodiment-Regler sowie vollständige Phaseninstrumentierung ergänzen; `network.step_batch(n)` ist gegen Einzel-Ticks validiert

- [ ] `full_change_scan` gegen causally complete `dirty_tracking` per A/B-Test validieren
- [x] Identität von Digest, Gewichten, Neuronenzustand, Struktur und Restore nachweisen (A/B/C-Produktionstest und Fresh-Process-Artefakt verifiziert)
- [ ] Dauerbetrieb für 1k, 10k, 100k und 1M Ticks mit reproduzierbaren Metriken vermessen
- [ ] Erst nach Gleichheitsnachweis `dirty_tracking` als Operator-Default aktivieren

## v0.5.0-alpha.8 — Adaptive Self-Regulation & Morphology

- [x] Kontrollierten `NetworkImpulseProbe` mit serialisierbarer
	`NetworkResponseSignature` für beobachtbare Impulsantworten einführen
- [x] `TemporalStateMemory` und `TemporalComparator` für FAST/MEDIUM/SLOW-
	Referenzzustände ohne Zurückspulen des Runtime-Zustands einführen
- [x] Interne Regelgrößen für Thermal Margin, Energy Reserve, Continuity Risk,
	Sensory Integrity, Resource Pressure und optional Task Progress deterministisch
	ableiten; unbekannte Quellen bleiben unsicher
- [x] Bounded funktionale Zustandsqualitäten für Valence, Activation, Safety und
	Uncertainty ableiten, ohne daraus menschliche Emotionen oder Bewusstsein abzuleiten
- [x] Deterministisches Morphology-Ledger für Geburts-Ticks, Strukturkosten und
	getrennte Growth-/Pruning-Budgets ergänzen
- [x] Strukturvorschläge mit per-Mechanismus-Hysterese gegen Druck-Oszillation
	absichern; Release-Schwelle und deterministisches Re-Arm-Intervall bleiben
	konfigurierbar
- [ ] `EXP-PING-0001` und `EXP-TEMP-0001` als unabhängige Clean-Freeze-Runs
	mit DATA/EVID-Provenienz ausführen
- [ ] Drives aus Energy, Thermal State, Sensor-/Netzwerkintegrität, Fehlern und Ressourcenlast ableiten
- [ ] Chronic Signals und Regional 5D Pressure integrieren; Neuron-/Synapsenalter
	und Growth Budgets sind technisch vorhanden
- [ ] Wachstum, Pruning, Kosten, Hysterese und Anti-Oszillation messen
- [ ] Stabilität unter Sensorausfall und chronischem Ressourcendruck nachweisen
- [x] Typisierten `ActionReceipt` einführen und Befehlsannahme strikt von
	beobachtetem Environment-Effekt trennen
- [x] Hashverkettete Action-Audit-Records dauerhaft als JSONL speichern und
	beim Wiederöffnen auf Kettenintegrität prüfen
- [x] `ActuatorHub`/`ActionRouter` für mehrere autorisierte Aktoren mit getrennten
	Capabilities, Safety Envelopes, Rate Limits und Auditpfaden implementieren
- [x] Deterministischen `EXP-REG-0001`-DATA-Runner für nominale, chronische
	Druck- und UNKNOWN-Telemetriebedingungen anbinden; wissenschaftliche EVID bleibt offen
- [x] Deterministischen `TaskOutcomeVerifier` als alleinige technische Quelle
	für Task-Erfolg und Reward anbinden; fehlende Beobachtungen bleiben UNKNOWN

## v0.5.0-alpha.9 — Memory & World Model

- [ ] Synaptic, episodic und semantic memory getrennt modellieren
- [ ] Persistent World Model mit Provenienz und gelernten Körpermodellen verbinden
- [ ] Retention, Interferenz, Relearning, Transfer, Recall und Catastrophic Forgetting messen

## v0.5.0-alpha.10 — Multimodal Perception

- [ ] AudioFrame in Amplitude, Frequenzbänder, Onsets und Rhythmus zerlegen
- [ ] VisualFrame in Helligkeit, Kanten, Bewegung, Position und Novelty zerlegen
- [ ] Sensorische Low-Level-Features in SNN-Populationen einspeisen

## v0.5.0-alpha.11 — Knowledge Grounding

- [ ] Knowledge Intake mit Quelle, Provenienz und KnowledgeFrame einführen
- [ ] Lernen aus sprachlich/symbolisch vermittelten Beziehungen messen
- [ ] LLM bleibt Übersetzer und erhält keine Speicher-, Reward- oder Mutationsautorität

## v0.5.0-alpha.12 — Language & Reflective Interface

- [ ] SignalFrame, MemoryFrame, WorldModelFrame und CurrentDriveFrame an das Language Organ geben
- [ ] Zustandsbeschreibung und Reflexion ermöglichen, ohne kausale Schreibrechte zu vergeben

## v1.0 — Integrated Embodied Cognitive Research Platform

Eine reproduzierbare, persistente und evaluierbare Plattform für verkörperte
Forschung mit begrenzten Aktionen. Dies ist kein Claim über AGI oder Bewusstsein.

## Historische Releases

- `v0.5.0-alpha.5`: Integration Hardening, Verification und Structural E2E
- `v0.5.0-alpha.6`: Operator Workbench, Observable Runtime und Evidence Gates
