\"""Write the complete restructured index.html for Phase 3."""
import pathlib

OUT = pathlib.Path(r"f:\Brain-5D\src\dashboard\static\index.html")

# Read what we already have (first part was written by create_file)
existing = OUT.read_text(encoding="utf-8") if OUT.exists() else ""

# The OVERVIEW and NETWORK tabs are already written.
# Now append CONTROL & CONSOLE, RESEARCH & DOCS, RELEASE, and footer.

parts = []

# ===== CONTROL & CONSOLE =====
parts.append(r"""

    <!-- ========================================================== -->
    <!-- TAB: CONTROL & CONSOLE -->
    <!-- ========================================================== -->
    <section class="tab-content" id="tab-control">

      <!-- Control Panel -->
      <section class="control-card" id="runtime-control-card" aria-labelledby="runtime-control-title">
        <div class="control-card__header">
          <div class="control-card__title-group">
            <h2 id="runtime-control-title">Runtime Control</h2>
            <p class="control-card__subtitle">Step execution, loop control, pacing, snapshots &amp; structural gates</p>
          </div>
          <span class="runtime-state" id="runtime-state" role="status">unknown</span>
        </div>
        <div class="runtime-metrics">
          <div class="metric-item"><span class="metric-label">Tick</span><strong class="metric-value" id="runtime-tick">0</strong></div>
          <div class="metric-item"><span class="metric-label">Queued</span><strong class="metric-value" id="runtime-queued">0</strong></div>
          <div class="metric-item"><span class="metric-label">Batch</span><strong class="metric-value" id="runtime-last-batch">0</strong></div>
          <div class="metric-item"><span class="metric-label">Batch ms</span><strong class="metric-value" id="runtime-last-ms">0.0</strong></div>
        </div>
        <div class="control-grid">
          <div class="control-group step-group">
            <div class="control-group__header"><span class="control-group__title">Step</span><span class="shortcut-hint">Ctrl+Shift+S</span></div>
            <div class="control-group__body">
              <label class="input-label" for="step-ticks">Ticks <input id="step-ticks" type="number" min="1" max="10000000" value="1" /></label>
              <button id="step-button" type="button" class="btn-primary"><span class="icon">&#9654;</span> Step</button>
            </div>
          </div>
          <div class="control-group run-group">
            <div class="control-group__header"><span class="control-group__title">Run Loop</span><span class="shortcut-hint">Ctrl+Shift+R</span></div>
            <div class="control-group__body">
              <label class="input-label" for="loop-size">Loop size <input id="loop-size" type="number" min="1" max="1000000" value="100" /></label>
              <button id="run-button" type="button" class="btn-success"><span class="icon">&#9654;&#9654;</span> Run</button>
            </div>
          </div>
          <div class="control-group config-group">
            <div class="control-group__header"><span class="control-group__title">Configure</span></div>
            <div class="control-group__body">
              <label class="input-label" for="delay-ms">Delay/tick (ms) <input id="delay-ms" type="number" min="0" max="60000" step="0.1" value="0" /></label>
              <button id="apply-runtime-config" type="button" class="btn-secondary"><span class="icon">&#9881;</span> Apply</button>
            </div>
          </div>
          <div class="control-group actions-group">
            <div class="control-group__header"><span class="control-group__title">Control</span></div>
            <div class="control-group__body actions-row">
              <button id="pause-button" type="button" class="btn-warning"><span class="icon">&#9208;</span> Pause</button>
              <button id="snapshot-button" type="button" class="btn-info"><span class="icon">&#128190;</span> Snapshot</button>
              <button id="stop-button" type="button" class="btn-danger"><span class="icon">&#9209;</span> Stop</button>
            </div>
          </div>
        </div>
        <details class="self-org-section" id="self-org-section">
          <summary class="self-org-summary"><h3>Self-Organization Gate</h3><span class="badge" id="self-org-status-badge">checking...</span></summary>
          <div class="self-org-controls">
            <div class="self-org-row">
              <label class="switch-line" for="self-org-enabled"><input id="self-org-enabled" type="checkbox" checked /><span class="switch-line__label">Policy enabled</span><span class="switch-line__help">Allow structural changes</span></label>
              <label class="switch-line" for="self-org-dry-run"><input id="self-org-dry-run" type="checkbox" checked /><span class="switch-line__label">Dry-run mode</span><span class="switch-line__help">Simulate without applying</span></label>
            </div>
            <div class="proposal-line">
              <span class="proposal-label">Last proposal</span>
              <strong id="self-org-proposal">none</strong>
              <span id="self-org-proposal-time" class="proposal-time"></span>
            </div>
            <div class="proposal-actions">
              <button id="btn-undo-structural" type="button" class="btn-small undo">Undo last change</button>
              <button id="btn-auto-approval" type="button" class="btn-small auto-approval" data-enabled="false">Enable Auto-Approval</button>
            </div>
          </div>
        </details>
        <output id="control-message" class="control-message" aria-live="polite">Ready</output>
      </section>

      <!-- Operator Console -->
      <section class="card operator-console" id="operator-console" aria-labelledby="console-title">
        <div class="console-header">
          <div class="console-title-group">
            <h2 id="console-title">Operator Console</h2>
            <p class="console-subtitle">Step execution, loop control, structural proposals &amp; system monitoring</p>
          </div>
          <div class="console-status-group">
            <span class="status-badge" id="b5d-state-badge">idle</span>
            <span class="tick-display" id="b5d-tick-display">0</span>
          </div>
        </div>
        <div class="console-metrics" id="b5d-metrics" role="group">
          <span class="metric">Neurons <span id="metric-neurons">0</span></span>
          <span class="metric">Synapses <span id="metric-synapses">0</span></span>
          <span class="metric">Spikes <span id="metric-spikes">0</span></span>
          <span class="metric">Queue <span id="metric-queue">0</span></span>
        </div>
        <div class="console-controls">
          <div class="control-group">
            <div class="control-group__header"><span class="control-group__title">Step</span><span class="shortcut-hint">Ctrl+Enter</span></div>
            <div class="control-group__body"><button id="b5d-step" class="btn-primary">+1 Tick</button></div>
          </div>
          <div class="control-group">
            <div class="control-group__header"><span class="control-group__title">Run N Ticks</span></div>
            <div class="control-group__body">
              <label class="input-label" for="b5d-tick-count"><input id="b5d-tick-count" type="number" min="1" max="10000000" value="100" /></label>
              <button id="b5d-run-ticks" class="btn-success">Run</button>
            </div>
          </div>
          <div class="control-group">
            <div class="control-group__header"><span class="control-group__title">Runtime</span></div>
            <div class="control-group__body actions-row">
              <button id="b5d-start" class="btn-success">Start</button>
              <button id="b5d-pause" class="btn-warning">Pause</button>
              <button id="b5d-resume" class="btn-primary">Resume</button>
              <button id="b5d-stop" class="btn-danger">Stop</button>
            </div>
          </div>
          <div class="control-group">
            <div class="control-group__header"><span class="control-group__title">Utilities</span></div>
            <div class="control-group__body actions-row">
              <button id="b5d-snapshot" class="btn-info">Snapshot</button>
              <button id="b5d-undo" class="btn-undo">Undo Change</button>
              <button id="b5d-clear-console" class="btn-secondary">Clear</button>
            </div>
          </div>
        </div>
        <details class="proposals-section" id="proposals-section">
          <summary class="proposals-summary"><span class="proposals-title">Structural Proposals</span><span class="badge" id="proposals-count">0 pending</span></summary>
          <div id="b5d-proposals" class="proposals-list"><div class="proposal-empty">No pending proposals</div></div>
        </details>
        <div class="console-output-wrapper">
          <div class="console-output-header"><span class="console-output-title">Console Log</span><span class="console-output-hint">Auto-scroll &middot; Max 1000 entries</span></div>
          <div id="console-output" class="console-output" role="log" aria-live="polite">
            <div class="log-entry log-info"><span class="log-time">[00:00:00]</span> Brain-5D Operator Console ready</div>
          </div>
        </div>
        <p class="operator-note">Structural proposals remain approval-gated. No autonomous mutation is enabled by this panel.</p>
      </section>

      <!-- Structural Live Loop Status -->
      <section class="card structural-live-card">
        <div class="panel-title">
          <h2>Structural Live Loop</h2>
          <span id="live-loop-badge" class="gate-badge pending">checking...</span>
        </div>
        <div class="structural-live-grid" id="structural-live-grid">
          <div class="live-loop-item" id="ll-adapter">RuntimeAdapter</div>
          <div class="live-loop-item" id="ll-signal">HomeostasisSignal</div>
          <div class="live-loop-item" id="ll-policy">Policy Proposal</div>
          <div class="live-loop-item" id="ll-coordinator">Coordinator</div>
          <div class="live-loop-item" id="ll-approval">Approval Gate</div>
          <div class="live-loop-item" id="ll-mutation">Mutation</div>
          <div class="live-loop-item" id="ll-journal">Journal</div>
          <div class="live-loop-item" id="ll-undo">Undo</div>
          <div class="live-loop-item" id="ll-replay">Replay</div>
        </div>
        <p class="heatmap-meta" id="live-loop-meta">Requires poc_structural_live.yaml config</p>
      </section>

    </section> <!-- /tab-control -->
""")

