/**
 * Shared dashboard API helpers for browser and Hugging Face Space deployments.
 */

"use strict";

const isHuggingFaceHost = () => /\.hf\.space$/i.test(window.location.hostname);

export const isHuggingFaceSpace = isHuggingFaceHost();

export function pollInterval(milliseconds) {
  return isHuggingFaceSpace ? milliseconds * 4 : milliseconds;
}

export async function readJson(response) {
  const contentType = response.headers.get("content-type") || "unknown";
  const body = await response.text();

  if (!body) return {};

  try {
    return JSON.parse(body);
  } catch {
    throw new Error(
      `API returned non-JSON data (HTTP ${response.status}, ${contentType})`,
    );
  }
}