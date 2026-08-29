f=open(r'F:\Brain-5D\src\dashboard\static\index.html','r',encoding='utf-8')
c=f.read()
f.close()

old='      <!-- Roadmap -->\n      <section class="grid roadmap-grid">'

new='      <!-- IO-Fluss Visualisierung -->\n      <section class="card io-flow-panel">\n        <div class="panel-title">\n          <div><h2>🔀 Input-Output Fluss</h2><p>Signalpropagation durch das Netzwerk</p></div>\n          <span id="io-flow-badge" class="gate-badge pending">⏳</span>\n        </div>\n        <div class="io-flow-grid">\n          <div class="io-flow-layer io-input">\n            <div class="io-layer-header">Input <span id="io-input-count">0</span></div>\n            <div class="io-layer-bar"><div class="io-layer-fill" id="io-input-fill"></div></div>\n            <div class="io-layer-rate"><span id="io-input-rate">0.000</span> spikes/tick</div>\n          </div>\n          <div class="io-flow-arrow">→</div>\n          <div class="io-flow-layer io-hidden">\n            <div class="io-layer-header">Hidden <span id="io-hidden-count">0</span></div>\n            <div class="io-layer-bar"><div class="io-layer-fill" id="io-hidden-fill"></div></div>\n            <div class="io-layer-rate"><span id="io-hidden-rate">0.000</span> spikes/tick</div>\n          </div>\n          <div class="io-flow-arrow">→</div>\n          <div class="io-flow-layer io-output">\n            <div class="io-layer-header">Output <span id="io-output-count">0</span></div>\n            <div class="io-layer-bar"><div class="io-layer-fill" id="io-output-fill"></div></div>\n            <div class="io-layer-rate"><span id="io-output-rate">0.000</span> spikes/tick</div>\n          </div>\n        </div>\n        <div class="io-flow-meta" id="io-flow-meta">⏳ Lade Daten...</div>\n      </section>\n\n      <!-- Populationen Übersicht -->\n      <section class="card population-panel">\n        <div class="panel-title">\n          <div><h2>👥 Neuronale Populationen</h2><p>E/I-Ratio, Aktivität pro Typ</p></div>\n          <span id="ei-ratio-badge" class="gate-badge">E/I: —</span>\n        </div>\n        <div class="population-grid" id="population-grid">\n          <div class="population-empty">⏳ Lade Populationsdaten...</div>\n        </div>\n        <div class="population-meta" id="population-meta">Aktualisiert: —</div>\n      </section>\n\n      <!-- Roadmap -->\n      <section class="grid roadmap-grid">'

c=c.replace(old,new,1)

f=open(r'F:\Brain-5D\src\dashboard\static\index.html','w',encoding='utf-8')
f.write(c)
f.close()
print("index.html updated OK")
