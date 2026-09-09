# Connectomics und geschlossene sensorimotorische Forschung in MHRN

## Ergaenzung der wissenschaftlichen Abhandlung: Rekursive Epistemik

**Stand: 9. September 2026. KI-generierter, noch nicht unabhaengig begutachteter Forschungszusatz.**
Diese Ergaenzung ist ein versionierter Entwicklungsstand, keine neue bestaetigte Evidenz.
Die kapitelweise Edition 1.3 und alle historischen DATA/EVID bleiben unveraendert.
Massgeblich sind die kanonischen Forschungsregister, die einzelnen Protokolle und die
jeweiligen Laufartefakte. Die Zustimmung zur technischen Implementierung ersetzt
keine protokollspezifische wissenschaftliche Begutachtung.

## 1. Literaturbefund und Korrektur der Ausgangsannahmen

Ein anatomisches Connectome beschreibt rekonstruierte Verschaltungen. Ein dynamisches
Neuronenmodell ergaenzt Annahmen zu Membranpotentialen, Gewichten, Verzoegerungen und
Transmitterwirkungen. Ein Koerpermodell beschreibt Gelenke, Kontakte und Kraefte.
Erst die tatsaechliche Rueckwirkung ausgefuehrter Aktionen auf neue Sensordaten schliesst
den sensorimotorischen Kreis. Keine dieser Ebenen allein belegt vollstaendige biologische
Gleichwertigkeit, Lernen, subjektiven Schmerz oder Bewusstsein.

Dorkenwald et al. (2024) behandeln das weibliche FlyWire-Gehirn. Berg et al. (2026)
behandeln das maennliche Zentralnervensystem einschliesslich ventralem Nervenstrang.
Die Cell-Veroeffentlichung ist vom 3. September 2026; Janelia dokumentiert jedoch bereits
MaleCNS v0.9 vom 3. Oktober 2025 und v1.0 vom 8. Juni 2026. Publikationsdatum und
Datensatzfreigabe sind verschieden. Der publizierte Abstract nennt 166700 Neuronen.
Die frueher genannte Zahl 166691 darf nicht versionsunabhaengig festgeschrieben werden.
Es wurde hier kein biologischer Grossdatensatz geladen. Auch etwa 125 Millionen
Synapsen sind keine gemessene Importgroesse dieses Projekts. [Dorkenwald2024; Berg2026; MaleCNS]

Shiu et al. modellieren ausgewaehlte sensorimotorische Transformationen mit einem
LIF-Netzwerk und pruefen Vorhersagen biologisch. MHRNs Izhikevich-Netz mit uebernommener
Topologie waere zunaechst eine Modellvariante, keine exakte Reproduktion dieser Arbeit.
NeuroMechFly v2 und das Ganzkoerper-Lokomotionsmodell sind eigenstaendige Arbeiten zu
Koerper, Sensoren und Steuerung. Sie duerfen weder miteinander noch mit einem
vollstaendig rekonstruierten funktionalen Gehirn gleichgesetzt werden.
[Shiu2024; WangChen2024; Vaxenburg2025]

Eons technischer Bericht vom 10. Maerz 2026 beschreibt eine verkoerperte Demonstration
mit vorhandenen Bewegungscontrollern, teils manuellen Gehirn-Koerper-Zuordnungen und
ungefaehr 15 ms Kopplung. Dieser Unternehmensbericht ist keine unabhaengige Replikation.
Der Nutzen fuer MHRN liegt vor allem darin, solche verborgenen Leistungsbeitraege
experimentell zu trennen. Vorhandene Controller sind nicht per se ein Fehler; ihre
Leistung darf nur nicht als Lernen des zentralen SNN ausgegeben werden. [Eon2026]

Connectome-beschraenkte, auf Aufgaben trainierte Modelle des visuellen Systems liefern
einen weiteren methodischen Vergleich. Ihre trainierten Parameter und ihre spezifische
Aufgabe sind Teil des Erklaerungsmodells; das ist kein direkter Beleg fuer eine beliebige
raumdimensionale SNN-Architektur. [Lappalainen2024]

