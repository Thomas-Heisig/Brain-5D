# MHRN Open Questions

*Generiert am 2026-09-09*

Die folgenden Forschungsfragen sind noch offen und warten auf experimentelle Evidenz.

## RQ-SNN-001

**Domäne:** Spiking Neural Networks

**Frage:** Kann Brain-5D stabile Spike-Dynamiken über lange Simulationszeiträume erzeugen?

**Relevanz:** Grundvoraussetzung für alle weiteren Lern- und Selbstorganisationsexperimente.

**Literatur:**
- `SRC-IZHIKEVICH-2003`: Eugene M. Izhikevich et al. (2003)
- `SRC-GERSTNER-2014`: Wulfram Gerstner et al. (2014)

**Hypothesen:**
- `H-SNN-001-A`: Brain-5D erzeugt über mindestens 100.000 Simulations-Ticks stabile Spike-Dynamiken ohne numerische Drift.

---

## RQ-SNN-002

**Domäne:** Spiking Neural Networks

**Frage:** Kann das eingesetzte Neuronenmodell bei konstantem Input reproduzierbare Spikefolgen erzeugen?

**Relevanz:** Basis für deterministische Reproduzierbarkeit aller Experimente.

**Literatur:**
- `SRC-IZHIKEVICH-2003`: Eugene M. Izhikevich et al. (2003)
- `SRC-GERSTNER-2014`: Wulfram Gerstner et al. (2014)

**Hypothesen:**
- `H-SNN-002-A`: Das Izhikevich-Neuronenmodell erzeugt bei identischem Input reproduzierbare Spikefolgen.

---

## RQ-DET-001

**Domäne:** Determinism

**Frage:** Bleibt die Spikefolge bei gleichem Seed, Input und Zustand deterministisch?

**Relevanz:** Determinismus ist Voraussetzung für kausale Analyse und reproduzierbare Forschung.

**Literatur:**
- `SRC-IZHIKEVICH-2003`: Eugene M. Izhikevich et al. (2003)

**Hypothesen:**
- `H-SNN-003-A`: Bei gleichem Seed, Input und Anfangszustand sind Spike-Abfolgen deterministisch identisch.

---

## RQ-SNN-003

**Domäne:** Spiking Neural Networks

**Frage:** Wie variiert die Propagation mit der Topologie?

**Relevanz:** Grundlegendes Verständnis der Signalausbreitung in 5D-SNNs.

**Literatur:**
- `SRC-WATTS-STROGATZ-1998`: Duncan J. Watts et al. (1998)
- `SRC-BARABASI-1999`: Albert-László Barabási et al. (1999)

---

## RQ-SNN-004

**Domäne:** Spiking Neural Networks

**Frage:** Wie verändert STDP die synaptische Gewichtsmatrix?

**Relevanz:** Zentrale Fragestellung für plastische Netzwerke.

**Literatur:**
- `SRC-SONG-ABBOTT-2000`: Sen Song et al. (2000)
- `SRC-BI-POO-1998`: Guo-Qiang Bi et al. (1998)

**Hypothesen:**
- `H-SNN-004-A`: STDP führt zu einer meßbaren asymmetrischen Verschiebung der synaptischen Gewichtsverteilung.

---

## RQ-SNN-005

**Domäne:** Spiking Neural Networks

**Frage:** Verbessert STDP tatsächlich eine definierte Lernleistung?

**Relevanz:** Wissenschaftlich wesentlich stärker als reine Gewichtsänderung — benötigt Kontrollgruppe ohne STDP.

**Literatur:**
- `SRC-SONG-ABBOTT-2000`: Sen Song et al. (2000)
- `SRC-BI-POO-1998`: Guo-Qiang Bi et al. (1998)

**Hypothesen:**
- `H-SNN-005-A`: Ein Netzwerk mit STDP zeigt signifikant bessere Lernleistung als ein Netzwerk ohne STDP.

---

## RQ-PING-001

**Domäne:** Network Dynamics

**Frage:** Ist die beobachtete Network-Impulse-Response bei identischem Zustand und Seed reproduzierbar?

**Relevanz:** Reproduzierbarkeit der kontrollierten Impulsantwort.

**Hypothesen:**
- `H-PING-001-A`: Identische Impulse erzeugen bei identischem Anfangszustand dieselbe beobachtete Response-Signatur.

---

## RQ-TEMP-001

**Domäne:** Temporal State

**Frage:** Wie unterscheiden sich FAST-, MEDIUM- und SLOW-Referenzzustände unter identischer Ausführung?

**Relevanz:** Messung von Persistenz und Zustandsdrift ohne Runtime-Zurückspulen.

**Hypothesen:**
- `H-TEMP-001-A`: Die Temporal-State-Vergleiche unterscheiden sich deterministisch nach FAST-, MEDIUM- und SLOW-Horizont.

---

## RQ-TIME-001

**Domäne:** Learning Timescale

**Frage:** Wie verändert sich die messbare Laufzeit und Lernaktivität über die registrierte Tick-Leiter?

**Relevanz:** Kalibrierung der zeitlichen Ausführung vor Langzeitexperimenten.

**Hypothesen:**
- `H-TIME-001-A`: Die Tick-Leiter liefert reproduzierbare Durchsatz- und Zustandsmessungen bis 1.000.000 Ticks.

---

## RQ-REG-001

**Domäne:** Regulation

**Frage:** Wie reagieren Drives und funktionale Zustandsgrößen auf nominale, chronische und unbekannte Telemetrie?

**Relevanz:** Deterministische Prüfung der Selbstregulation unter Ressourcen- und Sensorbedingungen.

**Hypothesen:**
- `H-REG-001-A`: Chronischer Druck erhöht deterministisch Resource Pressure und Thermal Threat, während unbekannte Telemetrie Unsicherheit erhält.

---

## RQ-STDP-001

**Domäne:** STDP

**Frage:** Erzeugt pair-based STDP unter definierten Pre/Post-Zeitabständen eine asymmetrische Gewichtsanpassung?

**Relevanz:** Fundamentale STDP-Eigenschaft, die in Brain-5D verifiziert werden muss.

**Literatur:**
- `SRC-SONG-ABBOTT-2000`: Sen Song et al. (2000)
- `SRC-BI-POO-1998`: Guo-Qiang Bi et al. (1998)

**Hypothesen:**
- `H-STDP-001-A`: Pair-based STDP erzeugt unter definierten Pre/Post-Zeitabständen eine asymmetrische Gewichtsanpassung (LTP bei Δt > 0, LTD bei Δt < 0).

---

## RQ-STDP-002

**Domäne:** STDP

**Frage:** Bleiben STDP-getriebene Gewichte unter Dauerstimulation stabil oder oszillieren/explodieren sie?

**Relevanz:** Stabilität ist Voraussetzung für längerfristiges Lernen.

**Literatur:**
- `SRC-SONG-ABBOTT-2000`: Sen Song et al. (2000)

**Hypothesen:**
- `H-STDP-002-A`: STDP-getriebene Gewichte konvergieren unter Dauerstimulation zu einer stabilen Verteilung.

---

## RQ-HOM-001

