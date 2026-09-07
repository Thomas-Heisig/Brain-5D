# Brain-5D Research Catalog

*Generiert am 2026-09-07*

## Übersicht

- **Forschungsfragen:** 48
- **Hypothesen:** 47
- **Claims:** 8
- **Literaturquellen:** 10

---

## 5D Topology

### RQ-5D-001

**Frage:** Hat die fünfdimensionale Anordnung einen messbaren Effekt auf die Netzwerkdynamik?

**Status:** open
**Relevanz:** Kernfrage des gesamten Brain-5D-Projekts.

**Hypothesen:**
- `H-5D-001-A`: Ein 5D-angeordnetes Netzwerk zeigt signifikant andere Dynamik als ein 2D/3D-Netzwerk gleicher Neuronenzahl. *(untested)*

**Claims:**
- `CLAIM-5D-001`: Die fünfdimensionale Organisation verbessert die Robustheit gegenüber lokalen Strukturverlusten. *(untested, none)*

**Literatur:**
- `SRC-IZHIKEVICH-2003`: Eugene M. Izhikevich et al. (2003)

---

### RQ-5D-002

**Frage:** Wie verändert Dimensionalität die Signalpropagation im Netzwerk?

**Status:** open
**Relevanz:** Verständnis der Informationsausbreitung in höherdimensionalen SNNs.

**Hypothesen:**
- `H-5D-002-A`: Die Signalpropagationszeit und -reichweite skaliert mit der Dimensionalität des Netzwerks. *(untested)*

---

### RQ-5D-003

**Frage:** Entsteht in 5D eine andere Modularität als in niedrigeren Dimensionen?

**Status:** open
**Relevanz:** Modularität ist ein Schlüsselkonzept für funktionale Spezialisierung.

**Hypothesen:**
- `H-5D-003-A`: 5D-Netzwerke entwickeln eine höhere Modularität als niedrigdimensionale Netzwerke. *(untested)*

---

### RQ-5D-004

**Frage:** Sind zusätzliche Dimensionen informationstragend oder lediglich zusätzliche Koordinaten?

**Status:** open
**Relevanz:** Eine der wichtigsten Fragen des gesamten Projekts — betrifft fundamentale Natur der 5D-Repräsentation.

**Hypothesen:**
- `H-5D-004-A`: Die zusätzlichen Dimensionen in 5D sind informationstragend und nicht redundant. *(untested)*

**Claims:**
- `CLAIM-5D-002`: 5D-Netzwerke zeigen eine höhere Informationskapazität als niedrigdimensionale Netzwerke gleicher Neuronenzahl. *(untested, none)*

---

### RQ-5D-005

**Frage:** Verändert 5D-Geometrie Propagation, Robustheit oder Dynamik, wenn Neuronenzahl, Synapsenzahl, Grad- und Gewichtsmuster sowie Stimulusplan kontrolliert gleich bleiben?

**Status:** open
**Relevanz:** Der kleine 5D-Test in EXP-GEN-0021 isolierte keinen dimensionsspezifischen Effekt.

**Hypothesen:**
- `H-5D-005-A`: Mindestens eine registrierte Propagationsmetrik unterscheidet sich in 5D von topology-matched niedrigdimensionalen Einbettungen. *(untested)*

---

## AI-Assisted Research

### RQ-AIR-001

**Frage:** Kann ein LLM-basierter Scientific Research Assistant methodische Fehler in Brain-5D-Experimenten anhand eines standardisierten ResearchPacket zuverlässig identifizieren?

**Status:** open
**Relevanz:** Prüft den wissenschaftlichen Nutzen der Research-Assistant-Architektur, ohne ihr wissenschaftliche Entscheidungsgewalt zu geben.

**Hypothesen:**
- `H-AIR-001-A`: Ein Scientific Research Assistant mit strukturiertem ResearchPacket erkennt vorab definierte methodische Defekte mit höherem F1-Score als dasselbe Modell mit einem unstrukturierten Experimentbericht. *(untested)*

