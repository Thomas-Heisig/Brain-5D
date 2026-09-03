# Brain-5D Research Roadmap

> Last updated: 2026-09-03
> Diese Datei beschreibt Forschungsfragen, nicht den Implementierungsstatus.

## Research Questions

| ID | Frage | Experiment |
| --- | --- | --- |
| R1 | Verändert produktives STDP reale Synapsengewichte reproduzierbar? | `EXP-STDP-0002` |
| R2 | Führt eine geschlossene Erfahrungsschleife zu verändertem späterem Verhalten? | `EXP-EMB-0001` |
| R3 | Bei welchen Zeitskalen treten Lern- und Strukturveränderungen auf? | `EXP-TIME-0001` |
| R4 | Erzeugt 5D messbare Eigenschaften jenseits anderer Topologien? | `EXP-5D-0001` |
| R5 | Stabilisieren Homeostase und Drives interne Zustände? | `EXP-REG-0001` |
| R6 | Wie reagiert Morphologie auf chronischen Druck? | `EXP-REG-0001` |
| R7 | Kompensiert das System den Verlust eines relevanten Sensors? | `EXP-BODY-0001` |
| R8 | Wie robust sind synaptisches, episodisches und semantisches Gedächtnis? | `EXP-MEM-0001` |
| R9 | Kann ein World Model Zustände vorhersagen und Transfer ermöglichen? | Alpha.9 experiments |
| R10 | Wie lernt das System aus Audio und visuellen Low-Level-Signalen? | Alpha.10 experiments |
| R11 | Kann Brain-5D Beziehungen aus provenance-gebundenem Wissen lernen? | Alpha.11 experiments |

## Reihenfolge

1. Productive STDP und geschlossene Learning Loop (`R1`, `R2`)
2. Laufzeit- und Zeitskalenkalibrierung (`R3`)
3. Dimensional Ablation (`R4`)
4. Selbstregulation und Sensorverlust (`R5` bis `R7`)
5. Memory und World Model (`R8`, `R9`)
6. Multimodales Lernen und Knowledge Grounding (`R10`, `R11`)

## Evidence Standard

Ein Ergebnis zählt erst als wissenschaftlicher Nachweis, wenn es auf einem
sauberen Source Freeze mit registriertem Protokoll, unabhängigen Wiederholungen,
vollständiger DATA/EVID-Provenienz und dokumentierten Limitationen beruht.
Dashboard-Zustände, aktivierte Flags und reine Implementierungstests sind keine
Evidenz für Lernwirkung.

## AI Research Track

Die AI-Unterstützung bleibt parallel zu den Brain-5D-Experimenten ein eigener
Forschungsgegenstand:

- Die Scientific AI Firewall klassifiziert Netzwerk, Synapsen, Struktur, Rewards,
  Memory und Experimentzustand als geschützte Ressourcen. AI-Zugriffe sind dort
  auf Beobachtung und Interpretation begrenzt; unbekannte Ressourcen scheitern
  fail-closed.

- **R-AI1 / RQ-AIR-001:** Erkennt der Scientific Research Assistant methodische Defekte zuverlässig?
- **R-AI2:** Wie genau sind AI Research Reports gegenüber einer menschlichen Referenzauswertung?

### Scientific AI Boundary

Die weitere AI-Integration folgt einer gestuften Rollen- und Autoritätsarchitektur:

- AI-0 Research AI: beobachtet und interpretiert außerhalb des Organismus.
- AI-1 Language Organ: übersetzt Signale read-only; das SNN lernt.
- AI-2 Cognitive Advisor: erzeugt typisierte Vorschläge ohne direkten Aktionspfad.
- AI-3 Controller: wird erst als eigenes, explizit registriertes Treatment untersucht.

Für alle Stufen werden AIExposure, Interaktionsprovenienz und kausale Beteiligung
separat erfasst. Shadow Mode, Frozen AI Replay, Counterfactual Twin Runs und
AI-Ablationen sind Voraussetzung, bevor AI-Einfluss als wissenschaftliche Ursache
interpretiert werden darf.

Der Research-Chat bleibt dabei ein konfigurierbarer, read-only Assistent: Ein eigener
System-Prompt darf Stil und Arbeitsweise präzisieren, erweitert aber weder die
Evidenzautorität noch die Experimentausführung. Externe Webquellen bleiben explizit
als unverified markiert.
- Jede Chat-Antwort trägt inzwischen einen digest-only `AIInteractionRecord` mit
	Exposure, kausaler Klassifikation und Read-only-Autorität; dies ist eine Basis für
	die noch offene vollständige Contract-/Firewall-Architektur.
- Der Ollama-Adapter liefert dafür Samplingparameter, Stop-Sequenzen, Timeout und
	Response-Digest; Modell-, Engine-, Hardware- und Tokenizer-Provenienz folgen noch.
