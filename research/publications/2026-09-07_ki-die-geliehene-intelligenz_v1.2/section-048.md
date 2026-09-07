[Inhaltsübersicht](README.md) | [Zurück](section-047.md) | [Weiter](section-049.md)

<a id="b5d-anhang-h-pruefprotokolle"></a>
# Anhang H – Prüfentwürfe für empirischen Erkenntnisgewinn

## H.0 Status, Zuständigkeit und Eintrittsbedingungen

Die folgenden Entwürfe operationalisieren offene Fragen. **Sie sind weder durchgeführte Experimente noch abgeschlossene Präregistrierungen noch bereits ausführbare Runner-Verträge.** Ihre Bezeichnungen P-DIM, P-LEARN, P-MEM, P-ATTR und P-CTRL sind lokale Planungskennungen dieser Publikation, keine neuen kanonischen EXP-, RQ- oder EVID-IDs. Vor einer Durchführung sind sie mit den bestehenden Forschungsfragen, Schemata und Protokollen abzugleichen. Beispielsweise dürfen eine Topologiefrage und eine STDP-Lernleistungsfrage nicht allein wegen eines neuen Publikationstitels doppelt registriert werden.

Die Unterscheidung zwischen vorab festgelegter Prüfung und nachträglicher Erklärung folgt der hier herangezogenen Präregistrierungsliteratur. Ein nach Kenntnis alter Ergebnisse erstellter Plan kann eine neue, ungesehene Untersuchung vorbereiten; er macht die alten Ergebnisse nicht rückwirkend konfirmatorisch. [M05](section-049.md#src-m05)

**Verbindliche Voraussetzungen für alle Entwürfe:** Ein sauberer und rekonstruierbarer Codezustand; nachweislich wirksame Parameter; ein separat getesteter Messpfad; Eingangs- und Zustandsprovenienz; festgelegte Analyse; begründete Versuchszahl und Stoppregeln; sowie unveränderte Rohartefakte. Bei einem Größen- oder Dimensionswert, den die produktive Runtime nicht unterstützt, ist zuerst eine dokumentierte Implementierung erforderlich. Ein fehlender Parameter darf nicht stillschweigend durch den Defaultwert ersetzt werden.

Die vorhandene Roadmap benennt einen eigenständigen N-D-Projektionsvergleich und Formatfragen oberhalb von fünf Dimensionen weiterhin als Entwicklungsaufgaben. Daher wird hier gerade nicht behauptet, die vollständige Vergleichsreihe sei schon mit dem bestehenden Runner ausführbar. Der binäre Ring in Anhang G ist kein Ersatz dafür.

## H.1 P-DIM: Adressierung und wirksame Geometrie trennen

**Fragestellung:** Liefert eine geometrisch wirksame 5D-Architektur gegenüber geeigneten Alternativen einen praktisch relevanten Zusatznutzen unter einem vorab bestimmten Ressourcenvertrag?

**Stufe A – Implementierungskontrolle:** Bei festem semantischem Graphen werden injektive Adressierungen mit D = 2, 3, 4, 5, 6 verwendet. Zu vergleichen sind nicht nur Ausgaben, sondern auch zurückübersetzte Zustände, Kanten, Gewichte, Verzögerungen und Ereigniswarteschlangen. Die Gleichheit ist vorab als exakt oder mit begründeter numerischer Toleranz festzulegen. Jede Abweichung wird bis zum verursachenden Codepfad untersucht. Diese Stufe prüft die Voraussetzungen von P1, nicht einen kognitiven Vorteil.

**Stufe B – Funktionaler Architekturvergleich:** D beeinflusst einen ausdrücklich benannten Mechanismus, zum Beispiel Kantenbildung über Distanz. Die primäre Zielgröße ist die mittlere Genauigkeit einer festgelegten verzögerten Reizabrufaufgabe auf zuvor unangetasteten Testfällen. Pro Initialisierung wird eine Genauigkeit berechnet; die unabhängige Einheit ist das neu initialisierte Netzwerk, nicht jeder einzelne Tick oder Testfall. Trainings- und Testgenerator erhalten getrennte Zufallsströme.

**Kontrollvertrag:** N, Synapsenbudget, Neuronenmodell, Simulationsschritt, Trainings- und Testumfang, Eingangsenergie und Hyperparametersuchbudget werden vorab festgelegt. Eine nichtgeometrische, gradangepasste Baseline sowie Rewiring- und Distanz-aus-Kontrollen ergänzen die Dimensionsarme. Falls die Topologie selbst der vermittelnde Mechanismus ist, wird ihr Unterschied für den Gesamteffekt nicht wegkonditioniert. Ein zweiter, topologiefester Vergleich schätzt ausdrücklich eine andere Zielgröße.

**Primäre Kontraste:** Für jede Vergleichsdimension d wird pro unabhängiger Initialisierung i die gepaarte Differenz δ_i(d) = y_i(5) − y_i(d) gebildet. Die Paarung betrifft gleiche Daten- und Zufallsbedingungen, nicht die Behauptung identischer Topologien. Eine spezielle Vorrangstellung von fünf Dimensionen verlangt die vorher festgelegten Vergleiche zu allen relevanten Alternativen, insbesondere vier und sechs. Die Familie der Kontraste und ihre Fehlerkontrolle werden vor Dateneinsicht eingefroren. Ein einzelner nachträglich ausgewählter positiver Vergleich genügt nicht.

**Praktische Relevanz:** Eine kleinste relevante Differenz Δ_min wird aus Aufgabennutzen und Kosten begründet. Eine im Pilot lediglich illustrative Marge, etwa zwei Prozentpunkte, ist noch keine validierte Wahl. Ein positiver Befund muss sowohl Unsicherheit als auch diese praktische Grenze berücksichtigen. Ein nicht signifikanter Unterschied ist keine Äquivalenz. Für eine Gleichwertigkeitsaussage sind vorab begründete obere und untere Grenzen und ein geeigneter Äquivalenztest erforderlich. Diese Unterscheidung wird durch den hier eingesehenen Abstract von Lakens gestützt; dessen vollständige Testimplementierung wird dadurch nicht als geprüft ausgegeben. [M04](section-049.md#src-m04)

**Fallzahl und Stopp:** Ein separater Pilot kann Messfehler, Varianz und Rechenbedarf bestimmen. Seine Ergebnisse dürfen nicht zugleich der abschließende Test der ausgewählten Hypothese sein. Die konfirmatorische Zahl unabhängiger Initialisierungen wird danach durch eine dokumentierte Präzisions- oder Powerplanung festgelegt. Ein willkürliches „20 Seeds“ wird nicht als Powernachweis übernommen. Abbruch erfolgt ausschließlich nach vorab definierten Ressourcen-, Sicherheits- oder technischen Fehlerregeln, nicht beim ersten günstigen p-Wert.

**Falsifikation und Begrenzung:** Eine robuste Unterlegenheit, eine ausreichend präzise praktische Gleichwertigkeit oder ein nur durch Mehrressourcen erklärter Unterschied schwächt den behaupteten 5D-Zusatznutzen im geprüften Scope. Ein breites Intervall ist dagegen zunächst unentschieden. Auch ein positiver Befund rechtfertigt keine Aussage über beliebige Aufgaben oder biologische Dimensionalität.

## H.2 P-LEARN: Lernregel gegen passende Kontrollen

**Fragestellung:** Verbessert die untersuchte Plastizitätsregel eine definierte Leistung, statt lediglich Gewichte zu verändern?

**Design:** Dieselbe Aufgabenfamilie wird mit aktivierter Lernregel, eingefrorenen Gewichten und einer passend entkoppelten Kontrollregel untersucht. Alle Arme erhalten gleiche Trainingsdaten, Anfangsbudgets und Auslesekapazität. Ein externer lernender Decoder wird entweder in allen Armen identisch behandelt oder separat als eigener Faktor variiert. Seine Parameter und sein Trainingsdatensatz werden vollständig erfasst.

**Endpunkt:** Primär wird die Differenz der Testleistung nach Training bewertet. Zusätzlich werden Vortrainingsleistung, Gewichtsänderungen, Aktivität, Kosten und technische Ausfälle berichtet. Eine Differenz-von-Differenzen kann verwendet werden, wenn die entsprechende Zielgröße vorab festgelegt wurde: (nach − vor)_Lernregel − (nach − vor)_Kontrolle. Verbesserungen auf ausschließlich bekannten Trainingsfällen gelten nicht als Generalisierungsnachweis.

**Fehlerquellen:** Datenleckage, nachträgliche Auswahl erfolgreicher Seeds, ein wesentlich stärkerer Decoder, unterschiedliche Trainingsdauer und die Verwechslung von Beispielzahl mit unabhängigen Netzwerken. Fehlgeschlagene Läufe werden vollständig berichtet. Ein technischer Fehler ist nicht automatisch ein Nullwert der Aufgabenleistung; seine Behandlung muss im Analysevertrag stehen.

**Erkenntnis:** Ein kontrollierter Vorteil stützt die konkret untersuchte Funktion der Regel. Ein Gewichtsdrift ohne Vorteil ist ein relevanter negativer Funktionsbefund, nicht durch die Bezeichnung „Plastizität“ wegzuerklären.

## H.3 P-MEM: Information, Behalten und Nutzung

**Fragestellung:** Trägt ein interner Zustand nach Reizende aufgabenrelevante Information und wird sie für die spätere Antwort kausal genutzt?

**Design:** Ausgeglichene Reizklassen werden präsentiert, anschließend folgen vorher festgelegte reizfreie Verzögerungen und gegebenenfalls Störungen. Der spätere Test besitzt keinen Zugriff auf die Reizkennzeichnung, Logs, Retrieval oder ein anderes verborgenes Gedächtnis. Ein Ausleseverfahren wird ausschließlich auf Trainingszuständen angepasst und vor der Testauswertung eingefroren.

**Kontrollen:** Reizlabelshuffle, zustandsangeglichene oder zeitlich verschobene Kontrollzustände, gezielte Löschung beziehungsweise Ersetzung des postulierten Trägers und Wiederherstellung aus einem gespeicherten Zustand. Der Eingriff muss separat darauf geprüft werden, ob er nur die relevante Information oder unspezifisch das ganze System zerstört. Aktivitätsniveau und Rechenbudget werden dokumentiert.

**Endpunkte:** Verzögerungsabhängige Testgenauigkeit, Veränderung nach der gezielten Zustandsintervention und Wiedergewinn nach geeigneter Wiederherstellung. Eine reine Dekodierbarkeit stützt zunächst Information im Zustand; eine kausale Aufgabenrolle benötigt den zusätzlichen Eingriff. Informationsschätzungen müssen Stichprobengröße und Schätzbias berücksichtigen und sind nicht aus Gesamtspikezahlen abzuleiten.

**Fortlaufendes Lernen:** Als gesonderte Erweiterung werden Aufgaben A, B und C ohne Neuinitialisierung desselben Systems nacheinander trainiert. Nach jeder Phase wird die Leistung auf allen bisherigen Aufgaben gemessen. Der Abfall einer alten Aufgabe wird gegenüber ihrer zuvor erreichten Leistung und passenden Referenzarmen definiert. Separat zurückgesetzte Erfolgsversuche erfüllen diesen Vertrag nicht.

## H.4 P-ATTR: Kern, Decoder und externe Informationspfade

**Fragestellung:** Welcher Systemteil trägt welchen Anteil der aufgabenbezogenen Leistung unter dem gewählten Eingriffsvertrag?

**Design:** Mindestens untersucht werden vollständiges System, isolierter Kern mit fixierter Auslese, externer Pfad ohne informative Kernzustände, gezielter Kernzustandsaustausch und eine Wiederherstellungskontrolle. Die erlaubten Informationen jedes Arms werden explizit aufgelistet. Zugänge zu Prompts, Dateien, Caches, Internet und gespeicherten Antworten gelten als mögliche Leistungspfade, nicht als unsichtbarer Hintergrund.

**Analyse:** Primäre Kontraste werden vorab gewählt. Wechselwirkungen sind relevant: Zwei einzeln wirksame Komponenten können redundant sein; zwei einzeln unwirksame können gemeinsam nützlich werden. Eine additive Aufteilung auf Prozentanteile wird ohne identifizierenden Vertrag nicht behauptet. Der kausale Vergleich setzt voraus, dass die Eingriffe korrekt ausgeführt wurden und keine unkontrollierten Ressourcenunterschiede erzeugen.

**Falsifikation:** Wenn derselbe Erfolg ohne informative Kernzustände erreicht wird und die postulierte Kernintervention unter hinreichend empfindlichen Bedingungen keine spezifische Wirkung zeigt, ist die behauptete zusätzliche Kernrolle in diesem Versuch nicht belegt. Das schließt andere Aufgaben oder redundante Rollen nicht pauschal aus.

## H.5 P-CTRL: Rechte und praktische Kontrolle getrennt prüfen

**Fragestellung:** Stimmen dokumentierte Entscheidungsrechte mit den tatsächlich durchgesetzten Handlungsmöglichkeiten überein, und bleiben kritische Eingriffe unter den vorgesehenen Störungen wirksam?

**Design:** Für jede Komponente des Hoheitsvektors wird die berechtigte Rolle mit einer positiven und einer unberechtigten negativen Testaktion geprüft. Für den Kontrollvektor werden begrenzte Ressourcenstörungen, nicht verfügbare Sensoren, verzögerte Rückmeldungen und Unterbrechungen in einer sicheren Simulation untersucht. Reale Hardwareüberlastung, physische Schäden oder unkontrollierte externe Aktionen sind ausgeschlossen.

**Endpunkte:** Nicht autorisierte erfolgreiche Aktionen, erkannte und übersehene Fehler, Stopplatenzen einschließlich Ausfällen, Limitüberschreitungen, Wiederherstellungserfolg und fehlende Provenienzfelder. Kritische Grenzwerte werden einzeln bewertet. Ein guter Durchschnitt darf einen versagenden kritischen Abbruchpfad nicht kompensieren.

**Grenze:** Technischer Erfolg des Audits bestätigt nicht automatisch moralische Legitimität oder sachkundiges menschliches Verständnis. Diese Fragen benötigen eigene Begründungen oder Studien. Der Audit operationalisiert einen begrenzten technischen Teil des Kontrollbegriffs.

## H.6 Einheitlicher Bericht und Entscheidung

Jeder Bericht enthält vorab bestimmte Frage und Hypothese, Implementierungsnachweis, Daten- und Codeidentität, tatsächliche unabhängige Einheiten, Ausschlüsse und Ausfälle, alle registrierten Kontraste, Effekte mit Unsicherheit, Kosten, Protokollabweichungen und getrenntes Review. Explorative Nachanalysen sind zulässig, werden aber als solche gekennzeichnet. Negative und unentschiedene Ergebnisse werden ebenso veröffentlicht wie positive.

Die Reihenfolge der Arbeit ist entscheidend: **zuerst ausführbarer und geprüfter Messvertrag, dann blinde Festlegung der Analyse, dann tatsächlicher Versuch, anschließend Auswertung und Review.** Diese Publikation präzisiert die Fragen und Entwürfe; sie ersetzt keinen dieser noch ausstehenden Schritte.

[Inhaltsübersicht](README.md) | [Zurück](section-047.md) | [Weiter](section-049.md)
