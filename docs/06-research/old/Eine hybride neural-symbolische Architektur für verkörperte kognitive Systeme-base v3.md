# Brain-5D: Eine hybride, räumlich organisierte Spiking-Architektur für selbstorganisierende und verkörperte kognitive Systeme

## Architektur, methodische Grundlagen, experimentelle Hypothesen und Forschungsroadmap

---

**Projekt:** Brain-5D
**Repository:** `Thomas-Heisig/Brain-5D`
**Entwicklungsstatus:** experimentelles Forschungsframework / Alpha-Phase
**Dokumenttyp:** Technisches und wissenschaftliches Architekturpapier mit methodischer Rahmung

---

## Abstract

Brain-5D ist ein experimentelles Forschungsframework zur Untersuchung selbstorganisierender kognitiver Systeme auf Grundlage zeitkontinuierlicher beziehungsweise diskret simulierter neuronaler Dynamik, lokaler Plastizität, struktureller Reorganisation und multimodaler Sensor-Aktor-Kopplung.

Die zentrale Architektur besteht aus einem **Spiking Neural Network (SNN)**, dessen Neuronen in einem logisch fünfdimensionalen Koordinatenraum organisiert werden. Dieser Raum dient nicht lediglich der Visualisierung, sondern soll als strukturelle Grundlage für Lokalität, Konnektivität, funktionale Regionen, Wachstumsprozesse und langfristig die Bildung interner Repräsentationen dienen.

Im Gegensatz zu Architekturen, bei denen ein Large Language Model (LLM) die zentrale kognitive Instanz bildet, behandelt Brain-5D ein Sprachmodell als **optionales externes Language Organ**. Dieses besitzt keine unmittelbaren Schreibrechte auf synaptische Gewichte, strukturelle Plastizität oder den zentralen Simulationszyklus. Die Kopplung zwischen SNN und symbolischen Systemen erfolgt über definierte Datenverträge, insbesondere `StimulusPlan` und `SignalFrame`.

Das langfristige Forschungsziel besteht nicht darin, ein Sprachmodell durch ein SNN lediglich zu ergänzen. Untersucht werden soll vielmehr, in welchem Umfang ein dynamisches, plastisches und verkörpertes neuronales Substrat eigenständig persistente interne Zustände, Assoziationen, adaptive Verhaltensmuster und gegebenenfalls abstraktere Repräsentationen ausbilden kann.

Entsprechend werden Behauptungen über „Verstehen“, „Bewusstsein“, „Reasoning“ oder „echte Intelligenz“ ausdrücklich **nicht als bereits erreichte Eigenschaften des Systems vorausgesetzt**. Sie sind – soweit überhaupt operationalisierbar – Gegenstand zukünftiger Experimente.

---

## 1. Einleitung: Forschungsfrage und Motivation

### 1.1 Ausgangsproblem

Moderne Large Language Models besitzen außerordentlich leistungsfähige Fähigkeiten zur Verarbeitung symbolischer Sequenzen. Ihre interne Berechnung unterscheidet sich jedoch fundamental von biologischen neuronalen Systemen:

- token- und sequenzorientiert,
- überwiegend durch Offline-Training geprägt,
- nicht intrinsisch sensorisch verkörpert,
- nicht kontinuierlich durch lokale synaptische Plastizität lernend,
- nicht primär ereignisgetrieben,
- nicht auf neuronale Entwicklung oder strukturelles Wachstum ausgelegt.

Spiking Neural Networks besitzen dagegen explizite zeitliche Zustände und diskrete Spike-Ereignisse. Sie erlauben die Untersuchung lokaler Plastizitätsmechanismen, rekurrenter Dynamik, Synchronisation, Oszillation und eventbasierter Informationsverarbeitung. SNNs sind zugleich keineswegs automatisch intelligent – ein biologisch inspiriertes Neuronenmodell, STDP oder Neurogenese erzeugen für sich genommen weder Sprache noch semantische Repräsentationen noch allgemeines Reasoning.

Brain-5D setzt genau an dieser offenen Lücke an.

### 1.2 Übergeordnete Forschungsfrage

Die zentrale Forschungsfrage des Projekts lautet:

> **Unter welchen Bedingungen kann ein räumlich und funktional strukturierter, kontinuierlich plastischer Spiking-Neural-Network-Verbund durch sensorisch-aktorische Interaktion stabile, abrufbare und generalisierbare interne Repräsentationen ausbilden, ohne dass deren semantischer Inhalt direkt durch ein externes Sprachmodell in den neuronalen Zustand geschrieben wird?**

### 1.3 Teilfragen

| Kennung | Frage |
|---------|-------|
| **RQ1 – Topologie** | Welchen messbaren Einfluss besitzt eine fünfdimensionale räumlich-funktionale Topologie gegenüber niedrigerdimensionalen und nichtgeometrischen Kontrolltopologien? |
| **RQ2 – Plastizität** | Welchen Beitrag leisten STDP, Homeostase, strukturelle Plastizität und modulatorische Lernsignale jeweils zur langfristigen Stabilität und Lernfähigkeit? |
| **RQ3 – Repräsentation** | Entstehen reproduzierbare neuronale Zustandsräume oder Aktivitätsmuster, die systematisch mit Klassen von Wahrnehmungen, Erfahrungen oder Handlungen korrespondieren? |
| **RQ4 – Gedächtnis** | Bleiben durch Lernprozesse erzeugte interne Veränderungen ohne erneute Bereitstellung der ursprünglichen Information abrufbar? |
| **RQ5 – Continual Learning** | Kann neues Wissen erworben werden, ohne zuvor erworbene funktionale Repräsentationen vollständig zu überschreiben? |
| **RQ6 – Embodiment** | Führt eine geschlossene Wahrnehmungs-Handlungs-Schleife zu anderen internen Repräsentationen als eine vergleichbare offene Stimulusverarbeitung? |
| **RQ7 – Language Organ** | Welche beobachtbaren Fähigkeiten stammen aus dem SNN und welche aus Encoder, Decoder, Retrieval-System oder LLM? |
| **RQ8 – Skalierung** | Welche neuronalen, strukturellen und rechnerischen Eigenschaften bleiben beim Übergang von kleinen Proof-of-Concept-Netzen zu größeren Netzwerken erhalten? |

### 1.4 Kernhypothese

> **Ein rekurrentes Spiking-Netzwerk mit räumlich-funktionaler Topologie, lokaler zeitabhängiger Plastizität, homeostatischer Regulation, struktureller Anpassung und verkörperter Rückkopplung kann unter geeigneten Randbedingungen persistente und funktional unterscheidbare interne Zustände ausbilden, ohne dass diese Zustände explizit durch ein externes symbolisches Modell vorgegeben werden müssen.**

Daraus folgt ausdrücklich **nicht**, dass das System Bewusstsein, menschliches Verständnis, allgemeine Intelligenz oder biologische Äquivalenz erreicht. Diese Begriffe bilden keine Voraussetzungen der Architektur.

---

## 2. Wissenschaftliche Positionierung und epistemischer Status

### 2.1 Forschungskontext

Brain-5D liegt an der Schnittstelle mehrerer Forschungsrichtungen:

- Computational Neuroscience
- Spiking Neural Networks
- Neuromorphic Computing
- Structural Plasticity
- Continual Learning
- Reinforcement Learning
- Neuro-Symbolic AI
- Embodied Intelligence
- Dynamische Systeme
- Adaptive Graphen
- Persistente neuronale Simulation
- Multimodale Agentensysteme

Der Begriff **neural-symbolisch** wird dabei funktional verwendet: Die neuronale Seite besteht aus Spike-Dynamik, Netzwerkzuständen und plastischen Verbindungen; die symbolische Seite umfasst Sprache, strukturierte Wissensobjekte, Provenienz und externe Schnittstellen. Die symbolische Komponente soll jedoch nicht unkontrolliert den neuronalen Zustand verändern können.

