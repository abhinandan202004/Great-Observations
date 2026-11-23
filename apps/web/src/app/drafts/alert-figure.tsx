"use client";

import { describe, type FiredAlert } from "@/lib/drafts";
import { Chart } from "../telemetry/chart";

/** The frozen snapshot as a chart, a caption saying what breached, and the points as a table. */
export function AlertFigure({ alert, service }: { alert: FiredAlert; service: string }) {
  return (
    <figure className="alert-figure">
      <Chart label={`${alert.metric} on ${service}, frozen snapshot`} points={alert.snapshot} changes={[]} />
      <figcaption>{describe(alert, service)}</figcaption>
      <details>
        <summary>Snapshot data ({alert.snapshot.length} points)</summary>
        <table>
          <caption>
            {alert.metric} on {service}, frozen when the alert first fired
          </caption>
          <thead>
            <tr>
              <th scope="col">Time</th>
              <th scope="col">Value</th>
            </tr>
          </thead>
          <tbody>
            {alert.snapshot.map((point) => (
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
