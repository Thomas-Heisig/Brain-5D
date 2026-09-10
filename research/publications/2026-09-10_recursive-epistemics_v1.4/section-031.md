[Inhaltsuebersicht](README.md) | [Zurueck](section-030.md) | [Weiter](section-032.md)

<a id="b5d-msba-modalitäten-gateways-und-ressourcenverteilung"></a>

# 27. MSBA: Modalitäten, Gateways und Ressourcenverteilung

<a id="b5d-modalitätsspezifische-pfade-als-kontrollierte-architekturhypothese"></a>

## Modalitätsspezifische Pfade als kontrollierte Architekturhypothese

Die Projektdokumentation beschreibt MSBA und Neural Symbiosis als Erweiterungen des peripheren Embodiment-Rands. Audio, Vision und digitale Nutzlasten erhalten spezialisierte Schnittstellen. Externe Modelle und virtuelle Komponenten können über Adapter beteiligt werden. Der persistierte produktive SNN-Core bleibt dabei **5D**; die möglichen **1 bis 32 Dimensionen externer Projektionsräume** sind keine bereits realisierte N-D-Erweiterung des neuronalen Kernformats. \[R1; R13\]

Die sinnvolle Differenzierung liegt in den Datenverträgen, nicht in einer starren Analogie “Audio ist seriell, Sehen ist parallel, Digitales ist symbolisch”. Audio kann mehrkanalig und zeitlich-spektral repräsentiert werden. Video enthält ebenfalls Zeit. Digitale Daten können zeitkritische Ereignisse, strukturierte Dokumente oder unveränderliche binäre Nutzlasten sein. Diese eigene begriffliche Präzisierung verhindert, dass eine anschauliche Gehirnmetapher unbemerkt zur technischen Beschränkung wird.

Für einen Audiopfad sind beispielsweise Zeitstempel, Kanalzuordnung, Fensterlänge, Samplingrate und Encoderlatenz relevant. Für einen visuellen Pfad sind räumliche Auflösung, Aufmerksamkeitsbereich, zeitliche Zuordnung und Verlust durch Vorverarbeitung wichtig. Ein digitaler Pfad benötigt Integrität, Schema, Herkunft und gegebenenfalls eine exakte Byte-Erhaltung. Ein gedrosselter Datenstrom darf langsamer oder seltener zugelassen werden, ohne seinen Inhalt unbemerkt zu verändern. Welche Eigenschaften tatsächlich gelten, ist pro Adapter zu testen.

<a id="b5d-die-fünf-registrierten-msba-fragen"></a>

## Die fünf registrierten MSBA-Fragen

`RQ-MSBA-E01` untersucht Ressourcenverbrauch je verwertbarer Information oder korrekter Entscheidung. `RQ-MSBA-E02` fragt nach dem Nutzen kostenadaptiver Allokation unter gleichem Gesamtbudget. `RQ-MSBA-E03` betrifft adaptive visuelle ROI beziehungsweise Foveation ohne hart codierte Zielregion. `RQ-MSBA-E04` betrifft digitale Payload-Integrität trotz Drosselung. `RQ-MSBA-E05` untersucht gezielte modalitätsübergreifende Kompensation nach Ausfall oder Degradation. Im gelesenen Fragenfragment stehen alle fünf auf **open**, ohne zugeordnete Evidenz. Die Begrenzungen nennen fehlende bestätigende Läufe beziehungsweise noch nicht vollständig operationalisierte adaptive Pfade. \[R13\]

Diese Fragen liefern eine klare Verbindung zwischen Embodiment und Forschungsdesign. Eine geringere Last ist nur dann ein Erfolg, wenn sie nicht durch den Verlust notwendiger Information erkauft wird. Eine bevorzugte Bildregion ist nur dann ein adaptiver Befund, wenn sie nicht schon im Encoder festgelegt war. Eine nach Sensorverlust erhöhte Aktivität einer zweiten Modalität ist nur dann funktionale Kompensation, wenn sie die relevante Aufgabe verbessert und gegen einfachere Allokationsregeln besteht.