### 2.2 Epistemischer Status und Evidenzebenen

Brain-5D ist im gegenwärtigen Entwicklungszustand als **experimentelles Forschungsframework** und nicht als bereits validiertes kognitives Modell einzuordnen. Die Architektur enthält Mechanismen, die aus verschiedenen Forschungsbereichen abgeleitet sind. Aus dem Vorhandensein dieser Mechanismen folgt jedoch nicht automatisch die Entstehung höherer kognitiver Fähigkeiten.

Daher unterscheidet Brain-5D konsequent zwischen vier Evidenzebenen:

| Ebene | Bezeichnung | Beschreibung |
|-------|-------------|--------------|
| **E0** | Architekturhypothese | Eine Komponente oder Beziehung ist theoretisch begründet, aber noch nicht experimentell validiert. |
| **E1** | Implementierungsnachweis | Eine Komponente funktioniert technisch entsprechend ihrer Spezifikation. |
| **E2** | Experimenteller Funktionsnachweis | Eine Komponente erzeugt unter kontrollierten Bedingungen einen reproduzierbaren messbaren Effekt. |
| **E3** | Systemischer Funktionsnachweis | Der Effekt bleibt in einer komplexeren Umgebung erhalten und lässt sich gegenüber Alternativerklärungen isolieren. |

Diese Ebenen verhindern eine Vermischung von Implementierung, Funktion und kognitiver Interpretation. Beispielsweise ist eine persistente synaptische Gewichtsänderung zunächst nur eine persistente Zustandsänderung. Sie wird erst dann zu einem Kandidaten für funktionales Gedächtnis, wenn nachgewiesen werden kann, dass sie durch eine spezifische Lernerfahrung verursacht wurde, über einen definierten Zeitraum erhalten bleibt, durch einen passenden Cue reaktiviert werden kann und Verhalten oder Netzwerkantwort spezifisch beeinflusst.

### 2.3 Abgrenzung zu verwandten Ansätzen

Keine der folgenden Komponenten ist isoliert als neu zu beanspruchen:

- Spiking Neural Networks
- STDP
- Homeostase
- strukturelle Plastizität
- verkörpertes Lernen
- LLMs
- neural-symbolische Systeme

Die potenzielle wissenschaftliche Eigenständigkeit von Brain-5D liegt daher primär in der **spezifischen Systemkomposition und den kontrollierten Kausalitätsgrenzen**. Insbesondere gilt die Architekturregel: **LLM → StimulusPlan → SNN**. Das LLM schreibt nicht direkt auf synaptische Gewichte.

---

## 3. Forschungsstatus versus Zielarchitektur

Für die wissenschaftliche Bewertung von Brain-5D ist eine klare Unterscheidung zwingend erforderlich:

### 3.1 Implementierter Zustand

Funktionen, die im Repository implementiert, durch Tests überprüfbar, reproduzierbar ausführbar und durch Messdaten belegbar sind.

### 3.2 Engineering-Roadmap

Bereits spezifizierte, aber noch nicht vollständig implementierte Komponenten.

### 3.3 Forschungshypothesen

Erwartete Eigenschaften wie selbstorganisierte Repräsentationsbildung, emergente funktionale Regionen, langfristiges assoziatives Gedächtnis, interne Symbolbildung, multimodale Begriffsbildung und transferierbare interne Repräsentationen. Diese Eigenschaften dürfen nicht mit implementierter Funktionalität gleichgesetzt werden.

---

## 4. Das Brain-5D-Systemmodell

### 4.1 Grundstruktur

Die Architektur kann abstrahiert dargestellt werden als:

\[
\mathcal{B} = (\mathcal{N},\mathcal{S},\mathcal{P},\mathcal{H},\mathcal{E},\mathcal{A},\mathcal{M})
\]

mit:
- \(\mathcal{N}\): Neuronenmenge
- \(\mathcal{S}\): Synapsen beziehungsweise gerichtete Kanten
- \(\mathcal{P}\): Plastizitätsoperatoren
- \(\mathcal{H}\): homöostatische Regelung
- \(\mathcal{E}\): sensorische Eingänge
- \(\mathcal{A}\): Aktoren/Ausgänge
- \(\mathcal{M}\): persistenter Systemzustand

Der Gesamtzustand zum Zeitpunkt \(t\) sei:

\[
X(t) = \{X_N(t), X_S(t), X_H(t), X_E(t), X_M(t)\}
\]

Die Entwicklung ergibt sich abstrakt aus:

\[
X(t+\Delta t) = F(X(t), I(t), R(t), \Theta)
\]

mit:
- \(I(t)\): sensorischem Input
- \(R(t)\): optionalem Reward beziehungsweise Modulationssignal
- \(\Theta\): globalen Simulationsparametern

Entscheidend ist: Das LLM ist kein Bestandteil von \(F\), der beliebig den internen neuronalen Zustand verändern darf. Es kann Daten für \(I(t)\) beziehungsweise semantische Interpretationen erzeugen, muss dabei jedoch definierte Schnittstellen passieren.

### 4.2 Zeitmodell

Brain-5D besitzt mindestens drei voneinander zu unterscheidende Zeitskalen:

| Bezeichnung | Symbol | Beschreibung |
|-------------|--------|--------------|
| Neuronale Zeit | \(t_n\) | Integrationsschritte des SNN (typisch 1 ms) |
| Plastizitätszeit | \(t_p\) | Langsamere Prozesse: STDP, Homeostase, Pruning, Wachstum |
| Kognitive Zeit | \(t_c\) | Language-Organ-Aufruf, Wissensaufnahme, Sensorfusion, Aktionsplanung |

Damit gilt typischerweise:

\[
t_n \ll t_p \ll t_c
\]

Diese explizite Trennung verhindert, dass langsame LLM-Inferenz die neuronale Simulation synchron blockiert.

---

## 5. Der fünfdimensionale neuronale Raum

### 5.1 Formale Definition

Jedes Neuron \(n_i\) besitzt eine Position

\[
p_i = (x_i, y_i, z_i, a_i, b_i)
\]

in einem fünfdimensionalen diskreten oder kontinuierlichen Raum. Für einen diskreten Hyperkubus mit Kantenlänge \(L\) ergibt sich:

\[
N = L^5
\]

Für \(L=50\) folgt:

\[
N = 50^5 = 312.500.000
\]

Diese Zahl stellt eine theoretische Zielkapazität des vollständigen 5D-Raumes dar und nicht notwendigerweise die Anzahl gleichzeitig materialisierter Simulationsobjekte.

### 5.2 Bedeutung der fünf Dimensionen

Die zusätzlichen Dimensionen werden als **logische beziehungsweise funktionale Dimensionen** behandelt. Eine mögliche Interpretation lautet:

- \((x,y,z)\): räumliche oder topologische Lokalität
- \((a,b)\): funktionale, modale, entwicklungsbezogene oder assoziative Lokalität

Die Semantik soll nicht dauerhaft fest einprogrammiert werden. Eine langfristige Forschungsfrage lautet, ob die zusätzlichen Dimensionen durch Lern- und Wachstumsprozesse funktionale Bedeutung erhalten können.

### 5.3 Metrik und Konnektivität im 5D-Raum

Für zwei Positionen \(p_i=(x_i,y_i,z_i,a_i,b_i)\) und \(p_j=(x_j,y_j,z_j,a_j,b_j)\) kann eine gewichtete euklidische Distanz definiert werden:

\[
d_{ij} = \sqrt{\lambda_x(x_i-x_j)^2 + \lambda_y(y_i-y_j)^2 + \lambda_z(z_i-z_j)^2 + \lambda_a(a_i-a_j)^2 + \lambda_b(b_i-b_j)^2}
\]

Die Koeffizienten \(\lambda_k\) definieren die Bedeutung der jeweiligen Dimension. Damit kann eine distanzabhängige Verbindungswahrscheinlichkeit formuliert werden:

\[
P(i\rightarrow j) = P_0 \exp\left(-\frac{d_{ij}}{\sigma}\right)
\]

Zusätzlich können Aktivitätskorrelation, Zelltyp und Entwicklungszustand berücksichtigt werden:

\[
P_{ij} = f(d_{ij}, C_{ij}, T_i, T_j, A_i, A_j)
\]

Damit entsteht kein vollständig verbundener Hypergraph, sondern ein **sparsamer, dynamischer Graph innerhalb eines fünfdimensionalen Koordinatenraums**.

### 5.4 Dimensionsablation

Die Frage "Warum fünf Dimensionen?" wird experimentell beantwortet. Verglichen werden:

\[
D \in \{2, 3, 4, 5, 6\}
\]

sowie mindestens eine nichtgeometrische Kontrolltopologie. Dabei müssen Neuronenzahl, mittlerer Knotengrad, synaptisches Budget, Stimuli, Lernregeln und Simulationsdauer so weit wie möglich kontrolliert werden.

Zu messen sind: Lernleistung, Retention, Modularität, Pfadlänge, Clustering, Aktivitätssparsity, Robustheit und Rechenkosten. Eine Überlegenheit von 5D wird somit nicht vorausgesetzt – sie ist eine falsifizierbare Hypothese.

---

## 6. Neuronales Dynamikmodell

### 6.1 Izhikevich-Modell

Brain-5D verwendet im derzeitigen Entwurf das Izhikevich-Modell als rechnerisch effiziente Näherung unterschiedlicher Spike-Dynamiken. Die Gleichungen lauten:

\[
\frac{dv}{dt} = 0.04v^2 + 5v + 140 - u + I
\]

\[
\frac{du}{dt} = a(bv - u)
\]

Bei \(v \geq 30\,\text{mV}\) erfolgt der Reset:

\[
v \leftarrow c, \quad u \leftarrow u + d
\]

Dabei bezeichnet:
- \(v\): Membranpotential
- \(u\): Recovery-Variable
- \(I\): Gesamteingang
- \(a,b,c,d\): zelltypspezifische Parameter

Das Modell stellt ausdrücklich **keine vollständige biophysikalische Simulation eines realen Neurons** dar. Sein Vorteil besteht darin, unterschiedliche Spike- und Burst-Regime mit relativ geringem numerischem Aufwand abzubilden.

### 6.2 Neuronentypen und inhibitorische Dynamik

Brain-5D unterscheidet explizit zwischen:
- exzitatorischen Neuronen
- inhibitorischen Neuronen
- sensorischen Neuronen
- Projektionsneuronen
- Modulationsknoten

Eine Synapse erhält entsprechend ein Vorzeichen:
- \(w_{ij} > 0\): exzitatorisch
- \(w_{ij} < 0\): inhibitorisch

Das Verhältnis von Erregung und Hemmung bildet einen wesentlichen Untersuchungsparameter:

\[
E/I = \frac{\sum |w_{exc}|}{\sum |w_{inh}|}
\]

Zu messen sind ferner: mittlere Populationsrate, Burst-Häufigkeit, Synchronisationsgrad, Anteil stiller Neuronen, Anteil dauerhaft hochaktiver Neuronen und Oszillationsspektrum.

### 6.3 Modellablation

Für ausgewählte Benchmarks sollte untersucht werden:

\[
M \in \{\text{LIF}, \text{AdEx}, \text{Izhikevich}\}
\]

Ziel ist nicht zwangsläufig zu zeigen, dass Izhikevich "das beste" Modell ist. Vielmehr lautet die Frage: Welche beobachteten Brain-5D-Eigenschaften sind robust gegenüber der Wahl des Neuronenmodells?

---

## 7. Synaptische Plastizität

### 7.1 STDP

Für \(\Delta t = t_{post} - t_{pre}\) wird die Gewichtsänderung beschrieben durch:

\[
\Delta w = \begin{cases}
A_+ e^{-\Delta t / \tau_+}, & \Delta t > 0 \\
-A_- e^{\Delta t / \tau_-}, & \Delta t < 0
\end{cases}
\]

Die Gewichte müssen begrenzt werden:

\[
w_{min} \leq w_{ij} \leq w_{max}
\]

Ohne solche Grenzen können lokale Hebb-Regeln zu instabilen positiven Rückkopplungen führen.

### 7.2 Reward-modulierte Plastizität

Für verkörpertes Lernen reicht reines STDP wahrscheinlich nicht aus. Brain-5D untersucht deshalb eine **Three-Factor-Learning-Rule** als zentrale Erweiterung. Dabei entsteht zunächst ein Eligibility Trace \(e_{ij}(t)\) aus prä- und postsynaptischer Aktivität. Eine tatsächliche Gewichtsänderung erfolgt erst in Verbindung mit einem Modulations- beziehungsweise Rewardsignal:

\[
\Delta w_{ij} = \eta \cdot R(t) \cdot e_{ij}(t)
\]

Damit werden drei Faktoren kombiniert: präsynaptische Aktivität, postsynaptische Aktivität und globales beziehungsweise regionales Modulationssignal.

### 7.3 Lernregeln als Hypothesenraum

STDP wird nicht als einzig mögliche Lernregel verstanden. Brain-5D sollte langfristig mindestens folgende Klassen berücksichtigen:

- Pair-based STDP
- Triplet STDP
- BCM-artige Regeln
- Reward-modulated STDP
- Eligibility-Trace-Verfahren
- Homeostatic Scaling
- Intrinsic Plasticity

Die Kernfrage lautet: **Welche Kombination lokaler Regeln erzeugt stabile Anpassung?**

### 7.4 Homöostatische Plastizität

Die mittlere Feuerrate eines Neurons sei \(\bar r_i(t)\). Für eine Zielrate \(r_i^*\) kann die Erregbarkeit angepasst werden:

\[
\theta_i(t + \Delta t) = \theta_i(t) + \eta_h (\bar r_i - r_i^*)
\]

Ziel ist nicht eine identische Aktivität aller Neuronen, sondern die Vermeidung degenerierter Zustände: \(r_i \rightarrow 0\) für große Netzwerkbereiche beziehungsweise \(r_i \rightarrow r_{max}\) für dauerhaft überaktive Populationen.

### 7.5 Strukturelle Plastizität

Brain-5D unterscheidet zwischen:
- **funktionaler Plastizität**: Änderung vorhandener Gewichte
- **struktureller Plastizität**: Änderung des Graphen selbst

Eine neue Synapse kann entstehen, wenn \(C_{ij} > C_{min}\), \(d_{ij} < d_{max}\) und ein Ressourcenbudget verfügbar ist. Pruning kann ausgelöst werden, wenn \(|w_{ij}| < w_{prune}\) über einen Zeitraum \(T > T_{grace}\) bestehen bleibt. Damit sollen kurzfristige Schwankungen nicht sofort strukturelle Änderungen verursachen.

### 7.6 Neurogenese

Von synaptischer Neurogenese muss die Erzeugung neuer **Neuronen** unterschieden werden. Ein Growth-Score kann definiert werden als:

\[
G_r = \alpha O_r + \beta E_r + \gamma D_r - \delta C_r
\]

mit \(O_r\): Überlastung einer Region, \(E_r\): wiederkehrender Lernfehler, \(D_r\): Diversitätsbedarf, \(C_r\): Ressourcenverbrauch. Nur wenn \(G_r > G_{threshold}\) und ein globales Budget vorhanden ist, darf Wachstum erfolgen.

### 7.7 Ressourcen- und Energiemodell

Unbegrenztes Wachstum wäre sowohl biologisch als auch rechnerisch unplausibel. Eine abstrakte Kostenfunktion lautet:

\[
C(t) = c_n N(t) + c_s S(t) + c_p P(t) + c_a A(t)
\]