**Claims:**
- `CLAIM-AIR-001`: Ein standardisiertes ResearchPacket verbessert die Identifikation vorab definierter methodischer Fehler gegenüber einem unstrukturierten Experimentbericht. *(untested, none)*

---

## Adaptive Resource Allocation

### RQ-MSBA-E02

**Frage:** Erhaelt kostenadaptive Gateway-Allokation unter identischem Gesamtbudget mehr Aufgabenleistung als fixe oder zufaellige Allokation?

**Status:** open
**Relevanz:** Operationalisiert die Frage, ob Ressourcenhomoeostase funktionalen Nutzen statt nur Verbrauchsreduktion erzeugt.

**Hypothesen:**
- `H-MSBA-E02-A`: Adaptive Utility-minus-Cost-Allokation erzielt bei gleichem Ressourcenbudget hoehere Aufgabenleistung oder laengere funktionsfaehige Laufzeit als fixe und zufaellige Kontrollen. *(untested)*

---

## Closed-loop Regulation

### RQ-REG-002

**Frage:** Verbessert aktive Regulation Stabilität und Recovery eines laufenden SNN unter identischen Ressourcen- oder Sensorperturbationen gegenüber deaktivierter Regulation?

**Status:** open
**Relevanz:** EXP-GEN-0021 validierte Regulationszustände, aber noch keinen funktionalen Closed-loop-Nutzen.

**Hypothesen:**
- `H-REG-002-A`: Der registrierte Regulationsfeedbackpfad verbessert die Recovery-Metrik nach einer identischen Druckphase gegenüber Regulation-off. *(untested)*

---

## Determinism

### RQ-DET-001

**Frage:** Bleibt die Spikefolge bei gleichem Seed, Input und Zustand deterministisch?

**Status:** open
**Relevanz:** Determinismus ist Voraussetzung für kausale Analyse und reproduzierbare Forschung.

**Hypothesen:**
- `H-SNN-003-A`: Bei gleichem Seed, Input und Anfangszustand sind Spike-Abfolgen deterministisch identisch. *(supported)* — Evidenz: EVID-2026-01, EVID-2026-03, EVID-2026-05, EVID-2026-07, EVID-2026-09, EVID-2026-11, EVID-2026-13, EVID-2026-15

**Claims:**
- `CLAIM-DET-001`: Brain-5D erzeugt bei identischem Seed, Input und Anfangszustand deterministisch identische Spike-Abfolgen und Netzwerkzustände. *(inconclusive, low)* — Evidenz: EVID-2026-01, EVID-2026-03, EVID-2026-05, EVID-2026-07, EVID-2026-09, EVID-2026-11, EVID-2026-13, EVID-2026-15

**Literatur:**
- `SRC-IZHIKEVICH-2003`: Eugene M. Izhikevich et al. (2003)

**Evidenzen:** EVID-2026-01, EVID-2026-03, EVID-2026-05, EVID-2026-07, EVID-2026-09, EVID-2026-11, EVID-2026-13, EVID-2026-15

---

## Digital Gateway Integrity

### RQ-MSBA-E04

**Frage:** Bleibt digitale Payload-Integritaet unter Ressourcen-Drosselung exakt erhalten, waehrend lediglich Durchsatz und Admission sinken?

**Status:** open
**Relevanz:** Sichert die wissenschaftliche und technische Trennung zwischen lernbarer Weiterleitung und unveraenderlicher digitaler Nutzlast.

**Hypothesen:**
- `H-MSBA-E04-A`: Ressourcen-Drosselung reduziert die zugelassene Symbolrate, erzeugt aber keine Mutation der digitalen Payload oder ihrer Checksumme. *(untested)*

---

## Embodiment

### RQ-EMB-001

