"use strict";

export async function apiGet(path) {
  const response = await fetch(path, { cache: "no-store", headers: { "Cache-Control": "no-store" } });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
  return payload;
}

export async function apiPost(path, body) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(payload.error || `HTTP ${response.status}`);
    error.status = response.status;
    error.payload = payload;
    throw error;
  }
  return payload;
}

export function byId(id) { return document.getElementById(id); }
export function text(value, fallback = "unknown") {
  return value === null || value === undefined || value === "" ? fallback : String(value);
}
