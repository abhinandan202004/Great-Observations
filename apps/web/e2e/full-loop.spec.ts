import { expect, type Page, test, type WebSocketRoute } from "@playwright/test";
import { compose, email, signedIn, sql } from "./stack";

/** Let the test cut a page's live connection and hold it down until restored. */
async function cuttable(page: Page) {
  let down = false;
  const open = new Set<WebSocketRoute>();
  await page.context().routeWebSocket(/\/api\/ws$/, (ws) => {
    if (down) {
      void ws.close({ code: 4000, reason: "cut by the test" });
      return;
    }
    ws.connectToServer();
    open.add(ws);
  });
  return {
    async cut() {
      down = true;
      for (const ws of open) await ws.close({ code: 4000, reason: "cut by the test" });
      open.clear();
    },
    restore() {
      down = false;
    },
  };
}

const status = (page: Page) => page.locator('[aria-label="Status"] [aria-current="step"]');
const live = (page: Page) => page.getByText("Live: updates appear as they happen");

// G9.3: the whole loop in real browsers, one per person. Along the way it checks G3.9: an open
// incident page updates by itself, and catches up after its connection was cut.
test("a fault becomes an incident that the teams work, document and the caller closes", async ({
  browser,
}) => {
  // A rule of this run's own, so drafts and incidents from earlier runs cannot absorb it.
  const rule = `E2E checkout errors ${Date.now()}`;
  const ruleId = sql(
    `INSERT INTO alert_rules (name, service_id, metric, comparator, threshold, duration_seconds,
      severity) SELECT '${rule}', id, 'error_rate_percent', 'above', 15, 30, 'P2'
      FROM services WHERE name = 'checkout' RETURNING id`,
  );
  try {
    await test.step("a fault is injected and the alert creates a draft", async () => {
      compose("demo-app", "python", "-m", "infrawatch_demo_app.fault", "stop");
      compose("demo-app", "python", "-m", "infrawatch_demo_app.fault", "error-burst", "--minutes", "4");
      await expect
        .poll(() => sql(`SELECT count(*) FROM alerts WHERE rule_id = '${ruleId}' AND state = 'draft'`), {
          timeout: 4 * 60_000,
          intervals: [5_000],
          message: "the alert to fire and leave a draft",
        })
        .toBe("1");
    });

    const support = await signedIn(browser, "support");
    const connection = await cuttable(support);
    let incidentUrl = "";
    let number = "";

    await test.step("Production Support raises the draft", async () => {
      await support.goto("/drafts");
      const draft = support.getByRole("article", { name: new RegExp(rule) });
      await draft.getByRole("textbox", { name: "Impact, as stakeholders will read it" }).fill(
        "Some customers cannot pay",
      );
      await draft.getByRole("button", { name: `Raise incident for ${rule}` }).click();
      await support.waitForURL(/\/incidents\/[0-9a-f-]{36}$/);
      incidentUrl = support.url();
      number = /#(\d+)/.exec((await support.getByRole("heading", { level: 1 }).textContent()) ?? "")![1];
      await expect(status(support)).toHaveText("raised");
      await expect(live(support)).toBeVisible();
    });

    await test.step("the owning team's group gets one email", async () => {
      const raised = await email(`#${number} Raised`);
      expect(raised.To.map((to) => to.Address)).toEqual(["payments-team@infrawatch.local"]);
    });

    const developer = await signedIn(browser, "developer");
    const move = (to: string) => developer.getByRole("button", { name: `Move to ${to}` }).click();

    await test.step("the team works it, and the caller's open page follows live", async () => {
      await developer.goto(incidentUrl);
      await expect(live(developer)).toBeVisible();
      await move("acknowledged");
      await expect(status(support)).toHaveText("acknowledged"); // no reload on the support page
      const task = developer.getByRole("region", { name: "Payments Platform" });
      await task.getByRole("textbox", { name: "New step" }).fill("Roll back the last deploy");
      await task.getByRole("button", { name: "Add step" }).click();
      await expect(support.getByText("Roll back the last deploy")).toBeVisible();
    });

    await test.step("a page whose connection drops catches up when it returns", async () => {
      await connection.cut();
      await expect(support.getByText("Connecting for live updates…")).toBeVisible();
      await move("investigating");
      await expect(status(developer)).toHaveText("investigating");
      await move("mitigating");
      await expect(status(developer)).toHaveText("mitigating");
      await expect(status(support)).toHaveText("acknowledged"); // it really missed them
      connection.restore();
      await expect(live(support)).toBeVisible({ timeout: 30_000 });
      await expect(status(support)).toHaveText("mitigating");
    });

    await test.step("the team resolves it and writes the runbook", async () => {
      await move("monitoring");
      await expect(status(developer)).toHaveText("monitoring");
      await move("resolved");
      await expect(status(developer)).toHaveText("resolved");
      await developer
        .getByRole("combobox", { name: "Root cause category" })
        .selectOption({ label: "Code or deploy" });
      const fields: [string, string][] = [
        ["Root cause", "The last deploy disabled the payment retry"],
        ["Contributing factors", "No canary stage for checkout"],
        ["Remediation and prevention", "Rolled back; add a canary stage"],
        ["Workaround applied", "Manual retries, since removed"],
        ["If none are similar: what did you search?", "Checkout incidents, last 90 days"],
      ];
      for (const [name, text] of fields) {
        await developer.getByRole("textbox", { name, exact: true }).fill(text);
      }
      await developer.getByRole("button", { name: "Submit for review" }).click();
      await expect(developer.getByText("Waiting for review")).toBeVisible();
    });

    await test.step("the Incident Commander approves it", async () => {
      const commander = await signedIn(browser, "commander");
      await commander.goto(incidentUrl);
      await commander.getByRole("button", { name: "Approve version 1" }).click();
      await expect(commander.getByText(/the caller can now close the incident/)).toBeVisible();
    });

    await test.step("the caller closes it, and the groups hear", async () => {
      await expect(support.getByText(/the caller can now close the incident/)).toBeVisible();
      await support.getByRole("button", { name: "Close incident" }).click();
      await expect(status(support)).toHaveText("closed");
      await expect(status(developer)).toHaveText("closed");
      await email(`#${number} Closed`);
    });
  } finally {
    compose("demo-app", "python", "-m", "infrawatch_demo_app.fault", "stop");
    sql(`UPDATE alert_rules SET enabled = false WHERE id = '${ruleId}'`);
  }
});
