"use client";

import { LineChart } from "echarts/charts";
import {
  GridComponent,
  MarkLineComponent,
  TooltipComponent,
} from "echarts/components";
import * as echarts from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { useEffect, useRef } from "react";

echarts.use([
  LineChart,
  GridComponent,
  MarkLineComponent,
  TooltipComponent,
  CanvasRenderer,
]);

export type Point = { time: string; value: number };
export type Change = { time: string; kind: string; summary: string };

/** One metric as a line, with each change event as a labelled vertical marker. */
export function chartOption(
  points: Point[],
  changes: Change[],
  colors: { series: string; muted: string },
) {
  return {
    animation: false,
    grid: { left: 64, right: 24, top: 28, bottom: 28 },
    tooltip: { trigger: "axis" },
    xAxis: { type: "time", axisLabel: { color: colors.muted } },
    yAxis: {
      type: "value",
      axisLabel: { color: colors.muted },
      splitLine: { lineStyle: { opacity: 0.25 } },
    },
    series: [
      {
        type: "line",
        showSymbol: false,
        lineStyle: { width: 2, color: colors.series },
        itemStyle: { color: colors.series },
        data: points.map((point) => [point.time, point.value]),
        markLine: {
          symbol: "none",
          lineStyle: { color: colors.muted, type: "dashed" },
          label: { formatter: "{b}", color: colors.muted },
          data: changes.map((change) => ({
            name: change.kind,
            xAxis: change.time,
          })),
        },
      },
    ],
  };
}

export function Chart(props: {
  label: string;
  points: Point[];
  changes: Change[];
}) {
  const element = useRef<HTMLDivElement>(null);
  const chart = useRef<echarts.ECharts>(null);

  useEffect(() => {
    const created = echarts.init(element.current);
    chart.current = created;
    const resize = () => created.resize();
    window.addEventListener("resize", resize);
    return () => {
      window.removeEventListener("resize", resize);
      created.dispose();
    };
  }, []);

  useEffect(() => {
    const style = getComputedStyle(document.documentElement);
    chart.current?.setOption(
      chartOption(props.points, props.changes, {
        series: style.getPropertyValue("--series").trim(),
        muted: style.getPropertyValue("--muted").trim(),
      }),
    );
  }, [props.points, props.changes]);

  // The canvas is opaque to screen readers: the label carries the latest value,
  // and the change events are also listed in a table on the page.
  return (
    <div ref={element} role="img" aria-label={props.label} className="chart" />
  );
}
