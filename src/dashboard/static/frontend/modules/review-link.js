"use strict";
function initReviewLink() {
  const urlEl = document.getElementById("mhrn-review-url");
  if (!urlEl) return;
  const link = new URL("/review", window.location.href).href;
  urlEl.textContent = link;
  const copyBtn = document.getElementById("review-copy-link");
  if (copyBtn) {
    copyBtn.addEventListener("click", async () => {
      try { await navigator.clipboard.writeText(link); copyBtn.textContent = "Kopiert"; }
      catch (_) { copyBtn.textContent = "Kopieren fehlgeschlagen"; }
    });
  }
}
export { initReviewLink };
