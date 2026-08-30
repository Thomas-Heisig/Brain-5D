Brain-5D Storage -- Theoretisches optisches Speichermodell und digitaler Zwilling

Projekt: Brain-5D
Dokumenttyp: Technische Theorie- und Architekturgrundlage
Status: Forschungs-/Entwurfsmodell
Ziel: Beschreibung eines theoretischen optischen 5D-Speichers und
des im Brain-5D-System verwendeten digitalen Zwillings.

1. Zweck und Abgrenzung

Brain-5D benötigt langfristig einen Speicher für sehr große Mengen
dynamischer neuronaler Zustände. Neben den Neuronen selbst müssen
insbesondere Synapsen, elektrische Zustände, chemische Zustände,
räumliche Beziehungen und zeitliche Veränderungen abgebildet werden.

Dieses Dokument trennt deshalb ausdrücklich zwei Ebenen:

Original / theoretisches optisches Speichermodell: ein
hypothetisches physisches Speichermedium, in dem Information über
räumliche und optische Freiheitsgrade eines Punktes kodiert wird.

Digitaler Zwilling: die praktisch implementierbare digitale
Repräsentation desselben Informationsmodells im Brain-5D-Projekt.

Das optische Original ist kein Nachweis einer bereits realisierten
Brain-5D-Hardware. Einige zugrunde liegende Prinzipien --
dreidimensionale optische Speicherung, spektrale Kodierung,
Polarisation, Phase und holografische Verfahren -- sind physikalisch
bekannte Konzepte. Ihre gemeinsame Nutzung in genau der hier
beschriebenen Form ist jedoch ein theoretisches Systemmodell und muss
experimentell validiert werden.

Der digitale Zwilling ist dagegen unabhängig von einer späteren
optischen Hardware implementierbar und testbar.

2. Ausgangsgröße des Brain-5D-Raums

Die vorgesehene logische Zielausdehnung lautet

[ 50 \times 50{=tex} \times 50{=tex} \times 50{=tex}
\times 50{=tex}. ]

Damit ergibt sich

[ N = 50^5 = 312,500,000 ]

mögliche logische Neuronenpositionen.

Ein logisches Neuron besitzt somit eine 5D-Adresse

[ \mathbf{q}{=tex}=(q_0,q_1,q_2,q_3,q_4),
\qquad {=tex}q_i\in{=tex}{0,\ldots{=tex},49}. ]

Die fünf Dimensionen müssen nicht fünf physische Raumdimensionen
darstellen. Im digitalen System sind sie zunächst abstrakte Koordinaten.
Eine spätere Hardware kann sie durch räumliche Positionen und
zusätzliche optische Freiheitsgrade abbilden.

3. Grundidee des theoretischen optischen Speichers

Ein physischer optischer Speicherpunkt wird als Zustand

[
P=(x,y,z,\mathcal{S}{=tex},I,\Phi{=tex},\mathbf{S}{=tex},\mathbf{d}{=tex},\gamma{=tex},\tau{=tex},\ldots{=tex})
]

beschrieben.

Dabei bedeuten:

(x,y,z): räumliche Position,

(\mathcal{S}{=tex}): spektrale Verteilung,

(I): Intensität/Helligkeit,

(\Phi{=tex}): Phase,

(\mathbf{S}{=tex}): Polarisationszustand,

(\mathbf{d}{=tex}): Richtungsinformation,

(\gamma{=tex}): Kohärenzparameter,

(\tau{=tex}): zeitlicher Zustand bzw. Zeitreferenz.

Der Punkt ist damit nicht als klassischer RGB-Pixel zu verstehen,
sondern als mehrkanaliges optisches Zustandsobjekt.

3.1 Räumliche Position

Die ersten drei Freiheitsgrade sind

[ (x,y,z). ]

Bei einem regelmäßigen Raster mit Punktabstand (d) ergibt sich für einen
Würfel mit (N) Punkten näherungsweise

[ L \approx {=tex}d\sqrt[3]{N}{=tex}. ]

