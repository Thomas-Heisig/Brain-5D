const $ = (id) => document.getElementById(id);
let heatmapKind = "activity";
let selectedSnapshot = "";

function formatBytes(value) {
  const units = ["B", "KiB", "MiB", "GiB"];
  let size = Number(value || 0);
  let index = 0;
  while (size >= 1024 && index < units.length - 1) {
    size /= 1024;
    index += 1;
  }
  return `${size.toFixed(index === 0 ? 0 : 2)} ${units[index]}`;
}

function setText(id, value) {
  const node = $(id);
  if (node) node.textContent = String(value);
}

async function refreshStatus() {
  try {
    const response = await fetch("/api/status", {cache: "no-store"});
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    const system = data.system;
    const storage = data.storage;
    const learning = data.learning;
    const selfOrg = data.self_organization;
    const homeostasis = data.homeostasis || {};
    const embodiment = data.embodiment || {};

    setText("tick", system.tick);
    setText("neurons", system.neurons.toLocaleString());
    setText("synapses", system.synapses.toLocaleString());
    setText("spikes", system.spikes_total.toLocaleString());
    setText("core-ms", Number(system.core_step_ms).toFixed(3));
    setText("energy", Number(system.mean_energy).toFixed(3));

    setText("deltas", storage.deltas_written.toLocaleString());
    setText("bytes", formatBytes(storage.bytes_written));
    setText("write-ms", `${Number(storage.write_latency_ms).toFixed(3)} ms`);
    setText("commit-ms", `${Number(storage.commit_latency_ms).toFixed(3)} ms`);
    setText("journal-size", formatBytes(storage.journal_size_bytes));
    setText("drops", storage.dropped_batches);
    setText("queue-badge", `${storage.queue_depth} / ${storage.queue_capacity}`);
    const queuePercent = storage.queue_capacity > 0
      ? Math.min(100, storage.queue_depth / storage.queue_capacity * 100)
      : 0;
    $("queue-fill").style.width = `${queuePercent}%`;

    setText("stdp", learning.stdp_updates);
    setText("reward-updates", learning.reward_updates);
    setText("rewards", `${learning.rewards_applied} / ${learning.rewards_received}`);
    setText("pending", learning.pending_rewards);
    setText("learning-ms", `${Number(learning.update_ms).toFixed(3)} ms`);

    setText("neurons-created", selfOrg.neurons_created);
    setText("neurons-removed", selfOrg.neurons_removed);
    setText("synapses-created", selfOrg.synapses_created);
    setText("synapses-pruned", selfOrg.synapses_pruned);

    setText("homeo-target", `${Number(homeostasis.target_rate_hz || 0).toFixed(3)} Hz`);
    setText("homeo-actual", `${Number(homeostasis.actual_rate_hz || 0).toFixed(3)} Hz`);
    setText("homeo-error", `${Number(homeostasis.rate_error_hz || 0).toFixed(3)} Hz`);
    setText("homeo-threshold", Number(homeostasis.mean_threshold_adaptation || 0).toFixed(3));
    setText("homeo-energy", Number(homeostasis.mean_energy_error || 0).toFixed(3));
    setText("homeo-active", Number(homeostasis.active_neurons || 0).toLocaleString());

    setText("embodiment-kind", embodiment.environment_kind || "unconfigured");
    setText("embodiment-sensors", Number(embodiment.active_sensors || 0));
    setText("embodiment-actuators", Number(embodiment.active_actuators || 0));
    setText("embodiment-episode", Number(embodiment.episode || 0));
    setText("embodiment-reward", Number(embodiment.last_reward || 0).toFixed(3));
    setText("embodiment-action", embodiment.last_action || "—");

    const status = $("system-status");
    status.textContent = `${data.status} · ${data.version}`;
    status.className = storage.worker_failed ? "status-pill error" : "status-pill online";
  } catch (error) {
    const status = $("system-status");
    status.textContent = "offline";
    status.className = "status-pill error";
  }
}

function colorFor(value, min, max) {
  const scale = max > min ? (value - min) / (max - min) : 0;
  const t = Math.max(0, Math.min(1, scale));
  const hue = 210 - (195 * t);
  const light = 16 + (46 * t);
  return `hsl(${hue} 88% ${light}%)`;
}

