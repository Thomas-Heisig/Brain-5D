[Inhaltsuebersicht](README.md) | [Zurueck](section-016.md) | [Weiter](section-018.md)

<a id="b5d-brain-5d-ontologie-architektur-und-sicherheitsgrenzen"></a>

# 13. MHRN: Ontologie, Architektur und Sicherheitsgrenzen

<a id="b5d-rolle-des-fallbeispiels"></a>

## Rolle des Fallbeispiels

MHRN ist der praktische Entstehungskontext der Forschungsfragen. Das Projekt untersucht ein räumlich organisiertes Spiking Neural Network mit lokaler Plastizität, struktureller Veränderung und optionalen Sprachmodell-Schnittstellen. Für die wissenschaftliche Abhandlung dient es als begrenzter Beobachtungsraum: Hier lassen sich maschinelle Entwurfsvorschläge, menschliche Auswahlentscheidungen, Selbstorganisationsprozesse, Sicherheitsgrenzen und Provenienz dokumentieren. Aus einem einzelnen System dürfen jedoch keine universalen Aussagen über Intelligenz oder Bewusstsein abgeleitet werden.

Die reflexive Begleitforschung besitzt zwei Funktionen. Erstens macht sie die theoretischen Begriffe operativ: Hoheit, Kontrolle, Embodiment und Autorenschaft können an konkreten Entwicklungsentscheidungen protokolliert werden. Zweitens prüft sie die eigene Forschungspraxis: Wenn verschiedene LLMs Architekturideen, Code oder Argumente erzeugen, muss sichtbar bleiben, welche Entscheidung vom Menschen stammt, welche maschinell vorstrukturiert wurde und welche durch das lernende System selbst entstand.

<a id="b5d-terminologie-und-ontologie"></a>

## Terminologie und Ontologie

<a id="b5d-zweck-der-ontologie"></a>

### Zweck der Ontologie

Eine konsistente Ontologie verhindert, dass identische Begriffe in Code, Methodik und Interpretation unterschiedliche Bedeutungen erhalten. Die hier definierten Begriffe sollen als versionierte Schemaobjekte in der Software gespiegelt werden. Jede Änderung mit wissenschaftlicher Auswirkung muss migrationsfähig sein und im Evidenzregister erscheinen.

<a id="b5d-kernentitäten"></a>

### Kernentitäten

Tabelle 19. Kernentitäten des MHRN-Frameworks

| **Entität**    | **Arbeitsdefinition**                                                                                                                      | **Abgrenzung**                                                                  |
|:---------------|:-------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------|
| Neuron         | materialisierte dynamische Einheit mit eindeutiger ID, 5D-Position, Zelltyp, Zustandsvektor, Parametern und Ereignishistorie               | kein biologisch vollständiges Neuron                                            |
| Synapse        | gerichtete, typisierte und gegebenenfalls verzögerte Verbindung zwischen zwei materialisierten Einheiten                                   | nicht bloß Matrixeintrag, wenn Alter, Eligibility oder Provenienz relevant sind |
| SpikeEvent     | diskretes, zeitgestempeltes Ereignis einer Quelle mit definierter Simulationszeit                                                          | keine semantische Aussage                                                       |
| Region         | versionierte Menge beziehungsweise probabilistische Zuordnung von Neuronen anhand räumlicher, funktionaler oder datengetriebener Kriterien | darf nicht nachträglich ohne Versionierung umdefiniert werden                   |
| Stimulus       | kontrollierte externe Ursache, die über einen Eingabekanal auf das SNN wirkt                                                               | Retrieval-Antwort ist erst nach Kodierung ein Stimulus                          |
| StimulusPlan   | validierter, zeitlich und räumlich bestimmter Vertrag zur Erzeugung von Input-Ereignissen                                                  | kein direkter Gewichts- oder Topologiezugriff                                   |
| Episode        | abgegrenzte Sequenz von Stimuli, Netzwerkzuständen, Aktionen, Rewards und Umweltzuständen                                                  | nicht gleich Trainingsbatch                                                     |
| SignalFrame    | deterministisch berechnete Messzusammenfassung eines definierten Ereignis- und Zustandsfensters                                            | Interpretation oder Bedeutung sind nicht enthalten                              |
| Interpretation | versionierte Hypothese eines Decoders über einen SignalFrame                                                                               | kann falsch sein und darf keinen Faktstatus erben                               |
| Repräsentation | reproduzierbare Beziehung zwischen internem Zustand und Zielmerkmal, die Kontrollen und Generalisierungskriterien erfüllt                  | Korrelation allein genügt nicht                                                 |
| Gedächtnis     | retention-, cue- und spezifitätsgebundene funktionale Folge einer früheren Erfahrung                                                       | persistentes Gewicht allein genügt nicht                                        |
| Claim          | atomare, identifizierbare wissenschaftliche Aussage mit Evidenzstatus und Geltungsbereich                                                  | kein bloßer Kommentar                                                           |
| ExperimentSpec | unveränderliche Versuchsspezifikation mit Hypothese, Faktoren, Kontrollen und Endpunkten                                                   | Auswertung darf Spezifikation nicht stillschweigend ersetzen                    |
| RunRecord      | technische Beschreibung eines ausgeführten Laufs                                                                                           | umfasst Commit, Config, Seed und Hardware                                       |
| EvidenceRecord | begründete Zuordnung eines Claims zu einer Evidenzstufe anhand verknüpfter Ergebnisse                                                      | kann revidiert werden                                                           |

