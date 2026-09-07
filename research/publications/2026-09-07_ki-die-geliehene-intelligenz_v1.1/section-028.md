[Inhaltsuebersicht](README.md) | [Zurueck](section-027.md) | [Weiter](section-029.md)

<a id="b5d-vier-aktuelle-ergebnislinien-und-ihre-grenzen"></a>

# 24. Vier aktuelle Ergebnislinien und ihre Grenzen

<a id="b5d-exp-snn-001-r2-aktive-stabilität-und-widersprüchliche-freigabe"></a>

## EXP-SNN-001-R2: aktive Stabilität und widersprüchliche Freigabe

Der Summary-Bericht weist **20 Durchläufe**, zehn Seeds von 42 bis 51 und je **100.000 ausgeführte Ticks** aus. Das Protokoll heisst `sustained_activity_stability_v1`; verglichen werden `no_input_control` und `tonic_drive` mit Drive 50,0, 10.000 Burn-in-Ticks und 1.000-Tick-Fenstern. Laufmodus ist `CONFIRMATORY`, Netzwerkmodus `OFFLINE`, Tickvertrag `SATISFIED`. Der im Bericht genannte Run-Commit ist `4cfcaf64e55b5c33f6fd818605a39da2c92871f9`, bei `git dirty = true`. \[R3\]

Der empirische Manuskriptnachtrag berichtet **20/20 Stabilitätspässe**, keine Laufzeitfehler, für den tonic-drive-Arm **300 Spikes pro 1.000-Tick-Fenster**, Variationskoeffizient 0 und relative Drift 0. Die zehn Kontrollen ohne Input bleiben ruhig. Diese speziellen Ergebnisgrößen stammen aus K3; im generischen Summary stehen die Spalten zu Spikezahl und Synapsenereignissen teilweise auf fehlend. Die fehlenden generischen Felder werden nicht mit Null ersetzt und nicht als Gegenbeweis zu den speziellen Kennzahlen interpretiert. \[K3, empirischer Nachtrag; R3\]

Zugleich klassifiziert derselbe Repository-Bericht die Zuordnung als `MISMATCH` und die Freigabereife als `BLOCKED_SEMANTIC_MISMATCH`. Die Begründung verlangt ein dediziertes Sustained-Activity-Protokoll, obwohl ein entsprechend benanntes Protokoll bereits ausgewiesen ist. Das ist ein **offener interner Dokumentations- beziehungsweise Klassifikationskonflikt**. Aus dem Widerspruch allein lässt sich weder schliessen, der Lauf sei wissenschaftlich unbrauchbar, noch, das Gate sei nur kosmetisch falsch. Erforderlich ist eine Prüfung der Protokollkennung, registrierten Conditions, Endpunkte und Gate-Regeln an der tatsächlichen Run-Codebasis. \[R3\]

Die zulässige Aussage bleibt eng: Ein kontrollierter kleiner Versuchsaufbau wurde über das registrierte Tickbudget ausgeführt; der Nachtrag berichtet stabile Messgrößen. Eine Freigabe für die allgemeine Hypothese langfristig stabiler Brain-5D-Dynamik ist daraus noch nicht abzuleiten. Auch CV = 0 bedeutet nur, dass die ausgewertete Größe in diesen Fenstern keine Variation zeigt. Ob der Zustand reichhaltig, anpassungsfähig oder lediglich periodisch ist, prüft eine andere Metrik.

<a id="b5d-exp-repl-0001-r1-klarer-rekurrenzeffekt-in-engem-scope"></a>

## EXP-REPL-0001-R1: klarer Rekurrenzeffekt in engem Scope

