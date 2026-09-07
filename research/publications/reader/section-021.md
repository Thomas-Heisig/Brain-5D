[Inhaltsuebersicht](README.md) | [Zurueck](section-020.md) | [Weiter](section-022.md)

<a id="b5d-plastizität-homeostase-und-struktureller-wandel"></a>

# 17. Plastizität, Homeostase und struktureller Wandel

<a id="b5d-synaptische-modulatorische-und-intrinsische-plastizität"></a>

## Synaptische, modulatorische und intrinsische Plastizität

<a id="b5d-pair-based-stdp"></a>

### Pair-based STDP

**\[MODEL\]** Für $\Delta t = t_{post} - t_{pre}$:

**\[MODEL \| redaktionelle Ergänzung\]** Die Originalformel in K1 endet an dieser Stelle mit „Delta w =“ und enthält keine rechte Seite. Als explizite Ergänzung wird folgende konventionelle Familie paarbasierter STDP-Regeln beschrieben; sie rekonstruiert keinen nachgewiesenen Brain-5D-Codepfad. Die positive und negative Timing-Abhängigkeit wird in K1 mit Bi und Poo (1998), Markram et al. (1997) und Song et al. (2000) eingeordnet.

$$\Delta w(\Delta t)=A_p\exp(-\Delta t/\tau_p),\qquad \Delta t>0$$$$\Delta w(\Delta t)=-A_d\exp(\Delta t/\tau_d),\qquad \Delta t<0$$Dabei sind $A_p,A_d,\tau_p,\tau_d>0$; $\Delta t=t_{post}-t_{pre}$ folgt der vorstehenden Vorzeichenkonvention. $p$ bezeichnet die potentiierende, $d$ die deprimierende Komponente. Der Fall gleichzeitiger Ereignisse muss im Protokoll festgelegt werden; eine Nulländerung bei $\Delta t=0$ wäre eine zulässige Modellkonvention, keine biologische Allgemeinregel. Paarbildung, Mehrfachspikes, Gewichtsschranken und Update-Reihenfolge bleiben eigenständige Festlegungen. Diese Ergänzung beansprucht keine empirische Bestätigung der Projektimplementierung.

