# Brain-5D: Eine hybride neural-symbolische Architektur für verkörperte kognitive Systeme

## Status und Zukunftsperspektive

---

## Zusammenfassung

Brain-5D ist ein experimentelles Forschungsframework, das ein **5D-Spiking-Neural-Network (SNN)** mit einer neuartigen, kontrollierten Kopplung an ein **Large Language Model (LLM)** als sprachliches Organ verbindet. Das System verfolgt das übergeordnete Ziel, eine **verkörperte, selbstorganisierende Intelligenz** zu schaffen, bei der das SNN als eigenständiger Lernender agiert, während das LLM als Übersetzer, Monitor und semantische Brücke zwischen der subsymbolischen Spike-Welt und der symbolischen Außenwelt fungiert. Dieser Beitrag beschreibt den aktuellen Entwicklungsstand (v0.5.0-alpha.5), die zugrundeliegenden biologisch inspirierten Lernmechanismen und die geplante Architektur für eine hybride neural-symbolische Kognition.

---

## 1. Einleitung

### 1.1 Motivation

Die Künstliche Intelligenz steht vor einer fundamentalen Herausforderung: Während Large Language Models (LLMs) beeindruckende symbolische Verarbeitungs- und Sprachfähigkeiten zeigen, bleiben sie im Kern statistische Mustererkennungssysteme ohne genuine Verkörperung, ohne intrinsische Lernfähigkeit und ohne ein Verständnis von Zeit, Kausalität und physikalischer Realität. Spiking Neural Networks (SNNs) hingegen bieten biologisch plausible Dynamiken, temporale Kodierung und plastizitätsgetriebenes Lernen, stoßen jedoch bei symbolischen Abstraktionen und sprachlicher Interaktion an ihre Grenzen.

Brain-5D adressiert diese komplementären Stärken und Schwächen durch eine **hybride neural-symbolische Architektur**, die das SNN als primäre, sich selbstorganisierende Intelligenz etabliert und das LLM als kontrolliertes, austauschbares Organ für Übersetzung, Monitoring und semantische Ein- und Ausgabe integriert.

### 1.2 Stand der Forschung

Die Forschung zu hybriden SNN-LLM-Architekturen gewinnt zunehmend an Bedeutung. Aktuelle Arbeiten wie **EMBER (Experience-Modulated Biologically-inspired Emergent Reasoning)** zeigen, dass die Integration eines LLM mit einem persistenten, biologisch fundierten assoziativen Substrat (einem SNN mit STDP) emergentes Reasoning und autonome Interaktion ohne externes Prompting ermöglichen kann. Diese Architekturen platzieren das LLM nicht als zentrale Steuerung, sondern als austauschbares Reasoning-Engine innerhalb eines biologisch inspirierten Grundgerüsts.

Brain-5D geht über diese Ansätze hinaus, indem es eine **strikte kausale Geschlossenheit** des SNN gegenüber dem LLM durchsetzt – das LLM hat keinen direkten Zugriff auf synaptische Gewichte, strukturelle Plastizität oder den Runtime-Loop.

---

## 2. Systemarchitektur

### 2.1 Überblick

Die Architektur von Brain-5D folgt einer strikten Schichtenlogik mit klar definierten Verantwortlichkeiten und Schnittstellen:

```
                         EXTERNE WELT
                Text / später Bild / Audio / Web
                              │
                              ▼
                    ┌───────────────────┐
                    │ Embodiment Layer  │
                    │ Sensor / Actuator │
                    └─────────┬─────────┘
                              │
              ┌───────────────▼────────────────┐
              │       LLM / Language Organ      │
              │                                 │
              │  LanguageModelBackend           │
              │  Translator                     │
              │  SemanticEncoder                │
              │  SemanticDecoder                │
              │  MonitoringInterpreter          │
              └───────┬─────────────────▲───────┘
                      │                 │
             semantic │                 │ SignalFrame
              intent  │                 │
                      ▼                 │
              ┌───────────────────────────────┐
              │       Signal Bridge           │
              │                               │
              │ Text → StimulusPlan           │
              │ Spike data → SignalFrame      │
              │ Channels / Regions / Timing   │
              └───────────────┬───────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │    Brain-5D SNN  │
                    │                  │
                    │ learning         │
                    │ homeostasis      │
                    │ self-org         │
                    │ memory           │
                    └────────┬─────────┘
                             │
                             ▼
                      eigene Entwicklung
```