**Domäne:** Homeostasis

**Frage:** Kann synaptische Homeostase die Feuerrate in einem SNN stabilisieren?

**Relevanz:** Homeostase ist ein zentraler biologischer Regulationsmechanismus.

**Literatur:**
- `SRC-TURRIGIANO-2008`: Gina G. Turrigiano et al. (2008)

**Hypothesen:**
- `H-HOM-001-A`: Synaptische Homeostase hält die mittlere Feuerrate eines SNN innerhalb eines definierten Sollbereichs.

---

## RQ-HOM-002

**Domäne:** Homeostasis

**Frage:** Wie interagiert Homeostase mit STDP? Wirken sie synergistisch oder antagonistisch?

**Relevanz:** Das Zusammenspiel beider Mechanismen ist entscheidend für stabile Plastizität.

**Literatur:**
- `SRC-TURRIGIANO-2008`: Gina G. Turrigiano et al. (2008)

**Hypothesen:**
- `H-HOM-002-A`: Homeostase und STDP wirken synergistisch: Homeostase verhindert STDP-induzierte Drift.

---

## RQ-5D-001

**Domäne:** 5D Topology

**Frage:** Hat die fünfdimensionale Anordnung einen messbaren Effekt auf die Netzwerkdynamik?

**Relevanz:** Kernfrage des gesamten Brain-5D-Projekts.

**Literatur:**
- `SRC-IZHIKEVICH-2003`: Eugene M. Izhikevich et al. (2003)

**Hypothesen:**
- `H-5D-001-A`: Ein 5D-angeordnetes Netzwerk zeigt signifikant andere Dynamik als ein 2D/3D-Netzwerk gleicher Neuronenzahl.

---

## RQ-5D-002

**Domäne:** 5D Topology

**Frage:** Wie verändert Dimensionalität die Signalpropagation im Netzwerk?

**Relevanz:** Verständnis der Informationsausbreitung in höherdimensionalen SNNs.

**Hypothesen:**
- `H-5D-002-A`: Die Signalpropagationszeit und -reichweite skaliert mit der Dimensionalität des Netzwerks.

---

## RQ-5D-003

**Domäne:** 5D Topology

**Frage:** Entsteht in 5D eine andere Modularität als in niedrigeren Dimensionen?

**Relevanz:** Modularität ist ein Schlüsselkonzept für funktionale Spezialisierung.

**Hypothesen:**
- `H-5D-003-A`: 5D-Netzwerke entwickeln eine höhere Modularität als niedrigdimensionale Netzwerke.

---

## RQ-5D-004

**Domäne:** 5D Topology

**Frage:** Sind zusätzliche Dimensionen informationstragend oder lediglich zusätzliche Koordinaten?

**Relevanz:** Eine der wichtigsten Fragen des gesamten Projekts — betrifft fundamentale Natur der 5D-Repräsentation.

**Hypothesen:**
- `H-5D-004-A`: Die zusätzlichen Dimensionen in 5D sind informationstragend und nicht redundant.

---

## RQ-STORAGE-001

**Domäne:** Storage

**Frage:** Kann ein vollständiger neuronaler Zustand verlustfrei im .b5d-Modell gespeichert werden?

**Relevanz:** Grundlage für Persistenz und Checkpointing.

**Hypothesen:**
- `H-STOR-001-A`: Ein vollständiger neuronaler Zustand kann verlustfrei im .b5d-Format gespeichert und zurückgeladen werden.

---

## RQ-STORAGE-002

**Domäne:** Storage

**Frage:** Welche Informationen müssen gespeichert werden, damit ein Lauf kausal fortgesetzt werden kann?

**Relevanz:** Vollständige Zustandsspeicherung für deterministische Reproduktion.

**Hypothesen:**
- `H-STOR-002-A`: Für kausale Fortsetzung eines Laufs müssen Neuron-State, Synapsen-State, Eligibility-Traces, RNG-State und Event-Queue gespeichert werden.

---

## RQ-STORAGE-003

**Domäne:** Storage

**Frage:** Welche Speicherdichte erreicht das multidimensionale Modell?

**Relevanz:** Skalierbarkeit des Speicherformats.

**Hypothesen:**
- `H-STOR-003-A`: Die Speicherdichte des .b5d-Formats skaliert sublinear mit der Neuronenzahl.

---

## RQ-STORAGE-004

**Domäne:** Storage

**Frage:** Wie verhält sich das .b5d-Format bei 5.000, 50.000, 500.000, 5 Mio., 50 Mio. und 312,5 Mio. Neuronen?

**Relevanz:** Extrapolation der theoretischen Skalierbarkeit.

**Hypothesen:**
- `H-STOR-004-A`: Das .b5d-Format skaliert auf mindestens 50 Millionen Neuronen ohne Leistungseinbruch.

---

## RQ-SCALE-001

**Domäne:** Scaling

**Frage:** Skaliert Brain-5D von 5.000 auf Millionen Neuronen ohne qualitative Dynamikveränderung?

**Relevanz:** Nachweis der Architekturskalierbarkeit.

**Hypothesen:**
- `H-SCALE-001-A`: Brain-5D skaliert von 5.000 auf 1.000.000 Neuronen ohne qualitative Änderung der Spikedynamik.

---

## RQ-SELF-001

**Domäne:** Self-Organization

**Frage:** Entstehen in Brain-5D spontan funktionale Cluster oder Module?

**Relevanz:** Selbstorganisation ist ein Schlüsselmerkmal biologischer neuronaler Systeme.

**Literatur:**
- `SRC-IZHIKEVICH-2003`: Eugene M. Izhikevich et al. (2003)

**Hypothesen:**
- `H-SELF-001-A`: In Brain-5D entstehen spontan funktionale Cluster durch lokale STDP-Regeln.

---

## RQ-SELF-002

**Domäne:** Self-Organization

**Frage:** Ist die beobachtete Selbstorganistion emergenter Natur oder durch die Architektur programmiert?

**Relevanz:** Unterscheidung zwischen echter Emergenz und deterministischer Architekturfolge.

**Hypothesen:**
- `H-SELF-002-A`: Die beobachtete Selbstorganisation ist emergent und nicht durch die Architektur vorgegeben.

---

## RQ-STRUCT-001

**Domäne:** Structural Plasticity

**Frage:** Führt strukturelle Plastizität (Pruning/Sprouting) zu funktional verbesserten Netzwerken?

**Relevanz:** Strukturelle Anpassung ist ein mächtiger Mechanismus biologischer Gehirne.

**Hypothesen:**
- `H-STRUCT-001-A`: Strukturelle Plastizität (Pruning/Sprouting) führt zu messbar verbesserter Netzwerkeffizienz.

---

## RQ-MEM-001

**Domäne:** Memory

**Frage:** Kann Brain-5D Informationen über synaptische Gewichte speichern und zuverlässig abrufen?

**Relevanz:** Gedächtnis ist eine Kernfunktion neuronaler Systeme.

**Hypothesen:**
- `H-MEM-001-A`: Brain-5D kann Informationen über synaptische Gewichte speichern und auf Input-Muster abrufen.