## 2. Uebertragbare Prinzipien und klare Nicht-Uebertragungen

| Externes Prinzip | MHRN-Ergaenzung | Grenze |
| --- | --- | --- |
| Geschlossener Koerperkreis | SNN-Aktion veraendert Gelenkzustand, dieser veraendert Eingangsstrom | Handentworfene Fehlerkodierung und Motorabbildung sind Mitursachen |
| Getrennte sensorische Bahnen | Propriozeption, Kontakt und interne Zustaende als explizite MSBA-Anschluesse | Nicht alle Modalitaeten sind im kleinen Gelenkversuch vorhanden |
| Unterlagerte Motorik | Controller-only und unterbrochene Motorverbindung als Kontrollen | Keine anatomische Homologie zu menschlichem Rueckenmark |
| Empirische Graphstruktur | Opt-in-Referenzimport mit Original-IDs und Transformationsprotokoll | Synthetische Testmotive sind keine Fliegendaten |
| Strukturerhaltende Kontrollen | Gerichtete Rewiring-, Gewichts- und Zufallskontrollen | Gradverteilung allein kontrolliert nicht alle physiologischen Eigenschaften |
| Mehrere Zeitskalen | Fixer neuronaler Schritt, getrennte Physik- und Sensorabtastung | Batchgeschwindigkeit ist keine neue Integrationskonstante |
| Plastizitaet und innere Zustaende | Eigene noch offene Lern-, Homoeostase- und Transferhypothesen | Noch kein neuer Nachweis produktiven Lernens |

Eine UMAP-/t-SNE-Anordnung begruendet keine menschliche Neuroanatomie. Ein humanoider
Umriss ist nur ein Layout. Aus Fliegenverschaltungen folgt ohne unabhaengige Validierung
keine Vorhersage menschlicher Verschaltungsdichten oder medizinischer Eigenschaften.
Das Projekt behauptet weder eine wissenschaftliche Erstleistung noch eine Ueberlegenheit
von 5D gegenueber 3D, 4D oder Zufallsnetzen. Diese Frage bleibt mit RQ-5D-005 verbunden.
Der kanonische produktive Kern und sein Speicherformat werden hier nicht migriert.

## 3. Implementierter Minimalversuch

Die produktive Architektur bleibt erhalten. Der neue experimentelle Pfad benutzt
MHRNs vorhandenen NeuralNetwork-Kern mit sechs Izhikevich-Neuronen und sechs gerichteten
Synapsen. Die Koordinaten sind (6,1,1,1,1): Dies ist ein Integrationsfixture, kein Test
mehrdimensionaler Geometrie. STDP und strukturelle Plastizitaet sind fuer diese
Kontrollversuche deaktiviert. Weder LLM noch externe Netze entscheiden ueber Aktionen.

Die Schleife lautet:

`Ziel und Koerper -> explizite Fehler-/Geschwindigkeitskodierung -> SNN -> gefilterte Ausgangsspikes -> Drehmoment -> Gelenk -> neue Propriozeption`.

Das Gelenkmodell verwendet einen deklarieren Traegheitsparameter von 0.00005 kg m^2,
eine Daempfung von 0.002 N m s, ein Aktuatormomentlimit von 0.015 N m und Winkelgrenzen
von -0.75 bis +0.75 rad. Diese Werte sind Konstruktionsannahmen des Fixtures, keine
biologischen Messdaten. Der Sollwinkel wechselt von +0.25 zu -0.25 rad in der zweiten
Haelfte. Eine externe Stoerung ist fuer die Hauptlaeufe gleich; Donoraufzeichnungen
entstehen in einem ausdruecklich bezeichneten ungestoerten Vorlauf.

