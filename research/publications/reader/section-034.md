[Inhaltsuebersicht](README.md) | [Zurueck](section-033.md) | [Weiter](section-035.md)

<a id="b5d-experimentfamilien-a-bis-j-baselines-und-falsifikation"></a>

# 30. Experimentfamilien A bis J, Baselines und Falsifikation

<a id="b5d-experiment-a-dimensionalität-und-geometrie"></a>

## Experiment A — Dimensionalität und Geometrie

<a id="b5d-fragestellung"></a>

### Fragestellung

Besitzt 5D unter gematchten Ressourcen einen kausalen Vorteil, und stammt dieser gegebenenfalls aus der Anzahl der Dimensionen, der Distanzfunktion oder der resultierenden Topologie?

<a id="b5d-design"></a>

### Design

Faktoren:

- Dimension $D \in \{ 2,3,4,5,6\}$;

- Metrik: Identität, diagonale Gewichtung, gelernte SPD-Matrix;

- Topologie: geometrisch, degree-preserving rewired, nichtgeometrisch;

- Aufgabenklasse: assoziativer Recall, Sequenzvorhersage, Closed-Loop-Navigation.

Primärendpunkt ist eine vorab gewählte funktionale Metrik. Sekundär werden Modularität, Interferenz, Edge Cost und Stabilität untersucht.

<a id="b5d-identifizierbarkeit-1"></a>

### Identifizierbarkeit

Die Anzahl der Dimensionen beeinflusst bei gleicher Distanzschwelle die Nachbarschaftsvolumina. Deshalb werden Dichte und Grad nicht über identische Radiusparameter, sondern direkt gematcht. Koordinaten werden normalisiert. Metriklernen erhält Train-/Validation-Splits, damit die Metrik nicht auf dem Testset optimiert wird.

<a id="b5d-falsifikation"></a>

### Falsifikation

$H_{0}^{5D}$**:** 5D besitzt keinen relevanten Vorteil gegenüber der besten gematchten Kontrolltopologie. Die Hypothese gilt als nicht unterstützt, wenn Effekte klein, inkonsistent, kostenbedingt oder nicht replizierbar sind. Ein Vorteil nur in einem einzelnen Seed oder einem Decoder ist unzureichend.

<a id="b5d-experiment-b-stabilitäts--und-phasenkarte"></a>

## Experiment B — Stabilitäts- und Phasenkarte

<a id="b5d-fragestellung-1"></a>

### Fragestellung

Welche Kombination aus Konnektivität, E/I-Balance, Lernrate, Homeostasezeit, Delay und Rauschen erzeugt ein begrenztes, responsives und plastisches Regime?

<a id="b5d-parameterraum"></a>

### Parameterraum

Ein vollfaktorielles Design ist häufig zu teuer. Vorgesehen ist eine sequenzielle Strategie:

1.  Latin-Hypercube- oder Sobol-Sampling des Parameterraums;

2.  Klassifikation dynamischer Regime;

3.  adaptive Verdichtung an Übergangsbereichen;

4.  Replikation ausgewählter Punkte über Seeds und Netzwerkgrößen;

5.  lokale Bifurkations- beziehungsweise Perturbationsanalyse.

<a id="b5d-primärendpunkt"></a>

### Primärendpunkt

Ein Lauf gilt nicht allein aufgrund mittlerer Zielrate als stabil. Ein zusammengesetzter Stabilitätsvektor umfasst Runaway-Anteil, Quieszenz, Sensitivität, Ressourcenüberschreitung, Feuerratenvarianz und funktionale Antwort. Phasengrenzen werden mit Unsicherheit berichtet.

<a id="b5d-experiment-c-plastizitätsmechanismen"></a>

## Experiment C — Plastizitätsmechanismen

<a id="b5d-faktorielles-ablationsdesign"></a>

### Faktorielles Ablationsdesign

Verglichen werden:

- ohne Plastizität;

- Pair-STDP;

- STDP + Homeostase;

- Three-Factor-Regel;

- Three-Factor + Homeostase;

- zusätzlich inhibitorische Plastizität;

