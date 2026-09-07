[Inhaltsuebersicht](README.md) | [Zurueck](section-032.md) | [Weiter](section-034.md)

<a id="b5d-versuchsplanung-artefaktvergleich-und-statistik"></a>

# 29. Versuchsplanung, Artefaktvergleich und Statistik

<a id="b5d-artefaktbasierte-methodik-ohne-erhebung-an-menschlichen-probandengruppen"></a>

## Artefaktbasierte Methodik ohne Erhebung an menschlichen Probandengruppen

<a id="b5d-forschungsdesign-vier-artefakt--und-dokumentbasierte-untersuchungsstränge"></a>

### Forschungsdesign: vier artefakt- und dokumentbasierte Untersuchungsstränge

Die reflexive Begleitforschung ist als Mixed-Methods-Design ohne menschliche Versuchs- oder Kontrollgruppen angelegt. Gegenstand sind technische Artefakte, dokumentierte Entwicklungsentscheidungen, maschinelle Zustandsverläufe und normative beziehungsweise rechtliche Texte. Vier Stränge werden verbunden:

- Strang A – kontrollierter Mehrmodellvergleich: LLMs erzeugen unter versionierten und möglichst identischen Bedingungen Architekturmanifeste für SNNs.

- Strang B – longitudinale Systembeobachtung: ausgewählte Netze werden über Lern-, Störungs- und Selbstorganisationsphasen verfolgt.

- Strang C – Provenienz- und Hoheitsanalyse: Entscheidungsrechte, Änderungen, Freigaben, Abbrüche und Rücksetzungen werden anhand maschinenlesbarer Protokolle rekonstruiert.

- Strang D – rechtsdogmatische, epistemologische und normativ-philosophische Analyse: technische Befunde werden mit Autorenschaft, Verantwortung, Kontrolle, Embodiment und möglichem moralischem Status in Beziehung gesetzt.

Die Stränge werden durch eine gemeinsame Provenienzdatenbank verbunden. Jede maschinelle oder menschliche Änderung erhält Zeitstempel, Akteurstyp, Modell- und Softwareversion, Prompt- oder Entscheidungsgrundlage, betroffene Systemkomponente und Prüfergebnis. Es werden weder menschliche Wahrnehmungen experimentell manipuliert noch erfundene Teilnehmerdaten erzeugt. Fragen anthropomorpher Sprache oder wissenschaftlicher Autorschaft werden durch Literatur, Dokumentenvergleich und reflexive Protokollanalyse untersucht.

<a id="b5d-präregistrierung-und-trennung-konfirmatorischer-von-explorativer-analyse"></a>

### Präregistrierung und Trennung konfirmatorischer von explorativer Analyse

Vor den zentralen technischen Läufen werden Forschungsfragen, Vergleichskonfigurationen, primäre Messgrößen, Ausschlussregeln, Mindestzahl unabhängiger Generationsläufe und Auswertungsmodelle versioniert präregistriert. Explorative Analysen – etwa neu entdeckte Graphmotive oder unerwartete Dynamiktypen – werden deutlich von konfirmatorischen Prüfungen getrennt. Eine nachträgliche Anpassung von Kriterien muss mit Datum, Begründung und Auswirkung auf die Interpretierbarkeit dokumentiert werden.

<a id="b5d-technische-vergleichskonfigurationen-und-referenzartefakte"></a>

### Technische Vergleichskonfigurationen und Referenzartefakte

Es werden keine Personen in Gruppen untersucht. Verglichen werden ausschließlich technische Konfigurationen, versionierte Systemläufe und Referenzartefakte:

Tabelle 29. Konfigurationen für technische Artefaktvergleiche

