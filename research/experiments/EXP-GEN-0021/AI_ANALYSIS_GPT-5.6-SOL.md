# EXP-GEN-0021 — KI-generierte wissenschaftliche Analyse

> **KI-GENERIERT / NICHT EVIDENZBILDEND**  
> Autor: OpenAI GPT-5.6 Sol  
> Erstellungsdatum: 2026-09-05  
> Rolle: post-hoc wissenschaftliche Interpretation der vorhandenen Experimentartefakte  
> Autorität: `interpretation_only`  
> Evidenzstatus dieses Dokuments: **keine wissenschaftliche Evidenz**  
> Human Review: **erforderlich**

Dieses Dokument ist eine nachträgliche KI-Analyse von `EXP-GEN-0021`. Es verändert weder `DATA`, noch Manifest, Workflow, deterministische Statistik oder Evidenzstatus. Zahlen sind aus den vorhandenen Artefakten des Experiments abgeleitet; Schlussfolgerungen sind als Interpretation zu behandeln.

## 1. Gesamtbewertung

`EXP-GEN-0021` ist technisch ein erfolgreicher Omnibus-Lauf der Science Suite mit 57 Teilruns und den Seeds 42, 43 und 44. Er zeigt, dass mehrere gegenwärtige Diagnose- und Experimentpfade gemeinsam ausgeführt und deterministisch ausgewertet werden können. Als Ganzes ist der Lauf jedoch **nicht als Primärevidenz für `RQ-SNN-001 / H-SNN-001-A` geeignet**, weil die Bedingungen mehrere unterschiedliche Forschungsdomänen mischen und die semantische RQ/Condition-Prüfung `NOT_AUTOMATICALLY_CLASSIFIED` ergibt.

Weitere Blocker für eine EVID-Promotion des Gesamtpakets sind:

- `git dirty = true`;
- fehlende beziehungsweise nicht sauber gebundene Versions-/Freeze-Informationen im wissenschaftlichen Laufkontext;
- keine explizit manifestgebundenen Datenpartitionen für die Learning-Teile;
- fehlgeschlagener AIRR-Lauf (`HTTP 500`);
- Omnibus-Protokoll statt hypothesenspezifischem Confirmatory Protocol.

Die technischen DATA bleiben trotzdem wissenschaftlich wertvoll für die Ableitung neuer, sauber getrennter Experimente.

## 2. Rekurrenz: stärkstes dynamisches Resultat

### Kontrollbedingung ohne Rekurrenz

`ping:recurrence_off` zeigt über alle drei Seeds:

- `total_spikes = 3`;
- `activated_neurons = 3`;
- `delivered_synaptic_events = 2`;
- `recurrent_events = 0`;
- `propagation_depth = 1`.

Die beobachtete Aktivität entspricht einer kurzen Feed-forward-Propagation und endet anschließend.

### Rekurrente Bedingung

`ping:recurrence_on` zeigt über alle drei Seeds:

- `total_spikes = 33`;
- `activated_neurons = 3`;
- `delivered_synaptic_events = 33`;
- `recurrent_events = 10`;
- `propagation_depth = 61`.

Deskriptive Verhältnisse gegenüber `recurrence_off`:

- Spikezahl: `33 / 3 = 11` → **11-fach**;
- synaptische Ereignisse: `33 / 2 = 16,5` → **16,5-fach**;
- Propagation Depth: `61 / 1 = 61` → **61-fach**.

Damit verändert der eingeführte rekurrente Rückpfad die beobachtete Netzwerkdynamik klar und reproduzierbar innerhalb dieses kleinen kontrollierten Modells.

### Inter-Spike-Struktur

Für `recurrence_off` liegt das beobachtete Inter-Spike-Intervall bei `1` Tick. Für `recurrence_on` werden laut deterministischer Statistik 96 Intervalle mit folgenden Kennzahlen beobachtet:

- Mittelwert: `1,9375` Ticks;
- Median: `2` Ticks;
- Minimum: `1` Tick;
- Maximum: `4` Ticks.

Die Aktivität bleibt damit nicht als triviale konstante Ein-Tick-Oszillation bestehen. Die Rückkopplungsdynamik verlangsamt sich und erlischt innerhalb des Beobachtungsfensters. Das begründet eine neue Forschungsachse: **Wo liegt der Übergang zwischen sofortigem Erlöschen, transienter rekurrenter Aktivität und stabiler beziehungsweise pathologisch selbsttragender Aktivität?**

Nicht zulässig wäre aus diesem Lauf allein die Aussage, Rekurrenz erzeuge bereits Gedächtnis, Arbeitsgedächtnis oder kognitive Persistenz.

## 3. Reward-moduliertes Lernen: funktionelles positives Signal

