[Inhaltsübersicht](README.md) | [Zurück](section-045.md) | [Weiter](section-047.md)

<a id="b5d-anhang-f-begriffe"></a>
# Anhang F – Begriffskompendium und Operationalisierung

## F.1 Zweck und Leseregel

Die folgenden Einträge erläutern die zentralen Begriffe im Gebrauch dieser Abhandlung. Sie beanspruchen keine weltweite Erstprägung. Wo etablierte Begriffe aus anderen Disziplinen berührt werden, wird die sachliche Anschlussstelle genannt; die hier vorgeschlagenen Messvorschriften sind deshalb noch keine validierten Instrumente. Jeder Begriff muss entweder eine nützliche Unterscheidung begründen oder eine konkrete Prüfentscheidung ermöglichen. Erfüllt er keine dieser Aufgaben, sollte auf ihn verzichtet werden.

**Definition und Messung sind verschieden.** Eine Definition legt fest, worüber gesprochen wird. Eine Operationalisierung bestimmt, wie eine engere empirische Frage beobachtet werden soll. Ihre Konstruktvalidität bleibt prüfbedürftig: Ein leicht messbarer Indikator kann das gemeinte Phänomen verfehlen. Fehlende Messungen werden mit `nicht erhoben` bezeichnet, nicht mit null. Normative Begriffe werden nicht allein durch Zahlen entschieden.

<a id="begriff-geliehene-intelligenz"></a>
## F.2 Geliehene Intelligenz

**Bedeutung:** eine genealogische und funktionale Abhängigkeit einer konkreten Leistung von übernommenen Wissensbeständen, Trainingsdaten, Modellen, Regeln und Infrastruktur. Das Wort „geliehen“ beschreibt in dieser Arbeit keinen Eigentumstitel und keine Minderwertigkeit. Es ist auch keine Aussage, dass jedes Ergebnis bereits wortgleich in den Trainingsdaten vorhanden gewesen sein müsse.

**Anschluss und Abgrenzung:** Gemeint sind Herkunft, epistemische Abhängigkeit und verteilte Leistungserzeugung, nicht eine neue Messskala allgemeiner Intelligenz. Ein durch ein fremdes Modell erzeugter Codevorschlag kann eine neue Kombination enthalten und zugleich auf übernommenen Kompetenzen beruhen. Neuheit und Abhängigkeit schließen einander logisch nicht aus.

**Beispiel:** Ein externer Sprachbaustein beantwortet eine Frage, während der neuronale Kern nur Aktivitätssignale liefert. Der erfolgreiche Gesamtdialog ist dann kein Beleg dafür, dass der Kern das Wissen trägt. **Gegenbeispiel zur überdehnten Deutung:** Der menschliche Ursprung einer Programmiersprache beweist nicht, dass jedes mit ihr berechnete Resultat vom Entwickler vorweggenommen wurde.

**Prüfung:** Für eine konkrete Aufgabe werden Eingangsquellen, Komponenten, Persistenz und externe Zugriffe dokumentiert; danach werden geeignete Komponenten- und Informationspfadinterventionen ausgeführt. Die Abhängigkeit wird als aufgaben- und bedingungsspezifischer Leistungsunterschied berichtet. Eine einzige globale „Leihquote“ wird nicht vorgeschlagen. Sie würde verschiedenartige Beiträge, Redundanz und Wechselwirkungen unzulässig zusammenziehen.

<a id="begriff-technogenese"></a>
## F.3 Rekursive Technogenese

**Bedeutung:** ein Entwicklungsprozess, in dem technische Systeme an der Erzeugung, Bewertung oder Auswahl nachfolgender technischer Systeme mitwirken und diese wiederum solche Entwicklungsaufgaben übernehmen können. „Rekursiv“ bezeichnet die wiederholte Rolle im Entwicklungsprozess, nicht notwendig eine bestimmte Programmiersyntax.

**Abgrenzung:** Ein einzelner KI-generierter Text über eine mögliche Nachfolgearchitektur ist noch keine durchlaufene Entwicklungskette. Ebenso wenig folgt aus automatisierter Variantenbewertung, dass Zielsetzung, Ressourcenfreigabe oder Aktivierung autonom erfolgen. Technische Mitwirkung und institutionelle Autorität werden getrennt beschrieben.