Für

[ N=312,500,000 ]

gilt

[ \sqrt[3]{N}{=tex}\approx678{,}{=tex}6. ]

Ein äquivalentes regelmäßiges 3D-Raster benötigt damit ungefähr (679^3)
Rasterplätze.

Bei (d=10,\mu {=tex}m) ergäbe sich rein geometrisch

[ L\approx6{,}{=tex}79,mm. ]

Dies ist keine Aussage über eine praktisch erreichbare
Speicherdichte. Reale Abstände hängen unter anderem von Wellenlänge,
numerischer Apertur, Schreibverfahren, Material, Übersprechen,
thermischer Stabilität und gewünschter Fehlerrate ab.

3.2 Kugelförmiges Medium

Für eine Kugel gilt

[ V=\frac{4}{3}{=tex}\pi {=tex}r^3. ]

Werden (N) diskrete Zellen mit charakteristischer Kantenlänge (d) als
Volumen (Nd^3) angenähert, folgt

[ \frac{4}{3}{=tex}\pi {=tex}r^3 = Nd^3 ]

und damit

[ r=d\left{=tex}(\frac{3N}{4\pi}{=tex}\right{=tex})^{1/3}. ]

Der Durchmesser lautet

[ D=2d\left{=tex}(\frac{3N}{4\pi}{=tex}\right{=tex})^{1/3}. ]

Würfel und Kugel sind deshalb alternative physische Geometrien. Der
Würfel vereinfacht Rasteradressierung; eine Kugel besitzt dagegen eine
isotropere Geometrie ohne ausgezeichnete Ecken.

4. Optische Informationskanäle eines Punktes

4.1 Spektrum

Statt nur RGB wird ein Spektrum als diskreter Vektor modelliert:

[ \mathcal{S}{=tex}=
(I_{\lambda{=tex}0},I{\lambda{=tex}1},\ldots{=tex},I{\lambda{=tex}_{K-1}}).
]

Brain-5D kann beispielsweise (K=32) Spektralkanäle verwenden. Die Kanäle
müssen im digitalen Zwilling nicht zwingend reale Wellenlängen
darstellen; sie können zunächst als optische Äquivalentkanäle dienen.

4.2 Intensität

Die normierte Intensität kann als

[ I\in[0,1]{=tex}]

definiert werden.

Bei (b) Bit Quantisierung stehen

[ Q=2^b ]

diskrete Zustände zur Verfügung. Die ideale Informationskapazität eines
einzelnen unabhängig auslesbaren Kanals beträgt damit

[ H=b;\text{Bit}{=tex}. ]

Diese Aussage gilt nur für ideal unterscheidbare Zustände. Rauschen
reduziert die praktisch nutzbare Kapazität.

4.3 Phase

Die optische Phase wird als

[ \Phi{=tex}`\in[0,2\pi)
]

beschrieben.

Eine digitale Quantisierung mit (b_\Phi) Bit verwendet

[
\Phi_q =
\operatorname{round}
\left(
\frac{\Phi}{2\pi}(2^{b_\Phi}-1)
\right).
]

Phase ist physikalisch nur relativ zu einer Referenz sinnvoll messbar und setzt daher ein geeignetes kohärentes Leseverfahren voraus.

4.4 Polarisation

Für eine vollständiger beschriebene Polarisation eignen sich Stokes-Parameter:

[
\mathbf{S}=(S_0,S_1,S_2,S_3).
]

Dabei beschreibt (S_0) die Gesamtintensität und (S_1,S_2,S_3) den Polarisationszustand.

Für vollständig polarisiertes Licht gilt idealisiert

[
S_0^2=S_1^2+S_2^2+S_3^2.
]

Allgemeiner ist der Polarisationsgrad

[
DoP=
\frac{\sqrt{S_1^2+S_2^2+S_3^2}}{S_0},
\qquad 0\le DoP\le1.
]

4.5 Richtung

Eine Richtung kann durch zwei Winkel beschrieben werden:

[
\mathbf{d}=(\theta,\varphi).
]

Alternativ kann ein normierter Richtungsvektor gespeichert werden:

[
\hat{\mathbf d}=
(\sin\theta\cos\varphi,
\sin\theta\sin\varphi,
\cos\theta).
]

4.6 Kohärenz

Ein vereinfachter digitaler Kohärenzkanal kann normiert als

[
\gamma\in[0,1]`{=tex}]

