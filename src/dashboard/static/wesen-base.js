/* MHRN Wesen workspace — stabilisierte Fassung
 * Read-only, machine-native body visualization.
 * Beobachteter Zustand: kein Lernen, keine Sprache, keine Aktor-Schreibzugriffe.
 */
const WESEN_POLL_MS = 1000;
const NS = "http://www.w3.org/2000/svg";
const WESEN_BASE = [
  { id: "kern", label: "SNN-Kern", kind: "core", hue: "gold", icon: "◆" },
  { id: "innenzustand", label: "Interozeption", kind: "internal", hue: "rose", icon: "♥" },
  { id: "rueckkopplung", label: "Rückkopplung", kind: "feedback", hue: "violet", icon: "↻" },
  { id: "struktur", label: "Körpergrenze", kind: "structure", hue: "green", icon: "⌬" },
];
const state = {
  status: null, embodiment: null, connections: null,
  selected: "kern", history: [], recurrence: [], morphologyHistory: [],
  previousSignature: "", paused: false, zoom: 1, filter: "all",
  timer: null, controller: null, organRefs: null, nerveRefs: null,
  lastPositions: null,
  smoothProfile: { scale: 1, tension: 0, pressure: 0, level: "ok" },
};