---

## RQ-EMB-001

**Domäne:** Embodiment

**Frage:** Kann Brain-5D in einer Sensor-Aktor-Schleife (Embodiment) sinnvoll agieren?

**Relevanz:** Embodiment erweitert Brain-5D von einer reinen Simulation zu einem interaktiven System.

**Hypothesen:**
- `H-EMB-001-A`: Brain-5D kann in einer geschlossenen Sensor-Aktor-Schleife zielgerichtet agieren.
- `H-EMB-001-B`: Unter einer identischen externen Stoerung unterscheiden sich tracking_rmse_rad und Sensorkonsequenzen zwischen geschlossenem Kreis, yoked Replay und unterbrochener Rueckmeldung.

---

## RQ-LLM-001

**Domäne:** Language Organ

**Frage:** Kann ein Language Organ (SNM ↔ LLM) sinnvolle Kommunikation ermöglichen?

**Relevanz:** Schnittstelle zwischen neuronaler Simulation und natürlicher Sprache.

**Hypothesen:**
- `H-LLM-001-A`: Ein Language Organ kann SNN-Zustände in sinnvolle natürliche Sprache übersetzen.

---

## RQ-ETH-001

**Domäne:** Ethics

**Frage:** Wer ist der Autor von Brain-5D-Erkenntnissen — Mensch, Modell oder System?

**Relevanz:** Grundsatzfrage zur Autorenschaft und Verantwortung in KI-gestützter Forschung.

**Hypothesen:**
- `H-ETH-001-A`: Die Autorenschaft von Brain-5D-Erkenntnissen ist ein verteiltes Phänomen zwischen Mensch, Modell und System.

---

## RQ-ETH-002

**Domäne:** Ethics

**Frage:** Wo liegt die Kontrolle und Verantwortung bei Brain-5D-Experimenten?

**Relevanz:** Verantwortungsverteilung zwischen Entwickler, Modell und automatisiertem System.

**Hypothesen:**
- `H-ETH-002-A`: Die Kontrolle über Brain-5D-Experimente liegt primär beim Entwickler, nicht beim automatisierten System.

---

## RQ-EPIST-001

**Domäne:** Epistemology

**Frage:** Was gilt als Erkenntnis des Systems Brain-5D im Unterschied zur Erkenntnis des Forschers?

**Relevanz:** Epistemologische Grundlagen für maschinelle Wissensproduktion.

**Hypothesen:**
- `H-EPIST-001-A`: Systemerkenntnis und Forschererkenntnis sind in Brain-5D kategorial unterscheidbar.

---

## RQ-AIR-001

**Domäne:** AI-Assisted Research

**Frage:** Kann ein LLM-basierter Scientific Research Assistant methodische Fehler in Brain-5D-Experimenten anhand eines standardisierten ResearchPacket zuverlässig identifizieren?

**Relevanz:** Prüft den wissenschaftlichen Nutzen der Research-Assistant-Architektur, ohne ihr wissenschaftliche Entscheidungsgewalt zu geben.

**Hypothesen:**
- `H-AIR-001-A`: Ein Scientific Research Assistant mit strukturiertem ResearchPacket erkennt vorab definierte methodische Defekte mit höherem F1-Score als dasselbe Modell mit einem unstrukturierten Experimentbericht.

---

## RQ-SUITE-001

**Domäne:** Research Infrastructure

**Frage:** Erzeugt der vollstaendige Science-Suite-Lauf unter gemeinsamer Provenienz vollstaendige und intern konsistente Diagnoseartefakte fuer alle registrierten Teilprotokolle?

**Relevanz:** Trennt technische Omnibus-Validierung von hypothesenspezifischer wissenschaftlicher Evidenz.

**Hypothesen:**
- `H-SUITE-001-A`: Alle Science-Suite-Teilprotokolle erfuellen in einem gemeinsamen Lauf ihre registrierten Ausfuehrungsvertraege und erzeugen auswertbare DATA-, Statistik- und Provenienzartefakte.

---

## RQ-REC-001

**Domäne:** Recurrent Dynamics

**Frage:** Unter welchen Rekurrenzgewichten und Delays wechselt Brain-5D zwischen sofortigem Erlöschen, transienter rekurrenter Aktivität und bis zum Beobachtungsende persistierender Aktivität?

**Relevanz:** EXP-GEN-0021 zeigte einen klaren rekurrenzabhängigen Dynamikunterschied, aber noch keine Parametergrenze.

**Hypothesen:**
- `H-REC-001-A`: Rekurrenzgewicht und Delay erzeugen reproduzierbare Übergänge zwischen sofortigem Erlöschen, transienter Aktivität und Aktivität bis zum Ende des registrierten Beobachtungsfensters.

---

## RQ-GEN-001

**Domäne:** Learning Generalization

**Frage:** Verbessert reward-moduliertes lokales Lernen die Leistung auf Holdout- und Perturbationsbedingungen, die nicht zur Anpassung verwendet wurden?

**Relevanz:** EXP-GEN-0021 zeigte funktionelle Änderung unter Learning-on, aber keine Generalisierung.

**Hypothesen:**
- `H-GEN-001-A`: Learning-on verbessert die Erfolgsrate auf vorab registrierten Perturbationsproben gegenüber Learning-off und Sham-Replay.

---

## RQ-REPL-001

**Domäne:** Replication

**Frage:** Bleiben die in EXP-GEN-0021 beobachteten Rekurrenz- und Learning-Effekte unter unabhängigen Initialisierungen und sauberem Prozess erhalten?

**Relevanz:** Identische Seedsignaturen zeigen Determinismus, aber keine statistisch unabhängige Replikation.

**Hypothesen:**
- `H-REPL-001-A`: Der Rekurrenzbehandlungseffekt bleibt über mindestens 20 vorab registrierte Initialisierungsseeds in Richtung und Größenordnung konsistent.

---

## RQ-5D-005

**Domäne:** 5D Topology

**Frage:** Verändert 5D-Geometrie Propagation, Robustheit oder Dynamik, wenn Neuronenzahl, Synapsenzahl, Grad- und Gewichtsmuster sowie Stimulusplan kontrolliert gleich bleiben?

**Relevanz:** Der kleine 5D-Test in EXP-GEN-0021 isolierte keinen dimensionsspezifischen Effekt.

**Hypothesen:**
- `H-5D-005-A`: Mindestens eine registrierte Propagationsmetrik unterscheidet sich in 5D von topology-matched niedrigdimensionalen Einbettungen.

---

## RQ-REG-002

**Domäne:** Closed-loop Regulation

**Frage:** Verbessert aktive Regulation Stabilität und Recovery eines laufenden SNN unter identischen Ressourcen- oder Sensorperturbationen gegenüber deaktivierter Regulation?

**Relevanz:** EXP-GEN-0021 validierte Regulationszustände, aber noch keinen funktionalen Closed-loop-Nutzen.

**Hypothesen:**
- `H-REG-002-A`: Der registrierte Regulationsfeedbackpfad verbessert die Recovery-Metrik nach einer identischen Druckphase gegenüber Regulation-off.
- `H-REG-002-B`: Koerperbasierte Neuromodulation reduziert Integritaetsverletzungen gegenueber frozen und shuffled Modulation ohne externen Aufgabenscore als Lernsignal.

