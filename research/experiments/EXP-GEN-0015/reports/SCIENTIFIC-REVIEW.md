# EXP-GEN-0015 – Korrigierte wissenschaftliche Auswertung

## Status

EXP-GEN-0015 wurde technisch erfolgreich abgeschlossen. Der Lauf umfasst sechs Runs: je drei Seeds (`42`, `43`, `44`) für `recurrence_off` und `recurrence_on`. Die Rohdaten sind vorhanden und enthalten keine Runtime-Fehler.

Der automatisch erzeugte AIRR ist jedoch nicht vollständig entstanden, weil die AI-Analyse-Pipeline beim Feld `confidence` abgebrochen ist. Dieser Fehler betrifft die Berichtserzeugung, nicht die experimentellen Rohdaten.

Zusätzlich besteht ein semantischer Zuordnungsfehler: Das Manifest verknüpft den Lauf mit `RQ-TEMP-001` / `H-TEMP-001-A`, tatsächlich wurde aber der Network-Impulse-Response-Versuch mit den Bedingungen `recurrence_off` und `recurrence_on` ausgeführt. Die Daten dürfen deshalb **nicht** als Evidenz für die FAST/MEDIUM/SLOW-Hypothese gewertet werden.

## Tatsächlich ausgeführtes Design

- Protokoll: `science_suite_v1`
- Titel: `Network impulse response`
- Seeds: `42, 43, 44`
- Ticks: `1000`
- Bedingungen: `recurrence_off`, `recurrence_on`
- Rekurrenz ist die kontrollierte Behandlung.

Die Versuchsanordnung entspricht damit einer Rekurrenz-/Impulsantwort-Untersuchung und nicht einem Temporal-State-Vergleich.

## Quantitative Ergebnisse

Die drei Seeds liefern innerhalb jeder Bedingung dieselbe Spike-Sequenz-Signatur. Das zeigt deterministische Reproduzierbarkeit des gemessenen Versuchsablaufs, ist aber nicht automatisch als drei statistisch unabhängige Beobachtungen zu interpretieren.

### Rekurrenz deaktiviert

Für alle drei Seeds:

- `total_spikes = 3`
- `delivered_synaptic_events = 2`
- `activated_neurons = 3`
- `propagation_depth = 1`
- `recurrent_events = 0`
- `last_response_latency = 2`
- `synaptic_activity_ticks = 2`
- `total_synapses = 2`
- `return_latency = null`

Spike-Sequenz:

```text
(Neuron 0, Tick 0)
(Neuron 1, Tick 1)
(Neuron 2, Tick 2)
```

### Rekurrenz aktiviert

Für alle drei Seeds:

- `total_spikes = 33`
- `delivered_synaptic_events = 33`
- `activated_neurons = 3`
- `propagation_depth = 61`
- `recurrent_events = 10`
- `last_response_latency = 62`
- `synaptic_activity_ticks = 33`
- `total_synapses = 3`
- `return_latency = 3`

Die Aktivität läuft damit deutlich länger weiter, ohne zusätzliche Neuronen zu rekrutieren.

## Abgeleitete Kennzahlen

### Spike-Zunahme

\[
RR_{spike} = \frac{33}{3} = 11
\]

Die beobachtete Spike-Anzahl ist in der Rekurrenz-Bedingung um den Faktor `11` höher.

Absolute Differenz:

\[
\Delta N_{spike} = 33 - 3 = 30
\]

### Synaptische Ereignisse

\[
RR_{syn} = \frac{33}{2} = 16{,}5
\]

\[
\Delta E_{syn} = 33 - 2 = 31
\]

### Antwortdauer

\[
\Delta L_{last} = 62 - 2 = 60\;Ticks
\]

### Propagation Depth

\[
\Delta D = 61 - 1 = 60
\]

Die Größe ist stark erhöht. Sie darf jedoch nur entsprechend ihrer Implementierungsdefinition interpretiert werden. Ohne explizite mathematische Definition ist `propagation_depth` kein allgemeines Maß für Informationskomplexität.

### Aktivierte Neuronen

\[
\Delta A = 3 - 3 = 0
\]

Die Rekurrenz aktiviert also keine zusätzlichen Neuronen. Sie hält vielmehr die Dynamik innerhalb derselben drei beobachteten Neuronen aufrecht.

### Recurrent Events

\[
\Delta R = 10 - 0 = 10
\]

Damit ist im aktuellen Messsystem erstmals eine direkte Rekurrenzmetrik > 0 vorhanden. Für eine wissenschaftliche Interpretation muss die exakte Zählregel von `recurrent_events` dokumentiert werden.

## Spike-Timing

Die `recurrence_on`-Sequenz umfasst 33 Spikes von Tick 0 bis Tick 62. Über alle aufeinanderfolgenden Spikes ergeben sich 32 Inter-Spike-Intervalle mit:

\[
\overline{ISI} = 1{,}9375\;Ticks
\]

Median:

\[
\widetilde{ISI} = 2\;Ticks
\]