Der Eingangsfehler wird mit Faktor 70, die Winkelgeschwindigkeit mit Faktor 1.5 und
ein tonischer Antrieb mit 2 kodiert. Der Aktuatordecoder filtert Spikes mit Faktor 0.95
und skaliert mit 0.008 N m pro Decoder-Einheit. Diese Abbildung ist handentworfen. Der
Controller-only-Vergleich umgeht den SNN-Ausgang mit einem expliziten PD-Regler; das
SNN laeuft zur gleichen Rechenbudgetierung weiter. Alle diese Annahmen werden im Lauf
als effective_config und boundary_contract aufgezeichnet.

Als primaere Leistungsmetrik dient

`RMSE = sqrt(sum_t (q_t - q_target,t)^2 / T)` in rad.

Zusaetzlich werden tatsaechlich ausgefuehrte Ticks, Spikeanzahl, aktivierte Neuronen,
zugestellte synaptische Ereignisse, nichtnull Aktuatorbefehle, Kontakte, Saettigungen und
Zustandspruefsummen erfasst. Modellierte absolute mechanische Arbeit ist
`sum |tau_actuator * Delta q|`. Sie ist weder signierte Nettoarbeit noch gemessene
GPU-/Rechnerenergie. measured_hardware_energy_j bleibt null, solange nicht gemessen.
Kontakt-/Integritaetszaehler sind technische Zustaende, keine Schmerzdiagnose.

Gehirn-, Koerper- und Decoderzustand bleiben getrennt identifizierbar. Ein eigener
DATA/gateway_state.json-Sidecar ergaenzt die kanonischen SNN-Digests. Dieser Sidecar
behauptet noch keine vollstaendige speicherbare Wiederaufnahme eines Gelenkversuchs.
Die vorhandene DATA-v2-Aufteilung bewahrt Rohdaten und erzeugt begrenzte KI-Pakete.

## 4. Forschungsfragen, Hypothesen und Ausfuehrungsstatus

Neun Fragen und zwoelf Hypothesen kommen hinzu. RQ-EMB-001, RQ-REG-002 und RQ-MSBA-E05
werden mit jeweils einer neuen Hypothese erweitert, nicht dupliziert. Sechs Protokolle
sind native explorative Versuche. Sechs weitergehende Entwuerfe sind im Programm
sichtbar, aber absichtlich nicht als ausfuehrbarer Standardversuch registriert.
Eine generische Tick-/PING-Ausfuehrung darf ihre fehlende Operationalisierung nicht
verdecken. Alle Hypothesen bleiben ungetestet im Sinne akzeptierter wissenschaftlicher
Evidenz; Entwicklungs-Smokes aktualisieren diesen Status nicht.

| Frage / Hypothese | Protokoll | Vergleich | Status |
| --- | --- | --- | --- |
| RQ-EMB-001 / H-EMB-001-B | `embodied_closed_loop_v1` | closed_loop, yoked_replay, feedback_absent | Ausfuehrbare Entwicklungspruefung |
| RQ-EMB-002 / H-EMB-002-A | `embodied_proprioception_v1` | closed_loop, feedback_absent, delayed_proprioception, timing_shuffle | Ausfuehrbare Entwicklungspruefung |
| RQ-EMB-003 / H-EMB-003-A | `embodied_mapping_learning_v1` | plasticity_on, frozen_snn, frozen_gateway, random_gateway, shuffled_reward | Gesperrter Entwurf |
| RQ-EMB-004 / H-EMB-004-A | `embodied_perturbation_screen_v1` | closed_loop, weak_actuator, blocked_joint, restored_actuator | Ausfuehrbare Entwicklungspruefung |
| RQ-MSBA-E05 / H-MSBA-E05-B | `embodied_sensor_compensation_v1` | adaptive, fixed, shuffled_compensation, no_compensation, noisy_area_suppression | Gesperrter Entwurf |
| RQ-REG-002 / H-REG-002-B | `embodied_homeostasis_v1` | body_modulation, frozen_modulation, shuffled_modulation, task_reward_baseline | Gesperrter Entwurf |
| RQ-EMB-007 / H-EMB-007-A | `embodied_efference_copy_v1` | efference_copy, no_copy, shuffled_copy, delayed_copy | Gesperrter Entwurf |
| RQ-EMB-008 / H-EMB-008-A | `embodied_morphology_transfer_v1` | adaptive, frozen, reinitialized, random_gateway | Gesperrter Entwurf |
| RQ-CONN-001 / H-CONN-001-A | `connectome_reference_replication_v1` | matched_lif_reference, weight_shuffle, transmitter_sensitivity, izhikevich_model_variant | Gesperrter Entwurf |
| RQ-CONN-002 / H-CONN-002-A | `connectome_topology_screen_v1` | structured, degree_preserving, weight_shuffle, random_edges | Ausfuehrbare Entwicklungspruefung |
| RQ-EMB-009 / H-EMB-009-A | `embodied_controller_attribution_v1` | closed_loop, disconnected_motor, controller_only, shuffled_motor | Ausfuehrbare Entwicklungspruefung |
| RQ-TIME-002 / H-TIME-002-A | `embodied_timing_v1` | batch_1, batch_16, batch_128, physics_5ms, physics_15ms, sensor_5ms, sensor_15ms | Ausfuehrbare Entwicklungspruefung |

