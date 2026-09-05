# Experiment Report – EXP-GEN-0015

## 1. Identifikation

- Experiment: `EXP-GEN-0015`
- Status: `completed`
- Registrierte Forschungsfrage: `RQ-TEMP-001`
- Registrierte Hypothese: `H-TEMP-001-A`
- Protokoll: `science_suite_v1`
- Seeds: `42, 43, 44`
- Ticks: `1000`
- Netzwerkmodus: `OFFLINE`
- Laufmodus: `EXPLORATORY`

## 2. Tatsächlich ausgeführte Bedingungen

Der Lauf enthält sechs Runs:

- 3 × `recurrence_off`
- 3 × `recurrence_on`

Damit handelt es sich faktisch um einen Network-Impulse-Response-/Rekurrenzvergleich.

## 3. Semantische Validierung

**Status: `RQ_PROTOCOL_MISMATCH`**

`RQ-TEMP-001` und `H-TEMP-001-A` beziehen sich auf FAST-, MEDIUM- und SLOW-Zustandsreferenzen. Diese unabhängige Variable wurde in EXP-GEN-0015 nicht getestet. Die ausgeführten Bedingungen sind stattdessen `recurrence_off` und `recurrence_on`.

Daher gilt:

```text
Technischer Lauf:            gültig
Rohdaten:                    vorhanden
RQ/Hypothesen-Zuordnung:     ungültig
Evidenzpromotion RQ-TEMP-001 blockiert
Human Review:                erforderlich
```

## 4. Rohdatenergebnisse

### recurrence_off

Für Seeds 42, 43 und 44 identisch:

| Metrik | Wert |
|---|---:|
| total_spikes | 3 |
| delivered_synaptic_events | 2 |
| activated_neurons | 3 |
| propagation_depth | 1 |
| recurrent_events | 0 |
| first_response_latency | 2 |
| last_response_latency | 2 |
| synaptic_activity_ticks | 2 |
| total_synapses | 2 |
| peak_spike_rate | 1.0 |
| return_latency | null |

Spike-Sequenz:

```text
0: neuron 0
1: neuron 1
2: neuron 2
```

### recurrence_on

Für Seeds 42, 43 und 44 identisch:

| Metrik | Wert |
|---|---:|
| total_spikes | 33 |
| delivered_synaptic_events | 33 |
| activated_neurons | 3 |
| propagation_depth | 61 |
| recurrent_events | 10 |
| first_response_latency | 2 |
| last_response_latency | 62 |
| synaptic_activity_ticks | 33 |
| total_synapses | 3 |
| peak_spike_rate | 1.0 |
| return_latency | 3 |

## 5. Abgeleitete Kennzahlen

### Spike-Effekt

\[
RR_{spike}=\frac{33}{3}=11
\]

\[
\Delta N_{spike}=33-3=30
\]

### Synaptische Ereignisse

\[
RR_{syn}=\frac{33}{2}=16{,}5
\]

\[
\Delta E_{syn}=33-2=31
\]

### Antwortdauer

\[
\Delta L_{last}=62-2=60\;Ticks
\]

### Propagationsmetrik

\[
\Delta D=61-1=60
\]

### Zahl aktivierter Neuronen

\[
\Delta A=3-3=0
\]

Der Effekt besteht somit nicht in einer breiteren Rekrutierung zusätzlicher Neuronen, sondern in einer zeitlich fortgesetzten Aktivität derselben drei Neuronen.

### Rekurrente Ereignisse

\[
\Delta R=10-0=10
\]

Die Interpretation dieser Größe muss an die konkrete Implementierungsdefinition gekoppelt bleiben.

## 6. Spike-Timing

Die `recurrence_on`-Sequenz umfasst 33 Spikes von Tick 0 bis Tick 62.

Für die 32 aufeinanderfolgenden Intervalle gilt:

\[
\overline{ISI}=1{,}9375\;Ticks
\]

\[
\widetilde{ISI}=2\;Ticks
\]

\[
s_{ISI}\approx0{,}5644\;Ticks
\]

