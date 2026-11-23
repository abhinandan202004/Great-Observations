import { describe as group, expect, it } from "vitest";
import { type Draft, describe } from "./drafts";

const draft: Draft = {
  id: "d1",
  rule: "Checkout error rate high",
  service: "checkout",
  metric: "error_rate_percent",
  comparator: "above",
  threshold: 15,
  severity: "P2",
  breach_started_at: "2026-11-19T09:00:00Z",
  last_fired_at: "2026-11-19T09:01:00Z",
  fire_count: 1,
  snapshot: [{ time: "2026-11-19T09:01:00Z", value: 42 }],
};

group("describe", () => {
  it("states the breach, the latest value and how often it fired", () => {
    const text = describe(draft, draft.service);

    expect(text).toContain("error_rate_percent on checkout was above 15");
    expect(text).toContain("latest 42");
    expect(text).toContain('"Checkout error rate high" fired once');
    expect(describe({ ...draft, fire_count: 3 }, "checkout")).toContain("fired 3 times");
  });
});