Die Propriozeptionsfrage untersucht Entfernen, 20-Tick-Verzoegerung und zeitliche
Vertauschung einer deklarierten Donoraufzeichnung. Open-loop-Replay ist keine
identische kontrafaktische Welt: Die sensorischen Konsequenzen koennen nach einer
Stoerung von denen eines geschlossenen Regelkreises abweichen. Donorart und
zusaetzlicher Rechenaufwand werden deshalb aufgezeichnet.

Die Stoerungsfrage prueft ein geschwaechtes Moment, eine Gelenkblockade und eine spaetere
Wiederherstellung. Das Netzwerk bleibt unveraendert; beobachtete Erholung ist keine
gelernte Adaptation. Erst ein separat kontrollierter Plastizitaetsversuch kann diese
Aussage pruefen. Der Topologieversuch haelt Knoten- und Kantenanzahl, Gewichts- und
Verzoegerungsmultimengen konstant; degree-preserving erhaelt auch gerichtete Ein- und
Ausgangsgrade. Erhaelte ein Rewiring keine tatsaechliche Aenderung, wird der Versuch
abgewiesen. Die derzeitige synthetische Struktur ist nicht aus Fliegenmotiven gewonnen.

## 5. Offene Lern- und Koerperhypothesen

**Sensorimotorisches Mapping:** Spontane motorische Exploration soll in einer spaeteren
Behandlung gelernt werden. Gegenkontrollen muessen eingefrorenes SNN, eingefrorenes
Gateway, zufaelliges Gateway und zerstoerte Reward-Zuordnung enthalten. Trainierbare
Peripherie bekommt eigene Seeds, Modellhashes, Zustand und Budget. Ein vortrainierter
Controller ist eine eigene Behandlung, kein unsichtbarer Bestandteil des SNN.

**Homoeostase:** Energie, Belastung und Integritaet koennen als explizite Koerperzustaende
in eine Drei-Faktor-Regel eingehen, beispielsweise `Delta w_ij = eta * e_ij * M`.
Dies ist eine zu pruefende Modellentscheidung. Ein interner Modulator ist weiterhin ein
definiertes Optimierungssignal; interne Herkunft beweist weder Autonomie noch Verhalten
ohne Zielvorgabe. Leistungsgewinn ist gegen feste Setpoints, eingefrorenes Lernen und
Signalzerstoerung bei gleichem Budget zu testen. Subjektiver Schmerz wird nicht postuliert.

**Efferenzkopie:** Aktionen und spaetere sensorische Konsequenzen koennen ein explizites
Vorhersagemodell liefern. Der Test benoetigt getrennte Trainings- und Holdout-Folgen,
zeitlich vertauschte Aktionskopien und einen Vergleich ohne Aktionsinformation.
Vorhersagegenauigkeit ist ein funktionaler Messwert, kein Bewusstseinsmass.