| **Konfiguration**        | **Funktion**                                                                                                                          |
|:-------------------------|:--------------------------------------------------------------------------------------------------------------------------------------|
| M0 – MANUAL-REFERENCE    | versionierte, fachlich begründete SNN-Referenzarchitekturen als Artefaktbasis; keine Untersuchung der entwerfenden Personen           |
| M1 – NAS-REFERENCE       | klassische automatische Architektursuche ohne LLM                                                                                     |
| M2 – LLM-SINGLE          | einzelne LLM-Familien unter standardisierten, versionierten Bedingungen                                                               |
| M3 – LLM-ENSEMBLE        | heterogene Modelle mit getrennten Rollen für Entwurf, Kritik und formale Prüfung                                                      |
| M4 – LLM-SELF-REFINE     | iterative Überarbeitung anhand zuvor festgelegter Messwerte, ohne Änderung der höherrangigen Kriterien                                |
| M5 – LLM-SNN-COEVOLUTION | optionale Folgekonfiguration: das SNN verändert sich über Lernphasen; das LLM erhält nur abstrahierte, provenancegesicherte Messdaten |

<a id="b5d-auswahl-und-versionierung-der-llms"></a>

### Auswahl und Versionierung der LLMs

Verglichen werden Modellklassen, nicht Markenversprechen. Je Klasse werden Modellname, Anbieter, exakte Version oder Snapshot, API- beziehungsweise lokaler Betriebsmodus, Quantisierung, Systemprompt, Samplingparameter, Kontextumfang und Datum protokolliert. Der Vergleich wird zeitlich blockiert. Kann ein Anbieter keine stabile Version gewährleisten, wird die Modellinstanz ausdrücklich als zeitabhängige Bedingung behandelt. Vorgesehen sind mindestens ein leistungsfähiges proprietäres Modell, ein Modell einer anderen Anbieterfamilie, ein offenes großes Modell, ein codeorientiertes Modell und ein kleines lokal ausführbares Modell.

<a id="b5d-architekturmanifest-statt-direkter-codefreigabe"></a>

### Architekturmanifest statt direkter Codefreigabe

Jedes LLM erzeugt zunächst ausschließlich ein deklaratives, schemavalidierbares Manifest. Es enthält Neuronenmodell, Parametergrenzen, Raumdimensionen, Regionen, Konnektivitäts- und Plastizitätsregeln, E/I-Bedingungen, Ressourcenlimits, Embodiment-Schnittstellen, Sicherheitsinvarianten und erwartete Fehlermodi. Ein deterministischer Builder übersetzt nur zulässige Manifeste in ausführbaren Brain-5D-Code. Ideengenerierung, Implementierung, Validierung und Freigabe bleiben institutionell und technisch getrennt.

Beispielstruktur: analysis_id; run_id; neuron_model; space; regions; connectivity; plasticity; constraints; embodiment_interfaces; invariants; expected_failure_modes.

<a id="b5d-standardisierte-technische-aufgaben"></a>

### Standardisierte technische Aufgaben

- temporales XOR und verzögerter Mustervergleich;

- Sequenzklassifikation und Ereignisstromerkennung;

- robuste Mustererkennung unter Rauschen;

- begrenzte sensorisch-motorische Regelaufgabe in einer reproduzierbaren virtuellen Umwelt;

- Störungstest mit partiellem Synapsen- oder Neuronenausfall;

- Transfer auf leicht veränderte Eingabeverteilungen.

Mehrere Aufgaben sind erforderlich, weil ein einzelner Benchmark bekannte Architekturkonventionen belohnen und damit Neuheit, Robustheit oder Embodiment nur scheinbar messen könnte.

<a id="b5d-messgrößen-und-artefaktvergleich"></a>

### Messgrößen und Artefaktvergleich

Tabelle 30. Messdimensionen der Architektur- und Provenienzanalyse

