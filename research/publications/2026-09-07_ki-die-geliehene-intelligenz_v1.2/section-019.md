[Inhaltsübersicht](README.md) | [Zurück](section-018.md) | [Weiter](section-020.md)

<a id="b5d-fünfdimensionaler-adressraum-und-dynamischer-graph"></a>
# 15. Fünfdimensionaler Adressraum und dynamischer Graph

## 15.1 Die zentrale Frage ist ein Mechanismus, nicht eine Zahl

Brain-5D bezeichnet das Projekt und seine bisherige Architekturwahl. Der Name ist kein Ergebnis eines bereits gewonnenen Dimensionsvergleichs. Die wissenschaftliche Behauptung muss enger formuliert werden: Unter welchen Aufgaben, Ressourcenbudgets und geometrieabhängigen Regeln verbessert eine bestimmte Einbettung die beobachtete Leistung? Für eine Überlegenheit von fünf Dimensionen gegenüber zwei, drei, vier oder sechs Dimensionen liegt in den hier ausgewerteten Berichten kein belastbarer Nachweis vor.

<a id="b5d-zwei-verschiedene-bedeutungen-von-fünf-dimensionen"></a>
Der philosophische Beschreibungsvektor I = (M, E, G, Z, X) und die technischen Koordinaten p = (x, y, z, a, b) beziehen sich auf verschiedene Gegenstände. Der erste ordnet Betrachtungsaspekte, der zweite adressiert oder geometrisiert Knoten. Die gleiche Komponentenanzahl begründet weder eine Entsprechung noch eine neurobiologische Erklärung. Auch eine mögliche empirische Überlegenheit der Architektur würde den philosophischen Vektor nicht dadurch bestätigen.

<a id="b5d-der-fünfdimensionale-raum"></a>
<a id="b5d-adressraum-und-materialisierung"></a>
## 15.2 Adressraum, Population und tatsächliche Ressourcen

**DEF:** Für eine Dimensionszahl D und eine ganzzahlige Kantenlänge L sei der diskrete Adressraum

$$A_D = \{0,\ldots,L-1\}^{D}, \qquad |A_D|=L^D.$$

Die materialisierten Neuronen bilden eine Teilmenge V des Adressraums; die Zahl N = |V| ist separat festzulegen. Bei L = 50 und D = 5 sind 312.500.000 Adressen möglich. Daraus folgen weder ebenso viele angelegte Neuronen noch ebenso viele aktive Zellen oder physisch verfügbare Rechenressourcen. Eine Adresse, ein Objekt, ein aktives Neuron und eine gespeicherte Zustandskomponente sind verschiedene Einheiten.

Ein Dimensionsvergleich bei identischem L verändert die potenzielle Kapazität exponentiell. Ein fairer Aufgabenvergleich fixiert deshalb zuerst N und ein Synapsen- und Rechenbudget, nicht nur die Kantenlänge. Eingangsenergie, Simulationsdauer, neuronale Parameter und Datenzugang müssen ebenfalls kontrolliert oder als bewusst variierte Faktoren ausgewiesen werden.

<a id="b5d-semantik-der-dimensionen"></a>
### Semantik ist eine Modellannahme

Zusätzliche Achsen können vorab zugewiesene funktionale Kategorien, entwicklungsabhängige Positionen oder eine lernbare Einbettung ausdrücken. Diese Varianten sind nicht austauschbar. Ein Netz mit handcodierten Modalitätsachsen besitzt bereits eine vom Entwickler vorgegebene Struktur; deren Wirkung darf nicht als allein entstandene Selbstorganisation ausgegeben werden. Eine lernbare Metrik ist ein anderes Modell als eine starre Koordinatenkonvention. Jede Variante benötigt eine eigene Konfiguration und eine passende Kontrollbedingung.

<a id="b5d-adressraum-oder-funktionale-geometrie"></a>
## 15.3 Ein bedingtes Invarianzresultat