**Morphologietransfer:** Gleicher Ausgangscheckpoint, veraenderte Gelenklaengen oder
Traegheiten, unabhaengige Koerper-Holdouts und gleiches Adaptationsbudget sind erforderlich.
Fehlgeschlagene Anpassungen werden nicht entfernt. Die Schwaechung eines festen Reglers
ist nur eine Vorstufe, nicht die Durchfuehrung dieser Transferstudie.

**Sensorverlust / MSBA:** RQ-MSBA-E05 bleibt die gemeinsame Frage. Der neue Entwurf
verknuepft sie mit geschlossenen Koerperaufgaben und den festen, vertauschten und
fehlenden Kompensationskontrollen. Die uebrigen MSBA-Fragen E01-E04 behalten ihre
bestehenden Protokolle: Aufgabenleistung pro deklariertem Ressourcenbudget,
Allokationskontrollen, ROI-/Foveationskontrollen und exakte digitale Integritaet.
Informationserhalt wird nicht durch eine hohe Aktivitaet ersetzt. Ein Quotient
Energie/nuetzliche Information braucht zuerst eine taskbezogene Definition des Nenners
und eine saubere Trennung modellierter und gemessener Energie.

## 6. Zeitskalen und Reproduzierbarkeit

Der neuronale Schritt bleibt 1 ms. Physik- und Sensorperioden variieren als ausdrueckliche
Behandlungen zwischen 1, 5 und 15 Ticks. Ausfuehrungsbatches von 1, 16 und 128 Ticks
veraendern nur die Abarbeitung und muessen denselben abgeschlossenen Zustand ergeben.
Auch nicht durch die Batchgroesse teilbare Tickzahlen werden getestet. Browser und
Render-Framerate sind kein Taktgeber. Der Real-Time-Factor ist simulierte Zeit geteilt
durch reale Rechenzeit; er ist keine Neudefinition von dt.

Die sechs Versuche sind reine Offline-Experimente. Sie aendern weder den globalen
Geschwindigkeitsregler noch alle bestehenden Laufzeitpfade. Bitweise Gleichheit
ueber unterschiedliche Hardware oder GPU-Kernels wird nicht behauptet. Fuer spaetere
Live-Sensoren muessen Zeitstempel, Pufferverluste und Nichtdeterminismen als eigene
Beobachtungen eingefuehrt werden.

## 7. Statistischer Plan und Abbruchregeln

Drei gepaarte Seeds pro Arm dienen der technischen Durchfuehrungspruefung. Unabhaengige
Seeds, nicht einzelne Spikes, Neuronen oder Zeitpunkte, bilden die Inferenz-Einheiten.
Alle Vergleiche bleiben explorativ; aus drei Smoke-Seeds werden keine Signifikanz-
oder Generalisierungsaussagen konstruiert. Negative Effekte werden gleichberechtigt
berichtet. Ein spaeterer konfirmatorischer Plan braucht vorab Effektdefinition,
Fallzahl-/Praezisionsanalyse, Holdout, Multiplizitaetsregel und menschliche Begutachtung.
Die im Design genannte Mindestzahl 20 ersetzt keine solche Fallzahlplanung.

Laeufe haben feste Tickfenster, keine erfolgsabhaengigen Abbrueche. Nichtfinite Zustaende,
Vertragsverletzungen und beschaedigte Eingaben fuehren zu Fehlern mit erhaltenem Audit.
Seeds werden nicht stillschweigend ersetzt. Das Programm sperrt neue Studien bei
bestehenden Ethik-Stopps. Abschaltung und Isolation bleiben davon unabhaengig moeglich.
Ein technischer PASS aendert weder EvidenceEngine-Status noch eine akzeptierte Antwort.

## 8. Visualisierung: das Wesen als lesende Messansicht

Die vorhandene Wesen-Seite bleibt bestehen. Neue Legenden trennen strukturelle
Konnektivitaet, gemessene Aktivitaet, protokollierte Plastizitaet und experimentelle
Kausalitaet. Eine Verbindung ist noch kein Informationsfluss; ein Sankey-Wert muss
als Kantenanzahl, Gewichtssumme oder Ereigniszahl benannt werden. Er ist ohne weitere
Definition kein Informationsmass.

