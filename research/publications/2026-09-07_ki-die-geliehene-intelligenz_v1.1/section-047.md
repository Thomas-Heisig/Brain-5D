[Inhaltsübersicht](README.md) | [Zurück](section-046.md) | [Weiter](section-048.md)

<a id="b5d-anhang-g-formale-ergebnisse"></a>
# Anhang G – Formale Ergebnisse, Gegenbeispiele und ausführbare Prüfung

## G.0 Status der Beiträge

Dieser Anhang enthält eigene Ausarbeitungen bedingter Argumente. Sie ersetzen keine empirischen Brain-5D-Versuche. Ihr Wert liegt darin, zulässige und unzulässige Schlussfolgerungen präzise zu trennen. Die zugrunde liegenden Prinzipien – Umbenennungsinvarianz, Informationsverlust durch Aggregation und Beobachtungsäquivalenz – werden nicht als weltweit neue mathematische Entdeckungen beansprucht. Die Nachweise sind vollständig im Text nachvollziehbar; das beigefügte Programm überprüft endliche Beispiele, nicht die allgemeine Gültigkeit durch erschöpfende Simulation.

<a id="proof-p1"></a>
## G.1 P1: Bedingte Invarianz unter reiner Umadressierung

### Aussage und Voraussetzungen

Sei V eine endliche Knotenmenge. Ein Zustand x enthält alle für die betrachtete Dynamik relevanten Knotenzustände, Kanten, Gewichte, Verzögerungen und weiteren Speicherbestandteile. Die Entwicklung sei

$$x_{t+1}=F_t(x_t,u_t,\xi_t),$$

wobei u_t der externe Eingang und ξ_t eine gegebenenfalls verwendete Zufallskomponente ist. Für D ∈ {2,3,4,5,6} sei ℓ_D eine injektive Adressabbildung von V in einen hinreichend großen D-dimensionalen Adressraum. Sie induziert eine umkehrbare Umbenennung ρ_D der tatsächlich verwendeten Zustände und Ein-/Ausgabezuordnungen.

Vorausgesetzt wird ausdrücklich, dass die D-adressierte Implementierung genau den konjugierten Übergang verwendet:

$$F_t^{(D)}(\rho_D(x),\rho_D(u),\xi)=\rho_D(F_t(x,u,\xi)).$$

Diese Bedingung schließt ein, dass keine zusätzliche Abhängigkeit von numerischen Koordinaten, einer veränderten Iterationsreihenfolge oder einem anders zugeordneten Zufallsstrom eingeführt wird. Anfangszustand und Eingänge werden konsistent abgebildet, die Zufallsfolgen werden gekoppelt.

**Dann gilt für jeden betrachteten Zeitschritt:**

$$x_t^{(D)}=\rho_D(x_t).$$

Insbesondere sind alle unter der Rückübersetzung verglichenen funktionalen Ausgaben identisch.

### Beweis durch Induktion

Für t = 0 gilt die Aussage aufgrund der Voraussetzung über den Anfangszustand. Gelte sie für t. Dann folgt aus der Übergangsbedingung:

$$x_{t+1}^{(D)}=F_t^{(D)}(\rho_D(x_t),\rho_D(u_t),\xi_t)=\rho_D(F_t(x_t,u_t,\xi_t))=\rho_D(x_{t+1}).$$

Damit gilt sie auch für t + 1 und folglich für alle betrachteten Schritte. Bei stochastischer Dynamik ist dies eine pfadweise Aussage unter derselben gekoppelten Zufallsfolge. Nur gleichverteilte, aber nicht gekoppelte Zufallsfolgen liefern im Allgemeinen keine Trajektoriengleichheit; unter entsprechenden Äquivarianzannahmen kann dann lediglich eine Verteilungsgleichheit gemeint sein.

### Konsequenz für Brain-5D

Die Dimension eines reinen Namensraums kann unter diesen Voraussetzungen keine zusätzliche aufgabenbezogene Dynamik erzeugen. Eine Behauptung funktionaler Überlegenheit muss einen Mechanismus nennen, der die Voraussetzungen verändert: beispielsweise distanzabhängige Kanten, Verzögerungen, räumliche Lernregeln oder Ressourcenallokation. Der Satz gilt nicht automatisch für jede existierende Runtime-Version; die Äquivarianz ihrer konkreten Codepfade ist eine eigene Testpflicht.

**Nicht behauptet:** gleiche Laufzeit, gleicher Speicherbedarf oder gleiche numerische Rundungsfehler unabhängig von Implementierungsdetails. Auch ein bloßes Umstellen der Datenstruktur kann solche Eigenschaften verändern. Der Satz trennt semantische Dynamik von Kosten der Repräsentation.