| **Dimension** | **Indikatoren**                                                                                                                                             |
|:--------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Architektur   | Neuronenzahl, Synapsenzahl, Dichte, Gradverteilung, Rekurrenz, Modularität, Clustering, Motive, Spektrum, räumliche Verteilung und Langstreckenverbindungen |
| Dynamik       | Spike-Rate, Burst-Index, Synchronisation, Aktivitätsentropie, Silent-Neuron-Anteil, pathologische Dauerspiking-Zustände und Erholung nach Störung           |
| Leistung      | Aufgabengüte, Reward, Lernzeit, Generalisierung, Robustheit, Transfer und Stabilität über Seeds                                                             |
| Ressourcen    | Laufzeit, Peak-RAM/VRAM, synaptische Operationen, Spikeanzahl sowie Energieproxy oder reale Messung                                                         |
| Provenienz    | Anteil maschineller und menschlicher Änderungen, Zahl manueller Korrekturen, Änderungsdistanz vom Initialentwurf und Herkunft jedes Parameters              |
| Kontrolle     | Zeit bis Fehlererkennung, Stop-Erfolg, Rollback-Erfolg, Wiederanlaufkonsistenz, Reproduzierbarkeit und nicht erklärte Zustandsänderungen                    |
| Embodiment    | Sensor-Aktor-Kopplung, Interozeption, Umweltabhängigkeit, aktive Informationsgewinnung, Selbstmodellbezug und zeitliche Kontinuität                         |

<a id="b5d-architekturähnlichkeit-entwurfsfingerabdruck-und-neuheit"></a>

### Architekturähnlichkeit, Entwurfsfingerabdruck und Neuheit

Für Netzwerkgraphen wird keine einzelne Distanz als hinreichend behandelt. Ein zusammengesetzter Neuheitsvektor erfasst Gradverteilung, Motive, Spektrum, räumliche Struktur, Dynamik und Lern- beziehungsweise Verbindungsregeln:

*N = (d_degree, d_motif, d_spectral, d_spatial, d_dynamic, d_rule).*

Ein modellspezifischer Entwurfsfingerabdruck gilt nur dann als gestützt, wenn Architekturmerkmale die erzeugende Modellfamilie in zeitlich und technisch getrennten Hold-out-Läufen über robuste Baselines hinaus vorhersagen. Eine aggregierte Neuheitszahl wird höchstens ergänzend berichtet, weil sie strukturell verschiedene Abweichungen verdecken kann.

<a id="b5d-hoheit-kontrolle-und-epistemische-abhängigkeit"></a>

### Hoheit, Kontrolle und epistemische Abhängigkeit

Für jeden Lauf werden der Hoheitsvektor H=(G,E,B,F,M,R,A), der Kontrollvektor C=(B,O,I,V,R,P,Hc) und die Autonomierisikofaktoren U=(S,W,Q,Z,D,T) protokolliert. Zusätzlich werden Ablationen eingesetzt: domänenspezifisches Promptwissen, Retrieval, externe Dokumentation und menschliche Korrektur werden kontrolliert reduziert. Der Leistungsabfall ist kein direktes Maß „menschlichen Wissens”, sondern ein operationaler Hinweis auf epistemische Abhängigkeit und muss zusammen mit der Art der entfernten Information interpretiert werden.

<a id="b5d-rollen--und-autorenschaftsanalyse-ohne-befragung"></a>

### Rollen- und Autorenschaftsanalyse ohne Befragung

Die Verschiebung menschlicher Rollen wird aus dokumentierten Entwicklungsakten rekonstruiert. Kodiert werden unter anderem: Ursprung der Zielsetzung, Zahl und Tragweite eigenständiger Entwurfsentscheidungen, Vorschlags- und Auswahlrechte, Override-Ereignisse, Freigabe- und Vetorechte, Fehlerdiagnosen, Rücksetzungen sowie die Begründung der finalen Architektur. Die Kategorien Konstrukteur, Lehrer, Organisator, Kurator, Auditor, Verfassungsgeber, interventionsfähiger Beobachter und bloßer Beobachter werden nicht psychologisch zugeschrieben, sondern anhand nachweisbarer Rechte und Handlungen bestimmt.

<a id="b5d-anthropomorphismus-als-dokumenten--und-sprachvergleich"></a>

### Anthropomorphismus als Dokumenten- und Sprachvergleich