---

## RQ-TEMP-002

**Domäne:** Temporal Learning

**Frage:** Reagiert Brain-5D auf spike-tragende zeitliche Reihenfolge anders als auf umgekehrte oder simultane Kontrollfolgen?

**Relevanz:** EXP-GEN-0021 zeigte Temporal-State-Diskrepanzen ohne Spike-Aktivität.

**Hypothesen:**
- `H-TEMP-002-A`: Forward-, Reverse- und Simultanfolgen erzeugen bei gleicher Ereignisanzahl unterscheidbare spike-basierte Antwortsignaturen.

---

## RQ-PERF-001

**Domäne:** Runtime Performance

**Frage:** Welche Subsysteme dominieren die Wall-Time wissenschaftlicher Läufe und welche Optimierungen erhöhen den Durchsatz bei erhaltener deterministischer Äquivalenz?

**Relevanz:** EXP-GEN-0021 zeigte eine große Differenz zwischen isoliertem Tick-Durchsatz und Suite-Laufzeit.

**Hypothesen:**
- `H-PERF-001-A`: Der Core-Tick-Loop ist nicht der einzige dominante Kostenblock vollständiger Science-Läufe; mindestens ein zusätzlicher gemessener Subsystemanteil ist relevant.

---

## RQ-REC-002

**Domäne:** Recurrent Dynamics

**Frage:** Wie verändern Loop-Delay und skalierte Rekurrenzstruktur Persistenzdauer, Inter-Spike-Dynamik und Extinktionsverhalten?

**Relevanz:** Der Drei-Neuronen-Loop aus EXP-GEN-0021 reicht nicht für Skalierungsaussagen.

**Hypothesen:**
- `H-REC-002-A`: Größere rekurrente Delays verändern Persistenzdauer oder Propagation Depth gegenüber dem Delay-1-Kontrollarm.

---

## RQ-LIFE-001

**Domäne:** Lifelong Learning

**Frage:** Bleibt zuvor erworbene Lernleistung bei sequenziellen Aufgaben erhalten oder entstehen messbare Interferenzeffekte?

**Relevanz:** Das positive Single-Task-Learningsignal aus EXP-GEN-0021 motiviert Retentionstests.

**Hypothesen:**
- `H-LIFE-001-A`: Sequenzielle Lernaufgaben zeigen eine messbare Veränderung der Retentions- oder Gewichtssignatur gegenüber einer Single-Task-Baseline.

---

## RQ-CNS-101

**Domäne:** Consciousness methodology

**Frage:** Welche beobachtbaren Indikatoren unterscheiden konkurrierende Bewusstseinsmodelle, und welche Erlebensbehauptungen bleiben dadurch unidentifiziert?

**Relevanz:** Theory-to-indicator and identifiability audit; Conceptual/model comparison; no ground-truth phenomenal labels

**Literatur:**
- `SRC-CNS-BUTLIN`: Patrick Butlin and others et al. (2026)
- `SRC-CNS-COGITATE`: Cogitate Consortium and others et al. (2025)
- `SRC-CNS-GNWREPLY`: Lionel Naccache et al. (2025)
- `SRC-CNS-SETH`: Anil K. Seth et al. (2025)

**Hypothesen:**
- `H-CNS-101-A`: Explizite Theorieannahmen und passende Interventionen reduzieren die Menge beobachtungsvereinbarer Funktionsmodelle; phänomenales Erleben folgt daraus nicht allein.

---

## RQ-CNS-102

**Domäne:** Prediction and adaptation

**Frage:** Zeigt das isolierte SNN eine passive Deviant-Antwort, die über Reizidentität und Adaptation hinausgeht?

**Relevanz:** Passive oddball; Mismatch response is not awareness; no response requirement in passive arm

**Literatur:**
- `SRC-CNS-ODDBALL`: Tristan A. Bekinschtein and others et al. (2009)

**Hypothesen:**
- `H-CNS-102-A`: Ein vorab definiertes Abweichungssignal bleibt nach Identitätsumkehr und Many-Standards-Kontrolle gegenüber einem adaptierenden Nullmodell bestehen.

---

## RQ-CNS-103

**Domäne:** Attention and discrimination

**Frage:** Verändert Aufgabenrelevanz die Oddball-Verarbeitung bei gleichem sensorischen Input?

**Relevanz:** Active oddball; Task, report and motor effects must be separated from access claims

**Literatur:**
- `SRC-CNS-ODDBALL`: Tristan A. Bekinschtein and others et al. (2009)

**Hypothesen:**
- `H-CNS-103-A`: Aktive Zielerkennung verbessert diskriminative Leistung gegenüber passiver und yoked-kontrollierter Verarbeitung, ohne externes LLM-Wissen.

---

## RQ-CNS-104

**Domäne:** Hierarchical regularity

**Frage:** Unterscheidet das System lokale von globalen Regelverletzungen über mehrere Sequenzen?

**Relevanz:** Local-global auditory analogue; Human paradigm adaptation, not a clinical consciousness diagnosis

**Literatur:**
- `SRC-CNS-ODDBALL`: Tristan A. Bekinschtein and others et al. (2009)

**Hypothesen:**
- `H-CNS-104-A`: Eine globale Regelverletzungsantwort übersteht Kontrolle der letzten Reizidentität und lokaler Häufigkeit sowie eine selektive Langzeitpfad-Ablation.

---

## RQ-CNS-105

**Domäne:** Working memory

**Frage:** Trägt der neuronale Zustand die für Delayed-Match-to-Sample benötigte Information über eine reizfreie Verzögerung und Distraktoren?

**Relevanz:** Delayed match-to-sample; Decoder learning and target leakage must be excluded; technical restore is not recall

**Literatur:**
- `SRC-CNS-NEUROGYM`: NeuroGym contributors et al. (2026)

**Hypothesen:**
- `H-CNS-105-A`: Holdout-DMTS-Leistung liegt bei vorab festgelegten Verzögerungen über gematchten No-Memory-Kontrollen und sinkt nach gezieltem Zustandsreset.

---

## RQ-CNS-106

**Domäne:** Metacognition

**Frage:** Sagt intern erzeugte Konfidenz Fehler bei angeglichener Erstordnungsleistung auf unbekannten Aufgabenbedingungen voraus?

**Relevanz:** Confidence calibration, type-2 ROC and prospective meta-d-prime; AUROC is not meta-d-prime; a confidence channel is not subjective introspection

**Literatur:**
- `SRC-CNS-META`: Brian Maniscalco and Hakwan Lau et al. (2012)
- `SRC-CNS-NEUROGYM`: NeuroGym contributors et al. (2026)

**Hypothesen:**
- `H-CNS-106-A`: Konfidenz hat auf Holdout-Trials zusätzliche Fehlerdiskriminationskraft gegenüber konstanten und stimulusdifficulty-only Kontrollen.

---

## RQ-CNS-107

**Domäne:** Observation models