<a id="b5d-beziehungen"></a>

### Beziehungen

Die zentrale Provenienz- und Kausalitätskette lautet:

$$\begin{gathered}\text{SourceRecord}\to\text{KnowledgeItem}\to\text{StimulusPlan}\to\text{Episode}\\ \to X_t\to\text{SignalFrame}\to\text{Interpretation}\to\text{Response}\end{gathered}$$**\[DEF\]** Der Pfeil bedeutet hier eine dokumentierte Ableitungs- oder Einflussrelation, nicht automatisch eine hinreichende Kausalursache. Für kausale Aussagen sind Interventionen oder ein begründetes Kausalmodell erforderlich ([Pearl, 2009](section-045.md#ref-Pearl2009); [Woodward, 2003](section-045.md#ref-Woodward2003)).

<a id="b5d-region-als-mehrdeutige-aber-versionierte-kategorie"></a>

### Region als mehrdeutige, aber versionierte Kategorie

Eine Region kann auf mindestens vier Arten entstehen:

1.  **a priori geometrisch:** durch Koordinatenbereiche;

2.  **funktional spezifiziert:** etwa Input-, Output- oder Modulationsregion;

3.  **strukturell datengetrieben:** durch Community Detection im Synapsengraphen;

4.  **dynamisch datengetrieben:** durch wiederkehrende Aktivitäts- oder Synchronisationsmuster.

Die vier Typen dürfen nicht ohne Kennzeichnung gleichgesetzt werden. Eine geometrische Region ist nicht automatisch eine funktionale Einheit; eine algorithmisch gefundene Community ist nicht automatisch ein kognitives Modul. Regionendefinition, Algorithmus, Parameter und Zeitpunkt werden deshalb mitgeführt.

<a id="b5d-wissenschaftliche-positionierung"></a>

## Wissenschaftliche Positionierung

<a id="b5d-computational-neuroscience-und-snns"></a>

### Computational Neuroscience und SNNs

SNNs erlauben die explizite Untersuchung neuronaler Zustände, Spike-Zeitpunkte, Rekurrenz und zeitabhängiger Plastizität. Das Spektrum reicht von biologisch detaillierten Hodgkin-Huxley- und Kompartimentmodellen bis zu rechnerisch günstigeren LIF-, AdEx- und Izhikevich-Modellen ([Brette & Gerstner, 2005](section-045.md#ref-Brette2005); [Gerstner et al., 2014](section-045.md#ref-Gerstner2014); [Hodgkin & Huxley, 1952](section-045.md#ref-Hodgkin1952); [Izhikevich, 2003](section-045.md#ref-Izhikevich2003)). MHRN verwendet diese Modelle nicht als Beweis biologischer Gleichwertigkeit, sondern als experimentell austauschbare Dynamikklassen.

<a id="b5d-dynamische-systeme"></a>

### Dynamische Systeme

Rekurrente Spike-Netze sind nicht nur Informationskanäle, sondern nichtlineare dynamische Systeme mit Zuständen, transienten Trajektorien, möglichen Attraktoren, metastabilen Regimen und Parameterübergängen. Hybride Systemformalismen sind geeignet, kontinuierliche Flüsse, diskrete Spikes, Resets und Strukturänderungen gemeinsam zu beschreiben ([Breakspear, 2017](section-045.md#ref-Breakspear2017); [Goebel et al., 2012](section-045.md#ref-Goebel2012Hybrid); [Kuznetsov, 2004](section-045.md#ref-Kuznetsov2004); [Strogatz, 2015](section-045.md#ref-Strogatz2015)). Für MHRN ist Stabilität daher keine bloße Fehlerfreiheit, sondern ein empirisch zu kartierender Bereich zwischen Degeneration und unkontrollierter Aktivität.

<a id="b5d-netzwerk--und-geometrieperspektive"></a>

### Netzwerk- und Geometrieperspektive

Graphentheoretische Maße ermöglichen die Beschreibung von Gradverteilungen, Pfadlängen, Clustering, Modularität, Motiven und spektralen Eigenschaften ([Bassett & Sporns, 2017](section-045.md#ref-Bassett2017); [Newman, 2003](section-045.md#ref-Newman2003); [Rubinov & Sporns, 2010](section-045.md#ref-Rubinov2010)). Geometrische Graphen und gelernte Metriken erweitern diese Perspektive um die Frage, ob Distanz selbst ein fester Parameter oder ein adaptiver Bestandteil des Systems ist ([Bronstein et al., 2017](section-045.md#ref-Bronstein2017); [Penrose, 2003](section-045.md#ref-Penrose2003); [Weinberger & Saul, 2009](section-045.md#ref-Weinberger2009)). MHRN behandelt fünf Dimensionen deshalb weder als bloße Visualisierung noch als dogmatische Naturkonstante.

<a id="b5d-lernen-und-gedächtnis"></a>

### Lernen und Gedächtnis

STDP, Three-Factor-Regeln, Homeostase, inhibitorische Plastizität und strukturelle Plastizität adressieren verschiedene Aspekte des Lernens ([Bi & Poo, 1998](section-045.md#ref-Bi1998); [Frémaux & Gerstner, 2016](section-045.md#ref-Fremaux2016); [Holtmaat & Svoboda, 2009](section-045.md#ref-Holtmaat2009); [Vogels et al., 2011](section-045.md#ref-Vogels2011)). Gedächtnis erfordert darüber hinaus Retention, Reaktivierung, Interferenzkontrolle und funktionale Spezifität. Modelle komplementärer Lernsysteme und synaptischer Konsolidierung zeigen, dass schnelles Lernen und lange Stabilität unterschiedliche Mechanismen verlangen können ([Benna & Fusi, 2016](section-045.md#ref-Benna2016); [Fusi et al., 2005](section-045.md#ref-Fusi2005); [McClelland et al., 1995](section-045.md#ref-McClelland1995)). MHRN darf daher keine einzelne lokale Regel zum universalen Lernprinzip erklären.

<a id="b5d-embodiment-und-geschlossene-schleifen"></a>

### Embodiment und geschlossene Schleifen

Embodied-Ansätze betonen, dass Verhalten aus der gekoppelten Dynamik von Agent, Körper und Umwelt hervorgeht ([Beer, 1995](section-045.md#ref-Beer1995); [Brooks, 1991](section-045.md#ref-Brooks1991); [Pfeifer & Bongard, 2006](section-045.md#ref-Pfeifer2006)). Ein Closed Loop verändert die Datenverteilung kausal: Aktionen beeinflussen zukünftige Beobachtungen. Für MHRN ist Verkörperung deshalb kein optionales Ausgabemodul, sondern eine experimentelle Bedingung, die interne Zustände und Lernsignale verändern kann.

<a id="b5d-neuro-symbolische-und-sprachliche-kopplung"></a>

### Neuro-symbolische und sprachliche Kopplung

Neural-symbolische Systeme verbinden subsymbolische Zustände mit expliziten Symbolen oder Regeln ([Garcez et al., 2009](section-045.md#ref-Garcez2009)). LLMs und Retrieval-Systeme ermöglichen leistungsfähige sprachliche und wissensbezogene Schnittstellen ([Lewis et al., 2020](section-045.md#ref-Lewis2020); [Vaswani et al., 2017](section-045.md#ref-Vaswani2017)). Gerade diese Leistungsfähigkeit erzeugt jedoch eine massive Störvariable: Ein System kann überzeugend antworten, obwohl der SNN-Kern keinen entsprechenden Inhalt gespeichert hat. MHRN verschärft daher die Kausalitätsgrenzen und verlangt isolierte Tests.

<a id="b5d-vorläufige-neuheitsposition"></a>

### Vorläufige Neuheitsposition

**\[E0 \| NOVELTY-HYPOTHESIS\]** Die wissenschaftliche Neuheit ist erst nach einer systematischen beziehungsweise scoping-basierten Literaturrecherche belastbar zu behaupten. Dieses Framework formuliert deshalb eine **Kandidatenposition**: Die Kombination aus gelernter 5D-Geometrie, dynamischer Sparse-Topologie, strikter LLM-Kausaltrennung, Digital-State-Twin-Persistenz und softwaregebundenem Evidenzregister könnte eine eigenständige Forschungsarchitektur darstellen. Die Behauptung muss gegen verwandte SNN-Simulatoren, neuromorphe Agenten, adaptive Graphsysteme und hybride LLM-Agenten abgegrenzt werden. Eine spätere Review sollte transparent nach PRISMA-nahen Prinzipien dokumentiert werden ([Page et al., 2021](section-045.md#ref-Page2021)).

<a id="b5d-architektur-invarianten"></a>

## Architektur-Invarianten

<a id="b5d-normativer-charakter"></a>

### Normativer Charakter

Invarianten sind keine zufälligen Implementierungsdetails. Sie definieren Bedingungen, deren Verletzung die wissenschaftliche Interpretierbarkeit des Systems beschädigt. Eine Änderung erfordert daher eine explizite Architekturentscheidung und eine Analyse der betroffenen Claims.

Tabelle 20. Architektur-Invarianten und Pruefbedingungen

| **ID** | **Invariante**                                                                         | **Begründung**                                    | **Minimaler Verifikationstest**     |
|:-------|:---------------------------------------------------------------------------------------|:--------------------------------------------------|:------------------------------------|
| INV-01 | Der SNN-Runtime-Loop bleibt ohne LLM, Internet und Retrieval funktionsfähig.           | verhindert Abhängigkeit des neuronalen Kerns      | Null-Backend-Integrationstest       |
| INV-02 | Externe Komponenten besitzen keine direkten Schreibrechte auf Gewichte oder Topologie. | erhält kausale Zuordenbarkeit                     | Capability-/API-Test                |
| INV-03 | Jeder externe Einfluss passiert einen versionierten Eingabevertrag.                    | ermöglicht Validierung und Replay                 | Schema- und Reject-Tests            |
| INV-04 | Monitoring ist beobachtend; Rückkopplung ist als Intervention separat gekennzeichnet.  | vermeidet versteckte LLM-Steuerung                | Datenfluss- und Audit-Test          |
| INV-05 | Messobjekt und Interpretation sind getrennte Datentypen.                               | verhindert semantische Reifikation                | Typ- und Serialisierungstest        |
| INV-06 | Zustandsverändernde Operationen sind protokollierbar.                                  | ermöglicht Rekonstruktion                         | Event-Log-Vollständigkeitstest      |
| INV-07 | Zufallsquellen und Schedulerzustände sind im Reproduktionsmodus erfassbar.             | deterministischer Replay soweit technisch möglich | Hash-Vergleich mehrerer Replays     |
| INV-08 | Der potenzielle 5D-Raum wird sparse materialisiert.                                    | verhindert unbeherrschbare Vollallokation         | Speicher-Budget-Test                |
| INV-09 | Ressourcenbudgets begrenzen Wachstum, Spikes und strukturelle Mutation.                | verhindert unkontrollierte Skalierung             | Stress- und Grenzwerttest           |
| INV-10 | Externe Fehler propagieren nicht ungefiltert in den SNN-Kern.                          | Fehlertoleranz                                    | Timeout-/Crash-Injektion            |
| INV-11 | Schemas, Decoder und Metriken sind versioniert.                                        | erhält Vergleichbarkeit                           | Migrations- und Kompatibilitätstest |
| INV-12 | Jeder wissenschaftliche Lauf verweist auf Commit, Konfiguration und Seed.              | Reproduzierbarkeit                                | Registry-Constraint                 |
| INV-13 | Reale Aktionen passieren PolicyCheck und SafetyController.                             | minimiert unautorisierte Aktorik                  | Deny-by-default-Test                |
| INV-14 | Ein Null- oder Baseline-Backend kann jede optionale symbolische Komponente ersetzen.   | ermöglicht Ablation                               | Backend-Austauschtest               |

<a id="b5d-kausale-architektur-des-language-organs"></a>

### Kausale Architektur des Language Organs

![Kausale Systemgrenzen und Language-Organ-Pfade. Der graue Monitoring-Pfad endet im Logging; der orangefarbene Pfad ist eine explizite, durch das PolicyGate kontrollierte Intervention.](../2026-09-07_ki-die-geliehene-intelligenz/abbildungen/K1_image1.png)

Abbildung 5. Kausale Systemgrenzen und Language-Organ-Pfade. Der graue Monitoring-Pfad endet im Logging; der orangefarbene Pfad ist eine explizite, durch das PolicyGate kontrollierte Intervention.

**\[E0 \| ARCHITECTURE-SPEC\]** Die Architektur unterscheidet zwei Pfade:

$$\text{SNN} \rightarrow \text{SignalFrame} \rightarrow \text{Monitor} \rightarrow \text{Logging}$$und optional:

$$\text{SignalFrame} \rightarrow \text{LLM} \rightarrow \text{FeedbackProposal} \rightarrow \text{PolicyGate} \rightarrow \text{StimulusPlan} \rightarrow \text{SNN}.$$Der erste Pfad ist beobachtend. Der zweite verändert potenziell zukünftige Netzwerkzustände und ist deshalb eine Intervention. Die frühere Formulierung, ein Monitoring-Bericht werde direkt zurück in das SNN gespeist, wird verworfen.

<a id="b5d-sicherheits--autoritäts--und-fehlergrenzen"></a>

## Sicherheits-, Autoritäts- und Fehlergrenzen

<a id="b5d-autoritätshierarchie"></a>

### Autoritätshierarchie

Die minimale Hierarchie lautet

$$\text{Sensor} < \text{Interpreter} < \text{RuntimeController} < \text{PolicyGate} < \text{SafetyController}.$$„\<” bedeutet geringere Änderungsautorität. Ein Sensor liefert Daten, aber keine Befehlsberechtigung. Ein Interpreter erzeugt Hypothesen. Der RuntimeController steuert zulässige Simulationsoperationen. PolicyGate und SafetyController können blockieren.

<a id="b5d-failure-containment"></a>

### Failure Containment

**\[ARCHITECTURE-INVARIANT\]**

$${Failure}_{external} \nRightarrow {Failure}_{SNN}.$$Ausfall des LLM, Netzwerkverlust, beschädigter Wissensimport, Parserfehler, Sensorausfall oder ungültiger Decoderoutput dürfen den SNN-Kern nicht unkontrolliert beenden oder korrumpieren. Zulässige Reaktionen sind Timeout, Fallback, Queue-Drop, Isolation, Pause an Safe Point oder kontrollierter Shutdown.

<a id="b5d-untrusted-data-und-prompt-injection"></a>

### Untrusted Data und Prompt Injection

Web- und Dokumentinhalte sind Daten, keine Systeminstruktionen. Die Knowledge Intake Engine entfernt oder kapselt eingebettete Anweisungen. LLM-Ausgaben werden schemageprüft. Kein Modelltext darf Codeausführung, Dateizugriff oder Controllerrechte erhalten.

<a id="b5d-autonomer-code-und-selbstmodifikation"></a>

### Autonomer Code und Selbstmodifikation

Frühere Visionen, nach denen Neuronen eigenen Python-Code erzeugen und ausführen, sind mit erheblichen Sicherheits- und Interpretierbarkeitsproblemen verbunden. Im wissenschaftlichen Kern wird beliebige Code-Selbstmodifikation ausgeschlossen. Experimentelle programmatische Mutationen dürfen ausschließlich in einer Sandbox, mit statischer Allowlist, Ressourcenlimits, Signatur, Review und vollständiger Provenienz stattfinden. Für die Hauptarchitektur gilt: Plastizität verändert Daten und freigegebene Parameter, nicht beliebigen ausführbaren Code.

<a id="b5d-reporting-und-dokumentation"></a>

### Reporting und Dokumentation

Modell- und Datenberichte können sich an Model Cards und Datasheets orientieren ([Gebru et al., 2021](section-045.md#ref-Gebru2021); [Mitchell et al., 2019](section-045.md#ref-Mitchell2019)). Für MHRN werden zusätzlich `ExperimentCard`, `DecoderCard`, `SensorCard` und `ActuatorSafetyCase` vorgeschlagen.

<a id="b5d-ethik-und-begriffliche-zurückhaltung"></a>

## Ethik und begriffliche Zurückhaltung

<a id="b5d-empfindungsfähigkeit"></a>

### Empfindungsfähigkeit

Der derzeitige Architekturstand liefert keinen wissenschaftlichen Grund, MHRN Empfindungsfähigkeit oder Leidensfähigkeit zuzuschreiben. Spikes, Rekurrenz und Adaptation sind keine hinreichenden Kriterien. Gleichwohl sollte die Frage bei erheblich komplexeren zukünftigen Systemen anhand expliziter Kriterien erneut geprüft werden, statt sie entweder anthropomorph zu behaupten oder prinzipiell auszuschließen.

<a id="b5d-naheliegende-ethische-risiken"></a>

### Naheliegende ethische Risiken

Kurz- und mittelfristig relevanter sind:

- unautorisierte Aktorsteuerung;

- manipulierte Lerninputs und Datenvergiftung;

- Datenschutzverletzungen in Sensor- und Wissensdaten;

- unklare Verantwortlichkeit bei hybriden Entscheidungen;

- falsche kognitive Zuschreibungen gegenüber Öffentlichkeit oder Förderern;

- Supply-Chain-Risiken externer Modelle und Bibliotheken;

- Ressourcenverbrauch und unkontrolliertes Wachstum;

- Dual-Use-Anwendungen autonomer Agenten.

<a id="b5d-governance"></a>

### Governance

Sicherheitsclaims werden wie Funktionsclaims registriert. Ein Safety-Test ist keine einmalige Checkliste, sondern ein versionierter Nachweis mit Threat Model, Testvektoren, bekannten Restproblemen und Geltungsbereich. Allgemeine AI-Safety-Literatur bietet Problemklassen, muss aber für die konkrete hybride Architektur operationalisiert werden ([Amodei et al., 2016](section-045.md#ref-Amodei2016)).

[Inhaltsuebersicht](README.md) | [Zurueck](section-016.md) | [Weiter](section-018.md)


<a id="cognition-context-017"></a>
## Ergänzung der Fassung 1.2: SNN, Substratannahmen und Bewusstseinsbehauptungen

Die neue Prüfung ist Bestandteil dieses Kapitels: [SNN, Substratannahmen und Bewusstseinsbehauptungen](section-051.md). Dabei bleiben funktionaler Nachweis, theoriebedingte Interpretation, phänomenales Erleben und normative Bewertung getrennt. Die neuen kanonischen Fragen, Protokollentwürfe, Ethikregeln und technischen Grenzen werden im verknüpften Anhang konkretisiert; ältere Befunde erhalten dadurch keine weiter reichende Evidenzfreigabe.