Der Learning-Teil trennt `learning_on`, `learning_off` und `sham_replay`.

Für `learning_on` wurde in den analysierten Artefakten eine Änderung des mittleren Gewichts von ungefähr

`0,05 -> 0,5172804698`

beobachtet. Die absolute Änderung beträgt damit

`Delta w = 0,5172804698 - 0,05 = 0,4672804698`.

Relativ zum Startwert entspricht dies ungefähr

`0,4672804698 / 0,05 * 100 ≈ 934,6 %`.

Gleichzeitig wechselt die beobachtete Erfolgsvariable von `0` auf `1`.

`learning_off` behält das Ausgangsgewicht und zeigt keinen entsprechenden Erfolg. Im `sham_replay` werden Rewards präsentiert, ohne dass die aktive Gewichtsänderung beziehungsweise der funktionelle Erfolg entsteht. Diese Trennung ist methodisch wesentlich stärker als ein reiner Weight-Change-Test, weil Reward-Empfang und aktive Plastizität getrennt werden.

Der zugehörige produktive STDP-Pfad zeigt zusätzlich eine funktionelle Veränderung der Zielantwort: Ein zuvor nicht spikendes Ziel erreicht nach Training eine deutlich veränderte Membranantwort und einen Zielspike. Damit existiert eine beobachtete Kette

`Reward -> Weight update -> veränderte synaptische Wirksamkeit -> veränderte Zielantwort -> Spike`.

Dies ist ein starkes Signal für ein separates Generalisierungs- und Replikationsexperiment, aber noch kein Nachweis generalisierbaren Lernens.

## 4. Warum die drei Seeds keine unabhängige Replikation garantieren

Mehrere Bedingungen liefern über die Seeds 42, 43 und 44 identische Resultate. Das belegt reproduzierbare Modelltrajektorien unter diesen konkreten Bedingungen, aber nicht automatisch statistisch unabhängige Replikate.

Für eine stärkere Replikation müssen gezielt unabhängige Ausgangsvariationen eingeführt werden, beispielsweise:

- Initialgewichte;
- Initialzustände der Neuronen;
- Trainingsmuster und Reihenfolgen;
- Eingangsstörungen/Noise;
- Topologievarianten innerhalb eines kontrollierten Ensembles;
- getrennte Prozesse oder Ausführungsumgebungen.

## 5. 5D-Vergleich: derzeit kein funktionaler 5D-Nachweis

Die Bedingungen `5d:1d`, `5d:2d`, `5d:3d` und `5d:5d` zeigen im aktuellen kleinen Test dieselben makroskopischen Kennzahlen:

- 3 Spikes;
- 2 synaptische Ereignisse;
- 3 aktivierte Neuronen;
- keine Rekurrenz;
- Propagation Depth 1.

Daraus folgt **nicht**, dass 5D keinen funktionalen Wert besitzt. Der aktuelle Test ist dafür zu klein und strukturell zu wenig anspruchsvoll. Er zeigt lediglich, dass der triviale Propagationspfad in mehreren Koordinatenräumen funktioniert.

Ein aussagekräftiger 5D-Versuch muss Neuronenzahl, Synapsenzahl, Gradverteilung, Gewichtverteilung, Anfangszustand und Stimulusplan matchen und nur die relevante räumliche/dimensionale Struktur variieren.

## 6. Regulation und Unknown-State-Verhalten

Die Regulationsbedingungen trennen nominale, chronisch belastete und unbekannte Telemetrie. Besonders positiv ist, dass unbekannte Telemetrie nicht durch plausible Ersatzwerte ausgefüllt wird. Unsicherheit bleibt als Unsicherheit erhalten.

Dies validiert den technischen Unknown-State-Contract. Es zeigt jedoch noch nicht, dass Homeostase oder Interozeption die Stabilität beziehungsweise Recovery eines laufenden SNN verbessern. Dafür muss die Regulation als Intervention in einen geschlossenen dynamischen Lauf zurückwirken und gegen `regulation_off` kontrolliert werden.

## 7. Temporal-State-Ergebnis

Der Temporal-State-Pfad führt 100.000 Ticks aus und liefert FAST-, MEDIUM- und SLOW-Vergleiche. Die mittlere Diskrepanz steigt mit dem Referenzhorizont:

- fast: `2,62576e-05`;
- medium: `3,78343e-05`;
- slow: `4,61094e-05`.

Gleichzeitig werden in dieser Bedingung `0` Spikes berichtet. Der Versuch misst damit vorwiegend kontinuierliche Zustandsabweichung beziehungsweise subthreshold state drift und ist noch kein Nachweis spike-basierter zeitlicher Repräsentation oder eines Arbeitsgedächtnisses.

