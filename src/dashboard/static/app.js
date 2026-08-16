const $ = (id) => document.getElementById(id);
let heatmapKind = "activity";

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
    setText(
      "homeo-threshold",
      Number(homeostasis.mean_threshold_adaptation || 0).toFixed(3),
    );
    setText("homeo-energy", Number(homeostasis.mean_energy_error || 0).toFixed(3));
    setText("homeo-active", Number(homeostasis.active_neurons || 0).toLocaleString());

    const status = $("system-status");
    status.textContent = `${data.status} · ${data.version}`;
    status.className = storage.worker_failed
      ? "status-pill error"
      : "status-pill online";
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
    `${payload.kind} · Tick ${payload.tick} · ${payload.samples} Samples · `
      + `${min.toFixed(4)}…${max.toFixed(4)}`,
  );
}

async function refreshHeatmap() {
  try {
    const path = `/api/heatmap?kind=${encodeURIComponent(heatmapKind)}`;
    const response = await fetch(path, {cache: "no-store"});
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

void refreshStatus();
void refreshHeatmap();
setInterval(() => void refreshStatus(), 1000);
setInterval(() => void refreshHeatmap(), 5000);
