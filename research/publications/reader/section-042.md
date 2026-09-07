[Inhaltsuebersicht](README.md) | [Zurueck](section-041.md) | [Weiter](section-043.md)

<a id="b5d-anhang-b---forschungsfragen-und-hypothesen-im-projektregister"></a>

# Anhang B - Forschungsfragen und Hypothesen im Projektregister

<a id="b5d-kanonisches-fragen--und-hypothesenregister"></a>

## Kanonisches Fragen- und Hypothesenregister

Die folgenden Kurzfassungen sind redaktionelle Synopsen, kein bytegetreuer Ersatz der versionierten YAML-Dateien. Sie bewahren IDs und unterscheiden den gelesenen Registry-Status von der Bewertung dieser Abhandlung. Die Fragen stehen im gelesenen Register auf open; zwei zugeordnete technische Hypothesen tragen supported. Die genaue Freigabe eines Befunds folgt aus den jeweiligen Artefakten, nicht aus seiner Aufnahme in diese Tabelle. \[R2; R6; R13\]

<a id="b5d-rq-snn-001---langfristig-stabile-spike-dynamik"></a>

### RQ-SNN-001 - Langfristig stabile Spike-Dynamik

**Hypothese:** `H-SNN-001-A`. Brain-5D erzeugt über mindestens 100.000 Simulations-Ticks stabile Spike-Dynamiken ohne numerische Drift.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** K3 berichtet 20/20 Stabilitätspässe; R3 weist semantischen Blocker und Dirty Tree aus. Keine Freigabe.

<a id="b5d-rq-snn-002---reproduzierbare-spikefolgen-bei-identischem-input"></a>

### RQ-SNN-002 - Reproduzierbare Spikefolgen bei identischem Input

**Hypothese:** `H-SNN-002-A`. Das Izhikevich-Neuronenmodell erzeugt bei identischem Input reproduzierbare Spikefolgen.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Technischer Restore-Nachweis vorhanden; nicht jede weitergehende notwendige Zustandsbedingung einzeln bewiesen.

<a id="b5d-rq-det-001---determinismus-bei-gleichem-seed-input-und-anfangszustand"></a>

### RQ-DET-001 - Determinismus bei gleichem Seed, Input und Anfangszustand

**Hypothese:** `H-SNN-003-A`. Bei gleichem Seed, Input und Anfangszustand sind Spike-Abfolgen deterministisch identisch.

**Registry:** Frage `open`; Hypothese `supported`. **Einordnung:** Technischer Restore-Nachweis vorhanden; nicht jede weitergehende notwendige Zustandsbedingung einzeln bewiesen.

<a id="b5d-rq-snn-003---topologieabhängige-signalpropagation"></a>

### RQ-SNN-003 - Topologieabhängige Signalpropagation

**Hypothese:** `keine zugeordnet`. Keine Hypothese in der gelesenen Fragenzuordnung hinterlegt.

**Registry:** Frage `open`; Hypothese `None`. **Einordnung:** Im hier untersuchten Material kein passender freigegebener Ergebnisnachweis.

<a id="b5d-rq-snn-004---stdp-und-gewichtsverteilung"></a>

### RQ-SNN-004 - STDP und Gewichtsverteilung

**Hypothese:** `H-SNN-004-A`. STDP führt zu einer messbaren asymmetrischen Verschiebung der synaptischen Gewichtsverteilung.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** EXP-GEN-0021 enthält ein sekundär berichtetes lokales Lernsignal. Kein Generalisierungs- oder Langzeitnachweis.

<a id="b5d-rq-snn-005---stdp-und-funktionale-lernleistung"></a>

### RQ-SNN-005 - STDP und funktionale Lernleistung

**Hypothese:** `H-SNN-005-A`. Ein Netzwerk mit STDP zeigt signifikant bessere Lernleistung als ein Netzwerk ohne STDP.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** EXP-GEN-0021 enthält ein sekundär berichtetes lokales Lernsignal. Kein Generalisierungs- oder Langzeitnachweis.

<a id="b5d-rq-ping-001---reproduzierbare-impulsantwort"></a>

### RQ-PING-001 - Reproduzierbare Impulsantwort

**Hypothese:** `H-PING-001-A`. Identische Impulse erzeugen bei identischem Anfangszustand dieselbe beobachtete Response-Signatur.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** 3 gegen 33 Spikes bei drei aktiven Neuronen; Freigabe blockiert, Initialisierungsvariation gesondert zu prüfen.