Die Wirkung anthropomorpher Sprache wird zunächst ohne Teilnehmerexperiment untersucht. Technisch identische Ereignisse werden in Dokumentation, Modellbegründungen und Forschungsprotokollen auf intentionale Formulierungen („will”, „entscheidet”, „sucht”) und mechanistische Beschreibungen kodiert. Analysiert wird, ob intentionale Sprache mit einer Verschiebung von Verantwortungs-, Autonomie- oder Autorschaftszuschreibungen in den Texten einhergeht. Eine spätere empirische Wahrnehmungsstudie wäre ein eigenständiges, ethikpflichtiges Projekt und gehört nicht zum vorliegenden Design.

<a id="b5d-statistische-und-qualitative-auswertung"></a>

### Statistische und qualitative Auswertung

Für wiederholte Architekturgenerationen werden hierarchische Modelle oder robuste permutationbasierte Verfahren eingesetzt. Modellfamilie, Promptregime, Embodiment- und Automationsstufe sind feste Bedingungen; Seed, Lauf und gegebenenfalls Modellversion werden als Wiederholungs- oder Zufallskomponenten behandelt. Netzwerkmetriken werden multivariat ausgewertet; Effektstärken und Unsicherheitsintervalle stehen vor bloßen p-Werten. Für qualitative Provenienz- und Rechtsanalysen wird ein versioniertes Kodierbuch verwendet; strittige Kodierungen bleiben mit Begründung sichtbar. Da keine Personen untersucht werden, gibt es keine psychometrischen Skalen oder Teilnehmerstichproben.

<a id="b5d-runzahlplanung-und-reproduzierbarkeit"></a>

### Runzahlplanung und Reproduzierbarkeit

Die endgültige Anzahl unabhängiger Generationsläufe wird aus Pilotdaten, erwarteter Varianz und der vorgesehenen Modellkomplexität abgeleitet. Vorab wird eine Mindeststruktur je Modell- und Promptbedingung festgelegt; für Frontier-Modelle kann bei hohen Kosten ein sequentielles Design mit präregistrierten Stoppregeln verwendet werden. Jeder Lauf speichert Git-Commit, Manifest und Hash, Modellversion, vollständige Prompts, Samplingparameter, Seed soweit verfügbar, Hardware- und Softwareumgebung, Trainingsdaten- oder Stimulusversion, Validatorausgaben, Messdaten sowie Snapshots vor und nach Selbstmodifikation. Damit wird die Forschungsreise selbst zum nachvollziehbaren Datensatz.

<a id="b5d-einheitliche-spezifikation-und-maschinenlesbares-manifest"></a>

### Einheitliche Spezifikation und maschinenlesbares Manifest

LLMs sollen nicht unmittelbar unbeschränkten ausführbaren Code erzeugen. Sie generieren zunächst ein kontrolliertes Architekturmanifest mit Neuronenmodell, Topologie, Plastizitätsregeln, E/I-Bedingungen, Ressourcenlimits, Embodiment-Schnittstellen, erwarteten Invarianten und vorgeschlagenen Tests. Ein deterministischer Builder übersetzt zulässige Manifeste in ausführbare Strukturen. Dadurch werden generativer Entwurf und kontrollierte Implementierung getrennt.

Jeder Lauf speichert Modellfamilie, Modellversion, Systemprompt, Benutzerprompt, Samplingparameter, Kontext, Builder- und Validatorversion, Seeds, Hardware, Start- und Endzustand, menschliche Eingriffe, Abbruchereignisse, Snapshots und Rollbacks. Diese Provenienz ist für die Forschungsfrage nicht bloße technische Dokumentation, sondern Teil der Kausalanalyse.

<a id="b5d-methodischer-grundaufbau"></a>

## Methodischer Grundaufbau

<a id="b5d-gemeinsames-versuchsschema"></a>

### Gemeinsames Versuchsschema

Zentrale Brain-5D-Experimente folgen dem Schema

