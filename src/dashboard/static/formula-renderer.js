"use strict";

/**
 * Scientific formula renderer for dynamically opened Markdown files.
 *
 * MathJax is loaded lazily only when a Markdown document contains TeX delimiters.
 * The dashboard remains usable without the CDN; in that case formula source is
 * preserved and presented in a readable fallback style instead of being lost.
 */

const MATHJAX_URL = "https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg.js";
let loadPromise = null;
let observer = null;
let scheduled = false;

function injectFormulaStyles() {
  if (document.getElementById("brain5d-formula-styles")) return;
  const style = document.createElement("style");
  style.id = "brain5d-formula-styles";
  style.textContent = `
    .fm-markdown mjx-container[jax="SVG"] {
      max-width: 100%;
      overflow-x: auto;
      overflow-y: hidden;
      padding: 0.08rem 0;
    }
    .fm-markdown mjx-container[display="true"] {
      margin: 1.15rem 0 !important;
      padding: 0.9rem 1rem;
      border: 1px solid color-mix(in srgb, currentColor 16%, transparent);
      border-radius: 10px;
      background: color-mix(in srgb, currentColor 4%, transparent);
      text-align: center;
    }
    .fm-markdown .fm-math-fallback {
      font-family: "Cambria Math", "STIX Two Math", "Times New Roman", serif;
      font-size: 1.04em;
      white-space: nowrap;
    }
    .fm-markdown .fm-math-fallback-display {
      display: block;
      overflow-x: auto;
      margin: 1rem 0;
      padding: 0.85rem 1rem;
      border: 1px solid color-mix(in srgb, currentColor 16%, transparent);
      border-radius: 10px;
      background: color-mix(in srgb, currentColor 4%, transparent);
      text-align: center;
      white-space: pre;
    }
  `;
  document.head.appendChild(style);
}

function containsMath(root) {
  const text = root?.textContent || "";
  return /\$\$[\s\S]+?\$\$|\\\[[\s\S]+?\\\]|\\\([\s\S]+?\\\)|\$[^\n$]+?\$/.test(text);
}

function ensureMathJax() {
  if (window.MathJax?.typesetPromise) return Promise.resolve(window.MathJax);
  if (loadPromise) return loadPromise;

  window.MathJax = {
    tex: {
      inlineMath: [["$", "$"], ["\\(", "\\)"]],
      displayMath: [["$$", "$$"], ["\\[", "\\]"]],
      processEscapes: true,
      packages: { "[+]": ["ams"] },
    },
    svg: { fontCache: "global" },
    options: {
      skipHtmlTags: ["script", "noscript", "style", "textarea", "pre", "code"],
      ignoreHtmlClass: "fm-code|fm-inline-code",
      processHtmlClass: "fm-markdown",
    },
    startup: { typeset: false },
  };

  loadPromise = new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = MATHJAX_URL;
    script.async = true;
    script.referrerPolicy = "no-referrer";
    script.onload = () => resolve(window.MathJax);
    script.onerror = () => reject(new Error("MathJax konnte nicht geladen werden"));
    document.head.appendChild(script);
  });
  return loadPromise;
}

function fallbackMath(root) {
  if (!root || root.dataset.mathFallbackApplied === "true") return;
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walker.nextNode()) {
    const node = walker.currentNode;
    const parent = node.parentElement;
    if (!parent || parent.closest("pre, code, script, style, textarea, mjx-container")) continue;
    if (/\$\$|\\\[|\\\]|\\\(|\\\)|\$/.test(node.nodeValue || "")) nodes.push(node);
  }

  const pattern = /(\$\$[\s\S]+?\$\$|\\\[[\s\S]+?\\\]|\\\([\s\S]+?\\\)|\$[^\n$]+?\$)/g;
  for (const node of nodes) {
    const value = node.nodeValue || "";
    const parts = value.split(pattern);
    if (parts.length === 1) continue;
    const fragment = document.createDocumentFragment();
    for (const part of parts) {
      if (!part) continue;
      const isDisplay = (part.startsWith("$$") && part.endsWith("$$")) ||
        (part.startsWith("\\[") && part.endsWith("\\]"));
      const isInline = (part.startsWith("$") && part.endsWith("$")) ||
        (part.startsWith("\\(") && part.endsWith("\\)"));
      if (!isDisplay && !isInline) {
        fragment.appendChild(document.createTextNode(part));
        continue;
      }
      const span = document.createElement("span");
      span.className = isDisplay
        ? "fm-math-fallback fm-math-fallback-display"
        : "fm-math-fallback";
      span.textContent = part
        .replace(/^\$\$|\$\$$/g, "")
        .replace(/^\$|\$$/g, "")
        .replace(/^\\\[|\\\]$/g, "")
        .replace(/^\\\(|\\\)$/g, "");
      fragment.appendChild(span);
    }
    node.replaceWith(fragment);
  }
  root.dataset.mathFallbackApplied = "true";
}

async function typesetMarkdownMath() {
  scheduled = false;
  const roots = [...document.querySelectorAll(".fm-markdown")].filter(
    (root) => root.dataset.mathProcessed !== "true" && containsMath(root),
  );
  if (!roots.length) return;

  try {
    const mathJax = await ensureMathJax();
    await mathJax.typesetPromise(roots);
    for (const root of roots) root.dataset.mathProcessed = "true";
  } catch (error) {
    console.warn("Brain-5D formula renderer fallback:", error);
    for (const root of roots) fallbackMath(root);
  }
}

function scheduleTypeset() {
  if (scheduled) return;
  scheduled = true;
  queueMicrotask(typesetMarkdownMath);
}

function initFormulaRenderer() {
  injectFormulaStyles();
  observer = new MutationObserver((mutations) => {
    if (mutations.some((mutation) =>
      [...mutation.addedNodes].some((node) =>
        node.nodeType === Node.ELEMENT_NODE &&
        (node.matches?.(".fm-markdown") || node.querySelector?.(".fm-markdown")),
      ),
    )) {
      scheduleTypeset();
    }
  });
  observer.observe(document.body, { childList: true, subtree: true });
  scheduleTypeset();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initFormulaRenderer, { once: true });
} else {
  initFormulaRenderer();
}