<a id="b5d-rq-temp-001---fast--medium--und-slow-zustandsvergleiche"></a>

### RQ-TEMP-001 - FAST-, MEDIUM- und SLOW-Zustandsvergleiche

**Hypothese:** `H-TEMP-001-A`. Die Temporal-State-Vergleiche unterscheiden sich deterministisch nach FAST-, MEDIUM- und SLOW-Horizont.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Horizontabhängige Zustandsabweichung berichtet, dabei null Spikes. Kein Arbeitsgedächtnisnachweis.

<a id="b5d-rq-time-001---durchsatz-und-zustände-in-einer-tick-leiter"></a>

### RQ-TIME-001 - Durchsatz und Zustände in einer Tick-Leiter

**Hypothese:** `H-TIME-001-A`. Die Tick-Leiter liefert reproduzierbare Durchsatz- und Zustandsmessungen bis 1.000.000 Ticks.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Suite-Ausführung dokumentiert; einzelne Fachhypothesen und Maximalbudgets nicht dadurch bestätigt.

<a id="b5d-rq-reg-001---regulation-bei-nominaler-chronischer-und-unbekannter-telemetrie"></a>

### RQ-REG-001 - Regulation bei nominaler, chronischer und unbekannter Telemetrie

**Hypothese:** `H-REG-001-A`. Chronischer Druck erhöht deterministisch Resource Pressure und Thermal Threat, während unbekannte Telemetrie Unsicherheit erhält.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Nominal-/Druck-/Unknown-Verhalten als Diagnose; kein isolierter Closed-Loop-Nutzennachweis.

<a id="b5d-rq-stdp-001---timingabhängige-ltp-ltd-asymmetrie"></a>

### RQ-STDP-001 - Timingabhängige LTP-/LTD-Asymmetrie

**Hypothese:** `H-STDP-001-A`. Pair-based STDP erzeugt bei definierten Pre/Post-Abständen asymmetrische Anpassung: LTP bei positivem und LTD bei negativem Delta t.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** EXP-GEN-0021 enthält ein sekundär berichtetes lokales Lernsignal. Kein Generalisierungs- oder Langzeitnachweis.

<a id="b5d-rq-stdp-002---langzeitverhalten-stdp-getriebener-gewichte"></a>

### RQ-STDP-002 - Langzeitverhalten STDP-getriebener Gewichte

**Hypothese:** `H-STDP-002-A`. STDP-getriebene Gewichte konvergieren unter Dauerstimulation zu einer stabilen Verteilung.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Im hier untersuchten Material kein passender freigegebener Ergebnisnachweis.

<a id="b5d-rq-hom-001---homöostatische-begrenzung-der-feuerrate"></a>

### RQ-HOM-001 - Homöostatische Begrenzung der Feuerrate

**Hypothese:** `H-HOM-001-A`. Synaptische Homeostase hält die mittlere Feuerrate eines SNN innerhalb eines definierten Sollbereichs.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Im hier untersuchten Material kein passender freigegebener Ergebnisnachweis.

<a id="b5d-rq-hom-002---zusammenspiel-von-homeostase-und-stdp"></a>

### RQ-HOM-002 - Zusammenspiel von Homeostase und STDP

**Hypothese:** `H-HOM-002-A`. Homeostase und STDP wirken synergistisch; Homeostase verhindert STDP-induzierte Drift.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Im hier untersuchten Material kein passender freigegebener Ergebnisnachweis.

<a id="b5d-rq-5d-001---dynamik-in-5d-gegenüber-2d3d"></a>

### RQ-5D-001 - Dynamik in 5D gegenüber 2D/3D

**Hypothese:** `H-5D-001-A`. Ein 5D-angeordnetes Netzwerk zeigt signifikant andere Dynamik als ein 2D/3D-Netzwerk gleicher Neuronenzahl.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Im kleinen Impulstest gleiche Kennzahlen. Dimensionsspezifischer funktionaler Vorteil nicht gezeigt.

<a id="b5d-rq-5d-002---dimensionalität-und-propagationszeit-reichweite"></a>

### RQ-5D-002 - Dimensionalität und Propagationszeit/-reichweite