**Frage:** Kann Brain-5D in einer Sensor-Aktor-Schleife (Embodiment) sinnvoll agieren?

**Status:** open
**Relevanz:** Embodiment erweitert Brain-5D von einer reinen Simulation zu einem interaktiven System.

**Hypothesen:**
- `H-EMB-001-A`: Brain-5D kann in einer geschlossenen Sensor-Aktor-Schleife zielgerichtet agieren. *(untested)*

---

## Epistemology

### RQ-EPIST-001

**Frage:** Was gilt als Erkenntnis des Systems Brain-5D im Unterschied zur Erkenntnis des Forschers?

**Status:** open
**Relevanz:** Epistemologische Grundlagen für maschinelle Wissensproduktion.

**Hypothesen:**
- `H-EPIST-001-A`: Systemerkenntnis und Forschererkenntnis sind in Brain-5D kategorial unterscheidbar. *(untested)*

---

## Ethics

### RQ-ETH-001

**Frage:** Wer ist der Autor von Brain-5D-Erkenntnissen — Mensch, Modell oder System?

**Status:** open
**Relevanz:** Grundsatzfrage zur Autorenschaft und Verantwortung in KI-gestützter Forschung.

**Hypothesen:**
- `H-ETH-001-A`: Die Autorenschaft von Brain-5D-Erkenntnissen ist ein verteiltes Phänomen zwischen Mensch, Modell und System. *(untested)*

---

### RQ-ETH-002

**Frage:** Wo liegt die Kontrolle und Verantwortung bei Brain-5D-Experimenten?

**Status:** open
**Relevanz:** Verantwortungsverteilung zwischen Entwickler, Modell und automatisiertem System.

**Hypothesen:**
- `H-ETH-002-A`: Die Kontrolle über Brain-5D-Experimente liegt primär beim Entwickler, nicht beim automatisierten System. *(untested)*

---

## Homeostasis

### RQ-HOM-001

**Frage:** Kann synaptische Homeostase die Feuerrate in einem SNN stabilisieren?

**Status:** open
**Relevanz:** Homeostase ist ein zentraler biologischer Regulationsmechanismus.

**Hypothesen:**
- `H-HOM-001-A`: Synaptische Homeostase hält die mittlere Feuerrate eines SNN innerhalb eines definierten Sollbereichs. *(untested)*

**Literatur:**
- `SRC-TURRIGIANO-2008`: Gina G. Turrigiano et al. (2008)

---

### RQ-HOM-002

**Frage:** Wie interagiert Homeostase mit STDP? Wirken sie synergistisch oder antagonistisch?

**Status:** open
**Relevanz:** Das Zusammenspiel beider Mechanismen ist entscheidend für stabile Plastizität.

**Hypothesen:**
- `H-HOM-002-A`: Homeostase und STDP wirken synergistisch: Homeostase verhindert STDP-induzierte Drift. *(untested)*

**Literatur:**
- `SRC-TURRIGIANO-2008`: Gina G. Turrigiano et al. (2008)

---

## Language Organ

### RQ-LLM-001

**Frage:** Kann ein Language Organ (SNM ↔ LLM) sinnvolle Kommunikation ermöglichen?

**Status:** open
**Relevanz:** Schnittstelle zwischen neuronaler Simulation und natürlicher Sprache.

**Hypothesen:**
- `H-LLM-001-A`: Ein Language Organ kann SNN-Zustände in sinnvolle natürliche Sprache übersetzen. *(untested)*

---

## Learning Generalization

### RQ-GEN-001

**Frage:** Verbessert reward-moduliertes lokales Lernen die Leistung auf Holdout- und Perturbationsbedingungen, die nicht zur Anpassung verwendet wurden?

**Status:** open
**Relevanz:** EXP-GEN-0021 zeigte funktionelle Änderung unter Learning-on, aber keine Generalisierung.