mit \(N(t)\): Neuronen, \(S(t)\): Synapsen, \(P(t)\): Spikes pro Zeiteinheit, \(A(t)\): strukturelle Änderungen. Das System kann dann unter \(C(t) \leq C_{max}\) operieren.

---

## 8. Der Signal Interpretation Layer

Das LLM erhält ausdrücklich **keine ungefilterten Spike-Arrays**. Stattdessen berechnet eine deterministische Transformationsschicht:

\[
S: \text{SpikeEvents} \rightarrow \text{SignalFrame}
\]

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

Der `SignalFrame` stellt eine **Messung**, keine Bedeutung dar. Ein hoher Synchronisationswert bedeutet zunächst nur: *Eine Population zeigte innerhalb eines definierten Zeitfensters erhöhte zeitliche Koordination.* Er bedeutet nicht automatisch: *Das Netzwerk denkt an Paris.* Diese semantische Zuordnung muss experimentell gelernt oder validiert werden.

Ein erweiterter Frame könnte abstrakt beschrieben werden als:

\[
F_t = (r, b, s, H, C, E, R, \Phi)
\]

mit Rate \(r\), Burststruktur \(b\), Synchronität \(s\), Entropie \(H\), Konnektivität \(C\), Energie \(E\), Regionen \(R\) und temporalen Motiven \(\Phi\).

---

## 9. Das Language Organ

### 9.1 Grundprinzip

Das Language Organ ist:
- optional,
- austauschbar,
- fehlertolerant,
- asynchron,
- nicht Eigentümer des Runtime Loops.

Die Beziehung lautet:

\[
\text{LLM} \neq \text{Brain-5D-Kern}
\]

Das LLM ist ein Adapter zwischen symbolischen und subsymbolischen Darstellungen.

### 9.2 Funktionen des Language Organs

Das LLM übernimmt drei klar definierte, nicht-invasive Funktionen:

**1. Füttern (Semantische Brücke nach innen)**
Das LLM kodiert externe, symbolische Eingaben in strukturierte Spike-Muster für den Input-Layer des SNN über den SemanticEncoder.

**2. Übersetzen (Semantische Brücke nach außen)**
Das LLM dekodiert die Spike-Muster des Output-Layers (als SignalFrame) in natürliche Sprache oder Handlungsanweisungen über den SemanticDecoder.

**3. Überwachen (Homöostatische Rückkopplung)**
Das LLM generiert auf Basis seiner Dekodierung einen Monitoring-Bericht, der als zusätzlicher Input zurück ins SNN gespeist wird.

### 9.3 Semantic Encoder und StimulusPlan

Text darf nicht unmittelbar als synaptischer Zustand geschrieben werden. Stattdessen gilt:

\[
\text{Text} \rightarrow \text{Semantic Representation} \rightarrow \text{StimulusPlan} \rightarrow \text{Spike Input}
\]

Ein `StimulusPlan` sollte mindestens definieren: Zielregion, Startzeit, Dauer, Intensität, Frequenz, räumliche Verteilung, zeitliches Muster, Modalität, Herkunft und Stimulus-ID.

### 9.4 Semantic Decoder

Die Gegenrichtung lautet:

\[
\text{SpikeEvents} \rightarrow \text{SignalFrame} \rightarrow \text{Decoder} \rightarrow \text{symbolische Hypothese}
\]

Wichtig ist der Begriff **Hypothese**. Die Decoder-Ausgabe sollte mit Confidence, Decoder-Version, zugrunde liegendem SignalFrame, Zeitpunkt und Modell-ID gespeichert werden.

### 9.5 Language-Organ-Backend

Die Schnittstelle sollte modellagnostisch bleiben:

```
LanguageModelBackend
├── NullLanguageBackend
├── LlamaCppBackend
├── RemoteBackend
└── FutureBackend
```

Die konkrete Wahl eines kleinen Qwen- oder Granite-Modells ist damit eine **Deployment-Entscheidung und keine Eigenschaft der Brain-5D-Theorie**.

---

## 10. Sicherheits- und Kausalitätsgrenzen

Folgende Architekturregeln sollten als formale Invarianten behandelt werden:

1. Kein direkter LLM-Zugriff auf `synapse.weight`
2. Kein direkter Aufruf struktureller Plastizitätsoperatoren
3. Kein eigenständiger Aufruf von `network.step()`
4. Keine Ausführung beliebigen vom LLM erzeugten Codes
5. Kein Webinhalt darf unmittelbar neuronale Gewichte setzen
6. LLM-Aussagen werden nicht automatisch als Fakten klassifiziert
7. Timeout oder Absturz des LLM darf den neuronalen Runtime-Loop nicht stoppen
8. Jeder externe Einfluss muss einem definierten Eingabekanal zugeordnet werden
9. Alle zustandsverändernden Operationen müssen protokollierbar sein
10. LLM-Backends müssen durch ein Null-Backend ersetzbar sein

Der SNN-Runtime-Loop muss auch dann weiterlaufen, wenn das LLM abstürzt, die Netzwerkverbindung ausfällt, Wikipedia nicht erreichbar ist, ein Parser fehlschlägt, ein Sensor keine Daten liefert oder ein Decoder ungültige Ergebnisse erzeugt:

\[
\text{Failure}_{external} \nRightarrow \text{Failure}_{SNN}
\]

---

## 11. Knowledge Intake Engine

Externe Wissensaufnahme wird vom Language Organ getrennt. Die Pipeline lautet:

\[
\text{Source} \rightarrow \text{SourceRecord} \rightarrow \text{KnowledgeItem} \rightarrow \text{LearningStimulus} \rightarrow \text{SNN}
\]

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

Die Provenienzrelation ist durchgängig:

\[
\text{Source} \rightarrow \text{KnowledgeItem} \rightarrow \text{Stimulus} \rightarrow \text{Episode} \rightarrow \text{NetworkState} \rightarrow \text{SignalFrame} \rightarrow \text{Interpretation} \rightarrow \text{Response}
\]

---

## 12. Lernen versus Retrieval

Die zentrale experimentelle Unterscheidung lautet:

\[
\text{Retrieval} \neq \text{Learning}
\]

Ein valides Lernexperiment benötigt mindestens:

### Phase A – Baseline
Frage stellen, bevor die Information gelernt wurde.

### Phase B – Exposition
Information als kontrollierten Lernstimulus zuführen.

### Phase C – Konsolidierung
SNN ohne weiteren Informationsabruf weiterlaufen lassen.

### Phase D – Isolation
Netzwerkzustand erhalten, LLM-Kontext löschen, Retrieval Cache löschen, Netzwerkzugriff deaktivieren.

### Phase E – Recall
Semantisch gleiche oder variierte Frage erneut stellen.

### Phase F – Kontrolle
Vergleich mit ungeübtem Netzwerk, eingefrorener Plastizität, zufälligem Stimulus, Null-Language-Backend und zerstörtem beziehungsweise permutiertem relevanten Netzwerkzustand.

Erst daraus lässt sich eine belastbare Aussage über neuronale Speicherung ableiten.

---

## 13. Formale Definitionen

### 13.1 Lernen

Ein Lernprozess liegt für eine Aufgabe \(T\) vor, wenn eine Erfahrung \(E\) eine reproduzierbare Änderung einer Leistungsmetrik \(Q\) hervorruft:

\[
Q(T|E) > Q(T|\neg E)
\]

unter geeigneten Kontrollen.

### 13.2 Interne Repräsentation

Ein neuronaler Zustand \(Z\) wird nicht allein deshalb als Repräsentation bezeichnet, weil er mit einem Stimulus korreliert. Eine interne Repräsentation eines Merkmals \(Y\) liegt vor, wenn:
1. \(Y\) aus einem Netzwerkzustand \(Z\) mit über Zufall liegender Genauigkeit dekodiert werden kann,
2. diese Beziehung über wiederholte Versuche besteht,
3. sie auf nicht identische Beispiele generalisiert und
4. geeignete Kontrollzustände keine vergleichbare Information enthalten.