Stichproben-Standardabweichung:

\[
s_{ISI} \approx 0{,}5644\;Ticks
\]

Pro Neuron beträgt das mittlere Wiederholungsintervall ungefähr:

- Neuron 0: `5.8` Ticks
- Neuron 1: `5.9` Ticks
- Neuron 2: `6.0` Ticks

Die Sequenz zeigt damit eine zunächst schnelle Zirkulation und anschließend eine weitgehend regelmäßige rekurrente Aktivität mit zunehmenden Abständen am Ende. Das ist ein beobachtbares dynamisches Muster, aber noch kein Beleg für Gedächtnis, Informationsverarbeitung oder biologische Rhythmik.

## Reproduzierbarkeit

Die drei Seeds liefern innerhalb einer Bedingung dieselben Spike-Sequenz-Digests und dieselben zentralen Messwerte. Dies belegt, dass der aktuelle Versuch unter diesen Bedingungen deterministisch reproduzierbar ist.

Wissenschaftlich wichtig ist aber die Unterscheidung zwischen:

1. technischer Reproduzierbarkeit und
2. statistisch unabhängigen Replikaten.

Wenn der Seed die beobachtete Dynamik nicht beeinflusst, darf `n=3` nicht ohne Weiteres als unabhängige Stichprobe verwendet werden.

## Was aus den Daten geschlossen werden darf

Die Rohdaten unterstützen folgende deskriptive Aussage:

> Unter der getesteten Network-Impulse-Response-Konfiguration führt die aktivierte Rekurrenz zu einer deutlich verlängerten und wiederholten Spike- und Synapsenaktivität innerhalb derselben drei Neuronen. Die Sequenz ist über die Seeds 42, 43 und 44 deterministisch reproduzierbar.

Nicht ausreichend belegt sind derzeit Aussagen über:

- höhere „Netzwerkkomplexität“,
- Informationsverarbeitung im semantischen Sinn,
- Gedächtnis,
- Lernen,
- biologische Plausibilität,
- allgemeine Kausalität über andere Topologien oder Gewichte,
- die Hypothese `H-TEMP-001-A`.

## Kritischer Fehler in der Forschungszuordnung

`RQ-TEMP-001` fragt nach FAST-, MEDIUM- und SLOW-Referenzzuständen. Die Daten von EXP-GEN-0015 enthalten diese Bedingungen nicht. Stattdessen wurden `recurrence_off` und `recurrence_on` ausgeführt.

Damit gilt:

```text
RQ/Hypothese: Temporal State
Ausführung:    Network Impulse Response / Recurrence
Ergebnis:      RQ_PROTOCOL_MISMATCH
```

Aus diesem Experiment darf daher keine Evidenzpromotion für `RQ-TEMP-001` oder `H-TEMP-001-A` erfolgen.

## Fehler der KI-Auswertung

Der gespeicherte Analyst behauptet, dass die Rekurrenzdaten `H-TEMP-001-A` stützen. Diese Schlussfolgerung ist logisch nicht zulässig, weil die registrierte Hypothese eine andere unabhängige Variable beschreibt.

Auch Formulierungen wie „signifikant höhere Werte“ sind ohne inferenzstatistischen Test nicht zulässig. Die Daten zeigen große **deskriptive** Unterschiede. Signifikanz wurde nicht berechnet.

Der AIRR-Abbruch `Invalid AI analysis output field: confidence` entstand in einer nachgelagerten AI-Rolle. Die Pipeline wurde inzwischen so gehärtet, dass numerische Strings und Prozentwerte normalisiert werden und ein nicht interpretierbarer Confidence-Wert konservativ auf `0.0` gesetzt wird, ohne die gesamte Berichtskette zu verwerfen.

## Empfohlene Folgeexperimente

1. Rekurrenzgewicht systematisch variieren statt nur `on/off`.
2. Mehrere Topologien und unabhängige Initialisierungen testen.
3. `recurrent_events` und `propagation_depth` formal definieren und in der Methodendokumentation festhalten.
4. Rekurrenzschleifen gezielt ablieren, um die beobachtete Persistenz mechanistisch zuzuordnen.
5. Für `RQ-TEMP-001` einen separaten Temporal-State-Lauf mit `fast`, `medium`, `slow` durchführen.
6. Bei Temporal-State-Experimenten deutlich mehr als acht Ticks und mehrere definierte Zustandsmetriken verwenden.
7. Effektgrößen und inferenzstatistische Verfahren nur dann anwenden, wenn tatsächlich unabhängige Replikate vorliegen.

## Wissenschaftlicher Status

- Technische Ausführung: **erfolgreich**
- Rohdaten vorhanden: **ja**
- Rekurrenzwirkung deskriptiv beobachtbar: **ja**
- Deterministische Wiederholung über Seeds: **ja**
- AIRR vollständig: **nein**
- RQ/Hypothesen-Zuordnung korrekt: **nein**
- Evidenz für `H-TEMP-001-A`: **nein**
- Human Review: **PENDING**
