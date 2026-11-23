import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import OnCallPage from "./page";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

const asha = { id: "u1", display_name: "Asha", email: "asha@x" };
const ben = { id: "u2", display_name: "Ben", email: "ben@x" };

function answer(byPath: Record<string, unknown>) {
  vi.stubGlobal(
    "fetch",
    vi.fn((url: string) => {
      const body = byPath[url.replace("/api", "")];
      return Promise.resolve(
        body === undefined
          ? new Response(JSON.stringify({ detail: "Your role may not do this" }), { status: 403 })
          : new Response(JSON.stringify(body)),
      );
    }),
  );
}

it("reorders the rotation in place, keeps focus on the button and announces it once", async () => {
  answer({
    "/oncall": [
      {
        team_id: "t1",
        team: "Payments Platform",
        group_email: "payments@x",
        rotation: { members: [asha, ben], handover_local: "2026-01-05T09:00:00", time_zone: "UTC", shift_days: 7 },
        on_call: asha,
        shift_ends_at: "2026-11-30T09:00:00Z",
      },
    ],
    "/teams": [{ id: "t1", name: "Payments Platform", members: [] }],
  });
  render(<OnCallPage />);

  const down = await screen.findByRole("button", { name: "Move down Asha" });
  down.focus();
  fireEvent.click(down);

  const names = screen.getAllByRole("listitem").map((item) => item.querySelector("span")?.textContent);
  expect(names).toEqual(["Ben", "Asha"]);
  expect(document.activeElement).toBe(down);
  expect(down.getAttribute("aria-disabled")).toBe("true");
  expect(screen.getByText("Asha moved to position 2 of 2.")).toBeDefined();
});

it("flags a team with nobody on call, and hides the outbox from non-admins", async () => {
  answer({
    "/oncall": [
      { team_id: "t2", team: "Core Infrastructure", group_email: "infra@x", rotation: null, on_call: null, shift_ends_at: null },
    ],
    "/teams": [],
  });
  render(<OnCallPage />);

  expect(await screen.findByText("Warning: no one is on call.")).toBeDefined();
  expect(screen.queryByRole("heading", { name: "Undelivered email" })).toBeNull();
});