- zusätzlich strukturelle Plastizität;

- vollständiges System.

Bei hoher Faktorzahl kann ein fraktionelles Design oder eine hierarchische Sequenz verwendet werden. Interaktionen sind wissenschaftlich relevant: Homeostase kann STDP nur in bestimmten Zeitskalen stabilisieren.

<a id="b5d-outcomes"></a>

### Outcomes

Lernleistung, Instabilitätsrate, Gewichtssättigung, Retention, Interferenz, Strukturkosten und Energieproxy. Ein Mechanismus gilt nur dann als funktional nützlich, wenn sein Nutzen nicht ausschließlich durch höhere Ressourcen entsteht.

<a id="b5d-experiment-d-gedächtnis-und-retrieval-isolation"></a>

## Experiment D — Gedächtnis und Retrieval-Isolation

<a id="b5d-phasen"></a>

### Phasen

**A — Baseline:** unbekannte Inhalte abfragen.<br>
**B — Exposition:** kontrollierte Stimuluspläne mit dokumentierter Dosis.<br>
**C — Konsolidierung:** keine externe Wiederholung.<br>
**D — Isolation:** LLM, Retrieval, Cache und Netzwerkzugang abschalten.<br>
**E — Recall:** identische, paraphrasierte und kontextvariierte Cues.<br>
**F — Kontrollen:** ungeübtes, plastizitätsgesperrtes, randomisiertes und relevant lädiertes Netzwerk.

<a id="b5d-state-destruction-kontrollen"></a>

### State-Destruction-Kontrollen

Um zu bestimmen, welcher Zustand Recall trägt, werden gezielt Gewichte, Eligibility, Schwellen, Struktur oder Aktivitätszustand zurückgesetzt beziehungsweise permutiert. Eine kontrollierte Störung, die Recall selektiv zerstört, stärkt die kausale Zuordnung.

<a id="b5d-decoder-confound"></a>

### Decoder-Confound

Der Decoder wird entweder vor dem Lernexperiment eingefroren oder auf separaten Daten trainiert. Ein Decoder, der nachträglich auf dieselben Recall-Labels angepasst wird, kann Netzwerkrauschen in scheinbar sinnvolle Klassen überführen.

<a id="b5d-experiment-e-continual-learning"></a>

## Experiment E — Continual Learning

<a id="b5d-aufgabenfolgen"></a>

### Aufgabenfolgen

Es werden unterschiedliche Sequenztypen verwendet:

- disjunkte Klassen;

- gemeinsame Merkmale mit wechselnden Labels;

- gradueller Domain Shift;

- wiederkehrende Aufgaben;

- widersprüchliche Inhalte;

- neue Sensor- oder Aktorzuordnungen.

Die Reihenfolge wird randomisiert oder als Faktor behandelt. Ein einziges Curriculum kann Mechanismen bevorzugen.

<a id="b5d-baselines"></a>

### Baselines