**Hypothesen:**
- `H-GEN-001-A`: Learning-on verbessert die Erfolgsrate auf vorab registrierten Perturbationsproben gegenüber Learning-off und Sham-Replay. *(untested)*

---

## Learning Timescale

### RQ-TIME-001

**Frage:** Wie verändert sich die messbare Laufzeit und Lernaktivität über die registrierte Tick-Leiter?

**Status:** open
**Relevanz:** Kalibrierung der zeitlichen Ausführung vor Langzeitexperimenten.

**Hypothesen:**
- `H-TIME-001-A`: Die Tick-Leiter liefert reproduzierbare Durchsatz- und Zustandsmessungen bis 1.000.000 Ticks. *(untested)*

---

## Lifelong Learning

### RQ-LIFE-001

**Frage:** Bleibt zuvor erworbene Lernleistung bei sequenziellen Aufgaben erhalten oder entstehen messbare Interferenzeffekte?

**Status:** open
**Relevanz:** Das positive Single-Task-Learningsignal aus EXP-GEN-0021 motiviert Retentionstests.

**Hypothesen:**
- `H-LIFE-001-A`: Sequenzielle Lernaufgaben zeigen eine messbare Veränderung der Retentions- oder Gewichtssignatur gegenüber einer Single-Task-Baseline. *(untested)*

---

## Memory

### RQ-MEM-001

**Frage:** Kann Brain-5D Informationen über synaptische Gewichte speichern und zuverlässig abrufen?

**Status:** open
**Relevanz:** Gedächtnis ist eine Kernfunktion neuronaler Systeme.

**Hypothesen:**
- `H-MEM-001-A`: Brain-5D kann Informationen über synaptische Gewichte speichern und auf Input-Muster abrufen. *(untested)*

---

## Multimodal Compensation

### RQ-MSBA-E05

**Frage:** Erhoeht das System nach Ausfall oder Degradation einer Modalitaet gezielt die Allokation einer anderen Modalitaet, wenn deren erwarteter Nutzen die Mehrkosten rechtfertigt?

**Status:** open
**Relevanz:** Prueft adaptive Kompensation unter kontrolliertem Modalitaetsausfall und gleichen Ressourcenbudgets.

**Hypothesen:**
- `H-MSBA-E05-A`: Nach kontrolliertem Modalitaetsausfall steigt die alternative Gateway-Allokation nur bei guenstigem Utility-Kosten-Verhaeltnis und verbessert die Aufgaben-Recovery gegenueber fixen und No-Compensation-Kontrollen. *(untested)*

---

## Multimodal Energy Efficiency

### RQ-MSBA-E01

**Frage:** Unterscheiden sich Audio-, Vision- und Digital-Gateways systematisch im Ressourcenverbrauch pro verwertbarer Information oder korrekter Entscheidung?

**Status:** open
**Relevanz:** Prueft die Ressourcenökonomie modalitaetsspezifischer Neural-Symbiosis-Gateways unter vergleichbaren Aufgabenbedingungen.

**Hypothesen:**
- `H-MSBA-E01-A`: Unter kontrollierter Aufgabeninformation unterscheiden sich Audio-, Vision- und Digital-Gateways reproduzierbar in Energie- und Synapsenkosten pro korrekter Entscheidung. *(untested)*

---

## Network Dynamics

### RQ-PING-001

**Frage:** Ist die beobachtete Network-Impulse-Response bei identischem Zustand und Seed reproduzierbar?

**Status:** open
**Relevanz:** Reproduzierbarkeit der kontrollierten Impulsantwort.

**Hypothesen:**
- `H-PING-001-A`: Identische Impulse erzeugen bei identischem Anfangszustand dieselbe beobachtete Response-Signatur. *(untested)*

---

## Recurrent Dynamics

### RQ-REC-001

**Frage:** Unter welchen Rekurrenzgewichten und Delays wechselt Brain-5D zwischen sofortigem Erlöschen, transienter rekurrenter Aktivität und bis zum Beobachtungsende persistierender Aktivität?