Null, boolesche Werte und leere Zeichenketten werden nicht laenger als numerische Null
interpretiert. Fehlgeschlagene oder ueberholte Abfragen duerfen keine alten Messwerte
weiter als aktuell ausgeben. Datenquellenstatus wird als NO_DATA, PARTIAL_DATA oder
LIVE_RUNTIME gezeigt. LIVE_RUNTIME bedeutet dabei erfolgreiche Abfrage beobachteter
Laufzeitdaten, nicht validierte Biologie. Ein Empfangszeitpunkt ersetzt noch keinen
vollstaendigen Zeitstempel des Sensors.

Das Layout darf koerperaehnlich sein, besitzt aber keine neuen behaupteten Organe.
Vier getrennte Ebenen bleiben das Ausbauziel: Struktur, Aktivitaet, Plastizitaet und
Koerperkopplung. Ein klickbarer Bezug auf Experimentartefakte nutzt den zentralen
File Viewer. Separate Modi fuer MHRN live, aufgezeichnete Experimente und biologische
Referenzen sind ein dokumentierter naechster Schritt, kein bereits geliefertes
3D-Avatar- oder Replay-System. Zufallsleuchten, EEG-/fMRI-Etiketten und anatomische
Homologie aus einem Layout sind ausgeschlossen.

## 9. Referenzimport und Replikationsgrenze

Der neue Importer liest ausschliesslich ein explizit ausgewaehltes lokales JSON-Teilnetz.
Er verlangt SHA-256, Original-IDs, Herkunft, Datensatzversion, Lizenz, Abrufdatum,
Auswahlregel, Transformationsangaben, Neuronenmodell und Interpretation von Gewichten,
Verzoegerungen und Transmittern. Grenzen fuer Dateigroesse, Knoten, Kanten und Werte
werden vor Rueckgabe geprueft. Es gibt keinen automatischen Vollimport und keinen
Schreibzugriff auf den produktiven Kern.

Ein Label BIOLOGICAL_REFERENCE ist eine deklarierte Herkunft, noch keine unabhaengige
Quellenpruefung. Der biologische Replikationsversuch bleibt bis zur beschafften,
lizenzierten Referenz, exakt passenden Modellparametern und unabhaengigen Zielwerten
gesperrt. Eine Teilnetzreplikation wuerde nur den konkret getesteten Modellbereich
validieren, nicht die gesamte Engine, Anatomie oder kuenftige Aufgaben.

## 10. Versionierung, Wissen und Roadmap

Design-Dateien sind durch einen versionierten SHA-256-Lock verbunden. Entwicklungs-
Smokes waehrend der Implementierung sind offengelegt; der Lock ist keine nachtraegliche
konfirmatorische Praeregistrierung. Spaetere Aenderungen benoetigen neue Versionen und
begruendete Review-Schritte. Die Messwerte speichern den tatsaechlichen Konfigurations-
und Quellstand. Ausfuehrbare Funktionen werden gegen den im Prozess geladenen Bytecode
geprueft, damit ein alter Dashboard-Prozess keine neue Quellversion vortaeuscht.

Das Wissensregister bewahrt Publikationstyp, Datum, URL, Verifikationsumfang und
Limitationen auch im API-Export. Der Claim-Ledger kennzeichnet falsche fruehere
Zuschreibungen und nicht abgeleitete Aussagen. Quellenwissen wird nicht als vom SNN
erworbenes Wissen ausgegeben. Die Forschung wird dadurch erweitert, nicht umetikettiert.

Die weitere Reihenfolge ist: kontrollierter Koerperkreis, sensorimotorisches Lernen,
Homoeostase, multimodale Kompensation, Transfer und Selbstvorhersage. Bestehende Sprach-
und Wissenskomponenten werden nicht entfernt. Das Language Organ bleibt im produktiven
System begrenzt; LLM-gestuetzte Steuerung waere ein eigenes AI-as-treatment-Experiment.