Der Replikationsbericht umfasst **40 Läufe über 20 Seedlabels** von 42 bis 61, jeweils 256 Ticks, zwei Conditions und das Protokoll `independent_replication_v1`. Die semantische Zuordnung lautet `DIRECT_MATCH`; die Evidenzfreigabe ist wegen `BLOCKED_DIRTY_SOURCE_TREE` gesperrt. Der Run-Commit lautet `48dacb9ce26e68f39d2d63f1b82c8a9192ee8185`. Ein passender Protokollname ist damit vorhanden, eine saubere freigegebene Replikation ist aber nicht bereits durch den Namen garantiert. \[R4\]

Tabelle 27. Berichteter Rekurrenzvergleich

| Messgröße                    | Rekurrenz aus | Rekurrenz an | Differenz / Verhältnis          |
|:-----------------------------|--------------:|-------------:|:--------------------------------|
| Spikes                       |             3 |           33 | +30; Faktor 11                  |
| Synaptische Ereignisse       |             2 |           33 | +31; Faktor 16,5                |
| Aktivierte Neuronen          |             3 |            3 | 0; Faktor 1                     |
| Rekurrenzereignisse          |             0 |           10 | +10; Verhältnis nicht definiert |
| Berichtete Propagationstiefe |             1 |           61 | +60; Faktor 61                  |
| Ticks                        |           256 |          256 | gleiches Beobachtungsbudget     |

Die Zahlen sind über die berichteten Seedlabels identisch. Das stützt die Reproduzierbarkeit des beobachteten kleinen Modellablaufs unter diesen Bedingungen. Es zeigt für sich genommen nicht, dass die Seeds in allen relevanten Anfangsgrößen unterschiedliche Realisierungen erzeugten. Identische Outcomes schliessen echte unabhängige Variation nicht aus, belegen sie aber auch nicht. Die zur Unabhängigkeitsprüfung notwendigen Anfangszustands-, Topologie-, Input- und RNG-Nachweise bleiben von den Outcome-Tabellen getrennt zu prüfen.

Die berichtete Propagationstiefe 61 darf in einem Modell mit drei aktivierten Neuronen nicht als 61 verschiedene anatomische Schichten oder 61 zusätzliche Neuronen beschrieben werden. Sie ist eine operative Kennzahl mit möglichen rekurrenten Wiederbesuchen. Für eine weitere Interpretation ist ihre konkrete Berechnung im Instrumentierungsvertrag maßgeblich.

Die gepoolten Inter-Spike-Intervalle betragen im Kontrollarm n = 40 mit Mittelwert 1 Tick; im Rekurrenzarm n = 640 mit Mittelwert 1,9375 Ticks, Median 2 und Spannweite 1 bis 4 Ticks. Diese Intervalle sind **keine 640 unabhängigen Netzwerke**. Ein Inferenztest, der jedes Intervall als vollständig unabhängige Replikation behandelte, würde die verschachtelte Datenstruktur ignorieren. Die primäre Versuchseinheit muss vorab festgelegt und gegebenenfalls auf der Ebene unabhängiger Initialisierungen ausgewertet werden. \[R4\]

<a id="b5d-exp-life-0001-r1-erfolgreicher-vorläuferscreen-offene-interferenzfrage"></a>

## EXP-LIFE-0001-R1: erfolgreicher Vorläuferscreen, offene Interferenzfrage

Das Protokoll `learning_interference_screen_v1` ist explorativ. Es verwendet 20 Seedlabels und die Condition `sequential_three_task_screen`. Der Tickvertrag lautet ausdrücklich `NOT_APPLICABLE`; die angeforderte Zahl 1 ist deshalb nicht als ein einziger neuronaler Simulationsschritt für einen Gedächtnistest zu interpretieren. Auch dieser Lauf ist semantisch passend, aber wegen Dirty-Tree-Provenienz blockiert. \[R12\]

Der Manuskriptnachtrag berichtet für alle drei Tasks in allen Läufen Erfolg und eine retained success fraction von 1,0. Zwischen den unabhängigen Task-Instanzen wird transienter neuronaler Zustand zurückgesetzt; gelernte Gewichte bleiben protokollspezifisch erhalten. Der Nachtrag begrenzt selbst die Aussage: Der Test ist kein Nachweis gegen katastrophales Vergessen in einem gemeinsam sequenziell weitertrainierten Netzwerk. \[K3, empirischer Nachtrag\]