**Status:** open
**Relevanz:** EXP-GEN-0021 zeigte einen klaren rekurrenzabhängigen Dynamikunterschied, aber noch keine Parametergrenze.

**Hypothesen:**
- `H-REC-001-A`: Rekurrenzgewicht und Delay erzeugen reproduzierbare Übergänge zwischen sofortigem Erlöschen, transienter Aktivität und Aktivität bis zum Ende des registrierten Beobachtungsfensters. *(untested)*

---

### RQ-REC-002

**Frage:** Wie verändern Loop-Delay und skalierte Rekurrenzstruktur Persistenzdauer, Inter-Spike-Dynamik und Extinktionsverhalten?

**Status:** open
**Relevanz:** Der Drei-Neuronen-Loop aus EXP-GEN-0021 reicht nicht für Skalierungsaussagen.

**Hypothesen:**
- `H-REC-002-A`: Größere rekurrente Delays verändern Persistenzdauer oder Propagation Depth gegenüber dem Delay-1-Kontrollarm. *(untested)*

---

## Regulation

### RQ-REG-001

**Frage:** Wie reagieren Drives und funktionale Zustandsgrößen auf nominale, chronische und unbekannte Telemetrie?

**Status:** open
**Relevanz:** Deterministische Prüfung der Selbstregulation unter Ressourcen- und Sensorbedingungen.

**Hypothesen:**
- `H-REG-001-A`: Chronischer Druck erhöht deterministisch Resource Pressure und Thermal Threat, während unbekannte Telemetrie Unsicherheit erhält. *(untested)*

---

## Replication

### RQ-REPL-001

**Frage:** Bleiben die in EXP-GEN-0021 beobachteten Rekurrenz- und Learning-Effekte unter unabhängigen Initialisierungen und sauberem Prozess erhalten?

**Status:** open
**Relevanz:** Identische Seedsignaturen zeigen Determinismus, aber keine statistisch unabhängige Replikation.

**Hypothesen:**
- `H-REPL-001-A`: Der Rekurrenzbehandlungseffekt bleibt über mindestens 20 vorab registrierte Initialisierungsseeds in Richtung und Größenordnung konsistent. *(untested)*

---

## Research Infrastructure

### RQ-SUITE-001

**Frage:** Erzeugt der vollstaendige Science-Suite-Lauf unter gemeinsamer Provenienz vollstaendige und intern konsistente Diagnoseartefakte fuer alle registrierten Teilprotokolle?

**Status:** open
**Relevanz:** Trennt technische Omnibus-Validierung von hypothesenspezifischer wissenschaftlicher Evidenz.

**Hypothesen:**
- `H-SUITE-001-A`: Alle Science-Suite-Teilprotokolle erfuellen in einem gemeinsamen Lauf ihre registrierten Ausfuehrungsvertraege und erzeugen auswertbare DATA-, Statistik- und Provenienzartefakte. *(untested)*

---

## Runtime Performance

### RQ-PERF-001

**Frage:** Welche Subsysteme dominieren die Wall-Time wissenschaftlicher Läufe und welche Optimierungen erhöhen den Durchsatz bei erhaltener deterministischer Äquivalenz?

**Status:** open
**Relevanz:** EXP-GEN-0021 zeigte eine große Differenz zwischen isoliertem Tick-Durchsatz und Suite-Laufzeit.

**Hypothesen:**
- `H-PERF-001-A`: Der Core-Tick-Loop ist nicht der einzige dominante Kostenblock vollständiger Science-Läufe; mindestens ein zusätzlicher gemessener Subsystemanteil ist relevant. *(untested)*

---

## STDP

### RQ-STDP-001

**Frage:** Erzeugt pair-based STDP unter definierten Pre/Post-Zeitabständen eine asymmetrische Gewichtsanpassung?

