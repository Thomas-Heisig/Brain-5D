# Brain-5D Dissertation Map

*Generiert am 2026-08-23*

Diese Karte zeigt, wie die Forschungsergebnisse von Brain-5D in eine
Dissertationsstruktur eingeordnet werden können.

## Kapitel 1 – Theorie und Grundlagen

Einführung in SNN-Theorie, Izhikevich-Modell, deterministische Dynamik

**Forschungsfragen:**
- `RQ-SNN-001`: Kann Brain-5D stabile Spike-Dynamiken über lange Simulationszeiträume erzeugen?... *(open)*
- `RQ-SNN-002`: Kann das eingesetzte Neuronenmodell bei konstantem Input reproduzierbare Spikefo... *(open)*
- `RQ-SNN-003`: Bleibt die Spikefolge bei gleichem Seed, Input und Zustand deterministisch?... *(open)*

**Literatur:**
- `SRC-IZHIKEVICH-2003`: Eugene M. Izhikevich et al. (2003)
- `SRC-GERSTNER-2014`: Wulfram Gerstner et al. (2014)
- `SRC-MAASS-1997`: Wolfgang Maass et al. (1997)

---

## Kapitel 2 – Plastizität und Lernen

STDP, Homeostase, Interaktion, Lernleistung

**Forschungsfragen:**
- `RQ-SNN-004`: Wie verändert STDP die synaptische Gewichtsmatrix?... *(open)*
- `RQ-SNN-005`: Verbessert STDP tatsächlich eine definierte Lernleistung?... *(open)*
- `RQ-STDP-001`: Erzeugt pair-based STDP unter definierten Pre/Post-Zeitabständen eine asymmetris... *(open)*
- `RQ-STDP-002`: Bleiben STDP-getriebene Gewichte unter Dauerstimulation stabil oder oszillieren/... *(open)*
- `RQ-HOM-001`: Kann synaptische Homeostase die Feuerrate in einem SNN stabilisieren?... *(open)*
- `RQ-HOM-002`: Wie interagiert Homeostase mit STDP? Wirken sie synergistisch oder antagonistisc... *(open)*

**Literatur:**
- `SRC-SONG-ABBOTT-2000`: Sen Song et al. (2000)
- `SRC-BI-POO-1998`: Guo-Qiang Bi et al. (1998)
- `SRC-TURRIGIANO-2008`: Gina G. Turrigiano et al. (2008)
- `SRC-HEBB-1949`: Donald O. Hebb et al. (1949)

---

## Kapitel 3 – 5D-Raum und Topologie

Dimensionsablation, Signalpropagation, Modularität, Informationstheorie

**Forschungsfragen:**
- `RQ-5D-001`: Hat die fünfdimensionale Anordnung einen messbaren Effekt auf die Netzwerkdynami... *(open)*
- `RQ-5D-002`: Wie verändert Dimensionalität die Signalpropagation im Netzwerk?... *(open)*
- `RQ-5D-003`: Entsteht in 5D eine andere Modularität als in niedrigeren Dimensionen?... *(open)*
- `RQ-5D-004`: Sind zusätzliche Dimensionen informationstragend oder lediglich zusätzliche Koor... *(open)*

---

## Kapitel 4 – Persistenz und Speicherung

.b5d-Format, verlustfreie Serialisierung, Speicherdichte, Skalierung

**Forschungsfragen:**
- `RQ-STORAGE-001`: Kann ein vollständiger neuronaler Zustand verlustfrei im .b5d-Modell gespeichert... *(open)*
- `RQ-STORAGE-002`: Welche Informationen müssen gespeichert werden, damit ein Lauf kausal fortgesetz... *(open)*
- `RQ-STORAGE-003`: Welche Speicherdichte erreicht das multidimensionale Modell?... *(open)*
- `RQ-STORAGE-004`: Wie verhält sich das .b5d-Format bei 5.000, 50.000, 500.000, 5 Mio., 50 Mio. und... *(open)*

---

## Kapitel 5 – Selbstorganisation

Emergenz, Clusterbildung, Pruning, Sprouting

**Forschungsfragen:**
- `RQ-SELF-001`: Entstehen in Brain-5D spontan funktionale Cluster oder Module?... *(open)*
- `RQ-SELF-002`: Ist die beobachtete Selbstorganistion emergenter Natur oder durch die Architektu... *(open)*
- `RQ-STRUCT-001`: Führt strukturelle Plastizität (Pruning/Sprouting) zu funktional verbesserten Ne... *(open)*

---

## Kapitel 6 – Skalierung

Skalierung von 5k auf Millionen Neuronen

**Forschungsfragen:**
- `RQ-SCALE-001`: Skaliert Brain-5D von 5.000 auf Millionen Neuronen ohne qualitative Dynamikverän... *(open)*

**Literatur:**
- `SRC-MARKRAM-2015`: Henry Markram et al. (2015)

---

## Kapitel 7 – Gedächtnis und Embodiment

Synaptisches Gedächtnis, Sensor-Aktor-Schleife, Language Organ

**Forschungsfragen:**
- `RQ-MEM-001`: Kann Brain-5D Informationen über synaptische Gewichte speichern und zuverlässig ... *(open)*
- `RQ-EMB-001`: Kann Brain-5D in einer Sensor-Aktor-Schleife (Embodiment) sinnvoll agieren?... *(open)*
- `RQ-LLM-001`: Kann ein Language Organ (SNM ↔ LLM) sinnvolle Kommunikation ermöglichen?... *(open)*

---

## Kapitel 8 – Autorenschaft und Epistemologie

Verteilte Autorenschaft, Kontrollverlust, maschinelle Erkenntnis

**Forschungsfragen:**
- `RQ-ETH-001`: Wer ist der Autor von Brain-5D-Erkenntnissen — Mensch, Modell oder System?... *(open)*
- `RQ-ETH-002`: Wo liegt die Kontrolle und Verantwortung bei Brain-5D-Experimenten?... *(open)*
- `RQ-EPIST-001`: Was gilt als Erkenntnis des Systems Brain-5D im Unterschied zur Erkenntnis des F... *(open)*

---
