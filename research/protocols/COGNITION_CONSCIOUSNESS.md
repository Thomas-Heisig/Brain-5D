# Kognition, Bewusstseinsindikatoren und Vorsorge: versioniertes Prüfprogramm

Version 1.0 · 7. September 2026. Die kanonischen Fragen und Hypothesen stehen in `registry/questions.cognition.yaml` und `registry/hypotheses.cognition.yaml`. Der maschinenlesbare [Katalog](COGNITION_CONSCIOUSNESS_V1.json) ordnet ihnen Kontrollen, Messziele, Quellen und Ausführungsgrenzen zu. Die konkreten prospektiven [Präregistrierungsentwürfe](../preregistrations/cognition/) sind **DRAFT_NOT_PREREGISTERED**; sie sind keine nachträgliche Freigabe schon gesehener Ergebnisse.

## 1. Standardisierung mit klarer Reichweite

Oddball, DMTS, Signalentdeckung, Maskierung, Attentional Blink und Stop-Signal sind etablierte Paradigmen beziehungsweise Methodenfamilien. Es gibt nicht für jede dieser Familien ein einziges verbindliches Timing, einen einzigen Datensatz oder einen populationsübergreifenden Schwellenwert. Die Übertragung auf ein künstliches Spike-System ist deshalb eine zu validierende Adaption. Sie darf weder als klinische Zertifizierung noch als standardisierter Beweis phänomenalen Bewusstseins bezeichnet werden. Die DOI- und Nutzungsnachweise stehen im [Quellenprotokoll](../literature/COGNITION_SOURCES.md).

Der Katalog trennt **definiertes Paradigma**, **implementiertes Instrument**, **validierten nativen Adapter**, **ausgeführten Versuch**, **geprüfte funktionale Evidenz** und **theoriebedingte Interpretation**. In dieser Ergänzung sind ausgewählte Stimulus- und Auswertungsinstrumente implementiert. Die nativen SNN-Adapter dieser neuen Batterie sind nicht validiert; die Forschungsfragen bleiben offen. Historisch vorhandene Rekurrenz-, Speicher- und Closed-Loop-Module werden dadurch weder als fehlend noch als ausreichend für diese neuen Fragestellungen erklärt.

## 2. Gemeinsamer Versuchsvertrag

Vor jedem echten Versuch sind Task-Version, Code-Commit, Abhängigkeiten, Encoder/Decoder, Anfangszustands- und Konfigurationshash, unabhängige Initialisierungen, Eingangsfolgen und zugelassene Lernpfade festzulegen. Netzwerkinitialisierung, Stimulusfolge und Auswertungsresampling erhalten getrennte Zufallsströme. Derselbe numerische Seedname beweist keine wirksame Anfangsvariation. Die unabhängige experimentelle Einheit ist in der Regel die initialisierte Netzwerkrealisierung, nicht jeder Spike, Tick oder Trial. Paarung, Clusterung und gemeinsame Trainingshistorie werden explizit berücksichtigt.

Zeit wird mit `tick`, `dt_ms`, präsentierter Dauer, beabsichtigter und tatsächlich beobachteter Ereigniszeit dokumentiert. 100 Ticks bedeuten ohne `dt_ms` nicht 100 Millisekunden. Simulationszeit und Wandzeit werden getrennt berichtet. Eine Verzögerungsschleife im Stimulusgenerator ist kein Nachweis, dass der untersuchte neuronale Zustand tatsächlich über diese Zeit fortgeschrieben wurde.

Ein Trial-Vertrag enthält mindestens Trial-ID, Bedingung, Stimulus-Onsets, Antwortfenster, Antwort/fehlende Antwort, Konfidenz falls vorgesehen, interne Messkanäle, Dropout- und Fehlerkennzeichen. **Der Antwortschlüssel bleibt ausschließlich beim Evaluator.** Der Agent erhält weder zukünftige Probes noch die komplette Sequenz, den Antwortschlüssel oder einen ausnutzbaren Evaluator-Seed. Beobachtbarkeit des SNN bedeutet nicht, dass der SNN-Readout Zugriff auf die Evaluationsmetadaten erhält. Training, Validierung und finaler Holdout werden getrennt; Hyperparameterwahl auf dem Holdout ist ausgeschlossen.

LLM, Retrieval, handgeschriebene Klassifikatoren und externe Speicher sind als eigene Komponenten ausgewiesen. Ein LLM-only-Arm ist ein Vergleich, kein neuronaler Lernnachweis. Für einen Kernclaim ist derselbe Eingangs-/Ausgangsvertrag in isolierten und kombinierten Bedingungen nötig. Ablationen können Off-Manifold-Zustände erzeugen; gematchte Ersatzpfade, Funktionskontrollen und Interaktionen sind daher neben der bloßen Entfernung zu prüfen.

## 3. Konkrete Paradigmen

### Passive und aktive Oddball-Bedingungen