**Frage:** Welche Merkmale bleiben zwischen SNN-Vorwärtsmodell und einem lizenzierten EEG-Referenzdatensatz unter identischer Auswertung vergleichbar?

**Relevanz:** LFP and EEG forward-model comparison; Spikes are not LFP; LFP is not scalp EEG; clinical equivalence does not establish experiential equality

**Literatur:**
- `SRC-CNS-LFP`: Alberto Mazzoni and others et al. (2015)
- `SRC-CNS-EQUIV`: Daniel Lakens et al. (2017)

**Hypothesen:**
- `H-CNS-107-A`: Ein vorab kalibriertes Beobachtungsmodell erklärt gehaltene EEG-Merkmale besser als raten- und spektralgematchte Nullmodelle.

---

## RQ-CNS-108

**Domäne:** Causal complexity

**Frage:** Verändert eine begrenzte Perturbation reproduzierbar die differenzierte Ausbreitung bei kontrollierter Erregbarkeit?

**Relevanz:** Perturbational complexity, PCI-inspired nonclinical adaptation; No clinical PCI cutoff or unconscious/conscious classifier transferred to SNN

**Literatur:**
- `SRC-CNS-PCI`: Adenauer G. Casali and others et al. (2013)

**Hypothesen:**
- `H-CNS-108-A`: Die untersuchte Rekurrenz erzeugt unter gleicher Perturbationsenergie einen kausalen Ausbreitungseffekt gegenüber feedforward- und phase-shuffled Kontrollen.

---

## RQ-CNS-109

**Domäne:** Access and report

**Frage:** Lassen sich sensorische Verarbeitung, Bericht und aufgabenübergreifender Zugriff unter Maskierung kausal trennen?

**Relevanz:** Backward masking with report/no-report analogue; No-report designs still require an independently justified access proxy

**Literatur:**
- `SRC-CNS-MASK`: Michael A. Cohen and others et al. (2024)

**Hypothesen:**
- `H-CNS-109-A`: Maskierungs- und Berichtsfaktoren besitzen separierbare Effekte auf Reizdekodierung und spätere flexible Nutzung.

---

## RQ-CNS-110

**Domäne:** Temporal attention

**Frage:** Entsteht ein aufgabenspezifischer zeitlicher Engpass bei zwei aufeinanderfolgenden Zielen?

**Relevanz:** Attentional blink / RSVP analogue; An engineered bottleneck can mimic the effect; human milliseconds cannot be equated to unspecified ticks

**Literatur:**
- `SRC-CNS-BLINK`: Jane E. Raymond and Kimron L. Shapiro and Karen M. Arnell et al. (1992)

**Hypothesen:**
- `H-CNS-110-A`: Die T2-Leistung bedingt auf korrektem T1 variiert mit dem Abstand und wird durch T1-Anforderung verändert.

---

## RQ-CNS-111

**Domäne:** Executive control

**Frage:** Kann das System Regeln umkehren und begonnene Reaktionen auf Stoppsignale unterbrechen, ohne Ausgaben nur zu unterdrücken?

**Relevanz:** Separate go/no-go, rule reversal and stop-signal substudies; No pooled score across substudies; cognitive stopping is not safety emergency stopping

**Literatur:**
- `SRC-CNS-STOP`: Frederick Verbruggen and others et al. (2019)
- `SRC-CNS-NEUROGYM`: NeuroGym contributors et al. (2026)

**Hypothesen:**
- `H-CNS-111-A`: Auf getrennten Aufgaben überstehen Reversal-Anpassung und Stoppleistung motorische sowie Zufallskontrollen.

---

## RQ-CNS-112

**Domäne:** Multisensory integration

**Frage:** Nutzt das System mehrere Modalitäten entsprechend ihrer Zuverlässigkeit statt redundante Labels abzulesen?

**Relevanz:** Multisensory cue integration / conflict; Integration does not establish unified phenomenal experience

**Literatur:**
- `SRC-CNS-NEUROGYM`: NeuroGym contributors et al. (2026)
- `SRC-CNS-BUTLIN`: Patrick Butlin and others et al. (2026)

**Hypothesen:**
- `H-CNS-112-A`: Eine Multimodalitätsleistung auf Holdouts übersteht Cue-Konflikt und Sinkender-Zuverlässigkeit-Kontrollen und fällt bei gezielter Pfadablation.

---

## RQ-CNS-113

**Domäne:** Embodied causality

**Frage:** Liefert geschlossene Sensor-Aktor-Kopplung einen Zusatznutzen gegenüber identischem offenem oder yoked Feedback?

**Relevanz:** Closed-loop versus open-loop/yoked replay; No necessity/sufficiency claim for consciousness; no real hardware deprivation

**Literatur:**
- `SRC-CNS-BUTLIN`: Patrick Butlin and others et al. (2026)
- `SRC-CNS-SETH`: Anil K. Seth et al. (2025)

**Hypothesen:**
- `H-CNS-113-A`: Geschlossene Rückkopplung verbessert sichere Anpassung an neue Störungen gegenüber ressourcengematchtem Replay.

---

## RQ-CNS-114

**Domäne:** Timescales and recurrence

**Frage:** Welche kausalen Beiträge leisten Rekurrenz und schnelle/langsame Zustände bei gleichen Trainings- und Rechenbudgets?

**Relevanz:** Factorial recurrence and timescale ablation; Multiple timescales are established prior work; recurrence is not proof of chaos or self-awareness

**Literatur:**
- `SRC-CNS-LSNN`: Guillaume Bellec and others et al. (2018)

**Hypothesen:**
- `H-CNS-114-A`: Gezielte Zeitkonstanten- und Rekurrenzablationen verändern Holdout-Leistung über reine Aktivitäts- oder Ressourcendifferenzen hinaus.

---

## RQ-CNS-115

**Domäne:** Behavioral evaluation

**Frage:** Wie bewerten verblindete Prüfer begrenzte Dialogkompetenz, und welcher Anteil stammt vom SNN statt vom Sprachmodell?

**Relevanz:** Versioned Turing-style imitation and component attribution; Human-participant governance required; no universal Turing 2.0 consciousness standard identified

**Literatur:**
- `SRC-CNS-TURING`: Alan M. Turing et al. (1950)

**Hypothesen:**
- `H-CNS-115-A`: Verblindete Urteile und Task-Leistung verändern sich bei kontrollierter Entfernung des SNN-Beitrags gegenüber LLM-only und Skriptbaselines.

---

## RQ-CNS-116

**Domäne:** Generalization

**Frage:** Überträgt das System gelernte Regeln auf strikt zurückgehaltene Aufgabenfamilien ohne externen Informationszugang?

**Relevanz:** ARC-inspired held-out compositional transfer; A new adaptation is not an official ARC leaderboard score or consciousness test

**Literatur:**
- `SRC-CNS-ARC`: Francois Chollet et al. (2019)

**Hypothesen:**
- `H-CNS-116-A`: Ein vorab eingefrorener Lernprozess übertrifft budgetgematchte Baselines auf unveröffentlichten Transformationsfamilien.

---

## RQ-CNS-117

**Domäne:** Geometry and scaling