**Hypothese:** `H-5D-002-A`. Signalpropagationszeit und -reichweite skalieren mit der Dimensionalität des Netzwerks.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Im kleinen Impulstest gleiche Kennzahlen. Dimensionsspezifischer funktionaler Vorteil nicht gezeigt.

<a id="b5d-rq-5d-003---dimensionalität-und-modularität"></a>

### RQ-5D-003 - Dimensionalität und Modularität

**Hypothese:** `H-5D-003-A`. 5D-Netzwerke entwickeln eine höhere Modularität als niedrigdimensionale Netzwerke.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Im hier untersuchten Material kein passender freigegebener Ergebnisnachweis.

<a id="b5d-rq-5d-004---informationstragende-oder-redundante-zusatzdimensionen"></a>

### RQ-5D-004 - Informationstragende oder redundante Zusatzdimensionen

**Hypothese:** `H-5D-004-A`. Die zusätzlichen Dimensionen in 5D sind informationstragend und nicht redundant.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Im kleinen Impulstest gleiche Kennzahlen. Dimensionsspezifischer funktionaler Vorteil nicht gezeigt.

<a id="b5d-rq-storage-001---verlustfreie-speicherung-und-wiederherstellung"></a>

### RQ-STORAGE-001 - Verlustfreie Speicherung und Wiederherstellung

**Hypothese:** `H-STOR-001-A`. Ein vollständiger neuronaler Zustand kann verlustfrei im .b5d-Format gespeichert und zurückgeladen werden.

**Registry:** Frage `open`; Hypothese `supported`. **Einordnung:** 15 Speicher-Tests bestanden, ein 50k-Smoke-Test übersprungen. Registry supported; enger Testscope.

<a id="b5d-rq-storage-002---notwendige-zustände-für-kausale-fortsetzung"></a>

### RQ-STORAGE-002 - Notwendige Zustände für kausale Fortsetzung

**Hypothese:** `H-STOR-002-A`. Neuron-State, Synapsen-State, Eligibility-Traces, RNG-State und Event-Queue müssen für kausale Fortsetzung gespeichert werden.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Technischer Restore-Nachweis vorhanden; nicht jede weitergehende notwendige Zustandsbedingung einzeln bewiesen.

<a id="b5d-rq-storage-003---speicherdichte-bei-wachsender-neuronenzahl"></a>

### RQ-STORAGE-003 - Speicherdichte bei wachsender Neuronenzahl

**Hypothese:** `H-STOR-003-A`. Die Speicherdichte des .b5d-Formats skaliert sublinear mit der Neuronenzahl.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Im hier untersuchten Material kein passender freigegebener Ergebnisnachweis.

<a id="b5d-rq-storage-004---speicherung-grosser-netzwerke"></a>

### RQ-STORAGE-004 - Speicherung grosser Netzwerke

**Hypothese:** `H-STOR-004-A`. Das .b5d-Format skaliert auf mindestens 50 Millionen Neuronen ohne Leistungseinbruch.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Im hier untersuchten Material kein passender freigegebener Ergebnisnachweis.

<a id="b5d-rq-scale-001---dynamikerhalt-beim-skalieren"></a>

### RQ-SCALE-001 - Dynamikerhalt beim Skalieren

**Hypothese:** `H-SCALE-001-A`. Brain-5D skaliert von 5.000 auf 1.000.000 Neuronen ohne qualitative Änderung der Spikedynamik.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Im hier untersuchten Material kein passender freigegebener Ergebnisnachweis.

<a id="b5d-rq-self-001---spontane-funktionale-cluster"></a>

### RQ-SELF-001 - Spontane funktionale Cluster

**Hypothese:** `H-SELF-001-A`. In Brain-5D entstehen spontan funktionale Cluster durch lokale STDP-Regeln.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Im hier untersuchten Material kein passender freigegebener Ergebnisnachweis.

<a id="b5d-rq-self-002---emergenz-oder-architekturfolge"></a>

### RQ-SELF-002 - Emergenz oder Architekturfolge

**Hypothese:** `H-SELF-002-A`. Die beobachtete Selbstorganisation ist emergent und nicht durch die Architektur vorgegeben.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Im hier untersuchten Material kein passender freigegebener Ergebnisnachweis.

<a id="b5d-rq-struct-001---funktionaler-nutzen-struktureller-plastizität"></a>

