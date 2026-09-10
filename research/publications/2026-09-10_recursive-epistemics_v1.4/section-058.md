# Beobachtungen, Fehlversuche und begrenzte Schlussfolgerungen

KI-unterstuetzte nachtraegliche Auswertung. Explorative DATA, keine akzeptierte EVID, kein Peer-Review oder externes Ethikvotum.

## Native synaptische Assoziation

Zehn gepaarte Initialisierungs-/Umwelt-Seeds und 40 neue balancierte Testepisoden je Seed und Arm. Learning-on erreicht im Mittel 78,5 Prozent Genauigkeit, jeder der vier Kontrollarme 50 Prozent. Differenz: 28,5 Prozentpunkte; punktweises 95-Prozent-Bootstrapintervall [20;37] Prozentpunkte; exakter zweiseitiger Vorzeichenwechseltest p=0,001953125, Holm-p=0,0078125. Sensitivitaet des Lernarms: 0,57; falsch-positive Rate: 0.

Die Testgewichte sind eingefroren, Testnetze frisch initialisiert, kein Teacher-Strom und keine Lernengine waehrend der Tests. Kontrollen: Learning-off, Sham-Replay, Gewichtsreset und Permutation desselben Gewichtsmultisets. 400 verschiedene Testepisoden werden bedingungsuebergreifend gepaart; die 2000 Arm-Episoden sind keine 2000 unabhaengigen Netzinitialisierungen. Vier identische Kontrollausgaenge sind auch keine vier unabhaengigen Replikationen.

Dieser positive Befund stuetzt einen begrenzten Mechanismus angeleiteter, reward-/eligibility-vermittelter synaptischer Anpassung im nativen SNN. Er belegt keine autonome Zielbildung, allgemeine Kognition, langfristiges Gedaechtnis oder sensorimotorische Generalisierung. Die Aufgabe und die Eingabepopulationen sind konstruiert; externe Instruktion waehrend der Akquisition wird offengelegt.

## Reale Dimensionsablation

2D, 3D, 4D, 5D, 6D und 8D erzeugen tatsaechlich unterschiedliche gerichtete Nachbarschaftsgraphen. Pro Bedingung: 128 Neuronen, 1024 Kanten, Ausgangsgrad acht, Gewicht 20, gleiche Verzoegerungsbudgets und Eingabe-/Ausgabeknoten. Die sechs Labels eines identischen 5D-Graphen dienen getrennt als Etikettenkontrolle.

Alle fuenf vorab deklarierten 5D-minus-andere-D-Kontraste der Output-Spikezahl haben Intervalle, die null einschliessen, und Holm-p=1. Ein belastbarer 5D-Vorteil ist damit nicht gezeigt. Mehr Output-Spikes sind zudem kein allgemeines Aufgabenqualitaetsmass. Eingangsgrade und Motive variieren mit der Graphgeometrie; das isoliert keinen universellen Effekt der Dimensionszahl. Die persistierte ID-Kodierung bleibt fuenfdimensional.

## Negativer Brian2-Vergleich

Der Einzelzellvergleich wurde ausgefuehrt, aber das vorab deklarierte Konformitaetskriterium wurde in allen drei Laeufen verfehlt. Maximale Spannungsabweichung: 99,5810677; maximale Recovery-Abweichung: 13,9959569. Die Spikefolgen stimmen nicht exakt ueberein. Im ersten Lauf wird die Spannungsabweichung 1e-8 erstmals bei Tickindex 137 ueberschritten; zuvor bestehen bereits kleinere Rechendifferenzen.

Die Verstaerkung kleiner numerischer Unterschiede in einem schwellenden System ist eine plausible Erklaerung, aber ihre konkrete Ursache wurde nicht durch eine separate Intervention isoliert. Der Befund wird weder entfernt noch durch eine nachtraeglich gelockerte Toleranz positiv gemacht. Naechster Versuch: vorab spezifizierte Ein-Schritt-Fehler, Auswertungsreihenfolge, Datentyp und Ereignisphasen isolieren. Die Kern-Dynamik wird nicht bloss zum Bestehen dieses Vergleichs veraendert.

Brian2 wurde mit NumPy-Backend und derselben zweiteiligen v-Aktualisierung, anschliessender u-Aktualisierung, Reset und deaktivierter Adaptation betrieben. Das ist kein Vergleich aller Faehigkeiten von Brian2, NEST oder Lava und kein fairer Framework-Geschwindigkeitsrang. Setup-/Codegenerierungszeiten sind enthalten und explizit bezeichnet.

## Stabilitaet und historische Tests