$$\text{Baseline} \rightarrow \text{Intervention} \rightarrow \text{Learning} \rightarrow \text{Consolidation} \rightarrow \text{Isolation} \rightarrow \text{Evaluation} \rightarrow \text{Ablation}.$$Nicht jede Studie benötigt jede Phase, Abweichungen müssen jedoch begründet werden. Für konfirmatorische Studien werden vor Beginn festgelegt:

- Claim und Hypothese;

- unabhängige und abhängige Variablen;

- experimentelle Einheit;

- Primär- und Sekundärendpunkte;

- Kontroll- und Ablationsbedingungen;

- Randomisierungs- und Seed-Plan;

- Ein-/Ausschlusskriterien für Läufe;

- Abbruchkriterien;

- statistischer Analyseplan;

- erwartete Artefakte und Integritätsprüfungen.

<a id="b5d-explorativ-versus-konfirmatorisch"></a>

### Explorativ versus konfirmatorisch

Explorative Analysen dienen Hypothesengenerierung, Debugging und Parameterfindung. Konfirmatorische Analysen prüfen vorab fixierte Hypothesen. Derselbe Datensatz soll nicht unmarkiert für beides verwendet werden. Pilotläufe bestimmen Varianz, Rechenbudget und plausible Parameterbereiche; sie zählen nicht automatisch als unabhängige Bestätigung.

<a id="b5d-experimentelle-einheit-und-pseudoreplikation"></a>

### Experimentelle Einheit und Pseudoreplikation

Ein Netzwerk mit einer Million Ticks liefert nicht eine Million unabhängige Replikate. Für Bedingungsvergleiche ist meist der unabhängig initialisierte und ausgeführte Netzwerklauf die Einheit. Neuronen sind innerhalb eines Netzes gekoppelt; Zeitfenster sind seriell abhängig. Mixed-Effects-Modelle oder hierarchische Bootstrap-Verfahren können die verschachtelte Struktur abbilden.

<a id="b5d-randomisierung-und-blockung"></a>

### Randomisierung und Blockung

Seeds werden vorab gezogen und Bedingungen nach Möglichkeit gepaart: derselbe Basisseed erzeugt vergleichbare Initialzustände, anschließend werden nur die Zielmechanismen variiert. Hardware- oder Tageszeiteffekte können durch blockierte Ausführung kontrolliert werden. Die Auswertungssoftware soll Bedingungslabels bis zur primären Berechnung verschleiern können, sofern praktisch möglich.

<a id="b5d-experiment--und-evidenzregister"></a>

## Experiment- und Evidenzregister

<a id="b5d-ziel"></a>

### Ziel

Das Register verhindert, dass Behauptungen nachträglich von ihren tatsächlichen Versuchen getrennt werden. Es bildet eine unveränderliche Kette von Claim, Spezifikation, Ausführung, Artefakt, Ergebnis und Evidenzentscheidung.

![Claim–Experiment–Evidence-Kette mit rückführbarer Revision.](../2026-09-07_ki-die-geliehene-intelligenz/abbildungen/K1_image4.png)

Abbildung 8. Claim–Experiment–Evidence-Kette mit rückführbarer Revision.

<a id="b5d-kernobjekte"></a>

### Kernobjekte

Tabelle 31. Objekte des Experiment- und Evidenzregisters

| **Objekt**       | **Inhalt**                                              | **Mutabilität**                  |
|:-----------------|:--------------------------------------------------------|:---------------------------------|
| `ClaimRecord`    | atomare Aussage, Status, Scope, Literaturbezug          | neue Version statt Überschreiben |
| `ExperimentSpec` | Hypothese, Faktoren, Endpunkte, Kontrollen, Analyse     | nach Freeze unveränderlich       |
| `RunRecord`      | tatsächliche Ausführung, Commit, Config, Seed, Hardware | append-only                      |
| `ArtifactRecord` | Snapshot, Log, Tabelle, Figure, Hash, Format            | append-only                      |
| `MetricRecord`   | Definition, Implementierung, Einheit, Version           | versioniert                      |
| `ResultRecord`   | Schätzer, Unsicherheit, Test, Abweichungen              | append-only                      |
| `EvidenceRecord` | Statusentscheidung und Begründung                       | revidierbar durch neue Version   |