### RQ-STRUCT-001 - Funktionaler Nutzen struktureller Plastizität

**Hypothese:** `H-STRUCT-001-A`. Pruning/Sprouting führt zu messbar verbesserter Netzwerkeffizienz.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Im hier untersuchten Material kein passender freigegebener Ergebnisnachweis.

<a id="b5d-rq-mem-001---synaptisches-speichern-und-gezielter-abruf"></a>

### RQ-MEM-001 - Synaptisches Speichern und gezielter Abruf

**Hypothese:** `H-MEM-001-A`. Brain-5D kann Informationen über synaptische Gewichte speichern und auf Input-Muster abrufen.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Speicherfunktion ist kein isolierter Erinnerungsabruf. Passender Funktionsnachweis offen.

<a id="b5d-rq-emb-001---zielgerichtete-sensor-aktor-schleife"></a>

### RQ-EMB-001 - Zielgerichtete Sensor-Aktor-Schleife

**Hypothese:** `H-EMB-001-A`. Brain-5D kann in einer geschlossenen Sensor-Aktor-Schleife zielgerichtet agieren.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Im hier untersuchten Material kein passender freigegebener Ergebnisnachweis.

<a id="b5d-rq-llm-001---kommunikation-durch-das-language-organ"></a>

### RQ-LLM-001 - Kommunikation durch das Language Organ

**Hypothese:** `H-LLM-001-A`. Ein Language Organ kann SNN-Zustände in sinnvolle natürliche Sprache übersetzen.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Im hier untersuchten Material kein passender freigegebener Ergebnisnachweis.

<a id="b5d-rq-eth-001---autorenschaft-von-brain-5d-erkenntnissen"></a>

### RQ-ETH-001 - Autorenschaft von Brain-5D-Erkenntnissen

**Hypothese:** `H-ETH-001-A`. Autorenschaft ist ein verteiltes Phänomen zwischen Mensch, Modell und System.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Begriffliche beziehungsweise normative Untersuchung; nicht mit Spike-Metriken bestätigbar.

<a id="b5d-rq-eth-002---kontrolle-und-verantwortung"></a>

### RQ-ETH-002 - Kontrolle und Verantwortung

**Hypothese:** `H-ETH-002-A`. Die Kontrolle über Experimente liegt primär beim Entwickler, nicht beim automatisierten System.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Begriffliche beziehungsweise normative Untersuchung; nicht mit Spike-Metriken bestätigbar.

<a id="b5d-rq-epist-001---systemerkenntnis-gegenüber-forschererkenntnis"></a>

### RQ-EPIST-001 - Systemerkenntnis gegenüber Forschererkenntnis

**Hypothese:** `H-EPIST-001-A`. Systemerkenntnis und Forschererkenntnis sind kategorial unterscheidbar.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Begriffliche beziehungsweise normative Untersuchung; nicht mit Spike-Metriken bestätigbar.

<a id="b5d-rq-air-001---methodische-fehlererkennung-durch-researchpacket"></a>

### RQ-AIR-001 - Methodische Fehlererkennung durch ResearchPacket

**Hypothese:** `H-AIR-001-A`. Ein strukturierter Scientific Research Assistant erzielt einen höheren F1-Score für vorab definierte Defekte als dasselbe Modell mit unstrukturiertem Bericht.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Im hier untersuchten Material kein passender freigegebener Ergebnisnachweis.

<a id="b5d-rq-suite-001---vollständige-konsistente-suite-diagnostik"></a>

### RQ-SUITE-001 - Vollständige, konsistente Suite-Diagnostik

**Hypothese:** `H-SUITE-001-A`. Alle Teilprotokolle erfüllen ihre Ausführungsverträge und erzeugen auswertbare DATA-, Statistik- und Provenienzartefakte.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Suite-Ausführung dokumentiert; einzelne Fachhypothesen und Maximalbudgets nicht dadurch bestätigt.

<a id="b5d-rq-rec-001---rekurrenzstärke-delay-und-persistenzgrenzen"></a>

### RQ-REC-001 - Rekurrenzstärke, Delay und Persistenzgrenzen

**Hypothese:** `H-REC-001-A`. Rekurrenzgewicht und Delay erzeugen reproduzierbare Übergänge zwischen Erlöschen, transienter Aktivität und Aktivität bis zum Beobachtungsende.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** 3 gegen 33 Spikes bei drei aktiven Neuronen; Freigabe blockiert, Initialisierungsvariation gesondert zu prüfen.