Informationstheoretisch kann zusätzlich untersucht werden: \(I(Z;Y) > 0\).

### 13.3 Gedächtnis

Für einen Lerninhalt \(K\) wird Gedächtnis durch mindestens drei Komponenten beschrieben:

\[
M_K = (R_K, C_K, S_K)
\]

mit:
- **Retention \(R\)**: Erhalt der relevanten Zustandsänderung über Zeit
- **Cue-dependent Recall \(C\)**: Reaktivierung durch einen geeigneten Hinweisreiz
- **Specificity \(S\)**: Unterscheidbarkeit gegenüber irrelevanten Kontrollreizen

Eine mögliche Gesamtmetrik ist: \(Q_M = R \cdot C \cdot S\).

---

## 14. Methodischer Grundaufbau

Alle zentralen Brain-5D-Experimente sollten einem gemeinsamen Schema folgen:

\[
\text{Baseline} \rightarrow \text{Intervention} \rightarrow \text{Learning} \rightarrow \text{Retention} \rightarrow \text{Evaluation} \rightarrow \text{Ablation}
\]

Jede Studie definiert vor Versuchsbeginn: unabhängige Variablen, abhängige Variablen, Kontrollbedingungen, Random Seeds, Abbruchkriterien, primäre Endpunkte und sekundäre Endpunkte.

### 14.1 Seed-Strategie und Wiederholungen

Ein einzelner Netzwerklauf kann aufgrund zufälliger Initialisierung, Topologie, Spike-Sequenzen und struktureller Änderungen nicht als belastbarer Effekt interpretiert werden. Jede Bedingung wird daher mit mehreren unabhängigen Seeds ausgeführt:

\[
s_1, s_2, \dots, s_n
\]

Die notwendige Anzahl \(n\) hängt ab von Effektgröße, Varianz, Testverfahren, gewünschter Power und verfügbarem Rechenbudget. Pilotversuche dienen ausschließlich zur Abschätzung dieser Größen und sollten von konfirmatorischen Tests getrennt werden.

### 14.2 Statistischer Analyseplan

Vor dem konfirmatorischen Experiment sollte ein Analyseplan festgelegt werden mit: primärem Endpunkt, Nullhypothese, Alternativhypothese, Signifikanzniveau, Effektgröße, Konfidenzintervall, Behandlung von Ausreißern und Umgang mit fehlgeschlagenen Läufen.

Je nach Design kommen in Betracht: t-Test, Welch-Test, Mann-Whitney-U, ANOVA, Mixed-Effects-Modelle, Permutationstests, Bootstrap-Konfidenzintervalle oder Bayes-Faktoren.

### 14.3 Kernmetriken

**Netzwerkdynamik:**
- Mean firing rate
- Spike count
- Burst index
- Synchrony
- Active neuron fraction
- Silent neuron fraction
- Inter-spike intervals

**Struktur:**
- Neuron count
- Synapse count
- Mean degree
- Degree distribution
- Clustering
- Path length
- Region connectivity

**Plastizität:**
- Weight distribution
- LTP/LTD ratio
- New synapses/tick
- Pruned synapses/tick
- Neurons generated/tick

**Ressourcen:**
- RAM
- CPU time/tick
- Spikes/second
- Synaptic updates/second
- Snapshot size
- Storage throughput

---

## 15. Experimentelle Designs

### 15.1 Experiment A – Dimensionalität

**Fragestellung:** Besitzt die fünfdimensionale Organisation einen funktionalen Vorteil?

**Bedingungen:**
- 2D, 3D, 4D, 5D, 6D
- randomisierte Kontrolltopologie

**Kontrollgrößen:** \(N\), \(S\), mittlerer Grad, Eingangsenergie, Lernrate, Stimulusanzahl.

**Primäre Metriken:** Recall, Retention, Lernrate, Generalisierung.
**Sekundäre Metriken:** Modularität, Clustering, Pfadlänge, Aktivitätssparsity, Energieaufwand.

**Nullhypothese:** \(H_{0,D}: Q_{5D} \leq Q_{controls}\)

### 15.2 Experiment B – Strukturelle Plastizität

Verglichen werden \(SP_{on}\) und \(SP_{off}\), wobei funktionale Gewichtsplastizität in beiden Bedingungen aktiv bleibt. Dadurch kann der spezifische Effekt von Synapsenbildung, Synapsenpruning und gegebenenfalls Neurogenese isoliert werden.

Gemessen werden: Lernleistung, Interferenz, Netzwerkgröße, Energiebedarf, Retention und Robustheit bei veränderten Aufgaben.

### 15.3 Experiment C – Language Organ

Vier Bedingungen sind vorgesehen:

| Bedingung | Beschreibung |
|-----------|--------------|
| **L0** | SNN ohne LLM |
| **L1** | LLM nur als Output-Decoder |
| **L2** | LLM als Encoder und Decoder |
| **L3** | LLM plus Knowledge Intake Engine |

Der entscheidende Test erfolgt anschließend im isolierten Zustand:

\[
L3 \rightarrow LLM_{off} \rightarrow Retrieval_{off} \rightarrow Recall
\]

Nur hierdurch kann überprüft werden, ob eine beobachtete Fähigkeit im SNN persistiert.

### 15.4 Experiment D – Continual Learning

Eine Sequenz von Aufgaben \(T_1, T_2, \ldots, T_k\) wird sukzessive trainiert. Nach jeder neuen Aufgabe werden frühere Aufgaben erneut getestet. Eine Forgetting-Metrik für Aufgabe \(i\):

\[
F_i = \max_{t < i} Q_i(t) - Q_i(k)
\]

Daraus können durchschnittliche Forgetting-, Transfer- und Retention-Werte berechnet werden.

### 15.5 Experiment E – Embodiment

Zwei Systeme mit möglichst gleicher neuronaler Architektur werden verglichen:

**Open Loop:** \(Stimulus \rightarrow SNN \rightarrow Response\)

**Closed Loop:** \(Environment \rightarrow Sensor \rightarrow SNN \rightarrow Action \rightarrow Environment\)

Untersucht werden: Lernstabilität, Adaptation, Generalisierung, Robustheit gegenüber Umweltänderungen und Repräsentationsstruktur.

---

## 16. Wissenschaftliche Ablationen und Nullhypothesen

### 16.1 Ablationen

\[
A_0: \text{vollständiges System}
\]
\[
A_1: \text{ohne STDP}
\]
\[
A_2: \text{ohne Homeostase}
\]
\[
A_3: \text{ohne strukturelle Plastizität}
\]
\[
A_4: \text{ohne Reward-Modulation}
\]
\[
A_5: \text{ohne LLM}
\]
\[
A_6: \text{LLM Monitoring only}
\]
\[
A_7: \text{ohne 5D-Lokalität}
\]
\[
A_8: \text{randomisierte Topologie}
\]

### 16.2 Nullhypothesen

\[
H_0^{5D}: \text{Die fünfdimensionale Organisation besitzt keinen messbaren Vorteil gegenüber einer geeigneten Kontrolltopologie.}
\]

\[
H_0^{SP}: \text{Strukturelle Plastizität verbessert die Lernleistung nicht.}
\]

\[
H_0^{LLM}: \text{Die beobachtete semantische Leistung stammt primär aus dem Language Organ und nicht aus dem SNN.}
\]

### 16.3 Falsifikationskriterien