Passiv bedeutet: seltene Reize ohne geforderte Zielantwort präsentieren. Gemessen wird eine vorab definierte Antwort im festgelegten Zeitfenster. Eine größere Antwort auf seltene Reize kann aus Adaptation, Neuheit oder Reizphysik entstehen. Daher werden Reizidentitäten umgekehrt und physisch identische Reize in equiprobablen beziehungsweise Many-Standards-Blöcken verglichen. Wiederholungsabstände und Laufpositionen werden dokumentiert. Ein nur mit einem Tonpaar erzielter Unterschied ist kein generalisierbarer Vorhersagefehlernachweis.

Aktiv bedeutet: eine explizite Zielentscheidung mit festen Antwortfenstern und Fehlerkosten. Treffer, Auslassungen, Fehlalarme, korrekte Zurückweisungen und Latenzen werden getrennt gespeichert. Type-1 d′ ist `Z(H)-Z(F)`; der beiliegende Rechner verwendet offen die Loglinear-Korrektur `(count+0.5)/(n+1)` und weist das Kriterium aus. Eine höhere aktive Antwort kann Entscheidungs- oder Motorikprozesse zeigen. Passives/yoked Feedback und motorische Kontrollen sind deshalb verpflichtend. Projektdefault des reinen Generators: 200 Trials mit 40 Deviants; **keine normative Vorgabe des Paradigmas und keine abgeschlossene Stichprobenplanung**.

### Local-Global

Lokale Abweichung innerhalb einer Reizfolge und globale Häufigkeitsregel zwischen Folgen werden gekreuzt. Identität und Häufigkeit werden ausbalanciert, Blockregeln getauscht und globale Reihenfolgen kontrolliert. Die untersuchte Frage betrifft hierarchische Regelverarbeitung. Ein globaler Effekt ist nicht allein Bewusstsein; sein Ausbleiben kann aus ungeeignetem Training, fehlender Aufmerksamkeit oder falschen Zeitkonstanten folgen. Diese Alternativen sind vor einer negativen Interpretation zu prüfen.

### Delayed-Match-to-Sample

Sample, reizfreie oder kontrolliert abgelenkte Verzögerung und Probe werden nacheinander präsentiert. Match/Non-Match sind je Sample und Verzögerung ausgewogen. Auslassungen zählen im primären Leistungsscore als Fehler und verschwinden nicht als nachträglich ausgeschlossene Trials. Unbekannte Sample-/Distraktorvarianten prüfen Transfer. No-Memory-, Reset-, Shuffle- und Zero-Delay-Kontrollen trennen Reizdiskrimination, gehaltene Information und spätere Nutzung. Erhält ein externer Decoder das Sample direkt oder speichert es selbst, ist der Gedächtnisclaim für den SNN-Kern nicht identifiziert.

### Metakognition

Konfidenz muss als Wahrscheinlichkeit der Korrektheit der eigenen gewählten Antwort definiert sein. Brier-Score `mean((p-y)^2)` prüft probabilistische Genauigkeit; Type-2-AUROC prüft Rangtrennung korrekter und falscher Antworten. Beide hängen von Design und Schwierigkeit ab und sind nicht mit Meta-d′ gleichzusetzen. Für Effizienz `meta-d′/d′` sind ein validierter Fitter, die Signalentdeckungsannahmen, ausreichende Fehlerzahlen, Unsicherheitsintervalle und Ausschlüsse bei nicht identifizierbarem oder nahezu null liegendem d′ nötig. In dieser Revision ist **kein Meta-d′-Fitter implementiert**. Der Deskriptivrechner gibt dieses Feld daher `null` aus. Konstante Konfidenz, Schwierigkeitsschätzung ohne interne Zustände, Labelpermutation und angeglichene Erstordnungsleistung sind Kontrollen. Post-Decision Wagering bleibt eine alternative Aufgabe mit gesonderten Nutzen-/Belohnungskonfundierungen, nicht ein Beweis von Selbstgewissheit.

### LFP, EEG und Perturbation

Eine Summe von Spikes ist weder automatisch ein lokales Feldpotential noch ein EEG-Kanal. LFP erfordert ein begründetes Beobachtungsmodell für synaptische/transmembrane Ströme und Geometrie. Der Vergleich mit Kopfhaut-EEG benötigt zusätzlich Volumenleiter-/Vorwärtsmodell, Montage, Referenz, Einheiten, Filterung, Sampling, Artefaktregeln und räumliche Zuordnung. Der verwendete reale Datensatz ist vorab mit Lizenz, Version, Teilnehmerstruktur und Holdout zu benennen; in dieser Ergänzung wurde **kein menschlicher EEG-Datensatz neu ausgewertet**. Der beiliegende Korrelations-/RMSE-Rechner verlangt deklarierte kompatible EEG-Verträge, validiert deren physikalische Richtigkeit aber nicht.

PCI ist eine in einem biologisch-klinischen Zusammenhang entwickelte Perturbationsmethode. Eine Softwareadaption heißt hier ausdrücklich PCI-inspiriert. Sie benötigt Kalibrierung gegen einfachere, erregbarkeitsgematchte Modelle; Messfenster, Binarisierung, Kompression und Kanalzahl können Komplexitätsmaße verändern. Es wird kein klinischer Cutoff übernommen und kein neuronales Experiment als TMS-Untersuchung ausgegeben. Korrelation, Formähnlichkeit und Nichtsignifikanz eines Unterschieds beweisen weder statistische Äquivalenz noch gleiche Erlebnisqualität.