Neben Brain-5D-Ablationen werden Replay, Elastic Weight Consolidation, Synaptic Intelligence und gegebenenfalls Reservoir-Baselines einbezogen ([Kirkpatrick et al., 2017](section-045.md#ref-Kirkpatrick2017); [Lopez-Paz & Ranzato, 2017](section-045.md#ref-LopezPaz2017); [Zenke et al., 2017](section-045.md#ref-Zenke2017CL)). Ziel ist nicht, biologische Inspiration gegen beliebige Deep-Learning-Benchmarks auszuspielen, sondern den spezifischen Nutzen der Mechanismen zu bestimmen.

<a id="b5d-widerspruchsexperiment"></a>

### Widerspruchsexperiment

Ein Inhalt $K$ wird gelernt, später durch $\neg K$ oder eine kontextabhängige Variante ergänzt. Gemessen wird, ob das System überschreibt, beide Kontexte trennt oder inkonsistente Antworten erzeugt. Provenienz und Zeit müssen im Stimulus repräsentierbar sein; andernfalls ist Konfliktauflösung nicht fair prüfbar.

<a id="b5d-experiment-f-language-organ-und-knowledge-intake"></a>

## Experiment F — Language Organ und Knowledge Intake

<a id="b5d-komponentenzuschreibung"></a>

### Komponentenzuschreibung

Die Bedingungen L0–L4 werden systematisch verglichen. Zusätzlich:

- Decoder mit echten SignalFrames versus geshuffelten Frames;

- LLM mit leerem versus vollständigem Promptkontext;

- Retrieval mit und ohne SNN;

- Encoder-Stimuli versus semantisch gematchte Zufallscodes;

- FeedbackProposal akzeptiert versus abgelehnt;

- NullLanguageBackend.

<a id="b5d-outcome-zerlegung"></a>

### Outcome-Zerlegung

Gesamtantwortqualität wird zerlegt in:

$$Q_{total} = Q_{retrieval} + Q_{decoder} + Q_{SNN} + Q_{interaction} + \varepsilon$$**\[MODEL\]** Die additive Form ist nur eine Analyseheuristik; Interaktionen können erheblich sein. Faktorielles Design oder Shapley-artige Komponentenanalyse kann Beiträge schätzen, ersetzt aber keine mechanistische Isolation.

<a id="b5d-prompt--und-modellversionierung"></a>

### Prompt- und Modellversionierung

Jede LLM-Bedingung speichert Systemprompt, Userprompt, Toolkontext, Samplingparameter, Modell-Hash beziehungsweise API-Version und Antwort. Sonst ist ein späterer Vergleich nicht reproduzierbar.

<a id="b5d-experiment-g-embodiment"></a>

## Experiment G — Embodiment

<a id="b5d-open-versus-closed-loop"></a>

### Open versus Closed Loop

Zwei Systeme erhalten möglichst gleiche Architektur und sensorische Grundinformation. Im Open Loop sind Stimuli vorab aufgezeichnet; im Closed Loop beeinflussen Aktionen die Umwelt. Ein dritter **yoked control** erhält die Beobachtungsfolge eines Closed-Loop-Agents, darf sie aber nicht selbst verursachen. Dadurch lässt sich aktive Kontingenz von bloßer Datenverteilung trennen.

<a id="b5d-aufgaben"></a>

### Aufgaben

Geeignete frühe Aufgaben sind einfache Navigation, Objektannäherung/-vermeidung, sensorische Kalibrierung und verzögerte Handlungswahl. Sie sollen kausal transparent sein, bevor komplexe multimodale Umgebungen eingeführt werden.

<a id="b5d-messungen"></a>

### Messungen

Lernrate, Robustheit bei Dynamics Shift, action-conditional Decodability, kausale Läsionen und Vorhersage zukünftiger Beobachtungen. Eine höhere Belohnung kann aus einfacher Exploration stammen und ist nicht allein Nachweis reichhaltigerer Repräsentation.

<a id="b5d-experiment-h-messbare-emergenz"></a>

## Experiment H — Messbare Emergenz

<a id="b5d-kandidatenerkennung"></a>

### Kandidatenerkennung

Strukturelle Communities, dynamische Sequenzen oder metastabile Zustände werden explorativ identifiziert. Der Erkennungsdatensatz bleibt von der konfirmatorischen Prüfung getrennt. Kandidaten erhalten eindeutige IDs und Definitionen.

<a id="b5d-konfirmatorische-prüfung"></a>

### Konfirmatorische Prüfung

1.  Replikation des Kandidaten in neuen Seeds;

2.  Vergleich mit Nullmodellen;

3.  Stabilität gegenüber Analyseparametern;

4.  gezielte Läsion;

5.  matched lesions;

6.  Rescue oder Ersatzintervention;

7.  Prüfung auf Aufgabenspezifität.

<a id="b5d-falsifikation-1"></a>

### Falsifikation

Ein Cluster ist nicht funktional emergent, wenn seine Entfernung keinen spezifischen Effekt hat oder wenn beliebige gleich große Läsionen denselben Effekt erzeugen. Ein dynamisches Muster ist nicht robust, wenn es nur unter einer Auswertungsparametrisierung erscheint.

<a id="b5d-experiment-i-storage--und-twin-fidelity"></a>

## Experiment I — Storage- und Twin-Fidelity

<a id="b5d-rekonstruktionsprüfung"></a>

### Rekonstruktionsprüfung

Aus einem Checkpoint plus Event-Log wird ein Zustand rekonstruiert. Verglichen werden Neuronenarrays, Synapsenstruktur, RNG, Scheduler, Metriken und Reaktion auf standardisierte Probe-Stimuli. Die Prüfung umfasst:

- Hash- und Schema-Integrität;

- State Error;

- Edge Set-Differenz;

- Event-Reihenfolge;

- Probe-Response-Divergenz;

- Restore-Zeit und Storage-Overhead.

<a id="b5d-forked-counterfactuals"></a>

### Forked Counterfactuals

Von demselben Snapshot werden mehrere Interventionen gestartet. Wenn Unterschiede vor der Intervention auftreten, ist der Fork nicht kausal sauber. Dieses Experiment ist Grundlage für spätere Emergenz- und Läsionsanalysen.

<a id="b5d-langzeitintegrität"></a>

### Langzeitintegrität

Artefakte werden nach wiederholtem Speichern, Migrieren und Wiederherstellen geprüft. Checksums allein erkennen keine semantisch falsche Schemaumwandlung; daher sind migrationsspezifische Invarianten erforderlich.

<a id="b5d-experiment-j-scaling-und-performance"></a>

## Experiment J — Scaling und Performance

<a id="b5d-komplexitätsmodell"></a>

### Komplexitätsmodell

Für ereignisbasierte Verarbeitung gilt näherungsweise

$$T_{tick} = O\left( N_{integrated} \right) + O\left( S_{event} \right) + O\left( P_{plasticity} \right) + O\left( G_{structural} \right) + O\left( IO_{dirty} \right).$$Die Größen sind empirisch zu messen. Bei dichter Integration kann $N_{integrated} = N_{active}$ oder sogar $N_{materialized}$ sein; eventbasierte Optimierung reduziert dies nur, wenn Zustände zwischen Ereignissen effizient fortgeschrieben werden können.

<a id="b5d-skalierungsachsen"></a>

### Skalierungsachsen

- materialisierte Neuronen;

- mittlerer Grad;

- Spike-Rate;

- Delay-Horizont;

- Plastizitätsdichte;

- Structural-Update-Frequenz;

- Snapshot-Intervall;

- Anzahl Regionen/Partitionen;

- parallele Worker oder Geräte.

Jeweils wird unterschieden, ob Laufzeit, RAM, I/O oder Synchronisation der Engpass ist.

<a id="b5d-strong-und-weak-scaling"></a>

### Strong und Weak Scaling

**Strong Scaling:** Problemgröße bleibt gleich, Ressourcen steigen.<br>
**Weak Scaling:** Problemgröße wächst proportional zu Ressourcen.<br>
Effizienz wird nicht nur als Speedup, sondern auch als wissenschaftliche Reproduzierbarkeit und numerische Abweichung bewertet.

<a id="b5d-größenübertragung"></a>

### Größenübertragung

Ein Mechanismus, der bei 5.000 Neuronen funktioniert, kann bei 500.000 andere Dynamik zeigen. Skalierungsexperimente prüfen dimensionslose oder normalisierte Parameter, Finite-Size-Effekte und Änderung der Phasengrenzen. Ergebnisse werden nicht allein auf Grundlage identischer absoluter Hyperparameter extrapoliert.

<a id="b5d-vergleichsbaselines"></a>

## Vergleichsbaselines

Brain-5D wird langfristig mindestens gegen folgende Systeme verglichen:

- statisches SNN gleicher Größe;

- SNN ohne 5D-Distanz;

- randomisierte oder degree-preserving rewired Topologie;

- Liquid State Machine beziehungsweise Reservoir Computing;

- einfache RNN-/GRU-Baseline bei Aufgaben mit vergleichbarer Ein-/Ausgabe;

- klassischer RL-Agent;

- LLM-only;

- Retrieval-Augmented LLM;

- Brain-5D mit NullLanguageBackend;

- zufälliges Feature- beziehungsweise untrainiertes Netzwerk.

Baselines werden nicht nur nach Leistung, sondern auch nach Ressourcen, Online-Lernfähigkeit, Persistenz und Ablationsinterpretierbarkeit bewertet.

<a id="b5d-falsifikationsmatrix"></a>

## Falsifikationsmatrix

Tabelle 32. Falsifikationsmatrix

| **Claim**                                              | **Unterstützendes Muster**                                                     | **Falsifikation / Nichtunterstützung**                                          |
|:-------------------------------------------------------|:-------------------------------------------------------------------------------|:--------------------------------------------------------------------------------|
| 5D verbessert funktionale Modularität                  | Vorteil gegenüber gematchten 2D–6D- und Rewiring-Kontrollen; Effekt über Seeds | kein relevanter Vorteil; nur höhere Dichte oder Kosten erklären Effekt          |
| Homeostase stabilisiert Lernen                         | weniger Runaway/Quieszenz bei erhaltener Leistung                              | Stabilität steigt nicht oder Lernen wird gleich stark unterdrückt               |
| strukturelle Plastizität verbessert Continual Learning | geringeres Forgetting bei kontrolliertem Budget                                | gleiche oder schlechtere Retention; Nutzen verschwindet bei Kostenmatching      |
| SNN speichert KnowledgeItem                            | Recall nach Isolation über Kontrollen                                          | Recall fällt nach Retrieval-/LLM-Abschaltung auf Kontrollniveau                 |
| emergentes Cluster ist funktional                      | spezifischer matched-lesion-Effekt und Rescue                                  | beliebige Läsion gleich wirksam; Effekt nicht replizierbar                      |
| interner Zustand ist prädiktiv                         | inkrementelle Zukunftsinformation und Verhaltensnutzen                         | keine Zusatzinformation über aktuellen Input; Ablation ohne spezifischen Effekt |
| Digital State Twin ist kausal fidel                    | Replay reagiert auf Probe-Stimuli äquivalent                                   | Restore divergiert vor Intervention oder verliert relevante Struktur            |

<a id="b5d-validität"></a>

## Validität

<a id="b5d-interne-validität"></a>

### Interne Validität

Gefährdungen sind ungematchte Ressourcen, Decoder-Leakage, variable Seeds, nachträgliche Parameterwahl, versteckte Retrieval-Caches und unkontrollierte LLM-Rückkopplung. Architektur-Invarianten und präregistrierte Spezifikationen adressieren diese Risiken.

<a id="b5d-konstruktvalidität"></a>

### Konstruktvalidität

Spikezahl ist keine Intelligenz; Modularität ist keine kognitive Modularität; Decodability ist keine kausale Repräsentation; Persistenz ist kein Gedächtnis. Jede Metrik wird gegen die theoretische Bedeutung geprüft.

<a id="b5d-externe-validität"></a>

### Externe Validität

Ergebnisse sollen über Seeds, Aufgaben, Netzwerkgrößen, Stimulusvarianten und Modelle geprüft werden. Ein Effekt in einem synthetischen Benchmark kann wertvoll sein, muss aber entsprechend eng formuliert werden.

<a id="b5d-ökologische-validität"></a>

### Ökologische Validität

Closed-Loop- und physische Tests erhöhen ökologische Nähe, führen aber neue Confounds ein. Sie ersetzen keine kontrollierten Laborbenchmarks. Beide Ebenen sind komplementär.

<a id="b5d-schlussfolgerungsvalidität"></a>

### Schlussfolgerungsvalidität

Zu kleine Seed-Zahlen, multiple Tests, selektive Berichterstattung und Pseudoreplikation gefährden Schlussfolgerungen. Reproduzierbare Forschungspraxis, Präregistrierung und vollständige Run-Berichte sind deshalb methodische Kernbestandteile ([Munafò et al., 2017](section-045.md#ref-Munafo2017); [Nosek et al., 2018](section-045.md#ref-Nosek2018); [Sandve et al., 2013](section-045.md#ref-Sandve2013)).

[Inhaltsuebersicht](README.md) | [Zurueck](section-033.md) | [Weiter](section-035.md)