gespeichert werden. Eine reale optische Kohärenzbeschreibung ist
komplexer und kann von zeitlicher und räumlicher Korrelation abhängen.

5. Abbildung eines Neurons auf einen optischen Punkt

Das theoretische Modell behandelt den optischen Punkt als Träger eines
neuronalen Zustandsvektors

[ \mathbf {=tex}n=
(\mathbf {=tex}q,\mathbf {=tex}o,\mathbf {=tex}e,\mathbf {=tex}c,\mathbf {=tex}b,\mathbf {=tex}m).
]

Dabei sind:

(\mathbf {=tex}q): logische 5D-Adresse,

(\mathbf {=tex}o): optische Kanäle,

(\mathbf {=tex}e): elektrische Zustände,

(\mathbf {=tex}c): chemische Zustände,

(\mathbf {=tex}b): biologische bzw. dynamische Zustände,

(\mathbf {=tex}m): Metadaten.

Beispiele elektrischer Größen:

[ V_m=\text{Membranpotential}{=tex}, ]

[ V_{th}=\text{Aktivierungsschwelle}{=tex}, ]

[ r=\text{Recovery-/Refraktärzustand}{=tex}. ]

Ein Spike kann abstrakt als

[ s(t)=

\begin{cases}
1,&V_m(t)\ge V_{th}\\
0,&\text{sonst}
\end{cases}

]

modelliert werden.

Chemische Kanäle können beispielsweise normierte Konzentrations- oder
Aktivitätsäquivalente darstellen:

[ \mathbf {=tex}c= (c_{\mathrm{Glu}{=tex}},
c_{\mathrm{GABA}{=tex}}, c_{\mathrm{DA}{=tex}},
c_{\mathrm{5HT}{=tex}}, c_{\mathrm{ACh}{=tex}},
c_{\mathrm{NE}{=tex}}, c_{\mathrm{Ca}{=tex}},
c_{\mathrm{Na}{=tex}}, c_{\mathrm{K}{=tex}}, \ldots{=tex}). ]

Diese Werte sind im digitalen Zwilling zunächst Modellgrößen. Eine
direkte Gleichsetzung mit realen intrazellulären Konzentrationen ist nur
zulässig, wenn Einheiten, Messmodell und Dynamik explizit definiert
wurden.

6. Synapsen als Graph

Neuronale Beziehungen werden nicht sinnvoll durch bloße Nachbarschaft im
Voxelraum beschrieben. Deshalb ergänzt Brain-5D den
Punkt-/Voxel-Speicher durch einen gerichteten Graphen

[ G=(V,E). ]

Dabei ist

[ V={v_0,v_1,\ldots{=tex},v_{N-1}} ]

die Menge der Neuronen und

[ E\subseteq {=tex}V\times {=tex}V ]

die Menge gerichteter Synapsen.

Eine Synapse wird als Zustandsvektor modelliert:

[ e_{ij}=
(i,j,w,d,\sigma{=tex},\mathbf {=tex}r,\mathbf {=tex}t,p,\ell{=tex},\ldots{=tex})
]

mit beispielsweise:

Quellneuron (i),

Zielneuron (j),

Gewicht (w),

Verzögerung (d),

Synapsentyp (\sigma{=tex}),

Rezeptorzuständen (\mathbf {=tex}r),

Transmitterzuständen (\mathbf {=tex}t),

Plastizität (p),

Lernzuständen (\ell{=tex}).

Die geometrische Distanz zweier räumlich eingebetteter Neuronen kann
berechnet werden:

[ d_{ij}= \sqrt{
(x_i-x_j)^2+
(y_i-y_j)^2+
(z_i-z_j)^2
}{=tex}. ]