### Endliches Beispiel und Negativkontrolle

`methodenpruefung.py` konstruiert einen binären gerichteten Ring aus zwölf Knoten. Das ist ausdrücklich nicht das Brain-5D-Neuronenmodell. Über 64 Aktualisierungen werden 65 Zustände aufgezeichnet. Die Adressierung variiert von zwei bis sechs Dimensionen, ohne Knotenmenge oder Regeln zu ändern. Eine zusätzliche Permutation benennt die Knoten um. Alle rückübersetzten Trajektorien bleiben gleich. Entfernt man dagegen eine Kante, verändert sich die Trajektorie. Diese Negativkontrolle prüft, dass der Vergleich nicht nur einen konstanten oder leeren Verlauf als gleich erkennt.

<a id="proof-p2"></a>
## G.2 P2: Aktivitätssummen identifizieren gespeicherte Information nicht

### Aussage

Aus Gesamtspikezahl und Anzahl jemals aktivierter Kanäle lässt sich im Allgemeinen nicht bestimmen, ob ein Zustand Information über einen vergangenen Reiz trägt. Insbesondere sind diese Summen kein hinreichender Gedächtnisnachweis.

### Konstruktion

Ein Reiz X ist gleichverteilt auf {0,1}. Nach Ende des Reizes werden vier Zeitschritte mit zwei binären Kanälen beobachtet. Im Modell A wird für X = 0 in jedem Schritt (1,0), für X = 1 dagegen (0,1) ausgegeben. Im Modell B wird unabhängig von X in jedem Schritt (1,0) ausgegeben.

Für jeden Reiz und beide Modelle ist die Gesamtaktivität vier und genau ein Kanal jemals aktiv. Die beiden genannten Zusammenfassungen sind daher vollständig gleich. Im Modell A bestimmt die Identität des aktiven Kanals den vergangenen Reiz; ein Decoder, der den zweiten Kanal liest, ist immer korrekt. Im Modell B ist der gesamte Verlauf unabhängig vom Reiz. Bei der ausgeglichenen Reizverteilung ist die bestmögliche Klassifikationsgenauigkeit aus diesem Verlauf 1/2.

In informationstheoretischer Schreibweise gilt für den gesamten beobachteten Zustand Z somit I(X;Z_A) = 1 Bit und I(X;Z_B) = 0 Bit. Diese Werte folgen exakt aus der endlichen Konstruktion; sie sind keine aus Brain-5D-Messdaten geschätzten Kennzahlen. Für die beiden Aktivitätssummen ist die gegenseitige Information mit X in beiden Modellen null.

### Beweis und Reichweite

Eine Funktion ausschließlich der identischen Zusammenfassungen müsste für beide Modelle dasselbe Ergebnis liefern. Die tatsächlich verfügbare Reizinformation ist jedoch verschieden. Deshalb kann keine solche Funktion diese Information für alle zulässigen Modelle korrekt identifizieren. Das einzelne Gegenbeispiel genügt, um die allgemeine Behauptung der Hinreichendheit zu widerlegen.

Der Beweis zeigt nicht, dass ein bestimmtes Brain-5D-Netz kein Gedächtnis besitzt. Er zeigt, dass der Schluss von aggregierter Aktivität auf Gedächtnis nicht gerechtfertigt ist. Die konstruierten Verläufe enthalten kein gelerntes Verhalten und keinen Nachweis eigenständiger Nutzung durch einen Agenten. Dafür wären weitere funktionale und kausale Tests erforderlich.

### Anwendung auf den berichteten Rekurrenzvergleich

Der im historischen Bericht dokumentierte Unterschied von drei zu dreiunddreißig Spikes ist ein dynamischer Befund. Die ebenfalls berichtete Zahl von drei aktivierten Neuronen entscheidet die Informationsfrage nicht. Ein aussagekräftiger Folgetest muss Reizidentität, Verzögerung, Ausleseverfahren, externe Gedächtnispfade und Zustandsintervention kontrollieren. Das ist eine stärkere und überprüfbare Anforderung als die unspezifische Forderung nach „mehr Aktivität“.

<a id="proof-p3"></a>
## G.3 P3: Gleiche Antworten identifizieren den Leistungsträger nicht

### Aussage und Konstruktion

Sei U ein binärer Aufgabenreiz. Im beobachteten Zustand tragen sowohl ein Kernsignal S als auch eine externe Quelle L denselben Wert U. Zwei Modelle sind möglich:

$$\mathcal{M}_A:\;Y=S, \qquad \mathcal{M}_B:\;Y=L.$$