Ein echter Continual-Learning-Test braucht eine explizite Leistungs-Matrix. Wird nach Training bis Task j die Leistung auf Task i gemessen, sei dies A(i,j). Dann kann ein vorab definiertes Vergessensmass beispielsweise den Rückgang gegenüber einer früheren besten Leistung quantifizieren. Entscheidend sind gemeinsamer Netzwerkträger, Reihenfolge, Lernbudget, unveränderte Evaluation und Kontrollen für Task-Aehnlichkeit. Ein Reset ist nicht grundsätzlich unzulässig; er muss jedoch dieselbe untersuchte Bedeutung von Persistenz in allen Armen bewahren. Ein als “lebenslang” bezeichneter Test darf nicht stillschweigend genau die Interferenz beseitigen, die er messen soll.

<a id="b5d-exp-gen-0033-r1-eine-diagnostische-suite-mit-passender-gesamtfrage"></a>

## EXP-GEN-0033-R1: eine diagnostische Suite mit passender Gesamtfrage

Die spätere Suite verwendet `RQ-SUITE-001`, `H-SUITE-001-A` und `science_all_v1`. Der Bericht dokumentiert **57 Teilruns**, die Seeds 42, 43 und 44 und eine semantische Zuordnung `DIRECT_MATCH`. Anders als eine pauschale Zuordnung der gesamten Suite zu einer einzelnen Stabilitätshypothese passt die Infrastrukturfrage zum heterogenen Umfang. Trotzdem bleibt die Freigabe wegen Dirty-Tree-Provenienz blockiert. Der Run-Commit lautet `0c64eb428430fcf0627715989857c875d674a74c`. \[R5\]

Die Suite enthält PING, zeitliche Zustände, STDP, Learning, Regulation, Dimensionsvergleiche und eine Zeit-Leiter. Das 100.000-Tick-Fenster gilt für die ausgewiesenen tickgebundenen SNN-Arme; die Timingbedingungen umfassen 100, 1.000, 10.000 und 100.000, während trialbasierte Verfahren nicht ohne Weiteres in diese Tickspanne eingehen. Deshalb ist “57 Läufe mit jeweils 100.000 Ticks” keine korrekte Gesamtzusammenfassung.

Die Suite ist ein wertvoller Test der gemeinsamen Ausführbarkeit und Berichtsstruktur. Sie ist jedoch nicht 57-fache Evidenz für jede der enthaltenen Forschungsfragen. Für eine hypothesenspezifische Auswertung müssen die jeweils passenden Teilbedingungen, Kontrollgruppen und experimentellen Einheiten aus dem gemeinsamen Herkunftskontext isoliert werden.

<a id="b5d-gemeinsames-ergebnis-ohne-künstliche-hochstufung"></a>

## Gemeinsames Ergebnis ohne künstliche Hochstufung

Die vier Ergebnislinien zeigen unterschiedliche Fortschritte: aktiven Langzeitbetrieb eines begrenzten Runners, rekurrente Veränderung der Impulsantwort, positiven Erfolg eines Vorläuferscreens und gemeinsame diagnostische Ausführung. Gemeinsam sind ihnen offene Freigabe- und Provenienzfragen. Keine der vier Linien beantwortet allein, ob Brain-5D generalisierbares Gedächtnis, eigenes Weltverstehen, Bewusstsein oder eine besondere Überlegenheit fünfdimensionaler Organisation besitzt. Diese Begrenzung nimmt den Daten nicht ihren Wert. Sie bestimmt vielmehr, welche nächsten Experimente durch sie begründet werden.

[Inhaltsuebersicht](README.md) | [Zurueck](section-027.md) | [Weiter](section-029.md)