Sie muss daher nicht zwingend redundant gespeichert werden.

7. Kompakte Graphspeicherung

Für Milliarden möglicher Synapsen ist eine Objektliste ineffizient. Eine
geeignete Struktur ist beispielsweise Compressed Sparse Row (CSR).

Verwendet werden im Kern:

offsets[N+1],

targets[M],

parallele Property-Arrays für (M) Synapsen.

Für Neuron (i) liegen seine ausgehenden Synapsen im Bereich

[ [\mathrm{offsets}{=tex}[i],\mathrm{offsets}{=tex}[i+1]). ]

Dadurch muss die Quell-ID nicht für jede Synapse erneut gespeichert
werden.

Ist (M) die Zahl der Synapsen und (B_s) die mittlere Zahl Bytes pro
Synapse, ergibt sich näherungsweise

[ S_{\mathrm{graph}{=tex}} \approx{=tex} M B_s + (N+1)B_o, ]

wobei (B_o) die Größe eines Offset-Eintrags ist.

8. Feldspeicher

Nicht jede Information gehört in jedes einzelne Neuron. Räumlich
geteilte Größen werden als Felder gespeichert:

[ F_k(x,y,z,t). ]

Beispiele:

extrazelluläres elektrisches Potential,

chemische Gradienten,

Modulatorfelder,

Energieversorgung,

Temperatur,

regionale Aktivität.

Damit lautet das vollständige Modell

[ \boxed{
Brain5D = V + G + F + T
}{=tex} ]

mit:

(V): Voxel-/Neuronenraum,

(G): Synapsengraph,

(F): räumliche Felder,

(T): Zeit-/Änderungsschicht.

9. Zeitdimension und Ticks

Eine naive Speicherung jedes vollständigen Zustands für jeden Tick
skaliert als

[
S_{\mathrm{naiv}{=tex}}=T\cdot {=tex}S_{\mathrm{snapshot}{=tex}}.
]

Das ist bei großen Netzen ungeeignet.

Brain-5D verwendet konzeptionell deshalb

[ State(t)=State(t_0)+\sum{=tex}_{k=t_0+1}^{t}\Delta{=tex}_k. ]

Ein Basissnapshot wird mit Delta-Datensätzen kombiniert.

Ist (f) der Anteil veränderter Datensätze pro Tick, ergibt sich grob

[ S_{\mathrm{delta}{=tex}} \approx{=tex}
S_{\mathrm{base}{=tex}}+ T f S_{\mathrm{snapshot}{=tex}}+
S_{\mathrm{index}{=tex}}. ]

Für (f\ll1{=tex}) ist dies erheblich kleiner als die
Vollsnapshot-Speicherung.

Periodische neue Basissnapshots begrenzen die Rekonstruktionszeit.

10. Digitaler Zwilling

Der digitale Zwilling bildet das theoretische optische Modell auf
deterministische Binärdaten ab.

Die zentrale Trennung lautet:

[ \text{physikalische Bedeutung}{=tex} \longleftrightarrow{=tex}
\text{digitale Kodierung}{=tex}. ]

Beispielsweise:

Theoretisches Original   Digitaler Zwilling

räumliche Position       Koordinaten/ID
Spektrum                 Array quantisierter Kanäle
Helligkeit               Integer/Float-Kanal
Phase                    quantisierter Phasenwert
Polarisation             Stokes-Kanäle
Kohärenz                 normierter Kanal
Neuronenzustand          Binärrecord
Synapse                  Graphkante
chemisches Umfeld        Feldarray
Zeitentwicklung          Snapshot + Delta

Dadurch bleibt die Brain-5D-Logik unabhängig davon, ob der Speicher
später auf SSD, RAM, mmap-Dateien oder einer experimentellen optischen
Hardware liegt.

11. Aktuelles digitales Punktformat

Für den gegenwärtigen Entwurf wird ein fester Record von

[ B_N=128;\text{Byte}{=tex} ]