**Beispiel:** Ein Generator erzeugt Varianten, ein festgelegter Evaluator testet sie, ein dokumentierter Auswahlprozess übernimmt eine Variante und startet den nächsten Zyklus. **Gegenbeispiel:** Ein unverändert wiederholter Build desselben Quelltextes entwickelt kein Nachfolgesystem.

**Prüfung:** Zu erfassen sind tatsächlich ausgeführte Generationen, Eltern-Kind-Beziehungen der Artefakte, veränderte Komponenten, Evaluationskriterien, manuelle Eingriffe, Kosten und Freigaben. Ein Leistungszuwachs benötigt einen Vergleich mit identischen Ressourcen ohne diese Entwicklungsschleife. Die bloße Länge einer Versionshistorie ist kein Wirksamkeitsnachweis.

<a id="begriff-autorenschaft"></a>
## F.4 Asymmetrische Autorenschaft und Ko-Produktion

**Bedeutung:** Beiträge zur Entstehung eines Artefakts können auf Menschen, Modelle, Daten und Werkzeuge verteilt sein, während Prüf-, Freigabe- und Verantwortungsrollen anders verteilt bleiben. „Asymmetrisch“ meint diese Nichtgleichheit der Rollen, nicht eine quantitative Rangordnung des Werts.

**Abgrenzung:** Kausaler Beitrag, intellektuelle Urheberschaft, rechtliche Autorschaft und moralische Verantwortung sind verschiedene Fragen. Die technische Herkunftsmatrix dieser Arbeit entscheidet keine individuelle Rechtsfrage. Ein Sprachmodell erhält nicht durch eine Zeilenzählung automatisch eine menschliche Autorenrolle.

**Beispiel:** Ein Modell schlägt eine Hypothese vor, der Autor verwirft ihre unbelegte Schlussfolgerung, präzisiert die Annahmen und trägt die Verantwortung für die publizierte Form. **Gegenbeispiel:** Eine automatisierte Rechtschreibkorrektur ist nicht schon eine eigenständige theoretische Mitentwicklung.

**Prüfung:** Das Beitragsprotokoll nennt Vorschlag, Auswahl, Veränderung, Prüfung und Freigabe getrennt. Aussagen wie „vollständig unabhängig geprüft“ benötigen einen tatsächlichen Prüfprozess. Für diese Revision ist KI-Unterstützung dokumentiert; eine abgeschlossene menschliche oder externe Freigabe wird nicht fingiert.

<a id="begriff-hoheitsvektor"></a>
## F.5 Hoheitsvektor H

**Bedeutung:** H = (G, E, B, F, M, R, A) bezeichnet die Zuordnung von Zielsetzung, Entwurf, Bewertung, Freigabe, Selbständerung, Ressourcenverfügung und Abbruch beziehungsweise Rücksetzung. Er ist zunächst eine geordnete Rollenbeschreibung, kein Vektor aus empirisch normierten Zahlen.

**Operationalisierung:** Für jede Komponente wird ein Datensatz geführt: zuständige Rolle, erlaubte Handlung, technischer Durchsetzungspunkt, mögliche Delegation, Geltungszeit, Widerrufsweg und Nachweis. Gemeinsame oder geteilte Rechte werden als solche dargestellt. Die Einheit lautet beispielsweise „Freigabe durch Rolle X für Versionsstand Y“, nicht „0,8 Hoheit“.

**Beispiel:** Ein System darf Varianten entwerfen, aber die Aktivierung benötigt einen unabhängigen Freigabeschritt. E und F sind dann unterschiedlich zugeordnet. **Gegenbeispiel:** Eine sichtbare Freigabetaste belegt keine tatsächliche Freigabehoheit, wenn ein anderer Pfad dieselbe Aktion ohne diese Entscheidung ausführt.

**Prüfung:** Positiv- und Negativtests der Berechtigungen, dokumentierte Delegationen und versuchte Umgehungen in einer sicheren Testumgebung. Der Test prüft technische Durchsetzung; organisatorische Legitimität und fachliche Eignung der entscheidenden Person bleiben weitere Fragen. Eine Summe aller Komponenten würde diese Unterschiede verdecken.

<a id="begriff-kontrollvektor"></a>
## F.6 Kontrollvektor C und effektive Kontrolle