## Literatur und Quellenstatus

Die folgenden Angaben wurden anhand der zugaenglichen Primaerquellen geprueft.
Der Umfang dieser Pruefung ist Metadaten- und Inhaltspruefung, keine Replikation.
Die maschinenlesbaren Angaben stehen in `research/registry/sources.connectome.yaml`.

**[Dorkenwald2024]** Dorkenwald, S. and others. *Neuronal wiring diagram of an adult brain*. Nature (2024). 10.1038/s41586-024-07558-y

Quelle: https://www.nature.com/articles/s41586-024-07558-y
Typ: peer_reviewed; geprueft am 2026-09-09.
Grenze: An anatomical adult female brain connectome; not a functional brain upload.

**[Shiu2024]** Shiu, P. K. and others. *A Drosophila computational brain model reveals sensorimotor processing*. Nature (2024). 10.1038/s41586-024-07763-9

Quelle: https://www.nature.com/articles/s41586-024-07763-9
Typ: peer_reviewed; geprueft am 2026-09-09.
Grenze: LIF simulation with connectivity and inferred transmitter signs; tested feeding/grooming predictions. Limited neuron/synapse dynamics and no complete behavioral equivalence.

**[WangChen2024]** Wang-Chen, S. and others. *NeuroMechFly v2: simulating embodied sensorimotor control in adult Drosophila*. Nature Methods (2024). 10.1038/s41592-024-02497-y

Quelle: https://www.nature.com/articles/s41592-024-02497-y
Typ: peer_reviewed; geprueft am 2026-09-09.
Grenze: Neuromechanical body, sensors and explicit controllers. Controller performance is not automatically connectome performance.

**[Lappalainen2024]** Lappalainen, J. K. and others. *Connectome-constrained networks predict neural activity across the fly visual system*. Nature (2024). 10.1038/s41586-024-07939-3

Quelle: https://www.nature.com/articles/s41586-024-07939-3
Typ: peer_reviewed; geprueft am 2026-09-09.
Grenze: Connectivity plus task constraints for visual-system models; not topology alone or human anatomical homology.

**[Vaxenburg2025]** Vaxenburg, R. and others. *Whole-body physics simulation of fruit fly locomotion*. Nature (2025). 10.1038/s41586-025-09029-4

Quelle: https://www.nature.com/articles/s41586-025-09029-4
Typ: peer_reviewed; geprueft am 2026-09-09.
Grenze: Whole-body locomotion with learned controllers; distinct from the body actually used by Eon.

**[Berg2026]** Berg, S. and others. *Sexual dimorphism in the complete Drosophila male central nervous system connectome*. Cell (2026). 10.1016/j.cell.2026.08.015

Quelle: https://www.sciencedirect.com/science/article/pii/S0092867426009426
Typ: peer_reviewed; geprueft am 2026-09-09.
Grenze: Male brain and nerve cord; published summary counts 166700 neurons. Version-specific anatomy, not a complete functional simulation.

**[Eon2026]** Eon Systems research team. *How the Eon Team Produced a Virtual Embodied Fly*. None (2026). None

Quelle: https://eon.systems/updates/embodied-brain-emulation
Typ: company_technical_report; geprueft am 2026-09-09.
Grenze: Integration demonstration: LIF brain, NeuroMechFly, imitation-trained controllers, manual mappings, 15 ms coupling; learning/internal states largely absent. Visual activity not yet a substantial behavioral driver in this report.

**[MaleCNS]** HHMI Janelia FlyEM. *Male CNS Connectome: data and release history*. None (2026). None

Quelle: https://www.janelia.org/project-team/flyem/male-cns-connectome
Typ: official_dataset_documentation; geprueft am 2026-09-09.
Grenze: v0.9 released 2025-10-03; v1.0 released 2026-06-08; CC-BY. Release date is distinct from Cell publication date.