Daraus folgt ein eigener Versuch mit tatsächlich spike-tragender, zeitlich geordneter Information und Shuffle-/Reverse-Kontrollen.

## 8. Performance

Die Timing-Subruns enthalten unterschiedliche Tickbudgets (`100`, `1.000`, `10.000`, `100.000`). Deshalb ist die globale Summary-Aussage `Tatsächlich ausgeführte Ticks je Lauf: 100000 .. 100000` für den vollständigen Omnibus-Lauf irreführend. Korrekt ist:

> Das Hauptbeobachtungsfenster mehrerer Science-Suite-Bedingungen beträgt 100.000 Ticks; die Timing-Subruns führen protokollspezifisch 100, 1.000, 10.000 und 100.000 Ticks aus.

Die isolierten Tick-Messungen sind deutlich schneller als die Gesamtlaufzeit der vollständigen Suite. Daraus entsteht eine konkrete Performance-Forschungs- und Engineering-Frage: Welcher Anteil der Laufzeit entfällt auf Core-Ticks, Statistik/Temporal-Vergleiche, Telemetrie, Serialisierung, Storage und Reportgenerierung?

Optimierungen dürfen erst nach einem solchen Profilergebnis erfolgen und müssen deterministische Äquivalenz nachweisen.

## 9. Wissenschaftlich zulässige Schlussfolgerung

Eine konservative, durch die vorhandenen DATA gedeckte Formulierung lautet:

> `EXP-GEN-0021` validiert die technische Funktionsfähigkeit der gegenwärtigen Science Suite über mehrere Forschungsdomänen. Besonders hervorzuheben sind eine reproduzierbare Veränderung der Netzwerkdynamik durch einen kontrollierten rekurrenten Rückpfad sowie eine funktionelle Veränderung eines Zielneurons unter reward-modulierter lokaler Plastizität, die in Learning-off- und Sham-Replay-Kontrollen ausbleibt. Aufgrund des explorativen Omnibus-Designs, der fehlenden RQ-spezifischen semantischen Zuordnung und unvollständiger Clean-Freeze-Provenienz bildet der Lauf jedoch keine akzeptierte Primärevidenz für die registrierte Hypothese.

## 10. Direkt daraus folgende Forschungsfragen

1. **RQ-REC-001:** Unter welchen Rekurrenzstärken und Delays entsteht der Übergang zwischen sofortigem Erlöschen, transienter Aktivität und stabiler selbsttragender Aktivität?
2. **RQ-GEN-001:** Verbessert reward-moduliertes lokales Lernen die Leistung auf echten Holdout- und Perturbationsbedingungen?
3. **RQ-REPL-001:** Bleiben Recurrence- und Learning-Effekte unter unabhängigen Initialisierungen und Clean-Process-Replikationen erhalten?
4. **RQ-5D-005:** Verändert 5D-Geometrie unter vollständig topology-matched Kontrollen Propagation, Robustheit, Lernen oder Motifbildung?
5. **RQ-REG-002:** Verbessert geschlossene Regulation die Stabilität und Recovery des SNN gegenüber identischen Perturbationen ohne Regulation?
6. **RQ-TEMP-002:** Kann Brain-5D zeitliche Reihenfolge in spike-tragenden Aufgaben nutzen und gegen Shuffle-/Reverse-Kontrollen unterscheiden?
7. **RQ-PERF-001:** Welche Subsysteme dominieren die Wall-Time einer Science-Suite-Ausführung und welche Optimierungen erhalten deterministische Äquivalenz?

## 11. Empfohlene Experimentfolge

Priorität 1: Recurrence-Parameter-Map.  
Priorität 2: Productive-Learning-Generalization mit sauberem Train/Validation/Holdout.  
Priorität 3: unabhängige Replikation der beiden Effekte.  
Priorität 4: topology-matched 5D-Ablation.  
Priorität 5: Regulation-on/off unter kontrollierten Perturbationen.  
Priorität 6: spike-basierte Temporal-Order-Aufgabe.  
Priorität 7: Subsystem-Performanceprofil.

## 12. Quellen innerhalb des Experimentordners

- `manifest.json`
- `workflow.json`
- `analysis/statistics.json`
- `summary.md`
- `report.md`
- während der ursprünglichen Ausführung erzeugte DATA-Artefakte, soweit im wissenschaftlichen Paket vorhanden

---

**Hinweis zur Autorenschaft:** Dieses Dokument wurde durch GPT-5.6 Sol erzeugt. Es darf als Forschungsassistenz, Hypothesengenerator und Review-Dokument verwendet werden, nicht als Messdatenquelle oder automatische Evidenzentscheidung.