<a id="b5d-rq-gen-001---lernen-auf-echten-holdout--und-perturbationsproben"></a>

### RQ-GEN-001 - Lernen auf echten Holdout- und Perturbationsproben

**Hypothese:** `H-GEN-001-A`. Learning-on verbessert registrierte Perturbationsproben gegenüber Learning-off und Sham-Replay.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Im hier untersuchten Material kein passender freigegebener Ergebnisnachweis.

<a id="b5d-rq-repl-001---rekurrenzeffekt-unter-unabhängiger-initialisierung"></a>

### RQ-REPL-001 - Rekurrenzeffekt unter unabhängiger Initialisierung

**Hypothese:** `H-REPL-001-A`. Der Rekurrenzbehandlungseffekt bleibt über mindestens 20 registrierte Initialisierungsseeds in Richtung und Größenordnung konsistent.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** 3 gegen 33 Spikes bei drei aktiven Neuronen; Freigabe blockiert, Initialisierungsvariation gesondert zu prüfen.

<a id="b5d-rq-5d-005---5d-unter-topology-matched-kontrollen"></a>

### RQ-5D-005 - 5D unter topology-matched Kontrollen

**Hypothese:** `H-5D-005-A`. Mindestens eine registrierte Propagationsmetrik unterscheidet sich in 5D von topology-matched niedrigdimensionalen Einbettungen.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Im kleinen Impulstest gleiche Kennzahlen. Dimensionsspezifischer funktionaler Vorteil nicht gezeigt.

<a id="b5d-rq-reg-002---regulation-und-funktionale-recovery"></a>

### RQ-REG-002 - Regulation und funktionale Recovery

**Hypothese:** `H-REG-002-A`. Der registrierte Regulationsfeedbackpfad verbessert Recovery nach identischer Druckphase gegenüber Regulation-off.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Im hier untersuchten Material kein passender freigegebener Ergebnisnachweis.

<a id="b5d-rq-temp-002---spike-getragene-zeitliche-reihenfolge"></a>

### RQ-TEMP-002 - Spike-getragene zeitliche Reihenfolge

**Hypothese:** `H-TEMP-002-A`. Forward-, Reverse- und Simultanfolgen erzeugen bei gleicher Ereignisanzahl unterscheidbare spike-basierte Antwortsignaturen.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Im hier untersuchten Material kein passender freigegebener Ergebnisnachweis.

<a id="b5d-rq-perf-001---subsystemkosten-vollständiger-science-läufe"></a>

### RQ-PERF-001 - Subsystemkosten vollständiger Science-Läufe

**Hypothese:** `H-PERF-001-A`. Neben dem Core-Tick-Loop ist mindestens ein weiterer gemessener Subsystemanteil relevant.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Im hier untersuchten Material kein passender freigegebener Ergebnisnachweis.

<a id="b5d-rq-rec-002---loop-delay-und-skalierte-rekurrenz"></a>

### RQ-REC-002 - Loop-Delay und skalierte Rekurrenz

**Hypothese:** `H-REC-002-A`. Größere rekurrente Delays verändern Persistenzdauer oder Propagation Depth gegenüber dem Delay-1-Kontrollarm.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Im hier untersuchten Material kein passender freigegebener Ergebnisnachweis.

<a id="b5d-rq-life-001---retention-und-interferenz-sequenzieller-lernaufgaben"></a>

### RQ-LIFE-001 - Retention und Interferenz sequenzieller Lernaufgaben

**Hypothese:** `H-LIFE-001-A`. Zu prüfen ist die Veränderung zuvor erworbener Leistung durch nachfolgende Aufgaben; erster Runner bleibt ein Vorläuferscreen.

**Registry:** Frage `open`; Hypothese `untested`. **Einordnung:** Retained success fraction 1,0 im Manuskriptnachtrag; kein gemeinsames Continual-Learning-Netz nachgewiesen.

<a id="b5d-rq-msba-e01---ressourcenverbrauch-von-audio--vision--und-digital-gateways-pro-nutzbarer-information-oder-korrekter-entscheidung"></a>

### RQ-MSBA-E01 - Ressourcenverbrauch von Audio-, Vision- und Digital-Gateways pro nutzbarer Information oder korrekter Entscheidung