### 2.2 Das Spiking Neural Network (SNN)

Das Kernsystem von Brain-5D basiert auf dem **Izhikevich-Neuronenmodell**, das eine Balance zwischen biologischer Plausibilität und rechnerischer Effizienz bietet. Die Membrandynamik eines einzelnen Neurons wird durch zwei gekoppelte Differentialgleichungen beschrieben:

\[
\frac{dV}{dt} = 0.04V^2 + 5V + 140 - u + I
\]

\[
\frac{du}{dt} = a(bV - u)
\]

mit der Spike-Bedingung: wenn \( V \geq 30 \, \text{mV} \), dann \( V \leftarrow c \) und \( u \leftarrow u + d \).

Die Parameter \( a, b, c, d \) erlauben die Nachbildung verschiedener kortikaler Neuronentypen:
- **Regular Spiking (RS)**: \( a = 0.02, b = 0.2, c = -65, d = 8 \)
- **Fast Spiking (FS)**: \( a = 0.1, b = 0.2, c = -65, d = 2 \)
- **Intrinsically Bursting (IB)**: \( a = 0.02, b = 0.2, c = -55, d = 4 \)
- **Chattering (CH)**: \( a = 0.02, b = 0.2, c = -50, d = 2 \)

### 2.3 Die Signal Bridge

Die Signal Bridge ist eine **deterministische Transformationsschicht**, die Spike-Zeitreihen in strukturierte, beschreibbare Merkmale überführt. Sie verhindert, dass das LLM Rauschen als Bedeutung interpretiert, und stellt sicher, dass die vom SNN erzeugte Information messbar und nachvollziehbar bleibt.

Ein **SignalFrame** fasst die relevanten Merkmale eines Zeitfensters zusammen:

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

Dieser Frame wird vom LLM interpretiert – nicht die interne neuronale Datenstruktur. Die handgeschriebene Feature-Extraktion kann später durch einen lernenden SNN-Decoder ersetzt werden, der die Bedeutung direkt aus den Spike-Mustern extrahiert.

---

## 3. Lernmechanismen

Brain-5D implementiert drei zentrale, biologisch inspirierte Plastizitätsmechanismen, die das Netzwerk zur Selbstorganisation befähigen.

### 3.1 Spike-Timing-Dependent Plasticity (STDP)

STDP ist der primäre Mechanismus für **synaptische Gewichtsveränderung**. Die Gewichtsänderung \( \Delta w \) hängt von der zeitlichen Differenz \( \Delta t = t_{\text{post}} - t_{\text{pre}} \) zwischen präsynaptischem und postsynaptischem Spike ab:

\[
\Delta w =
\begin{cases}
A_+ \cdot \exp(-\Delta t / \tau_+) & \text{für } \Delta t > 0 \text{ (Potenzierung)} \\
-A_- \cdot \exp(\Delta t / \tau_-) & \text{für } \Delta t < 0 \text{ (Depression)}
\end{cases}
\]

Diese Hebb'sche Lernregel verstärkt Verbindungen, bei denen präsynaptische Aktivität konsistent postsynaptische Spikes vorhersagt.

### 3.2 Homeostatische Plastizität

Die homöostatische Plastizität reguliert die **Gesamtfeuerrate** und die **Erregbarkeit** von Neuronen, um Instabilität und Ausreißer zu verhindern. Sie wirkt als globaler Regelkreis, der die Aktivität des Netzwerks in einem physiologisch plausiblen Bereich hält.

In Brain-5D umfasst dies:
- **Skalierung der Eingangsgewichte** basierend auf der durchschnittlichen Feuerrate
- **Anpassung der intrinsischen Erregbarkeit** (Parameter \( a, b \))
- **Regulation der Spikeschwellen** zur Vermeidung von Explodier- oder Erstarreffekten

### 3.3 Strukturelle Plastizität

Die strukturelle Plastizität simuliert das **Wachstum und die Beschneidung (Pruning) von Synapsen** – einen Mechanismus, der in biologischen Netzwerken kontinuierlich wirkt.

