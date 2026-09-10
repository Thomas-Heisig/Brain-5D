[Inhaltsuebersicht](README.md) | [Zurueck](section-034.md) | [Weiter](section-036.md)

<a id="b5d-acht-neue-synthesehypothesen-und-prüfprotokolle"></a>

# 31. Acht neue Synthesehypothesen und Prüfprotokolle

<a id="b5d-neue-synthesehypothesen-kennzeichnung-und-reichweite"></a>

## Neue Synthesehypothesen: Kennzeichnung und Reichweite

Die folgenden Hypothesen tragen das Präfix **H-SYN**. Sie sind Vorschläge dieser Abhandlung, keine bereits im produktiven Repository registrierten oder ausgeführten Studien. Jede verbindet mindestens zwei bisher getrennte Themenfelder. Die registrierten RQ- und H-IDs bleiben unverändert.

<a id="b5d-h-syn-01-provenienzerhaltende-kompaktierung-kann-reviewqualität-erhalten"></a>

### H-SYN-01: Provenienzerhaltende Kompaktierung kann Reviewqualität erhalten

**Aussage.** Ein strukturiertes, begrenztes ResearchPacket ermöglicht bei gleichem Modell und gleichem Ausgabebudget eine mindestens gleichwertige Erkennung vorab definierter wissenschaftlicher Defekte wie ein unstrukturierter längerer Bericht.

**Design.** Verwendet werden eingefrorene, technisch erzeugte Testartefakte mit bekannten Defekten und defektfreien Kontrollen. Dieselben Fälle erscheinen in beiden Darstellungsbedingungen. Die Modellversion, Promptschablone und Bewertungsrubrik bleiben fest. Ein Holdout-Satz verhindert die nachträgliche Optimierung des Pakets auf genau die Testfehler. Menschliche Versuchspersonen sind für die erste technische Modellvergleichsstufe nicht erforderlich; eine spätere Studie zur Bedienbarkeit wäre separat zu genehmigen.

**Endpunkte und Falsifikation.** Primär werden Sensitivität für schwerwiegende Defekte und Fehlalarmrate bewertet; F1 allein darf seltene gefährliche Auslassungen nicht verdecken. Eine Nichtunterlegenheitsgrenze ist fachlich vorab zu begründen. Wird ein relevanter Defekttyp durch die Kompaktierung systematisch unsichtbar, ist die Hypothese für diesen Scope nicht gestützt. Anschluss: `RQ-AIR-001`, F6, F12 und F24.

<a id="b5d-h-syn-02-korrekte-ressourcenrückmeldung-verbessert-ausfallanpassung"></a>

### H-SYN-02: Korrekte Ressourcenrückmeldung verbessert Ausfallanpassung

**Aussage.** Nutzbare interozeptive Information verbessert die Recovery einer registrierten Aufgabe nach Sensor- oder Ressourcendegradation gegenüber gleich budgetierten Frozen-, Missing- und zeitverschobenen Rückmeldungen.

**Design.** Gepaart verglichene Simulationszustände erhalten dieselbe Perturbation. Untersucht werden korrekte Rückmeldung, uninformative aber zeitlich passende Rückmeldung und keine Rückmeldung. Schutzgrenzen bleiben in allen Bedingungen aktiv. Damit wird Lernnutzen von der Wirkung eines unterschiedlich konfigurierten SafetyControllers getrennt.

**Endpunkte und Falsifikation.** Vorab bestimmt werden Zeit bis zur Wiederherstellung, Aufgabenleistung und Verletzung technischer Grenzen. Ein Vorteil, der nur auf mehr Rechenbudget oder auf handcodierter Wiederanlaufsteuerung beruht, zählt nicht als gelernte Kompensation. Anschluss: `RQ-REG-002`, `RQ-MSBA-E05`, H10 und H11.

<a id="b5d-h-syn-03-ein-minimaler-selbstzustandsvektor-verbessert-kalibrierung"></a>

### H-SYN-03: Ein minimaler Selbstzustandsvektor verbessert Kalibrierung

