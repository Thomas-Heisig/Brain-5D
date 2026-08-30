# Brain-5D: Eine hybride, räumlich organisierte Spiking-Architektur für selbstorganisierende und verkörperte kognitive Systeme

## Architektur, methodische Grundlagen, experimentelle Hypothesen und Forschungsroadmap

**Projekt:** Brain-5D
**Repository:** `Thomas-Heisig/Brain-5D`
**Entwicklungsstatus:** experimentelles Forschungsframework / Alpha-Phase
**Dokumenttyp:** Technisches und wissenschaftliches Architekturpapier

---

# Abstract

Brain-5D ist ein experimentelles Forschungsframework zur Untersuchung selbstorganisierender kognitiver Systeme auf Grundlage zeitkontinuierlicher beziehungsweise diskret simulierter neuronaler Dynamik, lokaler Plastizität, struktureller Reorganisation und multimodaler Sensor-Aktor-Kopplung.

Die zentrale Architektur besteht aus einem **Spiking Neural Network (SNN)**, dessen Neuronen in einem logisch fünfdimensionalen Koordinatenraum organisiert werden. Dieser Raum dient nicht lediglich der Visualisierung, sondern soll als strukturelle Grundlage für Lokalität, Konnektivität, funktionale Regionen, Wachstumsprozesse und langfristig die Bildung interner Repräsentationen dienen.

Im Gegensatz zu Architekturen, bei denen ein Large Language Model (LLM) die zentrale kognitive Instanz bildet, behandelt Brain-5D ein Sprachmodell als **optionales externes Language Organ**. Dieses besitzt keine unmittelbaren Schreibrechte auf synaptische Gewichte, strukturelle Plastizität oder den zentralen Simulationszyklus. Die Kopplung zwischen SNN und symbolischen Systemen erfolgt über definierte Datenverträge, insbesondere `StimulusPlan` und `SignalFrame`.

Damit wird eine experimentell wichtige Trennung eingeführt zwischen:

1. neuronaler Zustandsdynamik,
2. lokaler und struktureller Plastizität,
3. sensorischer Stimulation,
4. semantischer Interpretation,
5. externem Wissenszugriff und
6. sprachlicher Darstellung.

Das langfristige Forschungsziel besteht nicht darin, ein Sprachmodell durch ein SNN lediglich zu ergänzen. Untersucht werden soll vielmehr, in welchem Umfang ein dynamisches, plastisches und verkörpertes neuronales Substrat eigenständig persistente interne Zustände, Assoziationen, adaptive Verhaltensmuster und gegebenenfalls abstraktere Repräsentationen ausbilden kann.

Entsprechend werden Behauptungen über „Verstehen“, „Bewusstsein“, „Reasoning“ oder „echte Intelligenz“ ausdrücklich **nicht als bereits erreichte Eigenschaften des Systems vorausgesetzt**. Sie sind – soweit überhaupt operationalisierbar – Gegenstand zukünftiger Experimente.

---

# 1. Forschungsfrage und Motivation

## 1.1 Ausgangsproblem

Moderne Large Language Models besitzen außerordentlich leistungsfähige Fähigkeiten zur Verarbeitung symbolischer Sequenzen. Ihre interne Berechnung unterscheidet sich jedoch fundamental von biologischen neuronalen Systemen.

Insbesondere sind klassische LLMs typischerweise:

* token- und sequenzorientiert,
* überwiegend durch Offline-Training geprägt,
* nicht intrinsisch sensorisch verkörpert,
* nicht kontinuierlich durch lokale synaptische Plastizität lernend,
* nicht primär ereignisgetrieben,
* nicht auf neuronale Entwicklung oder strukturelles Wachstum ausgelegt.

Spiking Neural Networks besitzen dagegen explizite zeitliche Zustände und diskrete Spike-Ereignisse. Sie erlauben die Untersuchung lokaler Plastizitätsmechanismen, rekurrenter Dynamik, Synchronisation, Oszillation und eventbasierter Informationsverarbeitung.

SNNs sind zugleich keineswegs automatisch intelligent. Ein biologisch inspiriertes Neuronenmodell, STDP oder Neurogenese erzeugen für sich genommen weder Sprache noch semantische Repräsentationen noch allgemeines Reasoning.

Brain-5D setzt genau an dieser offenen Lücke an.

Die grundlegende Forschungsfrage lautet:

> **Kann aus einem räumlich strukturierten, zeitabhängigen, lokal plastischen und verkörperten Spiking-System durch kontinuierliche Interaktion eine stabile interne Repräsentations- und Verhaltensstruktur entstehen, ohne dass deren semantischer Inhalt direkt durch ein LLM in die synaptischen Zustände geschrieben wird?**

---

# 2. Wissenschaftliche Positionierung

Brain-5D liegt an der Schnittstelle mehrerer Forschungsrichtungen:

* Computational Neuroscience,
* Spiking Neural Networks,
* Neuromorphic Computing,
* Structural Plasticity,
* Continual Learning,
* Reinforcement Learning,
* Neuro-Symbolic AI,
* Embodied Intelligence,
* dynamische Systeme,
* adaptive Graphen,
* persistente neuronale Simulation,
* multimodale Agentensysteme.

Der Begriff **neural-symbolisch** wird dabei funktional verwendet.

Die neuronale Seite besteht aus Spike-Dynamik, Netzwerkzuständen und plastischen Verbindungen.

Die symbolische Seite umfasst Sprache, strukturierte Wissensobjekte, Provenienz und externe Schnittstellen.

Die symbolische Komponente soll jedoch nicht unkontrolliert den neuronalen Zustand verändern können.

---

# 3. Forschungsstatus versus Zielarchitektur

Für die wissenschaftliche Bewertung von Brain-5D ist eine klare Unterscheidung zwingend erforderlich.

## 3.1 Implementierter Zustand

Hierzu gehören ausschließlich Funktionen, die:

* im Repository implementiert,
* durch Tests überprüfbar,
* reproduzierbar ausführbar und
* durch Messdaten belegbar