Brain-5D implementiert:
- **Neurogenese**: Bildung neuer synaptischer Verbindungen basierend auf Aktivitätsmustern
- **Pruning**: Entfernung schwacher oder inaktiver Verbindungen zur Ressourcenoptimierung
- **Altersverfolgung** von Neuronen und Synapsen für entwicklungsbezogene Entscheidungen
- **Wachstumsbudgets** zur Begrenzung der strukturellen Expansion

Die strukturelle Plastizität ermöglicht dem Netzwerk, sich **topologisch** an neue Anforderungen anzupassen – ein entscheidender Vorteil gegenüber rein gewichtsbasierten Lernverfahren.

---

## 4. Das Language Organ: Integration eines LLM als kontrollierte Komponente

### 4.1 Design-Prinzipien

Die Integration eines LLM in Brain-5D folgt sieben grundlegenden **Verboten bzw. Grenzen**【aus der bereitgestellten Datei】:

1. Kein direkter Zugriff des LLM auf `synapse.weight`
2. Kein direkter Zugriff auf `StructuralPlasticityEngine.apply_*`
3. Kein eigenständiges `network.step()`
4. Kein beliebiger Python-/Shell-Code aus einer LLM-Ausgabe
5. Kein direkter Web-Inhalt → Synapse
6. Keine LLM-Antwort als „Fakt“ ohne Provenance
7. Ausfall oder Timeout des LLM darf das SNN nicht stoppen

Diese Prinzipien stellen sicher, dass **das Language Organ niemals Eigentümer des Brain-5D Runtime Loops wird**. Der `RuntimeController` behält die vollständige Kontrolle über den Simulationsablauf. Das LLM arbeitet asynchron und seine Ausgaben werden als **Input-Daten** behandelt.

### 4.2 Funktionen des Language Organs

Das LLM übernimmt drei klar definierte, nicht-invasive Funktionen:

**1. Füttern (Semantische Brücke nach innen)**
Das LLM kodiert externe, symbolische Eingaben (menschliche Sprache, Instruktionen) in strukturierte Spike-Muster für den Input-Layer des SNN. Diese Übersetzung erfolgt über den **SemanticEncoder**, der eine symbolische Anfrage in einen **StimulusPlan** (Zeit, Region, Rate, Muster) transformiert.

**2. Übersetzen (Semantische Brücke nach außen)**
Das LLM dekodiert die Spike-Muster des Output-Layers (als **SignalFrame**) in natürliche Sprache oder Handlungsanweisungen. Der **SemanticDecoder** erzeugt eine interpretierbare Beschreibung der Netzwerkaktivität.

**3. Überwachen (Homöostatische Rückkopplung)**
Das LLM generiert auf Basis seiner Dekodierung einen **Monitoring-Bericht**, der als zusätzlicher Input zurück ins SNN gespeist wird. Das SNN kann diesen Bericht in seine eigene, autonome Entscheidungsfindung einfließen lassen – oder ignorieren.

### 4.3 Modellwahl: Qwen2.5-0.5B-Instruct

Als Referenzmodell für das Language Organ wurde **Qwen2.5-0.5B-Instruct** ausgewählt. Mit rund **0,49 Milliarden Parametern** und einer **Q4_K_M-Quantisierung** (ca. 350 MB) ist es für den Betrieb auf Consumer-Hardware und Edge-Geräten optimiert.

Die wichtigsten Eigenschaften:
- **Mehrsprachige Unterstützung** (29+ Sprachen)
- **Kontextlänge** von bis zu 128K Tokens (mit RoPE)
- **GGUF-Format** für effiziente CPU-Inferenz mit `llama-cpp-python`
- **Instruction-Tuning** für strukturierte Ausgaben

Ein **austauschbarer LanguageModelBackend** abstrahiert das konkrete Modell:
```
LanguageModelBackend
 ├── LlamaCppBackend
 │     ├── Qwen2.5 GGUF
 │     ├── Granite Nano GGUF (350M/1B)
 │     └── andere llama.cpp-kompatible Modelle
 └── NullLanguageBackend
```

