import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { Incident } from "./incident";

vi.mock("next/navigation", () => ({ useParams: () => ({ id: "abc" }) }));
// The live connection has its own tests; here it stays quiet.
vi.mock("@/lib/live", () => ({ useLive: () => ({ live: false, version: 0 }) }));
// jsdom has no canvas; the figure's caption and table carry the same information.
vi.mock("../../telemetry/chart", () => ({ Chart: () => null }));
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

const timer = { due: "2099-01-01T00:00:00Z", stopped_at: null, remaining_seconds: 0, breached: false };
const summary = {
  id: "abc",
  number: 7,
  title: "Checkout errors",
  impact: "Some customers cannot pay",
  severity: "P2",
  status: "raised",
  service: "checkout",
  raised_at: "2026-11-19T09:00:00Z",
  acknowledge: timer,
  resolve: timer,
};

function answer(...bodies: unknown[]) {
  // Anything asked for beyond these (attachments, metrics, logs) gets an empty list.
  const fetch = vi.fn(() => Promise.resolve(new Response("[]")));
  for (const body of bodies) fetch.mockResolvedValueOnce(new Response(JSON.stringify(body)));
  vi.stubGlobal("fetch", fetch);
}

describe("Incident", () => {
  it("shows status and impact only when the API sends the summary", async () => {
    answer(summary);
    render(<Incident />);

    expect(await screen.findByText("Some customers cannot pay")).toBeDefined();
    expect(screen.getByRole("listitem", { current: "step" }).textContent).toBe("raised");
    expect(screen.queryByRole("button")).toBeNull();
    expect(screen.queryByText("Timeline")).toBeNull();
  });

  it("offers the next state and the team's task when the API sends the detail", async () => {
    const task = { team_id: "t1", team: "Payments Platform", assignee_id: null, assignee: null };
    answer(
      {
        ...summary,
        description: "5xx on POST /checkout",
        caller: "Demo Production Support",
        teams: [{ ...task, checklist: [] }],
        timeline: [],
        escalations: [
          { time: "2026-11-19T09:10:00Z", team: "Payments Platform", step: 1, from_person: "Asha", to_person: "Ben" },
        ],
        alerts: [
          {
            rule: "Checkout error rate high",
            metric: "error_rate_percent",
            comparator: "above",
            threshold: 15,
            breach_started_at: "2026-11-19T08:59:00Z",
            last_fired_at: "2026-11-19T09:00:00Z",
            fire_count: 2,
            snapshot: [{ time: "2026-11-19T09:00:00Z", value: 42 }],
          },
        ],
      },
      [{ id: "t1", name: "Payments Platform", members: [] }],
    );
    render(<Incident />);

    expect(await screen.findByRole("button", { name: "Move to acknowledged" })).toBeDefined();
    expect(screen.getByRole("region", { name: "Payments Platform" })).toBeDefined();
    const figure = screen.getByRole("figure");
    expect(figure.textContent).toContain('"Checkout error rate high" fired 2 times');
    expect(screen.getByRole("table", { name: /error_rate_percent on checkout, frozen/ })).toBeDefined();
    expect(screen.getByText(/passed it from Asha to Ben \(escalation 1\)/)).toBeDefined();
  });
});