| Hypothese | Falsifikation |
|-----------|---------------|
| **H1:** 5D-Lokalität verbessert selbstorganisierte Struktur | Wenn 5D-Netze gegenüber dimensionsreduzierten oder zufälligen Kontrollnetzen über mehrere Seeds keinen statistisch belastbaren Vorteil zeigen. |
| **H2:** Strukturelle Plastizität verbessert Continual Learning | Wenn Retention und Adaptationsleistung gegenüber statischer Topologie nicht steigen. |
| **H3:** Das SNN speichert externe Wissensinhalte | Wenn Recall nach Entfernung von LLM-Kontext und Retrieval-Zugriff auf Zufallsniveau fällt. |

---

## 17. Vergleichsbaselines

Brain-5D sollte langfristig nicht nur gegen sich selbst getestet werden:

- Statisches SNN
- SNN ohne 5D-Struktur
- Reservoir Computing
- Klassische rekurrente Netze
- Einfache Reinforcement-Learning-Agenten
- LLM-only-System
- Retrieval-Augmented LLM
- Randomisierte Netzwerke

---

## 18. Skalierbarkeit

### 18.1 Komplexitätsbetrachtung

Der theoretische Raum von \(50^5 = 312.500.000\) Neuronen verbietet eine naive objektorientierte Vollmaterialisierung. Angenommen, ein Neuron benötigt nur 128 Byte dynamischen Zustand:

\[
312.500.000 \times 128 \approx 40\,\text{GB}
\]

Bereits ohne Synapsen. Bei durchschnittlich \(k\) Synapsen pro Neuron gilt:

\[
S = N \cdot k
\]

Bei nur \(k=100\) entstünden \(31,25\) Milliarden Synapsen. Bei 16 Byte je Synapseneintrag: \(500\,\text{GB}\) Rohdaten.

### 18.2 Sparse Materialization

Der 5D-Hyperkubus sollte daher als **Adressraum** verstanden werden. Nur aktive beziehungsweise existente Neuronen werden materialisiert:

\[
\mathcal{N}_{active} \subset \mathcal{N}_{potential}
\]

Damit kann gelten: \(|\mathcal{N}_{active}| \ll |\mathcal{N}_{potential}|\).

### 18.3 Skalierungsgesetze

Für ereignisbasiertes Processing:

\[
T_{tick} = O(N_{active}) + O(S_{event}) + O(P_{plasticity}) + O(G_{structural})
\]

wobei \(N_{active}\): aktuell zu integrierende Neuronen, \(S_{event}\): durch aktuelle Spikes betroffene Synapsen, \(P_{plasticity}\): Plastizitätsoperationen, \(G_{structural}\): Growth-/Pruning-Prüfungen.

---

## 19. Validität und Reproduzierbarkeit

### 19.1 Validitätsdimensionen

**Interne Validität:** Ist der gemessene Unterschied tatsächlich durch die manipulierte Brain-5D-Komponente verursacht?

**Konstruktvalidität:** Misst eine verwendete Metrik tatsächlich das behauptete Konzept? (Spikezahl ≠ Intelligenz)

**Externe Validität:** Lassen sich Ergebnisse über Seeds, Netzwerkgrößen, Stimuli und Aufgaben hinweg reproduzieren?

**Ökologische Validität:** Bleiben beobachtete Fähigkeiten in kontinuierlichen oder verkörperten Umgebungen erhalten?

### 19.2 Reproduzierbarkeitsmetadaten

Jeder wissenschaftlich relevante Lauf sollte rekonstruierbar sein:

```text
experiment_id
git_commit
brain5d_version
configuration_hash
random_seed
rng_state
dataset_version
stimulus_version
network_schema
plasticity_schema
decoder_version
language_backend
hardware
operating_system
python_version
start_tick
end_tick
```

---

## 20. Erwartete Ergebnisse als konditionale Vorhersagen

Da Brain-5D noch keine ausreichende experimentelle Basis für quantitative Effektgrößen besitzt, werden zunächst qualitative gerichtete Vorhersagen formuliert:

### P1 – Homeostase
Bei aktivierter plastischer Hebb-Dynamik wird erwartet, dass zusätzliche Homeostase die Wahrscheinlichkeit extremer Aktivitätszustände reduziert.

### P2 – Structural Plasticity
Es wird erwartet, dass strukturelle Plastizität insbesondere bei veränderlichen Aufgaben eine bessere Anpassung der Netzwerktopologie ermöglicht.

### P3 – Dimensionalität
Falls zusätzliche funktionale Dimensionen einen Nutzen besitzen, sollte dieser sich bei gleichen Ressourcen als verbesserte Modularität, geringere Interferenz oder bessere Retention zeigen.

### P4 – Language Organ
Das LLM sollte die unmittelbare symbolische Kommunikationsleistung stark verbessern. Dies ist jedoch **kein Nachweis eines verbesserten SNN-Lernens**.

### P5 – Continual Learning
Unregulierte Hebb-Plastizität wird voraussichtlich stärkere Interferenz zeigen als Systeme mit Homeostase, struktureller Regulation oder Konsolidierungsmechanismen.

---

## 21. Limitationen

1. **Biologische Abstraktion:** Brain-5D simuliert keine vollständige Biochemie biologischer Nervenzellen. Izhikevich-, STDP- und Homeostasemodelle sind funktionale Abstraktionen.

2. **Skalierbarkeit:** Ein theoretischer Raum mit hunderten Millionen Neuronen bedeutet nicht, dass diese gleichzeitig in biologischer Detailtiefe simulierbar sind.

3. **Interpretierbarkeit:** Neuronale Zustände besitzen nicht automatisch eine für Menschen verständliche Semantik.

4. **Decoder-Bias:** Ein leistungsfähiger Decoder kann scheinbare Bedeutung erzeugen, die im SNN nicht vollständig vorhanden ist.

5. **LLM-Confounding:** Ein Language Organ besitzt bereits umfangreich extern gelerntes Wissen und stellt daher eine erhebliche Störvariable für Lernexperimente dar.

6. **Simulator-Realität:** Erfolg in einer digitalen Umgebung garantiert keinen Transfer auf physische Verkörperung.

7. **Long-Term Learning:** Sehr langfristige Continual-Learning-Eigenschaften können hohe Simulationszeiten und umfangreiche Experimente erfordern.

---

## 22. Ethische Dimension

Der derzeitige Stand von Brain-5D liefert keinen wissenschaftlichen Grund, dem System Empfindungsfähigkeit oder Leidensfähigkeit zuzuschreiben. Eine solche Behauptung wäre anthropomorph und nicht evidenzbasiert. Relevant sind zunächst konkretere Themen: autonome Systemaktionen, Fehlentscheidungen, Manipulation von Lerninputs, Datenherkunft, Datenschutz, Supply-Chain-Sicherheit externer Modelle, reproduzierbare Sicherheitsgrenzen und missbräuchliche Verwendung.

Das System sollte zwischen mindestens vier Autoritätsebenen unterscheiden:

\[
\text{Sensor} < \text{Interpreter} < \text{RuntimeController} < \text{SafetyController}
\]

Kein LLM darf den `SafetyController` überschreiben. Für reale Aktoren gilt:

\[
\text{ActionProposal} \rightarrow \text{PolicyCheck} \rightarrow \text{Actuator}
\]

---

## 23. Entwicklungsroadmap

### Alpha.6 – Morphological Stabilization
- Homeostasis
- Growth Budgets
- Structural Costs
- Anti-Oscillation
- Neuron/Synapse Age
- deterministische Contracts
- SignalFrame
- StimulusPlan
- LanguageOrgan Protocol

### Alpha.7 – Language Organ PoC
- lokales Backend
- asynchrone Queue
- Null-Backend
- Timeout
- Resource Limits
- Monitoring-only-Ablation

### v0.6 – Scaling & Knowledge Intake
- Sparse Storage
- Chunking
- Dirty Tracking
- Provenance
- KnowledgeItem
- SourceRecord
- Importer
- skalierbare Benchmarks

### v0.7 – Controlled Learning
- KnowledgeEpisode
- Train/Eval Isolation
- Delayed Reward
- Retention
- Contradiction Experiments
- Continual Learning