**Status:** open
**Relevanz:** Fundamentale STDP-Eigenschaft, die in Brain-5D verifiziert werden muss.

**Hypothesen:**
- `H-STDP-001-A`: Pair-based STDP erzeugt unter definierten Pre/Post-Zeitabständen eine asymmetrische Gewichtsanpassung (LTP bei Δt > 0, LTD bei Δt < 0). *(untested)*

**Claims:**
- `CLAIM-STDP-001`: Pair-based STDP erzeugt unter definierten Pre/Post-Zeitabständen eine asymmetrische Gewichtsanpassung. *(untested, none)*

**Literatur:**
- `SRC-SONG-ABBOTT-2000`: Sen Song et al. (2000)
- `SRC-BI-POO-1998`: Guo-Qiang Bi et al. (1998)

---

### RQ-STDP-002

**Frage:** Bleiben STDP-getriebene Gewichte unter Dauerstimulation stabil oder oszillieren/explodieren sie?

**Status:** open
**Relevanz:** Stabilität ist Voraussetzung für längerfristiges Lernen.

**Hypothesen:**
- `H-STDP-002-A`: STDP-getriebene Gewichte konvergieren unter Dauerstimulation zu einer stabilen Verteilung. *(untested)*

**Literatur:**
- `SRC-SONG-ABBOTT-2000`: Sen Song et al. (2000)

---

## Scaling

### RQ-SCALE-001

**Frage:** Skaliert Brain-5D von 5.000 auf Millionen Neuronen ohne qualitative Dynamikveränderung?

**Status:** open
**Relevanz:** Nachweis der Architekturskalierbarkeit.

**Hypothesen:**
- `H-SCALE-001-A`: Brain-5D skaliert von 5.000 auf 1.000.000 Neuronen ohne qualitative Änderung der Spikedynamik. *(untested)*

---

## Self-Organization

### RQ-SELF-001

**Frage:** Entstehen in Brain-5D spontan funktionale Cluster oder Module?

**Status:** open
**Relevanz:** Selbstorganisation ist ein Schlüsselmerkmal biologischer neuronaler Systeme.

**Hypothesen:**
- `H-SELF-001-A`: In Brain-5D entstehen spontan funktionale Cluster durch lokale STDP-Regeln. *(untested)*

**Claims:**
- `CLAIM-SELF-001`: In Brain-5D entstehen spontan funktionale Module ohne explizite Programmierung. *(untested, none)*

**Literatur:**
- `SRC-IZHIKEVICH-2003`: Eugene M. Izhikevich et al. (2003)

---

### RQ-SELF-002

**Frage:** Ist die beobachtete Selbstorganistion emergenter Natur oder durch die Architektur programmiert?

**Status:** open
**Relevanz:** Unterscheidung zwischen echter Emergenz und deterministischer Architekturfolge.

**Hypothesen:**
- `H-SELF-002-A`: Die beobachtete Selbstorganisation ist emergent und nicht durch die Architektur vorgegeben. *(untested)*

---

## Spiking Neural Networks

### RQ-SNN-001

**Frage:** Kann Brain-5D stabile Spike-Dynamiken über lange Simulationszeiträume erzeugen?

**Status:** open
**Relevanz:** Grundvoraussetzung für alle weiteren Lern- und Selbstorganisationsexperimente.

**Hypothesen:**
- `H-SNN-001-A`: Brain-5D erzeugt über mindestens 100.000 Simulations-Ticks stabile Spike-Dynamiken ohne numerische Drift. *(untested)*

**Literatur:**
- `SRC-IZHIKEVICH-2003`: Eugene M. Izhikevich et al. (2003)
- `SRC-GERSTNER-2014`: Wulfram Gerstner et al. (2014)

---

### RQ-SNN-002

**Frage:** Kann das eingesetzte Neuronenmodell bei konstantem Input reproduzierbare Spikefolgen erzeugen?