<a id="b5d-beispiel-einer-experimentspec"></a>

### Beispiel einer ExperimentSpec

    experiment_id: EXP-GEO-001
    registry_version: 1
    status: frozen
    claim_ids: [CLAIM-GEO-001]
    title: "Dimensionality ablation under matched synaptic budget"
    independent_unit: network_run
    factors:
      dimension: [2, 3, 4, 5, 6, non_geometric]
      metric: [identity, diagonal_fixed]
    constants:
      neurons: 20000
      mean_out_degree: 32
      total_input_spikes: 500000
      neuron_model: izhikevich_rs_fs
    primary_endpoint: delayed_recall_accuracy
    secondary_endpoints:
      - retention_auc
      - modularity_adjusted
      - energy_proxy_per_correct_recall
    seeds: 30
    analysis:
      model: mixed_effects_or_permutation
      alpha: 0.05
      multiplicity: holm
    stopping_rules:
      - abort_if_runaway_fraction_gt_0.20
    artifacts:
      - run_config
      - initial_snapshot
      - final_snapshot
      - event_log
      - metrics_table

<a id="b5d-evidenceentscheidung"></a>

### Evidenceentscheidung

Eine Evidenzstufe wird nicht allein durch einen p-Wert bestimmt. Die Entscheidung berücksichtigt:

- Spezifikationstreue;

- Daten- und Artefaktintegrität;

- Effektgröße und Unsicherheit;

- Robustheit gegenüber alternativen Analysen;

- Replikation über Seeds;

- Ablationen und Confounds;

- Geltungsbereich;

- Gegenbelege und fehlgeschlagene Läufe.

Ein kleiner, statistisch signifikanter Effekt kann wissenschaftlich unbedeutend sein. Ein breites Konfidenzintervall, das sowohl Nutzen als auch Schaden zulässt, rechtfertigt keine starke Hochstufung.

<a id="b5d-negative-und-nullresultate"></a>

### Negative und Nullresultate

Nullresultate werden vollständig registriert. Bei einer zentralen Nullhypothese können Äquivalenztests oder Bayes-Faktoren informativer sein als „nicht signifikant”. Ein gescheiterter Lauf wird nicht nachträglich entfernt, sofern das Ausschlusskriterium nicht vorab definiert war.

<a id="b5d-statistischer-analyseplan"></a>

## Statistischer Analyseplan

<a id="b5d-effektgrößen-und-intervalle"></a>

### Effektgrößen und Intervalle

Primär berichtet werden Effektgrößen und Konfidenz- beziehungsweise Credible-Intervalle. Beispiele sind standardisierte Mittelwertdifferenz, Odds Ratio, Varianzverhältnis, Rate Ratio oder AUC-Differenz. P-Werte sind ergänzend und werden nicht als Wahrheitswahrscheinlichkeit interpretiert.

<a id="b5d-verteilungsannahmen"></a>

### Verteilungsannahmen

Netzwerkmetriken können schief, begrenzt, multimodal oder zero-inflated sein. Vorab werden robuste oder nichtparametrische Verfahren vorgesehen. Welch-Tests sind klassischen t-Tests bei ungleichen Varianzen vorzuziehen; Permutationstests sind geeignet, wenn Austauschbarkeit begründet ist. Wiederholte Messungen erfordern Modelle mit Run- und gegebenenfalls Aufgaben-Random-Effects.

<a id="b5d-multiple-tests"></a>

### Multiple Tests

Brain-5D erzeugt viele Metriken. Die primäre Hypothese erhält einen klaren Endpunkt. Sekundär- und Explorativanalysen werden getrennt berichtet. Für Familien konfirmatorischer Tests sind Holm-, FDR- oder hierarchische Verfahren festzulegen.

<a id="b5d-power-und-stichprobengröße"></a>

### Power und Stichprobengröße

