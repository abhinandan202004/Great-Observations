import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { Incident } from "./incident";

vi.mock("next/navigation", () => ({ useParams: () => ({ id: "abc" }) }));
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
  const fetch = vi.fn();
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
      },
      [{ id: "t1", name: "Payments Platform", members: [] }],
    );
    render(<Incident />);

    expect(await screen.findByRole("button", { name: "Move to acknowledged" })).toBeDefined();
    expect(screen.getByRole("region", { name: "Payments Platform" })).toBeDefined();
  });
});
