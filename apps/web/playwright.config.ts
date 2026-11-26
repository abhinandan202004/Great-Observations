import { defineConfig, devices } from "@playwright/test";

// Runs against the Compose stack, which must already be up and seeded:
//   E2E_BASE_URL=http://localhost:<WEB_PORT> npm run e2e
export default defineConfig({
  testDir: "e2e",
  timeout: 8 * 60_000, // the loop waits for a real alert to fire, which takes about two minutes
  expect: { timeout: 15_000 },
  retries: 0,
  reporter: process.env.CI ? [["github"], ["html", { open: "never" }]] : "list",
  use: {
    baseURL: process.env.E2E_BASE_URL ?? "http://localhost:3000",
    trace: "retain-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