**PROOF – Kurzfassung von P1:** Werden lediglich die Adressen eines festen Netzwerks geändert, während alle wirksamen Zustandsübergänge, Kanten, Gewichte, Verzögerungen, Ein- und Ausgänge sowie Zufallsfolgen unter derselben Knotenabbildung erhalten bleiben, dann bleibt auch die entsprechend zurückübersetzte Trajektorie erhalten. Der vollständige Induktionsbeweis steht in [Anhang G.1](section-047.md#proof-p1).

Damit wird eine wichtige Fehlfrage ausgeschlossen: Ein korrekt koordinatenunabhängig ausgeführtes Netzwerk kann nicht allein deshalb andere semantische Zustände erzeugen, weil seine Knoten jetzt Tupel der Länge fünf statt drei als Namen tragen. Laufzeit- oder Speicheraufwand der Implementierung können dennoch verschieden sein. Ein geänderter Iterations- oder Rundungspfad kann außerdem die Voraussetzungen verletzen. Das Resultat ist daher kein ohne Codeprüfung geltender Satz über jede Brain-5D-Ausführung.

**Forschungsgewinn:** Die Architekturhypothese wird in zwei unterscheidbare Fragen zerlegt. Erstens: Ist die Implementierung unter bloßer Umadressierung invariant? Zweitens: Welchen funktionalen Beitrag leisten Regeln, die Koordinaten tatsächlich verwenden? Ein positiver Unterschied im zweiten Versuch ist nicht mit einer Widerlegung des ersten Satzes gleichzusetzen, denn die Voraussetzungen sind verschieden.

<a id="b5d-allgemeine-metrik"></a>
## 15.4 Eine geometrisch wirksame Modellfamilie

Für die Differenz zweier Koordinatenvektoren und eine symmetrische Matrix M wird definiert:

$$d_M(p_i,p_j)=\sqrt{(p_i-p_j)^T M(p_i-p_j)}.$$

Bei positiver Definitheit ist dies eine Metrik; bei nur positiver Semidefinitheit kann sie verschiedene Punkte auf Abstand null abbilden und ist im Allgemeinen eine Pseudometrik. Eine diagonale Matrix gewichtet einzelne Achsen. Nichtdiagonale Einträge koppeln Achsen in der Distanzberechnung, liefern aber für sich genommen keine semantische Interpretation.

<a id="b5d-lernbare-metrik"></a>
Eine mögliche positiv definite Parametrisierung lautet M = B^T B + εI mit ε > 0. Das ist eine Konstruktionsregel, kein Nachweis, dass eine entsprechende Metrik bereits erfolgreich gelernt wurde. Optimierung müsste Kollaps, extreme Eigenwerte und triviale Ressourcensteigerung kontrollieren. Eine Kombination aus Aufgabenfehler und Regularisierung ist eine zu untersuchende Modellfamilie. Die in der Ausgangsfassung angeführte Metriklernliteratur bleibt als historische Anschlussliteratur erhalten; aus ihrer Existenz folgt keine Validierung der projektspezifischen Übertragung.

![Konzeptionelle, nicht empirische Darstellung einer möglichen funktionalen Geometrie.](../2026-09-07_ki-die-geliehene-intelligenz/abbildungen/K1_image2.png)

Abbildung 6. Übernommenes Konzeptbild. Es zeigt keine gemessene Dimensionsüberlegenheit.

<a id="b5d-normierung-und-einheiten"></a>
Vor einem Vergleich sind Koordinatenskalierung, Randbedingungen und die Umrechnung von Distanzen in Wahrscheinlichkeiten oder Verzögerungen festzulegen. Identische Distanzschwellen in verschieden dimensionalen Räumen erzeugen nicht automatisch vergleichbare Nachbarschaften. Offene und toroidale Grenzen sind verschiedene Bedingungen. Eine nachträgliche Wahl der Normierung anhand des besten Testergebnisses ist Hyperparameterselektion und muss innerhalb des Trainings- beziehungsweise Validierungsverfahrens bleiben.

<a id="b5d-dynamischer-graph-und-graphentheorie"></a>
<a id="b5d-formale-graphdefinition"></a>
## 15.5 Dynamischer Graph und kausale Wirkung der Geometrie

**DEF:** Der materialisierte Graph wird durch Knoten V, gerichtete Kanten E, Gewichte W, Verzögerungen Δ, Typen T und Ressourcen- beziehungsweise Herkunftsattribute R beschrieben:

$$G_t=(V_t,E_t,W_t,\Delta_t,T_t,R_t).$$

Diese Definition beschreibt mögliche Zustandsbestandteile, nicht deren vollständige Implementierung in jeder Version. Die Koordinaten werden funktional relevant, sobald sie die Erzeugung von Kanten, Verzögerungen, Entwicklungsregeln, Lernregeln oder zulässige Sensor-Aktor-Kopplungen beeinflussen. Welcher Codepfad dies tut, muss für das konkrete Experiment benannt werden.

<a id="b5d-verbindungswahrscheinlichkeit"></a>
Beispielsweise kann eine vorgeschlagene Kantenregel eine logistische Linkfunktion mit Distanz- und Aktivitätsmerkmalen verwenden. Eine andere Familie wäre

$$P(i\to j)=P_0\exp[-d_M(p_i,p_j)/\sigma_d], \qquad 0\leq P_0\leq1,\;\sigma_d>0.$$

Diese Exponentialregel ist eine alternative Modellfamilie, nicht ohne weitere Transformation ein algebraischer Spezialfall einer logistischen Linkfunktion. Eine solche Regel muss außerdem angeben, wann Kanten gezogen werden und wie das Synapsenbudget eingehalten wird. Unkontrolliert mehr Kanten in einem Arm würden den Dimensionsvergleich verfälschen.

<a id="b5d-dimensionsablation"></a>
## 15.6 Zwei getrennte Vergleichsreihen

**Reihe A – Adressierungs-Kontrolle:** Ein festes semantisches Netzwerk wird mit D ∈ {2,3,4,5,6} injektiv adressiert. Die Rückübersetzung der Zustände, Topologie, Gewichte, Verzögerungen, Eingaben und Zufallsfolgen wird geprüft. Primärer Endpunkt ist die Trajektoriengleichheit unter dem vorher festgelegten numerischen Gleichheitsbegriff. Abweichungen zeigen einen wirksamen Codeunterschied oder verletzte Voraussetzungen, nicht automatisch einen wissenschaftlich vorteilhaften 5D-Effekt. Das kleine beigelegte Beispiel prüft ausschließlich eine binäre Ringkonstruktion, nicht diese Eigenschaft der gesamten Runtime.

**Reihe B – Geometrisch wirksame Architektur:** D variiert die tatsächlich genutzten geometrischen Regeln. Neuronenzahl, Synapsenzahl, Trainingsdaten, Simulationszeit und Optimierungsaufwand werden möglichst gleich gehalten. Der primäre Endpunkt ist eine vorab festgelegte Aufgabenleistung auf unangetasteten Testdaten. Laufzeit, Speicherbedarf und Graphmaße sind gesonderte sekundäre Endpunkte. Wird eine Budgetgleichheit technisch nicht erreicht, müssen die Unterschiede berichtet und die Schlussfolgerung entsprechend begrenzt werden.

Es gibt zwei verschiedene kausale Zielgrößen: Der **Gesamteffekt** einer geometrischen Architektur darf ihre durch D verursachte Topologieänderung einschließen. Ein **direkter Effekt bei festgehaltener Topologie** entfernt gerade diesen Vermittlungsweg. Beide Fragen sind sinnvoll, aber dürfen nicht vermischt werden. Insbesondere darf das Matching nicht unbemerkt genau die Eigenschaft eliminieren, über die die Hypothese wirken soll. Der Prüfentwurf in [Anhang H](section-048.md) benennt Zielgröße und Kontrollfamilie ausdrücklich.

Ein 5D-Vorteil gegenüber einer willkürlich schwachen 2D-Baseline ist kein Nachweis einer besonderen Stellung von fünf Dimensionen. Ein behauptetes Optimum bei fünf verlangt geeignete Vergleiche auch zu vier und sechs Dimensionen und darf nicht nach Sichtung der Testdaten definiert werden. Gleich gute Ergebnisse können eine einfachere Architektur nahelegen; fehlende statistische Signifikanz allein beweist jedoch keine Gleichwertigkeit. Eine vorab begründete praktische Äquivalenzmarge ist dafür gesondert erforderlich.

<a id="b5d-messgrößen"></a>
## 15.7 Messung und Interpretation

Gradverteilungen, Clustering, Pfadlängen, Modularität, Kantenlängen und Aktivitätsmaße charakterisieren das Netzwerk. Sie sind nicht automatisch Gütemaße für die Aufgabe. Höhere Modularität kann für eine Aufgabe nützlich und für eine andere hinderlich sein. Metriken werden deshalb mit ihrer mathematischen Definition, Einheiten, Bezugspopulation, Beobachtungszeit und den relevanten Kontrollgrößen berichtet. Fehlende Werte bleiben fehlend; sie werden nicht als null ausgegeben.

<a id="b5d-nullmodelle"></a>
Geeignete Kontrollen umfassen gradverteilungserhaltendes Rewiring, Gewichtsshuffles, koordinatenpermutierte Varianten, Verzögerungsshuffles und nichtgeometrische Reservoirs. Für jede Kontrolle ist anzugeben, welche Eigenschaft zerstört und welche erhalten wird. Eine Koordinatenpermutation bei anschließendem Neuaufbau des Graphen ist ein anderer Eingriff als eine reine Umbenennung bei unverändertem Graphen. Auch die Anzahl der Zufallsrealisierungen und der Anpassungsaufwand der Baselines gehören zur Vergleichbarkeit.

<a id="b5d-spektrale-perspektive"></a>
Spektrale Größen können als diagnostische Prädiktoren untersucht werden. Sie ersetzen keinen Funktionsnachweis des nichtlinearen Reset- und Plastizitätssystems. Ihre zusätzliche Erklärungskraft muss gegenüber einfacheren Größen wie Dichte und mittlerem Gewicht geprüft werden.

<a id="b5d-graphgeodäten-und-umgebungsdistanz"></a>
Schließlich sind Umgebungsdistanz d_M und kürzester beziehungsweise kostenminimaler Graphpfad d_G verschieden. Räumliche Nähe garantiert keine Kante; ein kurzer Graphpfad kann entfernte Koordinaten verbinden. Diese Unterscheidung verhindert, dass eine Visualisierung der Koordinaten bereits als Abbildung funktionaler Kausalität gelesen wird.

**Bilanz:** Die Kritik am ungeprüften 5D-Vorteil wird nicht durch eine stärkere Behauptung beantwortet. Die Revision beseitigt die Verwechslung von Name, Adressierung, Mechanismus und empirischer Leistung und liefert einen konkreten Prüfweg. Ob fünf Dimensionen in einer definierten Aufgabenfamilie einen relevanten Vorteil besitzen, bleibt eine empirisch offene Frage.

[Inhaltsübersicht](README.md) | [Zurück](section-018.md) | [Weiter](section-020.md)


<a id="cognition-context-019"></a>
## Ergänzung der Fassung 1.2: Dimensionsvergleich als kontrollierter Funktionsversuch

Die neue Prüfung ist Bestandteil dieses Kapitels: [Dimensionsvergleich als kontrollierter Funktionsversuch](section-052.md). Dabei bleiben funktionaler Nachweis, theoriebedingte Interpretation, phänomenales Erleben und normative Bewertung getrennt. Die neuen kanonischen Fragen, Protokollentwürfe, Ethikregeln und technischen Grenzen werden im verknüpften Anhang konkretisiert; ältere Befunde erhalten dadurch keine weiter reichende Evidenzfreigabe.