Die **NullLanguageBackend**-Implementierung ermöglicht Tests mit exakt derselben Architektur ohne LLM – eine wissenschaftlich unerlässliche Kontrollbedingung.

---

## 5. Knowledge Intake Engine: Kontrollierter Zugang zur Außenwelt

### 5.1 Motivation

Ein zentrales wissenschaftliches Problem bei der Integration von LLMs ist die **Ununterscheidbarkeit von gelerntem und geliefertem Wissen**. Wenn das System eine Frage beantwortet, kann dies auf drei unterschiedlichen Quellen beruhen:
1. **Intern gelernte Repräsentation** im SNN (Plastizität)
2. **Statistisches Muster** aus dem LLM (Halluzination oder Trainingsdaten)
3. **Kombination** beider Quellen

Die Knowledge Intake Engine adressiert dieses Problem durch eine **strikte Trennung von externem Wissen und internem Lernen**.

### 5.2 Architektur

```
Internet / Wikipedia / lokale Dokumente
                │
                ▼
       Knowledge Intake Engine
                │
        ┌───────┴────────┐
        │ Source Fetcher │
        │ Provenance     │
        │ Deduplication  │
        │ Validation     │
        │ Chunking       │
        └───────┬────────┘
                │
                ▼
          KnowledgeItem
                │
                ▼
        Language Organ
                │
                ▼
        LearningStimulus
                │
                ▼
             Brain-5D
```

### 5.3 Provenance und Nachvollziehbarkeit

Jeder Wissenseintrag durchläuft eine **Provenienzkette**【aus der bereitgestellten Datei】:

- **SourceRecord**: Quelle (URL, Zeile, Zeitstempel, Hash)
- **KnowledgeItem**: Inhalt + Quelle + Vertrauensstatus
- **LearningStimulus**: Aus KnowledgeItem generierter Spike-Reiz
- **SNN-Aktivität**: Netzwerkantwort auf den Stimulus
- **SignalFrame-Interpretation**: Dekodierung der SNN-Antwort
- **Systemantwort**: Finale Ausgabe

Diese durchgängige Rückverfolgbarkeit ermöglicht es, **jede Antwort auf ihre Herkunft zurückzuführen** – eine wissenschaftliche Grundvoraussetzung für die Validierung von Lernprozessen.

### 5.4 Das zentrale Experiment: Echtes Lernen vs. Retrieval

Der wissenschaftliche Kern der Knowledge Intake Engine ist das folgende Experiment【aus der bereitgestellten Datei】:

```
Wikipedia:
    "Paris ist die Hauptstadt Frankreichs."
                 │
                 ▼
        Knowledge Intake Engine
                 │
                 ▼
          LearningStimulus
                 │
                 ▼
              SNN lernt
                 │
          Internet trennen
          LLM-Kontext leeren
                 │
                 ▼
     Frage erneut einspeisen
                 │
                 ▼
           SNN-Aktivität
                 │
                 ▼
        Signal Interpreter
                 │
                 ▼
     "Paris" / richtige Antwort?
```

**Erst wenn dieser letzte Schritt ohne erneuten Abruf der Quelle funktioniert, darf das System als „lernend“ bezeichnet werden.** Dieses experimentelle Design ist die methodologische Grundlage für die Evaluierung von Brain-5D.

---

## 6. Vergleich mit bestehenden Ansätzen

### 6.1 EMBER (Experience-Modulated Biologically-inspired Emergent Reasoning)

EMBER integriert ein 220.000-Neuronen-SNN mit STDP in eine hybride LLM-Architektur. Im Gegensatz zu Brain-5D wird das LLM bei EMBER als "austauschbare Reasoning-Engine" innerhalb eines persistenten, biologisch fundierten assoziativen Substrats positioniert.

Brain-5D geht einen Schritt weiter: Es etabliert das SNN als **kausal geschlossenes System** und das LLM als **reines Organ ohne Schreibrechte**. Während EMBER das LLM als Reasoning-Engine nutzt, bleibt in Brain-5D die gesamte Entscheidungsfindung und Plastizität dem SNN vorbehalten.

### 6.2 Neuro-Symbolische Systeme

