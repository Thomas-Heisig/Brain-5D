import { test, expect } from "@playwright/test";
import { createReadStream, existsSync, statSync } from "node:fs";
import { createServer } from "node:http";
import { extname, join, normalize, resolve } from "node:path";

const STATIC_ROOT = resolve("src/dashboard/static");
const contentTypes = {
  ".css": "text/css",
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json",
};

let server;

function startStaticServer() {
  server = createServer((request, response) => {
    const requestPath = decodeURIComponent((request.url || "/").split("?")[0]);
    const relativePath = requestPath === "/" ? "index.html" : requestPath.slice(1);
    const filePath = normalize(join(STATIC_ROOT, relativePath));
    if (!filePath.startsWith(STATIC_ROOT) || !existsSync(filePath) || !statSync(filePath).isFile()) {
      response.writeHead(404);
      response.end("Not found");
      return;
    }
    response.writeHead(200, { "Content-Type": contentTypes[extname(filePath)] || "text/plain" });
    createReadStream(filePath).pipe(response);
  });
  return new Promise((resolveServer) => server.listen(4173, "127.0.0.1", resolveServer));
}

test.beforeAll(async () => startStaticServer());
test.afterAll(async () => new Promise((resolveServer) => server.close(resolveServer)));

async function openDashboard(page, batchResponse = null) {
  await page.route("https://cdnjs.cloudflare.com/**", (route) => route.fulfill({ status: 200, body: "" }));
  await page.route("**/api/**", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    if (url.pathname === "/api/experiment/workflow/catalog") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          questions: [
            { id: "RQ-BROWSER-001", label: "Browser workflow contract" },
            { id: "RQ-BROWSER-002", label: "Exploratory browser path" },
          ],
          hypotheses: [{ id: "H-BROWSER-001-A", question_id: "RQ-BROWSER-001", label: "The workflow is traceable" }],
          protocols: [{
            id: "browser_protocol",
            label: "Browser protocol",
            research_question: "RQ-BROWSER-001",
            hypothesis: "H-BROWSER-001-A",
            preregistration: "PREREG-BROWSER-001",
            default_seed_expression: "10-12",
            default_ticks: 24,
          }],
          next_experiment_id: "EXP-BROWSER-0001",
        }),
      });
      return;
    }
    if (url.pathname === "/api/gate/status") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          overall: "pending",
          live_runtime: [],
          gate_a: { items: [] },
          gate_b: { items: [] },
          gate_c: { items: [] },
        }),
      });
      return;
    }
    if (url.pathname === "/api/releases/timeline") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          sources: [
            { name: "TODO", available: true },
            { name: "ROADMAP", available: true },
            { name: "CHANGELOG", available: true },
          ],
          entries: [{
            date: "2026-09-07",
            title: "Release timeline restoration",
            sources: ["TODO", "ROADMAP", "CHANGELOG"],
            items: [{ text: "Timeline is visible in Release", done: true }],
          }],
        }),
      });
      return;
    }
    if (url.pathname === "/api/experiment/workflow/batch" && request.method() === "POST") {
      const body = JSON.parse(request.postData() || "{}");
      if (batchResponse) batchResponse.body = body;
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          ok: true,
          workflow_id: body.batch_id || "EXP-BROWSER-0001",
          report: "workflows/EXP-BROWSER-0001.json",
          report_markdown: "workflows/EXP-BROWSER-0001.md",
          completed: body.protocols.length,
          failed: 0,
          results: body.protocols.map((protocol) => ({ protocol, status: "completed" })),
        }),
      });
      return;
    }
    await route.fulfill({ status: 200, contentType: "application/json", body: "{}" });
  });
  await page.goto("/");
  await page.locator('[data-tab="research"]').evaluate((button) => button.click());
  await expect(page.locator("#workflow-status")).toHaveText("Bereit");
}

async function selectResearchView(page, view) {
  await page
    .locator(`[data-research-workspace-view="${view}"]`)
    .evaluate((button) => button.click());
  await expect(page.locator(`[data-research-workspace-panel="${view}"]`)).toBeVisible();
}