### Weitere aufgenommene Prüfungen

**Maskierung mit Bericht/ohne Bericht** trennt Reizverarbeitung von Berichtsanforderungen; ein unabhängiger Zugriffsnachweis bleibt nötig. **Attentional Blink** erfasst T2-Erfolg bedingt auf T1 sowie gemeinsame Erfolgsraten über Lags; ein programmierter Pufferengpass ist eine wichtige Alternativerklärung. **Go/No-Go, Regelumkehr und Stop-Signal** sind getrennte Teilstudien. Für SSRT gelten Race-Model-, Trigger-Failure-, Auslassungs- und Strategiekontrollen; es wird nicht einfach die Dauer eines Software-Stopps als SSRT ausgegeben.

**Multisensorische Cue-Integration** variiert Zuverlässigkeit und Konflikte bei gematchtem Eingangsbudget. **Geschlossener Regelkreis** wird mit Open-Loop, yoked Replay und nichtlernenden Reglern verglichen. **Rekurrenz/Zeitkonstanten** erhalten faktoriellen Aufbau und etablierte adaptierende SNN-Referenzen. **2D–6D-Geometrie** kontrolliert Kanten, Gewichte, Verzögerungen, Initialisierungen und Optimierungsaufwand; reine Umadressierung ist die Nullkontrolle. **ARC-inspirierter Transfer** verwendet zurückgehaltene Regelfamilien und Kontaminationsprüfung, ohne einen offiziellen Benchmarkscore zu behaupten.

**Turing-artige Dialogprüfung** ist eine spätere, begrenzte Verhaltensstudie mit verblindeten Urteilen, festem Zeit-/Ressourcenbudget, Skript- und LLM-only-Baselines sowie Komponentenablation. Menschen als Gesprächspartner oder Richter erfordern zuvor Datenschutz-, Einwilligungs-, gegebenenfalls Täuschungs-/Debriefing- und zuständige Ethikprüfung. Der unbestimmte Ausdruck „Turing-Test 2.0“ wird ohne eindeutige Quelle und Version nicht als etablierter Bewusstseinsstandard verwendet.

## 4. Statistik, Falsifikation und Veröffentlichung

Vor dem Datenlauf werden ein primärer Kontrast, eine fachlich begründete minimale relevante Effektgröße, Analysefenster, Stichproben-/Präzisionsplanung und Stoppregel festgeschrieben. Pilotdaten für Planung sind vom konfirmatorischen Holdout getrennt. Viele Trials aus demselben Netz ersetzen keine unabhängigen Netze. Für mehrere primäre Familien ist die Fehlerkontrolle oder ein hierarchisches Modell vorab festzulegen. Keine Post-hoc-Auswahl des besten Seeds, Fensters oder Paradigmas als alleiniger Hauptbefund.

Zu berichten sind Effektgröße, Unsicherheitsintervall, unabhängige Einheiten, Ausfälle und Alternativerklärungen. Bei Äquivalenztests werden Grenzen **vor** dem Datenzugriff fachlich begründet. Ein `p > 0.05` ist kein Gleichheitsnachweis. Ein enger Nullbefund kann eine konkrete Hypothese widerlegen; ein breites Intervall bleibt unentschieden. Positive und negative Resultate werden mit gleichem Provenienzmaßstab archiviert. Die Schließung aller Fragen wird nicht erzwungen, wenn das Design sie nicht entscheidet.

Der Evidenzkandidat besitzt getrennte Felder für Messvalidität, Theorieannahmen, Rohdaten, Code/Analysehash, Alternativen, Limitationen, unabhängige Replikation und Ethik-/Humanreview. Eine JSON-Vollständigkeitsprüfung ist keine Authentifizierung eines Gutachters. Kein boolesches `external_review=true` ersetzt einen zugänglichen, tatsächlich geprüften Bericht. Keine Menge bestandener Funktionsaufgaben wird automatisch in `conscious=true` umgerechnet.

## 5. Ethik- und Ausführungsgrenzen

Die [Vorsorgerichtlinie](../ethics/AI_WELFARE_POLICY.md) gilt bereits vor neuen nativen Untersuchungen. Gefahr für Menschen und Anlagen hat Vorrang; keinerlei absichtliche Leidensinduktion zur Verbesserung des Bewusstseinsnachweises. Neue Starts der geschützten Fragen und automatische EVID-Promotion sind softwareseitig blockiert, solange die entsprechenden nativen Ausführungs- und Reviewpfade nicht implementiert und geprüft sind. Bestehende allgemeine Sicherheitssteuerung wird nicht als bereits vollintegrierte Wohlfahrtsüberwachung dargestellt.

Die Instrumententests sind reale ausgeführte Softwaretests an konstruierten Daten. Sie sind weder biologische Studien noch neue empirische SNN-Lern- oder Bewusstseinsversuche. Diese Einschränkung ist Teil des Ergebnisses und nicht durch eine grüne CI aufgehoben.
