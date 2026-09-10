[Inhaltsuebersicht](README.md) | [Zurueck](section-019.md) | [Weiter](section-021.md)

<a id="b5d-neuronale-dynamik-und-synaptische-übertragung"></a>

# 16. Neuronale Dynamik und synaptische Übertragung

<a id="b5d-neuronale-dynamikmodelle"></a>

## Neuronale Dynamikmodelle

<a id="b5d-modellpluralismus"></a>

### Modellpluralismus

MHRN sollte keine zentrale Hypothese von einem einzigen Neuronenmodell abhängig machen. LIF, AdEx und Izhikevich bilden unterschiedliche Kompromisse zwischen Rechenaufwand und dynamischer Vielfalt ([Brette & Gerstner, 2005](section-045.md#ref-Brette2005); [Gerstner et al., 2014](section-045.md#ref-Gerstner2014); [Izhikevich, 2003](section-045.md#ref-Izhikevich2003)). Für ausgewählte Benchmarks ist deshalb eine Modellablation vorzusehen.

<a id="b5d-izhikevich-modell"></a>

### Izhikevich-Modell

**\[MODEL\]**

$$\frac{dv_{i}}{dt} = 0.04v_{i}^{2} + 5v_{i} + 140 - u_{i} + I_{i}(t),$$$$\frac{du_{i}}{dt} = a_{i}\left( b_{i}v_{i} - u_{i} \right).$$Bei $v_{i} \geq 30mV$ erfolgt der Sprung

$$v_{i} \leftarrow c_{i},u_{i} \leftarrow u_{i} + d_{i}.$$Die Parameter $a,b,c,d$ können unterschiedliche Spike-Regime approximieren ([Izhikevich, 2003](section-045.md#ref-Izhikevich2003)). Numerische Schrittweite, Integrationsmethode und Rundungsregeln müssen dokumentiert werden, weil sie das qualitative Verhalten verändern können.

<a id="b5d-leaky-integrate-and-fire"></a>

### Leaky Integrate-and-Fire

**\[MODEL\]**

$$\tau_{m}\frac{dV_{i}}{dt} = - \left( V_{i} - E_{L} \right) + R_{m}I_{i}(t).$$Bei Schwellenüberschreitung wird ein Spike ausgelöst und $V_{i}$ nach einer definierten Regel zurückgesetzt. LIF ist für große Skalierungen attraktiv, bildet jedoch nicht alle intrinsischen Burst- und Adaptationsregime ab.

<a id="b5d-adaptive-exponential-integrate-and-fire"></a>

### Adaptive Exponential Integrate-and-Fire

**\[MODEL\]**

$$C\dot{V} = - g_{L}\left( V - E_{L} \right) + g_{L}\Delta_{T}\exp\left( \frac{V - V_{T}}{\Delta_{T}} \right) - w + I(t),$$$$\tau_{w}\dot{w} = a\left( V - E_{L} \right) - w.$$AdEx erweitert LIF um exponentielle Spike-Initiation und Adaptation ([Brette & Gerstner, 2005](section-045.md#ref-Brette2005)). Die Modellablation soll prüfen, ob zentrale Ergebnisse an einer spezifischen intrinsischen Dynamik hängen.

<a id="b5d-eingangsströme-verzögerungen-und-synapsentypen"></a>

### Eingangsströme, Verzögerungen und Synapsentypen

Der Gesamteingang kann geschrieben werden als

**\[MODEL\]**

$$I_{i}(t) = I_{i}^{ext}(t) + \sum_jw_{ji}(t)k_{ji}\left( t - t_{j}^{spike} - \delta_{ji} \right) + I_{i}^{mod}(t) + \eta_{i}(t),$$mit synaptischem Kernel $k$, Verzögerung $\delta$, modulatorischem Eingang und Rauschen $\eta$. Exzitatorische und inhibitorische Wirkungen werden nicht nur durch Vorzeichen, sondern vorzugsweise durch typisierte Synapsen und getrennte Grenzwerte repräsentiert. Dale-artige Beschränkungen können als Versuchsbedingung aktiviert werden.

<a id="b5d-populationsstabilität-und-ei-balance"></a>

### Populationsstabilität und E/I-Balance

Ein einfacher E/I-Index

$$B_{EI}(t) = \frac{\sum_{(i,j)\in E_{exc}}\left| w_{ij}(t) \right|}{\sum_{(i,j)\in E_{inh}}\left| w_{ij}(t) \right| + \epsilon}$$ist nur eine grobe Strukturmetrik. Funktionale Balance betrifft zeitabhängige Ströme, Korrelationen und Netzwerkrückkopplungen. Balancierte Netze können irreguläre Aktivität erzeugen ([Brunel, 2000](section-045.md#ref-Brunel2000); [Vreeswijk & Sompolinsky, 1996](section-045.md#ref-VanVreeswijk1996)); ein einzelnes Gewichtsverhältnis genügt nicht als Nachweis.

[Inhaltsuebersicht](README.md) | [Zurueck](section-019.md) | [Weiter](section-021.md)
