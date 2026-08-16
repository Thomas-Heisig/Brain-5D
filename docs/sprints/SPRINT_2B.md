# Sprint 2B - STDP Integration and Eligibility Traces

## Ziel

Sprint 2B verbindet die in Sprint 2A validierte STDP-Mathematik mit dem realen
5D-Netzwerk, ohne Lernlogik in den Core zu verlagern.

## Architektur

Der Core kennt keine `LearningEngine`. `NeuralNetwork` stellt nur einen
generischen Post-Step-Hook bereit:

```python
network.add_post_step_hook(callback)
```

Die `LearningEngine` registriert `update()` an diesem Hook. Der Hook wird erst
nach der Spike-Erzeugung und Event-Queueing-Phase ausgefuehrt. Damit gilt:

1. Ein Spike bei Tick `t` plant Events mit dem Gewicht, das zu Beginn dieses
   Spike-Ereignisses aktiv war.
2. STDP darf danach das Gewicht veraendern.
3. Bereits geplante Events werden nicht rueckwirkend veraendert.
4. `core_step_ms` misst weiterhin nur den Core und schliesst die Lernzeit aus.

## Warum kein `last_post_spike` in `core.Synapse`?

`Neuron` besitzt bereits `last_spike_tick`, und postsynaptische Zeitstempel sind
keine strukturelle Eigenschaft einer Core-Synapse. Sprint 2B fuehrt deshalb
seinen eigenen Zustand pro Synapsenobjekt in `_SynapseLearningState`.

Das verhindert doppelte Zustandsfuehrung und haelt den Core lernneutral.

## STDP

Die Engine verwendet nearest-neighbour pair STDP:

- PRE nach einem frueheren POST: LTD
- POST nach einem frueheren PRE: LTP
- PRE und POST im gleichen Tick werden nicht miteinander gepaart
- Gewichte werden auf `min_weight .. max_weight` begrenzt

Die Zeitstempel des aktuellen Ticks werden erst nach der Berechnung beider
Seiten gespeichert. Dadurch haengt das Ergebnis nicht von der Iterationsreihenfolge
innerhalb eines Ticks ab.

## Eligibility Trace

`EligibilityTrace` verwendet exponentiellen Zerfall:

`e(t + dt) = e(t) * exp(-dt / tau_e)`

Der Zerfall wird lazy berechnet. Es ist deshalb nicht notwendig, in jedem Tick
alle Synapsen des Netzes zu durchlaufen.

In Sprint 2B kann der Trace lokale STDP-Korrelationsereignisse aufnehmen, wird
aber noch nicht mit einem Reward-Signal multipliziert. Das 3-Faktor-Lernen ist
ein spaeterer Sprint.

## Performance

Die LearningEngine baut einen Incoming-Index auf. Pro Tick werden nur Synapsen
betrachtet, die an aktuell feuernden Neuronen haengen. Ein vollstaendiger
O(E)-Scan des Netzes pro Tick wird vermieden.

Bei einer nachtraeglichen Topologieaenderung mit veraenderter Synapsenzahl wird
der Index automatisch aktualisiert. Wenn spaeter Synapsen entfernt und im
selben Schritt in gleicher Anzahl ersetzt werden, muss `refresh_topology()`
explizit aufgerufen werden.

## Konfiguration

```yaml
stdp:
  enabled: false
  a_plus: 0.1
  a_minus: 0.12
  tau_plus: 20.0
  tau_minus: 20.0
  max_weight: 1.0
  min_weight: 0.0

eligibility:
  enabled: true
  tau_ticks: 200.0
```

Mit `stdp.enabled: false` werden keine Gewichte veraendert. Eligibility kann
unabhaengig davon aktiviert werden, um die Korrelationsspur zu validieren.

## Tests

```bash
python -m pytest tests/test_stdp_isolated.py -v
python -m pytest tests/test_eligibility.py -v
python -m pytest tests/test_stdp_integration.py -v
python -m pytest tests -v
```

Der finale Abnahmelauf muss im vollstaendigen Repository erfolgen.