**Status:** open
**Relevanz:** Basis für deterministische Reproduzierbarkeit aller Experimente.

**Hypothesen:**
- `H-SNN-002-A`: Das Izhikevich-Neuronenmodell erzeugt bei identischem Input reproduzierbare Spikefolgen. *(untested)*

**Literatur:**
- `SRC-IZHIKEVICH-2003`: Eugene M. Izhikevich et al. (2003)
- `SRC-GERSTNER-2014`: Wulfram Gerstner et al. (2014)

---

### RQ-SNN-003

**Frage:** Wie variiert die Propagation mit der Topologie?

**Status:** open
**Relevanz:** Grundlegendes Verständnis der Signalausbreitung in 5D-SNNs.

**Literatur:**
- `SRC-WATTS-STROGATZ-1998`: Duncan J. Watts et al. (1998)
- `SRC-BARABASI-1999`: Albert-László Barabási et al. (1999)

---

### RQ-SNN-004

**Frage:** Wie verändert STDP die synaptische Gewichtsmatrix?

**Status:** open
**Relevanz:** Zentrale Fragestellung für plastische Netzwerke.

**Hypothesen:**
- `H-SNN-004-A`: STDP führt zu einer meßbaren asymmetrischen Verschiebung der synaptischen Gewichtsverteilung. *(untested)*

**Claims:**
- `CLAIM-SNN-001`: Pair-based STDP erzeugt unter definierten Pre/Post-Zeitabständen eine asymmetrische Gewichtsanpassung. *(untested, none)*

**Literatur:**
- `SRC-SONG-ABBOTT-2000`: Sen Song et al. (2000)
- `SRC-BI-POO-1998`: Guo-Qiang Bi et al. (1998)

---

### RQ-SNN-005

**Frage:** Verbessert STDP tatsächlich eine definierte Lernleistung?

**Status:** open
**Relevanz:** Wissenschaftlich wesentlich stärker als reine Gewichtsänderung — benötigt Kontrollgruppe ohne STDP.

**Hypothesen:**
- `H-SNN-005-A`: Ein Netzwerk mit STDP zeigt signifikant bessere Lernleistung als ein Netzwerk ohne STDP. *(untested)*

**Literatur:**
- `SRC-SONG-ABBOTT-2000`: Sen Song et al. (2000)
- `SRC-BI-POO-1998`: Guo-Qiang Bi et al. (1998)

---

## Storage

### RQ-STORAGE-001

**Frage:** Kann ein vollständiger neuronaler Zustand verlustfrei im .b5d-Modell gespeichert werden?

**Status:** open
**Relevanz:** Grundlage für Persistenz und Checkpointing.

**Hypothesen:**
- `H-STOR-001-A`: Ein vollständiger neuronaler Zustand kann verlustfrei im .b5d-Format gespeichert und zurückgeladen werden. *(supported)* — Evidenz: EVID-2026-02, EVID-2026-04, EVID-2026-06, EVID-2026-08, EVID-2026-10, EVID-2026-12, EVID-2026-14, EVID-2026-16

**Claims:**
- `CLAIM-STOR-001`: Das .b5d-Format ermöglicht verlustfreie Serialisierung und Deserialisierung des vollständigen Netzwerkzustands. *(inconclusive, low)* — Evidenz: EVID-2026-02, EVID-2026-04, EVID-2026-06, EVID-2026-08, EVID-2026-10, EVID-2026-12, EVID-2026-14, EVID-2026-16

**Evidenzen:** EVID-2026-02, EVID-2026-04, EVID-2026-06, EVID-2026-08, EVID-2026-10, EVID-2026-12, EVID-2026-14, EVID-2026-16

---

### RQ-STORAGE-002

**Frage:** Welche Informationen müssen gespeichert werden, damit ein Lauf kausal fortgesetzt werden kann?