Beide erzeugen für alle beobachteten Fälle die gleiche Antwort Y = U. Auch die gemeinsame Beobachtung von U, S, L und Y unterscheidet sie unter S = L = U nicht. Trotzdem ist ihre Abhängigkeit verschieden: Wird S gezielt auf 1 − U gesetzt und L unverändert gehalten, antwortet Modell A mit 1 − U und Modell B mit U.

### Schlussfolgerung

Die beobachtete Antwortübereinstimmung identifiziert nicht, welcher der beiden Pfade die Antwort bestimmt. Eine allgemeine Attribution allein aus korrekten Antworten ist daher durch dieses Gegenbeispiel widerlegt. Der Unterschied wird erst durch einen geeigneten Eingriff oder zusätzliche identifizierende Annahmen zugänglich.

Die Konstruktion ist absichtlich klein und enthält keine empirischen Brain-5D-Daten. Sie beweist weder, dass ein konkreter Sprachbaustein den Kern stets umgeht, noch dass jede beliebige Ablation einen eindeutigen Nachweis liefert. In realen Systemen können Redundanz, Wechselwirkungen, Kompensation oder unspezifische Eingriffsschäden auftreten. Der Versuch muss deshalb Pfadisolierung, Eingriffsgenauigkeit und alternative Erklärungen prüfen.

### Konsequenz für Hybridarchitekturen

Bei einer Aufgabe mit Language Organ, Retrieval, Encoder, Decoder und neuronaler Runtime darf Erfolg nicht allein dem SNN zugeschrieben werden. Benötigt werden unter anderem Kernzustandsinterventionen, externe Pfadkontrollen, angeglichene Ressourcen und eine unveränderte Auswertungslogik. Wenn der externe Pfad allein dieselbe Aufgabe löst, muss der zusätzlich behauptete Kernbeitrag separat gezeigt werden. Eine reine Schreibsperre für das LLM hilft bei der Trennung, beweist für sich jedoch noch nicht, welcher Pfad die beobachtete Antwort erzeugt.

## G.4 Tatsächlich ausgeführte Methodenprüfung

Die begleitende Standardbibliothek-Datei wurde mit folgenden Befehlen ausgeführt:

```bash
python methodenpruefung.py --output methodenpruefung.json
python methodenpruefung.py --check methodenpruefung.json
```

Ergebnis: **28 bestandene deterministische Prüfungen**. Zwanzig betreffen Adressinjektivität, Tupeldimension, Trajektoriengleichheit und Umbenennung über fünf Dimensionswerte. Drei prüfen nichtleere beziehungsweise veränderliche Aktivität und die Kanten-Negativkontrolle. Zwei prüfen die gleichen Aktivitätssummen bei beiden Reizen. Eine prüft die unterschiedliche Dekodierbarkeit. Zwei prüfen Beobachtungsäquivalenz und ihre Aufhebung durch die Kernintervention.

Der [JSON-Bericht](methodenpruefung.json) enthält Konfiguration, konstruierte Verläufe, Prüfnamen und den SHA-256-Wert des tatsächlich ausgeführten Skripts. Er setzt `brain5d_runtime_executed`, `scientific_evidence_promotion` und `preregistered` ausdrücklich auf `false`. Die Ausführung prüft die Konsistenz der dargestellten Beispiele mit diesem Programm; sie ist weder eine Stichprobe aus der Brain-5D-Runtime noch eine unabhängige Replikation wissenschaftlicher Lernresultate.

**Reproduktionsgrenze:** Ein bestandener Beispieltest ersetzt nicht die Prüfung des allgemeinen Beweises. Umgekehrt hängt der mathematische Gegenbeweis nicht von einer statistischen Signifikanzberechnung über wiederholte Ausführung desselben Beispiels ab. Es wäre falsch, die 28 Assertions als n = 28 unabhängige Experimente zu behandeln.

## G.5 Was hier neu gewonnen wird und was nicht

Die Revision macht drei vorher nur allgemein angesprochene Nachweisprobleme explizit entscheidbar: Sie gibt die Voraussetzungen an, unter denen Dimensionalität als bloße Adressierung unwirksam ist; widerlegt die Hinreichendheit bestimmter Aktivitätssummen für einen Informationsnachweis; und widerlegt die Hinreichendheit korrekter Antworten für eine eindeutige kausale Attribution. Daraus folgen konkrete Ausschluss- und Kontrollanforderungen für weitere Versuche.

Diese Resultate erweitern die Abhandlung methodisch. Sie sind nicht als empirischer Architekturvorteil, als gelerntes Gedächtnis oder als neue allgemeine Intelligenztheorie zu zitieren. Ein nachfolgendes Experiment kann diese methodischen Argumente verwenden, muss seine eigenen Daten und Bedingungen jedoch separat dokumentieren.

[Inhaltsübersicht](README.md) | [Zurück](section-046.md) | [Weiter](section-048.md)
