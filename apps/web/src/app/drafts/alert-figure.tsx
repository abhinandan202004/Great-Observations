"use client";

import { describe, type FiredAlert } from "@/lib/drafts";
import { Chart, type Point } from "../telemetry/chart";

/** Frozen metric points as a chart, a caption saying what they show, and the points as a table. */
export function PointsFigure(props: { label: string; caption: string; points: Point[] }) {
  return (
    <figure className="alert-figure">
      <Chart label={props.label} points={props.points} changes={[]} />
      <figcaption>{props.caption}</figcaption>
      <details>
        <summary>Snapshot data ({props.points.length} points)</summary>
        <table>
          <caption>{props.label}</caption>
          <thead>
            <tr>
              <th scope="col">Time</th>
              <th scope="col">Value</th>
            </tr>
          </thead>
          <tbody>
            {props.points.map((point) => (
              <tr key={point.time}>
                <td>
                  <time dateTime={point.time}>{new Date(point.time).toLocaleTimeString()}</time>
                </td>
                <td>{point.value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </figure>
  );
}

export function AlertFigure({ alert, service }: { alert: FiredAlert; service: string }) {
  return (
    <PointsFigure
      label={`${alert.metric} on ${service}, frozen when the alert first fired`}
      caption={describe(alert, service)}
      points={alert.snapshot}
    />
  );
}
