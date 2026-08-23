# Brain-5D Open Questions

*Generiert am 2026-08-23*

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

*Insgesamt 28 offene Fragen.*