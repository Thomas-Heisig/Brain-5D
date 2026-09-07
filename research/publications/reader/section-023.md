[Inhaltsuebersicht](README.md) | [Zurueck](section-022.md) | [Weiter](section-024.md)

<a id="b5d-repräsentation-gedächtnis-und-interne-prädiktion"></a>

# 19. Repräsentation, Gedächtnis und interne Prädiktion

<a id="b5d-informationsmaße-und-decodability"></a>

## Informationsmaße und Decodability

<a id="b5d-entropie-und-mutual-information"></a>

### Entropie und Mutual Information

**\[DEF\]** Für eine diskrete Variable $Y$ gilt

$$H(Y) = - \sum_{y}^{}p(y)\log p(y).$$Die Mutual Information zwischen internem Zustand $Z$ und Merkmal $Y$ lautet

$$I(Z;Y) = \sum_{z,y}^{}p(z,y)\log\frac{p(z,y)}{p(z)p(y)}.$$Sie misst statistische Abhängigkeit, nicht automatisch Kausalität oder semantische Repräsentation ([Cover & Thomas, 2006](section-045.md#ref-Cover2006); [Shannon, 1948](section-045.md#ref-Shannon1948)).

<a id="b5d-bedingte-information-und-confounds"></a>

### Bedingte Information und Confounds

Wenn aktueller Sensorinput $X$ sowohl $Z$ als auch $Y$ bestimmt, kann hohe Decodability triviales Durchreichen widerspiegeln. Deshalb ist bedingte Information relevant:

$$I\left( Z;Y|X \right).$$Für prädiktive Zustände ist beispielsweise zu testen, ob $Z_{t}$ Information über $S_{t + 1}$ enthält, die über $S_{t}$ und die Aktion $A_{t}$ hinausgeht.

<a id="b5d-schätzprobleme"></a>

### Schätzprobleme

Neuronale Zustände sind hochdimensional und Stichproben begrenzt. Naive Entropie- und MI-Schätzer sind verzerrt ([Panzeri et al., 2007](section-045.md#ref-Panzeri2007)). Brain-5D verlangt:

- vorab definierte Binning- oder Kernelverfahren;

- Bias-Korrektur beziehungsweise robuste nichtparametrische Schätzer;

- Konfidenzintervalle durch Bootstrap auf unabhängiger Episodenebene;

- Permutations- und Zeitshift-Nullmodelle;

- Sensitivitätsanalyse gegenüber Fenstergröße und Dimensionalitätsreduktion.

<a id="b5d-dekodierung"></a>

### Dekodierung

Ein Decoder $g$ schätzt $\hat{Y} = g(Z)$. Repräsentation wird nicht durch Trainingsgenauigkeit belegt. Erforderlich sind strikt getrennte Trainings-, Validierungs- und Testepisoden, idealerweise mit neuen Instanzen, Kontexten oder Transformationen. Zeitlich benachbarte Fenster derselben Episode dürfen nicht zufällig auf Train und Test verteilt werden, wenn dadurch Leakage entsteht.

<a id="b5d-representational-similarity-analysis"></a>

### Representational Similarity Analysis

RSA vergleicht Geometrien interner Zustände über Repräsentations-Dissimilaritätsmatrizen ([Kriegeskorte et al., 2008](section-045.md#ref-Kriegeskorte2008)). Für Brain-5D kann RSA prüfen, ob Stimulus-, Aktions- oder Kontextrelationen in neuronalen Zustandsräumen wiederkehren. Ergebnisse hängen jedoch von Distanzmaß, Normalisierung und Sampling ab. Ein RSA-Muster ist deskriptiv; funktionale Kausalität erfordert Intervention.

<a id="b5d-temporale-generalisierung"></a>

### Temporale Generalisierung

Ein Decoder, der auf Zeitfenster $t$ trainiert und auf $t\prime$ getestet wird, kann stabile oder transformierende Codes sichtbar machen ([King & Dehaene, 2014](section-045.md#ref-King2014)). Brain-5D kann damit unterscheiden, ob ein Signal nur während unmittelbarer Stimulation existiert oder in eine persistente Zustandsform übergeht.

<a id="b5d-transfer-entropy"></a>

### Transfer Entropy

**\[DEF\]** Transfer Entropy quantifiziert gerichtete prädiktive Information aus der Vergangenheit einer Variable in eine andere ([Schreiber, 2000](section-045.md#ref-Schreiber2000)). Sie ist nicht ohne zusätzliche Annahmen ein Beweis kausaler Wirkung. Gemeinsame Ursachen, unvollständige Beobachtung und unterschiedliche Zeitskalen können gerichtete Abhängigkeiten erzeugen. Transfer Entropy wird deshalb als exploratives Maß, nicht als alleinige Kausalanalyse verwendet.

<a id="b5d-decodability-repräsentation-und-funktion"></a>

### Decodability, Repräsentation und Funktion

Brain-5D verwendet eine dreistufige Unterscheidung:

1.  **Decodability:** $Y$ kann über Zufall aus $Z$ geschätzt werden;

2.  **Representation candidate:** Decodability ist stabil, generalisiert und übersteht Confound-Kontrollen;

3.  **Functional representation:** gezielte Manipulation von $Z$ verändert die auf $Y$ bezogene Leistung spezifisch.

Diese Trennung reagiert auf die Gefahr der Überinterpretation neuronaler Aktivitätsmuster und des Reverse Inference ([Jonas & Kording, 2017](section-045.md#ref-Jonas2017); [Poldrack, 2006](section-045.md#ref-Poldrack2006)).

<a id="b5d-repräsentation-gedächtnis-und-continual-learning"></a>

## Repräsentation, Gedächtnis und Continual Learning

<a id="b5d-operationalisierte-repräsentation"></a>

### Operationalisierte Repräsentation

**\[DEF\]** Ein Zustand oder eine Zustandsfamilie $Z$ gilt als Kandidat für eine Repräsentation des Merkmals $Y$, wenn:

1.  $Y$ aus $Z$ über Zufall dekodierbar ist;

2.  die Beziehung über unabhängige Seeds und Episoden reproduzierbar ist;

3.  sie auf nicht identische Beispiele oder Kontexte generalisiert;

4.  Kontrollzustände und Leakage-Quellen keine vergleichbare Leistung erzeugen;

5.  der Geltungsbereich explizit angegeben ist.

Ein funktionaler Status erfordert zusätzlich eine kausale Manipulation.

<a id="b5d-gedächtnisdefinition"></a>

### Gedächtnisdefinition

**\[DEF\]** Für Lerninhalt $K$ wird Gedächtnis als Tupel

$$M_{K} = \left( R_{K},C_{K},S_{K},G_{K} \right)$$definiert:

- $R_{K}$: Retention über eine definierte Zeit oder Anzahl von Interferenzen;

- $C_{K}$: cue-abhängiger Recall;

- $S_{K}$: Spezifität gegenüber Kontrollreizen;

- $G_{K}$: Generalisierung auf variierte Abfragen.

Eine zusammengesetzte Kennzahl kann

$$Q_{M} = \left( R_{K}C_{K}S_{K}G_{K} \right)^{\frac{1}{4}}$$sein. **\[HEUR\]** Diese geometrische Aggregation ist nur sinnvoll, wenn alle Komponenten normiert und substantiv erforderlich sind; Einzelmetriken müssen stets berichtet werden.

<a id="b5d-konsolidierung"></a>

### Konsolidierung

Schnelle lokale Anpassung kann störanfällig sein. Modelle synaptischer Kaskaden und komplementärer Lernsysteme motivieren mehrere Zeitskalen ([Benna & Fusi, 2016](section-045.md#ref-Benna2016); [Fusi et al., 2005](section-045.md#ref-Fusi2005); [McClelland et al., 1995](section-045.md#ref-McClelland1995)). Brain-5D kann schnelle Eligibility-/Gewichtsänderung, langsamere Metaplastizität und strukturelle Konsolidierung getrennt modellieren. Eine „Konsolidierungsphase” darf keine versteckte erneute Exposition enthalten.

<a id="b5d-arbeitsgedächtnis-und-stille-zustände"></a>

### Arbeitsgedächtnis und stille Zustände

Arbeitsgedächtnis kann durch anhaltende Aktivität oder kurzzeitige synaptische Zustände getragen werden ([Mongillo et al., 2008](section-045.md#ref-Mongillo2008)). Brain-5D soll deshalb sowohl aktive als auch activity-silent Kandidaten untersuchen. Ein Decoder darf jedoch nicht auf Metadaten zugreifen, die dem SNN selbst nicht verfügbar sind.

<a id="b5d-continual-learning-metriken"></a>

### Continual-Learning-Metriken

Für Aufgabenfolge $T_{1},\ldots,T_{K}$ sei $Q_{i,j}$ die Leistung auf Aufgabe $i$ nach Training bis Aufgabe $j$. Dann kann Forgetting definiert werden als

**\[DEF\]**

$$F_{i} = \max_{j < i}Q_{i,j} - Q_{i,K}.$$**Redaktioneller Befund.** Bei der gerade definierten Indexkonvention betrachtet j \< i Zeitpunkte vor dem Training der Aufgabe i; für i = 1 ist diese Indexmenge leer. Die übernommene Formel ist deshalb ohne weitere Festlegung kein wohldefiniertes Mass des Verlusts einer bereits erworbenen Aufgabenleistung. Sie wird hier als Originalformel sichtbar belassen und nicht als Auswertungsregel freigegeben.

**\[DEF \| Synthesevorschlag\]** Ein expliziter, nichtnegativer Post-Learning-Verlust kann stattdessen für i \< K definiert werden als:

$$F_i^{\mathrm{post}}=\max_{i\leq j\leq K}Q_{i,j}-Q_{i,K}.$$Die Einbeziehung des Endzeitpunkts K erzwingt F_post \>= 0; spätere Verbesserung wird dann nicht als negatives Forgetting, sondern separat etwa durch BWT berichtet. Das ist eine offengelegte Definitionsentscheidung, keine nachträgliche Neuberechnung der LIFE-Ergebnisse. Vor einem Experiment sind Indexkonvention, Messzeitpunkte und Umgang mit fehlenden Aufgabenwerten festzulegen.

Weitere Größen sind:

$$\text{BWT} = \frac{1}{K - 1}\sum_{i = 1}^{K - 1}\left( Q_{i,K} - Q_{i,i} \right),$$$$\text{FWT} = \frac{1}{K - 1}\sum_{i = 2}^{K}\left( Q_{i,i - 1} - b_{i} \right),$$mit Baseline $b_{i}$. Catastrophic forgetting ist ein langjähriges Problem sequenziellen Lernens ([French, 1999](section-045.md#ref-French1999); [Kirkpatrick et al., 2017](section-045.md#ref-Kirkpatrick2017); [McCloskey & Cohen, 1989](section-045.md#ref-McCloskey1989); [Parisi et al., 2019](section-045.md#ref-Parisi2019)). Brain-5D untersucht lokale und strukturelle Alternativen, sollte aber etablierte Baselines wie Regularisierung, Replay oder Synaptic Intelligence einbeziehen ([Lopez-Paz & Ranzato, 2017](section-045.md#ref-LopezPaz2017); [Zenke et al., 2017](section-045.md#ref-Zenke2017CL)).

<a id="b5d-retrieval-ist-nicht-lernen"></a>

### Retrieval ist nicht Lernen

**\[DEF\]** Retrieval liefert Information aus einer externen Quelle oder einem expliziten Speicher an die aktuelle Verarbeitung. Lernen verändert den zukünftigen internen Zustand oder die Leistung aufgrund einer Erfahrung. Ein System kann beides kombinieren; der Nachweis erfordert Isolation.

Das Minimalprotokoll lautet:

1.  Baseline-Abfrage vor Exposition;

2.  kontrollierte Exposition über `StimulusPlan`;

3.  Konsolidierungsintervall ohne erneuten Informationsabruf;

4.  Abschalten von LLM-Kontext, Retrieval, Cache und Netzwerkzugriff;

5.  Recall mit gleicher und variierter Abfrage;

6.  Vergleich mit ungeübtem, plastizitätsgesperrtem, zufällig stimuliertem und state-permutiertem Netzwerk.

Nur ein über Kontrollen hinausgehender Recall unterstützt den Claim neuronaler Speicherung.

<a id="b5d-kandidat-für-ein-internes-prädiktives-zustandsmodell"></a>

## Kandidat für ein internes prädiktives Zustandsmodell

<a id="b5d-terminologische-zurückhaltung"></a>

### Terminologische Zurückhaltung

Der Begriff „World Model” wird in der Literatur für unterschiedliche latente oder prädiktive Modelle verwendet ([Ha & Schmidhuber, 2018](section-045.md#ref-Ha2018); [Hafner et al., 2020](section-045.md#ref-Hafner2020); [Schrittwieser et al., 2020](section-045.md#ref-Schrittwieser2020)). Brain-5D verwendet in der Roadmap zunächst die vorsichtigere Bezeichnung **Kandidat für ein internes prädiktives Zustandsmodell**. Der Begriff „Weltmodell” ist erst nach expliziter Operationalisierung zulässig.

<a id="b5d-minimalmodell"></a>

### Minimalmodell

**\[MODEL\]** Ein interner Zustand $s_{t}$ und eine Aktion $a_{t}$ erzeugen eine Vorhersage

$${\hat{s}}_{t + 1} = f_{\psi}\left( s_{t},a_{t} \right),$$beziehungsweise eine Beobachtungsvorhersage

$${\hat{o}}_{t + 1} = g_{\omega}\left( s_{t},a_{t} \right).$$Ein Kandidat erfüllt mindestens:

1.  Vorhersage über einen zukünftigen Umwelt- oder Sensorzustand;

2.  Zusatzinformation über die triviale Kopie des aktuellen Inputs hinaus;

3.  Sensitivität gegenüber alternativen Aktionen;

4.  Generalisierung auf nicht trainierte Sequenzen oder Kontexte;

5.  mehrschrittige Rollouts mit quantifiziertem Fehler;

6.  funktionalen Nutzen für Planung oder Verhalten;

7.  Leistungsabfall bei gezielter Ablation des prädiktiven Zustands.

<a id="b5d-predictive-state-representations"></a>

### Predictive State Representations

Predictive State Representations beschreiben Zustand über Vorhersagen zukünftiger Beobachtungen statt über verborgene ontologische Variablen ([Littman et al., 2001](section-045.md#ref-Littman2001)). Dieses Konzept ist für Brain-5D attraktiv, weil es operationalisierbar bleibt: Entscheidend ist, welche Zukunftsinformation ein interner Zustand trägt und wie sie Verhalten beeinflusst.

<a id="b5d-dyna-und-interne-simulation"></a>

### Dyna und interne Simulation

Dyna-Architekturen verbinden Lernen, Planung und simulierte Erfahrung ([Sutton, 1991](section-045.md#ref-Sutton1991)). Brain-5D soll erst dann von interner Simulation sprechen, wenn das System intern erzeugte Zustandsübergänge von externen Sensorereignissen unterscheiden kann und diese Übergänge nachweisbar zur Handlungswahl nutzt. Zufällige Replay-Aktivität oder Traumlogs sind noch keine Planung.

<a id="b5d-prüfbare-hypothese"></a>

### Prüfbare Hypothese

**\[E0 \| HYPOTHESIS \| CLAIM-PRED-001\]** In einer geschlossenen, partiell beobachtbaren Umgebung können rekurrente Brain-5D-Zustände action-konditionierte Zukunftsinformation akkumulieren, die über aktuellen Sensorinput hinausgeht und die Leistung bei verzögerten Entscheidungsaufgaben verbessert.

Falsifikation: Ein kontrollierter Decoder findet keine inkrementelle Zukunftsinformation; oder die Ablation prädiktiver Zustände beeinflusst Verhalten nicht stärker als gematchte Kontrollablationen.

[Inhaltsuebersicht](README.md) | [Zurueck](section-022.md) | [Weiter](section-024.md)