sind.

## 3.2 Engineering-Roadmap

Hierunter fallen bereits spezifizierte, aber noch nicht vollständig implementierte Komponenten.

## 3.3 Forschungshypothesen

Hierunter fallen erwartete Eigenschaften wie:

* selbstorganisierte Repräsentationsbildung,
* emergente funktionale Regionen,
* langfristiges assoziatives Gedächtnis,
* interne Symbolbildung,
* multimodale Begriffsbildung,
* transferierbare interne Repräsentationen.

Diese Eigenschaften dürfen nicht mit implementierter Funktionalität gleichgesetzt werden.

Diese Dreiteilung sollte zukünftig auch in Repository, Dokumentation und Veröffentlichungen konsequent verwendet werden.

---

# 4. Das Brain-5D-Systemmodell

## 4.1 Grundstruktur

Die Architektur kann abstrahiert dargestellt werden als

[
\mathcal{B}
===========

(\mathcal{N},\mathcal{S},\mathcal{P},\mathcal{H},
\mathcal{E},\mathcal{A},\mathcal{M})
]

mit

* (\mathcal{N}): Neuronenmenge,
* (\mathcal{S}): Synapsen beziehungsweise gerichtete Kanten,
* (\mathcal{P}): Plastizitätsoperatoren,
* (\mathcal{H}): homöostatische Regelung,
* (\mathcal{E}): sensorische Eingänge,
* (\mathcal{A}): Aktoren/Ausgänge,
* (\mathcal{M}): persistenter Systemzustand.

Der Gesamtzustand zum Zeitpunkt (t) sei:

[
X(t)=
{
X_N(t),
X_S(t),
X_H(t),
X_E(t),
X_M(t)
}
]

Die Entwicklung ergibt sich abstrakt aus:

[
X(t+\Delta t)
=============

F(X(t),I(t),R(t),\Theta)
]

mit:

* (I(t)): sensorischem Input,
* (R(t)): optionalem Reward beziehungsweise Modulationssignal,
* (\Theta): globalen Simulationsparametern.

Entscheidend ist:

> Das LLM ist kein Bestandteil von (F), der beliebig den internen neuronalen Zustand verändern darf.

Es kann Daten für (I(t)) beziehungsweise semantische Interpretationen erzeugen, muss dabei jedoch definierte Schnittstellen passieren.

---

# 5. Der fünfdimensionale neuronale Raum

## 5.1 Formale Definition

Jedes Neuron (n_i) besitzt eine Position

[
p_i=(x_i,y_i,z_i,a_i,b_i)
]

in einem fünfdimensionalen diskreten oder kontinuierlichen Raum.

Für einen diskreten Hyperkubus mit Kantenlänge (L) ergibt sich:

[
N=L^5.
]

Für

[
L=50
]

folgt:

[
N=50^5=312,500,000.
]

Diese Zahl stellt eine theoretische Zielkapazität des vollständigen 5D-Raumes dar und nicht notwendigerweise die Anzahl gleichzeitig materialisierter Simulationsobjekte.

Ein Proof-of-Concept mit

[
L=10
]

besitzt dagegen:

[
N=10^5=100,000
]

potenzielle Positionen.

---

## 5.2 Bedeutung der fünf Dimensionen

Die zusätzlichen Dimensionen dürfen wissenschaftlich nicht lediglich als „weitere räumliche Achsen“ bezeichnet werden, sofern keine physikalische Interpretation existiert.

Brain-5D behandelt sie daher als **logische beziehungsweise funktionale Dimensionen**.

Eine mögliche Interpretation lautet:

[
(x,y,z)
]

für räumliche oder topologische Lokalität und

[
(a,b)
]

für funktionale, modale, entwicklungsbezogene oder assoziative Lokalität.

Wichtig ist, diese Semantik nicht dauerhaft fest einzuprogrammieren.

Eine langfristige Forschungsfrage lautet vielmehr, ob die zusätzlichen Dimensionen durch Lern- und Wachstumsprozesse funktionale Bedeutung erhalten können.

---

# 6. Metrik und Konnektivität im 5D-Raum

Eine zentrale bisher häufig unterschätzte Frage lautet:

> Wann sind zwei Neuronen in fünf Dimensionen „nah“?

Für zwei Positionen

[
p_i=(x_i,y_i,z_i,a_i,b_i)
]

und

[
p_j=(x_j,y_j,z_j,a_j,b_j)
]

kann eine gewichtete euklidische Distanz definiert werden:

[
d_{ij}
======

\sqrt{
\lambda_x(x_i-x_j)^2+
\lambda_y(y_i-y_j)^2+
\lambda_z(z_i-z_j)^2+
\lambda_a(a_i-a_j)^2+
\lambda_b(b_i-b_j)^2
}.
]

Die Koeffizienten (\lambda_k) definieren die Bedeutung der jeweiligen Dimension.

Damit kann eine distanzabhängige Verbindungswahrscheinlichkeit formuliert werden:

[
P(i\rightarrow j)
=================

P_0
\exp\left(
-\frac{d_{ij}}{\sigma}
\right).
]

Zusätzlich können Aktivitätskorrelation, Zelltyp und Entwicklungszustand berücksichtigt werden:

[
P_{ij}
======

f(
d_{ij},
C_{ij},
T_i,
T_j,
A_i,
A_j
).
]

Damit entsteht kein vollständig verbundener Hypergraph, sondern ein **sparsamer, dynamischer Graph innerhalb eines fünfdimensionalen Koordinatenraums**.

Diese Sparsität ist für die Skalierbarkeit entscheidend.

---

# 7. Neuronales Dynamikmodell

Brain-5D verwendet im derzeitigen Entwurf das Izhikevich-Modell als rechnerisch effiziente Näherung unterschiedlicher Spike-Dynamiken.

Die Gleichungen lauten:

[
\frac{dv}{dt}
=============

0.04v^2+5v+140-u+I
]

und