pro vollständigem optischem Neuron-Snapshot vorgesehen.

Für

[ N=312,500,000 ]

ergibt sich

[ S_N=N B_N ]

und damit

[ S_N= 312,500,000\cdot128{=tex} =
40,000,000,000;\text{Byte}{=tex}. ]

Das entspricht:

40,0 GB in dezimaler Angabe,

ungefähr 37,25 GiB binär.

Dies betrifft nur die Neuronenrecords eines Vollsnapshots. Graph,
Indizes, Felder, Metadaten, Fehlerkorrektur und Historie kommen hinzu.

12. Skalierung der Synapsen

Bei durchschnittlich (k) ausgehenden Synapsen pro Neuron gilt

[ M=N k. ]

Bei (N=312,500,000) und (k=100):

[ M=31,250,000,000. ]

Bei einem mittleren kompakten Synapsenrecord von beispielsweise (48)
Byte:

[ S_E=M\cdot48{=tex} ]

und damit

[ S_E= 1,500,000,000,000;\text{Byte}{=tex}
\approx1{,}{=tex}5;\text{TB}{=tex}. ]

Damit wird deutlich:

[ \boxed{S_{\mathrm{Synapsen}}\gg S_{\mathrm{Neuronen}}}{=tex} ]

sobald die mittlere Knotendichte steigt.

Deshalb sind Sparse-Graph-Strukturen, Property-Packing und
Delta-Speicherung wesentlich wichtiger als eine weitere Kompression der
Neuronenkoordinaten.

13. Informationskapazität eines theoretischen optischen Punktes

Sind (m) tatsächlich unabhängig unterscheidbare Kanäle vorhanden und
besitzt Kanal (i) (Q_i) zuverlässig unterscheidbare Zustände, ist die
ideale kombinatorische Obergrenze

[ C_{\mathrm{ideal}{=tex}} = \log{=tex}2 \left{=tex}(
\prod{=tex}{i=1}^{m}Q_i \right{=tex}) =
\sum{=tex}_{i=1}^{m}\log{=tex}_2(Q_i) ]

Bit pro Punkt.

Diese Formel darf nur angewendet werden, wenn die Kanäle ausreichend
unabhängig sind.

In einem realen Kommunikations-/Messkanal begrenzen Rauschen und
Bandbreite die Kapazität. Für einen idealisierten gaußschen Kanal
beschreibt Shannon:

[ C=B\log{=tex}_2(1+\mathrm{SNR}{=tex}) ]

mit Bandbreite (B) und Signal-Rausch-Verhältnis (\mathrm{SNR}{=tex}).

Für den Brain-5D-Speicher bedeutet dies: Die bloße mathematische Zahl
möglicher Kombinationen ist nicht automatisch die praktisch
speicherbare Informationsmenge. Auslesbarkeit, Kanalübersprechen und
Fehlerwahrscheinlichkeit sind entscheidend.

14. Fehler und Robustheit

Ein reales optisches System benötigt mindestens:

Kalibrierung,

Synchronisation,

Referenzsignale für Phase,

Korrektur von Drift,

Erkennung von Kanalübersprechen,

Prüfsummen,

Fehlerkorrekturcodes,

Redundanz für kritische Metadaten.

Für einen digitalen Block (D) kann beispielsweise eine Prüfsumme

[ h=H(D) ]

gespeichert werden. Sie erkennt Änderungen, ersetzt aber keinen
Fehlerkorrekturcode.

Für eine spätere Hardware sind Verfahren wie Reed-Solomon-, BCH- oder
LDPC-artige Fehlerkorrektur denkbar; die konkrete Wahl hängt vom
gemessenen Fehlermodell des Mediums ab.

15. Selbstorganisation

Der Speicher selbst soll zunächst keine unkontrollierte Eigenlogik
besitzen. Selbstorganisation wird als getrennte Schicht über
Manipulationsoperationen ausgeführt.

15.1 Hebb-artige Plastizität

Eine einfache abstrakte Regel lautet