# ===== RESEARCH & DOCS =====
parts.append(r"""

    <!-- ========================================================== -->
    <!-- TAB: RESEARCH & DOCS -->
    <!-- ========================================================== -->
    <section class="tab-content" id="tab-research">

      <div class="research-docs-split">

        <!-- Research side -->
        <div class="research-browser">
          <div class="research-sidebar">
            <div class="research-toolbar">
              <h3>B5D Scientific Evidence Framework</h3>
              <div id="research-summary" class="research-summary"><span class="research-stat">Initialisiere Research-Quelle...</span></div>
            </div>
            <div class="research-section">
              <h4>Generated Reports</h4>
              <div id="research-reports" class="research-list"><span class="research-empty">Wird geladen...</span></div>
            </div>
            <div class="research-section">
              <h4>Registry</h4>
              <div id="research-documents" class="research-docs"><span class="research-empty">Wird geladen...</span></div>
            </div>
            <div class="research-section">
              <h4>Experiments</h4>
              <div id="research-experiments" class="research-list"><span class="research-empty">Wird geladen...</span></div>
            </div>
          </div>
          <div id="research-viewer" class="research-viewer">
            <div class="research-placeholder">
              <p>Select a research document to view its contents.</p>
              <p class="research-hint">B5D-SEF registry: 27 Research Questions &middot; 27 Hypotheses &middot; 5 Claims &middot; 8 Sources &middot; 13 Methods</p>
            </div>
          </div>
        </div>

        <!-- Docs side -->
        <div class="doc-browser">
          <div class="doc-sidebar">
            <div class="doc-toolbar">
              <input type="text" id="doc-search" placeholder="Search documents..." />
              <div id="doc-filter-container"></div>
              <button id="doc-refresh">Refresh</button>
            </div>
            <div id="doc-stats" class="doc-stats">Lade Dokumentation...</div>
            <div id="doc-tree" class="doc-tree">Lade Verzeichnisstruktur...</div>
          </div>
          <div id="doc-viewer" class="doc-viewer">
            <div class="doc-placeholder">
              <p>Select a document to view its contents.</p>
              <p style="color: #888; font-size: 13px;">Supported formats: Markdown, Text, DOCX, XLSX, CSV, JSON, PDF (metadata)</p>
            </div>
          </div>
        </div>

      </div>

    </section> <!-- /tab-research -->
""")