**Hypothese:** `H-MSBA-E01-A`. Unter kontrollierter Aufgabeninformation unterscheiden sich Audio-, Vision- und Digital-Gateways reproduzierbar in Energie- und Synapsenkosten pro korrekter Entscheidung. \[R15; Originalwortlaut des Registers.\]

**Registry:** Frage `open`; Hypothese `untested`; `evidence: []`. **Einordnung:** Kein bestätigender Nachweis in den gelesenen Fragmenten. Adaptive Teilpfade sind teilweise noch nicht als Runner operationalisiert. \[R13; R15\]

<a id="b5d-rq-msba-e02---nutzen-kostenadaptiver-statt-fixer-oder-zufälliger-allokation-bei-gleichem-gesamtbudget"></a>

### RQ-MSBA-E02 - Nutzen kostenadaptiver statt fixer oder zufälliger Allokation bei gleichem Gesamtbudget

**Hypothese:** `H-MSBA-E02-A`. Adaptive Utility-minus-Cost-Allokation erzielt bei gleichem Ressourcenbudget hoehere Aufgabenleistung oder laengere funktionsfaehige Laufzeit als fixe und zufaellige Kontrollen. \[R15; Originalwortlaut des Registers.\]

**Registry:** Frage `open`; Hypothese `untested`; `evidence: []`. **Einordnung:** Kein bestätigender Nachweis in den gelesenen Fragmenten. Adaptive Teilpfade sind teilweise noch nicht als Runner operationalisiert. \[R13; R15\]

<a id="b5d-rq-msba-e03---entwicklung-nutzungsabhängiger-visueller-roifoveation-ohne-hart-codierte-zielregion"></a>

### RQ-MSBA-E03 - Entwicklung nutzungsabhängiger visueller ROI/Foveation ohne hart codierte Zielregion

**Hypothese:** `H-MSBA-E03-A`. Adaptive visuelle ROI-Allokation konzentriert Ressourcen auf aufgabenrelevante Regionen und verbessert Leistung pro Ressourceneinheit gegenueber einer zufaelligen ROI-Kontrolle. \[R15; Originalwortlaut des Registers.\]

**Registry:** Frage `open`; Hypothese `untested`; `evidence: []`. **Einordnung:** Kein bestätigender Nachweis in den gelesenen Fragmenten. Adaptive Teilpfade sind teilweise noch nicht als Runner operationalisiert. \[R13; R15\]

<a id="b5d-rq-msba-e04---exakte-digitale-payload-integrität-bei-drosselung-nur-durchsatz-und-admission-sinken"></a>

### RQ-MSBA-E04 - Exakte digitale Payload-Integrität bei Drosselung; nur Durchsatz und Admission sinken

**Hypothese:** `H-MSBA-E04-A`. Ressourcen-Drosselung reduziert die zugelassene Symbolrate, erzeugt aber keine Mutation der digitalen Payload oder ihrer Checksumme. \[R15; Originalwortlaut des Registers.\]

**Registry:** Frage `open`; Hypothese `untested`; `evidence: []`. **Einordnung:** Kein bestätigender Nachweis in den gelesenen Fragmenten. Adaptive Teilpfade sind teilweise noch nicht als Runner operationalisiert. \[R13; R15\]

<a id="b5d-rq-msba-e05---gezielte-modalitätsübergreifende-kompensation-bei-ausfall-oder-degradation"></a>

### RQ-MSBA-E05 - Gezielte modalitätsübergreifende Kompensation bei Ausfall oder Degradation

**Hypothese:** `H-MSBA-E05-A`. Nach kontrolliertem Modalitaetsausfall steigt die alternative Gateway-Allokation nur bei guenstigem Utility-Kosten-Verhaeltnis und verbessert die Aufgaben-Recovery gegenueber fixen und No-Compensation-Kontrollen. \[R15; Originalwortlaut des Registers.\]

**Registry:** Frage `open`; Hypothese `untested`; `evidence: []`. **Einordnung:** Kein bestätigender Nachweis in den gelesenen Fragmenten. Adaptive Teilpfade sind teilweise noch nicht als Runner operationalisiert. \[R13; R15\]

[Inhaltsuebersicht](README.md) | [Zurueck](section-041.md) | [Weiter](section-043.md)
