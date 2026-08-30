# Architektur – Brain 5D Stand 1

## 1. Grundprinzip

Brain 5D verwendet keinen vollständig materialisierten 5D-Tensor. Existierende Neuronen werden über `dict[int, Neuron]` gespeichert. Die 5 Koordinaten `(x,y,z,d4,d5)` werden in einen Integer gepackt. Synapsen liegen als Adjazenzlisten am präsynaptischen Neuron.

## 2. Schichten

```text
Diagnostics / Stimulus
        |
        v
+-----------------------+
|  NeuralNetwork Core   |
|  Neuron + Synapse     |
|  Event Ring Buffer    |
+----------+------------+
           | StepResult
           v
+-----------------------+
| Telemetry / History   |
| SpikeHistory / Probes |
+-----+-----------+-----+
      |           |
      v           v
Propagation    Observatory
Analyzer       / Run Artifacts
```

Der Core importiert keine Visualisierung. Matplotlib ist ausschließlich in `src/visualization/` erlaubt.

## 3. Tick-Semantik

Für Tick `t` gilt strikt:

1. externe Ströme für `t` übernehmen;
2. Ringpuffer-Slot `t` auslesen;
3. nur Events mit `delivery_tick == t` akzeptieren;
4. externe und synaptische Ströme getrennt halten;
5. jedes Neuron exakt einmal integrieren;
6. Spikes für `t` erfassen;
7. Events für `t + delay` einplanen;
8. aggregierte Werte in `StepResult` schreiben;
9. `current_tick = t + 1`.

## 4. Event-Ringpuffer

Es existieren `max_delay + 1` Slots. Ein Event mit Verzögerung `d` wird in `(t+d) % slot_count` eingetragen. Der absolute `delivery_tick` ist Teil des Events und wird als harte Invariante geprüft.

## 5. Input/Output

Input- und Output-Hyperflächen werden nur über Konfiguration definiert. Der Spatial Index enthält keine semantische Kenntnis von Sensorik oder Aktorik.

## 6. Energie

Energie ist in Stand 1 ausschließlich Telemetrie. `energy=0` blockiert kein Feuern. Eine metabolische Wirkung ist ausdrücklich zukünftiger Umfang.

## 7. Propagationsbegriff

`secondary_recruited` bedeutet nur: ein nicht direkt stimuliertes Neuron hat im Beobachtungsfenster gefeuert. Dies ist in beliebigen Netzen noch kein kausaler Beweis einer konkreten Synapsenkette. Dafür ist später Event-Tracing vorgesehen.
