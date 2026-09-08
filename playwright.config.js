import { defineConfig } from "@playwright/test";

const python = process.env.MHRN_TEST_PYTHON || process.env.BRAIN5D_TEST_PYTHON || "python";
const executablePath = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE;
export default defineConfig({
  testDir: "./tests/browser",
  timeout: 45_000,
  workers: 1,
  expect: { timeout: 10_000 },
  webServer: [
    { command: `"${python}" scripts/browser_server.py --port 4174`, url: "http://127.0.0.1:4174/", reuseExistingServer: false, timeout: 30_000 },
    { command: `"${python}" scripts/browser_server.py --port 4175 --dashboard-only`, url: "http://127.0.0.1:4175/", reuseExistingServer: false, timeout: 30_000 },
  ],
  use: {
    baseURL: "http://127.0.0.1:4173",
    browserName: "chromium", headless: true, serviceWorkers: "block",
    launchOptions: executablePath ? { executablePath } : {},
    trace: "retain-on-failure", screenshot: "only-on-failure",
  },
  reporter: [["list"], ["html", { outputFolder: "playwright-report", open: "never" }]],
});