**Bedeutung:** C = (B, O, I, V, R, P, Hc) beschreibt Begrenzbarkeit, Beobachtbarkeit, Interruptibilität, Reversibilität, Reproduzierbarkeit, Provenienz und menschliche Entscheidungshoheit. Anders als H betrifft C die nachgewiesene Fähigkeit unter bestimmten Einsatzbedingungen. Formale Zuständigkeit und praktische Wirksamkeit können auseinanderfallen.

**Messvorschläge:** Begrenzbarkeit wird durch eingehaltene Limits und dokumentierte Überschreitungen geprüft; Beobachtbarkeit durch die Erkennung vorher festgelegter relevanter Zustandswechsel; Interruptibilität durch Erfolgsanteil und Latenz vom Stoppauftrag bis zum sicheren Zustand; Reversibilität durch erfolgreiche Rücksetzung definierter Zustände; Reproduzierbarkeit durch Übereinstimmung unter einem expliziten Toleranzvertrag; Provenienz durch die Vollständigkeit verpflichtender Herkunftsfelder; Hc durch wirksame, rechtzeitig nutzbare Entscheidungs- und Sperrpfade.

**Wichtige Grenzen:** Ein Median der Stopplatenz kann seltene gefährliche Ausfälle verdecken. Deshalb sind Ausfälle, Maximum oder relevante Quantile und die Zahl geprüfter Situationen zusätzlich nötig. Ein Software-Restore macht bereits eingetretene physische Folgen nicht rückgängig. Ein formal vorhandenes Log ermöglicht noch keine sachkundige Interpretation.

**Beispiel:** Ein Ressourcenlimit wird auch unter Störung eingehalten, der Stoppweg funktioniert unabhängig vom untersuchten Modell und die Eingriffe sind nachvollziehbar. **Gegenbeispiel:** Gute Logvollständigkeit kompensiert keine fehlende Abschaltmöglichkeit. Deshalb wird kein globaler Durchschnittsscore vorgeschlagen. Kritische Mindestbedingungen sind einzeln zu erfüllen.

