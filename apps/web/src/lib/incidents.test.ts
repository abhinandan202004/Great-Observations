import { afterEach, describe, expect, it } from "vitest";
import { moves, type SlaTimer, timerText } from "./incidents";

const due = "2026-11-19T10:00:00Z";
const at = (iso: string) => Date.parse(iso);

describe("moves", () => {
  it("offers one step on and every earlier active state", () => {
    expect(moves("investigating")).toEqual({
      forward: "mitigating",
      back: ["raised", "acknowledged"],
      callerOnly: false,
    });
  });

  it("offers Resolved from Monitoring", () => {
    expect(moves("monitoring").forward).toBe("resolved");
  });

  it("leaves Resolved to the caller and Closed to nobody", () => {
    expect(moves("resolved")).toEqual({ forward: null, back: [], callerOnly: true });
    expect(moves("closed")).toEqual({ forward: null, back: [], callerOnly: false });
  });
});

describe("timerText", () => {
  const running: SlaTimer = { due, stopped_at: null, remaining_seconds: 0, breached: false };

  it("counts down a running clock from the current time", () => {
    expect(timerText(running, at("2026-11-19T08:55:00Z"))).toEqual({
      text: "1h 5m left",
      breached: false,
    });
  });

  it("flags a running clock past its due time", () => {
    expect(timerText(running, at("2026-11-21T10:30:00Z"))).toEqual({
      text: "overdue by 2d 30m",
      breached: true,
    });
  });

  it("reports a stopped clock from the API's figure", () => {
    const met = { ...running, stopped_at: "2026-11-19T09:57:00Z", remaining_seconds: 180 };
    const late = { ...met, remaining_seconds: -120, breached: true };

    expect(timerText(met, 0).text).toBe("met with 3m to spare");
    expect(timerText(late, 0)).toEqual({ text: "met 2m late", breached: true });
  });

  describe("with Intl.DurationFormat", () => {
    const intl = Intl as unknown as { DurationFormat?: unknown };
    afterEach(() => delete intl.DurationFormat);

    it("hands the balanced span to the browser's localised formatter", () => {
      const calls: unknown[] = [];
      intl.DurationFormat = class {
        constructor(...args: unknown[]) {
          calls.push(args);
        }
        format(span: object) {
          calls.push(span);
          return "1 hr, 5 min";
        }
      };

      expect(timerText(running, at("2026-11-19T08:55:00Z")).text).toBe("1 hr, 5 min left");
      expect(calls).toEqual([
        [undefined, { style: "narrow", minutesDisplay: "always" }],
        { days: 0, hours: 1, minutes: 5 },
      ]);
    });
  });
});