### v0.8 – Embodiment
- multimodale Sensoren
- Aktoren
- geschlossene Environment Loop
- multimodale zeitliche Synchronisation

### v0.9 – Memory and World Model
- episodische Gedächtnisstrukturen
- interne Zustandsvorhersage
- Sequenzrepräsentationen
- multimodale Assoziationen
- internes Weltmodell

---

## 24. Wissenschaftliche Hauptstruktur für zukünftige Ausarbeitung

### Kapitel 1 – Introduction
- Motivation, Problemstellung, Forschungslücke, Forschungsfrage, Beiträge, Aufbau

### Kapitel 2 – Theoretical Background
- Computational Neuroscience, dynamische Systeme, Spiking Models, synaptische Plastizität, Structural Plasticity, Homeostasis, Memory, Continual Learning, Embodied Cognition, Neuro-Symbolic AI, LLMs

### Kapitel 3 – Related Work
- SNN-Simulatoren, neuromorphe Systeme, Reservoir Computing, strukturell adaptive Netze, embodied agents, hybride LLM-Systeme

### Kapitel 4 – Brain-5D Architecture
- 5D Topology, Neuron Model, Synapses, Plasticity, Persistence, Language Organ, Knowledge Intake, Embodiment

### Kapitel 5 – Methodology
- Forschungsdesign, Hypothesen, Variablen, Metriken, Seeds, Statistik, Reproduzierbarkeit

### Kapitel 6 – Experiments
- Dimensionality, Plasticity, Memory, Continual Learning, Language Organ, Embodiment, Scaling

### Kapitel 7 – Results
- Strikte Ergebnisdarstellung ohne nachträgliche theoretische Überinterpretation

### Kapitel 8 – Discussion
- Interpretation, Alternativerklärungen, Vergleich mit Literatur, Limitationen, theoretische Bedeutung

### Kapitel 9 – Conclusions
- bestätigte Ergebnisse, verworfene Hypothesen, wissenschaftlicher Beitrag, offene Fragen

---

## 25. Literaturstrategie

Die Literaturbasis sollte nicht nach einer vorgegebenen Mindestanzahl von Publikationen aufgebaut werden. Stattdessen wird eine **Coverage Matrix** verwendet. Für jeden zentralen Brain-5D-Mechanismus werden erfasst: Grundlagen, Schlüsselarbeiten, Reviews und aktuelle Arbeiten.

Eine Literaturrecherche gilt als ausreichend, wenn die Argumentationskette vollständig belegt ist, nicht wenn eine bestimmte Zahl erreicht wurde.

### Initiale Literaturbasis

**Neuronendynamik und SNN:**
- Izhikevich, E. M. (2003). Simple Model of Spiking Neurons. IEEE Transactions on Neural Networks.
- Izhikevich, E. M. (2007). Dynamical Systems in Neuroscience. MIT Press.
- Gerstner, W., Kistler, W. M., Naud, R., & Paninski, L. (2014). Neuronal Dynamics. Cambridge University Press.

**STDP und Plastizität:**
- Bi, G. Q., & Poo, M. M. (1998). Spike-timing-dependent synaptic modification.
- Song, S., Miller, K. D., & Abbott, L. F. (2000). Competitive Hebbian learning through spike-timing-dependent synaptic plasticity.
- Morrison, A., Diesmann, M., & Gerstner, W. (2008). Phenomenological models of synaptic plasticity based on spike timing.
- Zenke, F., Hennequin, G., & Gerstner, W. (2013). Synaptic plasticity in neural networks needs homeostasis with a fast rate detector.

**Structural Plasticity:**
- Holtmaat, A., & Svoboda, K. (2009). Experience-dependent structural synaptic plasticity in the mammalian brain.

**Continual Learning:**
- Kirkpatrick, J. et al. (2017). Overcoming catastrophic forgetting in neural networks.
- Zenke, F., Poole, B., & Ganguli, S. (2017). Continual Learning Through Synaptic Intelligence.
- Parisi, G. I. et al. (2019). Continual lifelong learning with neural networks: A review.

**Memory:**
- Squire, L. R. (2004). Memory systems of the brain: A brief history and current perspective.
- Squire, L. R., & Wixted, J. T. (2011). The cognitive neuroscience of human memory since H.M.

**Predictive Processing:**
- Rao, R. P. N., & Ballard, D. H. (1999). Predictive coding in the visual cortex.
- Friston, K. (2010). The free-energy principle: a unified brain theory?

**Embodied Cognition:**
- Pfeifer, R., & Bongard, J. (2006). How the Body Shapes the Way We Think.

**Simulation:**
- Stimberg, M., Brette, R., & Goodman, D. F. M. (2019). Brian 2, an intuitive and efficient neural simulator.

---

## 26. Schlussfolgerung

Brain-5D sollte nicht primär als Versuch verstanden werden, ein weiteres Large Language Model zu bauen. Ebenso wenig ist es lediglich ein großer SNN-Simulator. Der wissenschaftlich interessante Teil liegt in der Kombination von Zeit, Topologie, Plastizität, Persistenz, Verkörperung und kontrollierter Symbolkopplung.

Das Language Organ stellt eine Brücke zur bestehenden symbolischen Welt dar, darf jedoch die zu untersuchende neuronale Dynamik nicht verdecken. Die wichtigste methodische Forderung lautet:

> **Jede beobachtete Fähigkeit muss daraufhin untersucht werden, wo sie tatsächlich entsteht.**

Liegt sie im Sprachmodell? Im Decoder? Im Retrieval-System? In handgeschriebenen Regeln? Oder lässt sie sich auch nach Isolation dieser Komponenten im Zustand und Verhalten des SNN nachweisen?

Die langfristige Bedeutung des Projekts wird nicht daran gemessen werden, ob das System überzeugend sprechen kann. Sie wird daran gemessen werden müssen, ob experimentell nachweisbar ist, dass sein neuronales Substrat **selbst persistente, adaptive und generalisierbare interne Strukturen ausbildet**.

Damit verschiebt sich Brain-5D von einem komplexen Architekturprojekt zu einer experimentellen Forschungsplattform. Das Ziel ist nicht, eine gewünschte Theorie zu bestätigen, sondern ein System zu schaffen, an dem sich die zugrunde liegenden Hypothesen **reproduzierbar prüfen, vergleichen und gegebenenfalls widerlegen lassen**.

---

**Heisig, T. et al.**
*Brain-5D: A Hybrid Spatial Spiking Architecture for Self-Organizing and Embodied Cognitive Systems.*
Experimental Research Framework, Brain-5D Project, 2026.

*Hinweis: Die endgültige bibliografische Form sollte erst bei einer formalen Veröffentlichung mit stabiler Version, DOI beziehungsweise archiviertem Release festgelegt werden.*

zu ergänzende inhalte

Was ich noch ergänzen würde
Ergänzung	Zweck	spätere Vertiefung
Scope & Non-Scope	verhindert überzogene Interpretation	kurz
Terminologie/Ontologie	definiert Neuron, Region, Episode, Repräsentation usw.	eigenes Kapitel
Architecture Invariants	trennt unveränderliche Prinzipien von Implementierungsdetails	technisch vertiefen
Mathematische Annahmen	kennzeichnet Arbeitsgleichungen vs. hergeleitete Modelle	stark vertiefen
Stabilität/Dynamik	Attraktoren, Bifurkationen, kritische Regime	eigenes Fachpapier
Informationsmaß	Entropie, Mutual Information, Decodability	eigenes Fachpapier
Graphentheorie	5D-Topologie wissenschaftlich messbar machen	eigenes Fachpapier
Storage/Digital Twin	Verbindung zum bereits entwickelten 5D-Speicherkonzept	eigenes Fachpapier
Experiment Registry	Hypothese → Versuch → Ergebnis → Evidenzstufe	mit Software koppeln
Open Questions	trennt ungelöste Fragen von Behauptungen	fortlaufend