[
\frac{du}{dt}
=============

a(bv-u).
]

Bei

[
v\geq 30,\mathrm{mV}
]

erfolgt der Reset:

[
v\leftarrow c
]

[
u\leftarrow u+d.
]

Dabei bezeichnet:

* (v): Membranpotential,
* (u): Recovery-Variable,
* (I): Gesamteingang,
* (a,b,c,d): zelltypspezifische Parameter.

Das Modell stellt ausdrücklich **keine vollständige biophysikalische Simulation eines realen Neurons** dar.

Sein Vorteil besteht vielmehr darin, unterschiedliche Spike- und Burst-Regime mit relativ geringem numerischem Aufwand abzubilden.

---

# 8. Neuronentypen und inhibitorische Dynamik

Für ein stabiles rekurrentes Netzwerk reicht die Definition verschiedener Spike-Profile allein nicht aus.

Brain-5D benötigt explizite Unterscheidungen zwischen:

* exzitatorischen Neuronen,
* inhibitorischen Neuronen,
* sensorischen Neuronen,
* Projektionsneuronen,
* Modulationsknoten beziehungsweise funktionalen Steuerpopulationen.

Eine Synapse erhält entsprechend ein Vorzeichen beziehungsweise einen Typ:

[
w_{ij}>0
]

für exzitatorische und

[
w_{ij}<0
]

für inhibitorische Wirkung.

Das Verhältnis von Erregung und Hemmung bildet einen wesentlichen Untersuchungsparameter.

Zu messen sind beispielsweise:

[
E/I
===

\frac{\sum |w_{exc}|}{\sum |w_{inh}|}
]

sowie:

* mittlere Populationsrate,
* Burst-Häufigkeit,
* Synchronisationsgrad,
* Anteil stiller Neuronen,
* Anteil dauerhaft hochaktiver Neuronen,
* Netzwerk-Lyapunov-artige Stabilitätsindikatoren,
* Oszillationsspektrum.

---

# 9. Zeitmodell

Brain-5D besitzt mindestens drei voneinander zu unterscheidende Zeitskalen.

## 9.1 Neuronale Zeit

[
t_n
]

bezeichnet die Integrationsschritte des SNN.

Typischerweise entspricht ein Schritt beispielsweise einer simulierten Millisekunde.

## 9.2 Plastizitätszeit

[
t_p
]

beschreibt langsamere Prozesse:

* STDP,
* Homeostase,
* Gewichtsnormierung,
* Pruning,
* Wachstum.

## 9.3 Kognitive beziehungsweise externe Zeit

[
t_c
]

bezeichnet Prozesse wie:

* Language-Organ-Aufruf,
* Wissensaufnahme,
* Sensorfusion,
* Aktionsplanung,
* Monitoring.

Damit gilt typischerweise:

[
t_n \ll t_p \ll t_c.
]

Diese explizite Trennung verhindert, dass langsame LLM-Inferenz die neuronale Simulation synchron blockiert.

---

# 10. Synaptische Plastizität

## 10.1 STDP

Für

[
\Delta t=t_{post}-t_{pre}
]

wird die Gewichtsänderung beschrieben durch:

[
\Delta w=
\begin{cases}
A_+e^{-\Delta t/\tau_+}, & \Delta t>0\
-A_-e^{\Delta t/\tau_-}, & \Delta t<0.
\end{cases}
]

Die Gewichte müssen begrenzt werden:

[
w_{min}\leq w_{ij}\leq w_{max}.
]

Ohne solche Grenzen können lokale Hebb-Regeln zu instabilen positiven Rückkopplungen führen.

---

# 11. Reward-modulierte Plastizität

Für verkörpertes Lernen reicht reines STDP wahrscheinlich nicht aus.

Brain-5D sollte deshalb eine **Three-Factor-Learning-Rule** als zentrale Erweiterung untersuchen.

Dabei entsteht zunächst ein Eligibility Trace:

[
e_{ij}(t)
]

aus prä- und postsynaptischer Aktivität.

Eine tatsächliche Gewichtsänderung erfolgt erst in Verbindung mit einem Modulations- beziehungsweise Rewardsignal:

[
\Delta w_{ij}
=============

\eta,R(t),e_{ij}(t).
]

Damit werden drei Faktoren kombiniert:

1. präsynaptische Aktivität,
2. postsynaptische Aktivität,
3. globales beziehungsweise regionales Modulationssignal.

Diese Architektur ist für verzögerte Belohnungen wesentlich geeigneter als unmittelbares STDP allein.

---

# 12. Homöostatische Plastizität

Die mittlere Feuerrate eines Neurons sei

[
\bar r_i(t).
]

Für eine Zielrate (r_i^*) kann beispielsweise die Erregbarkeit angepasst werden:

[
\theta_i(t+\Delta t)
====================

\theta_i(t)
+
\eta_h
(
\bar r_i-r_i^*
).
]

Alternativ können synaptische Gewichte skaliert werden.

Ziel ist nicht eine identische Aktivität aller Neuronen, sondern die Vermeidung zweier degenerierter Zustände:

[
r_i\rightarrow 0
]

für große Netzwerkbereiche beziehungsweise

[
r_i\rightarrow r_{max}
]

für dauerhaft überaktive Populationen.

---

# 13. Strukturelle Plastizität

Brain-5D unterscheidet zwischen:

* **funktionaler Plastizität**: Änderung vorhandener Gewichte,
* **struktureller Plastizität**: Änderung des Graphen selbst.

Eine neue Synapse kann entstehen, wenn beispielsweise:

[
C_{ij}>C_{min}
]

und gleichzeitig

[
d_{ij}<d_{max}
]

sowie ein Ressourcenbudget verfügbar ist.

Pruning kann dagegen ausgelöst werden, wenn:

[
|w_{ij}|<w_{prune}
]

über einen Zeitraum

[
T>T_{grace}
]

bestehen bleibt.

Damit sollen kurzfristige Schwankungen nicht sofort strukturelle Änderungen verursachen.