# ===== RELEASE (Alpha.5 Gate) =====
parts.append(r"""

    <!-- ========================================================== -->
    <!-- TAB: RELEASE (Alpha.5 Gate) -->
    <!-- ========================================================== -->
    <section class="tab-content" id="tab-gate">
      <div class="gate-board">
        <div class="gate-header">
          <h2>Alpha.5 Release Gate</h2>
          <p class="gate-subtitle">
            Alpha.5 is complete only when all Gate A, B and C criteria pass.
            <span class="gate-rule">Do not advance to alpha.6 while this gate is open.</span>
          </p>
          <p class="gate-legend">
            <strong>Live</strong> = current runtime config state &middot;
            <strong>Maturity</strong> = IMPLEMENTED &rarr; INTEGRATED &rarr; VERIFIED &rarr; EVIDENCED &middot;
            <strong>Gate</strong> = release verification result.
            Runtime disabled &ne; gate failed. Runtime disabled &ne; gate passed.
          </p>
          <button id="gate-refresh" type="button" class="btn-secondary">Re-check</button>
        </div>

        <div class="gate-overall-row">
          <strong>ALPHA.5 Overall:</strong>
          <span class="gate-badge pending" id="gate-overall">pending</span>
        </div>

        <!-- Live Runtime Profile -->
        <div class="gate-section">
          <h3>Live Runtime Profile <span class="gate-section-hint">(current config)</span></h3>
          <div id="gate-live-list" class="gate-live-grid"></div>
        </div>

        <!-- Gate A -->
        <div class="gate-section">
          <h3>Gate A &mdash; Technical Integration</h3>
          <div id="gate-a-list" class="gate-criteria-table"></div>
        </div>

        <!-- Gate B -->
        <div class="gate-section">
          <h3>Gate B &mdash; Verification</h3>
          <div id="gate-b-list" class="gate-criteria-table"></div>
        </div>

        <!-- Gate C -->
        <div class="gate-section">
          <h3>Gate C &mdash; Scientific Baseline</h3>
          <div id="gate-c-list" class="gate-criteria-table"></div>
        </div>
      </div>
    </section> <!-- /tab-gate -->

  </main>

  <!-- ============================================================ -->
  <!-- INTEG