Die Form abstrahiert experimentell beobachtete timingabhängige Änderungen ([Bi & Poo, 1998](section-045.md#ref-Bi1998); [Markram et al., 1997](section-045.md#ref-Markram1997)). Sie ist nicht universell: Zelltyp, Frequenz, Spannung, Kalzium und Spike-Triplets können die Regel verändern ([Clopath et al., 2010](section-045.md#ref-Clopath2010); [Graupner & Brunel, 2012](section-045.md#ref-Graupner2012); [Pfister & Gerstner, 2006](section-045.md#ref-Pfister2006)).

<a id="b5d-gewichtsgrenzen-und-soft-bounds"></a>

### Gewichtsgrenzen und Soft Bounds

Harte Begrenzung lautet

$$w_{ij} \leftarrow clip\left( w_{ij} + \Delta w,w_{min},w_{max} \right).$$Alternativ können multiplicative oder gewichtabhängige Updates Sättigung modellieren. Die Grenzregel beeinflusst langfristige Verteilungen und ist als eigener Faktor zu behandeln.

<a id="b5d-eligibility-und-three-factor-learning"></a>

### Eligibility und Three-Factor Learning

**\[MODEL\]** Ein Eligibility Trace kann durch

$$\tau_{e}{\dot{e}}_{ij} = - e_{ij} + \phi\left( s_{i}^{pre},s_{j}^{post} \right)$$und eine modulierte Änderung durch

$${\dot{w}}_{ij} = \eta m(t)e_{ij}(t)$$beschrieben werden. $m(t)$ kann Reward Prediction Error, regionales Modulationssignal oder experimentell kontrollierten Verstärker darstellen. Three-Factor-Regeln adressieren die zeitliche Lücke zwischen lokaler Aktivität und späterem Reward ([Frémaux & Gerstner, 2016](section-045.md#ref-Fremaux2016); [Gerstner et al., 2018](section-045.md#ref-Gerstner2018eligibility); [Izhikevich, 2007b](section-045.md#ref-Izhikevich2007reward)). Ein globales Signal ist jedoch nicht automatisch „Dopamin”; biologische Benennungen werden nur verwendet, wenn das Modell die entsprechende Funktion und Einschränkung tatsächlich abbildet.

<a id="b5d-inhibitorische-plastizität"></a>

### Inhibitorische Plastizität

Inhibitorische Anpassung kann E/I-Regime und Feuerraten stabilisieren ([Vogels et al., 2011](section-045.md#ref-Vogels2011)). Sie darf nicht als bloßes negatives STDP implementiert werden, ohne Zelltyp, Zielrate und Vorzeichenkonvention zu dokumentieren. Eine Ablation muss prüfen, ob der beobachtete Stabilitätseffekt spezifisch inhibitorisch oder nur Folge zusätzlicher Gewichtsnormalisierung ist.

<a id="b5d-intrinsische-plastizität"></a>

### Intrinsische Plastizität

Neuronale Schwellen, Adaptationsparameter oder Membranzeitkonstanten können langsam angepasst werden. Eine einfache Zielratenregel ist

**\[MODEL\]**

$$\theta_{i}(t + \Delta t) = \theta_{i}(t) + \eta_{h}\left( \bar{r}_{i}(t) - r_i^{\star} \right).$$Dies ist eine technische Homeostaseform. Biologische homeostatische Plastizität umfasst mehrere Mechanismen und Zeitskalen ([Turrigiano et al., 1998](section-045.md#ref-Turrigiano1998); [Turrigiano & Nelson, 2004](section-045.md#ref-Turrigiano2004)).

<a id="b5d-metaplastizität"></a>

### Metaplastizität

Metaplastizität verändert nicht unmittelbar das Gewicht, sondern die Lernbereitschaft oder Regelparameter. Ein BCM-artiger gleitender Schwellenwert kann geschrieben werden als

$$\tau_{\theta}{\dot{\theta}}_{i} = \bar{r}_{i}^{2} - \theta_{i},$$während die synaptische Änderung von $r_{i}\left( r_{i} - \theta_{i} \right)$ abhängt ([Bienenstock et al., 1982](section-045.md#ref-Bienenstock1982)). In Brain-5D ist Metaplastizität ein Kandidat zur Kontrolle langfristiger Interferenz, nicht vorausgesetzte Lösung.

<a id="b5d-stabilitäts-plastizitäts-konflikt"></a>

### Stabilitäts-Plastizitäts-Konflikt

Hebb-artige positive Rückkopplung kann zu Runaway-Aktivität führen. Homeostase wirkt dem entgegen, kann aber zu langsam sein oder Lernsignale neutralisieren ([Zenke et al., 2013](section-045.md#ref-Zenke2013); [Zenke & Gerstner, 2017](section-045.md#ref-Zenke2017homeostasis)). Brain-5D untersucht daher Zeitskalenverhältnisse, nicht nur das An-/Ausschalten einzelner Mechanismen. Ein stabiler Mittelwert kann zudem dynamische Pathologien verbergen; Varianz, Burststruktur, Korrelation und regionale Verteilung sind mitzuerfassen.

<a id="b5d-strukturelle-plastizität-und-neurogenese"></a>

## Strukturelle Plastizität und Neurogenese

<a id="b5d-funktionale-versus-strukturelle-änderung"></a>

### Funktionale versus strukturelle Änderung

**\[DEF\]** Funktionale Plastizität verändert Attribute bestehender Kanten oder Knoten. Strukturelle Plastizität verändert $V_{t}$ oder $E_{t}$ selbst. Beide können zusammenwirken, müssen im Event-Log aber unterscheidbar bleiben.

<a id="b5d-synapsenentstehung"></a>

### Synapsenentstehung

Eine neue Kante kann nur entstehen, wenn harte Constraints und ein probabilistisches beziehungsweise heuristisches Auswahlkriterium erfüllt sind:

**\[HEUR\]**

$$\text{create}_{ij} = 1\left\lbrack d_{M}(i,j) < d_{max} \right\rbrack1\left\lbrack B_{t}^{syn} > 0 \right\rbrack1\left\lbrack C_{ij} > C_{min} \right\rbrack \cdot Bernoulli\left( P_{ij} \right).$$$B_{t}^{syn}$ ist das verbleibende Synapsenbudget. Die Korrelation $C_{ij}$ muss mit einem kausal sauberen Zeitfenster berechnet werden; sonst können gemeinsame Inputs fälschlich direkte Beziehung suggerieren.

<a id="b5d-pruning"></a>

### Pruning

**\[HEUR\]** Eine Kante wird zum Pruning-Kandidaten, wenn

$$\left| w_{ij}(t) \right| < w_{prune},U_{ij}(t) < u_{min},age_{ij} > T_{grace}$$über ein Mindestintervall gilt. $U_{ij}$ kann Nutzung, Contribution oder Eligibility zusammenfassen. Sofortiges Pruning nach kurzfristiger Inaktivität würde langsame oder episodische Verbindungen benachteiligen.

<a id="b5d-neurogenese"></a>

### Neurogenese

Neue Neuronen dürfen nicht als Synapsenwachstum bezeichnet werden. Ein Growth-Score ist eine explizite Heuristik:

**\[HEUR\]**

$$G_{r} = \alpha O_{r} + \beta E_{r} + \gamma D_{r} + \zeta U_{r} - \delta C_{r},$$mit regionaler Überlastung $O_{r}$, wiederkehrendem Fehler $E_{r}$, Diversitätsbedarf $D_{r}$, unzureichender Kapazitätsnutzung $U_{r}$ und Kosten $C_{r}$. Wachstum erfolgt nur bei $G_{r} > G_{threshold}$, vorhandener Adresskapazität und globalem Budget. Die Heuristik muss gegen einfachere Alternativen wie mehr Anfangsneuronen oder erhöhte Synapsendichte getestet werden.

<a id="b5d-entwicklungs--und-altersattribute"></a>

### Entwicklungs- und Altersattribute

Knoten und Kanten erhalten Erzeugungszeitpunkt, Alter, letzte Nutzung, kumulative Aktivität und gegebenenfalls Entwicklungsphase. Diese Attribute ermöglichen Fragen wie: Werden neue Neuronen funktional integriert? Steigt ihre Survival Rate selektiv? Verändert sich Turnover mit Aufgabenwechseln? Eine bloße Erhöhung der Neuronenzahl ist kein Nachweis nützlicher Neurogenese.

<a id="b5d-ressourcenmodell"></a>

### Ressourcenmodell

**\[MODEL\]** Eine abstrakte Kostenfunktion lautet

$$C_{t} = c_{N}\left| V_{t} \right| + c_{E}\left| E_{t} \right| + c_{P}N_{spike}(t) + c_{U}N_{update}(t) + c_{G}N_{struct}(t) + c_{IO}B_{IO}(t).$$Das System arbeitet unter

$$C_{t} \leq C_{max},\left| V_{t} \right| \leq N_{max},\left| E_{t} \right| \leq S_{max}.$$Die Koeffizienten können reale Laufzeit, Energieproxy oder normierte Ressourcen repräsentieren. Sie sind zu kalibrieren und dürfen nicht ohne Messung als physikalische Energie interpretiert werden.

<a id="b5d-stand-der-forschung-und-brain-5d-hypothese"></a>

### Stand der Forschung und Brain-5D-Hypothese

Erfahrungsabhängige strukturelle Plastizität und aktivitätsabhängiges Rewiring sind etablierte Forschungsfelder ([Butz et al., 2009](section-045.md#ref-Butz2009); [Holtmaat & Svoboda, 2009](section-045.md#ref-Holtmaat2009); [Li et al., 2024](section-045.md#ref-Li2024rewiring)). Neuere Modelle untersuchen die Bildung mehrerer Engramme mit strukturellen und homeostatischen Mechanismen ([Kaster et al., 2024](section-045.md#ref-Kaster2024)). Brain-5D leitet daraus keine automatische Gedächtnisfunktion ab, sondern formuliert die prüfbare Hypothese, dass Turnover und Ressourcenregeln Continual Learning unter bestimmten Aufgabenverteilungen verbessern können.

[Inhaltsuebersicht](README.md) | [Zurueck](section-020.md) | [Weiter](section-022.md)