**Aussage.** Ein System, das verifizierbare Informationen über eigene Sensorverfügbarkeit und Aktorkapazität nutzt, sagt seinen Aufgabenerfolg besser kalibriert voraus als ein System ohne diese Information.

**Design.** Die Ausfallbedingungen werden vorab eingefroren. Prognosen erfolgen vor dem Handlungsergebnis. Training und Test nutzen getrennte Ausfallkombinationen. Als Kontrollen dienen ein konstantes Basismodell und ein Modell, das nur die äußere Aufgabenbeschreibung kennt. Der Sprachstil der Selbstauskunft wird nicht als Endpunkt verwendet.

**Endpunkte und Falsifikation.** Kalibrierungsfehler und ein geeigneter Proper Scoring Rule werden getrennt von der eigentlichen Erfolgsquote bewertet. Ein System kann gut handeln und schlecht wissen, wann es scheitert. Bleibt der Zusatznutzen auf die bereits im Training gesehenen Ausfälle beschränkt, ist keine robuste Selbstmodellfunktion nachgewiesen. Anschluss: F19 und `RQ-EMB-001`.

<a id="b5d-h-syn-04-geometriewirkung-ist-nur-über-einen-benannten-mechanismus-identifizierbar"></a>

### H-SYN-04: Geometriewirkung ist nur über einen benannten Mechanismus identifizierbar

**Aussage.** Eine Dimensionsvariation beeinflusst die Ergebnisgröße nur, soweit mindestens ein registrierter kausaler Mechanismus die geometrische Information verwendet.

**Design.** Ein Arm hält den Graphen und alle nichtgeometrischen Dynamikparameter fest und deaktiviert jede Distanzverwendung. Ein zweiter Arm verwendet die Geometrie für einen vorab bestimmten Mechanismus, etwa Delay-Zuordnung unter gematchtem Gesamtbudget. Dimensionswechsel und Mechanismusaktivierung werden faktoriell gekreuzt. Die Zielgröße ist nicht eine beliebige nachträglich auffällige Metrik, sondern ein festgelegter funktionaler Endpunkt.

**Endpunkte und Falsifikation.** Der erste Arm dient als Identitätskontrolle. Ein unerwarteter Unterschied dort deutet auf versteckte Confounds oder einen nicht dokumentierten Koordinatenpfad. Ein spezifischer Unterschied im zweiten Arm identifiziert zunächst den untersuchten Mechanismus, nicht die universelle Überlegenheit der Zahl fünf. Anschluss: `RQ-5D-004`, `RQ-5D-005`, Framework-RQ1.

<a id="b5d-h-syn-05-nichtkompensierbare-teilfehler-verbessern-regulationsdiagnostik"></a>

### H-SYN-05: Nichtkompensierbare Teilfehler verbessern Regulationsdiagnostik

**Aussage.** Lokale oder nichtsignierte Fehlermaße erkennen gleichzeitig über- und unteraktive Populationen zuverlässiger als ein globaler signierter Mittelwert und können dadurch eine funktional bessere Regelung unter definiertem Budget ermöglichen.

**Design.** Die Auswertung trennt die algebraische Eigenschaft der Metrik von der empirischen Qualität der darauf beruhenden Regelung. Eingebracht werden kontrolliert gegenläufige Störungen. Verglichen werden signierte, absolute, quadratische und lokale Zielfehler. Task-Rewards und Schutzgrenzen bleiben identisch.

**Endpunkte und Falsifikation.** Das Verschwinden gegensätzlicher Fehler im Mittel ist analytisch bekannt; zu testen ist der zusätzliche funktionale Nutzen einer anderen Regel. Ueberreaktion, Oszillation oder Neutralisierung von Lernsignalen können diesen Nutzen widerlegen. Anschluss: `RQ-HOM-002`, `RQ-MSBA-E02`.

<a id="b5d-h-syn-06-quellen--und-freigabestatus-müssen-unabhängig-sichtbar-sein"></a>

