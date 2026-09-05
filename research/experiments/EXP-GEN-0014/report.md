# EXP-GEN-0014: Network impulse response

## Protokoll

`science_suite_v1`

- Ticks: 100
- Seeds: 42, 43, 44
- Bedingungen: `recurrence_off`, `recurrence_on`
- Runs: 6
- Laufdauer laut Manifest: 0.006461 s

## Konsistenzprüfung

Die registrierte Forschungsfrage `RQ-TEMP-001` und Hypothese `H-TEMP-001-A` betreffen FAST/MEDIUM/SLOW-Temporal-State-Vergleiche. Dieser Lauf führte dagegen einen Rekurrenz-On/Off-Impulsantworttest aus.

**Folge:** Der Lauf ist technisch auswertbar, aber nicht als Evidenz für die registrierte Temporal-State-Hypothese geeignet.

## Hauptergebnisse

Unter `recurrence_off` wurde pro Seed ein Spike bei Tick 2 beobachtet. Unter `recurrence_on` wurden acht Spikes bei Ticks 2, 4, 8, 12, 16, 20, 24 und 30 beobachtet.

Spike-Verhältnis:

\[
RR_{spike}=\frac{8}{1}=8
\]

Verlängerung der beobachteten Antwort:

\[
\Delta t_{last}=30-2=28\;\text{Ticks}
\]

Gemeldete Änderung der Propagation Depth:

\[
\Delta D=29-1=28
\]

Die Zahl aktivierter Neuronen blieb bei 1. Der beobachtete Unterschied besteht somit in wiederholter Aktivität desselben beobachteten Neurons, nicht in einer breiteren Neuronenrekrutierung.

Für `recurrence_on` lauten die Inter-Spike-Intervalle:

\[
ISI=(2,4,4,4,4,4,6),\qquad \overline{ISI}=4.0\;\text{Ticks}
\]

## Reproduzierbarkeit

Die Spike-Sequenz-Digests sind innerhalb jeder Bedingung für Seeds 42, 43 und 44 identisch. Dies zeigt deterministische Reproduzierbarkeit der gespeicherten Ausgabe, ist aber nicht automatisch eine statistisch unabhängige Stichprobe von `n=3`.

## Methodische Einschränkungen

- `recurrent_events = 0` auch bei aktivierter Rekurrenz; Definition/Instrumentation muss geklärt werden.
- `propagation_depth` benötigt eine explizite operationale Definition.
- State-Digests zeigen Identität/Nichtidentität, aber keine metrische Zustandsdistanz.
- Ohne inferenzstatistisches Modell dürfen die Ergebnisse nicht als „statistisch signifikant“ oder „statistisch robust“ bezeichnet werden.
- Der RQ/H-Protokoll-Mismatch blockiert eine Evidenzfreigabe für `RQ-TEMP-001`.

## Wissenschaftlicher Status

- Technische Ausführung: erfolgreich
- Runtime-Fehler: keine gemeldet
- Wissenschaftliche Evidenz: `false`
- Human Review: `PENDING`
- Gültige Aussage: explorativer, deskriptiver Rekurrenz-/Impulsantwortbefund

## Ausführlicher korrigierter Bericht

[SCIENTIFIC-REVIEW.md](https://github.com/Thomas-Heisig/Brain-5D/blob/main/research/experiments/EXP-GEN-0014/reports/SCIENTIFIC-REVIEW.md)

## Rohdaten und Provenienz

- [DATA/runs.json](https://github.com/Thomas-Heisig/Brain-5D/blob/main/research/experiments/EXP-GEN-0014/DATA/runs.json)
- [manifest.json](https://github.com/Thomas-Heisig/Brain-5D/blob/main/research/experiments/EXP-GEN-0014/manifest.json)
- [workflow.json](https://github.com/Thomas-Heisig/Brain-5D/blob/main/research/experiments/EXP-GEN-0014/workflow.json)

Die ursprünglichen AIAR/AIRR-Dateien bleiben als unveränderte Provenienz der damaligen KI-Auswertung erhalten; ihre zu starken Aussagen werden durch den korrigierten Review ausdrücklich nicht übernommen.