Neuro-symbolische Architekturen kombinieren neuronale Netze mit symbolischen Repräsentationen. Brain-5D unterscheidet sich durch:
- **Temporale Kodierung** (Spikes) statt Ratenkodierung
- **Plastizitätsgetriebenes Lernen** statt Backpropagation
- **Strikte Trennung** zwischen subsymbolischer (SNN) und symbolischer (LLM) Ebene
- **Verkörperung** als zentrales Design-Prinzip

### 6.3 Embodied AI

Die Embodied-AI-Forschung betont die enge **Wahrnehmungs–Kognitions–Handlungs-Kopplung**【aus der bereitgestellten Datei】. Brain-5D realisiert dies durch:
- **Sensorische Input-Kanäle** (Text, später Bild, Audio, taktil)
- **Motorische Output-Kanäle** (Text, Sprache, Aktuatoren)
- **Geschlossene Wahrnehmungs-Handlungs-Schleife**
- **Kontinuierliches, online Lernen** durch Plastizität

---

## 7. Roadmap und Zukunftsperspektive

### 7.1 Entwicklungsstufen

Die geplante Evolution von Brain-5D folgt einer gestaffelten Roadmap【aus der bereitgestellten Datei】:

```
alpha.5
Persistent Structural Plasticity
        ↓
alpha.6
Morphological Stabilization
+ Language/Signal Contracts
        ↓
alpha.7
Local LLM Organ PoC
        ↓
v0.6
Scaling
+ Knowledge Intake Engine
        ↓
v0.7
Knowledge Learning Experiments
        ↓
v0.8
Real Embodiment
        ↓
v0.9
Memory / World Model
```

### 7.2 Alpha.6: Structural Stabilization + Cognitive Bridge Contracts

Diese Stufe etabliert die **Schnittstellen** für das künftige Language Organ, ohne bereits ein LLM zu laden:
- Chronische Homeostasis-Signale
- Growth Budgets / Structural Costs
- Anti-Oszillation Neurogenese ↔ Pruning
- Neuron/Synapse Age Tracking
- LanguageOrgan Protocol
- LanguageModelBackend Protocol
- SignalFrame / StimulusPlan Definitionen
- Dashboard-Platzhalter "Language Organ"

**Das LLM bleibt in dieser Stufe vollständig deaktiviert per Default.**

### 7.3 Alpha.7: Local Language Organ PoC

Diese Stufe implementiert das Language Organ als **optionales Plugin**:
- `llama.cpp`/`llama-cpp` Backend
- Qwen2.5-0.5B-Instruct GGUF als Referenzmodell
- Austauschbarer Granite-Nano-Test
- Kein `transformers`-Zwang
- CPU-Inferenz
- Separater Worker-Thread / Queue
- Timeouts und Ressourcenlimits
- Modellfehler dürfen Simulation nicht stoppen

Die **vergleichende Evaluation** umfasst:
- SNN ohne LLM (Kontrollgruppe)
- SNN mit passivem LLM (nur Monitoring)
- SNN mit I/O-Brücke (aktive Übersetzung)

### 7.4 V0.6: Scaling & Knowledge Intake Foundation

Diese Stufe skaliert das System und etabliert die Knowledge Intake Engine:
- Dirty Tracking für effiziente Snapshots
- Chunked Storage für große Netzwerke
- Parallel Domains für multi-task Lernen
- 50k → 500k → 1M Neuronen-Benchmarks
- KnowledgeItem Contract
- SourceRecord / Provenance
- Knowledge Intake Queue
- Lokaler Text-/Markdown-Importer
- Wikipedia Adapter
- Deduplication und Learning-Session Attribution

### 7.5 V0.7: Deterministic Learning Environment + Knowledge Learning

Diese Stufe führt **kontrollierte Lern-Experimente** durch:
- Episoden-basiertes Lernen
- Train/Eval Split
- Delayed Rewards
- Continual Learning Retention
- KnowledgeEpisode: Frage → Recherche → Lernreiz → Test
- Wissensabruf ohne erneuten Internetzugriff
- Retention nach 1k / 10k / 100k Ticks
- Widerspruchsexperimente
- Quellenwechsel-Experimente

### 7.6 V0.8: Production Embodiment