Mittlere Wiederholungsintervalle pro Neuron:

- Neuron 0: `5.8` Ticks
- Neuron 1: `5.9` Ticks
- Neuron 2: `6.0` Ticks

## 7. Reproduzierbarkeit

Die drei Seeds erzeugen innerhalb jeder Bedingung identische zentrale Metriken und identische Spike-Sequenz-Digests.

Das belegt technische deterministische Reproduzierbarkeit. Da die Messwerte keinerlei Streuung zwischen den Seeds zeigen, dürfen die drei Seeds jedoch nicht unkritisch als drei statistisch unabhängige Replikate behandelt werden.

## 8. Statistische Aussagegrenze

Für diesen Lauf wurde kein inferenzstatistischer Test registriert oder berechnet. Deshalb sind Formulierungen wie „statistisch signifikant“ oder „statistisch robust“ nicht zulässig.

Zulässig ist die deskriptive Aussage, dass die beiden Bedingungen in den gemessenen Größen stark voneinander abweichen.

## 9. AIRR-Fehler

Der Scientific Analyst wurde gespeichert. Eine nachfolgende AIRR-Rolle erzeugte jedoch ein nicht schema-konformes `confidence`-Feld. Dadurch brach die AIRR-Kette ab:

```text
Invalid AI analysis output field: confidence
```

Die Reporting-Pipeline wurde anschließend gehärtet:

- numerische Strings werden normalisiert,
- Prozentangaben werden in den Bereich 0..1 umgerechnet,
- nicht interpretierbare Confidence-Werte werden konservativ auf `0.0` gesetzt,
- der Originalwert wird als `confidence_original` erhalten,
- die Korrektur wird als methodische Einschränkung protokolliert,
- der restliche Bericht wird nicht mehr allein wegen dieses Formatfehlers verworfen.

## 10. Wissenschaftlich zulässige Schlussfolgerung

> Unter der ausgeführten Network-Impulse-Response-Konfiguration verursacht die aktivierte Rekurrenz eine deutlich längere und häufigere Spike- und Synapsenaktivität innerhalb derselben drei Neuronen. Der gemessene Ablauf ist über die Seeds 42, 43 und 44 deterministisch reproduzierbar. EXP-GEN-0015 testet jedoch nicht die registrierte FAST/MEDIUM/SLOW-Hypothese und darf nicht als Evidenz für `H-TEMP-001-A` verwendet werden.

## 11. Folgeexperimente

1. Korrektes Temporal-State-Experiment für `RQ-TEMP-001` mit `fast`, `medium`, `slow` ausführen.
2. Rekurrenzgewicht parametrisch variieren.
3. Rekurrenzpfade gezielt ablieren.
4. `recurrent_events` und `propagation_depth` mathematisch und algorithmisch dokumentieren.
5. Zusätzliche Topologien und echte unabhängige Initialisierungen verwenden.
6. Effektgrößen und inferenzstatistische Verfahren erst bei unabhängigen Replikaten einsetzen.
7. Lange Temporal-State-Läufe verwenden, wenn Aussagen über Persistenz oder Gedächtnis geprüft werden sollen.

## 12. Artefakte

- [Rohdaten](https://github.com/Thomas-Heisig/Brain-5D/blob/main/research/experiments/EXP-GEN-0015/DATA/runs.json)
- [Manifest](https://github.com/Thomas-Heisig/Brain-5D/blob/main/research/experiments/EXP-GEN-0015/manifest.json)
- [Workflow](https://github.com/Thomas-Heisig/Brain-5D/blob/main/research/experiments/EXP-GEN-0015/workflow.json)
- [Scientific Analyst](https://github.com/Thomas-Heisig/Brain-5D/blob/main/research/experiments/EXP-GEN-0015/analysis/AIAR-scientific_analyst-20260905173845441625-add0797e.json)
- [Ausführliche korrigierte wissenschaftliche Auswertung](https://github.com/Thomas-Heisig/Brain-5D/blob/main/research/experiments/EXP-GEN-0015/reports/SCIENTIFIC-REVIEW.md)
