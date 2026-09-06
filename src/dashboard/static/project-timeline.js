"use strict";

const TIMELINE_SOURCES = [
  {
    key: "changelog",
    label: "Changelog",
    path: "07-changelog/CHANGELOG.md",
    icon: "↗",
  },
  {
    key: "roadmap",
    label: "Roadmap",
    path: "08-roadmap/ROADMAP.md",
    icon: "◇",
  },
  {
    key: "todo",
    label: "TODO",
    path: "08-roadmap/TODO.md",
    icon: "□",
  },
];

const timelineState = {
  initialized: false,
  activeFilter: "all",
  activeHorizon: "timeline",
  entries: [],
};

function escapeHtml(value) {
  const element = document.createElement("div");
  element.textContent = value == null ? "" : String(value);
  return element.innerHTML;
}

function parseDate(value) {
  const match = value.match(/(20\d{2}-\d{2}-\d{2})/);
  return match ? match[1] : "";
}

function parseMarkdown(source, markdown) {
  const lines = markdown.split(/\r?\n/);
  const entries = [];
  let current = null;

  for (const line of lines) {
    const heading = line.match(/^##\s+(.+?)\s*$/);
    if (heading) {
      if (current) entries.push(current);
      const title = heading[1].replace(/\s+#+$/, "").trim();
      current = {
        source: source.key,
        sourceLabel: source.label,
        sourcePath: source.path,
        icon: source.icon,
        title,
        date: source.key === "changelog" ? parseDate(title) : "",
        bullets: [],
        done: 0,
        open: 0,
      };
      continue;
    }

    if (!current) continue;
    const checkbox = line.match(/^\s*-\s+\[([ xX])\]\s+(.+)$/);
    if (checkbox) {
      const done = checkbox[1].toLowerCase() === "x";
      current.bullets.push({ text: checkbox[2].trim(), done });
      if (done) current.done += 1;
      else current.open += 1;
      continue;
    }

    const bullet = line.match(/^\s*-\s+(.+)$/);
    if (bullet && current.bullets.length < 3) {
      current.bullets.push({ text: bullet[1].trim(), done: null });
    }
  }
  if (current) entries.push(current);

  return entries.map((entry, index) => ({ ...entry, order: index }));
}

function formatDate(value) {
  if (!value) return "aktueller Plan";
  const date = new Date(`${value}T00:00:00`);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("de-DE", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(date);
}

function entryStatus(entry) {
  if (entry.source === "changelog") return "released";
  if (entry.done && !entry.open) return "complete";
  if (entry.done) return "progress";
  return "planned";
}

function entryHorizon(entry) {
  if (entry.source === "changelog") return "past";
  return entry.done && !entry.open ? "past" : "future";
}

function entryProgress(entry) {
  if (!entry.done && !entry.open) return null;
  return Math.round((entry.done / (entry.done + entry.open)) * 100);
}

function renderStats() {
  const stats = document.getElementById("timeline-stats");
  if (!stats) return;
  const changelog = timelineState.entries.filter((entry) => entry.source === "changelog").length;
  const planEntries = timelineState.entries.filter((entry) => entry.source !== "changelog");
  const done = planEntries.reduce((total, entry) => total + entry.done, 0);
  const open = planEntries.reduce((total, entry) => total + entry.open, 0);
  stats.innerHTML = `
    <span><strong>${changelog}</strong> Releases</span>
    <span><strong>${done}</strong> erledigt</span>
    <span><strong>${open}</strong> offen</span>
  `;
}

function renderTimeline() {
  const container = document.getElementById("project-timeline-list");
  if (!container) return;
  const entries = timelineState.entries
    .filter((entry) => timelineState.activeFilter === "all" || entry.source === timelineState.activeFilter)
    .filter((entry) => timelineState.activeHorizon === "timeline"
      || timelineState.activeHorizon === "elements"
      || entryHorizon(entry) === timelineState.activeHorizon)
    .sort((left, right) => {
      if (left.date && right.date) return right.date.localeCompare(left.date);
      if (left.date) return -1;
      if (right.date) return 1;
      return right.order - left.order;
    });

  if (!entries.length) {
    container.innerHTML = '<p class="timeline-empty">Keine Einträge für diesen Filter.</p>';
    return;
  }

  container.innerHTML = entries.map((entry) => {
    const progress = entryProgress(entry);
    const progressMarkup = progress === null
      ? ""
      : `<div class="timeline-progress" aria-label="${progress}% erledigt"><span style="width:${progress}%"></span></div>`;
    const bullets = entry.bullets.slice(0, 3).map((bullet) => {
      const marker = bullet.done === null ? "·" : bullet.done ? "✓" : "○";
      return `<li class="${bullet.done ? "is-done" : ""}"><span>${marker}</span>${escapeHtml(bullet.text)}</li>`;
    }).join("");
    return `
      <article class="timeline-entry timeline-entry-${entry.source} timeline-status-${entryStatus(entry)}">
        <div class="timeline-marker" aria-hidden="true">${entry.icon}</div>
        <div class="timeline-entry-body">
          <div class="timeline-entry-meta"><span>${escapeHtml(entry.sourceLabel)}</span><time>${escapeHtml(formatDate(entry.date))}</time></div>
          <h3>${escapeHtml(entry.title)}</h3>
          ${bullets ? `<ul>${bullets}</ul>` : ""}
          ${progressMarkup}
          <button type="button" class="timeline-source-link" data-timeline-source="${escapeHtml(entry.sourcePath)}">Quelle öffnen</button>
        </div>
      </article>
    `;
  }).join("");

  container.querySelectorAll("[data-timeline-source]").forEach((button) => {
    button.addEventListener("click", () => {
      const source = button.dataset.timelineSource;
      window.Brain5DUtilityPopups?.close("gate");
      document.querySelector('.tab-btn[data-tab="research"]')?.click();
      const sourceButton = document.querySelector(`.fm-source-btn[data-source="docs"]`);
      sourceButton?.click();
      const search = document.getElementById("fm-search");
      if (search) {
        search.value = source;
        document.getElementById("fm-search-btn")?.click();
      }
    });
  });
}

async function loadTimeline() {
  const container = document.getElementById("project-timeline-list");
  if (!container) return;
  container.innerHTML = '<p class="timeline-empty">Lade Projektverlauf …</p>';
  try {
    const responses = await Promise.all(TIMELINE_SOURCES.map(async (source) => {
      const response = await fetch(`/api/docs-files/${encodeURIComponent(source.path)}`);
      if (!response.ok) throw new Error(`${source.label}: HTTP ${response.status}`);
      const payload = await response.json();
      return parseMarkdown(source, payload.content || "");
    }));
    timelineState.entries = responses.flat();
    renderStats();
    renderTimeline();
  } catch (error) {
    container.innerHTML = `<p class="timeline-empty timeline-error">Projektverlauf konnte nicht geladen werden: ${escapeHtml(error.message)}</p>`;
  }
}

function initProjectTimeline() {
  if (timelineState.initialized) return;
  const root = document.getElementById("project-timeline");
  if (!root) return;
  root.querySelectorAll("[data-timeline-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      timelineState.activeFilter = button.dataset.timelineFilter;
      root.querySelectorAll("[data-timeline-filter]").forEach((item) => {
        item.classList.toggle("active", item === button);
      });
      renderTimeline();
    });
  });
  root.querySelectorAll("[data-timeline-horizon]").forEach((button) => {
    button.addEventListener("click", () => {
      timelineState.activeHorizon = button.dataset.timelineHorizon;
      root.querySelectorAll("[data-timeline-horizon]").forEach((item) => {
        item.classList.toggle("active", item === button);
      });
      renderTimeline();
    });
  });
  timelineState.initialized = true;
  loadTimeline();
}

export { initProjectTimeline };
