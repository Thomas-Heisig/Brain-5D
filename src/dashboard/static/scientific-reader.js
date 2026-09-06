"use strict";

const READER_BUTTON_ID = "scientific-reader-toggle";
const READER_DIALOG_ID = "scientific-reader-dialog";

function byId(id) {
  return document.getElementById(id);
}

function activeWorkspace() {
  return document.querySelector(".tab-content.active:not([hidden])") || document.querySelector(".tab-content.active");
}

function cleanWorkspaceText(workspace) {
  if (!workspace) return "Keine aktive Workspace-Ausgabe verfügbar.";
  const clone = workspace.cloneNode(true);
  clone.querySelectorAll("button, input, select, textarea, svg, canvas, script, style, nav, [hidden], [aria-hidden=\"true\"], .wesen-visibility-menu").forEach((node) => node.remove());
  const raw = clone.innerText || clone.textContent || "";
  const lines = raw
    .split(/\r?\n/)
    .map((line) => line.replace(/[ \t]+/g, " ").trim())
    .filter(Boolean);
  const unique = [];
  for (const line of lines) {
    if (unique[unique.length - 1] !== line) unique.push(line);
  }
  return unique.join("\n") || "Keine lesbare Ausgabe im aktiven Workspace verfügbar.";
}

function statusLine(label, id) {
  return `${label}: ${byId(id)?.textContent?.trim() || "nicht berichtet"}`;
}

function buildReaderText() {
  const workspace = activeWorkspace();
  const workspaceName = byId("header-context")?.textContent?.trim() || document.body.dataset.currentTab || "unbekannt";
  const generated = new Date().toISOString();
  const activeText = cleanWorkspaceText(workspace);
  return [
    "BRAIN-5D SCIENTIFIC READER OUTPUT",
    "=================================",
    `Erzeugt: ${generated}`,
    `Workspace: ${workspaceName}`,
    "",
    "STATUS",
    "------",
    statusLine("Runtime", "overview-runtime-status"),
    statusLine("Health", "overview-health-status"),
    statusLine("Scientific Gate", "overview-scientific-status"),
    statusLine("Release", "overview-release-status"),
    "",
    "BEOBACHTETE DASHBOARD-AUSGABE",
    "------------------------------",
    activeText,
    "",
    "INTERPRETATIONSGRENZE",
    "--------------------",
    "Diese Ausgabe enthält publizierte Dashboard-Werte und sichtbare Workspace-Daten zum Erzeugungszeitpunkt.",
    "Nicht berichtete Werte werden nicht ersetzt oder als Null interpretiert.",
    "Die Reader-Ausgabe ist eine lesbare Momentaufnahme; sie ersetzt keine registrierte Studie, kein DATA-Artefakt und keinen EVID-Nachweis.",
  ].join("\n");
}

function ensureDialog() {
  let dialog = byId(READER_DIALOG_ID);
  if (dialog) return dialog;
  dialog = document.createElement("dialog");
  dialog.id = READER_DIALOG_ID;
  dialog.className = "scientific-reader-dialog";
  dialog.setAttribute("aria-labelledby", "scientific-reader-title");
  dialog.innerHTML = `
    <div class="scientific-reader-header">
      <div><span class="workspace-kicker">TEXT EVIDENCE VIEW</span><h2 id="scientific-reader-title">Scientific Reader Output</h2></div>
      <button type="button" class="icon-btn" data-reader-close title="Reader schließen" aria-label="Reader schließen">×</button>
    </div>
    <p class="scientific-reader-note">Lesbare Momentaufnahme aus den aktuell publizierten Dashboard-Daten.</p>
    <pre id="scientific-reader-output" class="scientific-reader-output" tabindex="0"></pre>
    <div class="scientific-reader-actions">
      <button type="button" class="btn-secondary" data-reader-copy>Text kopieren</button>
      <button type="button" class="btn-primary" data-reader-download>Als TXT speichern</button>
      <button type="button" class="btn-secondary" data-reader-close>Schließen</button>
    </div>`;
  document.body.appendChild(dialog);
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
  dialog.querySelectorAll("[data-reader-close]").forEach((button) => button.addEventListener("click", () => dialog.close()));
  dialog.querySelector("[data-reader-copy]")?.addEventListener("click", async () => {
    const output = byId("scientific-reader-output")?.textContent || "";
    try {
      await navigator.clipboard.writeText(output);
    } catch (_) {
      const fallback = document.createElement("textarea");
      fallback.value = output;
      document.body.appendChild(fallback);
      fallback.select();
      document.execCommand("copy");
      fallback.remove();
    }
  });
  dialog.querySelector("[data-reader-download]")?.addEventListener("click", () => {
    const output = byId("scientific-reader-output")?.textContent || "";
    const stamp = new Date().toISOString().replace(/[:.]/g, "-");
    const blob = new Blob([output], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `brain5d-scientific-reader-${stamp}.txt`;
    anchor.click();
    URL.revokeObjectURL(url);
  });
  return dialog;
}

export function initScientificReader() {
  const button = byId(READER_BUTTON_ID);
  if (!button || button.dataset.bound === "true") return;
  button.dataset.bound = "true";
  button.addEventListener("click", () => {
    const dialog = ensureDialog();
    const output = byId("scientific-reader-output");
    if (output) output.textContent = buildReaderText();
    if (typeof dialog.showModal === "function") dialog.showModal();
    else dialog.setAttribute("open", "true");
    output?.focus();
  });
}
