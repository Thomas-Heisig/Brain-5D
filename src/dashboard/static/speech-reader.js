"use strict";

let activeSession = null;

function supported() {
  return typeof window !== "undefined" && "speechSynthesis" in window && "SpeechSynthesisUtterance" in window;
}

function cleanSpeechText(value) {
  return String(value || "")
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/!\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1")
    .replace(/https?:\/\/\S+/g, "")
    .replace(/[#*_`~]+/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function splitSpeechText(value, limit = 220) {
  const text = cleanSpeechText(value);
  if (!text) return [];
  const sentences = text.match(/[^.!?]+[.!?]+|[^.!?]+$/g) || [text];
  const chunks = [];
  let current = "";
  for (const sentence of sentences) {
    const candidate = `${current} ${sentence}`.trim();
    if (current && candidate.length > limit) {
      chunks.push(current);
      current = sentence.trim();
    } else {
      current = candidate;
    }
  }
  if (current) chunks.push(current);
  return chunks.flatMap((chunk) => {
    if (chunk.length <= limit) return [chunk];
    const words = chunk.split(/\s+/);
    const result = [];
    let part = "";
    for (const word of words) {
      const candidate = `${part} ${word}`.trim();
      if (part && candidate.length > limit) {
        result.push(part);
        part = word;
      } else {
        part = candidate;
      }
    }
    if (part) result.push(part);
    return result;
  });
}

function germanVoice() {
  const voices = window.speechSynthesis.getVoices();
  return voices.find((voice) => /^de(-|_)/i.test(voice.lang)) || null;
}

export function stopSpeech() {
  if (!supported()) return;
  window.speechSynthesis.cancel();
  if (activeSession) activeSession.onState("stopped");
  activeSession = null;
}

export function speakText(value, { onState = () => {}, lang = "de-DE" } = {}) {
  if (!supported()) {
    onState("unsupported");
    return false;
  }
  const chunks = splitSpeechText(value);
  if (!chunks.length) {
    onState("empty");
    return false;
  }
  stopSpeech();
  const session = { chunks, index: 0, onState };
  activeSession = session;

  const speakNext = () => {
    if (activeSession !== session) return;
    if (session.index >= session.chunks.length) {
      activeSession = null;
      session.onState("done");
      return;
    }
    const utterance = new SpeechSynthesisUtterance(session.chunks[session.index++]);
    utterance.lang = lang;
    utterance.rate = 0.95;
    utterance.pitch = 1;
    const voice = germanVoice();
    if (voice) utterance.voice = voice;
    utterance.onstart = () => session.onState("speaking");
    utterance.onend = speakNext;
    utterance.onerror = () => {
      if (activeSession === session) {
        activeSession = null;
        session.onState("error");
      }
    };
    window.speechSynthesis.speak(utterance);
  };
  speakNext();
  return true;
}

export function createSpeechControls(mount, getText, { label = "Text vorlesen", includeStart = true } = {}) {
  const controls = document.createElement("div");
  controls.className = "speech-reader-controls";
  controls.setAttribute("role", "group");
  controls.setAttribute("aria-label", label);
  controls.innerHTML = `${includeStart ? `<button type="button" class="speech-reader-start" title="${label}">▶</button>` : ""}
    <button type="button" class="speech-reader-pause" title="Vorlesen pausieren" disabled>⏸</button>
    <button type="button" class="speech-reader-stop" title="Vorlesen anhalten" disabled>⏹</button>
    <span class="speech-reader-status" role="status" aria-live="polite"></span>`;
  mount.append(controls);
  const start = controls.querySelector(".speech-reader-start");
  const pause = controls.querySelector(".speech-reader-pause");
  const stop = controls.querySelector(".speech-reader-stop");
  const status = controls.querySelector(".speech-reader-status");
  let paused = false;

  const setState = (state) => {
    const active = state === "speaking" || state === "paused";
    pause.disabled = !active;
    stop.disabled = !active;
    if (state === "speaking") { status.textContent = "Liest vor"; pause.textContent = "Pause"; paused = false; }
    if (state === "paused") { status.textContent = "Pausiert"; pause.textContent = "Weiter"; paused = true; }
    if (state === "done") { status.textContent = "Fertig"; pause.textContent = "Pause"; paused = false; }
    if (state === "stopped") { status.textContent = "Angehalten"; pause.textContent = "Pause"; paused = false; }
    if (state === "empty") status.textContent = "Kein lesbarer Text";
    if (state === "unsupported") status.textContent = "Vorlesen wird hier nicht unterstützt";
    if (state === "error") status.textContent = "Vorlesen konnte nicht gestartet werden";
  };

  const startReading = () => speakText(getText(), { onState: setState });
  start?.addEventListener("click", startReading);
  pause.addEventListener("click", () => {
    if (!supported()) return;
    if (paused) { window.speechSynthesis.resume(); setState("speaking"); }
    else { window.speechSynthesis.pause(); setState("paused"); }
  });
  stop.addEventListener("click", stopSpeech);
  if (!supported() && start) start.disabled = true;
  return { start: startReading, stop: stopSpeech, element: controls };
}
