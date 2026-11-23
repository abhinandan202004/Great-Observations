import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { RunbookPanel } from "./runbook";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

const version = {
  version: 1,
  author: "Demo Developer",
  created_at: "2026-11-24T10:00:00Z",
  timeline: "09:00 detected",
  root_cause_category: "code_or_deploy",
  root_cause: "A bad deploy",
  contributing_factors: "No canary",
  remediation: "Rolled back",
  workaround: "None",
  none_similar: "Searched 90 days",
  similar_incidents: [],
  review: null,
};

function answer(runbook: object) {
  const body = { categories: [], suggested_timeline: "10:00 UTC  Raised by Support", may_close: false, pending_version: null, versions: [], ...runbook };
  vi.stubGlobal(
    "fetch",
    vi.fn((url: string) =>
      Promise.resolve(new Response(JSON.stringify(url.endsWith("/runbook") ? body : []))),
    ),
  );
}

it("offers the form at Resolved, starting from the suggested timeline", async () => {
  answer({});
  render(<RunbookPanel incidentId="abc" status="resolved" />);

  const timeline = (await screen.findByLabelText(/^Timeline/)) as HTMLTextAreaElement;
  expect(timeline.value).toBe("10:00 UTC  Raised by Support");
  expect(screen.getByRole("button", { name: "Submit for review" })).toBeDefined();
});

it("offers review, not the form, while a version waits", async () => {
  answer({ pending_version: 1, versions: [version] });
  render(<RunbookPanel incidentId="abc" status="resolved" />);

  expect(await screen.findByRole("button", { name: "Approve version 1" })).toBeDefined();
  expect(screen.queryByRole("button", { name: "Submit for review" })).toBeNull();
  expect(screen.getByText("Waiting for review")).toBeDefined();
});

it("says the caller may close once approved", async () => {
  const approved = { ...version, review: { decision: "approved", reviewer: "Demo Incident Commander", reviewed_at: "2026-11-24T10:05:00Z", comment: "" } };
  answer({ may_close: true, versions: [approved] });
  render(<RunbookPanel incidentId="abc" status="resolved" />);

  expect(await screen.findByText(/the caller can now close the incident/)).toBeDefined();
  expect(screen.queryByRole("button", { name: /Approve|Submit/ })).toBeNull();
});
