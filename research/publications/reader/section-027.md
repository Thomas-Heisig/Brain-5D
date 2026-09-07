[Inhaltsuebersicht](README.md) | [Zurueck](section-026.md) | [Weiter](section-028.md)

<a id="b5d-historische-versuche-und-explorative-ausgangsbefunde"></a>

# 23. Historische Versuche und explorative Ausgangsbefunde

<a id="b5d-historische-messgrenzen-exp-gen-0009-bis-exp-gen-0012"></a>

## Historische Messgrenzen: EXP-GEN-0009 bis EXP-GEN-0012

Die Projektdokumentation beschreibt für die frühen Network-Impulse-Läufe eine output-orientierte Instrumentierung, die keine sichtbaren Spikes beziehungsweise Aktivierung aufzeichnete. Die spätere Erweiterung des Probe-Vertrags erfasst unter anderem publizierte Spike-IDs, aktivierte Neuronen, synaptische Auslieferungen, Antwort- und Rückkehrlatenzen sowie Zustandsdigests. Die historischen DATA sollen nach der dokumentierten Projektregel unverändert bleiben. Ein neuer Lauf mit reparierter Beobachtung ist eine neue Untersuchung und keine nachträgliche Verbesserung alter Messdaten. \[R1\]

Damit sind zwei Behauptungen zu unterscheiden: “Die damalige Messung zeigte keine Aktivität” und “Im gesamten damaligen System gab es keine Aktivität”. Die erste beschreibt ein Artefakt. Die zweite verlangt eine ausreichende Beobachtungsabdeckung. Eine unzureichende Messkette kann weder Aktivität noch deren Abwesenheit sicher belegen. Der Fall ist deshalb nicht bloss ein Softwarefehler, sondern ein Beispiel für instrumentengebundene Erkenntnis.

<a id="b5d-exp-gen-0021-als-explorativer-ausgangspunkt"></a>

## EXP-GEN-0021 als explorativer Ausgangspunkt

Die KI-gekennzeichnete Nachanalyse zu `EXP-GEN-0021` beschreibt einen Omnibus-Lauf mit 57 Teilruns und den Seeds 42, 43 und 44. Sie ist ausdrücklich `interpretation_only` und nicht evidenzbildend. Ihre Rolle in der vorliegenden Abhandlung ist die eines dokumentierten Ausgangspunkts für Folgefragen. Messwerte, die nur aus dieser Nachanalyse übernommen werden, erhalten den Status “sekundär berichtet” und werden nicht nachträglich zu direkt geprüften Rohmessungen umetikettiert. \[R11\]

Der berichtete Rekurrenzvergleich zeigt denselben engen Effekt, der später im Replikationsbericht wiederkehrt: 3 statt 33 Spikes, 2 statt 33 synaptische Ereignisse und eine unveränderte Zahl von drei aktivierten Neuronen. Der Bericht beschreibt ausserdem einen Learning-on-Arm, in dem das mittlere Gewicht von **0,05 auf etwa 0,5172804698** ansteigt und ein binärer Erfolgsindikator von 0 auf 1 wechselt. Learning-off und Sham-Replay zeigen den entsprechenden Erfolg nicht. Die dokumentierte Beobachtung ist damit interessanter als eine blosse Gewichtsveränderung, bleibt aber auf einen kleinen funktionalen Test begrenzt. \[R11\]

Die aus den berichteten Zahlen berechnete Differenz lautet:

$$\Delta w=0{,}5172804698-0{,}05=0{,}4672804698.$$Die relative Zunahme gegenüber dem Ausgangswert beträgt rechnerisch:

$$100\cdot\Delta w/0{,}05=934{,}5609396\,\%.$$Diese große Prozentzahl ist teilweise Folge des kleinen Anfangswerts. Sie darf weder als prozentuale Zunahme von Intelligenz noch als Generalisierungsleistung gelesen werden. Gewichtsgrenzen, Lernrate, Anzahl der Updates und Aufgabenschwierigkeit sind für ihre Interpretation entscheidend. Die Rechnung ist im Begleitpaket reproduzierbar, nicht als neuer inferenzstatistischer Test ausgewiesen.

<a id="b5d-zeitliche-drift-ohne-spikes"></a>

## Zeitliche Drift ohne Spikes

Die Nachanalyse nennt für FAST, MEDIUM und SLOW mittlere Diskrepanzen von **2,62576e-05**, **3,78343e-05** und **4,61094e-05** bei einem 100.000-Tick-Fenster und gleichzeitig **0 berichteten Spikes**. Daraus ergibt sich eine horizontabhängige Zustandsabweichung, aber noch keine spike-getragene zeitliche Repräsentation. Subthreshold-Dynamik kann funktional relevant sein; das muss jedoch durch eine dafür geeignete Aufgabe und Intervention gezeigt werden. Der Unterschied zwischen “kein Spike” und “kein Zustand” ist genauso wichtig wie der Unterschied zwischen “Zustand” und “Gedächtnis”. \[R11\]

<a id="b5d-der-bisherige-dimensionsvergleich"></a>

## Der bisherige Dimensionsvergleich

Im kleinen Dimensionsvergleich lieferten die aufgeführten 1D-, 2D-, 3D- und 5D-Konfigurationen identische makroskopische Impulskennzahlen. Der spätere Suite-Bericht bestätigt ebenfalls diese Kennzahlen für die darin gezeigten Dimensionsarme und einen Zufallsgrapharm. Ein gemeinsamer trivialer Propagationspfad prüft damit vor allem die Ausführbarkeit verschiedener Einbettungen. Für eine Hypothese zur funktionalen Bedeutung der Geometrie ist entscheidend, ob die variierte Geometrie überhaupt in Verbindungsauswahl, Delay, Lernregel oder einer anderen kausal wirksamen Operation vorkommt. \[R5; R11\]

**Eigene logische Folgerung:** Wenn Graph, Gewichte, Delays, Anfangszustände, Inputs und Update-Regeln identisch bleiben und Koordinaten von keiner dieser Operationen gelesen werden, kann eine reine Umbenennung der Koordinaten keinen dynamischen Unterschied verursachen. Ein Nullbefund wäre dann durch das Design zu erwarten. Dies ist kein empirischer Beweis gegen 5D, sondern ein Hinweis auf die Identifizierbarkeit des Experiments. Ein aussagekräftiger Test muss den konkreten Wirkpfad der Geometrie vorab nennen.

[Inhaltsuebersicht](README.md) | [Zurueck](section-026.md) | [Weiter](section-028.md)