20 Stabilitaetslaeufe, zehn Seeds, zwei Bedingungen, jeweils 100000 Ticks. Alle Zustands-/Topologiepruefungen bestanden. Nach Burn-in: 300 Spikes pro 1000-Tick-Fenster im tonischen Arm des kleinen Drei-Zellen-Netzes, null im Nullinputarm; CV und relativer Drift null. Seed-invariante Resultate sind keine zehn unabhaengigen zufaelligen Netzreplikationen.

Der historische Lern-Runner nennt deklarierte Validierungs-/Holdout-Partitionsgroessen, fuehrt aber nur je eine Vorher-/Nachher-Probe aus. Diese Zahlen werden nicht als absolvierte Testepisoden interpretiert. Der neue Assoziationsversuch besitzt dagegen echte neue Testepisoden. Der historische Interferenz-Screen verwendet getrennte Task-Netzwerke: kein Nachweis gegen katastrophales Vergessen eines gemeinsam trainierten Netzes. Der lokale independent_replication-Runner ersetzt kein unabhaengiges Team. Memory-, Weltmodell- und Profil-Screens pruefen Komponenten, nicht automatisch neuronales Lernen. MSBA-Energieeinheiten sind keine gemessenen Joule; softwareberechnete Reglerleistungen sind nicht ohne Attribution dem SNN zuzuschreiben.

## Skalierung: offener Fehler und dokumentierte Korrektur

Der urspruengliche Skalierungsversuch v1 brach ab, als ein linearer Neuronenindex von 256 unzulaessig in die erste 8-Bit-Koordinate geschrieben wurde. Die Ergebnisliste wurde nicht zurueckgegeben; interne Teilmessungen werden deshalb nicht als gespeicherte Resultate behauptet. Der Fehlversuch bleibt im Originalbericht.

Die explizite v2-Amendierung zerlegt Indizes in fuenf gueltige Base256-Koordinaten. Graphbudgets, 32-Tick-Last und Messgroessen bleiben gleich; frische Seeds 21001 bis 21003. Das ist keine N-D-Migration der Persistenz. Die getrennte Ergebnistabelle nennt nur tatsaechlich absolvierte Groessen. RSS-Samples sind Prozessspeicher einschliesslich Interpreter/Bibliotheken, keine isolierten Allokationsspitzen. Keine Langzeit-, Vollplastizitaets-, Echtzeit-, GPU-, Energie- oder biologische Skalierungsaussage.


## Messgrenzen der Skalierung und Kennungen

Die v2-Serie umfasst tatsaechlich 15 Laeufe (fuenf Groessen, drei Seeds), alle mit endlichen Zustaenden. 100000 Neuronen und 400000 Kanten: im Mittel 2,00273 Ticks/s, beobachtete Spannweite 1,96761 bis 2,04618; jeweils nur 32 Ticks. Aufbauzeit im Mittel 4,81914 s; RSS nach dem Lauf im Mittel 436365995 Bytes (rund 416,15 MiB), ohne daraus isolierten Netzspeicher abzuleiten.

Die fuenf Groessen laufen pro Seed im selben Prozess. Speicherallokatoren koennen Speicher aus der vorherigen grossen Instanz behalten; daher sind die RSS-Werte kleinerer Instanzen in spaeteren Seeds deutlich hoeher. Diese Werte erlauben keine saubere Speicherskalierungskurve. Nur acht Quellen werden zweimal angeregt; die Aktivitaetsdichte wird nicht proportional zur Netzgroesse konstant gehalten. Die identische Spike-/Ereigniszahl der groessten zwei Instanzen stuetzt keinen dicht aktiven Durchsatznachweis.

Der aufgezeichnete v2-Kindmanifestname lautet aufgrund eines Metadatenfehlers noch EXP-EMP-20260910-001. Er ist ohne Kampagnenpfad nicht eindeutig. Unveraenderte Originalmanifeste bleiben erhalten; campaign-index.json bietet qualifizierte Referenzen aus Kampagne und Unterverzeichnis. Kuenftige Ausfuehrungen verwenden den deklarierten campaign-id-Praefix. Die Reparatur veraendert weder alte Messwerte noch deren Quellbindung.

Die Kampagnenindex-Manifeste sind nachtraegliche Navigationsmetadaten. Sie sind keine neuen Messlaeufe, keine eigenen unabhaengigen Replikationen und nicht zur automatischen Evidenzfreigabe geeignet. Alle unveraenderten Kindmanifeste, Rohdaten und Eingabeplaene bleiben ueber ihre SHA-256-Pruefsummen nachvollziehbar.