[ \Delta {=tex}w_{ij} = \eta {=tex}a_i a_j, ]

wobei:

(w_{ij}): Synapsengewicht,

(\eta{=tex}): Lernrate,

(a_i,a_j): Aktivitätsgrößen.

Die tatsächliche Brain-5D-Lernlogik kann davon abweichen; die Formel
beschreibt nur das Grundprinzip korrelationsbasierter Verstärkung.

15.2 Pruning

Eine Synapse kann entfernt werden, wenn beispielsweise

[ |w_{ij}|<w_{\min{=tex}} ]

über eine definierte Mindestdauer gilt.

Eine robustere Regel verwendet zusätzlich Aktivität und Alter:

[ P_{\mathrm{prune}{=tex}} =
f(|w_{ij}|,a_{ij},\Delta {=tex}t). ]

15.3 Sprouting

Neue Verbindungen können zwischen geeigneten Kandidaten erzeugt werden,
wenn

[ similarity(i,j)>\theta{=tex}_s ]

und zusätzliche Strukturbedingungen erfüllt sind.

15.4 Neurogenese

Ein neues Neuron kann in einer lokalen Umgebung erzeugt werden, wenn
beispielsweise Überlastung, Wachstumsreiz und freie Kapazität
zusammentreffen.

Formal:

[ g_i>\theta{=tex}g \land{=tex}
\rho{=tex}{\mathrm{local}{=tex}}<\rho{=tex}_{\max{=tex}}
\Rightarrow{=tex} \text{create neuron}{=tex}. ]

Diese Regeln sind Entwurfsregeln, keine Behauptung, dass biologische
Neurogenese exakt so funktioniert.

16. Manipulator als Instrument

Zwischen Speicher und Selbstorganisation liegt der Manipulator:

[ \text{Storage}{=tex} \leftrightarrow{=tex}
\text{Manipulator}{=tex} \leftrightarrow{=tex}
\text{Learning/Self-Organization}{=tex}. ]

Er stellt atomare Operationen bereit:

Neuron lesen,

Neuron ändern,

Neuron erzeugen/löschen,

Synapse lesen,

Synapse erzeugen/ändern/löschen,

Felder lesen/ändern,

räumliche Nachbarn suchen,

Snapshots erstellen,

Änderungen protokollieren,

Transaktionen zurückrollen.

Selbstorganisation soll dieselben kontrollierten Operationen benutzen
wie manuelle Eingriffe. Dadurch bleibt jede strukturelle Veränderung
grundsätzlich protokollierbar.

17. Plausibilität des Gesamtkonzepts

Plausibel und unmittelbar digital umsetzbar

Folgende Elemente sind etablierte Informatik-/Mathematikkonzepte:

multidimensionale Arrays,

quantisierte Mehrkanaldaten,

Sparse Graphs,

CSR-Adjazenzstrukturen,

Snapshot-/Delta-Speicherung,

Memory Mapping,

Chunking,

Prüfsummen,

Transaktionen,

Graphalgorithmen,

neuronale Plastizitätsregeln als Simulation.

Der digitale Zwilling ist deshalb technisch plausibel und kann
unabhängig von optischer Hardware entwickelt werden.

Physikalisch grundsätzlich motiviert

Auch folgende Größen sind reale Eigenschaften elektromagnetischer
Strahlung bzw. optischer Systeme:

Wellenlänge/Spektrum,

Intensität,

Phase,

Polarisation,

räumliche Richtung,

Kohärenz.

Die Verwendung mehrerer optischer Freiheitsgrade zur
Informationskodierung ist daher physikalisch grundsätzlich plausibel.

Noch experimentell/offen

Nicht als bereits bewiesen gelten dürfen:

dass alle vorgesehenen Kanäle in einem einzelnen realen
Speichervolumen unabhängig mit der gewünschten Dichte geschrieben
werden können,

dass sie mit ausreichender Geschwindigkeit und Fehlerrate
gleichzeitig ausgelesen werden können,