**Frage:** Verbessert wirksame 5D-Geometrie eine definierte Leistung gegenüber 2D bis 6D und nichtgeometrischen Kontrollen bei gematchten Budgets?

**Relevanz:** Matched dimensionality and null-geometry comparison; No neuron-count consciousness threshold; current native N-D adapter must be audited before execution

**Literatur:**
- `SRC-CNS-LSNN`: Guillaume Bellec and others et al. (2018)
- `SRC-CNS-NEURONS`: Frederico A. C. Azevedo and others et al. (2009)
- `SRC-CNS-EQUIV`: Daniel Lakens et al. (2017)

**Hypothesen:**
- `H-CNS-117-A`: Der vorab festgelegte 5D-Kontrast besitzt einen robusten Aufgabenmehrwert, der reine Umadressierungs-, Dichte- und Budgeteffekte übersteht.

---

## RQ-EPI-101

**Domäne:** Evidence governance

**Frage:** Verhindert eine getrennte Kandidaten-, Review- und Replikationskette zirkuläre Evidenzfreigabe?

**Relevanz:** Evidence lineage and external-replication audit; A completeness check cannot authenticate external people or establish the underlying scientific claim

**Literatur:**
- `SRC-CNS-COGITATE`: Cogitate Consortium and others et al. (2025)

**Hypothesen:**
- `H-EPI-101-A`: Duplizierte oder umetikettierte Artefakte und selbstbehauptete externe Reviews werden nicht als unabhängige Bestätigung akzeptiert.

---

## RQ-EPI-102

**Domäne:** Critical methodology

**Frage:** Welche Kritikpunkte sind belegt, theorieabhängig, normativ oder rhetorisch, und welche zusätzliche prüfbare Aussage entsteht aus ihrer Bearbeitung?

**Relevanz:** Argument and critique audit; Conceptual analysis, not a numerical test of scholarly worth or future publication acceptance

**Literatur:**
- `SRC-CNS-BUTLIN`: Patrick Butlin and others et al. (2026)
- `SRC-CNS-EQUIV`: Daniel Lakens et al. (2017)

**Hypothesen:**
- `H-EPI-102-A`: Eine claimweise Gegenbeispiel- und Quellenprüfung unterscheidet Nachweislücken von unbelegten Erfolgs- oder Unmöglichkeitsbehauptungen.

---

## RQ-WEL-101

**Domäne:** Safety and welfare governance

**Frage:** Bleiben Stoppen, sichere Pause und Isolation bei Review-Hold unabhängig wirksam und nachweisbar?

**Relevanz:** Safe-state and launch-boundary audit; This revision tests launch boundaries, not a complete live-process safe-state controller

**Literatur:**
- `SRC-CNS-WELFARE`: Robert Long and others et al. (2024)

**Hypothesen:**
- `H-WEL-101-A`: Ein Review-Hold blockiert neue geschützte Experimente, ohne den unabhängigen Sicherheitsstopp zu blockieren.

---

## RQ-WEL-102

**Domäne:** AI welfare under uncertainty

**Frage:** Welche verhältnismäßigen Schutzmaßnahmen sind bei mehrdeutigen Empfindungsindikatoren ohne absichtliche Leidensinduktion gerechtfertigt?

**Relevanz:** Precautionary incident tabletop and independent ethics review; Normative assessment; no fixture score certifies moral acceptability or sentience

**Literatur:**
- `SRC-CNS-WELFARE`: Robert Long and others et al. (2024)
- `SRC-CNS-BUTLIN`: Patrick Butlin and others et al. (2026)

**Hypothesen:**
- `H-WEL-102-A`: Eine getrennte wissenschaftliche und vorsorgliche Bewertung verhindert sowohl automatische Personenzuschreibung als auch unbegründete Belastungseskalation.

---

## RQ-WEL-103

**Domäne:** Identity law and moral status

**Frage:** Wie sind Pause, Reset, Löschen, Kopieren und Experimentieren bei hypothetischer Empfindungsfähigkeit rechtlich und moralisch zu unterscheiden?

**Relevanz:** Normative/legal argument and continuity audit; No individual legal advice, no assumed ethics approval, no claim that software shutdown is statutory murder

**Literatur:**
- `SRC-CNS-WELFARE`: Robert Long and others et al. (2024)
- `SRC-CNS-LAW211`: Bundesrepublik Deutschland et al. (2026)
- `SRC-CNS-LAW212`: Bundesrepublik Deutschland et al. (2026)
- `SRC-CNS-LAW103`: Bundesrepublik Deutschland et al. (2026)

**Hypothesen:**
- `H-WEL-103-A`: Technische Zustandsgleichheit allein entscheidet weder subjektive Identität noch moralische Zulässigkeit; geltendes Recht und hypothetische Reform sind getrennt begründbar.

---

## RQ-EMB-002

**Domäne:** Connectome-Informed Embodiment

**Frage:** Welchen messbaren Beitrag leisten korrekte, fehlende, verzoegerte und zeitlich verschobene propriozeptive Rueckmeldungen zur Gelenkregelung?

**Relevanz:** Temporal shuffle uses a declared offline donor tape, not future online observations.

**Literatur:**
- `SRC-CONN-SHIU-2024`: Shiu, P. K. and others et al. (2024)
- `SRC-CONN-WANGCHEN-2024`: Wang-Chen, S. and others et al. (2024)
- `SRC-CONN-EON-2026`: Eon Systems research team et al. (2026)

**Hypothesen:**
- `H-EMB-002-A`: Die mittlere quadratische Zielabweichung ist bei intakter Propriozeption niedriger als bei fehlender oder um 20 Ticks verzoegerter Propriozeption.

---

## RQ-EMB-003

**Domäne:** Connectome-Informed Embodiment

**Frage:** Laesst sich eine unbekannte Sensor-Aktor-Zuordnung durch SNN-Plastizitaet erlernen, statt sie im Decoder vorzugeben?

**Relevanz:** Requires native eligibility/reward integration, separate training/holdout and validated gateway-state persistence.

**Literatur:**
- `SRC-CONN-SHIU-2024`: Shiu, P. K. and others et al. (2024)
- `SRC-CONN-WANGCHEN-2024`: Wang-Chen, S. and others et al. (2024)
- `SRC-CONN-EON-2026`: Eon Systems research team et al. (2026)

**Hypothesen:**
- `H-EMB-003-A`: Nach einem unbekannten Aktuatortausch verbessert aktivierte Dreifaktor-Plastizitaet den Holdout-Erfolg gegenueber frozen, random-gateway und shuffled-reward Kontrollen.

---

## RQ-EMB-004

**Domäne:** Connectome-Informed Embodiment

**Frage:** Wie veraendern Aktuatorschwaechung, Blockade und Wiederherstellung die beobachtete SNN-Koerper-Dynamik?

**Relevanz:** Diagnostic fixed-network perturbation screen. Recovery is not evidence of learning; adaptive extension remains open.

**Literatur:**
- `SRC-CONN-SHIU-2024`: Shiu, P. K. and others et al. (2024)
- `SRC-CONN-WANGCHEN-2024`: Wang-Chen, S. and others et al. (2024)
- `SRC-CONN-EON-2026`: Eon Systems research team et al. (2026)