**Status:** open
**Relevanz:** Vollständige Zustandsspeicherung für deterministische Reproduktion.

**Hypothesen:**
- `H-STOR-002-A`: Für kausale Fortsetzung eines Laufs müssen Neuron-State, Synapsen-State, Eligibility-Traces, RNG-State und Event-Queue gespeichert werden. *(untested)*

---

### RQ-STORAGE-003

**Frage:** Welche Speicherdichte erreicht das multidimensionale Modell?

**Status:** open
**Relevanz:** Skalierbarkeit des Speicherformats.

**Hypothesen:**
- `H-STOR-003-A`: Die Speicherdichte des .b5d-Formats skaliert sublinear mit der Neuronenzahl. *(untested)*

---

### RQ-STORAGE-004

**Frage:** Wie verhält sich das .b5d-Format bei 5.000, 50.000, 500.000, 5 Mio., 50 Mio. und 312,5 Mio. Neuronen?

**Status:** open
**Relevanz:** Extrapolation der theoretischen Skalierbarkeit.

**Hypothesen:**
- `H-STOR-004-A`: Das .b5d-Format skaliert auf mindestens 50 Millionen Neuronen ohne Leistungseinbruch. *(untested)*

---

## Structural Plasticity

### RQ-STRUCT-001

**Frage:** Führt strukturelle Plastizität (Pruning/Sprouting) zu funktional verbesserten Netzwerken?

**Status:** open
**Relevanz:** Strukturelle Anpassung ist ein mächtiger Mechanismus biologischer Gehirne.

**Hypothesen:**
- `H-STRUCT-001-A`: Strukturelle Plastizität (Pruning/Sprouting) führt zu messbar verbesserter Netzwerkeffizienz. *(untested)*

---

## Temporal Learning

### RQ-TEMP-002

**Frage:** Reagiert Brain-5D auf spike-tragende zeitliche Reihenfolge anders als auf umgekehrte oder simultane Kontrollfolgen?

**Status:** open
**Relevanz:** EXP-GEN-0021 zeigte Temporal-State-Diskrepanzen ohne Spike-Aktivität.

**Hypothesen:**
- `H-TEMP-002-A`: Forward-, Reverse- und Simultanfolgen erzeugen bei gleicher Ereignisanzahl unterscheidbare spike-basierte Antwortsignaturen. *(untested)*

---

## Temporal State

### RQ-TEMP-001

**Frage:** Wie unterscheiden sich FAST-, MEDIUM- und SLOW-Referenzzustände unter identischer Ausführung?

**Status:** open
**Relevanz:** Messung von Persistenz und Zustandsdrift ohne Runtime-Zurückspulen.

**Hypothesen:**
- `H-TEMP-001-A`: Die Temporal-State-Vergleiche unterscheiden sich deterministisch nach FAST-, MEDIUM- und SLOW-Horizont. *(untested)*

---

## Visual Resource Allocation

### RQ-MSBA-E03

**Frage:** Kann sich eine nutzungsabhaengige visuelle ROI/Foveation ohne hart kodierte Zielregion entwickeln?

**Status:** open
**Relevanz:** Trennt adaptive visuelle Ressourcenlenkung von fest programmierten Zentrum- oder Vollbildstrategien.

**Hypothesen:**
- `H-MSBA-E03-A`: Adaptive visuelle ROI-Allokation konzentriert Ressourcen auf aufgabenrelevante Regionen und verbessert Leistung pro Ressourceneinheit gegenueber einer zufaelligen ROI-Kontrolle. *(untested)*

---


> Pruefstatus: RQ/H- und EVID-Statuswerte geben den Registry-Inhalt wieder. Insbesondere historische supports/supported-Eintraege sind keine Bestaetigung einer Freigabe nach den heutigen Clean-Freeze- und Human-Review-Gates. Ein abgeschlossener Lauf ist DATA, nicht automatisch akzeptierte Evidenz.