---

# 14. Neurogenese

Von synaptischer Neurogenese muss die Erzeugung neuer **Neuronen** unterschieden werden.

Neue Neuronen sollten nicht allein aufgrund hoher Aktivität erzeugt werden.

Ein Growth-Score kann beispielsweise definiert werden als:

[
G_r=
\alpha O_r+
\beta E_r+
\gamma D_r-
\delta C_r
]

mit:

* (O_r): Überlastung einer Region,
* (E_r): wiederkehrender Lernfehler,
* (D_r): Diversitätsbedarf,
* (C_r): Ressourcenverbrauch.

Nur wenn

[
G_r>G_{threshold}
]

und ein globales Budget vorhanden ist, darf Wachstum erfolgen.

Dies reduziert instabile Zyklen aus:

[
\text{Wachstum}
\rightarrow
\text{Pruning}
\rightarrow
\text{Wachstum}.
]

---

# 15. Ressourcen- und Energiemodell

Unbegrenztes Wachstum wäre sowohl biologisch als auch rechnerisch unplausibel.

Brain-5D benötigt deshalb ein explizites Ressourcenmodell.

Eine abstrakte Kostenfunktion lautet:

[
C(t)
====

c_nN(t)
+
c_sS(t)
+
c_pP(t)
+
c_aA(t)
]

mit:

* (N(t)): Neuronen,
* (S(t)): Synapsen,
* (P(t)): Spikes pro Zeiteinheit,
* (A(t)): strukturelle Änderungen.

Das System kann dann unter einer Bedingung

[
C(t)\leq C_{max}
]

operieren.

Damit wird Wachstum zu einem Optimierungsproblem und nicht zu einer unbeschränkten Expansion.

---

# 16. Der Signal Interpretation Layer

Das LLM erhält ausdrücklich **keine ungefilterten Spike-Arrays**.

Stattdessen berechnet eine deterministische Transformationsschicht:

[
S:
\text{SpikeEvents}
\rightarrow
\text{SignalFrame}.
]

Ein möglicher Vertrag lautet:

```python
@dataclass(frozen=True, slots=True)
class SignalFrame:
    tick_from: int
    tick_to: int
    neuron_ids: tuple[int, ...]
    population_rate_hz: float
    spike_count: int
    burst_index: float
    synchrony: float
    mean_energy: float
    mean_threshold_adaptation: float
    active_regions: tuple[RegionActivity, ...]
```

Der `SignalFrame` stellt eine **Messung**, keine Bedeutung dar.

Das ist wissenschaftlich entscheidend.

Ein hoher Synchronisationswert bedeutet zunächst nur:

> Eine Population zeigte innerhalb eines definierten Zeitfensters erhöhte zeitliche Koordination.

Er bedeutet nicht automatisch:

> Das Netzwerk denkt an Paris.

Diese semantische Zuordnung muss experimentell gelernt oder validiert werden.

---

# 17. Erweiterte Signalmerkmale

Für spätere Versionen sollten zusätzlich untersucht werden:

* Inter-Spike-Interval-Verteilungen,
* Fano-Faktor,
* Population Sparsity,
* Burst Duration,
* Burst Propagation,
* Phase Locking,
* Cross-Correlation,
* Spike-Train-Distanzen,
* regionale Entropie,
* funktionale Konnektivität,
* Aktivitätsfluss zwischen Regionen,
* metastabile Zustände,
* wiederkehrende Aktivitätsmotive.

Ein erweiterter Frame könnte damit abstrakt beschrieben werden als:

[
F_t=
(
r,
b,
s,
H,
C,
E,
R,
\Phi
)
]

mit Rate (r), Burststruktur (b), Synchronität (s), Entropie (H), Konnektivität (C), Energie (E), Regionen (R) und temporalen Motiven (\Phi).

---

# 18. Das Language Organ

## 18.1 Grundprinzip

Das Language Organ ist:

* optional,
* austauschbar,
* fehlertolerant,
* asynchron,
* nicht Eigentümer des Runtime Loops.

Die Beziehung lautet:

[
\text{LLM}\neq\text{Brain-5D-Kern}.
]

Das LLM ist ein Adapter zwischen symbolischen und subsymbolischen Darstellungen.

---

# 19. Sicherheits- und Kausalitätsgrenzen

Folgende Architekturregeln sollten als formale Invarianten behandelt werden:

1. Kein direkter LLM-Zugriff auf `synapse.weight`.
2. Kein direkter Aufruf struktureller Plastizitätsoperatoren.
3. Kein eigenständiger Aufruf von `network.step()`.
4. Keine Ausführung beliebigen vom LLM erzeugten Codes.
5. Kein Webinhalt darf unmittelbar neuronale Gewichte setzen.
6. LLM-Aussagen werden nicht automatisch als Fakten klassifiziert.
7. Timeout oder Absturz des LLM darf den neuronalen Runtime-Loop nicht stoppen.
8. Jeder externe Einfluss muss einem definierten Eingabekanal zugeordnet werden.
9. Alle zustandsverändernden Operationen müssen protokollierbar sein.
10. LLM-Backends müssen durch ein Null-Backend ersetzbar sein.

Diese Regeln ermöglichen Ablations- und Kontrollexperimente.

---

# 20. Semantic Encoder und StimulusPlan

Text darf nicht unmittelbar als synaptischer Zustand geschrieben werden.

Stattdessen gilt:

[
\text{Text}
\rightarrow
\text{Semantic Representation}
\rightarrow
\text{StimulusPlan}
\rightarrow
\text{Spike Input}.
]

Ein `StimulusPlan` sollte mindestens definieren:

* Zielregion,
* Startzeit,
* Dauer,
* Intensität,
* Frequenz,
* räumliche Verteilung,
* zeitliches Muster,
* Modalität,
* Herkunft,
* Stimulus-ID.

Damit kann derselbe Stimulus reproduzierbar wiederholt werden.

---

# 21. Semantic Decoder

Die Gegenrichtung lautet:

[
\text{SpikeEvents}
\rightarrow
\text{SignalFrame}
\rightarrow
\text{Decoder}
\rightarrow
\text{symbolische Hypothese}.
]

Wichtig ist der Begriff **Hypothese**.

Die Decoder-Ausgabe sollte mit:

* Confidence,
* Decoder-Version,
* zugrunde liegendem SignalFrame,
* Zeitpunkt,
* Modell-ID

gespeichert werden.

So kann später festgestellt werden, ob sich lediglich der Decoder verbessert hat oder tatsächlich das SNN.

---

# 22. Knowledge Intake Engine

Externe Wissensaufnahme wird vom Language Organ getrennt.

Die Pipeline lautet:

[
\text{Source}
\rightarrow
\text{SourceRecord}
\rightarrow
\text{KnowledgeItem}
\rightarrow
\text{LearningStimulus}
\rightarrow
\text{SNN}.
]

Ein `KnowledgeItem` benötigt mindestens:

```text
knowledge_id
content
source_id
retrieved_at
content_hash
source_type
trust_state
validation_state
parser_version
language
learning_session
```

Damit wird extern bereitgestellte Information von intern verändertem Netzwerkzustand unterscheidbar.

---

# 23. Provenienz

Brain-5D sollte eine durchgehende Provenienzrelation unterstützen:

[
Source
\rightarrow
KnowledgeItem
\rightarrow
Stimulus
\rightarrow
Episode
\rightarrow
NetworkState
\rightarrow
SignalFrame
\rightarrow
Interpretation
\rightarrow
Response.
]

Eine Antwort muss dadurch rückwirkend analysierbar sein.

Das ist besonders wichtig, wenn externe Wissensquellen beteiligt sind.

---

# 24. Lernen versus Retrieval

Die zentrale experimentelle Unterscheidung lautet:

[
\text{Retrieval}
\neq
\text{Learning}.
]

Dass ein System eine Information korrekt ausgibt, beweist noch nicht, dass diese im SNN gespeichert wurde.

Ein valides Lernexperiment benötigt mindestens:

### Phase A – Baseline

Frage stellen, bevor die Information gelernt wurde.

### Phase B – Exposition

Information als kontrollierten Lernstimulus zuführen.

### Phase C – Konsolidierung

SNN ohne weiteren Informationsabruf weiterlaufen lassen.

### Phase D – Isolation

* Netzwerkzustand erhalten,
* LLM-Kontext löschen,
* Retrieval Cache löschen,
* Netzwerkzugriff deaktivieren.

### Phase E – Recall

Semantisch gleiche oder variierte Frage erneut stellen.

### Phase F – Kontrolle

Vergleich mit:

* ungeübtem Netzwerk,
* eingefrorener Plastizität,
* zufälligem Stimulus,
* Null-Language-Backend,
* zerstörtem beziehungsweise permutiertem relevanten Netzwerkzustand.

Erst daraus lässt sich eine belastbare Aussage über neuronale Speicherung ableiten.

---

# 25. Gedächtnisdefinition

„Memory“ muss operationalisiert werden.

Für Brain-5D sollte Gedächtnis mindestens drei Bedingungen erfüllen:

### Retention

Eine durch Lernen erzeugte Zustandsänderung bleibt über Zeit erhalten.

### Recall

Ein geeigneter Cue reaktiviert eine unterscheidbare Netzwerkantwort.

### Specificity

Die Antwort tritt für passende Cues stärker auf als für Kontrollstimuli.

Formal:

[
M=
f(Retention,Recall,Specificity).
]

Damit ist nicht jede persistente Gewichtsänderung automatisch ein funktionales Gedächtnis.

---

# 26. Continual Learning

Ein langfristig laufendes Brain-5D muss zusätzlich untersuchen:

* catastrophic forgetting,
* interference,
* stability-plasticity dilemma,
* Konsolidierung,
* Rekonsolidierung,
* synaptische Konkurrenz.

Ein Retention-Maß könnte lauten:

[
R(\Delta t)
===========

\frac{Q(t+\Delta t)}{Q(t_0)}
]

wobei (Q) die Recall-Qualität bezeichnet.

Gemessen werden sollten beispielsweise:

[
R(10^3),
R(10^4),
R(10^5),
R(10^6)
]

Ticks.

---

# 27. Verkörperung

Brain-5D verwendet Embodiment nicht synonym mit Robotik.

Verkörperung bedeutet zunächst eine geschlossene Schleife:

[
Environment
\rightarrow
Sensor
\rightarrow
SNN
\rightarrow
Actuator
\rightarrow
Environment.
]

Dadurch beeinflussen Handlungen zukünftige Wahrnehmungen.

Genau diese Rückkopplung unterscheidet verkörpertes Lernen von der Verarbeitung statischer Datensätze.

---

# 28. Multimodale Architektur

Langfristig sind folgende Adapter vorgesehen:

```text
Sensor
├── TextSensor
├── CameraSensor
├── AudioSensor
├── TactileSensor
└── EnvironmentSensor

Actuator
├── TextActuator
├── SpeechActuator
├── MotorActuator
└── EnvironmentActuator
```

Nicht jede Modalität benötigt ein LLM.

Insbesondere sollten:

* visuelle Rohdaten,
* Audiodaten,
* taktile Daten,
* propriozeptive Signale

möglichst direkt über geeignete Encoder in neuronale Ereignisse transformiert werden.

---

# 29. Skalierbarkeit

Der theoretische Raum von

[
50^5=312,500,000
]

Neuronen verbietet eine naive objektorientierte Vollmaterialisierung.

Angenommen, ein Neuron benötigt nur 128 Byte dynamischen Zustand:

[
312,500,000\times128
\approx40,GB.
]

Bereits ohne Synapsen.

Bei durchschnittlich (k) Synapsen pro Neuron gilt:

[
S=N\cdot k.
]

Bei nur

[
k=100
]

entstünden:

[
31.25,\text{Milliarden Synapsen}.
]