- Die Contract-Basis unterscheidet nun Observation, Interpretation, Proposal,
	Intervention und Evidence als digest-only Datentypen ohne Ausführungsautorität.
- Der Research-Chat passiert eine explizite Read-only-Firewall; die vollständige
	Durchsetzung an Netzwerk-, Speicher- und Laufzeitgrenzen ist der nächste Ausbau.
- Die Authority-Matrix ist als validierter Contract im Research-Assistant-Paket
	hinterlegt und trennt AI-, Runtime-, Evidenz- und Human-Review-Autorität.
- Ein AST-Contract-Test schützt die AI-Pakete vor direkten Core-/Main-Imports;
	die Runtime- und Storage-Durchsetzung der Firewall bleibt davon getrennt offen.
- Experimentmanifeste tragen jetzt eine validierte `ai_exposure`-Stufe mit dem
	sicheren Default `none`; Interaktions- und Causal-Taint-Provenienz folgen separat.
- `AIInteractionRecord`-Einträge werden nun im Manifest persistiert und heben den
	aggregierten `causal_taint` nur monoton auf eine stärkere Einflussstufe an.
- Die Causal Card bündelt Interaktions-IDs, Rollen und Klassifikation; das
	Evidence-Gate verlangt für jeden nicht-puren Lauf ein registriertes AI-Treatment.
- Ollama liefert nun Request-/Response-Digests, Modell-ID, Completion-Grund und
	verfügbare Tokenmetriken; echte Artefakt- und Engine-Provenienz folgt über einen
	expliziten Provider-Manifestpfad.
- Fehlgeschlagene Ollama-Anfragen werden mit Request-ID, Request-Digest, Latenz,
	Backend und Retry-Status als eigene Audit-Ereignisse erfasst.
- Automatische Retries sind im Adapter deaktiviert und werden als `retry_count: 0`
	und `retry_policy: disabled` reproduzierbar ausgewiesen.
- Der `FrozenAIReplayBackend` erlaubt offline nur vorab registrierte Antworten,
	validiert Request-/Response-Digests und verweigert jeden Live-Fallback.
- `ObservationStream` erzeugt und validiert einen append-only JSONL-Stream für
	Beobachtungs-Replays mit Sequenz-, Tick- und Payload-Digest-Prüfung.
- AI-Beteiligung kann im Experimentmanifest mit einer validierten Stufe `R0` bis
	`R3` registriert werden; die Stufe ist eine Klassifikation und ersetzt keinen
	Twin-Run- oder Kontrollgruppen-Nachweis.
- Für Language-Organ-Kontrollgruppen stehen nun ein deterministisches Random-Sham
	und ein digestgebundenes Replay-Sham ohne Live-Fallback bereit; der bestehende
	Null-Backend bleibt als deaktivierte Baseline erhalten.
- Ein `ShadowMode` begrenzt AI auf Observation, Interpretation und markierte
	Proposal-Contracts. `propose` ist nur mit `PROPOSAL_ONLY` erlaubt; Ausführung
	ist nicht Bestandteil des Modus.
- Unterchats dürfen den Verlauf ihrer Elternräume als Gesprächskontext erben; dieser
	Kontext ist ausdrücklich keine DATA- oder EVIDENCE-Quelle.
- Vision- und Tool-Fähigkeiten müssen opt-in, begrenzt und reproduzierbar bleiben;
	freie System- oder Experimentausführung ist keine Chatfähigkeit.
- Multimodale Antworten bleiben vom Provider abhängig: Ollama-Vision liefert
	derzeit Textanalyse aus Bildern; Bildgenerierung wird nicht als verfügbar behauptet.
- **R-AI3:** Wie stark unterscheiden sich Modelle bei identischem ResearchPacket?
- **R-AI4:** Wie gut ist die Confidence der KI kalibriert?
- **R-AI5:** Wie unterscheiden sich menschliche und KI-wissenschaftliche Bewertungen?

AIRR ist ausschließlich KI-Interpretation. `scientific_evidence` bleibt immer
`false`; menschliche Prüfung wird als separates, append-only Review-Artefakt
gespeichert.

Der Research Self-Knowledge Chat darf Research und Docs lesend als Kontext
verwenden. Experimentausführung ist davon getrennt und ausschließlich über
registrierte, strukturierte Workflow-Parameter mit menschlicher Bestätigung
zulässig.

Antworten unterscheiden zwischen wissenschaftlichen Research-Quellen, technischen
Docs, aktuellem Runtime-Status und externen Webquellen. Ein abgeschlossener Versuch
oder ein Registry-Status ist kein Beleg für einen aktuell laufenden Prozess.