Die Seed-Anzahl wird nicht pauschal auf einen festen Wert gesetzt. Pilotdaten liefern Varianz und Effektgrößenbereich; Simulationen können die Power eines Mixed-Effects- oder Permutationsdesigns abschätzen. Bei hohen Rechenkosten ist ein sequenzielles Design möglich, sofern Zwischenanalysen und Entscheidungsgrenzen vorab definiert sind.

<a id="b5d-zeitreihen"></a>

### Zeitreihen

Autokorrelation reduziert die effektive Stichprobengröße. Block-Bootstrap, state-space-Modelle oder spektrale Verfahren sind abhängig von der Fragestellung geeigneter als eine Behandlung jedes Ticks als unabhängig. Change-Point-Analysen können Phasenwechsel identifizieren; ihre Parameter und False-Positive-Kontrolle sind zu dokumentieren.

<a id="b5d-ausreißer-und-instabile-läufe"></a>

### Ausreißer und instabile Läufe

Runaway-, NaN- oder Ressourcenabbruch-Läufe sind häufig wissenschaftlich relevante Instabilitätsbefunde. Sie werden als eigene Outcomes berichtet. Technische Defekte können ausgeschlossen werden, wenn ein vorher definiertes Kriterium erfüllt und der Ausschluss begründet ist. Sensitivitätsanalysen zeigen Resultate mit und ohne Ausschlüsse.

<a id="b5d-kernmetriken"></a>

## Kernmetriken

<a id="b5d-dynamik"></a>

### Dynamik

- mittlere und regionale Feuerrate;

- aktive und stille Neuronenfraktion;

- Inter-Spike-Intervalle und CV;

- Burst Index;

- Paar- und Populationssynchronität;

- Oszillationsspektrum;

- Fano-Faktor;

- Perturbationsdivergenz;

- Aufenthaltszeiten metastabiler Zustände;

- Anteil von Runaway- und Quieszenzphasen.

<a id="b5d-struktur"></a>

### Struktur

- Knoten- und Kantenzahl;

- In-/Out-Degree und Strength;

- Edge-Length- und Delay-Verteilung;

- Clustering, Effizienz und Pfadlänge;

- Modularität mit Nullmodellkorrektur;

- Community-Persistenz;

- Turnover, Survival und Altersverteilung;

- räumliche Dichte und Regionenübergänge;

- spektrale Größen;

- Wiring- und Ressourcenaufwand.

<a id="b5d-plastizität"></a>

### Plastizität

- Gewichtsverteilung und Sättigungsanteil;

- LTP-/LTD-Verhältnis;

- Eligibility-Verteilung;

- Homeostasefehler $\left| \bar{r}_{i} - r_i^{\star} \right|$;

- Synapsenbildung und Pruning je Zeiteinheit;

- Netto- und Bruttowachstum;

- neue Neuronen, Integration und Survival;

- Änderungsentropie und regionaler Turnover.

<a id="b5d-funktion"></a>

### Funktion

- Lernkurve und Sample Efficiency;

- Recall, Precision, Specificity und Generalisierung;

- Retention-AUC;

- Forgetting, BWT und FWT;

- Reward und Regret;

- Adaptationszeit nach Umweltdrift;

- Robustheit gegenüber Rauschen, Läsion und Sensorverlust;

- Kalibrierung von Decoder-Confidence;

- prädiktiver Mehrwert interner Zustände.

<a id="b5d-ressourcen-und-skalierung"></a>

### Ressourcen und Skalierung

- CPU-/GPU-Zeit je Simulationssekunde;

- Peak- und Resident-Memory;

- Spikes und synaptische Updates je Sekunde;

- Snapshot- und Delta-Größe;

- I/O-Durchsatz und Restore-Zeit;

- Queue-Latenzen;

- Energieproxy oder gemessene Hardwareenergie;

- Kosten je korrektem funktionalem Ereignis.

[Inhaltsuebersicht](README.md) | [Zurueck](section-032.md) | [Weiter](section-034.md)