Bei 16 Byte je Synapseneintrag:

[
500,GB
]

Rohdaten.

Die tatsächlichen Anforderungen können durch zusätzliche Zustände erheblich höher liegen.

Daraus folgt:

> Brain-5D muss langfristig sparse, chunked und ereignisorientiert arbeiten.

---

# 30. Sparse Materialization

Der 5D-Hyperkubus sollte daher als **Adressraum** verstanden werden.

Nur aktive beziehungsweise existente Neuronen werden materialisiert:

[
\mathcal{N}*{active}
\subset
\mathcal{N}*{potential}.
]

Damit kann gelten:

[
|\mathcal{N}*{active}|
\ll
|\mathcal{N}*{potential}|.
]

Diese Unterscheidung ist für die Skalierungsstrategie fundamental.

---

# 31. Persistenz und digitaler Zwilling

Ein persistenter Brain-5D-Zustand umfasst mindestens:

### Neuronenzustände

* ID,
* 5D-Koordinate,
* Zelltyp,
* Membranpotential,
* Recovery State,
* Erregbarkeit,
* Energie,
* Alter,
* Aktivitätshistorie.

### Synapsenzustände

* Source,
* Target,
* Gewicht,
* Typ,
* Delay,
* Alter,
* Eligibility Trace,
* letzte Aktivierung,
* Plastizitätsstatus.

### Globale Zustände

* Tick,
* RNG-State,
* Reward,
* Homeostasis State,
* Growth Budget,
* Konfigurationsversion.

---

# 32. Reproduzierbarkeit

Für wissenschaftliche Experimente muss ein Snapshot neben neuronalen Daten mindestens enthalten:

```text
experiment_id
software_version
git_commit
configuration_hash
random_seed
rng_state
tick
network_schema_version
plasticity_version
stimulus_history_hash
decoder_version
```

Nur dadurch kann ein Experiment exakt rekonstruiert werden.

---

# 33. Determinismus

Brain-5D sollte einen expliziten **Deterministic Research Mode** besitzen.

Bei identischem:

[
X_0,
I,
\Theta,
seed
]

sollte möglichst gelten:

[
X_t^{(1)}=X_t^{(2)}.
]

Nichtdeterministische Hardwarepfade müssen dokumentiert werden.

Dies ist insbesondere für GPU-Parallelisierung relevant.

---

# 34. Experimentelles Protokoll

Jedes veröffentlichte Experiment sollte mindestens dokumentieren:

* Git-Commit,
* Konfiguration,
* Seed,
* Hardware,
* Betriebssystem,
* Python-Version,
* Simulationsdauer,
* Neuronenzahl,
* Synapsenzahl,
* Spikezahl,
* Plastizitätsparameter,
* Eingabedaten,
* Rewards,
* Speicherstand,
* Evaluationsmetriken.

---

# 35. Kernmetriken

## Netzwerkdynamik

* Mean firing rate
* Spike count
* Burst index
* Synchrony
* Active neuron fraction
* Silent neuron fraction
* Inter-spike intervals

## Struktur

* Neuron count
* Synapse count
* Mean degree
* Degree distribution
* Clustering
* Path length
* Region connectivity

## Plastizität

* Weight distribution
* LTP/LTD ratio
* New synapses/tick
* Pruned synapses/tick
* Neurons generated/tick

## Ressourcen

* RAM
* CPU time/tick
* spikes/second
* synaptic updates/second
* snapshot size
* storage throughput.

---

# 36. Wissenschaftliche Ablationen

Brain-5D sollte nicht nur „funktionierende“ Konfigurationen zeigen.

Mindestens folgende Ablationen sind erforderlich:

[
A_0:\text{vollständiges System}
]

[
A_1:\text{ohne STDP}
]

[
A_2:\text{ohne Homeostase}
]

[
A_3:\text{ohne strukturelle Plastizität}
]

[
A_4:\text{ohne Reward-Modulation}
]

[
A_5:\text{ohne LLM}
]

[
A_6:\text{LLM Monitoring only}
]

[
A_7:\text{ohne 5D-Lokalität}
]

[
A_8:\text{randomisierte Topologie}.
]

Nur dadurch kann festgestellt werden, welche Komponenten tatsächlich zur gemessenen Leistung beitragen.

---

# 37. Falsifikationskriterien

Ein Forschungsframework benötigt nicht nur Erfolgsbedingungen.

Es benötigt Bedingungen, unter denen seine Hypothesen als nicht bestätigt gelten.

Beispiele:

### Hypothese H1

5D-Lokalität verbessert selbstorganisierte Struktur.

**Falsifikation:**

Wenn 5D-Netze gegenüber dimensionsreduzierten oder zufälligen Kontrollnetzen über mehrere Seeds keinen statistisch belastbaren Vorteil zeigen.

### H2

Strukturelle Plastizität verbessert Continual Learning.

**Falsifikation:**

Wenn Retention und Adaptationsleistung gegenüber statischer Topologie nicht steigen.

### H3

Das SNN speichert externe Wissensinhalte.

**Falsifikation:**

Wenn Recall nach Entfernung von LLM-Kontext und Retrieval-Zugriff auf Zufallsniveau fällt.

Diese Formulierungen sind für wissenschaftliche Glaubwürdigkeit wesentlich.

---

# 38. Nullhypothesen

Entsprechend sollten explizite Nullhypothesen definiert werden:

[
H_0^{5D}:
]

Die fünfdimensionale Organisation besitzt keinen messbaren Vorteil gegenüber einer geeigneten Kontrolltopologie.

[
H_0^{SP}:
]

Strukturelle Plastizität verbessert die Lernleistung nicht.

[
H_0^{LLM}:
]

Die beobachtete semantische Leistung stammt primär aus dem Language Organ und nicht aus dem SNN.

Gerade die letzte Nullhypothese ist für Brain-5D von zentraler Bedeutung.

---

# 39. Statistische Evaluation

Ein einzelner Lauf ist kein belastbarer Nachweis.

