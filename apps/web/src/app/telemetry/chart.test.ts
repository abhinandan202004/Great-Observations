import { describe, expect, it, vi } from "vitest";

// jsdom has no canvas; only the option builder is under test.
vi.mock("echarts/core", () => ({ use: vi.fn() }));

import { chartOption } from "./chart";

describe("chartOption", () => {
  it("draws the samples as a line and every change event as a marker", () => {
    const option = chartOption(
      [
        { time: "2026-11-17T10:00:00Z", value: 1.5 },
        { time: "2026-11-17T10:00:05Z", value: 2 },
      ],
      [{ time: "2026-11-17T10:00:03Z", kind: "deploy", summary: "v2" }],
      { series: "#2a78d6", muted: "#5f6368" },
    );

    const [line] = option.series;
    expect(line.data).toEqual([
      ["2026-11-17T10:00:00Z", 1.5],
      ["2026-11-17T10:00:05Z", 2],
    ]);
    expect(line.markLine.data).toEqual([
      { name: "deploy", xAxis: "2026-11-17T10:00:03Z" },
    ]);
  });
});
