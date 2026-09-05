# EXP-GEN-0014: Zusammenfassung

Diese Zusammenfassung wurde nachträglich korrigiert. Sie trennt den technischen Lauf, die tatsächlich gemessenen Ergebnisse und die wissenschaftliche Aussagekraft voneinander.

## Versuchsübersicht

- Status: `completed`
- Durchläufe: `6`
- Seeds: `42, 43, 44`
- Ticks: `100`
- Laufmodus: `EXPLORATORY`
- Netzwerkmodus: `OFFLINE`
- registrierte Forschungsfrage: `RQ-TEMP-001`
- registrierte Hypothese: `H-TEMP-001-A`

## Wichtiger Konsistenzhinweis

Die registrierte Forschungsfrage betrifft FAST-, MEDIUM- und SLOW-Referenzzustände. Tatsächlich ausgeführt wurde jedoch ein Impulsantwort-Experiment mit den Bedingungen `recurrence_off` und `recurrence_on`.

Damit beantwortet EXP-GEN-0014 **nicht** die registrierte Temporal-State-Frage. Das Experiment ist als explorativer Rekurrenz-/Impulsantwort-Test interpretierbar, darf aber nicht als Evidenz für `RQ-TEMP-001` oder `H-TEMP-001-A` freigegeben werden.

## Tatsächlich beobachtete Ergebnisse

### Rekurrenz aus

- 1 beobachteter Spike
- Spike bei Tick 2
- erste Antwort: Tick 2
- letzte Antwort: Tick 2
- `propagation_depth = 1`
- `activated_neurons = 1`
- `peak_spike_rate = 1.0`

### Rekurrenz an

- 8 beobachtete Spikes
- Spike-Ticks: `2, 4, 8, 12, 16, 20, 24, 30`
- erste Antwort: Tick 2
- letzte Antwort: Tick 30
- `propagation_depth = 29`
- `activated_neurons = 1`
- `peak_spike_rate = 1.0`

### Deskriptive Unterschiede

Spike-Verhältnis:

\[
RR_{spike}=\frac{8}{1}=8
\]

Die Rekurrenz-Bedingung erzeugte in dieser Konfiguration achtmal so viele beobachtete Spikes.

Verlängerung bis zum letzten Spike:

\[
\Delta t_{last}=30-2=28\;\text{Ticks}
\]

Unterschied der gemeldeten Propagation Depth:

\[
\Delta D=29-1=28
\]

Die Zahl aktivierter Neuronen blieb unverändert:

\[
\Delta A=1-1=0
\]

Damit besteht der beobachtete Unterschied nicht in einer Rekrutierung weiterer Neuronen, sondern in wiederholter Aktivität desselben beobachteten Neurons über einen längeren Zeitraum.

## Spike-Timing

Für `recurrence_on` ergeben sich die Inter-Spike-Intervalle:

\[
ISI=(2,4,4,4,4,4,6)
\]

Der Mittelwert beträgt:

\[
\overline{ISI}=4.0\;\text{Ticks}
\]

Dies beschreibt ein relativ regelmäßiges wiederholtes Antwortmuster. Daraus darf noch kein biologischer Rhythmus, Attraktor, Gedächtnismechanismus oder Oszillator abgeleitet werden.

## Reproduzierbarkeit

Die Spike-Sequenzen und ihre Digests sind für Seeds 42, 43 und 44 innerhalb der jeweiligen Bedingung identisch. Das zeigt eine reproduzierbare deterministische Ausgabe.

Es ist jedoch nicht automatisch eine statistisch unabhängige Stichprobe `n=3`. Falls der untersuchte Pfad seed-unabhängig oder vollständig deterministisch ist, handelt es sich um wiederholte Ausführungen und nicht um drei unabhängige experimentelle Einheiten.

## Kritische Messgrößen

`recurrent_events` ist in allen Läufen `0`, auch bei `recurrence_on`. Diese Metrik ist daher derzeit nicht interpretierbar, solange ihre operationale und mathematische Definition nicht dokumentiert und getestet ist.

Auch `propagation_depth` darf ohne Implementationsdefinition nicht als biologische Verarbeitungstiefe, kognitive Komplexität oder kausale Pfadlänge interpretiert werden.

State-Digests sind kryptographische Identifikatoren. Unterschiedliche Hashes zeigen, dass Zustände nicht identisch sind; sie definieren keine metrische Entfernung zwischen Zuständen.

## Wissenschaftlicher Status

- Technischer Lauf: **erfolgreich**
- Runtime-Fehler: **keine gemeldet**
- Semantische Übereinstimmung RQ/H ↔ Protokoll: **nicht gegeben**
- Deskriptiver Rekurrenzbefund: **vorläufig nutzbar**
- statistische Signifikanz: **nicht nachgewiesen**
- wissenschaftliche Evidenz: `false`
- Human Review: `PENDING`

## Artefakte

Die lokalen `127.0.0.1/#`-Links wurden bewusst nicht verwendet. Die folgenden Links zeigen direkt auf die Dateien im Repository:

- [DATA/runs.json](https://github.com/Thomas-Heisig/Brain-5D/blob/main/research/experiments/EXP-GEN-0014/DATA/runs.json)
- [manifest.json](https://github.com/Thomas-Heisig/Brain-5D/blob/main/research/experiments/EXP-GEN-0014/manifest.json)
- [workflow.json](https://github.com/Thomas-Heisig/Brain-5D/blob/main/research/experiments/EXP-GEN-0014/workflow.json)
- [report.md](https://github.com/Thomas-Heisig/Brain-5D/blob/main/research/experiments/EXP-GEN-0014/report.md)
- [AIRR-2026-0001.md](https://github.com/Thomas-Heisig/Brain-5D/blob/main/research/experiments/EXP-GEN-0014/reports/AIRR-2026-0001.md)
- [AIRR-2026-0001.json](https://github.com/Thomas-Heisig/Brain-5D/blob/main/research/experiments/EXP-GEN-0014/reports/AIRR-2026-0001.json)
- [SCIENTIFIC-REVIEW.md](https://github.com/Thomas-Heisig/Brain-5D/blob/main/research/experiments/EXP-GEN-0014/reports/SCIENTIFIC-REVIEW.md)

## Empfohlene Folgearbeiten

1. `RQ-TEMP-001` ausschließlich mit einem Temporal-State-Protokoll ausführen, das FAST/MEDIUM/SLOW tatsächlich misst.
2. Für Rekurrenz eine eigene Forschungsfrage und Hypothese registrieren.
3. Rekurrenzstärke systematisch variieren.
4. Impulsstärke systematisch variieren.
5. `recurrent_events` und `propagation_depth` mathematisch und im Code definieren und separat testen.
6. Längere Laufzeiten und größere rekurrente Motive untersuchen.
7. Eine geeignete unabhängige experimentelle Einheit definieren, bevor p-Werte, Konfidenzintervalle oder Aussagen wie „statistisch robust“ verwendet werden.

## Wissenschaftliche Grenze

Die KI-Auswertung ist post-hoc, steuert den Lauf nicht und ersetzt keine menschliche wissenschaftliche Prüfung oder Evidenzfreigabe. Insbesondere dürfen die ursprünglichen Aussagen „statistisch robust“, „signifikant“ oder eine allgemeine Kausalitätsbehauptung aus diesem Datensatz allein nicht übernommen werden.