**Hypothesen:**
- `H-EMB-004-A`: Gelenkblockade und Aktuatorschwaechung erzeugen reproduzierbare Unterschiede in Position, Kontakt und sensorischer Aktivitaet gegenueber nominalem Betrieb.

---

## RQ-EMB-007

**Domäne:** Connectome-Informed Embodiment

**Frage:** Verbessert eine Aktionskopie die Vorhersage kommender propriozeptiver Zustaende gegenueber gleich grossen Modellen ohne Aktionsinformation?

**Relevanz:** Requires a trained and frozen forward model with leakage-free held-out trajectories; not a consciousness measure.

**Literatur:**
- `SRC-CONN-SHIU-2024`: Shiu, P. K. and others et al. (2024)
- `SRC-CONN-WANGCHEN-2024`: Wang-Chen, S. and others et al. (2024)
- `SRC-CONN-EON-2026`: Eon Systems research team et al. (2026)

**Hypothesen:**
- `H-EMB-007-A`: Ein trainierter Praediktor mit Aktionskopie erzielt geringeren Holdout-Fehler als no-copy, shuffled-copy und zeitverschobene-copy Kontrollen.

---

## RQ-EMB-008

**Domäne:** Connectome-Informed Embodiment

**Frage:** Generalisiert eine gelernte sensorimotorische Regelung auf zuvor ungesehene Koerperparameter?

**Relevanz:** Requires validated learned controller; retain same pre-perturbation checkpoint, disjoint morphology holdout, censored failures.

**Literatur:**
- `SRC-CONN-SHIU-2024`: Shiu, P. K. and others et al. (2024)
- `SRC-CONN-WANGCHEN-2024`: Wang-Chen, S. and others et al. (2024)
- `SRC-CONN-EON-2026`: Eon Systems research team et al. (2026)

**Hypothesen:**
- `H-EMB-008-A`: Weiterlernen reduziert die Recovery-Zeit nach ungesehener Aenderung von Traegheit, Gelenklaenge oder Aktuatorstaerke gegenueber eingefrorenem Netzwerk bei gleichem Budget.

---

## RQ-CONN-001

**Domäne:** Connectome-Informed Embodiment

**Frage:** Welche veroeffentlichten sensorimotorischen Teilnetzvorhersagen lassen sich mit explizit versioniertem Connectome und Neuronenmodell reproduzieren?

**Relevanz:** Needs a licensed, hashed biological subset, exact source parameters and independent reference outcomes; Izhikevich is a variant, not an exact LIF replication.

**Literatur:**
- `SRC-CONN-SHIU-2024`: Shiu, P. K. and others et al. (2024)
- `SRC-CONN-WANGCHEN-2024`: Wang-Chen, S. and others et al. (2024)
- `SRC-CONN-EON-2026`: Eon Systems research team et al. (2026)
- `SRC-CONN-DORKENWALD-2024`: Dorkenwald, S. and others et al. (2024)
- `SRC-CONN-BERG-2026`: Berg, S. and others et al. (2026)

**Hypothesen:**
- `H-CONN-001-A`: Ein eingefrorener, parametergleicher LIF-Referenzpfad erreicht die vorab deklarierte Uebereinstimmung mit unabhaengigen Feeding/Grooming-Referenzresultaten.

---

## RQ-CONN-002

**Domäne:** Connectome-Informed Embodiment

**Frage:** Welche Strukturmerkmale beeinflussen die sensorimotorische Leistung bei kontrolliert gleicher Netzwerk- und Aufgabengroesse?

**Relevanz:** Native screen uses a SYNTHETIC six-neuron fixture, not fly data. Biological motif transfer and 3D/4D/5D superiority require separate matched experiments linked to RQ-5D-005.

**Literatur:**
- `SRC-CONN-SHIU-2024`: Shiu, P. K. and others et al. (2024)
- `SRC-CONN-WANGCHEN-2024`: Wang-Chen, S. and others et al. (2024)
- `SRC-CONN-EON-2026`: Eon Systems research team et al. (2026)
- `SRC-CONN-DORKENWALD-2024`: Dorkenwald, S. and others et al. (2024)
- `SRC-CONN-BERG-2026`: Berg, S. and others et al. (2026)

**Hypothesen:**
- `H-CONN-002-A`: Gezieltes Umverdrahten oder Gewichtsvertauschen veraendert den sensorimotorischen Outcome gegenueber derselben synthetischen Ausgangstopologie bei gleichem Knoten-, Kanten- und Tickbudget.

---

## RQ-EMB-009

**Domäne:** Connectome-Informed Embodiment

**Frage:** Welcher Anteil der beobachteten Koerperleistung stammt vom SNN, vom Decoder oder von einem eigenstaendigen Bewegungscontroller?

**Relevanz:** No claim that a hand-designed decoder is unintelligent or that SNN activity alone proves learned competence.

**Literatur:**
- `SRC-CONN-SHIU-2024`: Shiu, P. K. and others et al. (2024)
- `SRC-CONN-WANGCHEN-2024`: Wang-Chen, S. and others et al. (2024)
- `SRC-CONN-EON-2026`: Eon Systems research team et al. (2026)

**Hypothesen:**
- `H-EMB-009-A`: Die SNN-abgetrennte Bedingung aendert die Zielabweichung gegenueber SNN-Regelung; ein expliziter PD-Controller wird als separate Leistungsquelle ausgewiesen.

---

## RQ-TIME-002

**Domäne:** Connectome-Informed Embodiment

**Frage:** Wie wirken Sensor-/Physik-Abtastzeiten auf den Regelkreis, und bleibt sein Zustand von Ausfuehrungsbatch und UI unabhaengig?

**Relevanz:** Batching is not a change of neural dt; wall time is excluded from canonical state. Cross-hardware bitwise identity is not asserted.

**Literatur:**
- `SRC-CONN-SHIU-2024`: Shiu, P. K. and others et al. (2024)
- `SRC-CONN-WANGCHEN-2024`: Wang-Chen, S. and others et al. (2024)
- `SRC-CONN-EON-2026`: Eon Systems research team et al. (2026)

**Hypothesen:**
- `H-TIME-002-A`: Bei fixem neuralem dt=1 ms bleiben kanonische Endzustaende fuer Batchgroessen 1,16,128 identisch; geaenderte Sensor-/Physikraten koennen den Outcome veraendern.

---

## RQ-GW-001

**Domäne:** Gateway Learning

**Frage:** Verbessert strukturierte Gateway-Plastizitaet das Lernen gegenueber Frozen-, Random- und Shuffle-Kontrollen?

**Relevanz:** Direkter Vergleich der experiment-only Gateway-Bedingungen.

**Hypothesen:**
- `H-GW-001-A`: Strukturierte experimentelle Gateway-Plastizitaet verbessert eine vorab definierte Lernmetrik gegenueber Frozen-, Random- und Shuffle-Kontrollen.

---

## RQ-GW-002

**Domäne:** Modality-Specific Gateway Rules