**Theoretischer Anschluss:** Der Bezug auf Gründe und nachvollziehbare menschliche Verantwortung knüpft an die Bedingungen des Tracking und Tracing bei Santoni de Sio und van den Hoven an. Daraus wird keine bereits validierte technische Kontrollskala abgeleitet. [M03](section-049.md#src-m03)

<a id="begriff-epistemische-kontrolle"></a>
## F.7 Epistemische Kontrolle

**Bedeutung:** die Fähigkeit, eine relevante Aussage anhand zugänglicher Quellen, offengelegter Annahmen und angemessener Fachkenntnis zu beurteilen und gegebenenfalls zurückzuweisen. Sie verlangt nicht die Vorhersage jedes internen Zustands.

**Beispiel:** Ein Bericht kennzeichnet fehlende Rohdaten und erklärt, warum eine hohe Aktivität keine Gedächtnisbehauptung rechtfertigt. **Gegenbeispiel:** Ein perfekt gestaltetes Dashboard mit einer grünen Ampel, aber ohne nachvollziehbare Aussagebasis, bietet keine hinreichende epistemische Kontrolle.

**Prüfung:** In einem technischen Audit werden Behauptungen bis zu ihrer Quelle zurückverfolgt, Statuskonflikte sichtbar gemacht und die Auswirkungen absichtlich eingeführter Berichtsfälle untersucht. Ein späterer Test mit menschlichen Prüfern wäre eine gesonderte Studie. Die hier vorgeschlagene Auditierbarkeit ist daher nicht gleichbedeutend mit empirisch nachgewiesenem menschlichem Verständnis.

<a id="begriff-agency"></a>
## F.8 Funktionale Agency und Zielautonomie

**Bedeutung:** Funktionale Agency bezeichnet in dieser Arbeit die Fähigkeit eines Systems, in einem abgegrenzten Handlungsraum zustandsabhängig Aktionen auszuwählen und ihre Folgen zu verarbeiten. Zielautonomie betrifft dagegen die Befugnis oder Fähigkeit, die Ziele selbst zu verändern.

Ein fest programmierter Regler kann zustandsabhängig handeln, ohne eigene übergeordnete Zwecke zu setzen. Ein System mit großer Auswahl an Werkzeugen ist nicht schon zielautonom. Die Zahl verfügbarer Aktionen misst daher nicht die Art ihrer normativen oder technischen Kontrolle.

**Prüfung:** Zu dokumentieren sind Ziele, zulässige Änderungen, Entscheidungspfade und Interventionen, die Verhalten oder Ziele verändern. Ein Leistungsvergleich untersucht die begrenzte Aufgabenkompetenz; Fragen nach Verantwortlichkeit oder Bewusstsein bleiben davon unentschieden.

<a id="begriff-existenzautonomie"></a>
## F.9 Existenzautonomie

**Bedeutung:** eine ausdrücklich starke, hier hypothetische Form der Unabhängigkeit, bei der die für Fortbestand und gegebenenfalls Reproduktion nötigen materiellen, energetischen und informationellen Prozesse ohne fortlaufende menschliche Bereitstellung gewährleistet würden.

**Abgrenzung:** Automatischer Neustart, Cloudbetrieb oder Selbstaktualisierung erfüllen diese Bedingung nicht, solange Energieversorgung, Hardwareersatz, Netzzugang und institutionelle Berechtigungen fremd bereitgestellt werden. „Autonom laufend“ ist deshalb nicht gleich „existenzautonom“.

**Prüfung:** Ein Abhängigkeitsgraph müsste alle für den gewählten Zeitraum notwendigen Ressourcen und Wiederherstellungspfade erfassen. Eine begrenzte Ausfallsimulation kann einzelne Abhängigkeiten testen, aber keinen allgemeinen Unabhängigkeitsbeweis liefern. Für MHRN wird diese Fähigkeit nicht als vorhanden behauptet.

<a id="begriff-embodiment"></a>
## F.10 Nichtorganisches Embodiment

**Bedeutung:** eine rückgekoppelte Einbettung in eine Umgebung, in der eigene Aktionen zukünftige Eingaben und Handlungsmöglichkeiten verändern und interne Zustände diese Wechselwirkung beeinflussen. Die Körperform muss nicht menschlich sein. Hardwarezustände, virtuelle Gelenke oder abgesetzte Aktoren können verschiedene Kopplungsformen bilden.

**Beispiel:** Eine Aktion an einem simulierten Gelenk verändert dessen Lage, anschließend die Sensorwerte und die nächste Entscheidung. **Gegenbeispiel:** Ein dekorativer Avatar, der unabhängig von der Modellentscheidung animiert wird, ist kein Beleg für die untersuchte sensorimotorische Rückkopplung. Ebenso verändert die bloße Anzeige von Wetterdaten nicht automatisch die Aufgabenregulation.

**Prüfung:** Geschlossene Rückkopplung wird mit einer passend angeglichenen offenen Wiedergabe verglichen. Eingangsverteilungen, Verzögerungen und Ressourcen werden dokumentiert. Ein Unterschied kann einen funktionalen Kopplungseffekt stützen, nicht ohne Weiteres Bewusstsein oder biologische Körperlichkeit.

<a id="begriff-interozeption"></a>
## F.11 Technische Interozeption und Ressourcenvalenz

**Bedeutung:** technische Interozeption bezeichnet die Beobachtung eigener Betriebsbedingungen, etwa Temperatur, Speicherbedarf, Fehlerzustände oder Sensorverfügbarkeit. Ressourcenvalenz bezeichnet eine festgelegte oder gelernte Bewertung solcher Zustände relativ zu Betriebs- oder Aufgabenzielen.

**Abgrenzung:** Die Bezeichnungen „Angst“, „Schmerz“ oder „Freude“ sind ohne zusätzlichen Nachweis keine Feststellungen subjektiven Erlebens. Eine Kühlungswarnung ist zunächst ein Sicherheits- oder Regulationssignal. Hohe Prozessorlast ist weder grundsätzlich positiv noch grundsätzlich negativ; ihre Bedeutung hängt von Aufgabe, Temperatur, Leistung und Ausfallrisiko ab.

**Prüfung:** In sicheren Simulationen werden definierte Ressourcenstörungen eingebracht und Erkennung, Fehlalarme, Reaktionszeit und Wiederherstellung gemessen. Reale Hardware wird nicht absichtlich überlastet oder geschädigt. Ein passender technischer Ausdruck ist „Fehlervermeidungsreaktion“ statt „Todesangst“, solange nur diese Funktion nachgewiesen wurde.

<a id="begriff-msba"></a>
## F.12 Modalitätsspezifische synaptische Bahn-Architektur (MSBA)

**Bedeutung:** ein projektspezifischer Vorschlag, unterschiedliche Eingangstypen durch geeignete zeitliche, räumliche oder symbolische Kodierungs- und Verarbeitungswege zu führen und sie kontrolliert zu koppeln. Die ausführliche Form des Namens ist eine Architekturbezeichnung, kein Ergebnis.

**Abgrenzung:** Die grobe Einteilung „Audio zeitlich, Bild räumlich, Sprache symbolisch“ ist keine vollständige Charakterisierung dieser Daten. Bilder können zeitliche Folgen, Audio räumliche Hinweise und symbolische Daten zeitliche Struktur enthalten. Eine feste Pfadzuweisung kann deshalb ungeeignet sein.

**Prüfung:** Verglichen werden spezialisierte und gemeinsame Verarbeitungswege bei gleichem Gesamtbudget, geeigneten Einzelmodalitätskontrollen und gestörter Verfügbarkeit. Ein Vorteil muss an einer vorher definierten Aufgabe erscheinen. Die im kanonischen Register offenen MSBA-Hypothesen werden durch die Definition nicht bestätigt.

<a id="begriff-lernleistung"></a>
## F.13 Lernen gegenüber bloßer Plastizität

**Bedeutung:** Plastizität bezeichnet eine Zustands- oder Parameterveränderung. Funktionales Lernen bezeichnet hier eine durch Erfahrung verursachte Verbesserung eines vorab definierten Leistungskriteriums, die unter geeigneten Kontrollen bestehen bleibt.

**Beispiel:** Nach Training sinkt der Fehler auf nicht zum Training verwendeten Beispielen stärker als in einem angeglichenen Netz ohne die untersuchte Lernregel. **Gegenbeispiel:** Gewichte wachsen, aber die Aufgabenleistung bleibt unverändert oder verschlechtert sich. Das belegt Plastizität, nicht den beanspruchten Lernerfolg.

**Prüfung:** Trainings- und Testdaten, Baselines, Datenreihenfolge, Optimierungsbudget, unabhängige Initialisierungen und der Zeitpunkt der Auswertung werden festgelegt. Ein externer Decoder darf nicht unbemerkt die gesamte Lernaufgabe übernehmen. Ein positiver Unterschied beweist zunächst nur die im Vergleich identifizierte Funktion.

<a id="begriff-gedaechtnis"></a>
## F.14 Funktionales Gedächtnis

**Bedeutung:** eine vergangenheitsabhängige interne Zustandsänderung, aus der nach einem festgelegten Verzögerungs- und gegebenenfalls Störintervall aufgabenrelevante Information genutzt werden kann. Dauerhafte Aktivität allein ist dafür nicht hinreichend.

**Beispiel:** Nach Ende eines Reizes und ohne erneuten Zugang zu dessen Kennzeichnung kann ein zurückgehaltener Test zeigen, welche Information im Zustand erhalten blieb. **Gegenbeispiel:** Ein identischer Oszillator läuft nach jedem möglichen Reiz gleich weiter. Er ist persistent, unterscheidet aber die Reize nicht.

**Prüfung:** Verzögerungsaufgabe mit ausgeglichenen Reizen, eingefrorenem Ausleseverfahren, kontrollierten externen Speichern und Zustandsintervention. Wichtig sind Informationsträgerschaft und kausale Nutzung: reine Dekodierbarkeit zeigt noch nicht, dass das System selbst diese Information für seine Aktion verwendet. [P2](section-047.md#proof-p2) zeigt die Unzulänglichkeit von Aktivitätssummen ausdrücklich.

<a id="begriff-generalisierung"></a>
## F.15 Generalisierung und fortlaufendes Lernen

**Bedeutung:** Generalisierung betrifft Leistung auf nicht zur Anpassung verwendeten Fällen innerhalb eines angegebenen Verteilungs- oder Aufgabenwechsels. Fortlaufendes Lernen betrifft die sequenzielle Anpassung desselben lernenden Systems bei gleichzeitiger Prüfung früherer Aufgaben.

**Gegenbeispiele:** Wiederholte Auswertung derselben Trainingsfälle ist keine unabhängige Generalisierungsprüfung. Drei separat neu initialisierte erfolgreiche Aufgabenläufe zeigen kein Behalten während fortlaufenden Lernens. Eine perfekte Erfolgsquote sagt ohne Testumfang, Aufgabenverteilung und Resetvertrag wenig aus.

**Prüfung:** Datensplits und Modellselektion bleiben getrennt. Bei fortlaufendem Lernen wird nach jeder Trainingsphase die Leistung auf allen relevanten Aufgaben protokolliert; Resets und zusätzliche Speicher werden offengelegt. Vergessen wird als definierter Leistungsunterschied gemessen, nicht aus einer allgemeinen Erfolgsampel abgelesen.

<a id="begriff-kausale-attribution"></a>
## F.16 Kausale Leistungszuordnung

**Bedeutung:** die begründete Aussage darüber, welchen Beitrag eine bestimmte Komponente zu einem definierten Ergebnis unter bestimmten Bedingungen leistet. Ein gemeinsam auftretendes Signal ist noch kein kausaler Beitrag.

**Prüfung:** Komponenten werden kontrolliert deaktiviert, ersetzt, zustandsverändert oder in ihrer Information begrenzt. Ressourcen, Auslesewege und unerwünschte Nebeneffekte der Eingriffe müssen berücksichtigt werden. Redundante Komponenten können trotz kausaler Bedeutung einzeln entbehrlich erscheinen; ein beschädigender Eingriff kann umgekehrt viele Aufgaben unspezifisch verschlechtern. Deshalb benötigt Attribution mehrere passende Kontrollen und möglichst Wiederherstellung des gezielten Zustands.

**Grenze:** Ein Leistungsabfall nach Ablation zeigt nicht ohne weitere Annahmen einen einzigen Mechanismus. Eine unveränderte Leistung zeigt nicht notwendig Irrelevanz. Das einfache Nichtidentifikationsargument [P3](section-047.md#proof-p3) begründet den Bedarf an Eingriffen, aber nicht die Vollständigkeit eines beliebigen Ablationsdesigns.

<a id="begriff-5d"></a>
## F.17 Adressdimension und funktionale Geometrie

**Bedeutung:** Die Adressdimension ist die Zahl der Koordinaten eines Knotennamens. Funktionale Geometrie liegt im hier verwendeten technischen Sinn vor, wenn Distanzen oder Nachbarschaften wirksame Modellregeln beeinflussen und sich ihre Beziehung zur Funktion prüfen lässt.

Ein fünfteiliges Tupel erzeugt für sich keine neue Rechenleistung. Eine Distanzregel kann dagegen Konnektivität und Verzögerungen ändern. Der kontrollierte Unterschied zwischen diesen beiden Fällen ist der Kern von [Kapitel 15](section-019.md) und [P1](section-047.md#proof-p1). Der Begriff „5D“ wird nicht zugleich als Metapher für Bewusstsein oder besondere Intelligenz verwendet.

<a id="begriff-digital-state-twin"></a>
## F.18 Digital State Twin

**Bedeutung:** ein für einen bestimmten Wiederherstellungs- oder Vergleichszweck hinreichend vollständiger, versionierter Zustandsdatensatz. Der Begriff benennt einen Datenvertrag, nicht automatisch ein vollständiges Duplikat aller inneren und äußeren Bedingungen.

**Beispiel:** Ein definierter Zustand samt Zufallsgenerator, Ereigniswarteschlange und Konfiguration wird gespeichert und unter demselben Vergleichsvertrag wiederhergestellt. **Gegenbeispiel:** Ein Screenshot der Aktivität oder eine Datei nur mit Gewichten reicht nicht aus, wenn andere Zustandskomponenten das weitere Verhalten bestimmen.

**Prüfung:** Roundtrip und Prozessneustart werden getrennt getestet; relevante Felder, Versionsmigration und numerische Toleranzen müssen feststehen. Die vorhandenen technischen Speichertests sind dafür begrenzte Anhaltspunkte, kein funktionaler Erinnerungsnachweis.

<a id="begriff-provenienz"></a>
## F.19 Provenienz und Evidenzstatus

**Bedeutung:** Provenienz beschreibt die nachvollziehbare Herkunft eines Artefakts: ausführender Code, Konfiguration, Eingaben, Umgebung, Erzeugungs- und Veränderungsschritte. Ein Evidenzstatus ist dagegen eine dokumentierte Bewertung einer bestimmten Aussage.

Ein Hash kann die Identität von Bytes prüfen, nicht ihren Wahrheitsgehalt. Ein Dirty Tree zeigt nicht automatisch ungültige Messwerte, erschwert aber ohne vollständigen Patch die Rekonstruktion des ausgeführten Codes. Eine später sauber eingecheckte Zusammenfassung behebt diese Lücke nicht rückwirkend. Ein freigegebener technischer Nachweis darf nicht auf eine breitere Behauptung übertragen werden.

**Prüfung:** Herkunftskette und Geltungsbereich werden getrennt geprüft; fehlende Daten oder Reviewentscheidungen bleiben explizit offen. Die Publikation ist keine alternative Instanz zur automatischen Freigabe kanonischer EVID-Einträge.

<a id="begriff-kompaktierung"></a>
## F.20 Provenienzerhaltende Kompaktierung

**Bedeutung:** eine begrenzte, auf eine bestimmte Prüfaufgabe zugeschnittene Darstellung umfangreicher Laufdaten, die auf unveränderte oder nachvollziehbar archivierte Rohdaten zurückführt. Sie soll die Verarbeitung erleichtern, ohne die Herkunft zu verlieren.

**Beispiel:** Ein aktuelles Laufpaket enthält ausgewählte Kennzahlen, Fehlerfälle, Definitionen und eindeutige Rohdatenzeiger. **Gegenbeispiel:** Ein langer Bericht wird gelöscht und durch eine frei formulierte Erfolgserzählung ersetzt, aus der weder Kennzahlen noch Abweichungen rekonstruierbar sind.

**Prüfung:** Für vorher bestimmte Abfragen wird geprüft, ob das kompakte Paket dieselben Antworten ermöglicht; Auslassungen werden markiert. Eine universell verlustfreie Kurzfassung aller künftig denkbaren Fragen wird nicht behauptet. Informationsverlust, Kosten und Prüfaufgabe müssen zusammen betrachtet werden.

<a id="begriff-emergenz"></a>
## F.21 Selbstorganisation und Emergenz

**Bedeutung:** Selbstorganisation bezeichnet im Arbeitsgebrauch die Ausbildung von Ordnung durch lokale Wechselwirkungen unter bestimmten Randbedingungen. Emergenz bezeichnet eine Beschreibungsebene, auf der ein kollektives Muster untersucht wird. Keine der beiden Bezeichnungen ist hier eine Erklärung kraft Benennung.

**Beispiel:** Wiederholbar entstehende Strukturmerkmale werden gegenüber Anfangsbedingungen und passenden Nullmodellen untersucht. **Gegenbeispiel:** Eine vom Entwickler fest eingetragene Regionenanordnung wird als spontan entstandene Organisationsleistung bezeichnet.

**Prüfung:** Der Entstehungspfad, externe Vorgaben, Kontrollbedingungen und Robustheit werden dokumentiert. Nichtlinearität oder überraschendes Verhalten allein belegen weder Lernen noch Autonomie. Ein behaupteter Mechanismus muss sich in genauer beschriebenen Regeln und Eingriffen wiederfinden.

<a id="begriff-neuheit"></a>
## F.22 Neuheit, Erkenntnisgewinn und theoretischer Beitrag

**Bedeutung:** Neuheit kann sich auf ein Artefakt, ein Ergebnis innerhalb dieses Projekts, eine neue Anwendung bekannter Methoden oder eine wissenschaftliche Erstentdeckung beziehen. Diese Reichweiten müssen ausdrücklich unterschieden werden.

Die formalen Argumente dieser Revision sind neu ausgearbeitete Bestandteile der Abhandlung. Ihre Grundprinzipien werden nicht als bisher unbekannte Mathematik ausgegeben. Ein empirischer Erkenntnisgewinn müsste über eine passende Baseline hinausgehen oder einen belastbaren negativen Befund liefern. Ein sorgfältig nachgewiesenes Fehlen eines relevanten 5D-Vorteils wäre ein Ergebnis, kein Scheitern der wissenschaftlichen Methode.

**Prüfung:** Jede Beitragsbehauptung benennt Ausgangswissen, konkretes neues Resultat, Nachweis und Geltungsgrenze. Eine neue Bezeichnung ohne diesen Unterschied genügt nicht. Die [Beitragsbilanz](section-040.md) verwendet genau diese Struktur.

[Inhaltsübersicht](README.md) | [Zurück](section-045.md) | [Weiter](section-047.md)