test("batch dialog edits per-protocol options, reports completion, and updates footer", async ({ page }) => {
  const batchResponse = { body: null };
  await openDashboard(page, batchResponse);
  await selectResearchView(page, "runs");
  await expect(page.locator("#workflow-experiment-library")).toBeVisible();
  await expect(page.locator("#workflow-series-open")).toHaveText("Neue Reihe");
  await expect(page.locator("#workflow-active-experiments")).toContainText("Keine aktiven Experimente.");
  await expect(page.locator("#workflow-archived-experiments")).toContainText("Archiv ist leer.");

  await selectResearchView(page, "plan");
  await page.locator("#workflow-batch-open").click();
  await expect(page.locator("#workflow-batch-dialog")).toBeVisible();
  await page.locator('[data-batch-select="none"]').click();
  const row = page.locator(".workflow-batch-protocol").first();
  await row.locator('input[type="checkbox"]').check();
  await row.locator("[data-batch-seeds]").fill("21-23");
  await row.locator("[data-batch-ticks]").fill("48");
  await page.locator("#workflow-batch-id").fill("EXP-BROWSER-BATCH");
  await page.locator("#workflow-batch-start").click();

  await expect(page.locator("#workflow-batch-status")).toContainText("1 erfolgreich");
  await expect(page.locator("#workflow-result")).toContainText("EXP-BROWSER-BATCH");
  await expect(page.locator("#workflow-batch-dialog")).not.toBeVisible();
  await expect(page.locator("#footer-experiment-state")).toContainText("Experiment-Workflow abgeschlossen");
  expect(batchResponse.body.protocol_options.browser_protocol).toEqual({ seeds: "21-23", ticks: 48 });
});

test("research help explains operational and exploratory status", async ({ page }) => {
  await openDashboard(page);
  await page.locator("#help-toggle").click();
  await expect(page.locator("#context-help-title")).toHaveText("Research Workspace");
  await expect(page.locator("#context-help-text")).toContainText("Operational bedeutet");
  await expect(page.locator("#context-help-text")).toContainText("Exploratory bedeutet");
  await expect(page.locator("#context-help-text")).toContainText("niemals automatisch");
});

test("navigation and box-state controls remain usable", async ({ page }) => {
  await openDashboard(page);
  await page.locator('[data-tab="network"]').evaluate((button) => button.click());
  await expect(page.locator("#tab-network")).toHaveClass(/active/);
  await page.locator('[data-tab="research"]').evaluate((button) => button.click());
  await expect(page.locator("#tab-research")).toHaveClass(/active/);

  const box = page.locator(".tab-content.active .box-state-ready").first();
  await expect(box).toBeVisible();
  const ownControls = box.locator(":scope > .box-state-header > .box-state-tools");
  await ownControls.locator('[data-box-state="minimized"]').click();
  await expect(box).toHaveClass(/box-state-minimized/);
  await ownControls.locator('[data-box-state="maximized"]').click();
  await expect(box).toHaveClass(/box-state-maximized/);
  await page.keyboard.press("Escape");
  await expect(box).not.toHaveClass(/box-state-maximized/);
});

test("Release workspace renders the documentation timeline", async ({ page }) => {
  await openDashboard(page);
  await page.locator('[data-tab="gate"]').evaluate((button) => button.click());
  await expect(page.locator("#release-timeline-list .release-timeline-entry")).toHaveCount(1);
  await expect(page.locator("#release-timeline-list")).toContainText("Release timeline restoration");
  await expect(page.locator("#release-timeline-sources")).toContainText("TODO");
  await expect(page.locator("[data-timeline-phase]")).toHaveCount(3);
  await expect(page.locator('[data-timeline-phase="past"]')).toContainText("Was war");
  await expect(page.locator('[data-timeline-phase="current"]')).toContainText("Was ist");
  await expect(page.locator('[data-timeline-phase="future"]')).toContainText("Was wird");

  for (const view of ["releases", "preview", "timeline", "documents", "gate"]) {
    await page.locator(`[data-workspace-view="${view}"]`).click();
    await expect(page.locator(`[data-release-view="${view}"]`)).toBeVisible();
  }

  await page.locator('[data-workspace-view="documents"]').click();
  await page.locator('[data-release-document="08-roadmap/TODO.md"]').click();
  await expect(page.locator("#tab-research")).toHaveClass(/active/);
  await expect(page.locator("#fm-viewer")).not.toHaveClass(/fm-viewer-hidden/);
});

for (const viewport of [{ width: 1440, height: 900 }, { width: 1024, height: 768 }, { width: 390, height: 844 }]) {
  test(`responsive shell has no horizontal overflow at ${viewport.width}px`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await openDashboard(page);
    const metrics = await page.evaluate(() => {
      const footer = document.querySelector(".site-footer").getBoundingClientRect();
      return {
        horizontalOverflow: document.documentElement.scrollWidth - window.innerWidth,
        footerWidth: footer.width,
        viewportWidth: window.innerWidth,
        footerVisible: footer.height > 0,
      };
    });
    expect(metrics.horizontalOverflow).toBeLessThanOrEqual(1);
    expect(metrics.footerWidth).toBeLessThanOrEqual(metrics.viewportWidth);
    expect(metrics.footerVisible).toBe(true);
  });
}