function drawHeatmap(payload) {
  const canvas = $("heatmap");
  const ctx = canvas.getContext("2d");
  const rows = payload.values;
  if (!rows.length || !rows[0].length) return;
  const flat = rows.flat();
  const min = Math.min(...flat);
  const max = Math.max(...flat);
  const width = rows[0].length;
  const height = rows.length;
  const cellW = canvas.width / width;
  const cellH = canvas.height / height;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  rows.forEach((row, y) => {
    row.forEach((value, x) => {
      ctx.fillStyle = colorFor(value, min, max);
      ctx.fillRect(x * cellW, y * cellH, Math.ceil(cellW), Math.ceil(cellH));
    });
  });
  setText(
    "heatmap-meta",
    `${payload.snapshot} · ${payload.kind} · Tick ${payload.tick} · `
      + `${payload.samples} Samples · ${min.toFixed(4)}…${max.toFixed(4)}`,
  );
}

async function refreshHeatmap() {
  try {
    const params = new URLSearchParams({kind: heatmapKind});
    if (selectedSnapshot) params.set("snapshot", selectedSnapshot);
    const response = await fetch(`/api/heatmap?${params}`, {cache: "no-store"});
    if (!response.ok) {
      const data = await response.json();
      setText("heatmap-meta", data.error || `Heatmap HTTP ${response.status}`);
      return;
    }
    drawHeatmap(await response.json());
  } catch (error) {
    setText("heatmap-meta", "Heatmap nicht erreichbar.");
  }
}

async function refreshSnapshots() {
  const select = $("snapshot-select");
  try {
    const response = await fetch("/api/snapshots", {cache: "no-store"});
    if (!response.ok) return;
    const data = await response.json();
    const snapshots = data.snapshots || [];
    const previous = selectedSnapshot;
    select.replaceChildren();
    snapshots.forEach((entry) => {
      const option = document.createElement("option");
      option.value = entry.name;
      option.textContent = `${entry.name} (${formatBytes(entry.size_bytes)})`;
      select.appendChild(option);
    });
    if (snapshots.length) {
      selectedSnapshot = snapshots.some((entry) => entry.name === previous)
        ? previous
        : snapshots[0].name;
      select.value = selectedSnapshot;
    } else {
      const option = document.createElement("option");
      option.textContent = "Kein Snapshot";
      option.value = "";
      select.appendChild(option);
      selectedSnapshot = "";
    }
  } catch (error) {
    selectedSnapshot = "";
  }
}

function escapeText(value) {
  return String(value ?? "");
}

async function loadDocument(name) {
  const response = await fetch(`/api/docs?name=${encodeURIComponent(name)}`);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
  setText("docs-title", data.name);
  setText("docs-content", escapeText(data.content));
}

async function openDocs() {
  const modal = $("docs-modal");
  const list = $("docs-list");
  modal.classList.add("open");
  modal.setAttribute("aria-hidden", "false");
  list.replaceChildren();
  try {
    const response = await fetch("/api/docs", {cache: "no-store"});
    const data = await response.json();
    const documents = data.documents || [];
    documents.forEach((entry) => {
      const button = document.createElement("button");
      button.className = "doc-link";
      button.textContent = entry.name;
      button.addEventListener("click", () => void loadDocument(entry.name));
      list.appendChild(button);
    });
    if (documents.length) void loadDocument(documents[0].name);
  } catch (error) {
    setText("docs-content", "Dokumentation konnte nicht geladen werden.");
  }
}

function closeDocs() {
  const modal = $("docs-modal");
  modal.classList.remove("open");
  modal.setAttribute("aria-hidden", "true");
}

document.querySelectorAll("button[data-kind]").forEach((button) => {
  button.addEventListener("click", () => {
    heatmapKind = button.dataset.kind;
    document.querySelectorAll("button[data-kind]").forEach((node) => {
      node.classList.remove("active");
    });
    button.classList.add("active");
    void refreshHeatmap();
  });
});

$("snapshot-select").addEventListener("change", (event) => {
  selectedSnapshot = event.target.value;
  void refreshHeatmap();
});
$("docs-btn").addEventListener("click", () => void openDocs());
$("docs-close").addEventListener("click", closeDocs);
$("docs-modal").addEventListener("click", (event) => {
  if (event.target === $("docs-modal")) closeDocs();
});

async function initialize() {
  await refreshSnapshots();
  await refreshStatus();
  await refreshHeatmap();
}

void initialize();
setInterval(() => void refreshStatus(), 1000);
setInterval(() => void refreshHeatmap(), 5000);
setInterval(() => void refreshSnapshots(), 30000);