dass ein 128-Byte-Digitalrecord physikalisch 1:1 einem einzelnen
realen optischen Punkt entsprechen kann,

dass die theoretisch berechnete geometrische Punktdichte praktisch
erreichbar ist,

dass ein späterer optischer Speicher gegenüber elektronischem
Massenspeicher wirtschaftlich oder energetisch überlegen wäre.

Diese Punkte benötigen einen Hardware-Prototyp und Messdaten.

18. Warum der digitale Zwilling trotzdem sinnvoll ist

Die zentrale Architekturentscheidung lautet:

[
\boxed{\text{Semantik des Speichers von der Hardware trennen}}{=tex}
]

Brain-5D entwickelt zuerst ein stabiles logisches Modell.

Der digitale Zwilling dient dabei als:

Referenzimplementierung,

Testsystem,

Datenformat,

Simulationsumgebung,

Visualisierungsquelle,

Benchmark für eine spätere optische Hardware.

Eine spätere Hardware muss nicht exakt dieselben physischen Kanäle
besitzen. Sie benötigt lediglich einen Adapter

[ A: \text{Brain5D-State}{=tex} \rightarrow{=tex}
\text{Physical Optical State}{=tex} ]

und einen inversen Leseweg

[ A^{-1}: \text{Measured Optical State}{=tex} \rightarrow{=tex}
\text{Brain5D-State}{=tex}. ]

Dadurch kann die Softwarearchitektur bestehen bleiben, selbst wenn sich
das physische Speicherkonzept ändert.

19. Empfohlene logische Architektur

Brain-5D
|
+-- Simulation / Learning
|
+-- Self-Organization Engine
|
+-- Manipulator API
|
+-- Storage Abstraction
|   |
|   +-- Neuron/Voxel Store
|   +-- Synapse/Graph Store
|   +-- Field Store
|   +-- Timeline/Delta Store
|   +-- Index
|
+-- Backends
    |
    +-- .b5d Digital Storage
    +-- RAM / mmap
    +-- Analyse-/Exportformate
    +-- zukünftiger Optical Adapter

Das .b5d-Format ist somit nicht einfach eine Bilddatei. Es ist ein
multidimensionaler neuronaler Container, dessen Punktdaten bewusst
so gestaltet werden, dass sie als digitaler Zwilling eines theoretischen
optischen Speichers interpretiert werden können.

20. Zusammenfassung

Das Brain-5D-Speichermodell basiert auf vier Informationsklassen:

[ \boxed{
\text{Punkt}+\text{Graph}+\text{Feld}+\text{Zeit}
}{=tex} ]

Der Punkt speichert den lokalen neuronalen und optischen Zustand.

Der Graph speichert gerichtete Beziehungen und
Synapseneigenschaften.

Das Feld speichert räumlich geteilte elektrische, chemische und
modulatorische Zustände.

Die Zeit-/Delta-Schicht speichert Veränderungen, ohne jeden Tick als
vollständige Kopie des Systems abzulegen.

Das theoretische optische Original nutzt als Modell räumliche Position,
Spektrum, Intensität, Phase, Polarisation, Richtung, Kohärenz und
gegebenenfalls weitere experimentell validierbare Freiheitsgrade.

Der digitale Zwilling bildet diese Größen deterministisch auf Binärdaten
ab und erweitert sie um neuronale, elektrische, chemische und
graphbasierte Zustände.

Damit ist Brain-5D nicht von der erfolgreichen Entwicklung einer
optischen Hardware abhängig. Das digitale System ist eigenständig
nutzbar, während das optische Modell als theoretische
Hardwareperspektive und Forschungsrichtung erhalten bleibt.

21. Leitprinzip

Information wird dort gespeichert, wo sie semantisch hingehört:
Zustand im Punkt, Beziehung im Graphen, Umgebung im Feld und
Veränderung in der Zeit.

Dieses Prinzip soll unnötige Redundanz vermeiden und gleichzeitig
gewährleisten, dass der digitale Brain-5D-Speicher später auf andere
physische Speichertechnologien abgebildet werden kann.