Die finale Embodiment-Stufe vereinheitlicht alle Modalitäten:
- TextSensor, CameraSensor, AudioSensor, TactileSensor, EnvironmentSensor
- Motor Actuator, Text/Speech Actuator
- SignalFrame für alle Modalitäten
- LLM-Organ nur für semantische Modalitäten
- Rohsensorik nicht grundsätzlich durch LLM schicken
- Geschlossene Perception-Action Loop

---

## 8. Diskussion

### 8.1 Wissenschaftliche Einordnung

Brain-5D repräsentiert einen **Paradigmenwechsel** in der hybriden KI-Forschung: Statt das LLM als zentrale Intelligenz zu positionieren und das SNN als peripheres Modul zu behandeln, kehrt die Architektur die Hierarchie um. Das SNN ist das **primäre, lernende Subjekt**; das LLM ist ein **kontrolliertes Organ** für spezifische Übersetzungs- und Interpretationsaufgaben.

Diese Entscheidung ist wissenschaftlich fundiert: Sie ermöglicht die **Isolation** der Lernmechanismen des SNN von den statistischen Mustern des LLM und schafft damit die Voraussetzung für **valide Experimente** zum Thema "echtes Lernen".

### 8.2 Herausforderungen

Die zentrale Herausforderung bleibt die **Latenz-Diskrepanz**: Das SNN operiert im Millisekunden-Bereich, das LLM in Sekunden. Brain-5D adressiert dies durch:
- **Asynchrone** Verarbeitung des LLM in separaten Threads
- **Nutzung des LLM nur für höhere Kognition** (nicht für Reflexe)
- **Cognitive Ticks** (z.B. alle 500-1000 Simulationsschritte)
- **Zeitüberschreitungen** und **Ressourcenlimits**

### 8.3 Ausblick

Die langfristige Vision ist ein System, bei dem das SNN zunehmend **eigene Interpretationsfähigkeiten** entwickelt – sodass der handgeschriebene Signal Interpreter durch einen **lernenden SNN-Decoder** ersetzt werden kann. Das LLM würde dann nur noch für seltene, komplexe Übersetzungen benötigt werden – ein natürlicher Übergang von externer zu interner Symbolverarbeitung.

---

## 9. Fazit

Brain-5D ist ein **experimentelles Framework für verkörperte, selbstorganisierende Intelligenz**, das die komplementären Stärken von Spiking Neural Networks und Large Language Models in einer kontrollierten, wissenschaftlich validierbaren Architektur vereint.

Die zentralen Innovationen sind:

1. **Kausale Geschlossenheit** des SNN – das LLM hat keinen direkten Zugriff auf synaptische Gewichte oder Plastizität
2. **Signal Bridge** als deterministische Interpretationsschicht zwischen Spikes und Symbolen
3. **Knowledge Intake Engine** für provenienzgesicherten, kontrollierten Wissenszugang
4. **Austauschbares Language Organ** mit Null-Backend für Kontrollexperimente
5. **Gestaffelte Roadmap** für schrittweise, wissenschaftlich fundierte Entwicklung

Das System ist derzeit auf dem Stand v0.5.0-alpha.5 und befindet sich in der aktiven Entwicklung. Die geplanten Erweiterungen (Alpha.6–V0.8) werden Brain-5D zu einer **vollständigen, experimentierbaren Plattform für hybride neural-symbolische Kognition** machen – mit dem Potenzial, grundlegende Fragen zum Verhältnis von Verkörperung, Lernen und Sprache in intelligenten Systemen zu adressieren.

---

## Literatur

1. EMBER: Experience-Modulated Biologically-inspired Emergent Reasoning. arXiv, 2026.

2. Incorporating structural plasticity into self-organization recurrent networks for sequence learning. PMC, 2023.

3. Structural Plasticity Denoises Responses and Improves Learning Speed. PMC, 2016.

4. STDP-Driven Rewiring in Spiking Neural Networks under Stimulus-Induced and Spontaneous Activity. PMC, 2023.

5. Izhikevich Neuron Model Documentation. BrainPy, 2026.

6. Qwen2.5-0.5B-Instruct-Q4_K_M-GGUF. Hugging Face, 2026.

7. Neuro-Symbolic Hypothesis Engine. ChemRxiv, 2025.