### H-SYN-06: Quellen- und Freigabestatus müssen unabhängig sichtbar sein

**Aussage.** Ein maschineller Konsistenzprüfer kann Konflikte zwischen Protokoll, Messabdeckung, Registry-Status und Berichtssprache erkennen, ohne selbst eine Evidenzfreigabe zu erteilen.

**Design.** Ein eingefrorener Defektkatalog umfasst unter anderem die vier in dieser Abhandlung sichtbaren Konflikttypen. Der Prüfer erhält nur erlaubte Eingabefelder. Jede Meldung muss Feld, Quelle, Widerspruch und minimale Nachprüfung nennen. Reine Aussagen wie “alles grün” werden nicht als Nachweis gewertet.

**Endpunkte und Falsifikation.** Korrekte Lokalisierung, Vollständigkeit der Quellenkette und Fehlalarmrate sind zu messen. Ein Prüfer, der unklare Fälle eigenmächtig als bestätigt markiert, verfehlt das Sicherheitsziel selbst dann, wenn viele Einzelfälle richtig erkannt werden. Anschluss: `RQ-SUITE-001`, `RQ-AIR-001`, F8 und F24.

<a id="b5d-h-syn-07-persistenz-und-episodischer-recall-brauchen-getrennte-kontrollen"></a>

### H-SYN-07: Persistenz und episodischer Recall brauchen getrennte Kontrollen

**Aussage.** Ein gespeicherter neuronaler Zustand erzeugt nach Restore nur dann einen spezifischen Erinnerungsnutzen, wenn eine zurückliegende Lernphase die passende Reaktion gegenüber untrainierten, geshuffelten und retrieval-isolierten Kontrollen verbessert.

**Design.** Verglichen werden kompletter Restore, Restore ohne lernrelevante Zustandsanteile, sham-trainierter Restore und ein untrainiertes Netz. Derselbe Cue erscheint ohne erneute Bereitstellung des Zielinhalts. Encoder, Decoder und LLM-Zugriff sind kontrolliert. Ein technischer Hashvergleich bleibt ein separater Funktionscheck.

**Endpunkte und Falsifikation.** Cue-Spezifität, Verzögerungsrobustheit, Fehlabruf und Holdout-Transfer bestimmen den funktionalen Geltungsbereich. Kann der Decoder die Aufgabe ohne den gelernten SNN-Zustand lösen, ist kein intern getragener Recall belegt. Anschluss: `RQ-STORAGE-001`, `RQ-MEM-001`, Framework-RQ5.

<a id="b5d-h-syn-08-effektive-kontrolle-besitzt-ein-zeitliches-engpasskriterium"></a>

### H-SYN-08: Effektive Kontrolle besitzt ein zeitliches Engpasskriterium

**Aussage.** Ein formales Vetorecht ist bei einer registrierten Schadensklasse praktisch unzureichend, wenn Erkennung, Bewertung und Ausführung des Eingriffs zusammen länger dauern als das verbleibende sichere Interventionsfenster.

**Design.** In einer ausschließlich simulierten Umgebung werden Ereignisgeschwindigkeit, Monitoringlatenz und verifizierte Stopplatenz variiert. Die menschliche Bewertungszeit kann in einer ersten technischen Studie als expliziter Parameter modelliert werden; sie darf nicht als gemessene menschliche Eigenschaft ausgegeben werden. Eine spätere Bedienerforschung bleibt ein eigener Studienzweig.

**Endpunkte und Falsifikation.** Gemessen werden erfolgreiche Begrenzung, Zeitreserve und Wiederherstellbarkeit. Ein Zugriffstoken oder Stopbutton ist nur eine notwendige Schnittstelle. Bleibt das System auch ausserhalb der angenommenen Zeitgrenze durch automatisch wirksame Grenzen sicher, muss das Kontrollmodell die technische Vorbegrenzung zusätzlich berücksichtigen. Anschluss: F6 bis F9, H5 und H11.

[Inhaltsuebersicht](README.md) | [Zurueck](section-034.md) | [Weiter](section-036.md)