Besonders wichtig wäre außerdem eine Statusnotation direkt im Papier. Beispielsweise:

[E0 | HYPOTHESIS] 5D-Lokalität kann funktionale Modularisierung begünstigen.
[E1 | IMPLEMENTED] Neuronen besitzen fünf Koordinatenwerte.
[E2 | VALIDATED] Homeostase reduziert unter Benchmark X die Varianz der Populationsrate.
[E3 | SYSTEM] Der Effekt bleibt in Closed-Loop-Experiment Y über mehrere Seeds erhalten.

Damit könnte das Dokument mit dem Projekt mitwachsen, ohne dass ältere theoretische Aussagen später fälschlicherweise wie experimentelle Ergebnisse aussehen.

Eine wichtige fachliche Korrektur

Abschnitt 9.2 „Überwachen“ würde ich ändern. Dort steht derzeit sinngemäß:

Das LLM generiert einen Monitoring-Bericht, der als zusätzlicher Input zurück ins SNN gespeist wird.

Das kollidiert teilweise mit der zuvor sauber aufgebauten kausalen Trennung. Ein LLM-Monitoring-Bericht, der wieder ins SNN eingespeist wird, ist kein reines Monitoring mehr, sondern eine Intervention.

Ich würde daraus zwei strikt getrennte Pfade machen:

SNN→SignalFrame→Monitor→Logging

und optional:

SignalFrame→LLM→FeedbackProposal→PolicyGate→StimulusPlan→SNN

Damit kann ein LLM niemals allein entscheiden, dass seine Interpretation wieder neuronalen Input erzeugt.

Zusätzlich würde ich Kapitel 5 noch mathematisch öffnen

Derzeit ist die gewichtete euklidische Metrik:

d
ij
	​

=
k=1
∑
5
	​

λ
k
	​

(p
ik
	​

−p
jk
	​

)
2
	​


praktisch sinnvoll, aber sie darf nicht unbemerkt zu einer Grundannahme der gesamten 5D-Theorie werden.

Besser wäre:

d
ij
	​

=d
M
	​

(p
i
	​

,p
j
	​

)

mit einer allgemeinen Metrik beziehungsweise Metrikmatrix

d
M
	​

(p
i
	​

,p
j
	​

)=
(p
i
	​

−p
j
	​

)
T
M(p
i
	​

−p
j
	​

)
	​

.

Die bisherige Formel ist dann der Spezialfall einer diagonalen Matrix

M=diag(λ
x
	​

,λ
y
	​

,λ
z
	​

,λ
a
	​

,λ
b
	​

).

Damit kann später untersucht werden, ob beispielsweise a und b miteinander gekoppelt sind oder ob das Netzwerk seine effektive Geometrie sogar lernen kann.

Das führt zu einer deutlich interessanteren Forschungsfrage:

Ist 5D lediglich ein Adressraum oder entwickelt das Netzwerk eine funktionale Geometrie?
	​


Das könnte langfristig einer der wissenschaftlich interessanteren Teile von Brain-5D werden.

Ein weiteres Kapitel würde ich unbedingt einfügen

Zwischen den jetzigen Kapiteln 13 und 14 würde ich einen Abschnitt „Messbare Emergenz und Kausalität“ aufnehmen.

Darin sollte festgelegt werden, dass „Emergenz“ keine Erklärung darstellt. Ein emergentes Phänomen Y müsste mindestens:

Y=f(X
1
	​

,…,X
n
	​

)

aus lokalen Prozessen entstehen, ohne als direkte globale Regel implementiert worden zu sein.

Für Brain-5D könnten drei Stufen definiert werden:

Strukturelle Emergenz: Nicht vorgegebene Cluster, Regionen oder Verbindungsmuster entstehen.

Dynamische Emergenz: Nicht explizit programmierte Oszillationen, Aktivitätssequenzen, metastabile Zustände oder Attraktoren entstehen.

Funktionale Emergenz: Ein nicht direkt programmierter Netzwerkzustand verbessert messbar eine Aufgabe oder beeinflusst Verhalten.

Dann lässt sich mit Ablationen testen:

do(C=0)⇒ΔQ

also beispielsweise: Wird ein spontan entstandenes Cluster C deaktiviert und sinkt anschließend die Leistung Q, besitzt das Cluster zumindest Hinweise auf funktionale Relevanz.

Auch „World Model“ würde ich vorsichtiger formulieren

In der Roadmap steht für v0.9 bereits:

internes Weltmodell

Das ist für eine Roadmap okay, wissenschaftlich würde ich aber schreiben:

„candidate internal predictive state model“

beziehungsweise deutsch:

„Kandidat für ein internes prädiktives Zustandsmodell“

Ein echtes World Model sollte erst angenommen werden, wenn das System beispielsweise

s
^
t+1
	​

=f(s
t
	​

,a
t
	​

)

erzeugen kann und nachgewiesen wird, dass

s
^
t+1
	​


Information über einen zukünftigen Umweltzustand enthält, die nicht einfach aus dem aktuellen Sensorinput kopiert wurde.

Damit ergibt sich eine sinnvolle Dokumenthierarchie

Ich würde dieses Dokument künftig nicht immer größer machen. Es sollte das wissenschaftliche Stamm- bzw. Vordokument bleiben:

Brain-5D Scientific Framework
│
├── 01 Mathematical Foundations
│   ├── Hybrid Dynamical Systems
│   ├── Stability
│   ├── Bifurcation
│   └── Mean-Field Models
│
├── 02 5D Geometry
│   ├── Metric Space
│   ├── Learned Geometry
│   ├── Graph Topology
│   └── Dimensional Ablation
│
├── 03 Neural Dynamics
│
├── 04 Plasticity & Homeostasis
│
├── 05 Structural Plasticity & Neurogenesis
│
├── 06 Representation & Information Theory
│
├── 07 Memory & Continual Learning
│
├── 08 Language Organ
│
├── 09 Knowledge Intake
│
├── 10 Embodiment
│
├── 11 Storage & 5D Digital Twin
│
├── 12 Experimental Methodology
│
├── 13 Scaling & Performance
│
├── 14 Safety & Ethics
│
└── 15 Results & Evidence Registry

Das Vordokument sagt dann jeweils was untersucht wird, warum es untersucht wird und wie die Teile zusammenhängen. Die Unterdokumente beantworten anschließend mathematisch und experimentell wie genau.

Ein weiterer Vorteil: Wir können im Hauptdokument Aussagen wie

„siehe Brain-5D Mathematical Foundations: Stability and Hybrid Dynamics, §4“

verwenden, statt Stabilitätsanalyse, STDP-Theorie, Informationsgeometrie und Statistik jedes Mal erneut aufzuführen.

Status des jetzigen Dokuments

Ich würde es deshalb nicht mehr als bloßen Entwurf betrachten, sondern als:

Brain-5D Scientific Framework – Preliminary Research Architecture, Version 0.x

mit einem ausdrücklichen Hinweis:

This document defines the preliminary scientific framework of Brain-5D. Individual theoretical, mathematical, computational and experimental components remain subject to dedicated analysis, validation and revision. Statements concerning expected system properties constitute research hypotheses unless explicitly marked as experimentally validated.

Das ist für ein Fachpublikum wesentlich stärker als der Versuch, bereits jetzt den Eindruck einer fertigen Theorie zu erzeugen.

Und genau daraus können wir anschließend die einzelnen Vertiefungen entwickeln: 5D-Geometrie → mathematische Dynamik → Neuronen/Synapsen → Plastizität → Repräsentation → Gedächtnis → Storage → Language Organ → Embodiment → Methodik. Jede Vertiefung kann später eigenständig zitier- und veröffentlichungsfähig werden, während dieses Dokument die gemeinsame wissenschaftliche Klammer bleibt.