Experimente müssen über mehrere Seeds durchgeführt werden:

[
seed_1,\ldots,seed_n.
]

Zu berichten sind beispielsweise:

* Mittelwert,
* Median,
* Standardabweichung,
* Konfidenzintervalle,
* Effektgrößen.

Wo sinnvoll sollten Hypothesentests oder Bayes'sche Vergleiche ergänzt werden.

---

# 40. Vergleichsbaselines

Brain-5D sollte langfristig nicht nur gegen sich selbst getestet werden.

Geeignete Baselines umfassen:

* statisches SNN,
* SNN ohne 5D-Struktur,
* Reservoir Computing,
* klassische rekurrente Netze,
* einfache Reinforcement-Learning-Agenten,
* LLM-only-System,
* Retrieval-Augmented LLM,
* randomisierte Netzwerke.

Dabei muss nicht zwingend absolute Leistungsüberlegenheit gezeigt werden.

Wissenschaftlich interessanter kann sein, **welche Eigenschaften unter welchen Bedingungen entstehen**.

---

# 41. Verhältnis zu neuromorpher Hardware

Die eventbasierte Architektur von SNNs besitzt prinzipielle Nähe zu neuromorphen Systemen.

Brain-5D sollte deshalb langfristig die Trennung zwischen:

[
\text{mathematischem Modell}
]

und

[
\text{Ausführungsbackend}
]

stärken.

Dadurch könnten zukünftig unterschiedliche Backends unterstützt werden:

```text
Brain5D Model
      │
Intermediate Representation
      │
 ┌────┼────────────┐
CPU   GPU     Neuromorphic
```

Das logische Modell darf nicht unnötig von einer bestimmten Hardwarearchitektur abhängen.

---

# 42. Das LLM als experimentelle Variable

Das Language Organ sollte selbst Bestandteil der Ablationsmatrix sein.

Zu vergleichen sind:

### L0

Kein LLM.

### L1

LLM ausschließlich als Decoder.

### L2

LLM als Encoder und Decoder.

### L3

LLM plus externe Knowledge Intake Engine.

Dadurch kann gemessen werden:

[
\Delta Q_{LLM}=Q(L_n)-Q(L_0).
]

Noch wichtiger ist jedoch:

[
Q_{SNN-only}
]

nach einer Trainingsphase mit LLM.

Dadurch wird geprüft, ob Fähigkeiten in das SNN übergegangen sind oder weiterhin vollständig vom externen Modell abhängen.

---

# 43. Language-Organ-Backend

Die Schnittstelle sollte modellagnostisch bleiben:

```text
LanguageModelBackend
├── NullLanguageBackend
├── LlamaCppBackend
├── RemoteBackend
└── FutureBackend
```

Die konkrete Wahl eines kleinen Qwen-, Granite- oder anderen Modells ist damit eine **Deployment-Entscheidung und keine Eigenschaft der Brain-5D-Theorie**.

Das verhindert unnötige Kopplung an ein schnell alterndes konkretes LLM.

---

# 44. Fehlerisolation

Der SNN-Runtime-Loop muss auch dann weiterlaufen, wenn:

* das LLM abstürzt,
* die Netzwerkverbindung ausfällt,
* Wikipedia nicht erreichbar ist,
* ein Parser fehlschlägt,
* ein Sensor keine Daten liefert,
* ein Decoder ungültige Ergebnisse erzeugt.

Damit gilt:

[
Failure_{external}
\nRightarrow
Failure_{SNN}.
]

Diese Eigenschaft sollte automatisiert getestet werden.

---

# 45. Observability

Ein wissenschaftliches System benötigt mehr als Logging.

Brain-5D sollte mindestens vier Beobachtungsebenen besitzen:

### Runtime

Was geschieht gerade?

### Structural

Wie verändert sich der Graph?

### Functional

Welche Populationen reagieren?

### Experimental

Welche Hypothese wird mit welcher Konfiguration geprüft?

Telemetry darf jedoch den neuronalen Zustand nicht unbeabsichtigt verändern.

---

# 46. Entwicklungsroadmap

## Alpha.6 – Morphological Stabilization

Schwerpunkte:

* Homeostasis,
* Growth Budgets,
* Structural Costs,
* Anti-Oscillation,
* Neuron/Synapse Age,
* deterministische Contracts,
* SignalFrame,
* StimulusPlan,
* LanguageOrgan Protocol.

## Alpha.7 – Language Organ PoC

* lokales Backend,
* asynchrone Queue,
* Null-Backend,
* Timeout,
* Resource Limits,
* Monitoring-only-Ablation.

## v0.6 – Scaling & Knowledge Intake

* Sparse Storage,
* Chunking,
* Dirty Tracking,
* Provenance,
* KnowledgeItem,
* SourceRecord,
* Importer,
* skalierbare Benchmarks.

## v0.7 – Controlled Learning

* KnowledgeEpisode,
* Train/Eval Isolation,
* Delayed Reward,
* Retention,
* Contradiction Experiments,
* Continual Learning.

## v0.8 – Embodiment

* multimodale Sensoren,
* Aktoren,
* geschlossene Environment Loop,
* multimodale zeitliche Synchronisation.

## v0.9 – Memory and World Model

Erst wenn experimentelle Evidenz dies rechtfertigt:

* episodische Gedächtnisstrukturen,
* interne Zustandsvorhersage,
* Sequenzrepräsentationen,
* multimodale Assoziationen,
* internes Weltmodell.

---

# 47. Zentrale Forschungsfragen

Brain-5D sollte seine weitere Entwicklung an expliziten Forschungsfragen ausrichten.

### RQ1

Erzeugt die fünfdimensionale Topologie messbare Vorteile gegenüber 3D-, 2D- und nichtgeometrischen Graphen?

### RQ2

Kann strukturelle Plastizität stabile funktionale Regionen hervorbringen?

### RQ3

Kann ein SNN Informationen nach einmaliger oder wiederholter Exposition langfristig speichern?

