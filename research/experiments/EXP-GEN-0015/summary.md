# EXP-GEN-0015: Zusammenfassung

Diese Zusammenfassung wurde nach Abschluss des Laufs aus Manifest, Workflow und Rohdaten korrigiert und erweitert. Der technische Lauf ist abgeschlossen, die automatische AIRR-Kette ist jedoch nach dem Analysten an einem fehlerhaft formatierten `confidence`-Feld abgebrochen. Die Rohdaten bleiben davon unberührt.

## Versuchsübersicht

- Status: `completed`
- Registrierte Forschungsfrage: `RQ-TEMP-001`
- Registrierte Hypothese: `H-TEMP-001-A`
- Durchläufe: `6`
- Seeds: `42, 43, 44`
- Ticks: `1000`
- Laufmodus: `EXPLORATORY`
- Netzwerkmodus: `OFFLINE`
- Ausgeführte Bedingungen: `recurrence_off`, `recurrence_on`

## Wichtiger wissenschaftlicher Hinweis

Die registrierte Forschungsfrage untersucht FAST-, MEDIUM- und SLOW-Temporalzustände. EXP-GEN-0015 hat dagegen einen Rekurrenz-/Impulsantwort-Versuch ausgeführt. Damit liegt ein **RQ/Protokoll-Mismatch** vor.

**Folge:** Die Daten sind technisch verwertbar, dürfen aber nicht als Evidenz für `H-TEMP-001-A` gewertet werden.

## Quantitative Kernergebnisse

Über alle drei Seeds sind die zentralen Metriken innerhalb einer Bedingung identisch.

### `recurrence_off`

- `total_spikes = 3`
- `delivered_synaptic_events = 2`
- `activated_neurons = 3`
- `propagation_depth = 1`
- `recurrent_events = 0`
- `last_response_latency = 2`
- `synaptic_activity_ticks = 2`
- `total_synapses = 2`

### `recurrence_on`

- `total_spikes = 33`
- `delivered_synaptic_events = 33`
- `activated_neurons = 3`
- `propagation_depth = 61`
- `recurrent_events = 10`
- `last_response_latency = 62`
- `synaptic_activity_ticks = 33`
- `total_synapses = 3`
- `return_latency = 3`

### Abgeleitete Werte

Spike-Verhältnis:

\[
RR_{spike}=\frac{33}{3}=11
\]

Synaptische Ereignisse:

\[
RR_{syn}=\frac{33}{2}=16{,}5
\]

Antwortverlängerung:

\[
\Delta L=62-2=60\;Ticks
\]

Propagation-Depth-Differenz:

\[
\Delta D=61-1=60
\]

Aktivierte Neuronen:

\[
\Delta A=3-3=0
\]

Die Rekurrenz rekrutiert also keine zusätzlichen Neuronen, sondern hält die Dynamik innerhalb derselben drei Neuronen deutlich länger aufrecht.

Für die 33 Spikes der `recurrence_on`-Bedingung beträgt das mittlere Inter-Spike-Intervall über die gesamte Sequenz:

\[
\overline{ISI}=1{,}9375\;Ticks
\]

Median:

\[
\widetilde{ISI}=2\;Ticks
\]

## Reproduzierbarkeit

Die Spike-Sequenz-Digests und die zentralen Messwerte sind für Seeds `42`, `43` und `44` jeweils identisch. Das belegt technische deterministische Reproduzierbarkeit. Es belegt **nicht automatisch** drei statistisch unabhängige Replikate.

## AIRR-Status

- AIRR-Status: `failed`
- Fehler: `Invalid AI analysis output field: confidence`
- Bereits gespeicherter Analyst: vorhanden
- Reviewer/Writer: wegen Schemafehler nicht vollständig erzeugt
- Wissenschaftliche Evidenz: `false`
- Human Review: `PENDING`

Die Reporting-Pipeline wurde nach diesem Lauf so gehärtet, dass numerische Strings und Prozentwerte normalisiert werden. Nicht interpretierbare Confidence-Werte führen künftig nicht mehr zum Verlust der gesamten Berichtskette, sondern werden konservativ auf `0.0` gesetzt und als methodische Einschränkung protokolliert.

## Korrigierte wissenschaftliche Aussage

> Unter der ausgeführten Network-Impulse-Response-Konfiguration führt aktivierte Rekurrenz zu einer deutlich verlängerten und wiederholten Spike- und Synapsenaktivität innerhalb derselben drei Neuronen. Der beobachtete Ablauf ist über die Seeds 42, 43 und 44 deterministisch reproduzierbar. Dieser Befund testet jedoch nicht die registrierte FAST/MEDIUM/SLOW-Hypothese.

## Artefakte

- [Rohdaten – DATA/runs.json](https://github.com/Thomas-Heisig/Brain-5D/blob/main/research/experiments/EXP-GEN-0015/DATA/runs.json)
- [Manifest](https://github.com/Thomas-Heisig/Brain-5D/blob/main/research/experiments/EXP-GEN-0015/manifest.json)
- [Workflow](https://github.com/Thomas-Heisig/Brain-5D/blob/main/research/experiments/EXP-GEN-0015/workflow.json)
- [Technischer Bericht](https://github.com/Thomas-Heisig/Brain-5D/blob/main/research/experiments/EXP-GEN-0015/report.md)
- [Gespeicherte Analysten-Auswertung](https://github.com/Thomas-Heisig/Brain-5D/blob/main/research/experiments/EXP-GEN-0015/analysis/AIAR-scientific_analyst-20260905173845441625-add0797e.json)
- [Korrigierte ausführliche wissenschaftliche Auswertung](https://github.com/Thomas-Heisig/Brain-5D/blob/main/research/experiments/EXP-GEN-0015/reports/SCIENTIFIC-REVIEW.md)

## Wissenschaftliche Grenze

Die KI-Auswertung ist post-hoc, steuert den Lauf nicht und ersetzt keine menschliche wissenschaftliche Prüfung oder Evidenzfreigabe. Aussagen über Signifikanz, Komplexität, Gedächtnis, Lernen oder Informationsverarbeitung dürfen aus diesem Lauf nur dann abgeleitet werden, wenn dafür explizite Definitionen, Kontrollbedingungen und geeignete statistische Verfahren vorliegen.