<a id="b5d-ressourcenmodell-ohne-scheingenauigkeit"></a>

## Ressourcenmodell ohne Scheingenauigkeit

Die Einführung von Kosten benötigt eine Festlegung ihrer Einheit. CPU-Zeit, GPU-Zeit, Speicherbelegung, Netzwerklast, elektrische Energie und Latenz sind unterschiedliche Größen. Ein gemeinsamer Score kann als technische Heuristik nützlich sein, muss aber seine Gewichte offenlegen. Er ist ohne Messung und Kalibrierung keine physikalische Energie. Ein Vergleich verschiedener Modalitäten verlangt zudem eine sinnvolle gemeinsame Aufgabe oder ein explizites Multi-Objective-Modell; “Information pro Joule” ist ohne Definition und Schätzung der Information nicht bereits eine objektive Leistungskennzahl.

Die Projektdokumentation warnt bereits vor einem globalen signierten Homöostase-Reward, bei dem sich gegensätzliche Abweichungen aufheben. Ein elementares Beispiel macht dies deutlich: Zwei Populationen mit Fehlern +a und -a haben einen mittleren signierten Fehler von null, obwohl beide vom Soll abweichen. Absolute und quadratische Fehler verhindern diese spezielle Auslöschung, setzen aber andere Prioritäten. Quadratische Kosten bestrafen große Abweichungen stärker; absolute Kosten können robuster gegen einzelne Spitzen sein. Welche Regel nützlich ist, bleibt eine kontrollierte Vergleichsfrage. \[R1; eigene algebraische Erläuterung\]

Als heuristische Modellfamilie, nicht als bereits validierte Lernregel, kann ein Ressourcenentscheid formuliert werden als:

$$U(a)=\widehat{Q}(a)-\lambda_C C(a)-\lambda_L L(a)-\lambda_R R(a),$$wobei Q erwarteten Aufgabennutzen, C Ressourcenverbrauch, L Latenz und R eine definierte Risikogröße bezeichnet. Schätzunsicherheit und harte Safety-Grenzen dürfen in dieser gewichteten Summe nicht verschwinden. Eine verbotene Aktion bleibt verboten, auch wenn ihr berechneter Nutzen hoch ist. Dies begründet eine getrennte harte Zulassungsprüfung vor weicher Optimierung.

<a id="b5d-gateway-plastizität-und-kernlernen"></a>

## Gateway-Plastizität und Kernlernen

Ein adaptiver Gateway kann den neuronalen Input so stark vorverarbeiten, dass der eigentliche Lernerfolg ausserhalb des SNN entsteht. Umgekehrt kann ein zu restriktiver Encoder relevante zeitliche Struktur entfernen und einen tatsächlich geeigneten Kern unfähig erscheinen lassen. Die kausale Zurechnung verlangt deshalb mindestens Frozen-, Random-, Timing-Shuffle- und Information-Destroyed-Kontrollen, getrennte Zustandsprotokolle und identische Ressourcenbudgets. Die Projektdokumentation fordert entsprechend, Gateway-Plastizität ausserhalb ausdrücklich registrierter Experimentpfade deaktiviert zu lassen. \[R1\]

Ein positives multimodales Ergebnis muss am Ende mindestens drei Fragen beantworten: Welche Information war in welchem Pfad verfügbar? Welche Zustandskomponente veränderte sich durch Erfahrung? Welche gezielte Ablation beseitigt den zusätzlichen Nutzen? Erst diese Verbindung aus Verfügbarkeit, Lernen und Intervention erlaubt eine eng gefasste Aussage über multimodale Kompetenz.

[Inhaltsuebersicht](README.md) | [Zurueck](section-030.md) | [Weiter](section-032.md)