### RQ4

Kann gespeicherte Information unter veränderten Eingabemustern generalisiert abgerufen werden?

### RQ5

Verbessert verkörperte Rückkopplung die Repräsentationsbildung?

### RQ6

Kann die Abhängigkeit vom externen Language Organ im Laufe des Lernens reduziert werden?

### RQ7

Entstehen wiederkehrende neuronale Aktivitätsmuster, die robust mit semantischen oder sensorischen Kategorien korrelieren?

### RQ8

Kann das System widersprüchliche Information integrieren, ohne frühere Repräsentationen vollständig zu überschreiben?

---

# 48. Was Brain-5D derzeit ausdrücklich nicht behauptet

Brain-5D sollte keine unbelegten Aussagen darüber treffen, dass das System bereits:

* Bewusstsein besitzt,
* menschenähnlich denkt,
* semantisches Verständnis besitzt,
* biologisch vollständig realistisch ist,
* allgemeine Intelligenz erreicht,
* eigenständig Symbole entwickelt hat,
* ein Gehirn simuliert.

Das Projekt untersucht Mechanismen, die möglicherweise Bausteine solcher komplexeren Eigenschaften darstellen können.

Diese wissenschaftliche Zurückhaltung stärkt und schwächt das Projekt nicht.

---

# 49. Kernhypothese

Die zentrale Arbeitshypothese von Brain-5D kann präzise formuliert werden:

> **Ein räumlich strukturiertes, zeitdynamisches, rekurrentes Spiking-Netzwerk mit lokaler, homöostatischer und struktureller Plastizität kann durch kontinuierliche sensorische Interaktion persistente interne Zustände und funktionale Repräsentationen entwickeln. Ein externes Sprachmodell kann dabei als kontrollierte semantische Schnittstelle eingesetzt werden, ohne selbst Eigentümer der neuronalen Lern- und Zustandsdynamik zu werden.**

Diese Hypothese ist prüfbar.

Sie kann bestätigt, eingeschränkt oder falsifiziert werden.

Genau darin liegt ihr wissenschaftlicher Wert.

---

# 50. Schlussfolgerung

Brain-5D sollte nicht primär als Versuch verstanden werden, ein weiteres Large Language Model zu bauen.

Ebenso wenig ist es lediglich ein großer SNN-Simulator.

Der wissenschaftlich interessante Teil liegt in der Kombination von:

[
\text{Zeit}
+
\text{Topologie}
+
\text{Plastizität}
+
\text{Persistenz}
+
\text{Verkörperung}
+
\text{kontrollierter Symbolkopplung}.
]

Das Language Organ stellt dabei eine Brücke zur bestehenden symbolischen Welt dar, darf jedoch die zu untersuchende neuronale Dynamik nicht verdecken.

Die wichtigste methodische Forderung für die weitere Entwicklung lautet deshalb:

> **Jede beobachtete Fähigkeit muss daraufhin untersucht werden, wo sie tatsächlich entsteht.**

Liegt sie im Sprachmodell?

Liegt sie im Decoder?

Liegt sie im Retrieval-System?

Liegt sie in handgeschriebenen Regeln?

Oder lässt sie sich auch nach Isolation dieser Komponenten im Zustand und Verhalten des SNN nachweisen?

Erst diese Trennung macht Brain-5D zu einem wissenschaftlich interessanten Experiment.

Die langfristige Bedeutung des Projekts wird daher nicht daran gemessen werden, ob das System überzeugend sprechen kann.

Sie wird daran gemessen werden müssen, ob experimentell nachweisbar ist, dass sein neuronales Substrat **selbst persistente, adaptive und generalisierbare interne Strukturen ausbildet**.

---

# Literatur und technische Referenzbasis

1. E. M. Izhikevich: *Simple Model of Spiking Neurons*. IEEE Transactions on Neural Networks, 14(6), 1569–1572, 2003. DOI: 10.1109/TNN.2003.820440.

2. G.-Q. Bi, M.-M. Poo: *Synaptic Modifications in Cultured Hippocampal Neurons: Dependence on Spike Timing, Synaptic Strength, and Postsynaptic Cell Type*. Journal of Neuroscience, 1998.

3. W. Gerstner, W. M. Kistler, R. Naud, L. Paninski: *Neuronal Dynamics*. Cambridge University Press, 2014.

4. E. M. Izhikevich: *Dynamical Systems in Neuroscience*. MIT Press, 2007.

5. K. Roy, A. Jaiswal, P. Panda: *Towards spike-based machine intelligence with neuromorphic computing*. Nature 575, 607–617, 2019.

6. Neuromorphic Intermediate Representation (NIR): Arbeiten zur hardware- und simulatorunabhängigen Repräsentation neuromorpher Berechnungsmodelle.

7. Literatur zu Structural Plasticity, STDP-driven Rewiring und Homeostatic Plasticity.

8. Literatur zu Neuro-Symbolic AI und der Verbindung neuronaler Lernverfahren mit symbolischen Repräsentationen.

9. Literatur zu Embodied Intelligence, insbesondere zur dynamischen Kopplung von Wahrnehmung, Handlung, Körper und Umwelt.

10. `llama.cpp`: Referenzimplementierung für lokale, quantisierte LLM-Inferenz und mögliche technische Grundlage eines austauschbaren Brain-5D Language-Organ-Backends.

11. W3C PROV: Referenzmodell für Provenienz und nachvollziehbare Datenherkunft; potenzielle konzeptionelle Grundlage für die Brain-5D Knowledge Intake Engine.

---

## Empfohlene Zitierweise des Projekts

**Heisig, T. et al.**
*Brain-5D: A Hybrid Spatial Spiking Architecture for Self-Organizing and Embodied Cognitive Systems.*
Experimental Research Framework, Brain-5D Project, 2026.

*Hinweis: Die endgültige bibliografische Form sollte erst bei einer formalen Veröffentlichung mit stabiler Version, DOI beziehungsweise archiviertem Release festgelegt werden.*