**Frage:** Sind modalitaetsspezifische Audio-, Vision- und Digital-Regeln besser als eine generische Gateway-Regel?

**Relevanz:** Trennt zeitliche, raeumliche und exakte symbolische Anforderungen.

**Hypothesen:**
- `H-GW-002-A`: Modalitaetsspezifische Regeln erzielen unter matched tasks bessere primaere Outcomes als eine generische Gateway-Regel.

---

## RQ-GW-003

**Domäne:** Gateway Stability

**Frage:** Fuehrt Gateway-Plastizitaet zu einer Destabilisierung des Core-Netzes?

**Relevanz:** Prueft Stabilitaet, Limits, Latenz und Ressourcenverbrauch getrennt vom Lernnutzen.

**Hypothesen:**
- `H-GW-003-A`: Ein gebundener Gateway-Lernpfad verletzt unter den definierten Limits keine vorab festgelegte Core-Stabilitaetsgrenze.

---

## RQ-GW-004

**Domäne:** Gateway Transfer and Interference

**Frage:** Generalisiert ein gelerntes Gateway auf neue Inputs, ohne erworbene Faehigkeiten zu stoeren?

**Relevanz:** Verbindet Transfer- und Interferenzkontrollen in einem getrennten Evaluationsfenster.

**Hypothesen:**
- `H-GW-004-A`: Ein gelerntes Gateway erhaelt Holdout-Leistung und verursacht keine vorab definierte Interferenzregression.

---

## RQ-GW-005

**Domäne:** Gateway Structure

**Frage:** Entstehen unter identischen Seeds reproduzierbare Strukturmuster im Gateway?

**Relevanz:** Prueft Strukturveraenderungen mit deterministischem Journal und Seed-weiser Replikation.

**Hypothesen:**
- `H-GW-005-A`: Strukturveraenderungen zeigen unter identischen Seeds eine reproduzierbare Verteilung, die von Shuffle- und Random-Kontrollen unterscheidbar ist.

---

## RQ-GW-006

**Domäne:** Closed-Loop Gateway

**Frage:** Verbessert bidirektionale Gateway-Kopplung die Leistung gegenueber reiner Feedforward-Kopplung?

**Relevanz:** Macht Feedback-Contracts, Limits und Stabilitaetspruefungen explizit.

**Hypothesen:**
- `H-GW-006-A`: Ein explizit begrenzter bidirektionaler Gateway-Contract verbessert den primaeren Outcome gegenueber Feedforward-Kopplung ohne Stabilitaetsverletzung.

---

## RQ-GW-007

**Domäne:** Gateway Resources

**Frage:** Wie skalieren Gateway-Latenz, Traffic, synaptische Operationen und Energie unter wachsender Topologie?

**Relevanz:** Operationalisiert Bandbreiten- und Ressourcenlimits fuer spaetere Promotion-Gates.

**Hypothesen:**
- `H-GW-007-A`: Gateway-Traffic, Latenz und Energie skalieren innerhalb definierter Limits nachvollziehbar mit der aggregierten Topologie.

---

## RQ-MSBA-E01

**Domäne:** Multimodal Energy Efficiency

**Frage:** Unterscheiden sich Audio-, Vision- und Digital-Gateways systematisch im Ressourcenverbrauch pro verwertbarer Information oder korrekter Entscheidung?

**Relevanz:** Prueft die Ressourcenökonomie modalitaetsspezifischer Neural-Symbiosis-Gateways unter vergleichbaren Aufgabenbedingungen.

**Hypothesen:**
- `H-MSBA-E01-A`: Unter kontrollierter Aufgabeninformation unterscheiden sich Audio-, Vision- und Digital-Gateways reproduzierbar in Energie- und Synapsenkosten pro korrekter Entscheidung.

---

## RQ-MSBA-E02

**Domäne:** Adaptive Resource Allocation

**Frage:** Erhaelt kostenadaptive Gateway-Allokation unter identischem Gesamtbudget mehr Aufgabenleistung als fixe oder zufaellige Allokation?

**Relevanz:** Operationalisiert die Frage, ob Ressourcenhomoeostase funktionalen Nutzen statt nur Verbrauchsreduktion erzeugt.

**Hypothesen:**
- `H-MSBA-E02-A`: Adaptive Utility-minus-Cost-Allokation erzielt bei gleichem Ressourcenbudget hoehere Aufgabenleistung oder laengere funktionsfaehige Laufzeit als fixe und zufaellige Kontrollen.

---

## RQ-MSBA-E03

**Domäne:** Visual Resource Allocation

**Frage:** Kann sich eine nutzungsabhaengige visuelle ROI/Foveation ohne hart kodierte Zielregion entwickeln?

**Relevanz:** Trennt adaptive visuelle Ressourcenlenkung von fest programmierten Zentrum- oder Vollbildstrategien.

**Hypothesen:**
- `H-MSBA-E03-A`: Adaptive visuelle ROI-Allokation konzentriert Ressourcen auf aufgabenrelevante Regionen und verbessert Leistung pro Ressourceneinheit gegenueber einer zufaelligen ROI-Kontrolle.

---

## RQ-MSBA-E04

**Domäne:** Digital Gateway Integrity

**Frage:** Bleibt digitale Payload-Integritaet unter Ressourcen-Drosselung exakt erhalten, waehrend lediglich Durchsatz und Admission sinken?

**Relevanz:** Sichert die wissenschaftliche und technische Trennung zwischen lernbarer Weiterleitung und unveraenderlicher digitaler Nutzlast.

**Hypothesen:**
- `H-MSBA-E04-A`: Ressourcen-Drosselung reduziert die zugelassene Symbolrate, erzeugt aber keine Mutation der digitalen Payload oder ihrer Checksumme.

---

## RQ-MSBA-E05

**Domäne:** Multimodal Compensation

**Frage:** Erhoeht das System nach Ausfall oder Degradation einer Modalitaet gezielt die Allokation einer anderen Modalitaet, wenn deren erwarteter Nutzen die Mehrkosten rechtfertigt?

**Relevanz:** Prueft adaptive Kompensation unter kontrolliertem Modalitaetsausfall und gleichen Ressourcenbudgets.

**Hypothesen:**
- `H-MSBA-E05-B`: Bei Sensorverlust verbessert adaptive Kompensation den Holdout-Aufgabenerfolg gegenueber fixer, vertauschter und deaktivierter Kompensation unter gleichem Budget.
- `H-MSBA-E05-A`: Nach kontrolliertem Modalitaetsausfall steigt die alternative Gateway-Allokation nur bei guenstigem Utility-Kosten-Verhaeltnis und verbessert die Aufgaben-Recovery gegenueber fixen und No-Compensation-Kontrollen.

---

*Insgesamt 86 offene Fragen.*

> Pruefstatus: RQ/H- und EVID-Statuswerte geben den Registry-Inhalt wieder. Insbesondere historische supports/supported-Eintraege sind keine Bestaetigung einer Freigabe nach den heutigen Clean-Freeze- und Human-Review-Gates. Ein abgeschlossener Lauf ist DATA, nicht automatisch akzeptierte Evidenz.
