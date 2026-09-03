# Brain-5D Roadmap

> Last updated: 2026-09-03
> Operative task list: [TODO.md](TODO.md)
> Research questions and experiment sequence: [RESEARCH_ROADMAP.md](RESEARCH_ROADMAP.md)

Die Infrastruktur ist weitgehend gebaut. Die Roadmap trennt deshalb bewusst
zwischen technischer Produktreife, wissenschaftlichem Nachweis und Betrieb.
Ein abgeschlossenes Engineering-Item ist kein wissenschaftlicher Claim.

## Verifizierter Repository-Stand

`main` ist lokal sauber und mit `origin/main` synchron (`b8d5025`). Die lokale
Vollsuite meldet **618 passed, 5 skipped**. Die zuletzt abgeschlossene
Engineering-Etappe trennt nun Operator-, Experiment- und Dev-Artefakte über
`StorageLayout`; Scientific Integrity, AI-Provenienz und kausale
AI-Betriebsstatus sind ebenfalls technisch abgedeckt. Externe CI und
wissenschaftliche EVID bleiben separate offene Nachweise.

## v0.5.0-alpha.7 — Controlled Experience & Learning Loop (implemented, evidence open)

Alpha.7 schliesst, wenn ein deterministisches Environment experimentell die
vollständige Kette zeigt:

```text
Wahrnehmung -> Handlung -> Konsequenz -> Lernen -> verändertes Verhalten
```

- [ ] Lokale Änderungen committen, pushen und vollständige GitHub-CI grün bekommen
- [ ] Operator-, Experiment- und Dev-Storage physisch trennen und Zugriffsmatrix prüfen
- [ ] `EXP-STDP-0002`: NeuralNetwork -> LearningEngine -> reale Synapse, unabhängige Runs
- [x] `EXP-EMB-0001` Protocol Run: Sensor -> Encoder -> Network -> Decoder -> Action -> Environment -> Reward
- [ ] `EXP-EMB-0001` als wissenschaftliche Evidenz mit unabhängigen Clean-Freeze-Runs abschliessen
- [ ] Zweiten Durchlauf derselben Situation ausführen und verändertes Verhalten nachweisen
- [x] Audio/Vision aus dem Alpha.7-Kernnachweis herauslösen; Hardware bleibt opt-in

## v0.5.0-alpha.7.1 — Performance & Persistent Operator (current)

- [ ] `full_change_scan` gegen causally complete `dirty_tracking` per A/B-Test validieren
- [ ] Identität von Digest, Gewichten, Neuronenzustand, Struktur und Restore nachweisen
- [ ] Dauerbetrieb für 1k, 10k, 100k und 1M Ticks mit reproduzierbaren Metriken vermessen
- [ ] Erst nach Gleichheitsnachweis `dirty_tracking` als Operator-Default aktivieren

## v0.5.0-alpha.8 — Adaptive Self-Regulation & Morphology

- [x] Typisierte Vital Signals mit Safety Ranges, Confidence, Freshness und
	UNKNOWN-Semantik als Digital-Interoception-Basis einführen
- [x] Erste deterministische Drives für Thermal Threat, Resource Pressure und
	Continuity Risk aus Interoception ableiten; nicht beobachtbare Drives bleiben unsicher
- [ ] Drives aus Energy, Thermal State, Sensor-/Netzwerkintegrität, Fehlern und Ressourcenlast ableiten
- [ ] Chronic Signals, Regional 5D Pressure, Neuron-/Synapsenalter und Growth Budgets integrieren
- [ ] Wachstum, Pruning, Kosten, Hysterese und Anti-Oszillation messen
- [ ] Stabilität unter Sensorausfall und chronischem Ressourcendruck nachweisen

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
