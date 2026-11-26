import { execFileSync } from "node:child_process";
import path from "node:path";
import { expect, type Browser, type Page } from "@playwright/test";

const ROOT = path.resolve(__dirname, "../../..");
const MAILPIT = process.env.E2E_MAILPIT_URL ?? "http://localhost:8025";
export const PASSWORD = process.env.DEMO_USER_PASSWORD ?? "local-dev-demo-password";

/** Run a command in a Compose service, from the repository root. */
export function compose(...args: string[]): string {
  return execFileSync("docker", ["compose", "exec", "-T", ...args], { cwd: ROOT, encoding: "utf8" });
}

export function sql(statement: string): string {
  return compose("db", "psql", "-U", "postgres", "-d", "infrawatch", "-qtAc", statement).trim();
}

/** A browser of its own for one demo user, signed in through the login page. */
export async function signedIn(browser: Browser, user: string): Promise<Page> {
  const page = await (await browser.newContext()).newPage();
  await page.goto("/login");
  await page.getByLabel("Email").fill(`${user}@infrawatch.local`);
  await page.getByLabel("Password").fill(PASSWORD);
  await page.getByRole("button", { name: "Sign in" }).click();
  await page.waitForURL("/");
  return page;
}

type Message = { Subject: string; To: { Address: string }[]; Cc: { Address: string }[] | null };

/** The one email whose subject contains ``subject``, waiting for the worker to send it. */
export async function email(subject: string): Promise<Message> {
  let found: Message[] = [];
  await expect
    .poll(
      async () => {
        const query = new URLSearchParams({ query: `subject:"${subject}"` });
        const response = await fetch(`${MAILPIT}/api/v1/search?${query}`);
        found = (await response.json()).messages;
        return found.length;
      },
      { timeout: 60_000, message: `an email with subject ${subject}` },
    )
    .toBe(1);
  return found[0];
}
